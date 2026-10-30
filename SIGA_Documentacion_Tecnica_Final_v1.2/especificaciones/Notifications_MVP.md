# Notifications MVP

## 1. Alcance

El MVP ofrece notificaciones **in-app** personales. No incluye correo, SMS, push, WebSocket, SSE, difusión por rol ni motor genérico de reglas. La Web usa polling y nunca cae silenciosamente a datos Demo en modo remoto.

## 2. Seguridad y ownership

- La API requiere un JWT válido; no requiere un permiso IAM adicional.
- El propietario de una notificación es `recipientUserId`, persistido como `audit.notification.user_id`.
- El actor se obtiene exclusivamente del claim JWT `sub`, que debe ser UUID. El cliente no envía un usuario actuante.
- Listado, conteo y marcado como leído se restringen siempre a `user_id = sub`.
- Un identificador inexistente o perteneciente a otro usuario responde `404`, sin revelar su existencia.

## 3. Modelo

| Campo API | Persistencia/derivación | Regla MVP |
|---|---|---|
| `id` | `notification.id` | UUID de la notificación |
| `recipientUserId` | `notification.user_id` | Un único destinatario |
| `type` | `notification.type` | `MOVEMENT_CONFIRMED` |
| `title` | `notification.title` | `Movimiento confirmado` |
| `message` | `notification.message` | Texto generado por servidor con el `movementCode` recibido |
| `severity` | Derivada de `type` | `INFO`; no se persiste una columna redundante en este MVP |
| `referenceType` | `notification.reference_type` | `Movement` |
| `referenceId` | `notification.reference_id` | UUID del movimiento |
| `createdAt` | `notification.created_at` | Instante UTC de creación |
| `readAt` | `notification.read_at` | `null` mientras no haya sido leída |

`readAt` es la única fuente de verdad del estado leído/no leído. No se persisten en paralelo `status` ni `read`. Si la UI necesita un booleano, lo deriva como `readAt != null`.

## 4. Primer flujo vertical

El primer y único disparador del MVP es el contrato existente `MovementConfirmed v1`:

- productor: `inventory-service`;
- exchange topic durable: `siga.events`;
- routing key: `inventory.movement.confirmed.v1`;
- `eventType`: `MovementConfirmed`;
- `schemaVersion`: `1`;
- `aggregateType`: `Movement`;
- `aggregateId`: UUID del movimiento;
- sobre y payload: `api/movement-confirmed-v1.schema.json`.

No se bifurca ni amplía ese schema. El destinatario se toma de `payload.movement.registeredByUserId`, ya validado como UUID. La regla de negocio es: **quien registró el movimiento recibe la confirmación de que este terminó confirmado**. No se consulta IAM ni se difunde a roles, autorizador, confirmador o solicitante.

La notificación usa `referenceType=Movement`, `referenceId=aggregateId`, `type=MOVEMENT_CONFIRMED`, `severity=INFO`, título `Movimiento confirmado` y mensaje `El movimiento {movementCode} fue confirmado.` No transporta ni persiste JWT, OTP, credenciales o datos personales adicionales.

## 5. Entrega e idempotencia

- cola durable propia: `notifications.movement.confirmed.v1`;
- binding: exchange `siga.events`, routing key `inventory.movement.confirmed.v1`;
- identidad del consumidor: `notifications-movement-confirmed-v1`;
- entrega al menos una vez y ACK manual únicamente después del commit local;
- en una sola transacción local: reclamar `(eventId, consumer)` en `audit.processed_event` e insertar `audit.notification`;
- un conflicto de deduplicación confirma el mensaje sin insertar otra notificación;
- cualquier fallo revierte tanto la reclamación como la notificación;
- mensajes inválidos o fallos agotados se envían a `notifications.movement.confirmed.v1.dlq`;
- máximo 3 intentos de consumo con backoff exponencial configurable antes de DLQ.

No existe transacción distribuida. La cola de Notifications es independiente de la cola de Audit para evitar consumidores competidores sobre una misma cola.

## 6. API

### `GET /api/v1/notifications`

Lista exclusivamente las notificaciones del `sub` autenticado.

- `unreadOnly`: booleano, por defecto `false`;
- `page`: entero, por defecto `0`, mínimo `0`;
- `size`: entero, por defecto `20`, rango `1..100`;
- orden fijo: `createdAt DESC, id DESC`;
- respuesta: `content`, `page`, `size`, `totalElements`.

### `GET /api/v1/notifications/unread-count`

Devuelve `{ "unreadCount": n }` para el `sub` autenticado. El badge no descarga todas las páginas para contar.

### `POST /api/v1/notifications/{id}/read`

Comando idempotente sin body. Responde `200` con la notificación. La primera ejecución asigna `readAt`; las siguientes conservan exactamente el instante original y devuelven el mismo estado. La actualización incluye el predicado de ownership. Un ID inexistente o ajeno devuelve `404`.

Se adopta `POST`, y no `PATCH`, porque la URI representa el comando idempotente `read`, no una edición parcial enviada por el cliente; además coincide con las rutas de comando de SIGA.

## 7. Errores

- `400`: paginación o filtro inválido;
- `401`: JWT ausente o inválido;
- `404`: notificación inexistente o no perteneciente al actor;
- `409`: no aplica al marcado idempotente;
- `503`: no aplica a estas operaciones, que solo usan persistencia local.

Los errores usan `application/problem+json` y no revelan identificadores de otros usuarios.

## 8. Polling Web

- intervalo base: 30 segundos;
- solo con sesión autenticada;
- como máximo una solicitud de polling en vuelo;
- pausa mientras `document.hidden` y refresco inmediato al recuperar visibilidad;
- refresco de lista y conteo después de marcar como leída;
- estados explícitos de loading, empty y error;
- modo remoto usa `ApiNotificationRepository` mediante el `ApiClient` compartido; el repositorio Demo permanece únicamente en modo Demo.

## 9. Auditoría

`MARK_READ_AUDITED = NO`. Marcar una alerta personal como leída es estado de presentación de alto volumen y no una decisión de seguridad o negocio. La creación conserva trazabilidad mediante `eventId`, `processed_event`, `referenceId` y el evento fuente.

## 10. Consistencia y almacenamiento

Notifications es eventualmente consistente respecto de Inventory y transaccional dentro de `audit`. La tabla existente `audit.notification` es suficiente y no requiere migración para el MVP. El orden estable usa `created_at DESC, id DESC`; añadir `id` a los índices puede evaluarse posteriormente con evidencia de rendimiento, pero no es requisito de corrección.

No hay FK ni consulta al schema `iam`, `inventory` u otro schema externo.

## 11. Pruebas de aceptación futuras

- PostgreSQL Testcontainers: Flyway limpio, ownership, página/orden, filtro unread, conteo, marcado idempotente, duplicado concurrente y rollback de deduplicación.
- RabbitMQ Testcontainers: mensaje real conforme al schema, redelivery, duplicado, retry/DLQ y ACK posterior al commit.
- Seguridad/API: 401, aislamiento por `sub`, 404 anti-enumeración, paginación inválida, lista vacía y marcado repetido.
- Web: badge, lista/empty/loading/error, marcado, polling sin solapamiento/oculto y ausencia de fallback Demo en modo remoto.

## 12. Secuencia de implementación

1. **Slice A — Backend:** dominio, persistencia, consumidor, API y pruebas dentro de `audit-notification-service`.
2. **Slice B — Runtime:** aprovisionar cola/binding, activar el consumidor y validar un `MovementConfirmed v1` real de extremo a extremo.
3. **Slice C — Web Remote:** `ApiNotificationRepository`, badge/panel/lista, marcado y polling.
