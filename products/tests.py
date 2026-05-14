from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from products.models import Categoria, Ingrediente, Producto, ProductoIngrediente
from users.models import Role


class IngredienteDeleteGuardTest(TestCase):
	def setUp(self):
		self.staff_user = User.objects.create_user('admin_web', password='clave123', is_staff=True)
		self.client.login(username='admin_web', password='clave123')

		self.role_admin = Role.objects.create(name='admin', permissions={})
		self.api_user = User.objects.create_user('admin_api', password='clave123')
		self.api_user.userprofile.role = self.role_admin
		self.api_user.userprofile.is_active = True
		self.api_user.userprofile.save()

		self.categoria = Categoria.objects.create(nombre='Pruebas')
		self.ingrediente_ligado = Ingrediente.objects.create(nombre='Tomate', stock=10)
		self.producto = Producto.objects.create(
			nombre='Producto Test', categoria=self.categoria, precio=1000
		)
		ProductoIngrediente.objects.create(
			producto=self.producto,
			ingrediente=self.ingrediente_ligado,
			cantidad=1,
		)
		self.ingrediente_libre = Ingrediente.objects.create(nombre='Cebolla', stock=10)

	def test_no_elimina_ingrediente_ligado_en_vista_web(self):
		resp = self.client.post(reverse('ingrediente_delete', args=[self.ingrediente_ligado.pk]))
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(Ingrediente.objects.filter(pk=self.ingrediente_ligado.pk).exists())

	def test_si_elimina_ingrediente_no_ligado_en_vista_web(self):
		resp = self.client.post(reverse('ingrediente_delete', args=[self.ingrediente_libre.pk]))
		self.assertEqual(resp.status_code, 302)
		self.assertFalse(Ingrediente.objects.filter(pk=self.ingrediente_libre.pk).exists())

	def test_no_elimina_ingrediente_ligado_en_api(self):
		api_client = APIClient()
		api_client.force_authenticate(user=self.api_user)

		url = f'/api/products/ingredients/{self.ingrediente_ligado.pk}/'
		resp = api_client.delete(url)

		self.assertEqual(resp.status_code, 409)
		self.assertTrue(Ingrediente.objects.filter(pk=self.ingrediente_ligado.pk).exists())

	def test_si_elimina_ingrediente_no_ligado_en_api(self):
		api_client = APIClient()
		api_client.force_authenticate(user=self.api_user)

		url = f'/api/products/ingredients/{self.ingrediente_libre.pk}/'
		resp = api_client.delete(url)

		self.assertEqual(resp.status_code, 204)
		self.assertFalse(Ingrediente.objects.filter(pk=self.ingrediente_libre.pk).exists())
