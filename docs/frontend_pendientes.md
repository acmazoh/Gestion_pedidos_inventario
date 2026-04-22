# Checklist de pendientes de Frontend por Requisito Funcional

Este documento lista, para cada RF, lo que falta implementar, mejorar o probar en el frontend.

---

## RF-01: Gestión de Productos del Menú

- [ ] Pantalla de gestión de productos (tabla con nombre, categoría, precio)
- [ ] Formulario crear/editar producto (nombre, categoría, precio, descripción, ingredientes)
- [ ] Botón eliminar con confirmación
- [ ] Mensajes de éxito/error visibles
- [ ] Respuesta visual < 2 segundos
- [ ] Adaptable a tablet

Notas:
- El backend y los endpoints están completos y documentados.
- Solo falta la implementación visual y pruebas en frontend.

---


## RF-02: Visualizar Productos Disponibles en POS

- [x] Vista POS muestra catálogo de productos
- [x] Productos organizados por categoría
- [x] Cada producto muestra nombre y precio
- [x] Carga en < 2 segundos
- [x] Funciona en Chrome, Firefox y Edge (falta validación manual en todos)
- [x] Responsive: usable en tablet (falta validación manual)

Notas:
- Backend y endpoint GET /api/products/products/ completo y documentado.
- El frontend ahora refleja exactamente el filtrado del backend: si no hay stock, no se muestran productos.
- Validar visualmente en navegadores y dispositivos reales.

---

## RF-03: Crear Nueva Orden en POS

- [x] Vista "Nueva Orden" diseñada y conectada al backend
- [x] Selector de mesa disponible
- [x] Opción de "orden online" como alternativa
- [x] Interfaz para agregar productos a la orden
- [x] Botón "Crear Orden" conecta con backend
- [x] Mensaje de confirmación al crear
- [x] Manejo de errores visible
- [x] Orden creada aparece en la lista de pedidos y en cocina
- [x] Prueba manual: crear 3 órdenes diferentes

Notas:
- El endpoint POST `/ventas/api/orders/create/` está documentado y probado.
- El frontend refleja correctamente los pedidos creados por la API REST y por la interfaz web.
- Validar visualmente en navegadores y dispositivos reales.

---

## RF-04: Modificar Orden Activa

- [x] Lista de productos editable en la vista de orden
- [x] Botones + / - para cambiar cantidades
- [x] Botón para eliminar producto de la orden
- [x] Buscador para agregar nuevos productos
- [x] Total actualiza en tiempo real
- [x] Cambios se guardan con botón "Guardar"
- [x] No se puede modificar orden confirmada
- [x] Si eliminas el último producto, la orden se elimina automáticamente
- [x] Prueba manual: modificar una orden 5 veces

Notas:
- Endpoints disponibles:
  - POST `/ventas/api/orders/{id}/add-item/` para agregar producto
  - PATCH `/ventas/api/orders/{id}/items/{item_id}/quantity/` para cambiar cantidad
  - DELETE `/ventas/api/orders/{id}/items/{item_id}/` para eliminar producto
- El backend valida que solo se puedan modificar órdenes en estado pendiente.
- El frontend refleja los cambios en tiempo real y muestra mensajes de error si la orden queda vacía.
- Validar visualmente en navegadores y dispositivos reales.

---

## RF-05: Confirmar Orden y Enviar a Cocina

- [x] Botón "Confirmar Orden" visible en la vista de orden
- [x] Solicita confirmación antes de enviar
- [x] Muestra resumen final antes de confirmar
- [x] Redirige o muestra estado "Enviada a cocina"
- [x] Deshabilita modificación después de confirmar
- [x] Orden confirmada aparece en vista de cocina
- [x] Inventario se descuenta al confirmar
- [x] Prueba manual: confirmar 3 órdenes y verificar en cocina

Notas:
- Endpoint POST `/ventas/api/orders/{id}/confirm/` disponible para confirmar órdenes.
- El backend valida que solo se puedan confirmar órdenes pendientes y con productos.
- El frontend muestra mensajes de éxito o error según el resultado.
- El estado de la orden se actualiza y la edición queda deshabilitada tras confirmar.
- Validar visualmente en navegadores y dispositivos reales.

---

## RF-06: Calcular Total de Orden con Impuestos

- [x] Orden muestra desglose: productos, precios, cantidades
- [x] Muestra subtotal (sin impuesto)
- [x] Muestra impuesto calculado
- [x] Muestra total final
- [x] Total actualiza en tiempo real al modificar cantidades
- [x] Diseño claro y legible
- [x] Prueba manual: calcular total con 5 productos

Notas:
- Endpoint GET `/ventas/api/orders/{id}/calculate-total/` devuelve desglose y total.
- El backend aplica la tasa de impuesto configurada (`TAX_RATE`).
- El frontend refleja los cambios en tiempo real y muestra el desglose de forma clara.
- Validar visualmente en navegadores y dispositivos reales.
