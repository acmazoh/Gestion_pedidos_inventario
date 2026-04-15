import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from products.models import Producto, Categoria, MovimientoInventario
from .models import Pedido, PedidoProducto, Transaccion
from .forms import PedidoForm, PedidoProductoForm


# ── RF-13: Autenticación ─────────────────────────────────────────────────────

class RateLimitedLoginView(LoginView):
    """Login con rate limiting: bloquea IP tras 5 intentos fallidos por 15 min."""

    template_name = 'registration/login.html'
    _MAX_ATTEMPTS = 5
    _BLOCK_SECONDS = 900  # 15 minutos

    def _cache_key(self):
        ip = self.request.META.get('HTTP_X_FORWARDED_FOR', self.request.META.get('REMOTE_ADDR', 'unknown'))
        ip = ip.split(',')[0].strip()
        return f'login_attempts_{ip}'

    def get(self, request, *args, **kwargs):
        key = self._cache_key()
        attempts = cache.get(key, 0)
        if attempts >= self._MAX_ATTEMPTS:
            remaining = cache.ttl(key) if hasattr(cache, 'ttl') else self._BLOCK_SECONDS
            form = AuthenticationForm()
            return render(request, self.template_name, {
                'form': form,
                'rate_limited': True,
            })
        return super().get(request, *args, **kwargs)

    def form_invalid(self, form):
        key = self._cache_key()
        attempts = cache.get(key, 0) + 1
        cache.set(key, attempts, self._BLOCK_SECONDS)
        if attempts >= self._MAX_ATTEMPTS:
            return render(self.request, self.template_name, {
                'form': form,
                'rate_limited': True,
            })
        form.error_messages['invalid_login'] = (
            f'Usuario o contraseña incorrectos. '
            f'Intentos restantes: {self._MAX_ATTEMPTS - attempts}.'
        )
        return super().form_invalid(form)

    def form_valid(self, form):
        # Limpiar contador al iniciar sesión exitosamente
        cache.delete(self._cache_key())
        return super().form_valid(form)


# ── RF-03/04/05: Ventas ──────────────────────────────────────────────────────


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
        response = super().form_valid(form)
        messages.success(self.request, f'Orden #{self.object.pk} creada. Ahora agrega los productos.')
        return response

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
        if pedido.estado != 'pendiente':
            messages.error(request, 'Esta orden ya no puede modificarse (estado: {}).'.format(
                pedido.get_estado_display()))
            return redirect('pedido_detail', pk=pk)
        if not pedido.items.exists():
            messages.error(request, 'No puedes confirmar una orden vacía. Agrega al menos un producto.')
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
            MovimientoInventario.objects.create(
                ingrediente=ingrediente,
                tipo='descuento',
                cantidad=-required,
                stock_resultante=ingrediente.stock,
                pedido_id=pedido.pk,
            )

        pedido.estado = 'en_preparacion'
        pedido.save()
        messages.success(request, f'Orden #{pedido.pk} confirmada y enviada a cocina.')
        return redirect('pedido_detail', pk=pk)


class CocinaDashboardView(LoginRequiredMixin, ListView):
    """Interfaz de cocina: muestra los pedidos confirmados en tiempo real."""

    model = Pedido
    template_name = 'ventas/cocina_dashboard.html'
    context_object_name = 'pedidos'

    def get_queryset(self):
        # Mostrar pedidos que fueron confirmados (en preparación) y listos.
        return super().get_queryset().filter(
            estado__in=['en_preparacion', 'listo']
        ).order_by('fecha_creacion')


class PedidoMarcarListoView(LoginRequiredMixin, View):
    """Cocina marca el pedido como 'listo'."""
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'en_preparacion':
            pedido.estado = 'listo'
            pedido.save()
        return redirect('cocina_dashboard')


class PedidoMarcarEntregadaView(LoginRequiredMixin, View):
    """Marca el pedido como 'entregada' y registra la Transaccion automáticamente (RF-11)."""
    def post(self, request, pk, *args, **kwargs):
        pedido = get_object_or_404(Pedido, pk=pk)
        if pedido.estado == 'listo':
            pedido.estado = 'entregada'
            pedido.save()
            total = sum(
                item.producto.precio * item.cantidad
                for item in pedido.items.select_related('producto')
            )
            Transaccion.objects.get_or_create(pedido=pedido, defaults={'total': total})
        return redirect('cocina_dashboard')


class HistorialVentasView(LoginRequiredMixin, ListView):
    """Historial de ventas (RF-11)."""
    model = Transaccion
    template_name = 'ventas/historial_ventas.html'
    context_object_name = 'transacciones'
    paginate_by = 20

    def get_queryset(self):
        qs = Transaccion.objects.select_related('pedido').order_by('-fecha')
        fecha_desde = self.request.GET.get('desde')
        fecha_hasta = self.request.GET.get('hasta')
        if fecha_desde:
            qs = qs.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__date__lte=fecha_hasta)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['desde'] = self.request.GET.get('desde', '')
        context['hasta'] = self.request.GET.get('hasta', '')
        context['total_periodo'] = sum(t.total for t in self.get_queryset())
        # Adjuntar items a cada transacción para mostrarlos en el template
        for t in context['transacciones']:
            t.items_pedido = t.pedido.items.select_related('producto').all()
        return context


class ExportarHistorialCSVView(LoginRequiredMixin, View):
    """Exporta el historial de ventas filtrado por fecha en formato CSV (RF-11).
    Acepta los mismos parámetros ?desde= y ?hasta= que HistorialVentasView.
    Genera un archivo descargable con una fila por producto vendido.
    """
    def get(self, request, *args, **kwargs):
        qs = Transaccion.objects.select_related('pedido').order_by('-fecha')
        fecha_desde = request.GET.get('desde')
        fecha_hasta = request.GET.get('hasta')
        if fecha_desde:
            qs = qs.filter(fecha__date__gte=fecha_desde)
        if fecha_hasta:
            qs = qs.filter(fecha__date__lte=fecha_hasta)

        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="historial_ventas.csv"'
        # BOM para compatibilidad con Excel
        response.write('\ufeff')

        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Pedido', 'Mesa/Cliente', 'Producto', 'Cantidad', 'Total pedido'])

        for t in qs:
            items = t.pedido.items.select_related('producto').all()
            for item in items:
                writer.writerow([
                    t.fecha.strftime('%d/%m/%Y %H:%M'),
                    f'#{t.pedido.id}',
                    t.pedido.mesa_o_online,
                    item.producto.nombre,
                    item.cantidad,
                    t.total,
                ])

        return response
