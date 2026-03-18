from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Producto, Categoria, Ingrediente
from .forms import ProductoForm, IngredienteForm

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


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class IngredienteListView(ListView):
    model = Ingrediente
    template_name = 'products/ingrediente_list.html'
    context_object_name = 'ingredientes'


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class IngredienteCreateView(CreateView):
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'products/ingrediente_form.html'
    success_url = reverse_lazy('ingrediente_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class IngredienteUpdateView(UpdateView):
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'products/ingrediente_form.html'
    success_url = reverse_lazy('ingrediente_list')


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin), name='dispatch')
class IngredienteDeleteView(DeleteView):
    model = Ingrediente
    template_name = 'products/ingrediente_confirm_delete.html'
    success_url = reverse_lazy('ingrediente_list')
