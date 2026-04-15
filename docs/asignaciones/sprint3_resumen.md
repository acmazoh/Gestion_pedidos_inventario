# Restin POS — Asignaciones Sprint 3
> Entrega que cubre el trabajo de **Sprint 1 + Sprint 2 + Sprint 3**

---

## Distribución de requisitos

| Persona | Issues | Extra |
|---|---|---|
| [Andrés (acmazoh)](./acmazoh.md) | RF-01, RF-02, RF-06, RF-07 | Diagrama de clases + E-R |
| [Juan José (jjpalacioz)](./jjpalacioz.md) | RF-03, RF-04, RF-05, RF-13 | Diagrama de secuencia + casos de uso |
| [Alejandro (alejo180905)](./alejo180905.md) | RF-10, RF-11, RF-15 | Diagrama de actividades |
| [Mariana (Maripatino)](./maripatino.md) | RF-08, RF-09, RF-14 | Imagen corporativa (logo, slogan, paleta) |

> Andrés tiene carga reducida (~70%) porque desarrolló todo el backend de sprints anteriores.

---

## Estado general de requisitos

| Estado | RFs |
|---|---|
| ✅ Backend completo — solo falta frontend | RF-01, RF-02, RF-03, RF-04, RF-05, RF-06, RF-07, RF-08, RF-09, RF-10 |
| 🟡 Backend parcial — falta completar y hacer frontend | RF-13, RF-14, RF-15 |
| ❌ Por empezar (backend + frontend) | RF-11 |

---

## Diagramas — corregir incoherencias con el proyecto actual

Los diagramas ya existen pero tienen errores. Cada uno corrige los suyos:

| Persona | Diagrama(s) | Archivo |
|---|---|---|
| Andrés | Clases + Entidad-Relación | `docs/diagramas/diagrama_clases.md` · `diagrama_entidad_relacion.md` |
| Juan José | Secuencia + Casos de uso | `docs/diagramas/diagrama_secuencia.md` · `diagrama_casos_uso.md` |
| Alejandro | Actividades | `docs/diagramas/diagrama_actividades.md` |

> Asegurarse de que los diagramas reflejen los modelos, endpoints y flujos **tal como están implementados** en el código.

---

## Imagen corporativa — Mariana

- [ ] Logo del proyecto (isotipo, logotipo o imagotipo)
- [ ] Slogan
- [ ] Paleta de colores con códigos hex
- [ ] Capturas de la interfaz que muestren la identidad visual aplicada

---

## Tareas grupales — todos participan

| Tarea | Qué hace cada uno |
|---|---|
| **Documentación** | Cada quien documenta sus propios RFs en README y comentarios de código |
| **Reuniones semanales** | Registrar en la wiki de GitHub: qué hice, qué haré, qué impedimentos tuve |
| **Retrospectiva** | Responder: qué seguir haciendo, qué empezar, qué dejar de hacer |
| **Video** | Todos participan: pitch + demo de los RFs de la entrega |
| **Sustentación** | Cada uno presenta y defiende sus propios RFs |

---

## Cadenas de dependencia (coordinar)

```
RF-03 (Juan José) → RF-05 (Juan José) → RF-10 (Alejandro)
                                       ↘ RF-07 (Andrés) — necesita ingredientes de RF-15
RF-15 (Alejandro) ─────────────────────────────────────────↗

RF-13 (Juan José) ↔ RF-14 (Mariana)   ← login usa los roles definidos por Mariana
RF-09 (Mariana)   → RF-11 (Alejandro) ← "entregada" dispara el registro de venta
```

---

## Links útiles
- [Tablero GitHub](https://github.com/acmazoh/Gestion_pedidos_inventario/issues)
- [Milestones](https://github.com/acmazoh/Gestion_pedidos_inventario/milestones)
