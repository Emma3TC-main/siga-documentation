# Verificación de herencia visual v1.1 -> v1.2

## Resultado

- Diagramas PlantUML v1.1: 59.
- Diagramas canónicos v1.2: 61.
- Rutas comunes comparadas: 59.
- Rutas comunes textualmente idénticas: 46.
- Rutas con cambios funcionales v1.2: 13.
- Diferencias en fingerprint de `skinparam`/layout entre v1.1 y v1.2: 0.
- Diagramas nuevos de Proveedores: 2 (`UML_10`, `UML_11`).

## Interpretación

La estética/fixes de v1.1 ya estaban incorporados en los originales v1.2 para todos los diagramas comunes. Por ello no se sobrescribieron los originales. Los cambios detectados en las 13 rutas corresponden al delta funcional de Proveedores (Supplier/SupplierReference, snapshots, eventos, CUS/CUN y conteos de tablas).

Los derivados de `diagramas_render/` copian íntegramente la semántica de v1.2. Los dos UML nuevos reciben un perfil visual de la familia UML v1.1.

## Archivos comunes con cambio funcional

- `bpmn/BPMN_01_Entrada.puml`
- `c4/C4_04_Componente_Inventory.puml`
- `datos/DER_01_Conceptual.puml`
- `datos/DER_02_Logico.puml`
- `datos/DER_03_Fisico.puml`
- `datos/DER_05_Fisico_Catalog.puml`
- `datos/DER_06_Fisico_Inventory.puml`
- `datos/DER_09_Fisico_Reporting_Analytics.puml`
- `secuencia/SEQ_04_Registrar_Entrada.puml`
- `uml/UML_01_Modelo_Dominio.puml`
- `uml/UML_03_Clases_Catalog.puml`
- `uml/UML_04_Clases_Inventory.puml`
- `uml/UML_06_Clases_Audit_Reporting.puml`

## Fingerprint visual

**0 diferencias** en las directivas visuales/skinparam de los 59 diagramas comunes.
