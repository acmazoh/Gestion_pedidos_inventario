"""
Consumidores WebSocket para la vista de cocina en tiempo real.

Permite que los cocineros vean actualizaciones instantáneas de nuevas órdenes
sin necesidad de hacer polling AJAX. Requiere Django Channels.

Instalación:
    pip install channels channels-redis daphne

Configuración en restin/settings.py:
    1. Agregar a INSTALLED_APPS: 'daphne', 'ventas'
    2. En la parte superior: ASGI_APPLICATION = "restin.asgi.application"
    3. CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [("127.0.0.1", 6379)],
            },
        },
    }

Configuración en restin/asgi.py:
    Ver el archivo asgi.py actualizado en la documentación.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from channels.db import database_sync_to_async
from ventas.models import Pedido


class CocinaDashboardConsumer(AsyncWebsocketConsumer):
    """
    Consumidor WebSocket para el panel de cocina.
    Mantiene una conexión abierta y envía actualizaciones en tiempo real.
    """

    async def connect(self):
        """Se ejecuta cuando un cliente WebSocket se conecta."""
        # Verificar autenticación
        if not self.scope["user"].is_authenticated:
            await self.close()
            return

        # Agregar usuario a un grupo de "cocina"
        await self.channel_layer.group_add(
            "cocina_dashboard",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        """Se ejecuta cuando el cliente se desconecta."""
        await self.channel_layer.group_discard(
            "cocina_dashboard",
            self.channel_name
        )

    async def receive(self, text_data):
        """Se ejecuta cuando el cliente envía un mensaje."""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'request_update':
                # El cliente solicita una actualización
                pedidos_data = await self.get_pedidos_activos()
                await self.send(text_data=json.dumps({
                    'type': 'pedidos_update',
                    'pedidos': pedidos_data,
                    'timestamp': timezone.now().isoformat(),
                    'total': len(pedidos_data),
                }))
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Formato de JSON inválido'}))

    async def pedidos_update(self, event):
        """
        Evento personalizado para enviar actualizaciones de pedidos.
        Se dispara cuando hay nuevos pedidos en el grupo.
        """
        await self.send(text_data=json.dumps({
            'type': 'pedidos_update',
            'pedidos': event['pedidos'],
            'timestamp': event['timestamp'],
            'total': event['total'],
        }))

    async def pedido_cambio_estado(self, event):
        """
        Evento para notificar cambios de estado en un pedido específico.
        """
        await self.send(text_data=json.dumps({
            'type': 'pedido_cambio_estado',
            'pedido_id': event['pedido_id'],
            'nuevo_estado': event['nuevo_estado'],
            'mensaje': event['mensaje'],
        }))

    @database_sync_to_async
    def get_pedidos_activos(self):
        """
        Obtiene los pedidos activos desde la BD de forma async.
        """
        pedidos = Pedido.objects.filter(
            estado__in=['en_preparacion', 'listo']
        ).order_by('fecha_creacion')

        pedidos_data = []
        ahora = timezone.now()

        for pedido in pedidos:
            items = []
            for item in pedido.items.select_related('producto'):
                items.append({
                    'id': item.id,
                    'producto': item.producto.nombre,
                    'cantidad': item.cantidad,
                })

            segundos_transcurridos = (ahora - pedido.fecha_creacion).total_seconds()
            es_nuevo = segundos_transcurridos < 30

            pedidos_data.append({
                'id': pedido.id,
                'mesa_o_online': pedido.mesa_o_online,
                'estado': pedido.estado,
                'fecha_creacion': pedido.fecha_creacion.isoformat(),
                'hora_formateada': pedido.fecha_creacion.strftime('%H:%M'),
                'items': items,
                'es_nuevo': es_nuevo,
                'total_items': len(items),
            })

        return pedidos_data
