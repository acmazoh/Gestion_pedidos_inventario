# Mariana Patiño — `Maripatino`
**Sprint 3 · 3 requisitos**

> Tu trabajo cubre la interfaz de cocina (RF-08 y RF-09) y la gestión de roles de usuario (RF-14).
> RF-08 y RF-09 tienen el backend listo, solo falta el frontend.
> RF-14 hay que terminarlo tanto en backend como en frontend.

---

## RF-08 · Vista de Cocina en Tiempo Real
**Sprint 2 · Issue [#9](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/9) · Backend ✅ completo**

Cuando Juan José confirma una orden, el personal de cocina la ve aparecer automáticamente en su pantalla, sin necesidad de recargar.

**Qué falta hacer:**
- [ ] Implementar polling o WebSocket para actualización en tiempo real
- [ ] Vista de cocina diseñada (diferente a la vista POS del mesero)
- [ ] Tarjetas por orden: mesa, lista de productos, cantidades
- [ ] Órdenes nuevas aparecen automáticamente (sin F5)
- [ ] Indicador visual: órdenes nuevas vs órdenes en proceso
- [ ] Diseño con texto grande y alto contraste (se usa en cocina a distancia)
- [ ] Verificar que funciona en tablet
- [ ] Probar que la orden aparece en < 2 segundos de ser confirmada

---

## RF-09 · Actualizar Estado de Orden (Cocina)
**Sprint 2 · Issue [#10](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/10) · Backend ✅ completo**

El personal de cocina puede cambiar el estado de una orden: Confirmada → En preparación → Lista → Entregada.

> ⚠️ **Importante:** cuando se marca como "Entregada", Alejandro necesita que eso dispare el registro en el historial de ventas (RF-11). Coordinar que el trigger esté conectado.

**Qué falta hacer:**
- [ ] Validar que solo rol cocina/admin puede cambiar estados
- [ ] Botones de estado visibles en cada tarjeta de orden
- [ ] Flujo visual claro: En preparación → Lista → Entregada
- [ ] Confirmación antes de marcar como "Entregada"
- [ ] Estado cambia visualmente de inmediato al actualizar
- [ ] Verificar que el timestamp de cambio de estado se guarda

---

## RF-14 · Gestionar Roles de Usuarios
**Sprint 3 · Issue [#17](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/17) · Backend 🟡 parcial**

El administrador puede crear usuarios y asignarles roles: admin, mesero, cocina, cajero.

> ⚠️ **Coordinar con Juan José:** los roles que definas aquí son los que RF-13 (login) valida al entrar al sistema. Acordar los nombres exactos de los roles.

**Qué falta hacer:**

**Backend:**
- [ ] Endpoint PUT `/api/users/{id}` — cambiar rol de usuario
- [ ] Endpoint DELETE `/api/users/{id}` — desactivar usuario
- [ ] Validar que solo el admin puede cambiar roles
- [ ] Definir y aplicar permisos por rol en todos los módulos

**Frontend:**
- [ ] Panel de administración de usuarios
- [ ] Tabla: nombre, rol, estado (activo/inactivo)
- [ ] Formulario para crear nuevo usuario con selector de rol
- [ ] Opción para editar rol de usuario existente
- [ ] Opción para desactivar usuario con confirmación

---

## Checklist de entrega

- [ ] Vista de cocina muestra órdenes en tiempo real (< 2 seg)
- [ ] Flujo de estados completo funciona: En preparación → Lista → Entregada
- [ ] Al marcar "Entregada" se registra en historial de ventas (coordinar con Alejandro)
- [ ] RF-14: CRUD de usuarios con roles funcionando
- [ ] Rol cocina/admin es el único que puede cambiar estados de orden
- [ ] Los roles de RF-14 son compatibles con el login de Juan José (RF-13)
