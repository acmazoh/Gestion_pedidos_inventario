from django.contrib import admin
from .models import Pedido

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa_o_online', 'estado', 'metodo_pago', 'creado_por', 'cobrado_por', 'fecha_creacion', 'fecha_pago')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('mesa_o_online', 'creado_por__username')
