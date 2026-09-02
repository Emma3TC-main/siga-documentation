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
- IAM: eventos de usuario/rol que deban auditarse.
- Catalog: `ProductCreated/Updated` y cambios de conversiones/proyección.
- Inventory: `MovementConfirmed`, `StockBelowMinimum`, `InventoryAdjusted`, etc.
- Evidence: `EvidenceUploaded`.

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

## Revisión
Reabrir solo si se adopta un broker/infraestructura con garantía transaccional equivalente y existe evidencia de que reduce complejidad sin alterar ownership.
