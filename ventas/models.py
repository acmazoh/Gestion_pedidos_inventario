from django.db import models
from django.contrib.auth.models import User
from products.models import Producto


class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo'),
        ('pagado', 'Pagado'),
    ]

    mesa_o_online = models.CharField(max_length=100, help_text="Cliente")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    productos = models.ManyToManyField(Producto, through='PedidoProducto', blank=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.mesa_o_online}"


class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('pedido', 'producto')

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Pedido {self.pedido.id})"
