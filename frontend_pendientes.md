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

(Agrega aquí cada RF a medida que los revisemos)
