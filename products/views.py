from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Producto, Categoria, Ingrediente, MovimientoInventario
from .forms import ProductoForm, IngredienteForm

STOCK_MINIMO = 5  # Umbral para alerta de bajo stock

def is_admin(user):
    return user.is_staff

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class ProductoListView(ListView):
    model = Producto
    template_name = 'products/producto_list.html'
    context_object_name = 'productos'

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'products/producto_form.html'
    success_url = reverse_lazy('producto_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'products/producto_form.html'
    success_url = reverse_lazy('producto_list')

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'products/producto_confirm_delete.html'
    success_url = reverse_lazy('producto_list')


# --- Vistas de Ingredientes (RF-15) ---
# Todas las vistas requieren autenticación y rol administrador (is_staff).
# Rutas base: /products/ingredientes/

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class IngredienteListView(ListView):
    """Lista todos los ingredientes con su stock actual.
    Pasa STOCK_MINIMO al contexto para que el template muestre alertas visuales.
    Ruta: GET /products/ingredientes/
    """
    model = Ingrediente
    template_name = 'products/ingrediente_list.html'
    context_object_name = 'ingredientes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Umbral de alerta: ingredientes con stock <= STOCK_MINIMO se marcan en rojo
        context['stock_minimo'] = STOCK_MINIMO
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class IngredienteCreateView(CreateView):
    """Crea un nuevo ingrediente con nombre, unidad de medida y stock inicial.
    La validación del formulario asegura nombre único y cantidad >= 0.
    Ruta: GET/POST /products/ingredientes/create/
    """
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'products/ingrediente_form.html'
    success_url = reverse_lazy('ingrediente_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class IngredienteUpdateView(UpdateView):
    """Actualiza los datos de un ingrediente existente.
    Permite modificar nombre, unidad de medida y stock.
    Ruta: GET/POST /products/ingredientes/<pk>/update/
    """
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'products/ingrediente_form.html'
    success_url = reverse_lazy('ingrediente_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class IngredienteDeleteView(DeleteView):
    """Elimina un ingrediente tras confirmación del administrador.
    Muestra pantalla de confirmación antes de ejecutar el borrado.
    Ruta: GET/POST /products/ingredientes/<pk>/delete/
    """
    model = Ingrediente
    template_name = 'products/ingrediente_confirm_delete.html'
    success_url = reverse_lazy('ingrediente_list')


# --- Vista historial de movimientos de inventario (RF-10) ---

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class MovimientoInventarioListView(ListView):
    model = MovimientoInventario
    template_name = 'products/movimiento_list.html'
    context_object_name = 'movimientos'
    paginate_by = 30

    def get_queryset(self):
        return MovimientoInventario.objects.select_related('ingrediente').order_by('-fecha')
