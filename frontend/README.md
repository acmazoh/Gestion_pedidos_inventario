# Frontend - Autenticación de Usuarios (RF-13)

## Pantalla de Login
- Campos: usuario y contraseña
- Botón "Iniciar Sesión" envía POST a `/api/auth/login`
- Muestra mensajes claros en caso de error (credenciales inválidas, bloqueado, etc)
- Redirige al dashboard tras login exitoso

## Persistencia de Sesión
- Guarda los tokens JWT (`access`, `refresh`) en memoria segura (no localStorage)
- Si el token expira, solicita login de nuevo

## Logout
- Botón "Cerrar Sesión" envía POST a `/api/auth/logout` con el refresh token y el access token en el header
- Elimina los tokens del almacenamiento seguro

## Seguridad
- No guarda contraseñas en localStorage ni en logs
- No muestra datos sensibles en consola

## Pruebas Manuales
- Login correcto: acceso al sistema
- Login incorrecto: mensaje de error
- Rate limiting: bloquea tras 5 intentos
- Logout: sesión cerrada correctamente

## Gestión de usuarios y roles (RF-14)

### ¿Quién puede acceder?
- Solo el usuario con rol **admin** puede ver y acceder al panel de administración de usuarios.

### ¿Qué puede hacer el admin?
- Ver la tabla de usuarios con nombre, rol y estado (activo/inactivo).
- Crear un nuevo usuario (formulario con username, password y selector de rol).
- Editar el rol de un usuario existente (solo admin puede cambiar roles).
- Desactivar un usuario (con confirmación).

### ¿Qué NO pueden hacer cashier, kitchen ni waiter?
- No pueden acceder al panel de usuarios ni ver la tabla de usuarios.
- No pueden crear, editar ni desactivar usuarios.

### Flujo recomendado en frontend
1. El admin accede al panel de usuarios desde el menú de administración.
2. Puede ver la lista de usuarios, su rol y estado.
3. Puede crear un usuario nuevo usando el formulario y seleccionando el rol.
4. Puede editar el rol de un usuario existente (excepto el suyo propio).
5. Puede desactivar un usuario (con confirmación).
6. Los cambios se reflejan inmediatamente en la tabla.

### Pruebas manuales sugeridas
- El admin puede crear, editar y desactivar usuarios.
- Un usuario cashier/kitchen/waiter no puede acceder al panel ni a los endpoints de gestión de usuarios (recibe error 403).
- Si un usuario es desactivado, no puede volver a iniciar sesión.

---

> **Nota:** Si el frontend detecta un error 403, debe mostrar un mensaje claro: "No tiene permisos para realizar esta acción".
