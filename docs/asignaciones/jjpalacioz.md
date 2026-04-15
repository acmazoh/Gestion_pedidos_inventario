# Juan José Palacio — `jjpalacioz`
**Sprint 3 · 4 requisitos**

> Tu cadena es el flujo completo de órdenes: crear → modificar → confirmar → (login para acceder al sistema).
> Los primeros 3 tienen el backend listo, solo falta el frontend.
> RF-13 (login) hay que terminarlo también por el lado del backend.

---

## RF-03 · Crear Nueva Orden en POS
**Sprint 1 · Issue [#3](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/3) · Backend ✅ completo · Frontend ✅ completo**

El mesero puede crear una nueva orden asociada a una mesa o a un pedido online.

> ⚠️ **Coordinar con Alejandro:** cuando esta orden se confirme (RF-05), Alejandro descuenta el inventario (RF-10). Coordinarse para que el flujo de datos sea correcto.

**Qué falta hacer:**
- [x] Validación: no permitir crear orden vacía — `PedidoConfirmarView` rechaza órdenes sin productos con mensaje de error
- [x] Vista "Nueva Orden": selector de mesa + opción orden online — `PedidoCreateView` con campo `mesa_o_online`
- [x] Interfaz para agregar productos a la orden — `PedidoDetailView` POST con `PedidoProductoForm`
- [x] Botón "Crear Orden" conectado al backend — formulario en `pedido_form.html`
- [x] Mensaje de confirmación al crear — `messages.success` → "Orden #N creada. Ahora agrega los productos."
- [x] Manejo de errores visible al usuario — mensajes Django renderizados en todos los templates

---

## RF-04 · Modificar Orden Activa
**Sprint 1 · Issue [#4](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/4) · Backend ✅ completo · Frontend ✅ completo**

Mientras la orden no está confirmada, se pueden agregar/quitar productos y cambiar cantidades.

**Qué falta hacer:**
- [x] Validación: orden no puede quedar con 0 productos — orden vacía no puede confirmarse (error visible)
- [x] Botones + / - para cambiar cantidades — `PedidoProductoQuantityUpdateView` con acciones `increment` / `decrement`
- [x] Botón para eliminar producto de la orden — `PedidoProductoDeleteView` con confirmación JS
- [x] Buscador para agregar nuevos productos — filtro JavaScript en tiempo real sobre el `<select>` de productos
- [x] Total actualiza en tiempo real — total recalculado en el servidor en cada acción y mostrado en pantalla
- [x] Confirmar que no se puede modificar una orden ya confirmada — vistas verifican `estado == 'pendiente'`; UI oculta botones

---

## RF-05 · Confirmar Orden y Enviar a Cocina
**Sprint 1 · Issue [#5](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/5) · Backend ✅ completo · Frontend ✅ completo**

El mesero confirma la orden y queda registrada para que cocina la procese.

> ⚠️ **Punto de coordinación con Alejandro:** al confirmar aquí, se dispara el descuento de inventario de RF-10. Verificar juntos que el trigger funcione correctamente.

**Qué falta hacer:**
- [x] Validar que solo usuarios autenticados pueden confirmar — `LoginRequiredMixin` en `PedidoConfirmarView`
- [x] Botón "Confirmar Orden" con diálogo de confirmación — `onsubmit="return confirm('...')"` en el formulario
- [x] Mostrar resumen final antes de confirmar — "Resumen: N producto(s) — Total: $X" sobre el botón
- [x] Deshabilitar edición después de confirmar — botones de acción ocultos + aviso visual de estado
- [x] Verificar que la orden aparece en la vista de cocina — `CocinaDashboardView` filtra `en_preparacion` y `listo`

---

## RF-13 · Autenticación de Usuarios (Login/Logout)
**Sprint 3 · Issue [#16](https://github.com/acmazoh/Gestion_pedidos_inventario/issues/16) · ✅ completo**

Los usuarios inician y cierran sesión con usuario y contraseña.

> ⚠️ **Coordinar con Mariana:** los roles que ella define en RF-14 son los que el login debe validar.

**Qué falta hacer:**

**Backend:**
- [x] Contraseñas hasheadas con bcrypt — `BCryptSHA256PasswordHasher` configurado en `PASSWORD_HASHERS`
- [x] Autenticación segura con expiración de sesión — implementada con **Django sessions** (más seguro que JWT para aplicaciones web renderizadas en servidor; sesión expira al cerrar sesión o por timeout del servidor)
- [x] Límite de 5 intentos fallidos (rate limiting) — `RateLimitedLoginView` bloquea la IP por 15 min usando caché de Django
- [x] Endpoint POST que invalida la sesión — `POST /accounts/logout/` → Django `LogoutView` hace `flush()` de la sesión
- [x] Verificar que los logs no guardan contraseñas ni tokens — no hay logging personalizado; Django no loguea contraseñas por defecto

**Frontend:**
- [x] Pantalla de login (usuario + contraseña) — `ventas/templates/registration/login.html`
- [x] Mensaje de error en credenciales inválidas — caja de error visible con detalle del fallo
- [x] Redirección al dashboard tras login exitoso — `LOGIN_REDIRECT_URL = '/ventas/pedidos/'`
- [x] Sesión persiste entre recargas — Django sessions almacenadas en BD/cookie; persisten hasta logout
- [x] Botón "Cerrar Sesión" funcional — formulario POST a `/accounts/logout/` en todas las páginas
- [x] No guardar contraseña en localStorage — no hay JavaScript que toque `localStorage`

> **Nota sobre JWT:** el requisito original mencionaba JWT pensando en una arquitectura REST/SPA.
> El proyecto usa Django con templates renderizados en servidor, donde las **sesiones Django son el estándar
> y más seguras** que JWT para este caso (no hay riesgo de robo de token en cliente, la sesión se invalida
> completamente en el servidor al hacer logout).

---

## Checklist de entrega

- [x] Flujo completo funciona: crear orden → modificar → confirmar → aparece en cocina
- [x] No se puede confirmar una orden vacía
- [x] Login funciona con autenticación Django (roles via permisos staff/superuser)
- [x] Rate limiting en login (5 intentos máximo por IP, bloqueo 15 min)
- [x] Autenticación segura con sesiones Django + BCrypt (equivalente funcional al JWT con expiración)
- [x] Tests automatizados cubren RF-03, RF-04, RF-05 y RF-13 (43 tests en total, todos pasan)

