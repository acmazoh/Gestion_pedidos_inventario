from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    stock = models.PositiveIntegerField(default=0, help_text="Cantidad disponible en inventario")

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    nombre = models.CharField(max_length=200, db_index=True)
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
