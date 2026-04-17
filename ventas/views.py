# Exportar historial de ventas a CSV
from django.http import HttpResponse
import csv

def historial_ventas_csv(request):
    desde = request.GET.get('desde')
    hasta = request.GET.get('hasta')
    transacciones = Transaccion.objects.all().select_related('pedido')
    if desde:
        transacciones = transacciones.filter(fecha__date__gte=desde)
    if hasta:
        transacciones = transacciones.filter(fecha__date__lte=hasta)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="historial_ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(['Fecha', 'Pedido', 'Mesa / Cliente', 'Productos', 'Total'])
    for t in transacciones.order_by('-fecha'):
        productos = ', '.join([
            f"{item.producto.nombre} x{item.cantidad}"
            for item in t.pedido.items.select_related('producto').all()
        ])
        writer.writerow([
            t.fecha.strftime('%d/%m/%Y %H:%M'),
            t.pedido.id,
            getattr(t.pedido, 'mesa_o_online', ''),
            productos,
            f"${t.total}"
        ])
    return response

from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Sum
from products.models import Producto, Categoria
from .models import Pedido, PedidoProducto, Transaccion
from .forms import PedidoForm, PedidoProductoForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

# Historial de ventas
class HistorialVentasView(LoginRequiredMixin, View):
    template_name = 'ventas/historial_ventas.html'

    def get(self, request):
        desde = request.GET.get('desde')
        hasta = request.GET.get('hasta')
        transacciones = Transaccion.objects.all().select_related('pedido')
        if desde:
            transacciones = transacciones.filter(fecha__date__gte=desde)
        if hasta:
            transacciones = transacciones.filter(fecha__date__lte=hasta)
        total_periodo = transacciones.aggregate(total=Sum('total'))['total'] or 0
        return render(request, self.template_name, {
            'transacciones': transacciones.order_by('-fecha'),
            'desde': desde,
            'hasta': hasta,
            'total_periodo': total_periodo,
        })

# Cambiar estado de pedido desde cocina
class MarcarListoView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'en_preparacion':
            pedido.estado = 'listo'
            pedido.save()
        return redirect('cocina_dashboard')


class MarcarEntregadoView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'listo':
            pedido.estado = 'pagado'
            pedido.save()
            # Registrar transacción
            total = 0
            for item in pedido.items.select_related('producto'):
                total += item.producto.precio * item.cantidad
            Transaccion.objects.create(pedido=pedido, total=total)
        return redirect('cocina_dashboard')


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


class PedidoProductoDeleteView(LoginRequiredMixin, View):
    def post(self, request, pedido_pk, item_pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pedido_pk, creado_por=request.user)
        if pedido.estado != 'pendiente':
            return redirect('pedido_detail', pk=pedido_pk)
        item = get_object_or_404(PedidoProducto, pk=item_pk, pedido=pedido)
        item.delete()
        return redirect('pedido_detail', pk=pedido_pk)


class PedidoProductoQuantityUpdateView(LoginRequiredMixin, View):
    def post(self, request, pedido_pk, item_pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pedido_pk, creado_por=request.user)
        if pedido.estado != 'pendiente':
            return redirect('pedido_detail', pk=pedido_pk)
        item = get_object_or_404(PedidoProducto, pk=item_pk, pedido=pedido)
        action = request.POST.get('action')

        if action == 'increment':
            item.cantidad += 1
            item.save()
        elif action == 'decrement':
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                # eliminar si se reduce por debajo de 1
                item.delete()
        return redirect('pedido_detail', pk=pedido_pk)


class PedidoConfirmarView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk, creado_por=request.user)

        # Solo puede confirmarse un pedido pendiente con al menos un producto.
        if pedido.estado != 'pendiente' or not pedido.items.exists():
            return redirect('pedido_detail', pk=pk)

        # Calcular requisitos de ingredientes para el pedido completo
        required_per_ingredient = {}
        ingredient_products = {}

        for item in pedido.items.select_related('producto'):
            receta = list(item.producto.productoingrediente_set.select_related('ingrediente'))
            if receta:
                for pi in receta:
                    required = pi.cantidad * item.cantidad
                    required_per_ingredient.setdefault(pi.ingrediente, 0)
                    required_per_ingredient[pi.ingrediente] += required
                    ingredient_products.setdefault(pi.ingrediente, set()).add(item.producto.nombre)
            else:
                for ingrediente in item.producto.ingredientes.all():
                    required_per_ingredient.setdefault(ingrediente, 0)
                    required_per_ingredient[ingrediente] += item.cantidad
                    ingredient_products.setdefault(ingrediente, set()).add(item.producto.nombre)

        shortages = []
        for ingrediente, required in required_per_ingredient.items():
            if ingrediente.stock < required:
                shortages.append({
                    'ingrediente': ingrediente,
                    'required': required,
                    'available': ingrediente.stock,
                    'missing': required - ingrediente.stock,
                    'productos': sorted(ingredient_products.get(ingrediente, [])),
                })

        if shortages:
            # Render detail view with error info
            items = list(pedido.items.select_related('producto'))
            for item in items:
                item.subtotal = item.producto.precio * item.cantidad
            total = sum(item.subtotal for item in items)
            return render(request, 'ventas/pedido_detail.html', {
                'pedido': pedido,
                'form': PedidoProductoForm(),
                'items': items,
                'total': total,
                'confirm_errors': shortages,
            })

        # Si hay suficiencia, descontar stock y confirmar.
        for ingrediente, required in required_per_ingredient.items():
            ingrediente.stock -= required
            ingrediente.save()

        pedido.estado = 'en_preparacion'
        pedido.save()
        return redirect('pedido_detail', pk=pk)


class CocinaDashboardView(LoginRequiredMixin, ListView):
    """Interfaz de cocina: muestra los pedidos confirmados en tiempo real."""

    model = Pedido
    template_name = 'ventas/cocina_dashboard.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        # Mostrar pedidos que fueron confirmados (en preparación).
        return super().get_queryset().filter(estado='en_preparacion').order_by('fecha_creacion')
