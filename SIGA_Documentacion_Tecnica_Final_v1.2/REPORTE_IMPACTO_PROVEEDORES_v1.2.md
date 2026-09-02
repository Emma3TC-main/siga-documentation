# SIGA — Informe de impacto mínimo para incorporar Proveedores (v1.2)

## Decisión de diseño

La solución actual se conserva. No se crea un séptimo microservicio ni un módulo de compras completo. **Proveedor** se incorpora como dato maestro de `catalog-service` y se usa en CUN-01/CUS-07 para identificar el origen de recepciones externas. Inventory mantiene una proyección `supplier_ref` sincronizada por eventos, siguiendo el patrón ya usado por `product_ref`, por lo que la confirmación ACID sigue sin depender de REST a Catalog.

## Qué cambia en datos

- Nueva tabla `catalog.supplier`.
- Nueva tabla `inventory.supplier_ref` (proyección local).
- `inventory.movement`: `supplier_id`, `supplier_name_snapshot`, `supplier_tax_id_snapshot`.
- `analytics.movement_projection`: mismos campos de proveedor para reporting.
- Total: **40 tablas** = IAM 7 / Catalog 6 / Inventory 15 / Evidence 2 / Audit 3 / Analytics 7.
- Continúa: **0 FK cross-schema**. `movement.supplier_id` referencia localmente `inventory.supplier_ref`.

## Regla funcional

- En una **recepción de abastecimiento externo**, se selecciona un proveedor activo y se conserva su snapshot al confirmar.
- En un ingreso de origen interno que la política no considere abastecimiento externo, el proveedor puede quedar nulo.
- Desactivar un proveedor no elimina ni invalida movimientos históricos.
- El MVP no incluye OC, cotizaciones, CxP, homologación avanzada ni portal para proveedores.

## Diagramas que sí cambian

1. `BPMN_01_Entrada.puml`: agrega al Proveedor externo como participante de negocio y la selección/validación condicional.
2. `SEQ_04_Registrar_Entrada.puml`: valida `supplier_ref` local y persiste snapshot.
3. `DER_01_Conceptual.puml`: PROVEEDOR/PROVEEDOR_REF.
4. `DER_02_Logico.puml`: entidades lógicas y relación con movimiento.
5. `DER_03_Fisico.puml`: conteos 6 Catalog / 15 Inventory / 40 total.
6. `DER_05_Fisico_Catalog.puml`: `catalog.supplier`.
7. `DER_06_Fisico_Inventory.puml`: `inventory.supplier_ref` + campos en `movement`.
8. `DER_09_Fisico_Reporting_Analytics.puml`: proveedor en `movement_projection`.
9. `UML_01_Modelo_Dominio.puml`: Supplier/SupplierReference.
10. `UML_03_Clases_Catalog.puml`: Supplier.
11. `UML_04_Clases_Inventory.puml`: SupplierReference y snapshots.
12. `UML_06_Clases_Audit_Reporting.puml`: snapshot de proveedor en MovementProjection.
13. `C4_04_Componente_Inventory.puml`: el consumidor de proyecciones de Catalog incorpora Supplier events.
14. Nuevos `UML_10_Casos_Uso_Negocio_Proveedores.puml` y `UML_11_Casos_Uso_Sistema_Proveedores.puml` para insertar puntualmente en capítulos 8 y 9. UML-10 **no crea un octavo CUN**: solo incorpora al Proveedor externo como actor de CUN-01. UML-11 agrega CUS-31 y mantiene separada la validación de proveedor activo dentro de CUS-07.

## Diagramas que no deben cambiar

C4-01 Contexto, C4-02/C4-03 Contenedores, C4-05 Identity, IAM, Evidence, DevOps, diagramas de salida, transferencia, ajuste y estados. El Proveedor externo no es usuario del sistema ni un sistema tecnológico integrado; por eso no debe confundirse con el “proveedor de tipo de cambio” existente en C4/CUS-29.

## Archivos técnicos impactados

- `database/physical_model.sql`, `seed_demo.sql`, `dictionary.md`, `logical_model.md`
- `api/catalog-openapi.yaml`, `api/inventory-openapi.yaml`
- `trazabilidad/requirements.md`, `traceability-matrices.md`, `testing-matrix.md`
- `especificaciones/CUN_Detallados.md`, `CUS_Detallados.md`
- diagramas listados arriba
- `Manual_Tecnico_SIGA_Final.md`, `Guia_Diagramas_SIGA.md`, `README.md`, `ADR-018_Modelo_datos_canonico_coherencia.md`

## Documentos DOCX externos: cambios manuales, no regeneración

Se deja el DOCX original intacto para no alterar maquetación aprobada. Aplicar solo estas ediciones:

### Informe Curso Integrador II

- **2.4 Alcance:** agregar “gestión básica de proveedores y asociación del proveedor a recepciones externas”.
- **2.5 Requerimientos:** cambiar línea base de 34 a **35 RF** y agregar RF-35.
- **4.2 Objetivos específicos:** en gestión del catálogo, agregar proveedores.
- **5 Requerimientos:** agregar `RF-35 Proveedores — Gestionar proveedores básicos y asociarlos a entradas de abastecimiento externo preservando trazabilidad histórica.`
- **6.1 Arquitectura:** Catalog Service pasa a “Categorías, productos, proveedores, unidades, conversiones y atributos”. No crear servicio nuevo.
- **6.2 CUN-01:** agregar Proveedor como actor de negocio/entrada y selección cuando la recepción sea externa.
- **6.3 Dentro del alcance:** agregar maestro básico de proveedores y vínculo proveedor-entrada.
- **6.4 Fuera del alcance:** mantener fuera “ERP/compras completo: OC, cotizaciones, cuentas por pagar, homologación avanzada, portal de proveedor”; ya no decir que proveedores en general están fuera.
- **8 / 8.1:** CUN-01 actor `Proveedor externo + Encargado/Recepción`; agregar UML-10.
- **9 / 9.1:** línea base pasa de 30 a **31 CUS**; agregar `CUS-31 Gestionar proveedores`; agregar UML-11. No renumerar CUS-01..30.
- **10–12:** agregar RF-35 / US-35 / CUS-31 a matrices.
- **17–18:** actualizar DER y total físico a 40 tablas.

### Manual Administrativo

- **2 Actores:** agregar `Proveedor externo` como actor de negocio que entrega recurso/documento, aclarando que no inicia sesión en SIGA.
- **4 Proceso general:** agregar proveedores a datos maestros y al paso de recepción.
- **10 Entrada de productos:** después de seleccionar producto, seleccionar proveedor cuando la entrada sea de abastecimiento externo; validar proveedor activo; conservar snapshot.
- **14.2 Información obligatoria:** agregar proveedor (ID, razón social y RUC/identificador snapshot) cuando corresponda.
- **18.3 Integraciones futuras:** reemplazar “ERP para compras/proveedores” por “ERP o gestión de compras completa (OC, cotizaciones, CxP, homologación/portal de proveedor)”. Así no contradice el maestro básico dentro de SIGA.
- **21 Sprints:** maestro de proveedores en Sprint 2 y asociación con entradas en Sprint 3.
- **23 Controles:** agregar control `Proveedor — activo/identificado — requerido para recepción externa según política`.

## Motivo del enfoque

Este diseño satisface la observación docente sin tocar las reglas que ya estaban correctas: stock, lotes, activos, multiubicación, costo promedio, autorización, evidencia, auditoría, Outbox, seis servicios y ACID de Inventory.
