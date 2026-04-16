from decimal import Decimal
from rest_framework import serializers
from products.serializers import ProductoSerializer
from .models import Pedido, PedidoProducto
from django.conf import settings


TAX_RATE = Decimal(str(getattr(settings, 'TAX_RATE', 0.19)))


class PedidoItemSerializer(serializers.ModelSerializer):
    """Un ítem dentro de un pedido con subtotal calculado."""
    producto = ProductoSerializer(read_only=True)
    producto_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('products.models', fromlist=['Producto']).Producto.objects.all(),
        source='producto',
        write_only=True,
    )
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = PedidoProducto
        fields = ['id', 'producto', 'producto_id', 'cantidad', 'subtotal']

    def get_subtotal(self, obj):
        return round(float(obj.producto.precio) * obj.cantidad, 2)


class PedidoSerializer(serializers.ModelSerializer):
    """
    Pedido con ítems, subtotal, impuesto y total.
    RF-06: desglose en tiempo real.
    """
    items = PedidoItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    impuesto = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    creado_por = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'mesa_o_online', 'estado', 'creado_por',
            'fecha_creacion', 'items', 'subtotal', 'impuesto', 'total',
        ]
        read_only_fields = ['estado', 'creado_por', 'fecha_creacion']

    def _subtotal_decimal(self, obj):
        return sum(
            Decimal(str(item.producto.precio)) * item.cantidad
            for item in obj.items.select_related('producto')
        )

    def get_subtotal(self, obj):
        return round(float(self._subtotal_decimal(obj)), 2)

    def get_impuesto(self, obj):
        return round(float(self._subtotal_decimal(obj) * TAX_RATE), 2)

    def get_total(self, obj):
        sub = self._subtotal_decimal(obj)
        return round(float(sub + sub * TAX_RATE), 2)
