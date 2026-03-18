from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AutenticacionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='mesero1', password='clave1234')

    def test_pagina_login_accesible(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario')
        self.assertContains(response, 'Contraseña')

    def test_login_con_credenciales_validas(self):
        response = self.client.post(reverse('login'), {
            'username': 'mesero1',
            'password': 'clave1234',
        })
        self.assertRedirects(response, '/ventas/')

    def test_login_con_credenciales_invalidas(self):
        response = self.client.post(reverse('login'), {
            'username': 'mesero1',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_usuario_no_autenticado_redirige_a_login(self):
        response = self.client.get(reverse('pedido_list'))
        self.assertRedirects(response, '/login/?next=/ventas/pedidos/')

    def test_logout_cierra_sesion_y_redirige(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('logout'))
        self.assertRedirects(response, '/login/')
        response = self.client.get(reverse('pedido_list'))
        self.assertEqual(response.status_code, 302)
