#!/usr/bin/env bash
# =============================================================================
# restin_reestructurar.sh
# Reestructuración completa del backlog Restin — versión corregida
#
# DIFERENCIAS CON LA VERSIÓN ANTERIOR:
#   - NO crea milestones (ya existen): los consulta por título
#   - NO intenta borrar issues (requiere admin de org): los cierra con comentario
#   - USA `gh api PATCH --input -` con jq para editar issues existentes
#     (labels, assignees, milestone, body en un solo call)
#   - NO crea issues nuevos: los 20 RF ya existen, solo se editan
#
# Mapeo issue → RF:
#   #1→RF-01  #2→RF-02  #3→RF-03  #4→RF-04  #5→RF-05
#   #7→RF-06  #8→RF-07  #9→RF-08  #10→RF-09 #11→RF-10
#   #14→RF-11 #15→RF-12 #16→RF-13 #17→RF-14 #18→RF-15
#   #20→RF-16 #21→RF-17 #22→RF-18 #23→RF-19 #24→RF-20
#
# Issues a CERRAR (RNF + duplicados):
#   #6(RNF-01) #12(RNF-02) #13(RNF-03) #19(dup auth) #25(RNF-05) #32(RNF-resp)
#   + cualquier issue con número > 32 (creados por scripts anteriores)
#
# Requiere: gh CLI autenticado, jq instalado
# Repo: acmazoh/Gestion_pedidos_inventario
# =============================================================================

set -e

REPO="acmazoh/Gestion_pedidos_inventario"

echo "============================================="
echo " Restin POS - Reestructuración (v2 corregida)"
echo " Repo: $REPO"
echo "============================================="
echo ""

# =============================================================================
# VERIFICAR DEPENDENCIAS
# =============================================================================
if ! gh auth status &> /dev/null; then
  echo "ERROR: gh CLI no está autenticado. Ejecuta: gh auth login"
  exit 1
fi

# =============================================================================
# PASO 1: OBTENER IDs DE MILESTONES EXISTENTES (no crear)
# =============================================================================
echo ">>> PASO 1: Obteniendo IDs de milestones existentes..."
echo ""

S1_ID=$(gh api "repos/$REPO/milestones?state=all&per_page=50" \
  --jq '[.[] | select(.title | test("Sprint 1"))] | .[0].number')
S2_ID=$(gh api "repos/$REPO/milestones?state=all&per_page=50" \
  --jq '[.[] | select(.title | test("Sprint 2"))] | .[0].number')
S3_ID=$(gh api "repos/$REPO/milestones?state=all&per_page=50" \
  --jq '[.[] | select(.title | test("Sprint 3"))] | .[0].number')
S4_ID=$(gh api "repos/$REPO/milestones?state=all&per_page=50" \
  --jq '[.[] | select(.title | test("Sprint 4"))] | .[0].number')

echo "  Sprint 1 ID: $S1_ID"
echo "  Sprint 2 ID: $S2_ID"
echo "  Sprint 3 ID: $S3_ID"
echo "  Sprint 4 ID: $S4_ID"
echo ""

for VAR_NAME in S1_ID S2_ID S3_ID S4_ID; do
  eval "VAL=\$$VAR_NAME"
  if [[ -z "$VAL" || "$VAL" == "null" ]]; then
    echo "ERROR: No se encontró milestone $VAR_NAME."
    echo "  Verifica los títulos de los milestones en: https://github.com/$REPO/milestones"
    exit 1
  fi
done

echo "  ✓ Los 4 milestones encontrados correctamente"
echo ""

# =============================================================================
# PASO 2: CERRAR ISSUES NRF Y DUPLICADOS
# Los RNF no se borran (no tenemos permisos de admin), se cierran con comentario
# =============================================================================
echo ">>> PASO 2: Cerrando issues NRF y duplicados..."
echo ""

close_issue() {
  local num="$1"
  local msg="$2"
  echo "  Cerrando #$num..."
  gh issue close "$num" --repo "$REPO" \
    --comment "⚠️ **Cerrado en reestructuración del backlog.** $msg" \
    2>/dev/null \
    && echo "  ✓ #$num cerrado" \
    || echo "  (issue #$num ya estaba cerrado o no existe)"
}

close_issue 6  "RNF-01 (Rendimiento < 2s): este requisito queda embebido como nota en todos los issues RF de Sprint 1 y 2."
close_issue 12 "RNF-02 (Disponibilidad): embebido en RF-08 Vista de Cocina (issue #9)."
close_issue 13 "RNF-03 (Usabilidad): embebido en RF-01, RF-03, RF-08 y todos los RF de frontend."
close_issue 19 "Esta validación de credenciales queda completamente cubierta dentro de RF-13 Autenticación (issue #16)."
close_issue 25 "RNF-05 (Compatibilidad browsers): embebido en RF-02 (issue #2) y RF-19 (issue #23)."
close_issue 32 "RNF (Responsividad): embebido como criterio de aceptación en todos los RF de frontend."

echo ""
echo "  Buscando posibles duplicados con número > 32..."
EXTRA=$(gh issue list --repo "$REPO" --state open --json number \
  --jq '[.[] | select(.number > 32)] | .[].number' 2>/dev/null || true)
if [[ -n "$EXTRA" ]]; then
  for num in $EXTRA; do
    echo "  Cerrando duplicado #$num..."
    gh issue close "$num" --repo "$REPO" \
      --comment "Cerrado: duplicado de ejecución anterior del script de reestructuración." \
      2>/dev/null || echo "  (no se pudo cerrar #$num)"
  done
else
  echo "  No se encontraron duplicados > #32"
fi

echo ""
echo "  ✓ Issues NRF y duplicados procesados"
echo ""

# =============================================================================
# FUNCIÓN AUXILIAR: editar issue sin jq
#   - usa gh issue edit --body-file para el cuerpo (soporta multiline y chars especiales)
#   - usa printf para construir JSON de metadata (no necesita jq)
# =============================================================================
edit_issue() {
  local num="$1"
  local title="$2"
  local milestone="$3"          # número entero, ej: 1
  local assignees_json="$4"     # array JSON literal, ej: '["acmazoh"]'
  local labels_json="$5"        # array JSON literal, ej: '["requerimiento","modulo:productos"]'
  local body="$6"

  echo "  Editando #$num → $title ..."

  # Paso 1: actualizar título y cuerpo con gh issue edit
  local tmpfile
  tmpfile=$(mktemp /tmp/gh_issue_body_XXXXXX.md)
  printf '%s' "$body" > "$tmpfile"

  gh issue edit "$num" --repo "$REPO" \
    --title "$title" \
    --body-file "$tmpfile" > /dev/null

  rm -f "$tmpfile"

  # Paso 2: actualizar milestone, assignees y labels via API PATCH
  # printf construye JSON válido sin necesitar jq
  printf '{"milestone":%s,"assignees":%s,"labels":%s}' \
    "$milestone" "$assignees_json" "$labels_json" \
  | gh api "repos/$REPO/issues/$num" -X PATCH --input - > /dev/null

  echo "  ✓ #$num actualizado"
}

# =============================================================================
# PASO 3: EDITAR ISSUES RF (Sprint 1)
# =============================================================================
echo ">>> PASO 3: Editando issues RF — Sprint 1..."
echo ""

# --------------------------------------------------------------------------
# RF-01 → Issue #1 | acmazoh | Sprint 1
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-01: Gestión de Productos del Menú
**Asignado a:** Andrés Camilo Mazo (acmazoh) | **Sprint:** 1 | **Prioridad:** Alta

### Descripción
Si un administrador accede al módulo de gestión de productos, el Restin POS debe permitir crear, actualizar y eliminar productos del menú incluyendo nombre, categoría, precio, descripción e ingredientes asociados.

> ⚠️ **RNF embebidos:**
> - **RNF-01 (Rendimiento):** Operaciones CRUD deben responder en < 2 segundos.
> - **RNF-03 (Usabilidad):** Formulario operable sin capacitación previa.
> - **RNF-06 (Responsividad):** Interfaz funcional en desktop y tablet.

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Endpoint POST `/api/products/` crea producto con todos los campos
- [x] Endpoint PUT `/api/products/{id}` actualiza producto existente
- [x] Endpoint DELETE `/api/products/{id}` elimina producto
- [x] Asociación de ingredientes al producto funciona
- [ ] Validación: nombre único, precio > 0
- [ ] Errores documentados en respuesta

#### ❌ Frontend
- [ ] Pantalla de Gestión de Productos diseñada
- [ ] Tabla: nombre, categoría, precio
- [ ] Formulario crear/editar (nombre, categoría, precio, descripción, ingredientes)
- [ ] Botón eliminar con confirmación
- [ ] Mensajes de éxito/error visibles
- [ ] Respuesta visual < 2 segundos
- [ ] Adaptable a tablet

#### 📄 Documentación
- [ ] README: cómo crear, editar y eliminar productos
- [ ] Comentarios en código de endpoints
- [ ] Estructura de datos documentada

#### 🔗 Integración + Tests
- [ ] CRUD completo desde interfaz sin errores
- [ ] Ingredientes asociados se guardan bien
- [ ] Prueba manual: crear 3 productos, editar 2, eliminar 1
HEREDOC
)
edit_issue 1 \
  "RF-01: Gestión de Productos del Menú" \
  "$S1_ID" \
  '["acmazoh"]' \
  '["requerimiento","modulo:productos","prioridad:alta","backend:completo"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-02 → Issue #2 | acmazoh | Sprint 1
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-02: Visualizar Productos Disponibles en POS
**Asignado a:** Andrés Camilo Mazo (acmazoh) | **Sprint:** 1 | **Prioridad:** Alta

### Descripción
Cuando un usuario accede a la interfaz POS de ventas, el sistema debe mostrar los productos disponibles consultando la base de datos de productos activos.

> ⚠️ **RNF embebidos:**
> - **RNF-01 (Rendimiento):** La carga de productos debe completarse en < 2 segundos.
> - **RNF-05 (Compatibilidad):** La vista debe funcionar en Chrome, Firefox y Edge.
> - **RNF-06 (Responsividad):** Usable en tablet (pantalla de punto de venta).

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Endpoint GET `/api/products/` retorna lista de productos activos
- [x] Incluye: nombre, precio, categoría, descripción
- [ ] Filtra productos sin stock o inactivos
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Vista POS muestra catálogo de productos
- [ ] Productos organizados por categoría
- [ ] Cada producto muestra nombre y precio
- [ ] Carga en < 2 segundos
- [ ] Funciona en Chrome, Firefox y Edge
- [ ] Responsive: usable en tablet

#### 📄 Documentación
- [ ] README: cómo navegar el catálogo POS
- [ ] Comentarios en código del endpoint

#### 🔗 Integración + Tests
- [ ] Productos creados en RF-01 aparecen aquí
- [ ] Prueba en 3 navegadores: Chrome, Firefox, Edge
- [ ] Carga correcta con 20+ productos
HEREDOC
)
edit_issue 2 \
  "RF-02: Visualizar Productos Disponibles en POS" \
  "$S1_ID" \
  '["acmazoh"]' \
  '["requerimiento","modulo:productos","prioridad:alta","backend:completo"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-03 → Issue #3 | jjpalacioz | Sprint 1
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-03: Crear Nueva Orden en POS
**Asignado a:** Juan José Palacio (jjpalacioz) | **Sprint:** 1 | **Prioridad:** Alta

### Descripción
Si un mesero o usuario autorizado inicia una nueva orden en la interfaz POS, el sistema debe permitir crearla asociada a una mesa o identificador de orden online, registrando el timestamp automáticamente.

> ⚠️ **RNF embebidos:**
> - **RNF-01 (Rendimiento):** Creación de orden debe responder en < 2 segundos.
> - **RNF-03 (Usabilidad):** El flujo de creación debe ser intuitivo, sin capacitación.

> 🔗 **Depende de:** RF-02 (productos visibles para agregar a la orden)
> 🔗 **Coordinar con Alejo (alejo180905):** RF-15 (ingredientes) y RF-10 (descuento inventario al confirmar)

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Endpoint POST `/api/orders/create` crea orden en BD
- [x] Orden se asocia a mesa o identificador online
- [x] Timestamp se registra automáticamente
- [ ] Orden se puede modificar antes de confirmar
- [ ] Validación: no permitir órdenes vacías
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Vista "Nueva Orden" diseñada y maquetada
- [ ] Selector de mesa disponible
- [ ] Opción de "orden online" como alternativa
- [ ] Interfaz para agregar productos a la orden
- [ ] Botón "Crear Orden" conecta con backend
- [ ] Mensaje de confirmación al crear
- [ ] Manejo de errores visible

#### 📄 Documentación
- [ ] README: cómo crear una orden paso a paso
- [ ] Endpoint documentado en Postman
- [ ] Estructura de datos de la orden

#### 🔗 Integración + Tests
- [ ] Orden creada aparece en BD con datos correctos
- [ ] Timestamp correcto
- [ ] Prueba manual: crear 3 órdenes diferentes
HEREDOC
)
edit_issue 3 \
  "RF-03: Crear Nueva Orden en POS" \
  "$S1_ID" \
  '["jjpalacioz"]' \
  '["requerimiento","modulo:ordenes","prioridad:alta","backend:completo"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-04 → Issue #4 | jjpalacioz | Sprint 1
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-04: Modificar Orden Activa
**Asignado a:** Juan José Palacio (jjpalacioz) | **Sprint:** 1 | **Prioridad:** Alta

### Descripción
Mientras una orden permanece en estado activo y no ha sido confirmada, el sistema debe permitir al usuario modificarla agregando, eliminando o actualizando productos y cantidades.

> ⚠️ **RNF embebidos:**
> - **RNF-01 (Rendimiento):** Cada modificación debe reflejarse en < 2 segundos.
> - **RNF-03 (Usabilidad):** Las acciones de modificar deben ser claras e intuitivas.

> 🔗 **Depende de:** RF-03 (orden activa creada)

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Endpoint PUT `/api/orders/{id}` actualiza productos/cantidades
- [x] Solo permite modificar órdenes en estado activo
- [ ] Validación: no puede quedar con 0 productos
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Lista de productos de la orden editable
- [ ] Botones + / - para cambiar cantidades
- [ ] Botón para eliminar producto de la orden
- [ ] Buscador para agregar nuevos productos
- [ ] Total actualiza en tiempo real
- [ ] Cambios se guardan con botón "Guardar"

#### 📄 Documentación
- [ ] README: cómo modificar una orden
- [ ] Comentarios en código

#### 🔗 Integración + Tests
- [ ] Agregar producto: aparece en orden y BD
- [ ] Cambiar cantidad: se actualiza correctamente
- [ ] Eliminar producto: desaparece de la orden
- [ ] No se puede modificar orden confirmada
- [ ] Prueba manual: modificar una orden 5 veces
HEREDOC
)
edit_issue 4 \
  "RF-04: Modificar Orden Activa" \
  "$S1_ID" \
  '["jjpalacioz"]' \
  '["requerimiento","modulo:ordenes","prioridad:alta","backend:completo"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-05 → Issue #5 | jjpalacioz | Sprint 1
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-05: Confirmar Orden y Enviar a Cocina
**Asignado a:** Juan José Palacio (jjpalacioz) | **Sprint:** 1 | **Prioridad:** Alta

### Descripción
Si una orden está completa, el sistema debe permitir confirmarla y registrarla como solicitud válida para ser procesada por la cocina.

> ⚠️ **RNF embebidos:**
> - **RNF-01 (Rendimiento):** Confirmación debe completarse en < 2 segundos.
> - **RNF-04 (Seguridad):** Solo usuarios autenticados con rol mesero/admin pueden confirmar.

> 🔗 **Depende de:** RF-03, RF-04 (orden activa con productos)
> 🔗 **Desencadena:** RF-06 (cálculo total), RF-07 (validación stock), RF-08 (vista cocina), RF-10 (descuento inventario)
> 🔗 **Punto de coordinación con Alejo:** RF-10 se dispara desde aquí — coordinar que el descuento de inventario funcione en conjunto

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Endpoint POST `/api/orders/{id}/confirm` cambia estado a "confirmada"
- [x] Registra la orden como solicitud de cocina
- [ ] Solo permite confirmar si hay al menos 1 producto
- [ ] Valida que el usuario tiene permisos
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Botón "Confirmar Orden" visible en la vista de orden
- [ ] Solicita confirmación antes de enviar
- [ ] Muestra resumen final antes de confirmar
- [ ] Redirige o muestra estado "Enviada a cocina"
- [ ] Deshabilita modificación después de confirmar

#### 📄 Documentación
- [ ] README: flujo completo de confirmación
- [ ] Estados de orden documentados

#### 🔗 Integración + Tests
- [ ] Orden confirmada aparece en vista de cocina (RF-08)
- [ ] No se puede modificar orden confirmada (RF-04)
- [ ] Inventario se descuenta al confirmar (RF-10)
- [ ] Prueba manual: confirmar 3 órdenes y verificar en cocina
HEREDOC
)
edit_issue 5 \
  "RF-05: Confirmar Orden y Enviar a Cocina" \
  "$S1_ID" \
  '["jjpalacioz"]' \
  '["requerimiento","modulo:ordenes","prioridad:alta","backend:completo"]' \
  "$BODY"

echo ""
echo "  ✓ Sprint 1 completo"
echo ""

# =============================================================================
# PASO 4: EDITAR ISSUES RF (Sprint 2)
# =============================================================================
echo ">>> PASO 4: Editando issues RF — Sprint 2..."
echo ""

# --------------------------------------------------------------------------
# RF-06 → Issue #7 | acmazoh | Sprint 2
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-06: Calcular Total de Orden con Impuestos
**Asignado a:** Andrés Camilo Mazo (acmazoh) | **Sprint:** 2 | **Prioridad:** Alta

### Descripción
Mientras se confirma una orden, el sistema debe calcular automáticamente el precio total incluyendo precios de productos, cantidades e impuestos configurados.

> ⚠️ **RNF embebidos:**
> - **RNF-01 (Rendimiento):** El cálculo debe completarse en < 1 segundo.

> 🔗 **Depende de:** RF-05 (orden confirmada)

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Endpoint POST `/api/orders/{id}/calculate-total` funciona
- [x] Calcula suma de (precio × cantidad) por producto
- [x] Aplica impuestos configurados
- [x] Retorna total correcto con decimales
- [ ] Descuentos se aplican si existen
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Orden muestra desglose: productos, precios, cantidades
- [ ] Muestra subtotal (sin impuesto)
- [ ] Muestra impuesto calculado
- [ ] Muestra total final
- [ ] Total actualiza en tiempo real al modificar cantidades
- [ ] Diseño claro y legible

#### 📄 Documentación
- [ ] Fórmula de cálculo documentada en README
- [ ] Tasa de impuesto configurada documentada
- [ ] Ejemplos de cálculo incluidos

#### 🔗 Integración + Tests
- [ ] Cálculo correcto con diferentes productos y cantidades
- [ ] Impuestos aplicados correctamente
- [ ] Decimales redondeados bien
- [ ] Prueba manual: calcular total con 5 productos
HEREDOC
)
edit_issue 7 \
  "RF-06: Calcular Total de Orden con Impuestos" \
  "$S2_ID" \
  '["acmazoh"]' \
  '["requerimiento","modulo:ordenes","prioridad:alta","backend:completo"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-07 → Issue #8 | acmazoh | Sprint 2
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-07: Validar Stock al Confirmar Orden
**Asignado a:** Andrés Camilo Mazo (acmazoh) | **Sprint:** 2 | **Prioridad:** Alta

### Descripción
En caso de que el inventario de ingredientes requeridos para un producto sea insuficiente, el sistema debe impedir la confirmación de la orden y notificar al usuario qué producto y qué ingrediente están afectados.

> ⚠️ **RNF embebidos:**
> - **RNF-03 (Usabilidad):** El mensaje de error debe ser claro, en español, indicando exactamente qué falta.

> 🔗 **Depende de:** RF-05 (confirmación de orden), RF-15 (ingredientes registrados)
> 🔗 **Coordinar con Alejo:** RF-15 debe tener ingredientes cargados para que esta validación funcione

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Validación de stock corre antes de confirmar la orden
- [x] Retorna error con producto e ingrediente afectado
- [ ] Valida múltiples ingredientes a la vez
- [ ] Errores documentados correctamente

#### ❌ Frontend
- [ ] Mensaje de error claro: "Ingrediente X insuficiente para Producto Y"
- [ ] Muestra qué cantidad hay vs qué cantidad se necesita
- [ ] No permite confirmar mientras haya stock insuficiente
- [ ] Opción de quitar el producto afectado de la orden

#### 📄 Documentación
- [ ] README: qué pasa cuando no hay stock
- [ ] Comentarios en código de validación

#### 🔗 Integración + Tests
- [ ] Crear orden con producto sin stock: no se confirma
- [ ] Mensaje de error correcto
- [ ] Con stock suficiente: se confirma normalmente
- [ ] Prueba manual: probar con 3 escenarios distintos
HEREDOC
)
edit_issue 8 \
  "RF-07: Validar Stock al Confirmar Orden" \
  "$S2_ID" \
  '["acmazoh"]' \
  '["requerimiento","modulo:inventario","prioridad:alta","backend:completo"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-08 → Issue #9 | Maripatino | Sprint 2
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-08: Vista de Cocina en Tiempo Real
**Asignado a:** Mariana Patiño (Maripatino) | **Sprint:** 2 | **Prioridad:** Alta

### Descripción
Después de que una orden es confirmada, el personal de cocina debe poder ver la nueva orden en tiempo real a través de la interfaz de cocina.

> ⚠️ **RNF embebidos:**
> - **RNF-01 (Rendimiento):** La orden debe aparecer en cocina en < 2 segundos de ser confirmada.
> - **RNF-02 (Disponibilidad):** La vista de cocina debe estar disponible sin interrupciones durante la operación.
> - **RNF-03 (Usabilidad):** El personal de cocina debe entender la interfaz sin capacitación.
> - **RNF-06 (Responsividad):** Diseño legible en tablet (dispositivo típico de cocina).

> 🔗 **Depende de:** RF-05 (orden confirmada)

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Endpoint GET `/api/orders/kitchen` retorna órdenes confirmadas pendientes
- [x] Se actualiza al confirmar nuevas órdenes
- [ ] Soporte para polling o WebSocket en tiempo real
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Vista de cocina diseñada (diferente a la vista POS)
- [ ] Muestra tarjetas por orden: mesa, productos, cantidades
- [ ] Órdenes nuevas aparecen automáticamente (sin refrescar página)
- [ ] Indicador visual de órdenes nuevas vs antiguas
- [ ] Diseño legible a distancia (texto grande, alto contraste)
- [ ] Adaptable a tablet

#### 📄 Documentación
- [ ] README: cómo usar la vista de cocina
- [ ] Comentarios en código de actualización en tiempo real

#### 🔗 Integración + Tests
- [ ] Confirmar orden en POS → aparece en cocina en < 2 seg
- [ ] Múltiples órdenes simultáneas se muestran bien
- [ ] Prueba en tablet (tamaño cocina)
HEREDOC
)
edit_issue 9 \
  "RF-08: Vista de Cocina en Tiempo Real" \
  "$S2_ID" \
  '["Maripatino"]' \
  '["requerimiento","modulo:cocina","prioridad:alta","backend:completo"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-09 → Issue #10 | Maripatino | Sprint 2
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-09: Actualizar Estado de Orden (Cocina)
**Asignado a:** Mariana Patiño (Maripatino) | **Sprint:** 2 | **Prioridad:** Alta

### Descripción
Mientras una orden es procesada por el personal de cocina, el sistema debe permitir al personal autorizado actualizar el estado de la orden (en preparación, lista, entregada).

> ⚠️ **RNF embebidos:**
> - **RNF-04 (Seguridad):** Solo usuarios con rol cocina/admin pueden cambiar estados de orden.
> - **RNF-01 (Rendimiento):** Cambio de estado debe reflejarse en < 2 segundos.

> 🔗 **Depende de:** RF-08 (orden visible en cocina)
> 🔗 **Desencadena:** RF-11 (registro en historial cuando pasa a "entregada")

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Endpoint PATCH `/api/orders/{id}/status` actualiza estado
- [x] Estados: confirmada → en_preparacion → lista → entregada
- [ ] Solo personal autorizado puede cambiar estado
- [ ] Timestamp de cambio de estado registrado
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Botones de estado visibles en cada tarjeta de orden en cocina
- [ ] Flujo claro: En preparación → Lista → Entregada
- [ ] Estado cambia visualmente al actualizar
- [ ] Confirmación antes de marcar como entregada

#### 📄 Documentación
- [ ] README: flujo de estados de una orden
- [ ] Diagrama de estados documentado

#### 🔗 Integración + Tests
- [ ] Cambio de estado se refleja en tiempo real
- [ ] Usuario sin permisos no puede cambiar estado
- [ ] Al marcar "entregada" se registra en historial (RF-11)
- [ ] Prueba manual: procesar 3 órdenes completas
HEREDOC
)
edit_issue 10 \
  "RF-09: Actualizar Estado de Orden (Cocina)" \
  "$S2_ID" \
  '["Maripatino"]' \
  '["requerimiento","modulo:cocina","prioridad:alta","backend:completo"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-10 → Issue #11 | alejo180905 | Sprint 2
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-10: Descuento Automático de Inventario al Confirmar Orden
**Asignado a:** Alejandro Correa (alejo180905) | **Sprint:** 2 | **Prioridad:** Alta

### Descripción
Después de confirmar una orden exitosamente, el sistema debe descontar automáticamente del inventario las cantidades de ingredientes usados en los productos de la orden, según las recetas definidas.

> 🔗 **Depende de:** RF-05 (confirmación de orden), RF-15 (ingredientes cargados en inventario)
> 🔗 **Punto de coordinación con Juan José (jjpalacioz):** RF-05 debe confirmar la orden para que este descuento se dispare — coordinar flujo de datos

---

### Criterios de Aceptación

#### ✅ Backend (Completo - verificar)
- [x] Al confirmar orden, ingredientes se descuentan automáticamente
- [x] Descuenta según cantidades de la receta del producto
- [ ] Validación: si no hay stock suficiente, no confirma (coordina con RF-07)
- [ ] Historial de movimientos de inventario se registra
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Vista de inventario refleja cambios después de confirmar una orden
- [ ] Alerta visual si ingrediente queda bajo de stock tras el descuento
- [ ] Historial de movimientos visible en vista de inventario

#### 📄 Documentación
- [ ] README: cómo funciona el descuento automático
- [ ] Relación producto ↔ ingredientes (recetas) documentada

#### 🔗 Integración + Tests
- [ ] Confirmar orden: verificar que inventario se descontó correctamente
- [ ] Verificar en BD que cantidades son correctas
- [ ] Prueba manual: confirmar orden y revisar inventario
HEREDOC
)
edit_issue 11 \
  "RF-10: Descuento Automático de Inventario al Confirmar Orden" \
  "$S2_ID" \
  '["alejo180905"]' \
  '["requerimiento","modulo:inventario","prioridad:alta","backend:completo"]' \
  "$BODY"

echo ""
echo "  ✓ Sprint 2 completo"
echo ""

# =============================================================================
# PASO 5: EDITAR ISSUES RF (Sprint 3)
# =============================================================================
echo ">>> PASO 5: Editando issues RF — Sprint 3..."
echo ""

# --------------------------------------------------------------------------
# RF-11 → Issue #14 | alejo180905 | Sprint 3
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-11: Registrar Transacciones en Historial de Ventas
**Asignado a:** Alejandro Correa (alejo180905) | **Sprint:** 3 | **Prioridad:** Alta

### Descripción
Después de que una orden se marca como entregada, el sistema debe registrar automáticamente la transacción en el historial de ventas incluyendo ID de orden, productos vendidos, cantidades, timestamp y total.

> 🔗 **Depende de:** RF-09 (orden marcada como entregada)
> 🔗 **Desencadena:** RF-12 (registro de método de pago), RF-17 (historial de órdenes), RF-18 (reporte diario)

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Modelo de Transacción existe en BD
- [ ] Endpoint POST `/api/sales/register` registra venta completa
- [ ] Se dispara automáticamente cuando orden pasa a "entregada"
- [ ] Guarda: ID orden, productos, cantidades, timestamp, total
- [ ] Validación: transacción no puede duplicarse
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Historial de Ventas existe
- [ ] Lista de ventas con fecha, productos, total
- [ ] Búsqueda por fecha o rango de fechas
- [ ] Opción de exportar historial

#### 📄 Documentación
- [ ] README: cómo ver el historial de ventas
- [ ] Estructura de transacción documentada

#### 🔗 Integración + Tests
- [ ] Orden entregada → venta registrada automáticamente
- [ ] Datos en BD correctos
- [ ] Prueba manual: completar 3 órdenes y verificar en historial
HEREDOC
)
edit_issue 14 \
  "RF-11: Registrar Transacciones en Historial de Ventas" \
  "$S3_ID" \
  '["alejo180905"]' \
  '["requerimiento","modulo:ventas","prioridad:alta","backend:pendiente"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-13 → Issue #16 | jjpalacioz | Sprint 3
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-13: Autenticación de Usuarios (Login/Logout)
**Asignado a:** Juan José Palacio (jjpalacioz) | **Sprint:** 3 | **Prioridad:** Alta

### Descripción
Si un usuario intenta acceder al sistema, el Restin POS debe permitirle iniciar sesión con usuario y contraseña únicos, y gestionar el cierre de sesión.

> ⚠️ **RNF embebidos:**
> - **RNF-04 (Seguridad):** Contraseñas con hashing seguro (bcrypt), JWT con expiración, máximo 5 intentos fallidos, sin datos sensibles en logs ni en localStorage.
> - **RNF-03 (Usabilidad):** Login operativo sin capacitación.

> 🔗 **Coordinar con Mariana (Maripatino):** RF-14 define los roles que el login debe validar

---

### Criterios de Aceptación

#### 🟡 Backend (Parcial)
- [x] Endpoint POST `/api/auth/login` valida credenciales
- [ ] Contraseñas hasheadas con bcrypt
- [ ] Retorna JWT con expiración configurada
- [ ] Rate limiting: máximo 5 intentos fallidos
- [ ] Logs no contienen datos sensibles (passwords, tokens)
- [ ] Endpoint POST `/api/auth/logout` invalida sesión

#### ❌ Frontend
- [ ] Pantalla de login diseñada
- [ ] Campos usuario y contraseña
- [ ] Botón "Iniciar Sesión" conectado al backend
- [ ] Mensaje de error en credenciales inválidas
- [ ] Redirección a dashboard tras login exitoso
- [ ] Sesión persiste (no repite login)
- [ ] Botón "Cerrar Sesión" funciona
- [ ] No guarda contraseña en localStorage

#### 📄 Documentación
- [ ] README: cómo crear usuario y hacer login
- [ ] Política de contraseñas documentada
- [ ] Estructura del JWT documentada

#### 🔗 Integración + Tests
- [ ] Login correcto → acceso al sistema
- [ ] Login incorrecto → error claro
- [ ] Rate limiting funciona (5 intentos)
- [ ] Token expira correctamente
- [ ] Prueba manual: login, navegar, logout
HEREDOC
)
edit_issue 16 \
  "RF-13: Autenticación de Usuarios (Login/Logout)" \
  "$S3_ID" \
  '["jjpalacioz"]' \
  '["requerimiento","modulo:usuarios","prioridad:alta","backend:parcial"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-14 → Issue #17 | Maripatino | Sprint 3  (antes: acmazoh — CORRECCIÓN)
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-14: Gestionar Roles de Usuarios
**Asignado a:** Mariana Patiño (Maripatino) | **Sprint:** 3 | **Prioridad:** Alta

### Descripción
Si un administrador gestiona usuarios, el sistema debe permitir definir y asignar roles: administrador, mesero, personal de cocina y cajero.

> ⚠️ **RNF embebidos:**
> - **RNF-04 (Seguridad):** Solo el admin puede cambiar roles. Permisos aplicados correctamente por rol en todos los módulos.

> 🔗 **Coordinar con Juan José (jjpalacioz):** Los roles definidos aquí son los que RF-13 valida en el login

---

### Criterios de Aceptación

#### 🟡 Backend (Parcial)
- [x] Tabla de roles existe en BD (admin, cashier, kitchen, waiter)
- [x] Endpoint POST `/api/users/` crea usuario con rol
- [ ] Endpoint PUT `/api/users/{id}` cambia rol
- [ ] Endpoint DELETE `/api/users/{id}` desactiva usuario
- [ ] Validación: solo admin puede cambiar roles
- [ ] Permisos definidos y aplicados por rol

#### ❌ Frontend
- [ ] Panel de administración de usuarios
- [ ] Tabla de usuarios con nombre, rol, estado
- [ ] Formulario para crear nuevo usuario
- [ ] Selector de rol (admin, cashier, kitchen, waiter)
- [ ] Opción para editar rol de usuario existente
- [ ] Opción para desactivar usuario con confirmación

#### 📄 Documentación
- [ ] Tabla de permisos por rol documentada
- [ ] README: cómo crear y gestionar usuarios

#### 🔗 Integración + Tests
- [ ] Admin crea usuario → login funciona con RF-13
- [ ] No-admin no puede cambiar roles
- [ ] Permisos por rol se aplican en navegación
- [ ] Prueba: crear 4 usuarios con roles distintos (admin, cashier, kitchen, waiter)
HEREDOC
)
edit_issue 17 \
  "RF-14: Gestionar Roles de Usuarios" \
  "$S3_ID" \
  '["Maripatino"]' \
  '["requerimiento","modulo:usuarios","prioridad:alta","backend:parcial"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-15 → Issue #18 | alejo180905 | Sprint 3
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-15: Gestionar Ingredientes (Inventario)
**Asignado a:** Alejandro Correa (alejo180905) | **Sprint:** 3 | **Prioridad:** Alta

### Descripción
Si un administrador accede al módulo de inventario, el sistema debe permitir crear, actualizar, eliminar y mantener registros de ingredientes incluyendo nombre, unidad de medida y cantidad actual.

> 🔗 **Necesita coordinación con Andrés (acmazoh):** RF-07 (validación de stock) depende de que los ingredientes estén registrados aquí

---

### Criterios de Aceptación

#### 🟡 Backend (Parcial)
- [x] Modelo Ingrediente existe en BD
- [x] Endpoint POST `/api/ingredients/` crea ingrediente
- [x] Endpoint GET `/api/ingredients/` lista ingredientes
- [ ] Endpoint PUT `/api/ingredients/{id}` actualiza ingrediente
- [ ] Endpoint DELETE `/api/ingredients/{id}` elimina ingrediente
- [ ] Validación: nombre único, cantidad >= 0
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Gestión de Ingredientes diseñada
- [ ] Tabla: nombre, unidad, cantidad
- [ ] Botón "Agregar Ingrediente" con formulario
- [ ] Editar ingrediente existente
- [ ] Eliminar con confirmación
- [ ] Alerta si ingrediente está bajo de stock

#### 📄 Documentación
- [ ] README: cómo gestionar ingredientes
- [ ] Unidades de medida soportadas listadas

#### 🔗 Integración + Tests
- [ ] CRUD completo desde la interfaz
- [ ] Ingrediente aparece en validación de RF-07
- [ ] Alerta de bajo stock funciona
- [ ] Prueba: crear 5 ingredientes, editar 2, eliminar 1
HEREDOC
)
edit_issue 18 \
  "RF-15: Gestionar Ingredientes (Inventario)" \
  "$S3_ID" \
  '["alejo180905"]' \
  '["requerimiento","modulo:inventario","prioridad:alta","backend:parcial"]' \
  "$BODY"

echo ""
echo "  ✓ Sprint 3 completo"
echo ""

# =============================================================================
# PASO 6: EDITAR ISSUES RF (Sprint 4)
# =============================================================================
echo ">>> PASO 6: Editando issues RF — Sprint 4..."
echo ""

# --------------------------------------------------------------------------
# RF-12 → Issue #15 | alejo180905 | Sprint 4
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-12: Registrar Método de Pago
**Asignado a:** Alejandro Correa (alejo180905) | **Sprint:** 4 | **Prioridad:** Media

### Descripción
Después de completarse una venta, el sistema debe permitir al cajero registrar el método de pago utilizado en la transacción (efectivo o tarjeta como mínimo).

> 🔗 **Depende de:** RF-11 (venta registrada en historial)

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Modelo Método de Pago (cash, card)
- [ ] Endpoint POST `/api/payments/register` guarda método de pago
- [ ] Valida que el método sea válido
- [ ] Asocia pago a orden correctamente
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de selección de método de pago
- [ ] Opciones: Efectivo, Tarjeta
- [ ] Si efectivo: campo para monto recibido y cálculo automático de cambio
- [ ] Confirmación de pago registrado
- [ ] Manejo de errores si falla

#### 📄 Documentación
- [ ] README: cómo registrar un pago
- [ ] Métodos de pago soportados documentados
- [ ] Cálculo de cambio explicado

#### 🔗 Integración + Tests
- [ ] Pago en efectivo se registra correctamente
- [ ] Pago en tarjeta se registra correctamente
- [ ] Cambio se calcula bien en efectivo
- [ ] Prueba manual: pagar 3 órdenes con métodos diferentes
HEREDOC
)
edit_issue 15 \
  "RF-12: Registrar Método de Pago" \
  "$S4_ID" \
  '["alejo180905"]' \
  '["requerimiento","modulo:pagos","prioridad:media","backend:pendiente"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-16 → Issue #20 | alejo180905 | Sprint 4  (antes: acmazoh — CORRECCIÓN)
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-16: Consultar Niveles de Inventario Actuales
**Asignado a:** Alejandro Correa (alejo180905) | **Sprint:** 4 | **Prioridad:** Media

### Descripción
Si un administrador solicita información de inventario, el sistema debe mostrar los niveles actuales de todos los ingredientes registrados con indicadores visuales de estado.

> 🔗 **Depende de:** RF-15 (ingredientes registrados), RF-10 (inventario actualizado tras órdenes)

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Endpoint GET `/api/inventory/current` retorna todos los ingredientes
- [ ] Incluye: nombre, unidad, cantidad, mínimo recomendado
- [ ] Indica estado: normal, bajo, crítico
- [ ] Permite filtrar por estado
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Tabla de inventario con código de colores: verde (normal), amarillo (bajo), rojo (crítico)
- [ ] Filtro por estado de stock
- [ ] Opción de exportar reporte
- [ ] Actualización en tiempo real al confirmar órdenes

#### 📄 Documentación
- [ ] Definición de "bajo" y "crítico" documentada
- [ ] README: cómo consultar el inventario

#### 🔗 Integración + Tests
- [ ] Consulta retorna datos correctos
- [ ] Código de colores y filtros funcionan
- [ ] Prueba: ver estado de 10 ingredientes
HEREDOC
)
edit_issue 20 \
  "RF-16: Consultar Niveles de Inventario Actuales" \
  "$S4_ID" \
  '["alejo180905"]' \
  '["requerimiento","modulo:inventario","prioridad:media","backend:pendiente"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-17 → Issue #21 | Maripatino | Sprint 4
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-17: Ver Historial de Órdenes Procesadas
**Asignado a:** Mariana Patiño (Maripatino) | **Sprint:** 4 | **Prioridad:** Media

### Descripción
Si un administrador accede al historial de órdenes, el sistema debe mostrar la lista de órdenes procesadas con detalles, estados y filtros de búsqueda.

> 🔗 **Depende de:** RF-11 (ventas registradas)

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Endpoint GET `/api/orders/history` con filtros: fecha, estado, mesero
- [ ] Incluye: ID, fecha, productos, total, estado, mesero
- [ ] Búsqueda por ID de orden
- [ ] Paginación para listas grandes
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Tabla con órdenes y detalles
- [ ] Filtros: por fecha, por estado
- [ ] Búsqueda por ID de orden
- [ ] Detalle de orden al hacer click
- [ ] Paginación funciona

#### 📄 Documentación
- [ ] Estados de orden documentados
- [ ] Filtros soportados listados

#### 🔗 Integración + Tests
- [ ] Historial muestra todas las órdenes
- [ ] Filtros funcionan correctamente
- [ ] Prueba: buscar y filtrar 5 órdenes distintas
HEREDOC
)
edit_issue 21 \
  "RF-17: Ver Historial de Órdenes Procesadas" \
  "$S4_ID" \
  '["Maripatino"]' \
  '["requerimiento","modulo:ventas","prioridad:media","backend:pendiente"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-18 → Issue #22 | Maripatino | Sprint 4
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-18: Generar Reporte Diario de Ventas
**Asignado a:** Mariana Patiño (Maripatino) | **Sprint:** 4 | **Prioridad:** Media

### Descripción
Al cierre del día, el sistema debe generar un reporte diario de ventas con ingresos totales, número de órdenes procesadas y distribución de métodos de pago.

> 🔗 **Depende de:** RF-11 (transacciones registradas), RF-12 (métodos de pago)

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Endpoint POST `/api/reports/daily` genera reporte del día
- [ ] Incluye: ingresos totales, # órdenes, distribución de métodos de pago
- [ ] Desglose por categoría de producto
- [ ] Comparativa con día anterior
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Pantalla de Reporte Diario
- [ ] Gráfico de distribución de métodos de pago
- [ ] Tabla de productos más vendidos
- [ ] Comparativa con día anterior
- [ ] Opción de descargar como PDF o Excel

#### 📄 Documentación
- [ ] Fórmulas de cálculo documentadas
- [ ] README: cómo generar reporte diario

#### 🔗 Integración + Tests
- [ ] Ingresos calculados correctamente
- [ ] Métodos de pago son correctos
- [ ] Prueba: generar reporte del día actual
HEREDOC
)
edit_issue 22 \
  "RF-18: Generar Reporte Diario de Ventas" \
  "$S4_ID" \
  '["Maripatino"]' \
  '["requerimiento","modulo:reportes","prioridad:media","backend:pendiente"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-19 → Issue #23 | jjpalacioz | Sprint 4
# (antes: "Search for menu products" sin asignar — ahora RF-19 Buscar Productos)
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-19: Buscar Productos al Registrar Orden
**Asignado a:** Juan José Palacio (jjpalacioz) | **Sprint:** 4 | **Prioridad:** Media

### Descripción
Mientras un usuario registra productos en una orden, el sistema debe permitir buscar productos por nombre o categoría para agilizar la toma de pedido.

> ⚠️ **RNF embebidos:**
> - **RNF-01 (Rendimiento):** Búsqueda debe retornar resultados en < 500ms.
> - **RNF-05 (Compatibilidad):** Funcionar correctamente en Chrome, Firefox y Edge.

> 🔗 **Extiende:** RF-03 y RF-04 (creación y modificación de órdenes)

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Endpoint GET `/api/products/search?q=nombre` busca por nombre
- [ ] Endpoint GET `/api/products/category/{cat}` filtra por categoría
- [ ] Búsqueda case-insensitive y tolerante a errores menores
- [ ] Responde en < 500ms
- [ ] Paginación de resultados
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Barra de búsqueda visible al crear/modificar orden
- [ ] Filtro por categoría (dropdown)
- [ ] Resultados aparecen en tiempo real
- [ ] Click en producto lo agrega a la orden
- [ ] Muestra precio del producto en los resultados

#### 📄 Documentación
- [ ] Categorías disponibles listadas
- [ ] Ejemplos de búsqueda documentados

#### 🔗 Integración + Tests
- [ ] Búsqueda por nombre funciona
- [ ] Filtro por categoría funciona
- [ ] Producto se agrega correctamente a la orden
- [ ] Probado en Chrome, Firefox y Edge
- [ ] Prueba: buscar 5 productos distintos
HEREDOC
)
edit_issue 23 \
  "RF-19: Buscar Productos al Registrar Orden" \
  "$S4_ID" \
  '["jjpalacioz"]' \
  '["requerimiento","modulo:ordenes","modulo:productos","prioridad:media","backend:pendiente"]' \
  "$BODY"

# --------------------------------------------------------------------------
# RF-20 → Issue #24 | Maripatino | Sprint 4
# --------------------------------------------------------------------------
BODY=$(cat <<'HEREDOC'
## RF-20: Exportar Reportes a PDF
**Asignado a:** Mariana Patiño (Maripatino) | **Sprint:** 4 | **Prioridad:** Media

### Descripción
Si un administrador solicita exportar reportes, el sistema debe generar un PDF del reporte de ventas para impresión o archivo.

> 🔗 **Depende de:** RF-18 (reporte diario generado)

---

### Criterios de Aceptación

#### ❌ Backend
- [ ] Endpoint POST `/api/reports/{id}/export-pdf` genera PDF
- [ ] PDF incluye todos los datos del reporte (ingresos, órdenes, métodos de pago)
- [ ] Formato profesional y legible
- [ ] Metadatos correctos (fecha de generación, responsable)
- [ ] Errores documentados

#### ❌ Frontend
- [ ] Botón "Descargar PDF" en pantalla de reporte
- [ ] Click inicia descarga del archivo
- [ ] Opción para vista previa del PDF
- [ ] Manejo de errores si falla la generación

#### 📄 Documentación
- [ ] README: cómo exportar reporte a PDF
- [ ] Formato de archivo explicado

#### 🔗 Integración + Tests
- [ ] PDF se genera sin errores
- [ ] Datos en el PDF son correctos
- [ ] Prueba: generar y descargar 3 PDFs de diferentes fechas
HEREDOC
)
edit_issue 24 \
  "RF-20: Exportar Reportes a PDF" \
  "$S4_ID" \
  '["Maripatino"]' \
  '["requerimiento","modulo:reportes","prioridad:media","backend:pendiente"]' \
  "$BODY"

echo ""
echo "  ✓ Sprint 4 completo"
echo ""

# =============================================================================
# RESUMEN FINAL
# =============================================================================
echo "============================================="
echo " ✅ Reestructuración completada exitosamente"
echo ""
echo " Issues CERRADOS (RNF + duplicados):"
echo "   #6  → RNF-01 (Rendimiento)"
echo "   #12 → RNF-02 (Disponibilidad)"
echo "   #13 → RNF-03 (Usabilidad)"
echo "   #19 → Duplicado de RF-13 autenticación"
echo "   #25 → RNF-05 (Compatibilidad browsers)"
echo "   #32 → RNF (Responsividad)"
echo ""
echo " Issues EDITADOS (20 RF con milestone, assignee, labels, body):"
echo "   Sprint 1 → #1(RF-01) #2(RF-02) #3(RF-03) #4(RF-04) #5(RF-05)"
echo "   Sprint 2 → #7(RF-06) #8(RF-07) #9(RF-08) #10(RF-09) #11(RF-10)"
echo "   Sprint 3 → #14(RF-11) #16(RF-13) #17(RF-14) #18(RF-15)"
echo "   Sprint 4 → #15(RF-12) #20(RF-16) #21(RF-17) #22(RF-18) #23(RF-19) #24(RF-20)"
echo ""
echo " Distribución final:"
echo "   acmazoh    → #1  #2  #7  #8          (4 issues - ~70% carga)"
echo "   jjpalacioz → #3  #4  #5  #16 #23     (5 issues)"
echo "   alejo180905→ #11 #14 #15 #18 #20      (5 issues)"
echo "   Maripatino → #9  #10 #17 #21 #22 #24  (6 issues)"
echo ""
echo " Verifica en:"
echo "   https://github.com/$REPO/issues"
echo "   https://github.com/$REPO/milestones"
echo "============================================="
