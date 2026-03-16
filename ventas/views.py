from django.shortcuts import render
from django.views.generic import ListView
from products.models import Producto, Categoria

class ProductoVentaListView(ListView):
    model = Producto
    template_name = 'ventas/producto_venta_list.html'
    context_object_name = 'productos'

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all()
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            try:
                context['categoria_seleccionada'] = Categoria.objects.get(id=categoria_id)
            except Categoria.DoesNotExist:
                pass
        return context
