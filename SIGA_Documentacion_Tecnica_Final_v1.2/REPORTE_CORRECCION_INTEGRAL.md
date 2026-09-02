# Reporte de corrección integral — SIGA v1.1

## 1. Alcance autorizado

Se consolidó el paquete técnico para que Manual Técnico, arquitectura por microservicios, DER, UML, SQL, diccionario, OpenAPI, secuencias, estados, CUS, trazabilidad y testing expresen el mismo diseño implementable. El paquete original no se sobrescribe.

## 2. Decisiones preservadas

Se mantienen sin cambio: seis microservicios; ownership por schema; PostgreSQL como autoridad; ausencia de FK/escrituras cross-schema; Inventory+Movement en un único núcleo ACID; READ COMMITTED + `SELECT ... FOR UPDATE`; idempotencia; RabbitMQ selectivo; Transactional Outbox; Redis no autoritativo; MinIO/GCS; JWT RS256 + refresh + TOTP/MFA + RBAC; JSONB restringido; React/Expo; sin movimientos offline; Docker Compose baseline/GKE objetivo; GCP y multirepo.

## 3. Modelo físico consolidado

| Schema | Owner | Tablas |
|---|---|---:|
| `iam` | identity-service | 7 |
| `catalog` | catalog-service | 5 |
| `inventory` | inventory-service | 14 |
| `evidence` | evidence-service | 2 |
| `audit` | audit-notification-service | 3 |
| `analytics` | reporting-analytics-service | 7 |
| **Total** |  | **38** |

### IAM
Se documentan y modelan `user_account`, `role`, `permission`, `user_role`, `role_permission`, `refresh_token` y Outbox. MFA/bloqueo permanecen en `user_account`; se elimina la contradicción UML que trataba `MfaSecret` y `LoginAttempt` como agregados persistentes separados.

### Catalog
Se adopta `unit_conversion` como modelo normalizado N por producto. `product` conserva unidad de almacenamiento/base y flags de trazabilidad, pero deja de depender de un único `conversion_factor`. Se agrega Outbox local.

### Inventory
Se amplía `product_ref` con stock mínimo, flags completos y unidades; se agrega `product_unit_conversion_ref` y `processed_event` para consumo idempotente de Catalog. Lote, activo, stock, movimiento, autorización, conteo, idempotencia y Outbox quedan completamente representados.

`stock_balance` es la única autoridad de ubicación del activo; `asset.current_location_id` se elimina. La BD impide cantidad >1 para activos y más de una existencia positiva del mismo activo. FK compuestas protegen que lote/activo pertenezcan al mismo producto.

`movement` separa registrador, solicitante y centro de costo; autorización e idempotencia dejan de duplicarse en la cabecera. `movement_detail` conserva snapshot de cantidad ingresada, unidad, factor, cantidad de stock, moneda, TC, fuente y costos.

### Evidence
Se sustituye el acoplamiento exclusivo a `movement_id` por `owner_type + owner_id`, soportando MOVEMENT, ASSET, ADJUSTMENT y REPORT. Se agrega Outbox local.

### Audit/Notification
Se consolidan `audit_event`, `notification` y `processed_event`, con índices por actor, agregado, correlationId, fecha y no-leídas.

### Reporting/Analytics
Se implementan físicamente los read models que el Manual ya declaraba: `product_projection`, `inventory_projection`, `movement_projection`, `kpi_snapshot`, `report_job`, `processed_event` y `export_checkpoint`. Continúan siendo eventualmente consistentes y nunca autoridad de stock.

## 4. Integración y eventos

- Outbox por productor: IAM, Catalog, Inventory y Evidence.
- `processed_event` por consumidor/ownership: Inventory, Audit y Analytics.
- No existe Outbox ni tabla de consumo compartida.
- Catalog actualiza `product_ref` y `product_unit_conversion_ref` mediante eventos.
- Inventory confirma sin llamada REST a Catalog dentro del commit crítico.

## 5. Estados y reglas

Estado interno canónico de movimiento:
`DRAFT`, `PENDING_AUTHORIZATION`, `AUTHORIZED`, `CONFIRMED`, `REJECTED`, `CANCELLED`.

`CANCELLED` solo aplica antes de confirmar. `CONFIRMED` es inmutable; toda corrección usa un movimiento compensatorio.

Tipos:
`ENTRY`, `EXIT`, `TRANSFER`, `ADJUST_POSITIVE`, `ADJUST_NEGATIVE`.

## 6. Diagramas

Los DER pasan de tres vistas incompletas a nueve fuentes:
- DER-01 conceptual global.
- DER-02 lógico global.
- DER-03 físico por schemas.
- DER-04 IAM.
- DER-05 Catalog.
- DER-06 Inventory.
- DER-07 Evidence.
- DER-08 Audit/Notification.
- DER-09 Reporting/Analytics.

También se alinearon UML-01..06, STATE-01, SEQ-03/10/11/12/13/14 y C4-04.

## 7. Contratos

Los seis OpenAPI se elevan a versión 1.1:
- Identity: login/MFA/refresh, usuarios, roles y asignaciones.
- Catalog: productos, flags y conversiones múltiples.
- Inventory: inventario, ubicaciones, lotes/activos, estados, snapshots, autorización, cancelación y conteos.
- Evidence: `ownerType/ownerId`.
- Audit: filtros de auditoría y notificaciones.
- Reporting: dashboard, report jobs y export incremental.

## 8. Trazabilidad y pruebas

Se agrega ADR-018 para gobernar el modelo canónico y se amplía ADR-007 para Outbox por productor. Las matrices incluyen RF↔entidad e invariante↔artefacto↔prueba.

La matriz de testing incorpora pruebas de doble ubicación de activo, trazabilidad producto/lote/activo, snapshot de conversiones, operación sin REST a Catalog, redelivery de eventos, Outbox por productor, Evidence genérico y Reporting read-only.

## 9. Archivos de datos que deben evolucionar juntos

1. `database/logical_model.md`
2. `database/physical_model.sql`
3. `database/dictionary.md`
4. `diagramas/datos/DER_01..09`
5. UML afectados
6. OpenAPI afectados
7. CUS/trazabilidad/testing
8. Manual Técnico
9. Flyway de cada repo implementado

La regla de gobierno es que un cambio de entidad, estado, evento, ownership, contrato o invariante no se considera terminado si deja estos artefactos desalineados.

## 10. Cambios deliberadamente no realizados

No se creó un séptimo microservicio, no se separó Movement de Inventory, no se añadieron FK cross-schema, no se adoptó Kafka, Event Sourcing, Saga/2PC, MongoDB, ERP/CMMS, transacciones offline ni un Data Warehouse empresarial. Son ampliaciones fuera del alcance y/o contrarias a las decisiones aprobadas.

## 11. Resultado de validación final certificada

La validación final se ejecutó después de regenerar y revisar visualmente el Manual Técnico DOCX. El documento final renderiza correctamente en **65 páginas**, sin páginas rotas, contenido recortado, tablas inválidamente partidas, solapamientos ni elementos gráficos incrustados ilegibles. CUS-23 y CUS-26 reflejan las correcciones canónicas aprobadas.

Comprobaciones finales:

- 38 `CREATE TABLE` detectados y 38 tablas documentadas en el diccionario.
- Distribución por schema: IAM 7 / Catalog 5 / Inventory 14 / Evidence 2 / Audit 3 / Analytics 7.
- 0 FK cross-schema.
- Diccionario con paridad de columnas 1:1 respecto al SQL canónico.
- DER físicos DER-04..09 con paridad de tablas y columnas 1:1 respecto al SQL canónico.
- 6 OpenAPI válidos, parseables y con `info.version` 1.1.
- 9 DER de datos presentes.
- 57 fuentes PlantUML con marcadores estructurales `@startuml` / `@enduml` válidos.
- 6 microservicios de negocio presentes en Docker Compose y en el Manual; no existe `movement-service`.
- Frontera ACID Inventory + Movement preservada y documentada en Manual/ADR-003/SQL/testing.
- Idempotencia, Outbox por productor, `processed_event` por consumidor/ownership, Audit y read models de Analytics coherentes entre SQL, UML, DER, ADR, Manual y pruebas.
- Seeds no referencian tablas inexistentes.
- No se despliegan ni configuran Kafka, Event Sourcing, Saga, ERP/CMMS ni nuevos microservicios.

### Correcciones adicionales detectadas durante el gate final

La comparación a nivel de columnas encontró omisiones documentales que no alteraban el SQL canónico pero podían generar ambigüedad futura. Se corrigieron antes de certificar la entrega:

- `inventory.movement`: se incorporaron `requested_by_user_id` y `cost_center_code` en diccionario y DER físico.
- `inventory.movement_authorization`: se incorporó `decision` en diccionario/DER y `requestedAt` en UML.
- `inventory.physical_count`: se incorporó `notes` en diccionario/DER/UML.
- `evidence.evidence_metadata`: se incorporaron `object_key`, `sha256` y `status` en diccionario/DER físico.
- `audit.audit_event`: se incorporó `aggregate_type` en diccionario/DER físico.
- `audit.notification`: se incorporó `type` en diccionario/DER físico.
- `analytics.report_job`: se incorporaron `format` y `sha256` en diccionario/DER y `sha256` en UML.
- `database/logical_model.md`: se hicieron explícitos `unit_measure` y `movement_authorization`.

Tras estas correcciones se volvió a ejecutar la validación afectada y el resultado fue **0 errores**.
