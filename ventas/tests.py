from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Ingrediente, Producto, Categoria, ProductoIngrediente, MovimientoInventario
from .models import Pedido, PedidoProducto, Transaccion


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
