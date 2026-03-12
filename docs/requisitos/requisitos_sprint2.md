# Requisitos Priorizados — Sprint 2

## Proyecto: Sistema de Gestión de Pedidos e Inventario
**Metodología:** Scrum  
**Sprint:** 2  
**Duración del sprint:** 2 semanas

> 📄 Ver el Product Backlog completo en: [`product_backlog.md`](./product_backlog.md)

---

## Historias de Usuario del Sprint 2

Las historias de usuario están priorizadas usando el método **MoSCoW** y puntuadas con **Story Points** (escala de Fibonacci: 1, 2, 3, 5, 8, 13).

### Prioridad: 🔴 Must Have (Debe tener — Sprint 2)

| ID | Historia de Usuario | Story Points | Criterios de Aceptación |
|----|---------------------|:------------:|-------------------------|
| HU-01 | Como **mesero**, quiero registrar un nuevo pedido con los productos y cantidades seleccionados, para que la cocina lo reciba de forma inmediata. | 8 | ✅ El pedido se guarda en BD con estado "Pendiente" <br> ✅ El inventario se descuenta automáticamente <br> ✅ El cocinero ve el pedido en su panel |
| HU-02 | Como **cocinero**, quiero visualizar la lista de pedidos pendientes y cambiar su estado (En Preparación / Listo), para organizar el flujo de trabajo en cocina. | 5 | ✅ La lista se actualiza en tiempo real <br> ✅ Solo el cocinero puede cambiar el estado desde "Pendiente" <br> ✅ El mesero/cajero ven el estado actualizado |
| HU-03 | Como **cajero**, quiero procesar el pago de un pedido listo (efectivo o tarjeta), para cerrar la cuenta de la mesa correctamente. | 5 | ✅ Solo pedidos en estado "Listo" aparecen disponibles <br> ✅ El pago queda registrado con método y monto <br> ✅ El pedido cambia a estado "Pagado" |
| HU-04 | Como **administrador**, quiero gestionar el inventario (ver, agregar, editar y eliminar ítems), para mantener el stock actualizado y recibir alertas de stock bajo. | 8 | ✅ CRUD completo de inventario funcional <br> ✅ Alerta visible cuando stock <= stock mínimo <br> ✅ No se puede eliminar un producto con pedidos activos |
| HU-05 | Como **usuario**, quiero iniciar y cerrar sesión con correo y contraseña, para acceder solo a las funciones de mi rol. | 3 | ✅ Autenticación con JWT <br> ✅ Redirección al panel correcto según rol <br> ✅ Sesión expira después de inactividad |

---

### Prioridad: 🟡 Should Have (Debería tener — Sprint 2)

| ID | Historia de Usuario | Story Points | Criterios de Aceptación |
|----|---------------------|:------------:|-------------------------|
| HU-06 | Como **mesero**, quiero modificar o cancelar un pedido antes de que entre en preparación, para corregir errores del cliente. | 5 | ✅ Solo se puede modificar/cancelar en estado "Pendiente" <br> ✅ El stock se devuelve al cancelar <br> ✅ Se registra quién y cuándo canceló |
| HU-07 | Como **administrador**, quiero gestionar productos (crear, editar, habilitar/deshabilitar del menú), para mantener el menú actualizado. | 5 | ✅ CRUD completo de productos funcional <br> ✅ Productos deshabilitados no aparecen en el menú del mesero <br> ✅ Cambios reflejados en tiempo real |
| HU-08 | Como **administrador**, quiero generar un reporte de ventas por rango de fechas, para analizar el desempeño del negocio. | 8 | ✅ Reporte muestra total de pedidos, ingresos y top 5 productos <br> ✅ Filtro por fecha de inicio y fin funcional <br> ✅ Opción de exportar a PDF |
| HU-09 | Como **administrador**, quiero gestionar usuarios del sistema (crear, editar, activar/desactivar), para controlar el acceso. | 5 | ✅ CRUD de usuarios con asignación de rol <br> ✅ Usuarios desactivados no pueden iniciar sesión |

---

### Prioridad: 🟢 Could Have (Podría tener — Sprint 3+)

| ID | Historia de Usuario | Story Points | Criterios de Aceptación |
|----|---------------------|:------------:|-------------------------|
| HU-10 | Como **cajero**, quiero generar un reporte de cierres de caja diarios, para cuadrar las cuentas al final del turno. | 8 | ✅ Reporte muestra pagos del día por método <br> ✅ Total en efectivo y tarjeta separados |
| HU-11 | Como **administrador**, quiero exportar el reporte de inventario en Excel, para compartirlo con proveedores. | 3 | ✅ Exportación genera archivo .xlsx válido <br> ✅ Incluye nombre, stock actual y stock mínimo |
| HU-12 | Como **usuario**, quiero recuperar mi contraseña por correo electrónico, para no perder acceso al sistema. | 5 | ✅ Envío de correo con enlace de recuperación <br> ✅ El enlace expira en 30 minutos |

---

### Prioridad: ⚪ Won't Have (No en este proyecto)

| ID | Historia de Usuario | Justificación |
|----|---------------------|---------------|
| HU-13 | Módulo de reservas de mesas | Fuera del alcance del proyecto actual |
| HU-14 | Integración con pasarela de pagos externa | Complejidad técnica elevada para el alcance del curso |
| HU-15 | App móvil nativa | Requiere recursos adicionales de desarrollo |

---

## Sprint 2 Backlog

### Objetivo del Sprint
> Implementar el flujo completo de gestión de pedidos (registro, preparación y pago) junto con la autenticación de usuarios y la gestión básica de inventario.

### Tareas del Sprint 2

| ID Tarea | Historia | Descripción | Responsable | Estado | Estimación |
|----------|----------|-------------|-------------|--------|:----------:|
| T-01 | HU-05 | Implementar modelo y tabla de Usuarios en BD | Backend | 📋 Por hacer | 2 pts |
| T-02 | HU-05 | Desarrollar endpoint POST /auth/login con JWT | Backend | 📋 Por hacer | 3 pts |
| T-03 | HU-05 | Desarrollar endpoint POST /auth/logout | Backend | 📋 Por hacer | 1 pt |
| T-04 | HU-05 | Crear pantalla de login con validación de formulario | Frontend | 📋 Por hacer | 2 pts |
| T-05 | HU-01 | Implementar modelo y tabla de Pedidos y Detalle_Pedido | Backend | 📋 Por hacer | 3 pts |
| T-06 | HU-01 | Desarrollar endpoint POST /pedidos | Backend | 📋 Por hacer | 5 pts |
| T-07 | HU-01 | Desarrollar lógica de descuento de inventario al crear pedido | Backend | 📋 Por hacer | 3 pts |
| T-08 | HU-01 | Crear pantalla de toma de pedidos para mesero | Frontend | 📋 Por hacer | 5 pts |
| T-09 | HU-02 | Desarrollar endpoint PATCH /pedidos/{id}/estado | Backend | 📋 Por hacer | 3 pts |
| T-10 | HU-02 | Crear pantalla de cocina con lista de pedidos | Frontend | 📋 Por hacer | 5 pts |
| T-11 | HU-03 | Implementar modelo y tabla de Pagos | Backend | 📋 Por hacer | 2 pts |
| T-12 | HU-03 | Desarrollar endpoint POST /pagos | Backend | 📋 Por hacer | 3 pts |
| T-13 | HU-03 | Crear pantalla de caja para cajero | Frontend | 📋 Por hacer | 5 pts |
| T-14 | HU-04 | Implementar modelo y tabla de Inventario | Backend | 📋 Por hacer | 2 pts |
| T-15 | HU-04 | Desarrollar endpoints CRUD /inventario | Backend | 📋 Por hacer | 5 pts |
| T-16 | HU-04 | Crear pantalla de gestión de inventario para admin | Frontend | 📋 Por hacer | 5 pts |
| T-17 | HU-06 | Desarrollar endpoint PATCH /pedidos/{id} y DELETE /pedidos/{id} | Backend | 📋 Por hacer | 3 pts |
| T-18 | HU-07 | Desarrollar endpoints CRUD /productos | Backend | 📋 Por hacer | 5 pts |
| T-19 | HU-07 | Crear pantalla de gestión de productos para admin | Frontend | 📋 Por hacer | 5 pts |
| T-20 | HU-09 | Desarrollar endpoints CRUD /usuarios | Backend | 📋 Por hacer | 3 pts |
| T-21 | HU-09 | Crear pantalla de gestión de usuarios para admin | Frontend | 📋 Por hacer | 3 pts |
| T-22 | Todas | Pruebas de integración de los endpoints principales | QA | 📋 Por hacer | 5 pts |

**Total Story Points Sprint 2:** 29 puntos (Must Have) + 23 puntos (Should Have) = **52 puntos totales comprometidos**

---

## Definición de Terminado (Definition of Done)

Una historia de usuario se considera **terminada** cuando cumple todos los siguientes criterios:

- [x] El código ha sido revisado por al menos un compañero (code review)
- [x] Las pruebas unitarias e integración del endpoint están escritas y pasan
- [x] La funcionalidad ha sido probada manualmente en el entorno de desarrollo
- [x] No quedan bugs bloqueantes relacionados con la historia
- [x] El código está integrado en la rama principal (`main`) sin conflictos
- [x] La documentación técnica (comentarios de código y README) está actualizada si aplica

---

## Velocidad Estimada del Equipo

| Métrica | Valor |
|---------|-------|
| Duración del sprint | 2 semanas |
| Número de integrantes | Por definir |
| Velocidad estimada | 40–50 story points |
| Story points comprometidos (Must Have) | 29 pts |
| Story points objetivo con Should Have | 52 pts |
