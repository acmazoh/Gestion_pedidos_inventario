# RF-13: Autenticación de Usuarios (Login/Logout)

## Descripción
Permite a los usuarios iniciar y cerrar sesión en el sistema Restin POS usando credenciales únicas. Cumple requisitos de seguridad y usabilidad.

---

## Endpoints Backend

### Login
- **POST** `/api/auth/login`
- **Body:**
  ```json
  {
    "username": "usuario",
    "password": "contraseña"
  }
  ```
- **Respuesta:**
  ```json
  {
    "refresh": "...",
    "access": "..."
  }
  ```
- **Errores:**
  - 401: Credenciales inválidas
  - 429: Demasiados intentos fallidos (espera 15 minutos)

### Logout
- **POST** `/api/auth/logout`
- **Headers:**
  - Authorization: Bearer ACCESS_TOKEN
- **Body:**
  ```json
  {
    "refresh": "REFRESH_TOKEN"
  }
  ```
- **Respuesta:**
  - 205: Sesión cerrada correctamente
  - 400: Token inválido o ya bloqueado

---

## Política de Contraseñas
- Contraseñas almacenadas con **bcrypt** (hash seguro)
- Validador de longitud mínima y fortaleza
- No se almacenan ni transmiten contraseñas en texto plano

---

## Estructura del JWT
- **access**: Token corto para autenticación (expira en 30 días)
- **refresh**: Token largo para renovar sesión (expira en 60 días)
- Payload típico:
  ```json
  {
    "token_type": "access",
    "exp": 1745251200,
    "jti": "...",
    "user_id": 1
  }
  ```

---

## Cómo crear usuario (admin)
1. Desde el admin de Django (`/admin/`) o vía endpoint de creación de usuario si tienes permisos.
2. El usuario debe tener un rol asignado y estar activo.

---

## Flujo de Frontend
- Pantalla de login con campos usuario y contraseña
- Botón "Iniciar Sesión" envía petición a `/api/auth/login`
- Si es exitoso, guarda los tokens en memoria segura (no localStorage)
- Si es error, muestra mensaje claro
- Tras login, redirige al dashboard
- Botón "Cerrar Sesión" envía refresh token a `/api/auth/logout` y elimina los tokens

---

## Seguridad
- Rate limiting: máximo 5 intentos fallidos por usuario/IP cada 15 minutos
- JWT con expiración
- No se guardan contraseñas en localStorage ni logs

---

## Pruebas
- Login correcto → acceso
- Login incorrecto → error
- Rate limiting → bloquea tras 5 intentos
- Logout → invalida refresh token
- Token expirado → requiere login de nuevo
