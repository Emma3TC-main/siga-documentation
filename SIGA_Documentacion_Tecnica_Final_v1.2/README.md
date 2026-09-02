# SIGA — Documentación Técnica Consolidada v1.2 — Proveedores

Paquete técnico coherente con el Manual Técnico y las decisiones arquitectónicas aprobadas. Incluye Manual DOCX/MD, PlantUML, modelo lógico/físico, diccionario, OpenAPI, ADR, DevOps, trazabilidad y seeds.

## Fuentes de verdad y gobierno
1. Manual/ADR y reglas aprobadas.
2. `database/logical_model.md`.
3. `database/physical_model.sql`.
4. `database/dictionary.md`.
5. DER/UML/OpenAPI/testing sincronizados.

La base PostgreSQL conserva seis schemas con ownership exclusivo y **40 tablas**. No existen FK ni escrituras cross-schema entre microservicios. Inventory+Movement permanece como un único núcleo ACID.

## Diagramas de datos
- DER-01: conceptual global.
- DER-02: lógico global.
- DER-03: físico general por schemas.
- DER-04..09: físicos detallados de IAM, Catalog, Inventory, Evidence, Audit/Notification y Reporting/Analytics.

## Cambios arquitectónicos
Requieren ADR y actualización coordinada de manual, modelo de datos, diagramas, contratos y pruebas. Ver `adr/ADR-018_Modelo_datos_canonico_coherencia.md` y `REPORTE_CORRECCION_INTEGRAL.md`.


## Alcance del cambio v1.2 — Proveedores

Se incorpora gestión básica de proveedores con impacto acotado: `catalog.supplier` como maestro, `inventory.supplier_ref` como proyección local y snapshot de proveedor en entradas. La arquitectura conserva seis servicios y cero FK cross-schema. El alcance **no** incluye órdenes de compra, cotizaciones, cuentas por pagar, homologación avanzada ni portal de proveedor.


> Nota: `REPORTE_CORRECCION_INTEGRAL.md` del paquete base es un registro histórico de v1.1 y puede mencionar 38 tablas. Para el estado vigente use `VALIDACION_v1.2.txt` y `REPORTE_IMPACTO_PROVEEDORES_v1.2.md`.

## Gobierno de diagramas canónicos y derivados visuales

- `diagramas/` contiene las **fuentes PlantUML canónicas v1.2**.
- `diagramas_render/` contiene derivados para informe/renderizado y **no es fuente de implementación**.
- Agentes de IA, herramientas RAG y desarrolladores deben excluir `diagramas_render/**` y leer `AGENTS.md`.
- Los derivados se regeneran con `tools/generar_derivados_visuales.py`.
- La paridad se valida con `tools/validar_fuentes_y_derivados.py`.
- La decisión formal está en `adr/ADR-019_Fuentes_PlantUML_Canonicas_y_Derivados_Visuales.md`.

Las fuentes canónicas de `diagramas/` se mantienen sin cambios visuales adicionales respecto de la v1.2 aprobada.
