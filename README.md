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
