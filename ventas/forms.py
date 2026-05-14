from django import forms
from django.db.models import Exists, F, OuterRef
from products.models import Producto
from products.models import ProductoIngrediente
from .models import Pedido


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['mesa_o_online']
        labels = {
            'mesa_o_online': 'Número de mesa o ID de pedido en línea',
        }


class PedidoProductoForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.none(), label='Producto')
    cantidad = forms.IntegerField(min_value=1, initial=1, label='Cantidad')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        faltantes = ProductoIngrediente.objects.filter(
            producto=OuterRef('pk'),
            ingrediente__stock__lt=F('cantidad'),
        )
        queryset = (
            Producto.objects.filter(disponible=True, productoingrediente__isnull=False)
            .annotate(tiene_faltante=Exists(faltantes))
            .filter(tiene_faltante=False)
            .select_related('categoria')
            .order_by('categoria__nombre', 'nombre')
            .distinct()
        )
        self.fields['producto'].queryset = queryset
