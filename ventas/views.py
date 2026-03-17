from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Producto, Categoria
from .models import Pedido, PedidoProducto
from .forms import PedidoForm, PedidoProductoForm


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


class PedidoCreateView(LoginRequiredMixin, CreateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'ventas/pedido_form.html'

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('pedido_detail', kwargs={'pk': self.object.pk})


class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'ventas/pedido_list.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        # Show only orders created by the current user
        return super().get_queryset().filter(creado_por=self.request.user)


class PedidoDetailView(LoginRequiredMixin, ListView):
    model = PedidoProducto
    template_name = 'ventas/pedido_detail.html'
    context_object_name = 'items'

    def get(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk, creado_por=request.user)
        form = PedidoProductoForm()
        items = list(pedido.items.select_related('producto'))
        for item in items:
            item.subtotal = item.producto.precio * item.cantidad
        total = sum(item.subtotal for item in items)
        return render(request, self.template_name, {
            'pedido': pedido,
            'form': form,
            'items': items,
            'total': total,
        })

    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk, creado_por=request.user)
        form = PedidoProductoForm(request.POST)
        if form.is_valid():
            producto = form.cleaned_data['producto']
            cantidad = form.cleaned_data['cantidad']
            item, created = PedidoProducto.objects.get_or_create(
                pedido=pedido,
                producto=producto,
                defaults={'cantidad': cantidad},
            )
            if not created:
                item.cantidad += cantidad
                item.save()
            return redirect('pedido_detail', pk=pedido.pk)

        items = list(pedido.items.select_related('producto'))
        for item in items:
            item.subtotal = item.producto.precio * item.cantidad
        total = sum(item.subtotal for item in items)
        return render(request, self.template_name, {
            'pedido': pedido,
            'form': form,
            'items': items,
            'total': total,
        })
