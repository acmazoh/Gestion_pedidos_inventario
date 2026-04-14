#!/usr/bin/env bash
# =============================================================================
# crear_issues_restin.sh
# Crea los issues reestructurados del proyecto Restin en GitHub via gh CLI
# Repo: acmazoh/Gestion_pedidos_inventario
# =============================================================================

set -e

REPO="acmazoh/Gestion_pedidos_inventario"

echo "============================================="
echo " Creando issues reestructurados - Restin POS"
echo " Repo: $REPO"
echo "============================================="
echo ""

# -----------------------------------------------------------------------------
# SPRINT 3
# -----------------------------------------------------------------------------

echo "[1/10] RF-03: Crear Nueva Orden en POS..."
gh issue create \
  --repo "$REPO" \
  --title "RF-03: Crear Nueva Orden en POS" \
  --assignee "jjpalacioz" \
  --label "requerimiento,sprint-3,high-priority" \
  --body "## RF-03: Crear Nueva Orden en POS
**Asignado a:** Juan José Palacio | **Prioridad:** High | **Estado:** 30% completado

### Descripción
El sistema debe permitir que un mesero o usuario autorizado inicie una nueva orden en la interfaz POS, asociándola a una mesa del restaurante o a un identificador de orden en línea. La orden debe registrarse con timestamp y ser editable antes de ser confirmada.

---

### Criterios de Aceptación

#### ✅ Backend
- [x] Endpoint POST \`/api/orders/create\` funciona y crea orden en BD
- [x] Orden se asocia correctamente a mesa o identificador online
- [x] Timestamp se registra automáticamente
- [ ] Orden se puede modificar (agregar/quitar productos) antes de confirmar
- [ ] Validación: no permitir órdenes vacías
- [ ] Errores están bien documentados en la respuesta

#### ❌ Frontend
- [ ] Vista de \"Nueva Orden\" diseñada y maquetada
- [ ] Selector de mesa funciona y muestra mesas disponibles
- [ ] Opción de \"orden online\" como alternativa
- [ ] Interfaz permite agregar productos a la orden
- [ ] Botón \"Crear Orden\" está habilitado y conecta con el backend
- [ ] Mensaje de confirmación cuando la orden se crea
- [ ] Manejo de errores: muestra mensaje si algo falla

#### 📄 Documentación
- [ ] README actualizado: cómo crear una orden (paso a paso)
- [ ] Comentarios en el código explicando qué hace cada función
- [ ] Estructura de datos de la orden documentada
- [ ] Endpoint documentado en Postman o similar

#### 🔗 Integración + Tests
- [ ] Frontend conecta correctamente con el backend
- [ ] Se puede crear una orden desde la interfaz sin errores
- [ ] Orden aparece en la BD con datos correctos
- [ ] Timestamp se guarda correctamente
- [ ] Prueba manual: crear 3 órdenes diferentes y verificar"

echo "  ✓ RF-03 creado"
echo ""

# -----------------------------------------------------------------------------

echo "[2/10] RF-13: Autenticación de Usuarios..."
gh issue create \
  --repo "$REPO" \
  --title "RF-13: Autenticación de Usuarios" \
  --assignee "jjpalacioz" \
  --label "requerimiento,sprint-3,high-priority" \
  --body "## RF-13: Autenticación de Usuarios
**Asignado a:** Juan José Palacio | **Prioridad:** High | **Estado:** 20% completado

### Descripción
Si un usuario intenta acceder al sistema, el Restin POS System debe proporcionar funcionalidad de autenticación que permita al usuario iniciar sesión con una combinación única de nombre de usuario y contraseña.

---

### Criterios de Aceptación

#### 🟡 Backend
- [x] Endpoint POST \`/api/auth/login\` existe y valida credenciales
- [ ] Contraseñas se encriptan correctamente (hashing seguro)
- [ ] Retorna token de sesión o JWT válido
- [ ] Validación: rechaza credenciales inválidas
- [ ] Manejo de intentos fallidos (límite de intentos)
- [ ] Errores bien documentados en respuestas

#### ❌ Frontend
- [ ] Pantalla de login diseñada y maquetada
- [ ] Campos para usuario y contraseña funcionales
- [ ] Botón \"Iniciar Sesión\" conecta con backend
- [ ] Mensaje de error si credenciales son inválidas
- [ ] Redirección a dashboard después de login exitoso
- [ ] Sesión persiste (no vuelve a pedir login)
- [ ] Botón \"Cerrar Sesión\" funciona

#### 📄 Documentación
- [ ] README: pasos para crear un usuario y hacer login
- [ ] Comentarios en código del endpoint de auth
- [ ] Estructura de token/sesión documentada
- [ ] Datos sensibles no están en logs

#### 🔗 Integración + Tests
- [ ] Login con credenciales correctas funciona
- [ ] Login con credenciales incorrectas falla
- [ ] Token se valida en requests posteriores
- [ ] Sesión expira después de X minutos
- [ ] Prueba manual: login, navegar, logout"

echo "  ✓ RF-13 creado"
echo ""

# -----------------------------------------------------------------------------

echo "[3/10] RF-14: Gestionar Roles de Usuarios..."
gh issue create \
  --repo "$REPO" \
  --title "RF-14: Gestionar Roles de Usuarios" \
  --assignee "Maripatino" \
  --label "requerimiento,sprint-3,high-priority" \
  --body "## RF-14: Gestionar Roles de Usuarios
**Asignado a:** Mariana Patiño | **Prioridad:** High | **Estado:** 15% completado

### Descripción
Si un administrador gestiona usuarios del sistema, el Restin POS System debe proporcionar la capacidad de definir y gestionar roles de usuario incluyendo administrador, mesero, personal de cocina y cajero.

---

### Criterios de Aceptación

#### 🟡 Backend
- [x] Tabla de roles existe en BD (admin, cashier, kitchen, waiter)
- [x] Endpoint POST \`/api/users/\` permite crear usuarios con rol
- [ ] Endpoint PUT \`/api/users/{id}\` permite cambiar rol
- [ ] Validación: solo admin puede cambiar roles
- [ ] Cada rol tiene permisos definidos
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Panel de administración de usuarios diseñado
- [ ] Tabla muestra lista de usuarios
- [ ] Opción para crear nuevo usuario
- [ ] Selector de rol funciona (admin, cashier, kitchen, waiter)
- [ ] Opción para editar rol de usuario existente
- [ ] Opción para desactivar/eliminar usuario
- [ ] Confirmación antes de eliminar

#### 📄 Documentación
- [ ] README: cómo crear un admin, mesero, cocinero
- [ ] Comentarios en código de permisos
- [ ] Tabla de permisos por rol documentada
- [ ] Proceso de cambio de rol explicado

#### 🔗 Integración + Tests
- [ ] Admin puede crear usuarios
- [ ] Admin puede cambiar roles
- [ ] Usuario no-admin NO puede cambiar roles (validación)
- [ ] Permisos se aplican correctamente por rol
- [ ] Prueba manual: crear 4 usuarios distintos con roles diferentes"

echo "  ✓ RF-14 creado"
echo ""

# -----------------------------------------------------------------------------

echo "[4/10] RF-15: Gestionar Ingredientes (Inventario)..."
gh issue create \
  --repo "$REPO" \
  --title "RF-15: Gestionar Ingredientes (Inventario)" \
  --assignee "alejo180905" \
  --label "requerimiento,sprint-3,high-priority" \
  --body "## RF-15: Gestionar Ingredientes (Inventario)
**Asignado a:** Alejandro Correa | **Prioridad:** High | **Estado:** 25% completado

### Descripción
Si un administrador accede al módulo de gestión de inventario, el Restin POS System debe proporcionar la capacidad de crear, actualizar, eliminar y mantener registros de ingredientes incluyendo nombre, unidad de medida e inventario actual.

---

### Criterios de Aceptación

#### 🟡 Backend
- [x] Modelo de Ingrediente existe en BD
- [x] Endpoint POST \`/api/ingredients/\` crea ingrediente
- [x] Endpoint GET \`/api/ingredients/\` lista ingredientes
- [ ] Endpoint PUT \`/api/ingredients/{id}\` actualiza ingrediente
- [ ] Endpoint DELETE \`/api/ingredients/{id}\` elimina ingrediente
- [ ] Validación: nombre único, cantidad >= 0
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Gestión de Ingredientes diseñada
- [ ] Tabla muestra lista de ingredientes con nombre, unidad, cantidad
- [ ] Botón \"Agregar Ingrediente\" abre formulario
- [ ] Formulario permite crear ingrediente (nombre, unidad, cantidad inicial)
- [ ] Opción para editar ingrediente existente
- [ ] Opción para eliminar ingrediente con confirmación
- [ ] Muestra alertas si ingrediente está bajo de stock

#### 📄 Documentación
- [ ] README: cómo agregar, editar, eliminar ingredientes
- [ ] Comentarios en código CRUD de ingredientes
- [ ] Estructura de datos del ingrediente documentada
- [ ] Unidades de medida soportadas listadas

#### 🔗 Integración + Tests
- [ ] Se puede crear ingrediente desde interfaz
- [ ] Ingrediente aparece en BD y en lista
- [ ] Se puede editar cantidad sin errores
- [ ] Se puede eliminar ingrediente
- [ ] Validación rechaza ingredientes sin nombre
- [ ] Prueba manual: crear 5 ingredientes, editar 2, eliminar 1"

echo "  ✓ RF-15 creado"
echo ""

# -----------------------------------------------------------------------------

echo "[5/10] RF-06: Calcular Total de Orden..."
gh issue create \
  --repo "$REPO" \
  --title "RF-06: Calcular Total de Orden" \
  --assignee "acmazoh" \
  --label "requerimiento,sprint-3,high-priority" \
  --body "## RF-06: Calcular Total de Orden
**Asignado a:** Andrés Camilo Mazo | **Prioridad:** High | **Estado:** 40% completado

### Descripción
Mientras se confirma una orden, el Restin POS System debe calcular automáticamente el precio total de la orden incluyendo precios de productos, cantidades e impuestos configurados en el sistema.

---

### Criterios de Aceptación

#### ✅ Backend
- [x] Endpoint POST \`/api/orders/{id}/calculate-total\` funciona
- [x] Calcula: suma de (precio × cantidad) por cada producto
- [x] Aplica impuestos configurados
- [x] Retorna total correcto
- [x] Maneja decimales correctamente
- [ ] Descuentos se aplican si existen
- [ ] Histórico de cambios en total se registra

#### ❌ Frontend
- [ ] Orden muestra desglose de productos con precios
- [ ] Muestra subtotal (antes de impuesto)
- [ ] Muestra impuesto calculado
- [ ] Muestra total final
- [ ] Actualiza total en tiempo real al agregar/quitar productos
- [ ] Visualmente clara y fácil de leer
- [ ] Manejo de errores de cálculo

#### 📄 Documentación
- [ ] README: cómo se calcula el total (fórmula)
- [ ] Comentarios en código de cálculo
- [ ] Tasa de impuesto configurada documentada
- [ ] Ejemplos de cálculo en documentación

#### 🔗 Integración + Tests
- [ ] Cálculo es correcto con diferentes productos
- [ ] Impuestos se aplican correctamente
- [ ] Total actualiza al cambiar cantidades
- [ ] Decimales se redondean correctamente
- [ ] Prueba manual: calcular total con 5 productos diferentes"

echo "  ✓ RF-06 creado"
echo ""

# -----------------------------------------------------------------------------
# SPRINT 4
# -----------------------------------------------------------------------------

echo "[6/10] RF-11: Registrar Transacciones en Historial de Ventas..."
gh issue create \
  --repo "$REPO" \
  --title "RF-11: Registrar Transacciones en Historial de Ventas" \
  --label "requerimiento,sprint-4,high-priority" \
  --body "## RF-11: Registrar Transacciones en Historial de Ventas
**Asignado a:** Pendiente | **Prioridad:** High | **Estado:** 0% completado

### Descripción
Después de que una orden se marca como entregada, el Restin POS System debe registrar automáticamente la transacción en la base de datos de historial de ventas incluyendo identificador de orden, productos vendidos, cantidades, timestamp y valor total de pago.

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Modelo de Transacción existe en BD
- [ ] Endpoint POST \`/api/sales/register\` registra venta completa
- [ ] Guarda: ID orden, productos, cantidades, timestamp, total
- [ ] Automático: se registra cuando orden pasa a \"entregada\"
- [ ] Validación: transacción no puede duplicarse
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Historial de Ventas existe
- [ ] Muestra lista de ventas con fecha, productos, total
- [ ] Búsqueda por fecha o rango de fechas
- [ ] Búsqueda por monto total
- [ ] Opción de descargar/exportar historial
- [ ] Interfaz clara y fácil de navegar

#### 📄 Documentación
- [ ] README: cómo ver historial de ventas
- [ ] Comentarios en código de registro
- [ ] Estructura de transacción documentada
- [ ] Filtros soportados listados

#### 🔗 Integración + Tests
- [ ] Orden completada registra automáticamente venta
- [ ] Datos en BD son correctos
- [ ] Historial muestra todas las ventas
- [ ] Búsqueda funciona correctamente
- [ ] Prueba manual: completar 3 órdenes y verificar en historial"

echo "  ✓ RF-11 creado"
echo ""

# -----------------------------------------------------------------------------

echo "[7/10] RF-12: Registrar Método de Pago..."
gh issue create \
  --repo "$REPO" \
  --title "RF-12: Registrar Método de Pago" \
  --label "requerimiento,sprint-4,medium-priority" \
  --body "## RF-12: Registrar Método de Pago
**Asignado a:** Pendiente | **Prioridad:** Medium | **Estado:** 0% completado

### Descripción
Después de que una venta se completa, el Restin POS System debe proporcionar al cajero la capacidad de registrar el método de pago usado en la transacción incluyendo al menos efectivo o tarjeta.

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Modelo de Método de Pago existe (cash, card, otros)
- [ ] Endpoint POST \`/api/payments/register\` guarda método
- [ ] Valida que método sea válido
- [ ] Asocia pago a orden correctamente
- [ ] Maneja múltiples pagos por orden (parciales)
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Seleccionar Método de Pago existe
- [ ] Opciones: Efectivo, Tarjeta, Cheque (si aplica)
- [ ] Si es tarjeta: opción para ingresar número
- [ ] Si es efectivo: opción para indicar monto recibido
- [ ] Calcula cambio si aplica
- [ ] Confirmación de pago registrado
- [ ] Manejo de errores

#### 📄 Documentación
- [ ] README: cómo registrar pago
- [ ] Comentarios en código de pago
- [ ] Métodos de pago soportados documentados
- [ ] Cálculo de cambio explicado

#### 🔗 Integración + Tests
- [ ] Pago en efectivo se registra correctamente
- [ ] Pago en tarjeta se registra correctamente
- [ ] Cambio se calcula bien en efectivo
- [ ] Pago se asocia a orden correcta
- [ ] Prueba manual: pagar 3 órdenes con métodos diferentes"

echo "  ✓ RF-12 creado"
echo ""

# -----------------------------------------------------------------------------

echo "[8/10] RF-16: Consultar Niveles de Inventario..."
gh issue create \
  --repo "$REPO" \
  --title "RF-16: Consultar Niveles de Inventario" \
  --label "requerimiento,sprint-4,medium-priority" \
  --body "## RF-16: Consultar Niveles de Inventario
**Asignado a:** Pendiente | **Prioridad:** Medium | **Estado:** 0% completado

### Descripción
Si un administrador solicita información de inventario, el Restin POS System debe proporcionar la capacidad de consultar los niveles de inventario actuales para todos los ingredientes registrados.

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Endpoint GET \`/api/inventory/current\` retorna todos los ingredientes
- [ ] Muestra: nombre, unidad, cantidad, mínimo recomendado
- [ ] Indica cuáles están bajo de stock
- [ ] Permite filtrar por estado (normal, bajo, crítico)
- [ ] Historial de cambios de inventario disponible
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Nivel de Inventario diseñada
- [ ] Tabla muestra ingredientes con cantidades actuales
- [ ] Código de colores: verde (normal), amarillo (bajo), rojo (crítico)
- [ ] Opción de filtrar por estado de stock
- [ ] Opción de exportar reporte
- [ ] Actualización en tiempo real al hacer cambios
- [ ] Gráfico opcional mostrando tendencias

#### 📄 Documentación
- [ ] README: cómo consultar inventario
- [ ] Comentarios en código
- [ ] Definición de \"bajo\" y \"crítico\" documentada
- [ ] Estados de stock explicados

#### 🔗 Integración + Tests
- [ ] Consulta retorna datos correctos
- [ ] Filtros funcionan (normal, bajo, crítico)
- [ ] Código de colores se muestra
- [ ] Datos se actualizan cuando cambia inventario
- [ ] Prueba manual: ver estado de 10 ingredientes"

echo "  ✓ RF-16 creado"
echo ""

# -----------------------------------------------------------------------------

echo "[9/10] RF-17: Ver Historial de Órdenes..."
gh issue create \
  --repo "$REPO" \
  --title "RF-17: Ver Historial de Órdenes" \
  --label "requerimiento,sprint-4,medium-priority" \
  --body "## RF-17: Ver Historial de Órdenes
**Asignado a:** Pendiente | **Prioridad:** Medium | **Estado:** 0% completado

### Descripción
Si un administrador accede al módulo de historial de órdenes, el Restin POS System debe proporcionar la capacidad de recuperar y visualizar la lista histórica de órdenes procesadas incluyendo detalles de orden y estado.

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Endpoint GET \`/api/orders/history\` retorna todas las órdenes
- [ ] Incluye: ID, fecha, productos, total, estado, mesero
- [ ] Permite filtrar por fecha, estado, mesero
- [ ] Permite buscar por ID de orden
- [ ] Paginación para listas grandes
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Historial de Órdenes existe
- [ ] Tabla muestra órdenes con detalles
- [ ] Filtros: por fecha, por estado (completada, cancelada, etc)
- [ ] Búsqueda por ID de orden
- [ ] Opción de ver detalles de una orden
- [ ] Opción de descargar/imprimir
- [ ] Paginación funciona

#### 📄 Documentación
- [ ] README: cómo ver historial de órdenes
- [ ] Comentarios en código
- [ ] Estados de orden documentados
- [ ] Filtros soportados listados

#### 🔗 Integración + Tests
- [ ] Historial muestra todas las órdenes
- [ ] Filtros funcionan correctamente
- [ ] Búsqueda por ID funciona
- [ ] Detalles de orden son correctos
- [ ] Prueba manual: buscar y filtrar 5 órdenes distintas"

echo "  ✓ RF-17 creado"
echo ""

# -----------------------------------------------------------------------------

echo "[10/10] RF-18: Generar Reporte Diario de Ventas..."
gh issue create \
  --repo "$REPO" \
  --title "RF-18: Generar Reporte Diario de Ventas" \
  --label "requerimiento,sprint-4,medium-priority" \
  --body "## RF-18: Generar Reporte Diario de Ventas
**Asignado a:** Pendiente | **Prioridad:** Medium | **Estado:** 0% completado

### Descripción
Después de que el día de negocio ha terminado, el Restin POS System debe generar un reporte diario de ventas que incluya ingresos totales, número de órdenes procesadas y distribución de métodos de pago.

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Endpoint POST \`/api/reports/daily\` genera reporte del día
- [ ] Calcula: ingresos totales, # órdenes, métodos de pago
- [ ] Desglose por categoría de producto (si aplica)
- [ ] Compara con días anteriores (tendencias)
- [ ] Genera automáticamente al final del día
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Reporte Diario existe
- [ ] Muestra: fecha, ingresos totales, # órdenes
- [ ] Gráfico de distribución de métodos de pago
- [ ] Tabla con productos más vendidos
- [ ] Comparativa con día anterior
- [ ] Opción de descargar como PDF/Excel
- [ ] Interfaz clara y profesional

#### 📄 Documentación
- [ ] README: cómo generar reporte diario
- [ ] Comentarios en código
- [ ] Fórmulas de cálculo documentadas
- [ ] Campos del reporte explicados

#### 🔗 Integración + Tests
- [ ] Reporte calcula ingresos correctamente
- [ ] # órdenes es exacto
- [ ] Métodos de pago son correctos
- [ ] PDF se genera sin errores
- [ ] Prueba manual: generar reporte de hoy"

echo "  ✓ RF-18 creado"
echo ""

# -----------------------------------------------------------------------------

echo "============================================="
echo " ✅ 10 issues creados exitosamente"
echo " Verifica en: https://github.com/$REPO/issues"
echo "============================================="
