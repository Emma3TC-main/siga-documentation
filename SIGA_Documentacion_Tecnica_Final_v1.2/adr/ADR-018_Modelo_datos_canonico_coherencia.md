# ADR-018 — Modelo de datos canónico y coherencia entre artefactos

**Estado:** Aceptado

## Contexto
La línea técnica original definía seis bounded contexts, pero los DER físicos mostraban principalmente Inventory Core y existían diferencias entre UML, SQL, diccionario y OpenAPI: IAM no estaba desarrollado en DER, conversiones tenían dos modelos, Evidence estaba acoplado a Movement y Reporting declaraba read models no implementados físicamente.

Estas diferencias podían provocar implementaciones incompatibles entre repositorios y decisiones contradictorias durante los sprints.

## Decisión
Se adopta como cadena canónica:

`Manual/ADR/reglas aprobadas -> logical_model.md -> physical_model.sql -> dictionary.md -> DER/UML/OpenAPI/tests`.

El modelo mantiene seis schemas y **40 tablas**:
- IAM: 7
- Catalog: 6
- Inventory: 15
- Evidence: 2
- Audit: 3
- Analytics: 7

Reglas asociadas:
1. FK solo dentro del mismo ownership; UUID externos sin FK cross-schema.
2. `catalog.unit_conversion` normaliza conversiones múltiples.
3. Inventory usa `product_ref` y `product_unit_conversion_ref` como proyecciones locales, con `processed_event`.
4. `stock_balance` es la única autoridad de ubicación actual del activo.
5. Autorización e idempotencia no se duplican en `movement`.
6. Evidence usa `owner_type + owner_id`.
7. Reporting implementa read models y su propio `processed_event`.
8. Outbox es local a cada servicio productor.

## Alternativas descartadas
- DER resumido como única especificación física: insuficiente para implementación.
- Un modelo relacional monolítico con FK entre schemas: contradice bounded contexts.
- Crear nuevos microservicios para centro de costo/conversiones: sobreingeniería.
- Mantener datos duplicados de ubicación/autorización/idempotencia: riesgo de divergencia.

## Consecuencias
+ Una única interpretación implementable del dominio.
+ Mejor trazabilidad RF/CUS -> entidad -> API -> prueba.
+ Menos riesgo de divergencia entre repositorios.
+ DER de sustentación siguen legibles mediante vistas globales y físicas por schema.
- Mayor número de artefactos de datos que deben mantenerse coordinados.

## Gobierno
Todo cambio que afecte entidad, ownership, FK, estado, evento, contrato o invariante debe modificar en el mismo PR los artefactos impactados. `physical_model.sql` y `dictionary.md` nunca deben quedar con conjuntos de tablas distintos.


## Adenda v1.2 — Proveedores

Se añaden `catalog.supplier` e `inventory.supplier_ref`. La segunda es una proyección local sincronizada por eventos para que la confirmación de una entrada no introduzca una dependencia REST síncrona a Catalog. `inventory.movement` conserva `supplier_id` y snapshots de razón social/identificador tributario cuando corresponda. No se crea un nuevo bounded service ni FK cross-schema.
