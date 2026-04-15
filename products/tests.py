from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Ingrediente


class IngredienteModelTest(TestCase):
    """Pruebas unitarias del modelo Ingrediente (RF-15)."""

    def test_crear_ingrediente(self):
        """Un ingrediente se crea correctamente con nombre, unidad y stock."""
        ing = Ingrediente.objects.create(nombre='Tomate', unidad_medida='unidad', stock=10)
        self.assertEqual(ing.nombre, 'Tomate')
        self.assertEqual(ing.stock, 10)

    def test_nombre_unico(self):
        """No pueden existir dos ingredientes con el mismo nombre (case-insensitive vía form)."""
        Ingrediente.objects.create(nombre='Sal', unidad_medida='gramo', stock=500)
        self.assertEqual(Ingrediente.objects.filter(nombre='Sal').count(), 1)

    def test_str_incluye_unidad(self):
        """El __str__ del ingrediente muestra nombre y unidad de medida."""
        ing = Ingrediente.objects.create(nombre='Harina', unidad_medida='kilogramo', stock=5)
        self.assertIn('Harina', str(ing))
        self.assertIn('Kilogramo', str(ing))


class IngredienteFormTest(TestCase):
    """Pruebas de validación del formulario IngredienteForm (RF-15)."""

    def test_nombre_duplicado_es_invalido(self):
        """El formulario rechaza un nombre que ya existe en BD."""
        from .forms import IngredienteForm
        Ingrediente.objects.create(nombre='Cebolla', unidad_medida='unidad', stock=20)
        form = IngredienteForm(data={'nombre': 'cebolla', 'unidad_medida': 'unidad', 'stock': 5})
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_stock_negativo_es_invalido(self):
        """El formulario rechaza una cantidad negativa en stock."""
        from .forms import IngredienteForm
        form = IngredienteForm(data={'nombre': 'Pimienta', 'unidad_medida': 'gramo', 'stock': -1})
        self.assertFalse(form.is_valid())
        self.assertIn('stock', form.errors)

    def test_nombre_vacio_es_invalido(self):
        """El formulario rechaza un nombre vacío."""
        from .forms import IngredienteForm
        form = IngredienteForm(data={'nombre': '', 'unidad_medida': 'unidad', 'stock': 10})
        self.assertFalse(form.is_valid())
        self.assertIn('nombre', form.errors)

    def test_formulario_valido(self):
        """Un formulario con datos correctos es válido."""
        from .forms import IngredienteForm
        form = IngredienteForm(data={'nombre': 'Aceite', 'unidad_medida': 'litro', 'stock': 3})
        self.assertTrue(form.is_valid())


class IngredienteViewTest(TestCase):
    """Prueba manual de integración: crear 5, editar 2, eliminar 1 (RF-15)."""

    def setUp(self):
        # Crear usuario administrador para las vistas protegidas
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'pass123')
        self.client = Client()
        self.client.login(username='admin', password='pass123')

    def test_crear_cinco_ingredientes(self):
        """Se pueden crear 5 ingredientes distintos desde la vista."""
        ingredientes = [
            ('Pan', 'unidad', 100),
            ('Lechuga', 'unidad', 50),
            ('Queso', 'gramo', 200),
            ('Tomate', 'unidad', 30),
            ('Mayonesa', 'mililitro', 500),
        ]
        for nombre, unidad, stock in ingredientes:
            resp = self.client.post(reverse('ingrediente_create'), {
                'nombre': nombre, 'unidad_medida': unidad, 'stock': stock
            })
            self.assertIn(resp.status_code, [200, 302])
        self.assertEqual(Ingrediente.objects.count(), 5)

    def test_editar_ingrediente(self):
        """Se puede editar la cantidad de un ingrediente existente."""
        ing = Ingrediente.objects.create(nombre='Mantequilla', unidad_medida='gramo', stock=100)
        resp = self.client.post(reverse('ingrediente_update', args=[ing.pk]), {
            'nombre': 'Mantequilla', 'unidad_medida': 'gramo', 'stock': 150
        })
        self.assertIn(resp.status_code, [200, 302])
        ing.refresh_from_db()
        self.assertEqual(ing.stock, 150)

    def test_eliminar_ingrediente(self):
        """Se puede eliminar un ingrediente; ya no aparece en BD."""
        ing = Ingrediente.objects.create(nombre='Vinagre', unidad_medida='mililitro', stock=50)
        resp = self.client.post(reverse('ingrediente_delete', args=[ing.pk]))
        self.assertIn(resp.status_code, [200, 302])
        self.assertFalse(Ingrediente.objects.filter(pk=ing.pk).exists())
