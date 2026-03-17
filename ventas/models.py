from django.db import models
from django.contrib.auth.models import User

class Pedido(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_preparacion', 'En Preparación'),
        ('listo', 'Listo'),
        ('pagado', 'Pagado'),
    ]

    mesa_o_online = models.CharField(max_length=100, help_text="Número de mesa o identificador de pedido en línea")
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.mesa_o_online}"
