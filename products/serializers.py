from rest_framework import serializers
from .models import Producto, Categoria, Ingrediente, ProductoIngrediente


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre']


class IngredienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingrediente
        fields = ['id', 'nombre', 'stock', 'unidad_medida']


class ProductoIngredienteSerializer(serializers.ModelSerializer):
    ingrediente_id = serializers.IntegerField(source='ingrediente.id', read_only=True)
    ingrediente_nombre = serializers.CharField(source='ingrediente.nombre', read_only=True)

    class Meta:
        model = ProductoIngrediente
        fields = ['ingrediente_id', 'ingrediente_nombre', 'cantidad']


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer completo con categoría anidada e ingredientes."""
    categoria = CategoriaSerializer(read_only=True)
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=Categoria.objects.all(), source='categoria', write_only=True
    )
    ingredientes = IngredienteSerializer(many=True, read_only=True)
    ingrediente_ids = serializers.PrimaryKeyRelatedField(
        queryset=Ingrediente.objects.all(),
        many=True,
        source='ingredientes',
        write_only=True,
        required=False,
    )
    receta = ProductoIngredienteSerializer(
        source='productoingrediente_set', many=True, read_only=True
    )

    class Meta:
        model = Producto
        fields = [
            'id', 'nombre', 'categoria', 'categoria_id',
            'precio', 'descripcion', 'disponible',
            'ingredientes', 'ingrediente_ids', 'receta',
        ]

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a 0.")
        return value

    def validate_nombre(self, value):
        # Validar nombre único (excluir el propio objeto en updates)
        qs = Producto.objects.filter(nombre__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Ya existe un producto con este nombre.")
        return value

    def create(self, validated_data):
        ingredientes = validated_data.pop('ingredientes', [])
        producto = Producto.objects.create(**validated_data)
        producto.ingredientes.set(ingredientes)
        return producto

    def update(self, instance, validated_data):
        ingredientes = validated_data.pop('ingredientes', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredientes is not None:
            instance.ingredientes.set(ingredientes)
        return instance
