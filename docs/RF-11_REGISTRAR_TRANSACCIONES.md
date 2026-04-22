# RF-11: Registrar Transacciones en Historial de Ventas

## Descripción
Cuando una orden se marca como entregada, el sistema registra automáticamente una transacción en el historial de ventas, incluyendo:
- ID de la orden
- Productos vendidos y cantidades
- Fecha y hora (timestamp)
- Total de la venta

## Flujo de Negocio
1. El cocinero o responsable marca el pedido como "entregada" desde la vista de cocina.
2. El sistema crea automáticamente una transacción asociada a ese pedido (si no existe).
3. La transacción aparece en el historial de ventas y en el panel de administración.

## Endpoints y Vistas
- **Automático:**
  - POST `/ventas/pedidos/<pk>/entregada/` (desde la web, botón "Entregada")
  - Backend: `PedidoMarcarEntregadaView` crea la transacción automáticamente.
- **Manual/API:**
  - POST `/ventas/api/sales/register/` (requiere autenticación JWT)
  - Body: `{ "pedido_id": <id> }`
  - Respuesta: datos de la transacción creada

## Validaciones
- No se puede crear más de una transacción por pedido.
- Si ya existe una transacción para ese pedido, no se duplica.
- Si el pedido no existe o no está en estado válido, retorna error.

## Ejemplo de Transacción
```json
{
  "id": 5,
  "pedido": 1,
  "productos": [
    { "producto_nombre": "Hamburguesa Sencilla", "cantidad": 3 }
  ],
  "total": 15000,
  "fecha": "2026-04-21T15:30:00Z"
}
```

## Errores posibles
- 400: Ya existe transacción para ese pedido
- 404: Pedido no encontrado
- 401: No autenticado (API)

## Historial de Ventas
- Vista: `/ventas/ventas/historial/`
- Exportar CSV: `/ventas/ventas/historial/exportar/`
- Filtros por fecha disponibles en la vista

## Pruebas
- Marcar pedido como entregada crea transacción automáticamente
- No se duplican transacciones
- Aparece en historial y admin
- Prueba manual: completar 3 órdenes y verificar en historial

---
**Desarrollador:** Alejandro Correa (alejo180905)
**Sprint:** 3
**Prioridad:** Alta
