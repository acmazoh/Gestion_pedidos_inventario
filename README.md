## RF-10: Descuento Automático de Inventario al Confirmar Orden

Cuando una orden es confirmada (desde el POS), el sistema descuenta automáticamente del inventario las cantidades de ingredientes usados en los productos de la orden, según las recetas definidas.

### ¿Cómo funciona?
- Al confirmar una orden, el backend recorre todos los productos y sus cantidades.
- Para cada producto, consulta su receta (`ProductoIngrediente`) y descuenta el stock de cada ingrediente involucrado.
- Si falta stock de algún ingrediente, la orden NO se confirma y se muestra un mensaje claro (ver RF-07).
- Cada descuento queda registrado en el historial de movimientos de inventario (`MovimientoInventario`), con fecha, cantidad, stock resultante y pedido asociado.

### ¿Cómo lo veo en el sistema?
- Ve a **Productos → Ingredientes** (`/products/ingredientes/`) para ver el stock actualizado tras confirmar una orden.
- Ingredientes con stock bajo (≤ 5) aparecen resaltados y con etiqueta "Stock bajo".
- Haz clic en **Movimientos** para ver el historial detallado de entradas y salidas de inventario.

### Pruebas recomendadas
1. Confirma una orden y verifica que el stock de ingredientes se descuenta correctamente.
2. Si el stock de algún ingrediente queda bajo, la alerta visual aparece en la tabla.
3. Consulta el historial de movimientos para ver el registro del descuento.

### Comentarios técnicos
- El flujo está cubierto por pruebas automáticas en `ventas/tests.py`.
- El frontend de inventario y movimientos es solo visual y no afecta otros módulos.

---
## RF-09: Actualizar Estado de Orden (Cocina) — Control de Permisos y Feedback Visual

En la vista de cocina (`/ventas/cocina/`), solo los usuarios con rol **cocina** o **admin** pueden ver y utilizar los botones para cambiar el estado de los pedidos ("Listo" y "Entregada").

### ¿Cómo funciona?
- El backend expone el rol del usuario autenticado al template.
- El frontend (JS en `cocina_dashboard.html`) solo muestra los botones de cambio de estado si el usuario tiene rol `kitchen` o `admin`.
- Si un usuario sin permisos intenta manipular el DOM o forzar el envío del formulario, el JS bloquea la acción y muestra una notificación: "No tienes permiso para cambiar el estado de la orden.".
- El backend también valida los permisos antes de procesar el cambio de estado (seguridad total).

### Pruebas recomendadas
1. Iniciar sesión como usuario con rol **cocina** o **admin**: los botones aparecen y funcionan.
2. Iniciar sesión como otro rol (mesero, cajero): los botones NO aparecen.
3. Intentar manipular el DOM para enviar el formulario: aparece notificación de error y no se envía.
4. Revisar que el backend rechaza cambios de estado si el usuario no tiene permisos (ver logs o respuesta HTTP).

### Comentarios técnicos
- El control de visibilidad y feedback visual está implementado en el JS del template `cocina_dashboard.html`.
- El backend valida el rol antes de procesar cambios de estado para máxima seguridad.

---
## RF-08: Vista de Cocina en Tiempo Real

Permite al personal de cocina visualizar en tiempo real todas las órdenes confirmadas y pendientes de preparación, con una interfaz optimizada para tablets y dispositivos de cocina.

### ¿Cómo funciona?
- Cuando una orden es confirmada en el POS, aparece automáticamente en la vista de cocina en menos de 2 segundos.
- La vista de cocina se actualiza en tiempo real mediante AJAX polling (cada 3 segundos) y puede soportar WebSocket si está habilitado.
- Cada orden se muestra como una tarjeta con:
  - Número de orden
  - Mesa o cliente
  - Hora de creación
  - Lista de productos y cantidades
  - Estado visual (en preparación, listo, entregada)
  - Botones para marcar como "Listo" o "Entregada"
- Las órdenes nuevas se resaltan con color y animación.
- El diseño es responsivo, con texto grande y alto contraste, ideal para tablets.

### Endpoints y lógica
- `GET /api/orders/kitchen/` — Devuelve todas las órdenes en estado "en_preparacion" o "listo".
- El frontend consulta este endpoint periódicamente y actualiza la vista automáticamente.
- El backend soporta tanto polling como WebSocket para notificaciones en tiempo real.

### Ejemplo de uso
1. Confirma una orden desde el POS.
2. En la vista de cocina (`/ventas/cocina/`), la nueva orden aparece automáticamente.
3. El cocinero puede marcar la orden como "Listo" o "Entregada" desde la misma interfaz.

### Diseño y usabilidad
- Interfaz clara, sin necesidad de capacitación.
- Tarjetas grandes, colores diferenciados por estado.
- Indicador visual de órdenes nuevas.
- Adaptable a pantallas de tablet y escritorio.

### Pruebas recomendadas
1. Confirmar una orden y verificar que aparece en cocina en <2 segundos.
2. Confirmar varias órdenes seguidas y verificar que todas aparecen.
3. Probar la vista en un dispositivo tablet o simulador de pantalla pequeña.

### Comentarios técnicos
- El código de actualización automática está comentado en la plantilla `cocina_dashboard.html`.
- El endpoint de backend está documentado en `ventas/api_views.py` y `ventas/consumers.py`.

---
## RF-03: Crear Nueva Orden en POS

Permite crear una nueva orden desde el POS, asociada a una mesa o identificador online, registrando el timestamp automáticamente.

#### Cómo crear una orden (paso a paso)
1. Ingresa a la vista POS y haz clic en "Nueva Orden".
2. Selecciona la mesa o ingresa el identificador online.
3. Agrega productos y cantidades.
4. Haz clic en "Crear Orden".
5. El sistema crea la orden y la muestra en la lista de pedidos y en cocina.

#### Ejemplo de petición al endpoint (Thunder Client/Postman)

POST http://localhost:8000/ventas/api/orders/create/

Headers:
- Authorization: Bearer TU_TOKEN
- Content-Type: application/json

Body:
```json
{
  "mesa_o_online": "Mesa 5",
  "productos": [
    {"producto": 1, "cantidad": 2},
    {"producto": 5, "cantidad": 1}
  ]
}
```

#### Ejemplo de respuesta
```json
{
  "id": 18,
  "mesa_o_online": "Mesa 5",
  "fecha_creacion": "2026-04-21T22:47:53.564517Z",
  "productos": [
    {"producto": "Hamburguesa Sencilla", "cantidad": 2},
    {"producto": "Coca Cola 400ml", "cantidad": 1}
  ]
}
```

#### Validaciones
- No se permite crear órdenes vacías (sin productos).
- Solo usuarios autenticados pueden crear órdenes.
- El timestamp se registra automáticamente.
- El pedido puede modificarse antes de confirmar.

#### Pruebas manuales
- Crear 3 órdenes diferentes y verificar que aparecen en la BD y en el frontend.

### ¿Cómo crear una orden paso a paso?
1. Ingresa a la vista POS y haz clic en "Nueva Orden".
2. Selecciona la mesa o ingresa el identificador online del cliente.
3. Haz clic en "Crear Orden".
4. El sistema crea la orden y te redirige al detalle para agregar productos.
5. Agrega productos y cantidades a la orden antes de confirmarla.
6. Solo puedes confirmar la orden si tiene al menos un producto.

### Validaciones y mensajes
- Solo usuarios autenticados pueden crear órdenes.
- No se permite confirmar órdenes vacías (sin productos).
- El sistema muestra mensajes de éxito y error en cada paso.

### Estructura de datos de la orden
Ejemplo de una orden en la base de datos:
```json
{
  "id": 1,
  "mesa_o_online": "Mesa 5",
  "estado": "pendiente",
  "creado_por": "mesero1",
  "fecha_creacion": "2026-04-21T15:30:00Z",
  "productos": [
    { "id": 2, "nombre": "Hamburguesa Sencilla", "cantidad": 2 },
    { "id": 5, "nombre": "Coca Cola 400ml", "cantidad": 1 }
  ]
}
```

### Notas técnicas
- El timestamp se registra automáticamente.
- El flujo es intuitivo y no requiere capacitación especial.
- Puedes modificar la orden antes de confirmarla.
- Prueba manual: crea 3 órdenes diferentes y verifica en la BD.
# Sistema de Gestión de Pedidos e Inventario

Sistema web para restaurantes que permite tomar pedidos, controlar inventario y gestionar el flujo completo desde la mesa hasta el pago.

## Funcionalidades principales

- Gestión de productos del menú
- Control de inventario con alertas de stock mínimo
- Registro y seguimiento de pedidos por mesa
- Actualización automática del stock al tomar pedidos
- Procesamiento de pagos (efectivo / tarjeta)
- Reportes de ventas e inventario
- Control de acceso por roles (Administrador, Mesero, Cajero, Cocinero)

## Tecnologías

- Backend: Django 4.2 (Python)
- Base de datos: SQLite (desarrollo)
- Autenticación: Django Auth (sesiones)

---

## Gestión de Ingredientes (RF-15)

El módulo de ingredientes está disponible para administradores en `/products/ingredientes/`.

### Estructura del ingrediente

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `nombre` | texto (máx. 100 car.) | Nombre único del ingrediente |
| `unidad_medida` | selección | Unidad en que se mide el ingrediente |
| `stock` | entero ≥ 0 | Cantidad disponible actualmente |

### Unidades de medida soportadas

| Valor interno | Etiqueta |
|---------------|----------|
| `unidad` | Unidad |
| `gramo` | Gramo |
| `kilogramo` | Kilogramo |
| `mililitro` | Mililitro |
| `litro` | Litro |
| `porcion` | Porción |

### Cómo agregar un ingrediente

1. Iniciar sesión como administrador.
2. Ir a `/products/ingredientes/`.
3. Hacer clic en **Agregar Ingrediente**.
4. Completar el formulario: nombre, unidad de medida y cantidad inicial.
5. Guardar — el ingrediente aparece en la lista y queda disponible para asignarse a productos.

### Cómo editar un ingrediente

1. En la tabla de ingredientes, hacer clic en **Editar** en la fila del ingrediente.
2. Modificar los campos deseados y guardar.
3. El stock actualizado se refleja de inmediato en la lista.

### Cómo eliminar un ingrediente

1. En la tabla, hacer clic en **Eliminar** en la fila del ingrediente.
2. Confirmar la eliminación en la pantalla de confirmación.
3. Si el ingrediente está asociado a productos, deberá desvincularse primero.

### Errores de validación

| Error | Causa | Mensaje |
|-------|-------|---------|
| Nombre duplicado | Ya existe un ingrediente con ese nombre (no distingue mayúsculas) | *"Ya existe un ingrediente con ese nombre."* |
| Stock negativo | Se ingresó un valor menor a 0 en cantidad | *"La cantidad no puede ser negativa."* |
| Nombre vacío | El campo nombre es obligatorio | *"Este campo es obligatorio."* |

---

## Relación Producto ↔ Ingredientes (Recetas)

Cada **Producto** del menú tiene una receta definida por la tabla intermedia `ProductoIngrediente`.
Esta tabla especifica **cuántas unidades de cada ingrediente** se necesitan para preparar una unidad del producto.

### Modelo de datos

```
Producto (nombre, categoría, precio)
    │
    └─ ProductoIngrediente (cantidad)  ←── define la receta
            │
            └─ Ingrediente (nombre, unidad_medida, stock)
```

- `Ingrediente.stock` = cantidad disponible actualmente en inventario.
- `Ingrediente.unidad_medida` = gramo, kilogramo, litro, mililitro, unidad, porción.
- `ProductoIngrediente.cantidad` = cuántas unidades del ingrediente consume una unidad del producto.

### Flujo de descuento de inventario

Cuando un pedido se **confirma** (`estado: pendiente → en_preparacion`):

1. El sistema recorre todos los productos del pedido y sus cantidades.
2. Para cada producto, consulta su receta en `ProductoIngrediente`.
3. Calcula el total de cada ingrediente requerido: `cantidad_receta × cantidad_pedida`.
4. Verifica que haya stock suficiente para **todos** los ingredientes antes de confirmar.
5. Si falta stock: muestra un error con el ingrediente, cantidad requerida y faltante.
6. Si hay stock: descuenta el stock de cada `Ingrediente` y registra un `MovimientoInventario`.

### MovimientoInventario

Cada descuento queda registrado en `MovimientoInventario` con:
- Ingrediente afectado
- Cantidad descontada (negativa)
- Stock resultante tras el movimiento
- ID del pedido que lo originó
- Fecha y hora

El historial es visible en `/products/ingredientes/movimientos/`.

### Errores al confirmar una orden (RF-10)

Si al confirmar una orden falta stock de algún ingrediente, el sistema **no confirma** la orden y muestra una alerta por cada ingrediente con problema:

| Campo mostrado | Descripción |
|----------------|-------------|
| Ingrediente | Nombre del ingrediente sin stock suficiente |
| Requerido | Cantidad total necesaria para cubrir el pedido |
| Disponible | Stock actual en inventario |
| Faltante | Diferencia entre requerido y disponible |
| Productos | Qué productos del pedido usan ese ingrediente |

La orden permanece en estado `pendiente` y el stock **no se modifica** hasta que haya suficiente inventario.

---

## Historial de Ventas (RF-11)

### Cómo ver el historial de ventas

1. Iniciar sesión en el sistema.
2. Ir a `/ventas/ventas/historial/`.
3. Por defecto muestra todas las ventas registradas, ordenadas de más reciente a más antigua.
4. Usar los campos **Desde** y **Hasta** para filtrar por rango de fechas y hacer clic en **Filtrar**.
5. Para exportar el historial filtrado en CSV, hacer clic en el botón **Exportar CSV**.

### Estructura de la Transacción

Cada venta queda registrada en el modelo `Transaccion` con los siguientes campos:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `pedido` | OneToOne FK | Referencia única al pedido que generó la venta |
| `total` | decimal (10,2) | Suma de `precio × cantidad` de todos los productos del pedido |
| `fecha` | datetime | Timestamp automático del momento en que se registró la venta |

Los productos y cantidades vendidas se consultan desde `pedido.items` (tabla `PedidoProducto`).

### Cuándo se registra una transacción

La transacción se crea automáticamente cuando el cocinero marca un pedido como **Entregada** (estado `listo → entregada`). El sistema usa `get_or_create` para garantizar que no se duplique si la acción se ejecuta más de una vez.

### Errores del historial de ventas (RF-11)

| Error | Causa | Comportamiento |
|-------|-------|----------------|
| Transacción duplicada | Se intenta registrar una venta para un pedido que ya tiene transacción | Sistema ignora silenciosamente el duplicado (`get_or_create`) |
| Sin ventas en el período | No hay transacciones en el rango de fechas seleccionado | Muestra mensaje *"No hay ventas registradas en ese período."* |

---

## Vista de Cocina en Tiempo Real (RF-08)

La vista de cocina proporciona una interfaz en tiempo real para que el personal de cocina visualice y gestione los pedidos activos sin necesidad de recargar la página.

### Cómo funciona

1. **Acceso**: Los usuarios con rol de cocinero pueden acceder a la vista en `/ventas/cocina/`.
2. **Actualización automática**: La página se actualiza automáticamente cada 3 segundos mediante AJAX polling para mostrar nuevos pedidos en tiempo real.
3. **Visualización de pedidos**:
   - Los pedidos se muestran como tarjetas visuales con diseño moderno.
   - Cada tarjeta incluye: mesa/cliente, hora de creación, lista de productos con cantidades, y estado actual.
   - Los pedidos nuevos (creados hace menos de 30 segundos) se destacan con color rojo y animación.
4. **Estados de los pedidos**:
   - **En preparación** (naranja): Pedido confirmado y en proceso.
   - **Listo** (verde): Pedido preparado y listo para entrega.
5. **Interacción**:
   - El cocinero puede cambiar el estado de un pedido haciendo clic en los botones correspondientes.
   - Al marcar como "Listo", el pedido pasa a estado `entregada` y se registra la transacción de venta.
6. **Notificaciones**: Aparecen alertas emergentes cuando llegan nuevos pedidos.
7. **Diseño responsivo**: Funciona en dispositivos de escritorio y móviles.
8. **Optimización**: La actualización se pausa cuando la pestaña no está activa para ahorrar recursos.



---

## Equipo de desarrollo

| Integrante | Usuario | Contribuciones |
|------------|---------|----------------|
| Alejandro Correa | `alejo180905` | CRUD de ingredientes (RF-15), descuento automático de inventario al confirmar orden (RF-10), registro de transacciones e historial de ventas con filtro por fecha (RF-11) |

---

## Documentación del Proyecto

### 📋 Requisitos y Sprints

| Documento | Descripción |
|-----------|-------------|
| [📌 Resumen Asesoría Sprint 2](docs/requisitos/resumen_asesoria_sprint2.md) | **Documento principal para la asesoría** — estado del sprint, historias comprometidas y criterios de aceptación |
| [📋 Requisitos Sprint 2](docs/requisitos/requisitos_sprint2.md) | Historias de usuario priorizadas (MoSCoW), backlog de tareas y Definition of Done |
| [📦 Product Backlog](docs/requisitos/product_backlog.md) | Backlog completo del producto con épicas, prioridades y planificación de sprints |

### 📐 Diagramas (Segunda Entrega)

| Diagrama | Descripción |
|----------|-------------|
| [Casos de Uso](docs/diagramas/diagrama_casos_uso.md) | Actores del sistema y sus interacciones principales |
| [Clases](docs/diagramas/diagrama_clases.md) | Modelo de objetos del dominio y sus relaciones |
| [Secuencia](docs/diagramas/diagrama_secuencia.md) | Flujos detallados: login, registro de pedido, pago |
| [Actividades](docs/diagramas/diagrama_actividades.md) | Flujo del proceso completo de un pedido |
| [Entidad-Relación](docs/diagramas/diagrama_entidad_relacion.md) | Modelo de base de datos |

---

## RF-01: Gestión de Productos del Menú

**Asignado a:** Andrés Camilo Mazo (acmazoh)
**Sprint:** 1
**Prioridad:** Alta

### Descripción
Permite a un administrador crear, actualizar y eliminar productos del menú, incluyendo nombre, categoría, precio, descripción e ingredientes asociados.

### Endpoints principales

- `POST /api/products/` — Crear producto
- `PUT /api/products/{id}/` — Actualizar producto
- `DELETE /api/products/{id}/` — Eliminar producto

#### Ejemplo: Crear producto

```http
POST /api/products/
Content-Type: application/json
Authorization: Bearer <token>

{
  "nombre": "Pizza Margarita",
  "categoria_id": 1,
  "precio": 25000,
  "descripcion": "Pizza clásica con tomate y queso",
  "ingrediente_ids": [1, 2, 3]
}
```

#### Ejemplo de respuesta exitosa

```json
{
  "id": 5,
  "nombre": "Pizza Margarita",
  "categoria": { "id": 1, "nombre": "Pizzas" },
  "precio": "25000.00",
  "descripcion": "Pizza clásica con tomate y queso",
  "disponible": true,
  "ingredientes": [
    { "id": 1, "nombre": "Queso" },
    { "id": 2, "nombre": "Tomate" }
  ],
  "receta": [
    { "ingrediente_id": 1, "ingrediente_nombre": "Queso", "cantidad": 100 },
    { "ingrediente_id": 2, "ingrediente_nombre": "Tomate", "cantidad": 50 }
  ]
}
```

#### Validaciones y errores
- Nombre único: `{"nombre": ["Ya existe un producto con este nombre."]}`
- Precio mayor a 0: `{"precio": ["El precio debe ser mayor a 0."]}`

### Pruebas manuales sugeridas
- Crear 3 productos distintos
- Editar 2 productos
- Eliminar 1 producto
- Verificar asociación de ingredientes

### Notas técnicas
- El modelo y los endpoints están optimizados con `select_related` y `prefetch_related`.
- Los errores se devuelven en formato JSON con mensajes claros.
- Ver código en `products/api_views.py` y `products/serializers.py` para detalles de validaciones y lógica.

---

## RF-02: Visualizar Productos Disponibles en POS

**Asignado a:** Andrés Camilo Mazo (acmazoh)
**Sprint:** 1
**Prioridad:** Alta

### Descripción
Permite mostrar en la interfaz POS solo los productos activos y con ingredientes disponibles en inventario.

### Endpoint principal

- `GET /api/products/?disponible=true` — Lista productos activos y con stock suficiente

#### Ejemplo de petición
```http
GET /api/products/?disponible=true
Authorization: Bearer <token>
```

#### Ejemplo de respuesta
```json
[
  {
    "id": 1,
    "nombre": "Pizza Margarita",
    "categoria": { "id": 1, "nombre": "Pizzas" },
    "precio": "25000.00",
    "descripcion": "Pizza clásica con tomate y queso",
    "disponible": true
  },
  ...
]
```

#### Notas
- Solo aparecen productos con disponible=True y cuyos ingredientes tienen stock > 0.
- Ordenados por categoría y nombre.
- Si un producto no aparece, revisa el stock de sus ingredientes.

#### Validaciones y errores
- Si no hay productos disponibles: retorna lista vacía `[]`.
- Si el token es inválido: error 401.

### Pruebas manuales sugeridas
- Crear productos con ingredientes en stock y sin stock, verificar que solo aparecen los que cumplen la condición.
- Probar con más de 20 productos.

### Notas técnicas
- Consulta optimizada con `select_related` y `prefetch_related`.
- Lógica de filtrado en `products/api_views.py`.
