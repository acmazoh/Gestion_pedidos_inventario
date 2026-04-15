# Diagrama de Casos de Uso — Sistema de Gestión de Pedidos e Inventario

> Actualizado para reflejar la implementación real del proyecto.

## Actores del Sistema

| Actor | Descripción |
|-------|-------------|
| **Usuario autenticado** | Cualquier usuario que haya iniciado sesión (mesero, cocinero, admin) |
| **Mesero** | Crea, modifica y confirma órdenes |
| **Cocinero** | Visualiza las órdenes confirmadas y actualiza su estado |
| **Administrador** | Gestiona productos, ingredientes e inventario vía Django Admin |

> **Nota:** El sistema actual usa autenticación por sesiones de Django (`django.contrib.auth`).
> Los roles se distinguen por permisos de Django (staff/superuser para el admin).

---

## Diagrama (Mermaid)

```mermaid
flowchart TD
    Admin([👤 Administrador\nsuperuser/staff])
    Mesero([👤 Mesero\nusuario autenticado])
    Cocinero([👤 Cocinero\nusuario autenticado])

    subgraph Sistema["Sistema Restin POS"]
        UC1([RF-13 · Iniciar sesión\nPOST /accounts/login/])
        UC2([RF-13 · Cerrar sesión\nPOST /accounts/logout/])
        UC3([RF-03 · Crear nueva orden\nPOST /ventas/pedidos/nuevo/])
        UC4([RF-04 · Modificar orden activa\n+ / - / eliminar productos])
        UC5([RF-05 · Confirmar orden\ny enviar a cocina])
        UC6([RF-08 · Ver panel de cocina\nGET /ventas/pedidos/cocina/])
        UC7([RF-09 · Marcar orden lista\n/ entregada])
        UC8([RF-10 · Descuento automático\nde inventario])
        UC9([RF-11 · Registrar transacción\nal entregar])
        UC10([RF-11 · Ver historial de ventas\ncon filtro por fechas])
        UC11([RF-11 · Exportar CSV\nde ventas])
        UC12([RF-01/02 · Gestionar productos\ne ingredientes vía Admin])
        UC13([RF-15 · Gestionar stock\nde ingredientes vía Admin])
    end

    Mesero --> UC1
    Mesero --> UC2
    Mesero --> UC3
    Mesero --> UC4
    Mesero --> UC5
    Mesero --> UC10

    Cocinero --> UC1
    Cocinero --> UC2
    Cocinero --> UC6
    Cocinero --> UC7

    Admin --> UC1
    Admin --> UC2
    Admin --> UC12
    Admin --> UC13
    Admin --> UC10
    Admin --> UC11

    UC3 -->|precondición| UC1
    UC5 -->|«include»| UC8
    UC7 -->|«include»| UC9
```

---

## Descripción de Casos de Uso Principales

### CU-RF13: Iniciar / Cerrar Sesión
- **Actor primario:** Todos los usuarios
- **Backend:** `RateLimitedLoginView` — Django `LoginView` con rate limiting en caché (5 intentos / 15 min)
- **Contraseñas:** hasheadas con `BCryptSHA256PasswordHasher`
- **Sesión:** gestionada con `django.contrib.sessions` (persiste entre recargas)
- **Flujo login:** POST `/accounts/login/` → valida credenciales → crea sesión → redirige a `/ventas/pedidos/`
- **Flujo logout:** POST `/accounts/logout/` → invalida sesión → redirige a `/accounts/login/`
- **Flujo alternativo:** Credenciales inválidas → muestra error con intentos restantes; 5 fallos → bloqueo 15 min

---

### CU-RF03: Crear Nueva Orden
- **Actor primario:** Mesero (usuario autenticado)
- **Precondición:** Sesión iniciada (`LoginRequiredMixin`)
- **Flujo:** GET `/ventas/pedidos/nuevo/` → formulario con campo `mesa_o_online` → POST → crea `Pedido` (estado=`pendiente`) → redirige al detalle con mensaje de éxito
- **Validación:** El campo `mesa_o_online` es obligatorio

---

### CU-RF04: Modificar Orden Activa
- **Actor primario:** Mesero
- **Precondición:** Orden en estado `pendiente`; si el estado es distinto, las acciones de edición no se muestran
- **Flujo:** Agregar producto → POST al detalle; cambiar cantidad → POST `/items/M/incrementar|disminuir/`; eliminar → POST `/items/M/eliminar/` (con confirmación JS)
- **Búsqueda:** Filtro en tiempo real sobre el `<select>` de productos mediante JavaScript

---

### CU-RF05: Confirmar Orden y Enviar a Cocina
- **Actor primario:** Mesero
- **Precondición:** Orden en estado `pendiente` con al menos 1 producto
- **Flujo:** Botón "Confirmar Orden" → diálogo `confirm()` en JS → POST `/ventas/pedidos/N/confirmar/` → verifica stock → descuenta ingredientes → registra `MovimientoInventario` → cambia estado a `en_preparacion` → muestra mensaje de éxito
- **Flujo alternativo:** Stock insuficiente → muestra lista de ingredientes faltantes y cantidades

---

### CU-RF08/09: Panel de Cocina
- **Actor primario:** Cocinero
- **Flujo:** GET `/ventas/pedidos/cocina/` → lista pedidos en `en_preparacion` y `listo` → botones para avanzar estado (listo → entregada)
- **Auto-recarga:** Cada 10 segundos con `setTimeout`

---

### CU-RF10: Descuento Automático de Inventario
- **Disparador:** Al confirmar orden (RF-05)
- **Lógica:** Para cada `PedidoProducto`, consulta `ProductoIngrediente` (receta); descuenta `ingrediente.stock`; registra `MovimientoInventario` con `tipo='descuento'`

