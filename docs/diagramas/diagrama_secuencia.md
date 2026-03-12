# Diagramas de Secuencia — Sistema de Gestión de Pedidos e Inventario

---

## SD-01: Iniciar Sesión

```mermaid
sequenceDiagram
    actor Usuario
    participant UI as Interfaz Web
    participant API as API REST
    participant Auth as Servicio Autenticación
    participant DB as Base de Datos

    Usuario->>UI: Ingresa correo y contraseña
    UI->>API: POST /auth/login {correo, contrasena}
    API->>Auth: validarCredenciales(correo, contrasena)
    Auth->>DB: SELECT * FROM usuarios WHERE correo=?
    DB-->>Auth: Registro del usuario
    Auth->>Auth: Verifica hash de contraseña
    alt Credenciales válidas
        Auth-->>API: {token, rol, nombre}
        API-->>UI: 200 OK {token, usuario}
        UI-->>Usuario: Redirige al panel según rol
    else Credenciales inválidas
        Auth-->>API: Error 401
        API-->>UI: 401 Unauthorized
        UI-->>Usuario: Muestra mensaje de error
    end
```

---

## SD-02: Registrar Pedido

```mermaid
sequenceDiagram
    actor Mesero
    participant UI as Interfaz Web
    participant API as API REST
    participant PedidoSvc as Servicio Pedidos
    participant InvSvc as Servicio Inventario
    participant DB as Base de Datos

    Mesero->>UI: Selecciona mesa y abre nuevo pedido
    UI->>API: GET /productos/disponibles
    API->>DB: SELECT productos WHERE disponible=true
    DB-->>API: Lista de productos
    API-->>UI: Lista de productos disponibles
    UI-->>Mesero: Muestra menú

    loop Agrega ítems al pedido
        Mesero->>UI: Selecciona producto y cantidad
        UI->>UI: Agrega ítem a pedido local
    end

    Mesero->>UI: Confirma pedido
    UI->>API: POST /pedidos {mesa, idMesero, items[]}
    API->>InvSvc: verificarStock(items[])
    InvSvc->>DB: SELECT inventario WHERE idProducto IN (?)
    DB-->>InvSvc: Niveles de stock
    alt Stock suficiente
        InvSvc-->>API: Stock OK
        API->>PedidoSvc: crearPedido(datos)
        PedidoSvc->>DB: INSERT INTO pedidos ...
        PedidoSvc->>DB: INSERT INTO detalle_pedido ...
        PedidoSvc->>InvSvc: descontarStock(items[])
        InvSvc->>DB: UPDATE inventario SET cantidad=cantidad-?
        DB-->>PedidoSvc: Confirmación
        PedidoSvc-->>API: {idPedido, estado: "Pendiente"}
        API-->>UI: 201 Created {idPedido}
        UI-->>Mesero: Pedido registrado exitosamente
    else Stock insuficiente
        InvSvc-->>API: Error stock insuficiente {producto}
        API-->>UI: 422 Unprocessable Entity
        UI-->>Mesero: Alerta: producto sin stock
    end
```

---

## SD-03: Actualizar Estado de Pedido (Cocinero)

```mermaid
sequenceDiagram
    actor Cocinero
    participant UI as Interfaz Web
    participant API as API REST
    participant PedidoSvc as Servicio Pedidos
    participant DB as Base de Datos

    Cocinero->>UI: Visualiza lista de pedidos pendientes
    UI->>API: GET /pedidos?estado=Pendiente
    API->>DB: SELECT pedidos WHERE estado='Pendiente'
    DB-->>API: Lista de pedidos
    API-->>UI: Pedidos pendientes
    UI-->>Cocinero: Muestra pedidos

    Cocinero->>UI: Cambia estado del pedido a "En Preparación"
    UI->>API: PATCH /pedidos/{id}/estado {estado: "EnPreparacion"}
    API->>PedidoSvc: actualizarEstado(id, "EnPreparacion")
    PedidoSvc->>DB: UPDATE pedidos SET estado='EnPreparacion' WHERE id=?
    DB-->>PedidoSvc: Confirmación
    PedidoSvc-->>API: Pedido actualizado
    API-->>UI: 200 OK
    UI-->>Cocinero: Estado actualizado

    Note over Cocinero,DB: Luego de preparar el pedido...

    Cocinero->>UI: Cambia estado a "Listo"
    UI->>API: PATCH /pedidos/{id}/estado {estado: "Listo"}
    API->>PedidoSvc: actualizarEstado(id, "Listo")
    PedidoSvc->>DB: UPDATE pedidos SET estado='Listo' WHERE id=?
    DB-->>PedidoSvc: Confirmación
    API-->>UI: 200 OK
    UI-->>Cocinero: Pedido marcado como listo
```

---

## SD-04: Procesar Pago

```mermaid
sequenceDiagram
    actor Cajero
    participant UI as Interfaz Web
    participant API as API REST
    participant PagoSvc as Servicio Pagos
    participant PedidoSvc as Servicio Pedidos
    participant DB as Base de Datos

    Cajero->>UI: Busca pedido listo para cobrar
    UI->>API: GET /pedidos?estado=Listo
    API->>DB: SELECT pedidos WHERE estado='Listo'
    DB-->>API: Pedidos listos
    API-->>UI: Lista de pedidos
    UI-->>Cajero: Muestra pedidos para cobrar

    Cajero->>UI: Selecciona pedido y método de pago
    UI->>API: POST /pagos {idPedido, metodoPago, monto}
    API->>PagoSvc: procesarPago(idPedido, metodoPago, monto)
    PagoSvc->>DB: INSERT INTO pagos ...
    PagoSvc->>PedidoSvc: cerrarPedido(idPedido)
    PedidoSvc->>DB: UPDATE pedidos SET estado='Pagado' WHERE id=?
    DB-->>PagoSvc: Confirmación
    PagoSvc-->>API: {idPago, recibo}
    API-->>UI: 201 Created {idPago}
    UI-->>Cajero: Pago registrado — muestra recibo
```
