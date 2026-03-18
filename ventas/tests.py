from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Pedido


class PedidoCobroTests(TestCase):
	def setUp(self):
		self.cajero_group = Group.objects.create(name='Cajero')
		self.mesero = User.objects.create_user(username='mesero', password='1234')
		self.cajero = User.objects.create_user(username='cajero', password='1234')
		self.cajero.groups.add(self.cajero_group)
		self.otro_usuario = User.objects.create_user(username='otro', password='1234')

		self.pedido = Pedido.objects.create(
			mesa_o_online='Mesa 10',
			estado='en_preparacion',
			creado_por=self.mesero,
		)

	def test_cajero_puede_registrar_pago_efectivo(self):
		self.client.force_login(self.cajero)
		response = self.client.post(
			reverse('pedido_cobrar', kwargs={'pk': self.pedido.pk}),
			{'metodo_pago': 'efectivo'},
		)

		self.assertEqual(response.status_code, 302)
		self.pedido.refresh_from_db()
		self.assertEqual(self.pedido.estado, 'pagado')
		self.assertEqual(self.pedido.metodo_pago, 'efectivo')
		self.assertIsNotNone(self.pedido.fecha_pago)
		self.assertEqual(self.pedido.cobrado_por, self.cajero)

	def test_no_permite_cobrar_pedido_ya_pagado(self):
		self.pedido.estado = 'pagado'
		self.pedido.metodo_pago = 'tarjeta'
		self.pedido.save()

		self.client.force_login(self.cajero)
		response = self.client.post(
			reverse('pedido_cobrar', kwargs={'pk': self.pedido.pk}),
			{'metodo_pago': 'efectivo'},
		)

		self.assertEqual(response.status_code, 302)
		self.pedido.refresh_from_db()
		self.assertEqual(self.pedido.metodo_pago, 'tarjeta')

	def test_usuario_sin_rol_cajero_no_puede_cobrar(self):
		self.client.force_login(self.otro_usuario)
		response = self.client.post(
			reverse('pedido_cobrar', kwargs={'pk': self.pedido.pk}),
			{'metodo_pago': 'tarjeta'},
		)

		self.assertEqual(response.status_code, 403)
		self.pedido.refresh_from_db()
		self.assertEqual(self.pedido.estado, 'en_preparacion')
