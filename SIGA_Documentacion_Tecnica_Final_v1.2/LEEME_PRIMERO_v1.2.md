# SIGA v1.2 — Base de trabajo con Proveedores

Este paquete es la **base completa fusionada**: conserva todos los archivos no afectados de v1.1 e incorpora el delta de Proveedores v1.2 en sus rutas originales.

## Estado de los DOCX
- `Manual_Tecnico_SIGA_Final.docx` se encuentra sincronizado con v1.2 y con la gestión de Proveedores.
- Los DOCX externos del Informe y Manual Administrativo fueron verificados con los cambios de Proveedores ya aplicados.
- `CAMBIOS_DOCX_PARA_APLICAR.md` se conserva como registro histórico de migración; **no debe reaplicarse** sobre documentos ya actualizados.

## Estado técnico vigente
- 40 tablas: IAM 7 / Catalog 6 / Inventory 15 / Evidence 2 / Audit 3 / Analytics 7.
- 0 FK cross-schema.
- 6 servicios; no se agrega microservicio de proveedores.
- CUN existentes: 7; Proveedor externo se añade como actor de CUN-01.
- CUS: 31; se agrega CUS-31 Gestionar proveedores.

## Artefactos históricos
`REPORTE_CORRECCION_INTEGRAL.md` se conserva como evidencia histórica de v1.1 y puede indicar 38 tablas. No usar esa cifra como estado vigente. Use `VALIDACION_v1.2.txt`.

## DER dbDiagram SVG
El SVG `DER_02_L#U00f3gico (dbDiagram).svg` heredado es v1.1. El script DBML `.txt` sí está actualizado; regenere el SVG si lo va a presentar.

## Fuentes PlantUML: canónico vs render

- **Canónico / agentes / implementación:** `diagramas/**/*.puml`.
- **Solo presentación:** `diagramas_render/**/*.puml`.
- Si difieren, prevalece `diagramas/`.
- Leer `AGENTS.md` y ADR-019 antes de automatizar cambios.
