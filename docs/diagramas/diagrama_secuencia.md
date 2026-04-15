# Diagramas de Secuencia — Sistema de Gestión de Pedidos e Inventario

> Los diagramas reflejan la implementación real del proyecto (Django + sesiones).

---

## SD-01: Iniciar Sesión (RF-13)

```mermaid
sequenceDiagram
    actor Usuario
    participant UI as Interfaz Web (template login.html)
    participant View as RateLimitedLoginView
    participant Cache as Django Cache (rate limiting)
    participant Auth as django.contrib.auth
    participant DB as Base de Datos (SQLite)

    Usuario->>UI: GET /accounts/login/
    UI-->>Usuario: Muestra formulario de login

    Usuario->>View: POST /accounts/login/ {username, password}
    View->>Cache: Consulta intentos fallidos para la IP
    Cache-->>View: N intentos (si ≥ 5 → bloquea 15 min)

    alt IP bloqueada (≥ 5 intentos fallidos)
        View-->>UI: Muestra mensaje de bloqueo temporal
    else IP no bloqueada
        View->>Auth: authenticate(username, password)
        Auth->>DB: SELECT * FROM auth_user WHERE username=?
        DB-->>Auth: Registro del usuario
        Auth->>Auth: Verifica hash BCrypt de contraseña
        alt Credenciales válidas
            Auth-->>View: Objeto User
            View->>Cache: Elimina contador de intentos fallidos
            View->>Auth: login(request, user) → crea sesión
            View-->>UI: Redirige a /ventas/pedidos/
        else Credenciales inválidas
            View->>Cache: Incrementa contador (+1)
            View-->>UI: 200 — Muestra error "Usuario o contraseña incorrectos. Intentos restantes: N"
        end
    end
```

---

## SD-02: Crear y Confirmar Orden (RF-03 + RF-04 + RF-05)

```mermaid
sequenceDiagram
    actor Mesero
    participant UI as Interfaz Web (pedido_form / pedido_detail)
    participant CV as PedidoCreateView
    participant DV as PedidoDetailView
    participant CFV as PedidoConfirmarView
    participant DB as Base de Datos

    %% RF-03: Crear orden
    Mesero->>UI: GET /ventas/pedidos/nuevo/
    UI-->>Mesero: Formulario "Nueva Orden"

    Mesero->>CV: POST /ventas/pedidos/nuevo/ {mesa_o_online}
    CV->>DB: INSERT INTO ventas_pedido (estado='pendiente', creado_por=user)
    DB-->>CV: Pedido #N
    CV-->>UI: Redirige a /ventas/pedidos/N/ + mensaje "Orden #N creada"

    %% RF-04: Modificar orden
    loop Agrega / ajusta productos (estado='pendiente')
        Mesero->>DV: POST /ventas/pedidos/N/ {producto, cantidad}
        DV->>DB: INSERT / UPDATE ventas_pedidoproducto
        DB-->>DV: OK
        DV-->>UI: Redirige a /ventas/pedidos/N/ (total actualizado)
    end

    opt Cambiar cantidad
        Mesero->>UI: POST /pedidos/N/items/M/incrementar/ o /disminuir/
        Note right of DB: UPDATE cantidad; si llega a 0 → DELETE
    end

    opt Eliminar producto
        Mesero->>UI: POST /pedidos/N/items/M/eliminar/ (con confirmación JS)
        Note right of DB: DELETE FROM ventas_pedidoproducto
    end

    %% RF-05: Confirmar orden
    Mesero->>UI: Click "Confirmar Orden" (diálogo JS de confirmación)
    Mesero->>CFV: POST /ventas/pedidos/N/confirmar/
    CFV->>DB: SELECT items + ingredientes con cantidades receta
    DB-->>CFV: Requisitos de ingredientes

    alt Stock insuficiente
        CFV-->>UI: Muestra lista de ingredientes faltantes
    else Stock suficiente
        CFV->>DB: UPDATE stock de ingredientes (descuento)
        CFV->>DB: INSERT MovimientoInventario por cada ingrediente
        CFV->>DB: UPDATE Pedido SET estado='en_preparacion'
        CFV-->>UI: Redirige a /ventas/pedidos/N/ + mensaje "Enviado a cocina"
    end
```

---

## SD-03: Actualizar Estado de Pedido (Cocinero — RF-08/09)

```mermaid
sequenceDiagram
    actor Cocinero
    participant UI as cocina_dashboard.html
    participant V1 as PedidoMarcarListoView
    participant V2 as PedidoMarcarEntregadaView
    participant DB as Base de Datos

    Cocinero->>UI: GET /ventas/pedidos/cocina/
    Note right of DB: SELECT pedidos WHERE estado IN ('en_preparacion','listo')
    UI-->>Cocinero: Lista de pedidos confirmados (auto-recarga cada 10 s)

    Cocinero->>V1: POST /ventas/pedidos/N/listo/
    V1->>DB: UPDATE Pedido SET estado='listo' WHERE id=N
    DB-->>V1: OK
    V1-->>UI: Redirige a /ventas/pedidos/cocina/

    Cocinero->>V2: POST /ventas/pedidos/N/entregada/
    V2->>DB: UPDATE Pedido SET estado='entregada'
    V2->>DB: INSERT INTO ventas_transaccion (total=sum de items)
    DB-->>V2: OK
    V2-->>UI: Redirige a /ventas/pedidos/cocina/
```

---

## SD-04: Cerrar Sesión (RF-13)

```mermaid
sequenceDiagram
    actor Usuario
    participant UI as Cualquier página
    participant View as LogoutView (django.contrib.auth)
    participant Session as Sesión Django

    Usuario->>UI: POST /accounts/logout/ (formulario con CSRF token)
    UI->>View: POST /accounts/logout/
    View->>Session: flush() — invalida la sesión actual
    View-->>UI: Redirige a /accounts/login/
```

