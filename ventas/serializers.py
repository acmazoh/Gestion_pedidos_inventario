from rest_framework import serializers
from .models import Pedido, PedidoProducto

class PedidoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoProducto
        fields = ['producto', 'cantidad']

class PedidoCreateSerializer(serializers.ModelSerializer):
    productos = PedidoProductoSerializer(many=True, write_only=True)

    class Meta:
        model = Pedido
        fields = ['id', 'mesa_o_online', 'productos']

    def create(self, validated_data):
        productos_data = validated_data.pop('productos', [])
        pedido = Pedido.objects.create(**validated_data)
        for item in productos_data:
            PedidoProducto.objects.create(pedido=pedido, **item)
        return pedido


# Serializador para mostrar los productos de un pedido (detalle)
class PedidoItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)

    class Meta:
        model = PedidoProducto
        fields = ['id', 'producto', 'producto_nombre', 'cantidad']


# Serializador para mostrar el pedido completo (detalle)
class PedidoSerializer(serializers.ModelSerializer):
    items = PedidoItemSerializer(many=True, read_only=True, source='items')

    class Meta:
        model = Pedido
        fields = ['id', 'mesa_o_online', 'estado', 'fecha_creacion', 'items']
