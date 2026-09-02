# ADR-019 — Fuentes PlantUML canónicas y derivados visuales

**Estado:** Aceptado  
**Versión de aplicación:** SIGA v1.2 — Proveedores  
**Ámbito:** documentación, diagramación, agentes de IA, automatización y sustentación

## Contexto

La versión v1.1 incorporó ajustes de presentación y correcciones de renderizado PlantUML para mejorar legibilidad: tipografía, espaciado, DPI, colores, separación de capas, estilos de secuencia, notas ancladas, saltos de línea y ajustes de layout.

La versión v1.2 incorpora cambios funcionales de Proveedores y es la línea técnica vigente. Mezclar una fuente optimizada para presentación con una fuente usada por agentes o desarrolladores aumenta el riesgo de que un cambio puramente visual sea interpretado como una decisión de dominio.

## Decisión

Se separan explícitamente dos clases de artefacto:

### 1. Fuentes canónicas
Ruta:

`diagramas/**/*.puml`

Son la única fuente PlantUML que puede ser utilizada para:
- implementación;
- revisión arquitectónica;
- trazabilidad;
- generación de código o tareas;
- contexto de agentes de IA;
- validación contra SQL, OpenAPI, CUS/RF/HU y ADR.

Los originales de v1.2 se conservan sin modificaciones visuales adicionales.

### 2. Derivados visuales
Ruta:

`diagramas_render/**/*.puml`

Se generan desde los originales canónicos y sirven únicamente para:
- renderizado;
- informes;
- Word;
- sustentación;
- exportación PNG/SVG;
- material visual.

Un derivado visual **no puede cambiar semántica**. Solo puede modificar presentación: `skinparam`, tipografía, color, DPI, espaciado, orientación, wrapping y ayudas de layout que no introduzcan relaciones funcionales.

## Herencia visual de v1.1

Los 59 diagramas comunes entre v1.1 y v1.2 fueron comparados. La v1.2 ya conserva los ajustes visuales de v1.1; en 13 fuentes solo cambió contenido asociado a Proveedores. Los dos diagramas nuevos de Proveedores (`UML_10` y `UML_11`) reciben en sus derivados un perfil visual equivalente al utilizado por la familia UML de v1.1.

Por ello no se reescriben los originales v1.2: los derivados reutilizan su contenido semántico y agregan únicamente una capa de presentación.

## Reglas de precedencia

En caso de conflicto:

1. ADR/reglas aprobadas.
2. `database/logical_model.md`.
3. `database/physical_model.sql`.
4. `database/dictionary.md`.
5. `diagramas/**/*.puml`.
6. OpenAPI, matrices y especificaciones sincronizadas.
7. `diagramas_render/**/*.puml` — solo presentación.

La cadena completa de coherencia del modelo de datos continúa regida por ADR-018.

## Flujo de cambio

1. Modificar la fuente canónica.
2. Ejecutar validaciones.
3. Regenerar `diagramas_render/`.
4. Ejecutar validación de paridad canónico/derivado.
5. Renderizar.
6. Insertar el render en informe o manual.

Los derivados no se editan a mano.

## Consecuencias

### Positivas
- Los agentes de IA leen una única fuente funcional.
- Los informes pueden usar una presentación mejorada sin contaminar la especificación.
- Se preservan los fixes de render de v1.1.
- Es posible regenerar los derivados de forma determinista.
- Las diferencias visuales no alteran trazabilidad ni arquitectura.

### Costos
- Existe un segundo árbol de archivos generado.
- Cada cambio canónico exige regenerar derivados antes de publicar material visual.

## Controles

- `AGENTS.md` prohíbe a agentes usar `diagramas_render/`.
- `tools/generar_derivados_visuales.py` genera los derivados.
- `tools/validar_fuentes_y_derivados.py` verifica paridad semántica.
- `manifest_diagramas_v1.2.json` registra hashes y relación canónico/derivado.
- `VALIDACION_EXHAUSTIVA_v1.2_VISUAL.txt` documenta la revisión ejecutada.
