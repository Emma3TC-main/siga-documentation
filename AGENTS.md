# Gobierno documental

- Fuente de verdad: `SIGA_Documentacion_Tecnica_Final_v1.2/`; aplicar también su `AGENTS.md`.
- Prioridad: manuales/ADR aprobados, `database/logical_model.md`, `database/physical_model.sql`, `database/dictionary.md`, fuentes `diagramas/**/*.puml`, contratos `api/*.yaml`, reglas `especificaciones/` y `trazabilidad/`.
- Excluir `diagramas_render/` y `out/` de inferencias de implementación. No cambiar fuentes aprobadas para justificar divergencias del código; registrar la decisión pendiente.
- Comprobar contratos y matrices de pruebas afectadas; ejecutar validadores documentales cuando se modifiquen fuentes canónicas. No declarar validación sin evidencia.
- Revisar estado Git antes de cambios y preservar trabajo local. Las tareas de configuración local no autorizan publicar, desplegar ni consumir recursos cloud.
