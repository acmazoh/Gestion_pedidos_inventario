from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Categoria, Ingrediente, Producto, ProductoIngrediente
from .models import Pedido, PedidoProducto


class TransaccionAtomicaTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mesero1', password='clave1234')
        self.categoria = Categoria.objects.create(nombre='Bebidas')
        self.ingrediente = Ingrediente.objects.create(nombre='Agua', stock=5)
        self.producto = Producto.objects.create(
            nombre='Vaso de agua', categoria=self.categoria, precio=1000
        )
        ProductoIngrediente.objects.create(
            producto=self.producto, ingrediente=self.ingrediente, cantidad=2
        )
        self.pedido = Pedido.objects.create(
            mesa_o_online='Mesa 1', estado='pendiente', creado_por=self.user
        )
        PedidoProducto.objects.create(pedido=self.pedido, producto=self.producto, cantidad=2)

    def test_confirmar_pedido_descuenta_stock_correctamente(self):
        self.client.force_login(self.user)
        self.client.post(reverse('pedido_confirm', kwargs={'pk': self.pedido.pk}))
        self.pedido.refresh_from_db()
        self.ingrediente.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'en_preparacion')
        # Agua: stock 5 - (2 unidades x 2 cantidad pedido) = 1
        self.assertEqual(self.ingrediente.stock, 1)

    def test_confirmar_pedido_sin_stock_no_cambia_estado(self):
        self.ingrediente.stock = 1
        self.ingrediente.save()
        self.client.force_login(self.user)
        self.client.post(reverse('pedido_confirm', kwargs={'pk': self.pedido.pk}))
        self.pedido.refresh_from_db()
        self.ingrediente.refresh_from_db()
        # No debe pasar a en_preparacion ni descontar stock
        self.assertEqual(self.pedido.estado, 'pendiente')
        self.assertEqual(self.ingrediente.stock, 1)

    def test_lista_pedidos_solo_muestra_los_del_usuario(self):
        otro = User.objects.create_user(username='otro', password='1234')
        Pedido.objects.create(mesa_o_online='Mesa 99', estado='pendiente', creado_por=otro)
        self.client.force_login(self.user)
        response = self.client.get(reverse('pedido_list'))
        self.assertEqual(len(response.context['pedidos']), 1)
