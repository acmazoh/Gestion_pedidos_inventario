from django import forms
from products.models import Producto
from .models import Pedido


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['mesa_o_online']
        labels = {
            'mesa_o_online': 'Número de mesa o ID de pedido en línea',
        }


class PedidoProductoForm(forms.Form):
    producto = forms.ModelChoiceField(queryset=Producto.objects.all(), label='Producto')
    cantidad = forms.IntegerField(min_value=1, initial=1, label='Cantidad')


class PagoPedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['metodo_pago']
        labels = {
            'metodo_pago': 'Método de pago',
        }
