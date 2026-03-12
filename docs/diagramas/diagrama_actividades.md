# Diagrama de Actividades — Sistema de Gestión de Pedidos e Inventario

---

## DA-01: Proceso Completo de un Pedido

```mermaid
flowchart TD
    Start([🟢 Inicio]) --> A[Mesero selecciona mesa]
    A --> B[Abre nuevo pedido en el sistema]
    B --> C[Consulta menú de productos disponibles]
    C --> D[Agrega productos y cantidades]
    D --> E{¿Desea agregar más productos?}
    E -- Sí --> D
    E -- No --> F[Confirma el pedido]
    F --> G{¿Hay stock suficiente?}
    G -- No --> H[Sistema alerta falta de stock]
    H --> D
    G -- Sí --> I[Sistema registra el pedido]
    I --> J[Sistema descuenta inventario automáticamente]
    J --> K[Pedido enviado a cocina — estado: Pendiente]
    K --> L[Cocinero visualiza pedido]
    L --> M[Cocinero cambia estado: En Preparación]
    M --> N[Cocinero prepara los productos]
    N --> O[Cocinero cambia estado: Listo]
    O --> P[Cajero visualiza pedido listo]
    P --> Q[Cajero selecciona método de pago]
    Q --> R{Método de pago}
    R -- Efectivo --> S[Registra pago en efectivo]
    R -- Tarjeta --> T[Registra pago con tarjeta]
    S --> U[Sistema cierra pedido — estado: Pagado]
    T --> U
    U --> V[Sistema genera recibo]
    V --> End([🔴 Fin])
```

---

## DA-02: Gestión de Inventario

```mermaid
flowchart TD
    Start([🟢 Inicio]) --> A[Administrador accede al módulo de inventario]
    A --> B[Sistema muestra lista de productos con stock actual]
    B --> C{¿Qué acción desea realizar?}

    C -- Agregar producto --> D[Ingresa datos del nuevo producto]
    D --> E[Establece cantidad inicial y stock mínimo]
    E --> F[Sistema guarda el nuevo producto]
    F --> G[Sistema actualiza inventario]
    G --> End([🔴 Fin])

    C -- Actualizar stock --> H[Selecciona producto a actualizar]
    H --> I[Ingresa nueva cantidad en stock]
    I --> J[Sistema actualiza inventario]
    J --> K{¿Stock <= Stock mínimo?}
    K -- Sí --> L[Sistema genera alerta de stock bajo]
    L --> End
    K -- No --> End

    C -- Eliminar producto --> M[Selecciona producto]
    M --> N{¿Tiene pedidos activos?}
    N -- Sí --> O[Sistema impide eliminación]
    O --> B
    N -- No --> P[Sistema elimina el producto del inventario]
    P --> End
```

---

## DA-03: Generar Reporte de Ventas

```mermaid
flowchart TD
    Start([🟢 Inicio]) --> A[Administrador accede al módulo de reportes]
    A --> B[Selecciona tipo de reporte]
    B --> C{Tipo de reporte}

    C -- Ventas --> D[Selecciona rango de fechas]
    D --> E[Sistema consulta pedidos pagados en el período]
    E --> F[Calcula totales, ingresos y productos más vendidos]
    F --> G[Muestra reporte en pantalla]

    C -- Inventario --> H[Sistema consulta estado actual del inventario]
    H --> I[Identifica productos con stock bajo]
    I --> G

    G --> J{¿Desea exportar?}
    J -- PDF --> K[Sistema genera archivo PDF]
    J -- Excel --> L[Sistema genera archivo Excel]
    J -- No --> End([🔴 Fin])
    K --> End
    L --> End
```
