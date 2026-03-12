# Product Backlog — Sistema de Gestión de Pedidos e Inventario

## Visión del Producto
Desarrollar un sistema web que permita a restaurantes gestionar de manera eficiente sus pedidos e inventario, reduciendo errores manuales y mejorando la comunicación entre meseros, cocina y caja.

---

## Épicas del Proyecto

| ID | Épica | Descripción |
|----|-------|-------------|
| EP-01 | Autenticación y Roles | Control de acceso por rol al sistema |
| EP-02 | Gestión de Pedidos | Flujo completo de vida de un pedido |
| EP-03 | Gestión de Inventario | Control de stock y alertas |
| EP-04 | Gestión de Productos | Administración del menú |
| EP-05 | Reportes y Estadísticas | Generación de informes de ventas e inventario |
| EP-06 | Gestión de Usuarios | Administración de cuentas del personal |

---

## Backlog Completo Priorizado

### 🔴 Prioridad Alta (Sprint 1 y 2)

| ID | Épica | Historia de Usuario | Story Points | Criterios de Aceptación Clave |
|----|-------|---------------------|:------------:|-------------------------------|
| HU-01 | EP-02 | Como **mesero**, quiero registrar un nuevo pedido con productos y cantidades, para que la cocina lo reciba inmediatamente. | 8 | Pedido guardado en BD; inventario descontado; cocinero notificado |
| HU-02 | EP-02 | Como **cocinero**, quiero ver los pedidos pendientes y cambiar su estado, para organizar el trabajo en cocina. | 5 | Lista en tiempo real; estados: Pendiente → En Preparación → Listo |
| HU-03 | EP-02 | Como **cajero**, quiero procesar el pago de un pedido listo, para cerrar la cuenta de la mesa. | 5 | Registro de pago; cambio de estado a "Pagado"; recibo generado |
| HU-04 | EP-03 | Como **administrador**, quiero gestionar el inventario, para mantener el stock actualizado con alertas de mínimos. | 8 | CRUD completo; alerta visible cuando stock ≤ mínimo |
| HU-05 | EP-01 | Como **usuario**, quiero iniciar sesión con mis credenciales, para acceder solo a las funciones de mi rol. | 3 | JWT válido; redirección por rol; sesión segura |

### 🟡 Prioridad Media (Sprint 2 y 3)

| ID | Épica | Historia de Usuario | Story Points | Criterios de Aceptación Clave |
|----|-------|---------------------|:------------:|-------------------------------|
| HU-06 | EP-02 | Como **mesero**, quiero modificar o cancelar un pedido antes de que entre en preparación, para corregir errores. | 5 | Solo modificable en "Pendiente"; stock devuelto al cancelar |
| HU-07 | EP-04 | Como **administrador**, quiero gestionar productos del menú (CRUD + habilitar/deshabilitar), para mantener la carta actualizada. | 5 | Productos deshabilitados no aparecen en toma de pedidos |
| HU-08 | EP-05 | Como **administrador**, quiero generar reportes de ventas por rango de fechas, para analizar el desempeño del negocio. | 8 | Top 5 productos; total de ingresos; exportar PDF |
| HU-09 | EP-06 | Como **administrador**, quiero gestionar usuarios del sistema (CRUD + activar/desactivar), para controlar el acceso. | 5 | Asignación de roles; usuarios desactivados no inician sesión |

### 🟢 Prioridad Baja (Sprint 3+)

| ID | Épica | Historia de Usuario | Story Points | Criterios de Aceptación Clave |
|----|-------|---------------------|:------------:|-------------------------------|
| HU-10 | EP-05 | Como **cajero**, quiero generar un reporte de cierre de caja diario, para cuadrar las cuentas al final del turno. | 8 | Total por método de pago; agrupado por día |
| HU-11 | EP-05 | Como **administrador**, quiero exportar el reporte de inventario en Excel, para compartirlo con proveedores. | 3 | Archivo .xlsx válido con stock actual y mínimo |
| HU-12 | EP-01 | Como **usuario**, quiero recuperar mi contraseña por correo, para no perder acceso al sistema. | 5 | Enlace de recuperación por correo; expira en 30 min |
| HU-13 | EP-04 | Como **administrador**, quiero categorizar los productos del menú, para facilitar la navegación del mesero al tomar pedidos. | 3 | Filtro por categoría en la pantalla de pedidos |
| HU-14 | EP-03 | Como **administrador**, quiero registrar entradas de inventario (compras a proveedores), para mantener el historial de abastecimiento. | 8 | Historial de entradas; actualiza stock automáticamente |

---

## Resumen del Backlog por Épica

| Épica | Total Historias | Total Story Points |
|-------|:---------------:|:-----------------:|
| EP-01 Autenticación y Roles | 2 | 8 |
| EP-02 Gestión de Pedidos | 3 | 18 |
| EP-03 Gestión de Inventario | 2 | 16 |
| EP-04 Gestión de Productos | 2 | 8 |
| EP-05 Reportes y Estadísticas | 3 | 19 |
| EP-06 Gestión de Usuarios | 1 | 5 |
| **Total** | **13** | **74** |

---

## Sprints Planificados

| Sprint | Épicas Cubiertas | Historias | Story Points |
|--------|-----------------|-----------|:------------:|
| Sprint 1 *(entrega anterior)* | EP-01, EP-02 (parcial) | HU-05, HU-01 (parcial) | ~15 |
| **Sprint 2** *(entrega actual)* | EP-01, EP-02, EP-03, EP-04 | HU-01, HU-02, HU-03, HU-04, HU-05, HU-06, HU-07 | 39 |
| Sprint 3 | EP-05, EP-06 | HU-08, HU-09, HU-10, HU-11 | 24 |
| Sprint 4 (si aplica) | EP-03, EP-04 | HU-12, HU-13, HU-14 | 16 |
