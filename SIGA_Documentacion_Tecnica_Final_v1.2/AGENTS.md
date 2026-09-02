# AGENTS.md — Gobierno de fuentes para implementación y agentes de IA

## Regla obligatoria

Los agentes de programación, asistentes de IA, revisores automáticos y herramientas RAG **deben usar las fuentes canónicas de SIGA v1.2** y **deben ignorar los derivados visuales**.

### Fuentes canónicas

1. Manuales, ADR y reglas aprobadas.
2. `database/logical_model.md`.
3. `database/physical_model.sql`.
4. `database/dictionary.md`.
5. `diagramas/**/*.puml` — fuentes PlantUML canónicas.
6. `api/*.yaml`, `trazabilidad/*.md`, `especificaciones/*.md` y pruebas/matrices sincronizadas.

### Fuentes NO canónicas

- `diagramas_render/**/*.puml`
- PNG/SVG/PDF generados para informe o sustentación.
- `diagramas/datos/DER_02_L#U00f3gico (dbDiagram).svg` heredado de v1.1.
- `REPORTE_CORRECCION_INTEGRAL.md` cuando se use como estado actual; es evidencia histórica.
- `CAMBIOS_DOCX_PARA_APLICAR.md` como instrucción vigente; es registro de migración a v1.2.

## Política para agentes e IA

- No extraer requisitos, entidades, cardinalidades, endpoints, eventos, CUS/RF/HU ni decisiones arquitectónicas desde `diagramas_render/`.
- No editar manualmente `diagramas_render/`.
- Si existe diferencia entre un derivado visual y su original, **manda el archivo de `diagramas/`**.
- Si existe diferencia entre un diagrama canónico y el modelo de datos canónico, aplicar la cadena de gobierno definida en ADR-018.
- Todo cambio funcional se realiza primero en la fuente canónica correspondiente y luego se regeneran los derivados visuales.
- Para búsquedas automáticas, embeddings o contexto de agentes, excluir por defecto `diagramas_render/**`.

## Flujo correcto

`cambio funcional -> fuentes canónicas -> validación -> regenerar derivados -> renderizar -> insertar imagen en informe`

Nunca:

`imagen/derivado visual -> inferir implementación`

Ver `adr/ADR-019_Fuentes_PlantUML_Canonicas_y_Derivados_Visuales.md`.
