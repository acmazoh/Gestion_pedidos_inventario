from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['mesa_o_online']
        labels = {
            'mesa_o_online': 'Número de mesa o ID de pedido en línea',
        }