# Modelo lógico canónico — SIGA

## 1. Propósito

Este modelo es la referencia lógica consolidada entre el Manual Técnico, DER, UML, SQL, OpenAPI y pruebas. **PostgreSQL sigue siendo la autoridad operacional** y cada microservicio escribe exclusivamente su schema. Las referencias a otro bounded context son UUID sin FK cross-schema; cuando una regla necesita datos de otro contexto dentro de una transacción crítica se usa una **proyección local sincronizada por eventos**, no una consulta síncrona dentro del commit.

## 2. Ownership y fronteras

| Schema | Servicio owner | Función | Tipo de consistencia |
|---|---|---|---|
| `iam` | identity-service | Usuarios, RBAC, refresh/MFA y eventos IAM | Transaccional local |
| `catalog` | catalog-service | Productos, categorías, proveedores, UoM y conversiones | Transaccional local |
| `inventory` | inventory-service | Stock, ubicaciones, lotes, activos, movimientos, autorizaciones, conteos, costo e idempotencia | **ACID crítico** |
| `evidence` | evidence-service | Metadata/hash y vínculo con Object Storage | Transaccional local |
| `audit` | audit-notification-service | Auditoría funcional y notificaciones | Eventualmente consistente |
| `analytics` | reporting-analytics-service | Read models, KPI, reportes y exportaciones | Eventualmente consistente |

## 3. Modelo por bounded context

### 3.1 IAM

`user_account` N:M `role` mediante `user_role`; `role` N:M `permission` mediante `role_permission`. `refresh_token` pertenece a un usuario y conserva JTI/familia para rotación y revocación. MFA y bloqueo se mantienen en `user_account` para el alcance MVP; no se crean tablas independientes `MfaSecret`/`LoginAttempt`. Los cambios que deban auditarse se publican mediante `iam.outbox_event`.

### 3.2 Catálogo

`supplier` mantiene el maestro básico de proveedores (identificación, razón social, contacto y estado), sin convertir SIGA en un ERP de compras. `category` 1:N `product`. `unit_measure` define las unidades maestras; cada `product` referencia una unidad de almacenamiento y una unidad base. Las equivalencias se normalizan en `unit_conversion`, permitiendo múltiples conversiones por producto sin limitar el dominio a un único `conversion_factor`. `catalog.outbox_event` transporta cambios a Inventory/Reporting.

### 3.3 Inventory Core

`supplier_ref`, `product_ref` y `product_unit_conversion_ref` son proyecciones locales de Catalog. No son un segundo maestro: contienen únicamente los datos requeridos por las reglas de inventario y su `source_version`.

`location` es recursiva. Su `code` global, case-sensitive, es inmutable; `active` implementa lifecycle sin borrado y `version` parte en cero y avanza una vez por mutación efectiva. `parent_id=NULL` representa raíz, no existe matriz rígida de tipos y la aplicación impide auto-parent/ciclos incluso bajo concurrencia. La desactivación no hace cascade y respeta stock positivo, descendientes activos y conteos abiertos del subárbol.

`lot` y `asset` pertenecen a `product_ref`, usan `version` optimista y no se eliminan. En Lot, producto/lote/colada son inmutables; las fechas son metadata corregible, `expires_at` determina la caducidad y `DEPLETED` se deriva de una transición de stock agregado positivo a cero. En Asset, producto/código/serie son inmutables y solo marca, modelo y snapshot técnico son metadata reemplazable. `EN_TRANSITO` queda reservado para un futuro flujo asíncrono y `FUERA_SERVICIO` es terminal. No existe custodia/responsable de Asset en el MVP.

`stock_balance` es la única fuente de verdad para cantidad, costo promedio y **ubicación actual**; `lot` no almacena cantidad/ubicación y `asset` no mantiene `current_location_id`. Los listados administrativos pueden derivar totales y ubicación, pero no se convierten en otra autoridad.

`movement` puede referenciar un `supplier_ref` para entradas asociadas a abastecimiento externo y conserva snapshot de razón social/RUC para trazabilidad histórica. `movement` tiene N `movement_detail` y puede tener N registros `movement_authorization` según el flujo sensible. Las líneas conservan snapshot de cantidad ingresada, unidad, factor de conversión, cantidad aplicada al stock y, cuando corresponde, moneda/TC/costo histórico. `physical_count` cubre exactamente una ubicación; al crearse copia sus dimensiones de `stock_balance` en `physical_count_line`, conserva cantidades observadas, actores y versión optimista, y deriva `difference_quantity`. El conteo nunca muta stock ni crea ajustes automáticamente; cualquier regularización posterior es una acción explícita mediante movimientos de ajuste trazables.

`idempotency_record` evita doble efecto de comandos críticos; `processed_event` evita aplicar dos veces un evento consumido; `outbox_event` evita perder eventos producidos.

En D4, `movement_detail.base_unit_cost_pen` conserva el costo base de una entrada o ajuste positivo valorizado y `applied_avg_cost_pen` el promedio aplicado a salida, transferencia o ajuste. `stock_balance.avg_cost_pen` es el promedio de su dimensión física. La confirmación confirma stock, snapshots, movimiento e `inventory.outbox_event` en una sola transacción; `MovementConfirmed v1` transporta solo saldos afectados hacia Audit y Reporting.

### 3.4 Evidencia

En el MVP, `evidence_metadata` usa `owner_type=MOVEMENT + owner_id` como referencia externa al movimiento de Inventory; los ajustes usan el UUID de su movimiento `ADJUST_POSITIVE` o `ADJUST_NEGATIVE`. `ASSET`, `ADJUSTMENT` y `REPORT` quedan reservados hasta disponer de una interfaz canónica de autorización por owner. El binario vive en MinIO/GCS; PostgreSQL conserva metadata, SHA-256, MIME, tamaño, estado y actor. `upload_idempotency` reserva una identidad estable por `Idempotency-Key` y permite reproducir el resultado sin duplicar objeto, metadata ni evento. `evidence.outbox_event` publica `EvidenceUploaded` y eventos relacionados.

### 3.5 Audit / Notification

`audit_event` es append-only. `notification` pertenece a un único `user_id`, derivado de `JWT sub`, y gestiona alertas in-app; `read_at` nullable es la única fuente de verdad de lectura. El primer flujo consume `MovementConfirmed v1` y notifica a `registeredByUserId`, sin FK ni consultas al schema IAM. `processed_event` garantiza consumidor idempotente frente a redelivery de RabbitMQ mediante una identidad de consumidor distinta para Audit y Notifications.

### 3.6 Reporting / Analytics

`product_projection`, `inventory_projection` y `movement_projection` son modelos de lectura; `movement_projection` conserva el snapshot de proveedor cuando exista para filtros y reportes; `kpi_snapshot` conserva indicadores; `report_job` modela generación/exportación; `processed_event` evita reprocesamiento y `export_checkpoint` soporta extracción incremental. Ninguna tabla `analytics.*` puede modificar o sustituir `inventory.stock_balance`.

## 4. Referencias y relaciones críticas

- **FK locales permitidas:** dentro del mismo schema/ownership.
- **FK cross-schema prohibidas:** actores IAM, owners de evidencia y referencias analíticas son UUID externos.
- `lot.product_id`, `asset.product_id`, `stock_balance.product_id`, `movement_detail.product_id` y `physical_count_line.product_id` referencian localmente `inventory.product_ref`.
- Las FK compuestas `(lot_id, product_id)` y `(asset_id, product_id)` impiden vincular trazabilidad de un producto distinto.
- Un activo serializado puede tener cantidad 0/1 y una sola existencia positiva, evitando doble ubicación.
- La configuración de lote/colada/serie/vencimiento se aplica desde `inventory.product_ref`.
- `movement.supplier_id` referencia localmente `inventory.supplier_ref`; no existe FK de Inventory hacia `catalog.supplier`.

## 5. Máquina de estados canónica de movimiento

`DRAFT -> PENDING_AUTHORIZATION -> AUTHORIZED -> CONFIRMED` cuando el movimiento es sensible o el actor que envía carece de `MOVEMENT_AUTHORIZE`; `DRAFT -> CONFIRMED` solo está permitido para un actor con `MOVEMENT_AUTHORIZE` y un movimiento no sensible. `PENDING_AUTHORIZATION -> REJECTED`. En authorize/reject, el `sub` autenticado debe ser distinto de `registered_by_user_id` (maker-checker). Un borrador o autorizado puede cancelarse según política antes de confirmar. `CONFIRMED` es inmutable; una corrección se expresa con un movimiento compensatorio.

Tipos: `ENTRY`, `EXIT`, `TRANSFER`, `ADJUST_POSITIVE`, `ADJUST_NEGATIVE`. Las cantidades de detalle son siempre positivas; la dirección del efecto la determina el tipo.

## 6. Invariantes de implementación

1. Confirmación de movimiento, actualización de stock/costo y `inventory.outbox_event` ocurren en una sola transacción local.
2. Las filas de stock afectadas se cargan con `SELECT ... FOR UPDATE`, se revalidan y recién entonces se actualizan.
3. `CHECK(quantity >= 0)` es segunda barrera; la UI nunca es autoridad.
4. ENTRY exige destino; cuando el origen sea abastecimiento externo exige además proveedor activo en `supplier_ref`; EXIT origen; TRANSFER origen/destino distintos; los ajustes usan el tipo positivo/negativo.
5. Los estados confirmados y auditoría no se borran ni editan.
6. Los consumidores registran `event_id` en su propio schema (`inventory`, `audit`, `analytics`).
7. Redis, RabbitMQ, reporting y object storage nunca sustituyen la fuente de verdad relacional que corresponda.
