from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Ingrediente


class IngredienteCrudTests(TestCase):
	def setUp(self):
		self.admin_user = User.objects.create_user(username='admin', password='1234', is_staff=True)
		self.normal_user = User.objects.create_user(username='normal', password='1234')
		self.ingrediente = Ingrediente.objects.create(nombre='Tomate', stock=20)

	def test_admin_puede_crear_ingrediente(self):
		self.client.force_login(self.admin_user)
		response = self.client.post(reverse('ingrediente_create'), {'nombre': 'Queso', 'stock': 15})

		self.assertEqual(response.status_code, 302)
		self.assertTrue(Ingrediente.objects.filter(nombre='Queso', stock=15).exists())

	def test_admin_puede_actualizar_ingrediente(self):
		self.client.force_login(self.admin_user)
		response = self.client.post(
			reverse('ingrediente_update', kwargs={'pk': self.ingrediente.pk}),
			{'nombre': 'Tomate Cherry', 'stock': 10},
		)

		self.assertEqual(response.status_code, 302)
		self.ingrediente.refresh_from_db()
		self.assertEqual(self.ingrediente.nombre, 'Tomate Cherry')
		self.assertEqual(self.ingrediente.stock, 10)

	def test_admin_puede_eliminar_ingrediente(self):
		self.client.force_login(self.admin_user)
		response = self.client.post(reverse('ingrediente_delete', kwargs={'pk': self.ingrediente.pk}))

		self.assertEqual(response.status_code, 302)
		self.assertFalse(Ingrediente.objects.filter(pk=self.ingrediente.pk).exists())

	def test_usuario_no_admin_no_puede_acceder_crud(self):
		self.client.force_login(self.normal_user)
		response = self.client.get(reverse('ingrediente_list'))

		self.assertEqual(response.status_code, 302)
