# Diagrama de Clases — Sistema de Gestión de Pedidos e Inventario

## Diagrama (Mermaid)

```mermaid
classDiagram
    direction TB

    class Usuario {
        +int id
        +String nombre
        +String correo
        +String contrasena
        +String rol
        +Boolean activo
        +iniciarSesion(correo, contrasena) Boolean
        +cerrarSesion() void
        +actualizarPerfil(datos) void
    }

    class Administrador {
        +gestionarUsuarios() void
        +generarReporte(tipo, fechaInicio, fechaFin) Reporte
        +gestionarProductos() void
    }

    class Mesero {
        +String mesaAsignada
        +crearPedido(mesa) Pedido
        +modificarPedido(idPedido, items) void
        +cancelarPedido(idPedido) void
    }

    class Cajero {
        +procesarPago(idPedido, metodoPago) Pago
        +generarCuenta(idPedido) Cuenta
    }

    class Cocinero {
        +actualizarEstadoPedido(idPedido, estado) void
        +verPedidosPendientes() List~Pedido~
    }

    class Producto {
        +int id
        +String nombre
        +String descripcion
        +float precio
        +String categoria
        +Boolean disponible
        +obtenerPrecio() float
        +actualizarDisponibilidad(disponible) void
    }

    class Inventario {
        +int id
        +int idProducto
        +int cantidadActual
        +int cantidadMinima
        +Date ultimaActualizacion
        +verificarStock() Boolean
        +actualizarStock(cantidad) void
        +alertaStockBajo() Boolean
    }

    class Pedido {
        +int id
        +int idMesero
        +String mesa
        +String estado
        +Date fechaHora
        +float total
        +agregarItem(producto, cantidad) void
        +quitarItem(idItem) void
        +calcularTotal() float
        +cambiarEstado(nuevoEstado) void
    }

    class DetallePedido {
        +int id
        +int idPedido
        +int idProducto
        +int cantidad
        +float precioUnitario
        +float subtotal
        +calcularSubtotal() float
    }

    class Pago {
        +int id
        +int idPedido
        +float monto
        +String metodoPago
        +Date fechaHora
        +String estado
        +procesar() Boolean
        +generarRecibo() String
    }

    class Reporte {
        +int id
        +String tipo
        +Date fechaInicio
        +Date fechaFin
        +Date fechaGeneracion
        +Object datos
        +generar() void
        +exportarPDF() File
        +exportarExcel() File
    }

    Usuario <|-- Administrador
    Usuario <|-- Mesero
    Usuario <|-- Cajero
    Usuario <|-- Cocinero

    Mesero "1" --> "0..*" Pedido : crea
    Pedido "1" *-- "1..*" DetallePedido : contiene
    DetallePedido "1" --> "1" Producto : referencia
    Producto "1" -- "1" Inventario : tiene
    Cajero "1" --> "0..*" Pago : procesa
    Pago "1" --> "1" Pedido : corresponde a
    Administrador "1" --> "0..*" Reporte : genera
    Administrador "1" --> "0..*" Producto : gestiona
    Administrador "1" --> "0..*" Inventario : gestiona
```

---

## Descripción de las Clases

| Clase | Responsabilidad |
|-------|-----------------|
| `Usuario` | Clase base para todos los usuarios del sistema; maneja autenticación |
| `Administrador` | Hereda de Usuario; gestiona productos, usuarios y reportes |
| `Mesero` | Hereda de Usuario; crea y gestiona pedidos |
| `Cajero` | Hereda de Usuario; procesa pagos y genera cuentas |
| `Cocinero` | Hereda de Usuario; actualiza el estado de los pedidos |
| `Producto` | Representa un ítem del menú con precio y disponibilidad |
| `Inventario` | Controla el stock de cada producto con alertas de mínimos |
| `Pedido` | Agrupa los ítems solicitados por una mesa; tiene estado de ciclo de vida |
| `DetallePedido` | Línea de cada pedido: producto + cantidad + precio unitario |
| `Pago` | Registra la transacción económica asociada a un pedido |
| `Reporte` | Genera y exporta información estadística del sistema |

---

## Estados del Pedido

```mermaid
stateDiagram-v2
    [*] --> Pendiente : Mesero crea pedido
    Pendiente --> EnPreparacion : Cocinero acepta
    EnPreparacion --> Listo : Cocinero finaliza
    Listo --> Pagado : Cajero procesa pago
    Pendiente --> Cancelado : Mesero/Admin cancela
    Pagado --> [*]
    Cancelado --> [*]
```
