# Frontend — Sistema POS Restaurante

> **Módulos implementados por Andres Mazo (acmazoh)**
> RF-01 · RF-02 · RF-06 · RF-07

## Tecnologías

| Herramienta | Versión |
|-------------|---------|
| React | 18 |
| TypeScript | 5 |
| Vite | 6 |
| Tailwind CSS | 3.4 |
| Axios | 1.7.x |
| React Router | 6.28 |

## Estructura

```
frontend/
├── src/
│   ├── api/              # Clientes HTTP (Axios)
│   │   ├── client.ts     # Instancia Axios con Token auth
│   │   ├── products.ts   # CRUD productos, categorías, ingredientes
│   │   └── orders.ts     # Órdenes, ítems, confirmar, login
│   ├── components/
│   │   ├── orders/
│   │   │   └── OrderPanel.tsx    # RF-06 (totales) + RF-07 (stock)
│   │   ├── pos/
│   │   │   └── POSView.tsx       # RF-02 catálogo POS táctil
│   │   ├── products/
│   │   │   └── ProductsManagement.tsx  # RF-01 CRUD menú
│   │   └── ui/
│   │       ├── Alert.tsx
│   │       ├── ConfirmDialog.tsx
│   │       └── Spinner.tsx
│   ├── hooks/
│   │   ├── useOrder.ts     # Estado de orden activa
│   │   └── useProducts.ts  # Listado de productos
│   ├── types/
│   │   └── index.ts        # Interfaces TypeScript
│   ├── App.tsx             # Router + Layout + Auth
│   ├── main.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
└── postcss.config.js
```

## Instalación y uso

### Prerrequisitos

- Node.js 20+
- Backend Django corriendo en `http://localhost:8000`

### Pasos

```bash
# 1. Instalar dependencias
cd frontend
npm install

# 2. Iniciar servidor de desarrollo
npm run dev
# → http://localhost:5173
```

El proxy Vite redirige `/api/*` a `http://localhost:8000` automáticamente.

### Producción

```bash
npm run build
# Genera dist/ para servir con cualquier servidor estático
```

## RFs implementados

### RF-01 — Gestión de Productos del Menú (`/products`)
- Tabla con todos los productos, categoría, precio y estado (activo/inactivo).
- Formulario modal para **crear** y **editar** (nombre único, precio > 0).
- Toggle de disponibilidad sin salir de la vista.
- Confirmación antes de **eliminar**.

### RF-02 — Vista POS / Catálogo (`/pos`)
- Grid táctil (optimizado para tablet).
- **Solo muestra productos `disponible=true`**.
- Filtro por categoría en sidebar.
- Búsqueda por nombre en tiempo real.
- Panel lateral de orden integrado (compartido con RF-06/07).

### RF-06 — Cálculo de Total de Orden
- Subtotal por ítem (precio × cantidad).
- **IVA Colombia 19%** sobre subtotal.
- Total = subtotal + impuesto.
- Los valores se calculan en el backend (`ventas/api_views.py`) y se muestran en tiempo real al agregar/quitar ítems.

### RF-07 — Validación de Stock al Confirmar
- Al presionar **Confirmar**, el backend verifica cada ingrediente requerido.
- Si algún ingrediente no tiene stock suficiente, la API responde `409 Conflict` con la lista de faltantes.
- El frontend muestra **tipo de ingrediente**, cantidad disponible, requerida y faltante, y qué productos se ven afectados.
- El stock **solo** se descuenta si todos los ingredientes son suficientes.

## Autenticación

- **Token Auth** (DRF `rest_framework.authtoken`).
- `POST /api/auth/login/` → `{ token: "..." }` → guardado en `localStorage`.
- Header `Authorization: Token <token>` en todas las peticiones.
- Redirección automática a `/login` en error 401.

## Variables de entorno

Por defecto no se necesitan. Para cambiar la URL del backend en producción, editar `vite.config.ts`:

```ts
proxy: {
  '/api': { target: 'http://tu-backend.com', ... }
}
```
=======
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
