# Andrés Camilo Mazo — `acmazoh`
**Sprint 3 · 4 requisitos · Carga reducida (~70%)**

> Andrés desarrolló todo el backend de los sprints anteriores.
> Su trabajo aquí es **verificar que el backend funcione** y **completar el frontend** de sus 4 RFs.

---

## RF-01 · Gestión de Productos del Menú
**Sprint 1 · Issue [#1](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/1) · Backend ✅ completo**

El admin puede crear, editar y eliminar productos del menú (nombre, categoría, precio, ingredientes).

**Qué falta hacer:**
- [ ] Verificar validaciones: nombre único, precio > 0
- [ ] Pantalla de gestión de productos (tabla + formulario)
- [ ] Botón eliminar con confirmación
- [ ] Mensajes de éxito/error visibles
- [ ] Documentar en README cómo crear/editar/eliminar productos

---

## RF-02 · Visualizar Productos Disponibles en POS
**Sprint 1 · Issue [#2](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/2) · Backend ✅ completo**

La interfaz POS muestra los productos activos organizados por categoría.

**Qué falta hacer:**
- [ ] Filtrar productos sin stock o inactivos desde el backend
- [ ] Vista POS con lista de productos por categoría
- [ ] Verificar que carga en < 2 segundos
- [ ] Probar en Chrome, Firefox y Edge
- [ ] Verificar que es usable en tablet

---

## RF-06 · Calcular Total de Orden con Impuestos
**Sprint 2 · Issue [#7](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/7) · Backend ✅ completo**

Al confirmar una orden se calcula el total automáticamente (precio × cantidad + impuestos).

**Qué falta hacer:**
- [ ] Implementar descuentos si existen
- [ ] Vista mostrando desglose: productos, precios, subtotal, impuesto, total
- [ ] Total se actualiza en tiempo real al cambiar cantidades
- [ ] Documentar fórmula de cálculo y tasa de impuesto en README

---

## RF-07 · Validar Stock al Confirmar Orden
**Sprint 2 · Issue [#8](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/8) · Backend ✅ completo**

Si no hay suficiente inventario, el sistema bloquea la confirmación y muestra qué ingrediente falta.

> ⚠️ **Coordinar con Alejandro:** RF-15 debe tener ingredientes cargados para que esta validación funcione.

**Qué falta hacer:**
- [ ] Verificar que valida múltiples ingredientes a la vez
- [ ] Mensaje de error claro: "Ingrediente X insuficiente para Producto Y"
- [ ] Mostrar cantidad disponible vs cantidad necesaria
- [ ] Opción de quitar el producto afectado de la orden
- [ ] Documentar en README qué pasa cuando no hay stock

---

## Checklist de entrega

- [ ] RF-01 frontend funcional
- [ ] RF-02 probado en 3 navegadores
- [ ] RF-06 cálculo correcto con impuestos y decimales
- [ ] RF-07 validación de stock funciona con ingredientes reales
- [ ] README actualizado
