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

`location` es recursiva. `lot` y `asset` pertenecen a `product_ref`. `stock_balance` es la única fuente de verdad para cantidad, costo promedio y **ubicación actual**; `asset` no mantiene `current_location_id`.

`movement` puede referenciar un `supplier_ref` para entradas asociadas a abastecimiento externo y conserva snapshot de razón social/RUC para trazabilidad histórica. `movement` tiene N `movement_detail` y puede tener N registros `movement_authorization` según el flujo sensible. Las líneas conservan snapshot de cantidad ingresada, unidad, factor de conversión, cantidad aplicada al stock y, cuando corresponde, moneda/TC/costo histórico. `physical_count` y `physical_count_line` registran diferencias sin mutar stock por sí mismos; cualquier regularización posterior se realiza mediante movimiento de ajuste trazable.

`idempotency_record` evita doble efecto de comandos críticos; `processed_event` evita aplicar dos veces un evento consumido; `outbox_event` evita perder eventos producidos.

### 3.4 Evidencia

`evidence_metadata` usa `owner_type + owner_id` como referencia externa genérica para `MOVEMENT`, `ASSET`, `ADJUSTMENT` o `REPORT`. El binario vive en MinIO/GCS; PostgreSQL conserva metadata, SHA-256, MIME, tamaño, estado y actor. `evidence.outbox_event` publica `EvidenceUploaded` y eventos relacionados.

### 3.5 Audit / Notification

`audit_event` es append-only. `notification` gestiona alertas in-app. `processed_event` garantiza consumidor idempotente frente a redelivery de RabbitMQ.

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

`DRAFT -> PENDING_AUTHORIZATION -> AUTHORIZED -> CONFIRMED`, o `DRAFT -> CONFIRMED` cuando no es sensible. `PENDING_AUTHORIZATION -> REJECTED`. Un borrador o autorizado puede cancelarse según política antes de confirmar. `CONFIRMED` es inmutable; una corrección se expresa con un movimiento compensatorio.

Tipos: `ENTRY`, `EXIT`, `TRANSFER`, `ADJUST_POSITIVE`, `ADJUST_NEGATIVE`. Las cantidades de detalle son siempre positivas; la dirección del efecto la determina el tipo.

## 6. Invariantes de implementación

1. Confirmación de movimiento, actualización de stock/costo y `inventory.outbox_event` ocurren en una sola transacción local.
2. Las filas de stock afectadas se cargan con `SELECT ... FOR UPDATE`, se revalidan y recién entonces se actualizan.
3. `CHECK(quantity >= 0)` es segunda barrera; la UI nunca es autoridad.
4. ENTRY exige destino; cuando el origen sea abastecimiento externo exige además proveedor activo en `supplier_ref`; EXIT origen; TRANSFER origen/destino distintos; los ajustes usan el tipo positivo/negativo.
5. Los estados confirmados y auditoría no se borran ni editan.
6. Los consumidores registran `event_id` en su propio schema (`inventory`, `audit`, `analytics`).
7. Redis, RabbitMQ, reporting y object storage nunca sustituyen la fuente de verdad relacional que corresponda.
