# RF-14: Gestión de Roles de Usuarios

## Tabla de permisos por rol

| Acción / Módulo                | admin | cashier | kitchen | waiter |
|-------------------------------|:-----:|:-------:|:-------:|:------:|
| Crear usuario                 |   ✔️  |         |         |        |
| Cambiar rol/desactivar usuario|   ✔️  |         |         |        |
| Crear pedido                  |   ✔️  |   ✔️    |         |   ✔️   |
| Modificar pedido              |   ✔️  |   ✔️    |         |   ✔️   |
| Confirmar pedido              |   ✔️  |   ✔️    |         |   ✔️   |
| Ver pedidos activos           |   ✔️  |   ✔️    |   ✔️    |   ✔️   |
| Registrar venta               |   ✔️  |   ✔️    |         |        |
| Crear/editar/eliminar producto|   ✔️  |         |         |        |
| Activar/desactivar producto   |   ✔️  |         |         |        |
| Ver productos                 |   ✔️  |   ✔️    |   ✔️    |   ✔️   |
| Actualizar estado cocina      |   ✔️  |         |   ✔️    |        |

## Cómo crear y gestionar usuarios

1. Solo el administrador puede crear usuarios, asignar roles, editar roles y desactivar usuarios.
2. Para crear un usuario:
   - Endpoint: `POST /api/users/`
   - Campos: username, password, rol (admin, cashier, kitchen, waiter)
3. Para cambiar el rol de un usuario:
   - Endpoint: `PUT /api/users/{id}/`
   - Solo el admin puede cambiar el rol.
4. Para desactivar un usuario:
   - Endpoint: `DELETE /api/users/{id}/`
   - Solo el admin puede desactivar usuarios.
5. Un usuario desactivado no puede autenticarse ni operar en el sistema.

## Pruebas de integración

- El admin puede crear usuarios de cualquier rol y estos pueden iniciar sesión (RF-13).
- Un usuario no-admin no puede cambiar roles ni desactivar usuarios.
- Los permisos por rol se aplican en todos los endpoints y navegación.
- Prueba recomendada: crear 4 usuarios (admin, cashier, kitchen, waiter) y validar que cada uno solo puede hacer lo permitido.

---

> **Nota:** Si algún usuario intenta realizar una acción no permitida, recibirá un error 403 (Forbidden).
