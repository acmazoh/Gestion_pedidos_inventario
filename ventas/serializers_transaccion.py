from rest_framework import serializers
from .models import Transaccion, PedidoProducto

class TransaccionProductoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    class Meta:
        model = PedidoProducto
        fields = ['producto_nombre', 'cantidad']

class TransaccionSerializer(serializers.ModelSerializer):
    productos = serializers.SerializerMethodField()
    class Meta:
        model = Transaccion
        fields = ['id', 'pedido', 'productos', 'total', 'fecha']

    def get_productos(self, obj):
        items = obj.pedido.items.select_related('producto').all()
        return TransaccionProductoSerializer(items, many=True).data
