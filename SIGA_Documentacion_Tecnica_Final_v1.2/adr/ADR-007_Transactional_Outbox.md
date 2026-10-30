# ADR-007 — Transactional Outbox por servicio productor

**Estado:** Aceptado — actualizado en la consolidación 1.1

## Contexto
SIGA usa RabbitMQ para efectos secundarios y proyecciones, pero un `COMMIT` de PostgreSQL y un `publish` al broker no forman una transacción distribuida. Si se confirma el negocio y falla la publicación, podría perderse un evento.

## Decisión
Todo servicio que produzca eventos relevantes conserva un **Outbox local dentro de su propio schema** y lo inserta en la misma transacción que el cambio de dominio:

- `iam.outbox_event`
- `catalog.outbox_event`
- `inventory.outbox_event`
- `evidence.outbox_event`

Un publisher independiente reclama eventos `PENDING`, publica mensajes persistentes con publisher-confirm y marca `PUBLISHED`. Los fallos incrementan `attempts` y programan retry/backoff.

**No existe un Outbox global/compartido**, porque violaría ownership de datos.

## Aplicación
- IAM: los mensajes históricos v1 (`UserCreated`, `UserUpdated`, `UserDisabled`, `RoleChanged`) conservan envelope/payload y routing originales. El contrato futuro v2 separa `UserCreated`, `UserUpdated`, `UserDisabled`, `UserRolesChanged`, `RoleCreated` y `RolePermissionsChanged`, con aggregates User/Role, actor derivado de JWT `sub` y snapshots seguros before/after definidos en `api/iam-*-v2.schema.json`. No se publica `RoleUpdated` porque no existe esa operación canónica.
- Catalog: `ProductCreated/Updated` y cambios de conversiones/proyección. Para `ProductCreated v1`, el append de `catalog.outbox_event` ocurre con producto y conversiones en la misma transacción. Para `ProductUpdated v1`, el append ocurre únicamente ante un cambio efectivo y se confirma con el incremento condicional de versión y el reemplazo completo de conversiones; un no-op no escribe Outbox. El publisher posterior entrega al menos una vez e Inventory/Reporting deduplican por `eventId` en su propia `processed_event`.
- Inventory: `MovementConfirmed`, `StockBelowMinimum`, `InventoryAdjusted`, `LocationChanged v1`, `LotChanged v1` y `AssetChanged v1`. Para Location/Lot/Asset, solo una mutación efectiva confirma estado + Outbox en la misma transacción; un no-op, conflicto o rechazo no crea evento. Los routings administrativos son `inventory.location.changed.v1`, `inventory.lot.changed.v1` e `inventory.asset.changed.v1`. El publisher envía mensajes persistentes a `siga.events`, conserva el `eventId` entre reintentos y marca `PUBLISHED` únicamente tras publisher-confirm. Audit deduplica por `eventId`; estos cambios no producen notificaciones.
- Evidence: `EvidenceUploaded v1`, exchange `siga.events`, routing key `evidence.uploaded.v1`; el sobre se valida contra `api/evidence-uploaded-v1.schema.json`. Metadata y Outbox se confirman en la misma transacción y el `eventId` estable es el UUID de `evidence.outbox_event`.

## Alternativas descartadas
1. Publicar directamente después del commit: ventana de evento perdido.
2. Transacción distribuida/2PC con RabbitMQ: complejidad desproporcionada.
3. Outbox compartido: acoplamiento y escritura cross-schema.

## Consecuencias
+ Garantía de publicación eventual sin comprometer la transacción local.
+ El productor sigue disponible aunque RabbitMQ esté temporalmente caído.
+ Se mantiene ownership por bounded context.
- Requiere worker, retry, métricas, cleanup y pruebas.

## Pruebas obligatorias
Broker disponible/no disponible, retry, publisher confirm, evento duplicado y recuperación posterior. Los consumidores deben ser idempotentes mediante `processed_event` en su propio schema.

Para IAM, el futuro consumidor `audit-identity-events-consumer` reclama `eventId` y persiste Audit + `audit.processed_event` en una transacción; ACK solo después del commit y duplicado sin segundo efecto. La cola existente `siga.identity.audit` se conserva con binding `iam.#`. Sin recrearla, una policy `^siga\.identity\.audit$` añadirá DLX `siga.identity.audit.dlx`, routing `siga.identity.audit.dead` y DLQ `siga.identity.audit.dlq` antes de habilitar el consumidor. Mensaje inválido/no soportado va a DLQ; fallo transitorio usa retry acotado y luego DLQ. Los seis `RoleChanged v1` históricos se mapean a `IDENTITY_ROLE_CHANGED_LEGACY`, sin reconstrucción, y ningún evento IAM crea Notifications. Esta aplicación permanece pendiente de los slices de productor/consumidor/runtime.

## Revisión
Reabrir solo si se adopta un broker/infraestructura con garantía transaccional equivalente y existe evidencia de que reduce complejidad sin alterar ownership.
