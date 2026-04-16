# Configuración para Django Channels - Referencia Rápida

## Paso 1: Instalar paquetes

```bash
pip install channels channels-redis daphne
```

## Paso 2: Actualizar restin/settings.py

Agrega al inicio del archivo (ANTES de INSTALLED_APPS):

```python
ASGI_APPLICATION = "restin.asgi.application"
```

Agrega `"daphne"` PRIMERO en INSTALLED_APPS:

```python
INSTALLED_APPS = [
    "daphne",  # ← DEBE SER PRIMERO
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "products",
    "ventas",
]
```

Agrega al final del archivo:

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
```

## Paso 3: Crear ventas/routing.py

```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/cocina/dashboard/$', consumers.CocinaDashboardConsumer.as_asgi()),
]
```

## Paso 4: Actualizar restin/asgi.py

Reemplaza TODO el contenido con:

```python
import os
from django.core.asgi import get_django_asgi_app
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restin.settings')
django.setup()

from ventas.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_django_asgi_app(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
```

## Paso 5: Instalar y ejecutar Redis

### Opción A: Docker (Recomendado)

```bash
docker run -d -p 6379:6379 redis:latest
```

### Opción B: Windows - WSL2

```bash
wsl --install  # Si no está instalado
wsl
sudo apt update
sudo apt install redis-server
redis-server
```

## Paso 6: Ejecutar el servidor

```bash
daphne -b 0.0.0.0 -p 8000 restin.asgi:application
```

## Verificar que funciona

1. Ve a: `http://localhost:8000/ventas/pedidos/cocina/`
2. Abre la consola (F12)
3. Deberías ver en el título: "En línea - Actualizando en tiempo real"
4. Crea una nueva orden desde el panel de mesero
5. La nueva orden debe aparecer automáticamente sin recargar

---

## Estructura de archivos (resumen)

```
restin/
├── asgi.py (MODIFICADO)
├── settings.py (MODIFICADO)
└── ...

ventas/
├── consumers.py (NUEVO)
├── routing.py (NUEVO)
├── views.py (MODIFICADO - agregada PedidosActivosAPIView)
├── urls.py (MODIFICADO - agregada ruta /api/pedidos/activos/)
└── templates/
    └── ventas/
        └── cocina_dashboard.html (REEMPLAZADO con versión mejorada)
```

---

## Verificar instalación

```bash
# Verificar que los paquetes están instalados
pip list | grep -E "channels|daphne|redis"

# Probar conexión a Redis
python -c "import redis; r = redis.Redis(); print(r.ping())"
```

Si ves `True`, Redis está funcionando correctamente.

---

## Para DESARROLLO

Puedes usar la configuración de Channels en memoria (sin Redis):

```python
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

**Nota**: Solo funciona con un único worker/proceso. Para producción, siempre usa Redis.

---

## Comandos útiles

```bash
# Ver estadísticas de Redis
redis-cli info

# Limpiar base de datos Redis
redis-cli FLUSHDB

# Ver todas las claves
redis-cli KEYS '*'

# Ver logs de Daphne
daphne --verbosity 2 restin.asgi:application
```

---

## Troubleshooting

### Error: "No module named 'channels'"
```bash
pip install channels
```

### Error: "Cannot connect to Redis"
```bash
# Verificar que Redis está ejecutándose
redis-cli ping  # Debe responder PONG

# Si no está ejecutándose, inicia Docker
docker run -d -p 6379:6379 redis:latest
```

### WebSocket aún no funciona después de configurar
1. Detén y reinicia Daphne (no es suficiente runserver)
2. Limpia caché del navegador (Ctrl+Shift+R en Chrome)
3. Revisa la consola (F12) por errores

---

Si necesitas soporte, consulta la documentación oficial en:
- https://channels.readthedocs.io/
- https://redis.io/
