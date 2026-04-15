from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Ingrediente(models.Model):
    UNIDADES = [
        ('unidad', 'Unidad'),
        ('gramo', 'Gramo'),
        ('kilogramo', 'Kilogramo'),
        ('mililitro', 'Mililitro'),
        ('litro', 'Litro'),
        ('porcion', 'Porción'),
    ]
    nombre = models.CharField(max_length=100, unique=True)
    unidad_medida = models.CharField(max_length=20, choices=UNIDADES, default='unidad')
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible en inventario")

    def __str__(self):
        return f"{self.nombre} ({self.get_unidad_medida_display()})"


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField(blank=True)
    ingredientes = models.ManyToManyField(Ingrediente)

    def __str__(self):
        return self.nombre


class ProductoIngrediente(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1, help_text="Cantidad de ingrediente necesaria por unidad de producto")

    class Meta:
        unique_together = ('producto', 'ingrediente')

    def __str__(self):
        return f"{self.cantidad} x {self.ingrediente.nombre} para {self.producto.nombre}"


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('descuento', 'Descuento por pedido'),
        ('ajuste', 'Ajuste manual'),
    ]
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField(help_text="Negativo = descuento, Positivo = entrada")
    stock_resultante = models.PositiveIntegerField(help_text="Stock después del movimiento")
    fecha = models.DateTimeField(auto_now_add=True)
    pedido_id = models.IntegerField(null=True, blank=True, help_text="ID del pedido que generó el movimiento")

    def __str__(self):
        return f"{self.fecha:%Y-%m-%d %H:%M} | {self.ingrediente.nombre} | {self.cantidad:+d}"
