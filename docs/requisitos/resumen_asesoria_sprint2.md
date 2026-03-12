# Resumen para Asesoría — Segunda Entrega
## Sistema de Gestión de Pedidos e Inventario

> **Fecha de asesoría:** Clase de la semana del Sprint 2  
> **Tiempo asignado:** 20 minutos por grupo (a partir de las 9:15 a.m.)

---

## 1. ¿Qué es el sistema?

Sistema web para restaurantes que permite:
- Tomar y gestionar pedidos por mesa
- Controlar el inventario de productos en tiempo real
- Procesar pagos y generar reportes de ventas
- Gestionar usuarios por roles: Administrador, Mesero, Cajero, Cocinero

---

## 2. Estado de los Diagramas (Segunda Entrega)

| Diagrama | Archivo | Estado |
|----------|---------|:------:|
| Casos de Uso | [`diagrama_casos_uso.md`](../diagramas/diagrama_casos_uso.md) | ✅ Listo |
| Clases | [`diagrama_clases.md`](../diagramas/diagrama_clases.md) | ✅ Listo |
| Secuencia | [`diagrama_secuencia.md`](../diagramas/diagrama_secuencia.md) | ✅ Listo |
| Actividades | [`diagrama_actividades.md`](../diagramas/diagrama_actividades.md) | ✅ Listo |
| Entidad-Relación | [`diagrama_entidad_relacion.md`](../diagramas/diagrama_entidad_relacion.md) | ✅ Listo |

---

## 3. Resumen Sprint 1 (Base de partida)

Lo que se estableció en el Sprint 1:

| Entregable | Estado |
|------------|:------:|
| Definición del problema y alcance del sistema | ✅ Completado |
| Identificación de actores y roles | ✅ Completado |
| Historias de usuario iniciales (HU-01, HU-05 borrador) | ✅ Completado |
| Tecnologías seleccionadas (Backend + BD SQL + API REST) | ✅ Completado |
| Repositorio de código creado y configurado | ✅ Completado |

---

## 4. Sprint 2 — Historias Comprometidas

### 🔴 Must Have (obligatorias para este sprint)

| ID | Historia | Story Points |
|----|----------|:------------:|
| HU-01 | Registrar pedido (mesero → cocina + descuento de inventario) | 8 pts |
| HU-02 | Ver y actualizar estado de pedidos (cocinero) | 5 pts |
| HU-03 | Procesar pago de un pedido listo (cajero) | 5 pts |
| HU-04 | Gestionar inventario con alertas de stock mínimo (admin) | 8 pts |
| HU-05 | Iniciar/cerrar sesión con rol y JWT | 3 pts |
| **Total Must Have** | | **29 pts** |

### 🟡 Should Have (objetivo si hay capacidad)

| ID | Historia | Story Points |
|----|----------|:------------:|
| HU-06 | Modificar/cancelar pedido en estado Pendiente (mesero) | 5 pts |
| HU-07 | Gestionar productos del menú — CRUD (admin) | 5 pts |
| HU-08 | Generar reporte de ventas por rango de fechas (admin) | 8 pts |
| HU-09 | Gestionar usuarios — CRUD + roles (admin) | 5 pts |
| **Total Should Have** | | **23 pts** |

**Total Sprint 2: 52 pts comprometidos**

---

## 5. Sprint 2 — Backlog de Tareas

| # | Tarea | Historia | Estado |
|---|-------|----------|:------:|
| T-01 | Modelo y tabla Usuarios en BD | HU-05 | 📋 Por hacer |
| T-02 | Endpoint POST /auth/login con JWT | HU-05 | 📋 Por hacer |
| T-03 | Endpoint POST /auth/logout | HU-05 | 📋 Por hacer |
| T-04 | Pantalla de Login (frontend) | HU-05 | 📋 Por hacer |
| T-05 | Modelo y tablas Pedidos + Detalle_Pedido en BD | HU-01 | 📋 Por hacer |
| T-06 | Endpoint POST /pedidos | HU-01 | 📋 Por hacer |
| T-07 | Lógica de descuento de inventario al crear pedido | HU-01 | 📋 Por hacer |
| T-08 | Pantalla de toma de pedidos — mesero (frontend) | HU-01 | 📋 Por hacer |
| T-09 | Endpoint PATCH /pedidos/{id}/estado | HU-02 | 📋 Por hacer |
| T-10 | Pantalla de cocina con lista de pedidos (frontend) | HU-02 | 📋 Por hacer |
| T-11 | Modelo y tabla Pagos en BD | HU-03 | 📋 Por hacer |
| T-12 | Endpoint POST /pagos | HU-03 | 📋 Por hacer |
| T-13 | Pantalla de caja — cajero (frontend) | HU-03 | 📋 Por hacer |
| T-14 | Modelo y tabla Inventario en BD | HU-04 | 📋 Por hacer |
| T-15 | Endpoints CRUD /inventario | HU-04 | 📋 Por hacer |
| T-16 | Pantalla de gestión de inventario — admin (frontend) | HU-04 | 📋 Por hacer |
| T-17 | Endpoints PATCH y DELETE /pedidos/{id} | HU-06 | 📋 Por hacer |
| T-18 | Endpoints CRUD /productos | HU-07 | 📋 Por hacer |
| T-19 | Pantalla de gestión de productos — admin (frontend) | HU-07 | 📋 Por hacer |
| T-20 | Endpoints CRUD /usuarios | HU-09 | 📋 Por hacer |
| T-21 | Pantalla de gestión de usuarios — admin (frontend) | HU-09 | 📋 Por hacer |
| T-22 | Pruebas de integración endpoints principales | Todas | 📋 Por hacer |

> ⚠️ **Actualizar la columna "Estado"** conforme avance el equipo:  
> `📋 Por hacer` → `🔄 En progreso` → `✅ Listo`

---

## 6. Criterios de Aceptación Clave (Must Have)

### HU-01 — Registrar Pedido
- El pedido se guarda con estado **"Pendiente"**
- El stock del inventario se descuenta automáticamente
- Si no hay stock, el sistema alerta al mesero sin guardar el pedido

### HU-02 — Estado de Pedido (Cocinero)
- El cocinero puede cambiar: **Pendiente → En Preparación → Listo**
- El mesero y cajero ven el estado actualizado

### HU-03 — Procesar Pago
- Solo pedidos en estado **"Listo"** aparecen para cobrar
- Se registra método de pago (efectivo / tarjeta) y monto
- El pedido pasa a estado **"Pagado"**

### HU-04 — Gestión de Inventario
- CRUD completo de ítems de inventario
- Alerta visible cuando `stock_actual ≤ stock_mínimo`
- No se puede eliminar un producto con pedidos activos

### HU-05 — Inicio de Sesión
- Autenticación con **JWT** (token seguro)
- Redirección al panel correcto según rol
- Contraseña almacenada con hash (bcrypt)

---

## 7. Definición de Terminado (DoD)

Una historia queda **terminada** cuando:
- [ ] El endpoint o pantalla funciona correctamente en el entorno de desarrollo
- [ ] Fue revisado por al menos un compañero del equipo (code review)
- [ ] No tiene bugs bloqueantes
- [ ] Está integrado en la rama `main` sin conflictos

---

## 8. Datos del Equipo

| Campo | Valor |
|-------|-------|
| Nombre del proyecto | Sistema de Gestión de Pedidos e Inventario |
| Metodología | Scrum |
| Repositorio | [github.com/acmazoh/Gestion_pedidos_inventario](https://github.com/acmazoh/Gestion_pedidos_inventario) |
| Número de integrantes | *(completar)* |
| Integrantes | *(completar con nombres del equipo)* |

---

## 9. Preguntas Frecuentes del Profesor (preparación)

**¿Cuál es el objetivo del Sprint 2?**  
Implementar el flujo completo de un pedido: desde que el mesero lo toma, pasa por cocina y se cobra en caja, junto con autenticación de usuarios y gestión básica de inventario y productos.

**¿Cómo priorizaron los requisitos?**  
Usamos el método MoSCoW: las historias *Must Have* son el núcleo del negocio (sin ellas el sistema no funciona); las *Should Have* mejoran la experiencia pero el sistema puede operar sin ellas temporalmente.

**¿Cómo manejan el control de inventario?**  
Al crear un pedido, el sistema descuenta automáticamente las unidades del inventario. Si el stock llega al mínimo configurado, se genera una alerta visible para el administrador.

**¿Qué queda para sprints siguientes?**  
Reportes avanzados (cierre de caja, exportar Excel), recuperación de contraseña e historial de entradas de inventario por proveedor.
