from django.contrib import admin
from .models import Pedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa_o_online', 'estado', 'creado_por', 'fecha_creacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('mesa_o_online', 'creado_por__username')
