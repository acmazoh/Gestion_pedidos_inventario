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

- Backend: API REST
- Base de datos: SQL
- Autenticación: JWT

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
