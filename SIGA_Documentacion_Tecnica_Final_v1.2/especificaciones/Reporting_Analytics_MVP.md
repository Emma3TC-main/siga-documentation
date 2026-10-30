# Reporting / Analytics MVP

## 1. Alcance y ownership

`reporting-analytics-service` es dueño exclusivo del esquema `analytics`. Sus modelos son eventualmente consistentes y nunca son autoridad para stock, movimientos ni maestros. No se permiten consultas, vistas, claves foráneas ni migraciones contra `catalog.*`, `inventory.*`, `iam.*`, `audit.*` o `evidence.*`.

El MVP mantiene únicamente:

- `analytics.product_projection`;
- `analytics.inventory_projection`;
- `analytics.movement_projection`;
- `analytics.processed_event`.

`kpi_snapshot`, `report_job` y `export_checkpoint` quedan diferidos hasta los slices de snapshots históricos, generación de archivos e integración BI. Los KPI del MVP se calculan sobre las proyecciones propias.

## 2. Entradas asíncronas

| Evento | Productor | Exchange | Routing key | Uso |
|---|---|---|---|---|
| `MovementConfirmed v1` | Inventory | `siga.events` | `inventory.movement.confirmed.v1` | Proyectar el movimiento confirmado y reemplazar solamente los saldos afectados incluidos en el payload. |
| `ProductUpdated v1` | Catalog | `siga.events` | `catalog.product.updated.v1` | Upsert condicional del snapshot de producto cuando `product.version` sea mayor que `source_version`. |

Ambos usan el sobre canónico: `eventId`, `eventType`, `schemaVersion`, `occurredAt`, `aggregateType`, `aggregateId`, `correlationId`, `producer` y `payload`. No se define un schema duplicado.

`MovementConfirmed v1` basta para movimientos confirmados, costos, actores UUID, centro de costo, proveedor snapshot, ajustes y saldos afectados. No basta para reconstruir saldos que existían antes de activar Reporting, ni para dimensiones completas de productos.

`ProductCreated v1` es insuficiente para `product_projection`: no contiene nombre ni categoría. Se conserva intacto y no se consume en el MVP. El alta nunca modificada se incorpora mediante la reconciliación definida abajo; no se requiere un evento nuevo para este slice.

## 3. Entrega, deduplicación y orden

- La entrega es al menos una vez.
- La inserción de `(event_id, consumer)` y todos los cambios de proyección del mensaje se confirman en una sola transacción local.
- Si la clave ya existe, el mensaje es duplicado y no produce ningún cambio adicional.
- `ProductUpdated v1` aplica solo cuando `source_version` aumenta; una versión igual o anterior no sobrescribe la proyección.
- La cola de Reporting opera con consumidor único activo y `prefetch=1`. Esto preserva el orden de los snapshots absolutos de saldo de `MovementConfirmed v1`; un mensaje fallido no se omite para procesar mensajes posteriores.
- Un replay completo solo se ejecuta sobre proyecciones vacías creadas para ese rebuild. No se reproducen eventos históricos sobre una `inventory_projection` vigente.
- La caída de Reporting no bloquea al productor. La cola durable conserva mensajes y el consumidor continúa desde el primer mensaje no confirmado.

## 4. Bootstrap y reconciliación

La estrategia aprobada es una combinación acotada de eventos y reconciliación por API:

1. Un actor autenticado con `REPORT_READ`, `CATALOG_READ` e `INVENTORY_READ` invoca `POST /api/v1/admin/reconciliation`.
2. Reporting toma un lock exclusivo local de reconciliación y pausa su consumer.
3. Con el mismo bearer recibido, consulta de forma paginada `GET /api/v1/products` y `GET /api/v1/inventory`; consulta además `GET /api/v1/categories` y `GET /api/v1/units` para resolver códigos y nombres de dimensión.
4. Reporting nunca accede a tablas de otro schema. Cada página se valida y se aplica a tablas temporales de staging dentro de su conexión/transacción. Los productos se comparan por `version`.
5. Al completar todas las páginas, reemplaza atómicamente las proyecciones vigentes por el staging dentro de `analytics`, actualiza los `updated_at` de las filas reconciliadas, libera el lock y reanuda el consumer.
6. Los eventos acumulados durante el barrido se aplican después. Como los saldos del evento son snapshots absolutos y la cola mantiene orden, la convergencia no aplica deltas dos veces. La versión impide regresión de productos.

Una falla conserva las proyecciones vigentes, descarta el staging y deja la reconciliación como fallida. No existe transacción distribuida. La operación se puede repetir con el mismo resultado lógico.

## 5. Permisos

- `REPORT_READ` (`10000000-0000-0000-0000-000000000007`) protege dashboard, reportes operacionales y reconciliación. Roles MVP: `ADMIN` y `SUPERVISOR`.
- `ANALYTICS_READ` (`10000000-0000-0000-0000-000000000014`) es una capacidad separada para exportación técnica/BI incremental. En el MVP se reserva y se asigna solo a `ADMIN`; `ENCARGADO` y `SUPERVISOR` no la reciben.
- La credencial dedicada de integración BI y `/analytics/exports` quedan diferidas. No se reutiliza `REPORT_READ` como sustituto.
- La incorporación a IAM operativa exige una migración versionada posterior con detección de colisión; este contrato no autoriza cambios manuales ni operativos.

## 6. Tiempo y consistencia visible

- Persistencia y eventos usan `TIMESTAMPTZ`/RFC 3339 en UTC.
- `from` es inclusivo y `to` exclusivo. Se exige `from < to`.
- Un día o mes de negocio se interpreta en `America/Lima`: `[inicio local, inicio local siguiente)` y luego se convierte a UTC.
- Las respuestas devuelven instantes UTC y `timeZone: America/Lima`; la Web presenta en esa zona.
- Toda respuesta analítica incluye `dataUpdatedAt`, calculado como el mayor `updated_at`/`processed_at` incorporado; es `null` antes del primer evento o reconciliación. La consistencia es eventual y el cliente no debe presentarla como stock autoritativo en tiempo real.

## 7. API MVP

El contrato detallado está en `api/reporting-openapi.yaml`:

- `GET /api/v1/dashboard`: KPI operativos y tendencia por período.
- `GET /api/v1/reports/movements`: movimientos confirmados paginados.
- `GET /api/v1/reports/inventory-valuation`: valorización de saldos actuales paginada.
- `GET /api/v1/reports/adjustments`: ajustes confirmados paginados.
- `POST /api/v1/admin/reconciliation`: bootstrap/reconciliación explícita de proyecciones.

Los listados usan `page=0`, `size=20`, `page >= 0`, `1 <= size <= 100`. Movimientos y ajustes se ordenan por `confirmedAt DESC, movementId DESC`; valorización por `stockValuePen DESC, stockBalanceId ASC`. No se admite sort arbitrario.

Los KPI no quedan abiertos a interpretación: `stockValuePen` es la suma de `quantity * avgCostPen` por saldo; la existencia por producto es la suma de todos sus saldos. `outOfStockProductCount` cuenta productos activos con existencia total cero y `lowStockProductCount` productos activos con existencia mayor que cero y menor o igual que `minStock`, sin doble conteo. Los conteos de movimientos usan `confirmedAt` dentro de `[from,to)` y la tendencia agrupa esos conteos por límites `DAY` o `MONTH` de `America/Lima`. `topCriticalProducts` ordena por déficit `max(minStock - existenciaTotal, 0) DESC` y luego `productId ASC`.

La generación PDF/XLSX/CSV, `report_job`, exportación incremental BI, kardex completo, activos, vencimientos de lote, consumo por centro de costo y exactitud de conteos quedan diferidos. No aparecen como endpoints activos del OpenAPI MVP.

## 8. Seguridad y errores

Todas las rutas usan JWT RS256. La ausencia o invalidez del token responde 401; permiso insuficiente, 403. Parámetros inválidos responden 400. Los errores usan `application/problem+json` con `type`, `title`, `status`, `detail`, `code` y `correlationId` cuando esté disponible. No se persisten JWT, OTP, contraseñas, secretos ni datos personales no incluidos expresamente en los snapshots canónicos.

## 9. Migraciones limpias para servicio no liberado

La secuencia a implementar es:

1. `V1__create_schema.sql`: crear exclusivamente `analytics`.
2. `V2__reporting_mvp_projections.sql`: crear las cuatro tablas MVP, sus constraints e índices.

La actual `V3__initial_reference_data.sql` es inválida porque lee `catalog.*` e `inventory.*`; debe eliminarse antes de la primera liberación. No se migra ni copia información mediante SQL cross-schema.

## 10. Pruebas de aceptación futuras

- PostgreSQL Testcontainers: Flyway limpio, ownership, persistencia, agregación, deduplicación, replay sobre proyecciones vacías y rollback.
- RabbitMQ Testcontainers: mensajes reales de ambos schemas canónicos, redelivery, versión anterior de producto, fallo/recovery y orden del consumer.
- Reconciliación: APIs stub paginadas, staging, fallo sin reemplazo parcial, token reenviado y convergencia con eventos acumulados.
- Seguridad: 401, 403, permisos de reconciliación y Problem Details.
- API: rangos `[from,to)`, zona Lima, datos vacíos, conteos, precisión monetaria, paginación y orden determinista.
