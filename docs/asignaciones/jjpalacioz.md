# Juan José Palacio — `jjpalacioz`
**Sprint 3 · 4 requisitos**

> Tu cadena es el flujo completo de órdenes: crear → modificar → confirmar → (login para acceder al sistema).
> Los primeros 3 tienen el backend listo, solo falta el frontend.
> RF-13 (login) hay que terminarlo también por el lado del backend.

---

## RF-03 · Crear Nueva Orden en POS
**Sprint 1 · Issue [#3](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/3) · Backend ✅ completo**

El mesero puede crear una nueva orden asociada a una mesa o a un pedido online.

> ⚠️ **Coordinar con Alejandro:** cuando esta orden se confirme (RF-05), Alejandro descuenta el inventario (RF-10). Coordinarse para que el flujo de datos sea correcto.

**Qué falta hacer:**
- [ ] Validación: no permitir crear orden vacía
- [ ] Vista "Nueva Orden": selector de mesa + opción orden online
- [ ] Interfaz para agregar productos a la orden
- [ ] Botón "Crear Orden" conectado al backend
- [ ] Mensaje de confirmación al crear
- [ ] Manejo de errores visible al usuario

---

## RF-04 · Modificar Orden Activa
**Sprint 1 · Issue [#4](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/4) · Backend ✅ completo**

Mientras la orden no está confirmada, se pueden agregar/quitar productos y cambiar cantidades.

**Qué falta hacer:**
- [ ] Validación: orden no puede quedar con 0 productos
- [ ] Botones + / - para cambiar cantidades
- [ ] Botón para eliminar producto de la orden
- [ ] Buscador para agregar nuevos productos
- [ ] Total actualiza en tiempo real
- [ ] Confirmar que no se puede modificar una orden ya confirmada

---

## RF-05 · Confirmar Orden y Enviar a Cocina
**Sprint 1 · Issue [#5](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/5) · Backend ✅ completo**

El mesero confirma la orden y queda registrada para que cocina la procese.

> ⚠️ **Punto de coordinación con Alejandro:** al confirmar aquí, se dispara el descuento de inventario de RF-10. Verificar juntos que el trigger funcione correctamente.

**Qué falta hacer:**
- [ ] Validar que solo usuarios autenticados con rol mesero/admin pueden confirmar
- [ ] Botón "Confirmar Orden" con diálogo de confirmación
- [ ] Mostrar resumen final antes de confirmar
- [ ] Deshabilitar edición después de confirmar
- [ ] Verificar que la orden aparece en la vista de cocina (RF-08 de Mariana)

---

## RF-13 · Autenticación de Usuarios (Login/Logout)
**Sprint 3 · Issue [#16](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/16) · Backend 🟡 parcial**

Los usuarios inician y cierran sesión con usuario y contraseña.

> ⚠️ **Coordinar con Mariana:** los roles que ella define en RF-14 son los que el login debe validar.

**Qué falta hacer:**

**Backend:**
- [ ] Contraseñas hasheadas con bcrypt
- [ ] Retornar JWT con fecha de expiración
- [ ] Límite de 5 intentos fallidos (rate limiting)
- [ ] Endpoint POST `/api/auth/logout` que invalida la sesión
- [ ] Verificar que los logs no guardan contraseñas ni tokens

**Frontend:**
- [ ] Pantalla de login (usuario + contraseña)
- [ ] Mensaje de error en credenciales inválidas
- [ ] Redirección al dashboard tras login exitoso
- [ ] Sesión persiste entre recargas
- [ ] Botón "Cerrar Sesión" funcional
- [ ] No guardar contraseña en localStorage

---

## Checklist de entrega

- [ ] Flujo completo funciona: crear orden → modificar → confirmar → aparece en cocina
- [ ] No se puede confirmar una orden vacía
- [ ] Login funciona con los roles de Mariana (RF-14)
- [ ] Rate limiting en login (5 intentos máximo)
- [ ] JWT con expiración configurada
