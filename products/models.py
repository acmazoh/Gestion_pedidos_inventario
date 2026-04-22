from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Ingrediente(models.Model):
    UNIDAD_CHOICES = [
        ('unidad', 'Unidad'),
        ('gramo', 'Gramo'),
        ('kilogramo', 'Kilogramo'),
        ('mililitro', 'Mililitro'),
        ('litro', 'Litro'),
        ('porcion', 'Porción'),
    ]
    nombre = models.CharField(max_length=100, unique=True)
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible en inventario")
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default='unidad')

    def __str__(self):
        return self.nombre



class Producto(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    ingredientes = models.ManyToManyField(Ingrediente, blank=True, related_name="productos")
    disponible = models.BooleanField(default=True, help_text="¿El producto está activo para ventas?")

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


# Modelo restaurado para registro de movimientos de inventario
class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('descuento', 'Descuento'),
        ('ajuste', 'Ajuste'),
        ('ingreso', 'Ingreso'),
    ]
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField(help_text="Cantidad de movimiento, negativo para descuento")
    stock_resultante = models.IntegerField(help_text="Stock después del movimiento")
    pedido_id = models.IntegerField(null=True, blank=True, help_text="ID del pedido relacionado si aplica")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} {self.cantidad} {self.ingrediente.nombre} (Pedido {self.pedido_id})"
