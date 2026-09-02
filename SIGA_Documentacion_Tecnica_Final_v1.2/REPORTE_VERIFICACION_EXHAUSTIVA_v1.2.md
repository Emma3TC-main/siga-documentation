# Reporte de verificación exhaustiva — SIGA v1.2

## Resultado ejecutivo

**Estado: APROBADO.** Se preservaron los **61 PlantUML canónicos v1.2** sin cambios de contenido ni de bytes. Se creó una segunda familia, `diagramas_render/`, con **61 derivados visuales** destinados exclusivamente a informe/renderizado.

La versión v1.1 se utilizó únicamente como referencia de estilo y fixes. La comparación mostró que los **59 diagramas comunes ya conservaban el mismo fingerprint visual**; 46 eran idénticos y 13 solo contenían el delta funcional de Proveedores. Por ello no se reescribieron los originales v1.2. Los dos UML nuevos de Proveedores reciben el perfil visual únicamente en sus derivados.

## Gobierno adoptado

- `diagramas/**/*.puml`: **canónico / implementación / agentes / IA**.
- `diagramas_render/**/*.puml`: **derivado / Word / informe / sustentación / render**.
- `AGENTS.md`: exclusión obligatoria de `diagramas_render/**` para RAG y agentes.
- `ADR-019`: decisión técnica formal de separación de fuentes.
- `canonical_hashes_v1.2.json`: hashes de no regresión.
- `manifest_diagramas_v1.2.json`: relación canónico ↔ derivado.

## Validaciones principales

| Control | Resultado |
|---|---:|
| PlantUML canónicos | 61/61 preservados |
| Derivados visuales | 61/61 |
| Paridad semántica derivado/canónico | 61/61 |
| Estructura `@startuml/@enduml` canónica | 61/61 |
| Estructura `@startuml/@enduml` derivada | 61/61 |
| `!includeurl` / referencias remotas | 0 |
| Tablas SQL | 40 |
| Distribución | 7 / 6 / 15 / 2 / 3 / 7 |
| FK cross-schema | 0 |
| OpenAPI YAML | 6 válidos |
| Microservicios | 6 |
| Supplier Service | No existe |
| Manual Técnico renderizado | 62/62 páginas revisadas |

## Documentación técnica

Durante la revisión exhaustiva se detectaron referencias principales del Manual Técnico que todavía reflejaban parcialmente la línea v1.1, aunque la adenda de Proveedores ya estaba incorporada. En la **copia gobernada** se sincronizaron de forma mínima CUS-31/CUN-01, responsabilidad de Catalog, bounded contexts, API/eventos, CUS-07 y la identificación de versión. No se rediseñó la arquitectura y no se modificó ningún PlantUML canónico.

## Limitación declarada

El entorno de revisión no disponía de compilador PlantUML local, por lo que la verificación de las 122 fuentes se realizó mediante estructura, hashes, paridad canónico/derivado y comparación de directivas visuales, no mediante compilación binaria. Los archivos comunes de v1.2 mantienen los fixes y directivas visuales de v1.1 sin regresión.

El detalle completo está en `VALIDACION_EXHAUSTIVA_v1.2_VISUAL.txt`.
