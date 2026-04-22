from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.cache import cache
from products.models import Ingrediente, Producto, Categoria, ProductoIngrediente, MovimientoInventario
from .models import Pedido, PedidoProducto, Transaccion
from rest_framework.test import APITestCase

def crear_escenario_base():
    """Crea un set de objetos reutilizable para los tests de RF-10."""
    admin = User.objects.create_superuser('chef', 'chef@test.com', 'pass123')
    categoria = Categoria.objects.create(nombre='Platos')
    ingrediente = Ingrediente.objects.create(nombre='Queso', unidad_medida='gramo', stock=100)
    producto = Producto.objects.create(
        nombre='Pizza', categoria=categoria, precio=15000, descripcion=''
    )
    ProductoIngrediente.objects.create(producto=producto, ingrediente=ingrediente, cantidad=30)
    pedido = Pedido.objects.create(mesa_o_online='Mesa 1', creado_por=admin, estado='pendiente')
    PedidoProducto.objects.create(pedido=pedido, producto=producto, cantidad=2)
    return admin, ingrediente, pedido


class DescuentoInventarioTest(TestCase):
    """Tests de integración para RF-10: descuento automático de inventario al confirmar orden."""

    def setUp(self):
        self.client = Client()
        self.admin, self.ingrediente, self.pedido = crear_escenario_base()
        self.client.login(username='chef', password='pass123')

    def test_confirmar_orden_descuenta_stock(self):
        """Al confirmar una orden el stock de los ingredientes se descuenta según la receta.
        Pizza x2 con 30g de Queso por unidad → descuenta 60g de los 100g disponibles → stock resultante = 40.
        """
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        self.ingrediente.refresh_from_db()
        self.assertEqual(self.ingrediente.stock, 40)  # 100 - (30 * 2)

    def test_confirmar_orden_cambia_estado(self):
        """Al confirmar exitosamente, el pedido pasa de 'pendiente' a 'en_preparacion'."""
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_preparacion')

    def test_confirmar_registra_movimiento_inventario(self):
        """Cada descuento de ingrediente queda registrado en MovimientoInventario."""
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        mov = MovimientoInventario.objects.filter(ingrediente=self.ingrediente).first()
        self.assertIsNotNone(mov)
        self.assertEqual(mov.tipo, 'descuento')
        self.assertEqual(mov.cantidad, -60)  # negativo = descuento
        self.assertEqual(mov.stock_resultante, 40)
        self.assertEqual(mov.pedido_id, self.pedido.pk)

    def test_confirmar_sin_stock_suficiente_no_confirma(self):
        """Si no hay stock suficiente la orden NO se confirma y el stock no cambia.
        Pedido requiere 60g pero solo hay 20g → debe fallar.
        """
        self.ingrediente.stock = 20
        self.ingrediente.save()
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        self.pedido.refresh_from_db()
        self.ingrediente.refresh_from_db()
        # El estado sigue siendo pendiente
        self.assertEqual(self.pedido.estado, 'pendiente')
        # El stock no se tocó
        self.assertEqual(self.ingrediente.stock, 20)
        # No se registró ningún movimiento
        self.assertFalse(MovimientoInventario.objects.filter(pedido_id=self.pedido.pk).exists())

    def test_stock_en_bd_es_correcto_tras_confirmar(self):
        """Verificación directa en BD: el valor persistido en BD es el correcto después de confirmar."""
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        stock_en_bd = Ingrediente.objects.get(pk=self.ingrediente.pk).stock
        self.assertEqual(stock_en_bd, 40)


class HistorialVentasTest(TestCase):
    """Tests de integración para RF-11: registro de transacciones en historial de ventas."""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('mesero', 'mesero@test.com', 'pass123')
        self.client.login(username='mesero', password='pass123')
        categoria = Categoria.objects.create(nombre='Bebidas')
        self.producto = Producto.objects.create(
            nombre='Jugo', categoria=categoria, precio=5000, descripcion=''
        )

    def _crear_pedido_listo(self, mesa='Mesa 2'):
        """Helper: crea un pedido en estado 'listo' listo para marcar como entregada."""
        pedido = Pedido.objects.create(
            mesa_o_online=mesa, creado_por=self.admin, estado='listo'
        )
        PedidoProducto.objects.create(pedido=pedido, producto=self.producto, cantidad=2)
        return pedido

    def test_marcar_entregada_crea_transaccion(self):
        """Al marcar un pedido como entregada se crea automáticamente una Transaccion."""
        pedido = self._crear_pedido_listo()
        self.client.post(reverse('pedido_entregada', args=[pedido.pk]))
        self.assertTrue(Transaccion.objects.filter(pedido=pedido).exists())

    def test_transaccion_total_correcto(self):
        """El total de la transacción es precio × cantidad de los productos del pedido."""
        pedido = self._crear_pedido_listo()
        self.client.post(reverse('pedido_entregada', args=[pedido.pk]))
        t = Transaccion.objects.get(pedido=pedido)
        self.assertEqual(t.total, self.producto.precio * 2)  # 5000 * 2 = 10000

    def test_transaccion_no_se_duplica(self):
        """Marcar entregada dos veces no genera dos transacciones (get_or_create)."""
        pedido = self._crear_pedido_listo()
        self.client.post(reverse('pedido_entregada', args=[pedido.pk]))
        # Forzar segunda llamada cambiando estado manualmente
        pedido.estado = 'listo'
        pedido.save()
        self.client.post(reverse('pedido_entregada', args=[pedido.pk]))
        self.assertEqual(Transaccion.objects.filter(pedido=pedido).count(), 1)

    def test_datos_en_bd_correctos(self):
        """Verificación directa en BD: pedido_id y total están correctamente persistidos."""
        pedido = self._crear_pedido_listo()
        self.client.post(reverse('pedido_entregada', args=[pedido.pk]))
        t = Transaccion.objects.get(pedido=pedido)
        self.assertEqual(t.pedido.id, pedido.id)
        self.assertIsNotNone(t.fecha)

    def test_tres_ordenes_en_historial(self):
        """Prueba manual: completar 3 órdenes y verificar que aparecen en el historial."""
        for i in range(1, 4):
            p = self._crear_pedido_listo(mesa=f'Mesa {i}')
            self.client.post(reverse('pedido_entregada', args=[p.pk]))
        self.assertEqual(Transaccion.objects.count(), 3)
        resp = self.client.get(reverse('historial_ventas'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.context['transacciones']), 3)

    def test_exportar_csv_retorna_archivo(self):
        """La vista de exportar CSV devuelve una respuesta con Content-Type text/csv."""
        pedido = self._crear_pedido_listo()
        self.client.post(reverse('pedido_entregada', args=[pedido.pk]))
        resp = self.client.get(reverse('historial_ventas_csv'))
        self.assertEqual(resp.status_code, 200)
        self.assertIn('text/csv', resp['Content-Type'])
        self.assertIn('historial_ventas.csv', resp['Content-Disposition'])


# ─────────────────────────────────────────────────────────────────────────────
# RF-13: Autenticación
# ─────────────────────────────────────────────────────────────────────────────

class AutenticacionTest(TestCase):
    """Tests para RF-13: login / logout / rate limiting."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('mesero1', 'mesero1@test.com', 'clave123')
        # Limpiar caché de rate limiting antes de cada test
        cache.clear()

    def test_login_exitoso_redirige_a_pedidos(self):
        """Credenciales correctas → redirección a /ventas/pedidos/."""
        resp = self.client.post(reverse('login'), {
            'username': 'mesero1',
            'password': 'clave123',
        })
        self.assertRedirects(resp, '/ventas/pedidos/', fetch_redirect_response=False)

    def test_login_credenciales_invalidas_muestra_error(self):
        """Credenciales incorrectas → permanece en login con caja de error."""
        resp = self.client.post(reverse('login'), {
            'username': 'mesero1',
            'password': 'mala_clave',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'error-box')

    def test_usuario_no_autenticado_redirige_a_login(self):
        """Sin sesión activa, /ventas/pedidos/ redirige al login."""
        resp = self.client.get(reverse('pedido_list'))
        self.assertRedirects(resp, '/accounts/login/?next=/ventas/pedidos/',
                             fetch_redirect_response=False)

    def test_logout_invalida_sesion(self):
        """Tras logout el usuario no puede acceder a páginas protegidas."""
        self.client.login(username='mesero1', password='clave123')
        self.client.post(reverse('logout'))
        resp = self.client.get(reverse('pedido_list'))
        self.assertEqual(resp.status_code, 302)  # redirige a login

    def test_rate_limiting_bloquea_tras_5_intentos(self):
        """Tras 5 intentos fallidos la respuesta contiene el aviso de bloqueo."""
        url = reverse('login')
        for _ in range(5):
            self.client.post(url, {'username': 'mesero1', 'password': 'mala'})
        # El 5.° intento (o el GET siguiente) debe mostrar el mensaje de bloqueo
        resp = self.client.get(url)
        self.assertContains(resp, 'bloqueada')

    def test_login_exitoso_limpia_contador_rate_limit(self):
        """Después de un login exitoso el contador de intentos se resetea."""
        url = reverse('login')
        # Acumular 4 intentos fallidos
        for _ in range(4):
            self.client.post(url, {'username': 'mesero1', 'password': 'mala'})
        # Login correcto
        self.client.post(url, {'username': 'mesero1', 'password': 'clave123'})
        # Logout y 4 intentos más no deben bloquear (contador fue reseteado)
        self.client.post(reverse('logout'))
        for _ in range(4):
            self.client.post(url, {'username': 'mesero1', 'password': 'mala'})
        resp = self.client.get(url)
        self.assertNotContains(resp, 'bloqueada')


# ─────────────────────────────────────────────────────────────────────────────
# RF-03: Crear Nueva Orden
# ─────────────────────────────────────────────────────────────────────────────

class CrearOrdenTest(TestCase):
    """Tests para RF-03: crear nueva orden."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('mesero2', 'm@test.com', 'clave123')
        self.client.login(username='mesero2', password='clave123')

    def test_crear_orden_exitosamente(self):
        """POST a /ventas/pedidos/nuevo/ crea un Pedido y redirige al detalle."""
        resp = self.client.post(reverse('pedido_create'), {'mesa_o_online': 'Mesa 5'})
        self.assertEqual(Pedido.objects.count(), 1)
        pedido = Pedido.objects.first()
        self.assertEqual(pedido.mesa_o_online, 'Mesa 5')
        self.assertEqual(pedido.estado, 'pendiente')
        self.assertRedirects(resp, reverse('pedido_detail', args=[pedido.pk]),
                             fetch_redirect_response=False)

    def test_crear_orden_sin_autenticar_redirige(self):
        """Sin sesión activa no se puede crear una orden."""
        self.client.logout()
        resp = self.client.post(reverse('pedido_create'), {'mesa_o_online': 'Mesa 5'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_crear_orden_muestra_mensaje_exito(self):
        """Tras crear la orden debe aparecer el mensaje de éxito en el detalle."""
        self.client.post(reverse('pedido_create'), {'mesa_o_online': 'Mesa 6'})
        pedido = Pedido.objects.first()
        resp = self.client.get(reverse('pedido_detail', args=[pedido.pk]),
                                follow=True)
        messages = list(resp.context['messages'])
        self.assertTrue(any('creada' in str(m) for m in messages))

    def test_lista_pedidos_solo_muestra_propios(self):
        """El mesero sólo ve sus propias órdenes, no las de otros."""
        otro = User.objects.create_user('otro', 'otro@test.com', 'clave123')
        Pedido.objects.create(mesa_o_online='Mesa A', creado_por=otro, estado='pendiente')
        Pedido.objects.create(mesa_o_online='Mesa B', creado_por=self.user, estado='pendiente')
        resp = self.client.get(reverse('pedido_list'))
        self.assertEqual(len(resp.context['pedidos']), 1)
        self.assertEqual(resp.context['pedidos'][0].mesa_o_online, 'Mesa B')


# ─────────────────────────────────────────────────────────────────────────────
# RF-04: Modificar Orden Activa
# ─────────────────────────────────────────────────────────────────────────────

class ModificarOrdenTest(TestCase):
    """Tests para RF-04: agregar, cambiar cantidad y eliminar productos de una orden."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('mesero3', 'm3@test.com', 'clave123')
        self.client.login(username='mesero3', password='clave123')
        categoria = Categoria.objects.create(nombre='Comidas')
        self.producto = Producto.objects.create(
            nombre='Hamburguesa', categoria=categoria, precio=12000, descripcion=''
        )
        self.pedido = Pedido.objects.create(
            mesa_o_online='Mesa 3', creado_por=self.user, estado='pendiente'
        )

    def _agregar_item(self, cantidad=1):
        self.client.post(reverse('pedido_detail', args=[self.pedido.pk]), {
            'producto': self.producto.pk,
            'cantidad': cantidad,
        })
        return PedidoProducto.objects.get(pedido=self.pedido, producto=self.producto)

    def test_agregar_producto_a_orden(self):
        """POST al detalle de pedido agrega un PedidoProducto."""
        self._agregar_item(2)
        self.assertEqual(PedidoProducto.objects.filter(pedido=self.pedido).count(), 1)
        item = PedidoProducto.objects.get(pedido=self.pedido)
        self.assertEqual(item.cantidad, 2)

    def test_incrementar_cantidad(self):
        """Botón + incrementa la cantidad del producto en 1."""
        item = self._agregar_item(1)
        self.client.post(
            reverse('pedido_item_increment', args=[self.pedido.pk, item.pk]),
            {'action': 'increment'}
        )
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 2)

    def test_decrementar_cantidad(self):
        """Botón - decrementa la cantidad del producto en 1."""
        item = self._agregar_item(3)
        self.client.post(
            reverse('pedido_item_decrement', args=[self.pedido.pk, item.pk]),
            {'action': 'decrement'}
        )
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 2)

    def test_decrementar_a_cero_elimina_item(self):
        """Al bajar la cantidad a 0 (decrement desde 1) el ítem es eliminado."""
        item = self._agregar_item(1)
        self.client.post(
            reverse('pedido_item_decrement', args=[self.pedido.pk, item.pk]),
            {'action': 'decrement'}
        )
        self.assertFalse(PedidoProducto.objects.filter(pk=item.pk).exists())

    def test_eliminar_producto_de_orden(self):
        """POST a pedido_item_delete elimina el ítem de la orden."""
        item = self._agregar_item(2)
        self.client.post(
            reverse('pedido_item_delete', args=[self.pedido.pk, item.pk])
        )
        self.assertFalse(PedidoProducto.objects.filter(pk=item.pk).exists())

    def test_no_se_puede_modificar_orden_confirmada(self):
        """Una orden confirmada (en_preparacion) no permite cambiar cantidades."""
        item = self._agregar_item(2)
        self.pedido.estado = 'en_preparacion'
        self.pedido.save()
        self.client.post(
            reverse('pedido_item_increment', args=[self.pedido.pk, item.pk]),
            {'action': 'increment'}
        )
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 2)  # sin cambios


# ─────────────────────────────────────────────────────────────────────────────
# RF-05: Confirmar Orden y Enviar a Cocina
# ─────────────────────────────────────────────────────────────────────────────

class ConfirmarOrdenTest(TestCase):
    """Tests para RF-05: confirmar orden y enviar a cocina."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('mesero4', 'm4@test.com', 'clave123')
        self.client.login(username='mesero4', password='clave123')
        categoria = Categoria.objects.create(nombre='Postres')
        self.ingrediente = Ingrediente.objects.create(nombre='Harina', stock=500)
        self.producto = Producto.objects.create(
            nombre='Torta', categoria=categoria, precio=8000, descripcion=''
        )
        ProductoIngrediente.objects.create(
            producto=self.producto, ingrediente=self.ingrediente, cantidad=50
        )
        self.pedido = Pedido.objects.create(
            mesa_o_online='Mesa 4', creado_por=self.user, estado='pendiente'
        )

    def test_no_puede_confirmar_orden_vacia(self):
        """Una orden sin productos no puede confirmarse."""
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'pendiente')

    def test_confirmar_orden_vacia_muestra_error(self):
        """Al intentar confirmar una orden vacía se muestra un mensaje de error."""
        resp = self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]),
                                follow=True)
        messages = list(resp.context['messages'])
        self.assertTrue(any('vacía' in str(m) or 'vac' in str(m) for m in messages))

    def test_confirmar_orden_con_productos_cambia_estado(self):
        """Con productos y stock suficiente la orden pasa a en_preparacion."""
        PedidoProducto.objects.create(pedido=self.pedido, producto=self.producto, cantidad=1)
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_preparacion')

    def test_orden_confirmada_aparece_en_cocina(self):
        """Una orden en_preparacion aparece en el panel de cocina."""
        PedidoProducto.objects.create(pedido=self.pedido, producto=self.producto, cantidad=1)
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        resp = self.client.get(reverse('cocina_dashboard'))
        pedidos_cocina = list(resp.context['pedidos'])
        self.assertIn(self.pedido.pk, [p.pk for p in pedidos_cocina])

    def test_no_puede_confirmar_orden_ya_confirmada(self):
        """Intentar confirmar una orden ya confirmada muestra error y no cambia estado."""
        PedidoProducto.objects.create(pedido=self.pedido, producto=self.producto, cantidad=1)
        self.pedido.estado = 'en_preparacion'
        self.pedido.save()
        resp = self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]),
                                follow=True)
        messages = list(resp.context['messages'])
        self.assertTrue(any('modificarse' in str(m) or 'estado' in str(m) for m in messages))

    def test_confirmar_sin_stock_no_cambia_estado(self):
        """Con stock insuficiente la orden permanece en pendiente."""
        self.ingrediente.stock = 10  # insuficiente para 50 requeridos
        self.ingrediente.save()
        PedidoProducto.objects.create(pedido=self.pedido, producto=self.producto, cantidad=1)
        self.client.post(reverse('pedido_confirm', args=[self.pedido.pk]))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'pendiente')


# ─────────────────────────────────────────────────────────────────────────────
# RF-11: API de Ventas
# ─────────────────────────────────────────────────────────────────────────────

class RegistrarVentaAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('apiuser', 'api@test.com', 'pass123')
        self.client.login(username='apiuser', password='pass123')
        categoria = Categoria.objects.create(nombre='Bebidas')
        self.producto = Producto.objects.create(nombre='Jugo', categoria=categoria, precio=5000)
        self.pedido = Pedido.objects.create(mesa_o_online='Mesa API', creado_por=self.user, estado='listo')
        PedidoProducto.objects.create(pedido=self.pedido, producto=self.producto, cantidad=3)

    def test_post_register_crea_transaccion(self):
        url = '/ventas/api/sales/register/'
        resp = self.client.post(url, {'pedido_id': self.pedido.id}, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Transaccion.objects.filter(pedido=self.pedido).exists())
        t = Transaccion.objects.get(pedido=self.pedido)
        self.assertEqual(t.total, self.producto.precio * 3)

    def test_post_register_sin_pedido_id(self):
        url = '/ventas/api/sales/register/'
        resp = self.client.post(url, {}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', getattr(resp, 'data', {}))

    def test_post_register_pedido_no_existe(self):
        url = '/ventas/api/sales/register/'
        resp = self.client.post(url, {'pedido_id': 9999}, format='json')
        self.assertEqual(resp.status_code, 404)
        self.assertIn('error', getattr(resp, 'data', {}))

    def test_post_register_no_duplicar_transaccion(self):
        url = '/ventas/api/sales/register/'
        # Primer registro
        resp1 = self.client.post(url, {'pedido_id': self.pedido.id}, format='json')
        self.assertEqual(resp1.status_code, 201)
        # Segundo intento (debería fallar)
        resp2 = self.client.post(url, {'pedido_id': self.pedido.id}, format='json')
        self.assertEqual(resp2.status_code, 400)
        self.assertIn('ya existe', getattr(resp2, 'data', {}).get('error', ''))
