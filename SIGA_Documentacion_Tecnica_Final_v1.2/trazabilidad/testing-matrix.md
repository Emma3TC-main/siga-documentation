# Matriz de Testing — SIGA v1.2

| ID | Requisito/Regla | Escenario | Nivel | Herramienta | Resultado esperado | Evidencia |
|---|---|---|---|---|---|---|
| TC-INV-001 | RF-08/RNF-05 | Salida válida | Integración | JUnit/Testcontainers | `CONFIRMED` + stock/costo/outbox en un commit | JUnit |
| TC-INV-002 | RNF-14 | Salidas 8 y 7 concurrentes sobre stock 10 | Concurrencia | JUnit/Testcontainers | una confirma; otra 409; stock nunca <0 | JUnit/log |
| TC-INV-003 | RNF-05/14 | Falla tras update parcial | Transacción | Testcontainers | rollback total, sin movimiento/outbox parcial | JUnit |
| TC-INV-004 | RNF-15 | Retry misma Idempotency-Key/payload | API | REST Assured | misma respuesta, un solo efecto | API report |
| TC-INV-005 | RNF-15 | Misma key con payload distinto | API | REST Assured | 409 | API report |
| TC-INV-D4-001 | D4 costo | ENTRY/EXIT/TRANSFER/ADJUST con snapshots y `HALF_UP` escala 6 | Integración | JUnit/Testcontainers | costo y stock coherentes en un commit | JUnit |
| TC-INV-D4-002 | ADR-007/D4 | `MovementConfirmed v1` | Integración/Mensajería | JUnit/Testcontainers | schema, routing, outbox, confirm y retry | JUnit |
| TC-INV-D4-003 | D4 atomicidad | rollback multi-detalle | Integración PostgreSQL | JUnit/Testcontainers | movimiento, saldo, snapshots, idempotencia y outbox revierten juntos | JUnit |
| TC-INV-D4-004 | D4 concurrencia | misma Idempotency-Key y saldo competido | Integración PostgreSQL | JUnit/Testcontainers | una aplicación efectiva; no stock negativo ni outbox duplicado | JUnit |
| TC-INV-D4-005 | D4 concurrencia | transferencias cruzadas y creación destino | Integración PostgreSQL | JUnit/Testcontainers | orden de locks sin deadlock; una fila destino y saldos consistentes | JUnit |
| TC-INV-D4-006 | D4 outbox | confirm, fallo y retry de MovementConfirmed | Integración RabbitMQ | JUnit/Testcontainers | mensaje persistente; PUBLISHED solo tras ACK; eventId estable en retry | JUnit |
| TC-INV-D4-007 | D4 concurrencia | creación de destinos multi-clave en orden inverso | Integración PostgreSQL | JUnit/Testcontainers | claves deduplicadas/ordenadas, sin deadlock y una fila por saldo | JUnit |
| TC-INV-D4-008 | D4 evento | payload Reporting/Audit y mensaje Rabbit real | Integración/Mensajería | JUnit/Testcontainers | schema valida snapshots aprobados y no transporta secretos | JUnit |
| TC-INV-D4-009 | D4 publisher | worker configurado y fallo observable | Integración/Mensajería | JUnit/Testcontainers | invocación programada configurable, log de eventId y retry preservado | JUnit |
| TC-STATE-001 | RF-29 | Transición inválida | Unit | JUnit | rechazo | JUnit |
| TC-STATE-002 | RF-10 | Intento de editar `CONFIRMED` | Integración | JUnit | rechazado; compensación separada | JUnit |
| TC-ASSET-001 | RF-28 | Mismo asset con stock positivo en dos ubicaciones | DB/Integración | PostgreSQL/Testcontainers | constraint/validación rechaza segundo registro | JUnit |
| TC-ASSET-002 | RF-28 | Asset con cantidad >1 | DB | PostgreSQL | CHECK rechaza | JUnit |
| TC-TRACE-001 | RF-27/28 | Asociar lote/asset de otro producto | DB/Integración | PostgreSQL | FK compuesta/validación rechaza | JUnit |
| TC-TRACE-002 | RF-27/CUS-25 | Consulta operacional de lotes | API/Integración | MockMvc/JUnit/Testcontainers | `INVENTORY_READ`; solo ACTIVE no vencidos; agregado/filtro de ubicación, disponibilidad, paginación y orden estable; 400/401/403 | JUnit |
| TC-TRACE-003 | RF-28/CUS-25 | Consulta operacional de activos | API/Integración | MockMvc/JUnit/Testcontainers | `INVENTORY_READ`; solo OPERATIVO; UNASSIGNED sin saldo positivo e IN_STOCK con saldo unitario; filtros, paginación y orden estable; 400/401/403 | JUnit |
| TC-LOT-ADMIN-001 | RF-27/CUS-25 | Alta y validación de lote | API/Integración (planificado) | MockMvc/JUnit/PostgreSQL | flags requeridos, `lotNumber` nullable cuando corresponda, identidad producto+lote, fechas, ACTIVE/EXPIRED inicial y versión 0; sin stock | Evidencia futura Slice B |
| TC-LOT-ADMIN-002 | RF-27/RNF-14 | PUT/no-op/concurrencia y lifecycle Lot | Integración/Concurrencia (planificado) | JUnit/PostgreSQL | versión antes del no-op; cuarentena/bloqueo/reactivación; expiración y depletion automáticos; reapertura DEPLETED válida | Evidencia futura Slice B |
| TC-LOT-ADMIN-003 | RF-27/ADR-007 | Selectores, Outbox y seguridad Lot | API/Mensajería (planificado) | JUnit/PostgreSQL/RabbitMQ | selector excluye no utilizables; admin ve todos; no muta stock; evento solo en cambio; retry/schema/permisos | Evidencia futura Slice B/D |
| TC-ASSET-ADMIN-001 | RF-28/CUS-25 | Registro y metadata Asset | API/Integración (planificado) | MockMvc/JUnit/PostgreSQL | exige producto serial, código/serie únicos, OPERATIVO/version 0; PUT/no-op/stale; sin stock/custodia | Evidencia futura Slice C |
| TC-ASSET-ADMIN-002 | RF-28/RNF-14 | Lifecycle STATE-02 | Integración (planificado) | JUnit/PostgreSQL | transiciones permitidas; EN_TRANSITO rechazado por admin; FUERA_SERVICIO exige cero y es terminal | Evidencia futura Slice C |
| TC-ASSET-ADMIN-003 | RF-28/ADR-007 | Selector, Outbox y seguridad Asset | API/Mensajería (planificado) | JUnit/PostgreSQL/RabbitMQ | selector solo OPERATIVO; admin ve todos; no muta stock; evento solo en cambio; retry/schema/permisos | Evidencia futura Slice C/D |
| TC-TRACE-AUDIT-001 | RF-12/RF-27/28 | Audit LotChanged/AssetChanged | Integración/Mensajería (planificado) | JUnit/Testcontainers | mapeos LOT_*/ASSET_*, deduplicación por eventId y ausencia de notificación | Evidencia futura Slice D |
| TC-LOC-001 | RF-24/CUS-24 | Crear raíz e hijo; código duplicado | API/Integración (planificado) | MockMvc/JUnit/Testcontainers | 201 activo/version 0; código único e inmutable; 409 DATA_CONFLICT en duplicado | Evidencia futura Slice B |
| TC-LOC-002 | RF-24/CUS-24 | Jerarquía inválida y concurrencia | Integración/Concurrencia (planificado) | JUnit/PostgreSQL | rechaza padre inactivo, self-parent, ciclo profundo y reparentados inversos concurrentes | Evidencia futura Slice B |
| TC-LOC-003 | RF-24/RNF-14 | PUT, no-op y versión obsoleta | API/Integración (planificado) | MockMvc/JUnit | reemplazo editable incrementa una vez; no-op no escribe/evento; stale 409 antes del no-op | Evidencia futura Slice B |
| TC-LOC-004 | RF-24/CUS-24 | Desactivar hoja y bloqueadores de subárbol | Integración (planificado) | JUnit/Testcontainers | bloquea descendiente activo, stock positivo y conteo abierto; permite saldo cero/conteo terminal/histórico; sin cascade | Evidencia futura Slice B |
| TC-LOC-005 | RF-24/CUS-24 | Reactivación | API/Integración (planificado) | MockMvc/JUnit | conserva id/código; exige versión y padre activo; no-op vigente sin escritura | Evidencia futura Slice B |
| TC-LOC-006 | RF-24/RF-03 | Permisos Location | Seguridad/API (planificado) | MockMvc/JWT | GET admite INVENTORY_READ o LOCATION_MANAGE; mutaciones solo LOCATION_MANAGE; 401/403 | Evidencia futura Slice B |
| TC-LOC-007 | RF-24/ADR-007 | LocationChanged v1 | Integración/Mensajería (planificado) | PostgreSQL/RabbitMQ Testcontainers | mutación + Outbox atómico, schema/routing/confirm/retry; sin evento en no-op o rechazo | Evidencia futura Slice B |
| TC-LOC-008 | RF-12/RNF-07 | Audit central Location | Integración/Mensajería (planificado) | JUnit/Testcontainers | acciones LOCATION_* y actor correctos; deduplicación por eventId; sin notificación | Evidencia futura Slice B |
| TC-UOM-001 | RF-23 | 2 cajas × factor 50 | Integración | JUnit | snapshot entered=2, factor=50, stockQty=100 | JUnit |
| TC-UOM-002 | RF-23 | Cambiar conversión después del movimiento | Integración | JUnit | histórico conserva factor aplicado | JUnit |
| TC-CAT-001 | RF-04/CUS-04 | Listar categorías | API/Integración | REST Assured/JUnit | 200, arreglo `{id,code,name,categoryType,active}`, activas/inactivas y `code ASC`; 401/403 según JWT/permisos | API report/JUnit |
| TC-UOM-003 | RF-23/CUS-23 | Listar unidades | API/Integración | REST Assured/JUnit | 200, arreglo `{id,code,name,symbol,dimension,active}`, activas/inactivas y `code ASC`; 401/403 según JWT/permisos | API report/JUnit |
| TC-PROD-001 | RF-05/RF-23/CUS-05 | Alta de producto | Integración | JUnit | 201; producto, conversiones y `ProductCreated v1` PENDING en un commit; UoM storage→base directa si difieren; precisión 18,6 | JUnit |
| TC-PROD-002 | RF-05/CUS-05 | Referencia Product inexistente/inactiva | API/Integración | MockMvc/JUnit | 404 para categoría/UoM inexistente; 409 para referencia inactiva; sin producto ni outbox | JUnit |
| TC-PROD-003 | ADR-007/RNF-07 | Redelivery ProductCreated | Mensajería | Testcontainers | Inventory deduplica `eventId` mediante `processed_event`; entrega al menos una vez | JUnit |
| TC-PROD-004 | RF-05/RF-27/RF-28/CUS-05 | Flags de trazabilidad independientes | Integración | JUnit | Acepta una combinación válida, incluso `requiresHeatNumber=true` con `requiresLot=false`, y conserva cada booleano | JUnit |
| TC-PROD-005 | RF-05/RF-16/CUS-05/CUS-16 | Consultar productos | API/Integración | MockMvc/JUnit | Page estable por SKU/nombre + id; filtros combinados, `%`/`_` literales, vacío, límites, activo/inactivo, detalle 404 y 401/403 sin efectos | JUnit |
| TC-PROD-006 | RF-05/RNF-14/CUS-05 | Reemplazo completo y concurrencia de Product | API/Integración | MockMvc/JUnit/PostgreSQL | PUT exige todos los campos y `expectedVersion`; update condicional incrementa versión una vez; versión obsoleta devuelve 409 aun si el contenido coincide; no-op vigente devuelve 200 sin producto/conversiones/timestamps/outbox nuevos | JUnit |
| TC-PROD-007 | RF-05/CUS-05 | Desactivar/reactivar con referencias históricas | Integración | JUnit/PostgreSQL | Desactivación conserva referencias existentes ahora inactivas sin consultar Inventory; no admite referencias inactivas nuevas; reactivación exige todas las referencias vigentes; no borra historial | JUnit |
| TC-PROD-008 | RF-05/RF-23/ADR-007 | ProductUpdated v1 transaccional | Integración/Mensajería | JUnit/RabbitMQ | Producto + reemplazo completo de conversiones + Outbox PENDING en un commit; rollback total; schema y `catalog.product.updated.v1`; snapshot cubre Inventory/Reporting; regresión de los cuatro eventos Catalog previos | JUnit |
| TC-SUP-001 | RF-35 | Alta con taxId/RUC duplicado | API/Integración | REST Assured/JUnit | 409; no crea duplicado | API report |
| TC-SUP-002 | RF-35/RF-07/RNF-06 | Entrada externa con proveedor activo | Integración | JUnit/Testcontainers | valida `supplier_ref`, confirma y conserva snapshot de proveedor | JUnit |
| TC-SUP-003 | RF-35/RF-07 | Entrada externa con proveedor inexistente/inactivo | Integración | JUnit/Testcontainers | 422/409; no modifica stock | JUnit |
| TC-SUP-004 | RF-35/RNF-07 | `SupplierUpdated` redelivered | Mensajería | RabbitMQ/Testcontainers | `processed_event` evita doble proyección | JUnit |
| TC-SUP-005 | RF-35/CUS-31 | API de proveedores | API/Integración | MockMvc/JUnit | POST/GET/PUT, búsqueda literal, filtros, página/orden, estados y 400/401/403/404/409 | JUnit |
| TC-SUP-006 | RF-35/CUS-31/RNF-14 | Versión, transiciones y no-op | Integración | JUnit/PostgreSQL | update condicional; no-op sin versión/outbox; desactivar/reactivar emite evento correcto | JUnit |
| TC-SUP-007 | RF-35/ADR-007/RNF-07 | Outbox y publicación Supplier v1 | Integración/Mensajería | JUnit/RabbitMQ | atomicidad/rollback, schemas, routing, persistencia, confirm, retry y regresión ProductCreated | JUnit |
| TC-PROJ-001 | RNF-05/07 | Catalog no disponible durante confirmación | Integración | WireMock/Testcontainers | Inventory usa product_ref/supplier_ref local; no dependencia REST | JUnit |
| TC-PROJ-002 | RNF-07 | ProductUpdated redelivered o fuera de orden | Mensajería | RabbitMQ/Testcontainers | `processed_event` deduplica `eventId`; `source_version` impide sobrescribir con una versión igual/anterior; producto y conjunto completo de conversiones se aplican en una transacción | JUnit |
| TC-PROJ-003 | RNF-07/RF-20 | Alta Product en Reporting | Contrato/Integración | JUnit/Testcontainers | Pendiente: definir ProductCreated v2 o bootstrap; ProductCreated v1 no contiene nombre/categoría y ProductUpdated no cubre altas nunca modificadas | Evidencia futura |
| TC-COUNT-001 | RF-33 | Conteo con diferencia | Integración | JUnit | guarda diferencia; stock no cambia hasta ajuste | JUnit |
| TC-COUNT-002 | RF-33/CUS-28 | Snapshot por ubicación | Integración PostgreSQL | JUnit/Testcontainers | creación captura una vez todas las dimensiones; movimiento posterior no reescribe `system_quantity`; sin locks largos | JUnit |
| TC-COUNT-003 | RF-33/CUS-28 | Ciclo y concurrencia | API/Integración | MockMvc/JUnit/Testcontainers | DRAFT→IN_PROGRESS→COMPLETED y cancelación; `expectedVersion` obsoleto 409; cierre incompleto 400; rollback atómico | JUnit |
| TC-COUNT-004 | RF-33/CUS-28 | Seguridad y actores | Seguridad/API | MockMvc/JUnit | 401/403 `INVENTORY_COUNT`; actores solo desde JWT `sub`; ADMIN/ENCARGADO/SUPERVISOR autorizados | JUnit |
| TC-COUNT-005 | RF-33/CUS-28 | Regularización separada | Integración | JUnit/Testcontainers | cierre no modifica stock ni crea eventos/ajustes; posterior ADJUST +/- reutiliza autorización, Evidence MOVEMENT y MovementConfirmed v1 | JUnit |
| TC-EVI-001 | RF-30/RNF-17 | PDF válido owner=MOVEMENT | Integración | PostgreSQL+MinIO Testcontainers | owner validado antes de storage; objeto privado + metadata + SHA-256 + Outbox; respuesta no expone objectKey | JUnit |
| TC-EVI-002 | RF-30 | Listado scoped y descarga | API | REST Assured+MinIO | ownerType/ownerId obligatorios; page 0, size 20/1..100; orden uploadedAt DESC,id DESC; stream privado con nombre sanitizado | JUnit |
| TC-EVI-003 | RNF-17 | MIME/extensión/magic bytes, tamaño o metadata inválidos | Security | REST Assured | 400/413/415 sin objeto ni DB; metadata raíz object <=16 KiB/profundidad 5 | JUnit |
| TC-EVI-004 | RF-30/RNF-06 | Autorización coarse + owner | Security/Integración | JWT+Inventory stub | 401 sin JWT; 403 sin permiso; owner inexistente/no visible 404; Inventory no disponible 503; no IDOR | JUnit |
| TC-EVI-005 | RNF-07 | Retry de upload por Idempotency-Key | Integración | PostgreSQL+MinIO Testcontainers | mismo request devuelve 201 original; request distinto/en proceso 409; un objeto, metadata y evento | JUnit |
| TC-EVI-006 | RNF-07/RNF-17 | Falla DB después de storage | Integración | PostgreSQL+MinIO Testcontainers | rollback y borrado del objeto exacto; falla de compensación observable como incidente sin datos sensibles | JUnit |
| TC-EVI-007 | ADR-007 | Publicación EvidenceUploaded v1 | Mensajería | RabbitMQ Testcontainers | mensaje persistente en siga.events/evidence.uploaded.v1, schema válido, PUBLISHED solo tras confirm, retry con eventId estable | JUnit |
| TC-EVI-008 | RF-29/RF-30 | Política de evidencia de movimiento | Contrato/Integración | Inventory+Evidence adapters | ENTRY/EXIT/TRANSFER opcional; ajustes sensibles exigen evidencia AVAILABLE antes de submit; sin transacción distribuida | JUnit |
| TC-EVT-001 | ADR-007 | RabbitMQ caído tras commit en IAM/CAT/INV/EVI | Integración | Testcontainers | negocio confirmado; outbox pendiente/retry | logs/JUnit |
| TC-EVT-002 | RNF-07 | Evento duplicado en INV/AUD/REP | Mensajería | Testcontainers | un solo efecto por processed_event | JUnit |
| TC-AUTH-001 | RF-01 | MFA incorrecto | API | REST Assured | 401/rate/block policy | report |
| TC-AUTH-002 | RF-03 | Permiso insuficiente | API | REST Assured | 403 backend | report |
| TC-IAM-ADMIN-001 | RF-02/CUS-02 | Usuarios administrativos | API/Seguridad | MockMvc/JUnit | página 0/20/100 y `username ASC`; modelo limitado; 400/401/403/404/409; sin filtros globales | JUnit |
| TC-IAM-ADMIN-002 | RF-02/RF-03/ADR-011 | Mutaciones administrativas con step-up | Seguridad/API | MockMvc/JUnit | permiso efectivo + `auth_time <=300s`; refresh no renueva; stale devuelve `403 AUTH_FORBIDDEN`; sin actor cliente | JUnit |
| TC-IAM-ADMIN-003 | RF-03/CUS-03 | Roles y catálogo de permisos | API/Integración | MockMvc/JUnit | listar/crear roles; permisos read-only por `code ASC`; reemplazo completo; ADMIN protegido; sin PATCH/delete | JUnit |
| TC-IAM-ADMIN-004 | RF-02/RF-03 | Reemplazo last-write-wins MVP | UI/API | Smoke autenticado | carga conjunto vigente, confirmación explícita y recarga posterior; no se simula versión o conflicto inexistente | Reporte UI |
| TC-IAM-ADMIN-005 | ADR-007/RF-02/RF-03 | Eventos administrativos Identity v2 | Contrato/Integración/Mensajería (planificado) | JSON Schema+PostgreSQL+RabbitMQ | 10 schemas Draft 2020-12 válidos; requeridos/objetos cerrados/causation opcional/sin secretos; cada mutación emite aggregate/actor/snapshots v2 correctos | Evidencia futura Slice A/B |
| TC-IAM-AUDIT-001 | ADR-007/RF-02/RF-03 | Consumidor Audit IAM dual v1/v2 | Integración/Mensajería (planificado) | PostgreSQL+RabbitMQ | acciones canónicas y fallback `IDENTITY_ROLE_CHANGED_LEGACY`; eventId idempotente; Audit+processed_event atómicos; duplicado sin efecto | Evidencia futura Slice C |
| TC-IAM-AUDIT-002 | ADR-007/RNF-07 | Fallos del consumidor Audit IAM | Integración/Mensajería (planificado) | RabbitMQ | inválido/no soportado a DLQ; retry transitorio acotado; sin requeue infinito ni Notifications; nueve históricos preservados | Evidencia futura Slice C/D |
| TC-INV-SENS-001 | RF-29 | Sensibilidad MVP | Unitario/Integración | JUnit/Testcontainers | Ajustes y EXIT/TRANSFER con asset requieren autorización; EXIT sin asset no se marca por tipo | JUnit |
| TC-INV-ACTOR-001 | RNF-02/RF-09 | Actor autenticado | Seguridad | JUnit | `sub` UUID deriva registrador/autorizador; body no puede suplantarlo | JUnit |
| TC-INV-STEPUP-001 | RF-29 | Step-up JWT | Seguridad | JUnit | `amr=otp`, `auth_time` <=300 s y MOVEMENT_AUTHORIZE; ausencia o stale rechaza | JUnit |
| TC-INV-APPROVAL-001 | RF-08/RF-09/RF-29 | Aprobación por capacidad | Unitario/API/Integración | JUnit/Testcontainers | Actor sin MOVEMENT_AUTHORIZE envía a PENDING_AUTHORIZATION y no confirma DRAFT; actor con permiso puede confirmar directo solo no sensible | JUnit |
| TC-INV-MAKER-CHECKER-001 | RF-29 | Separación maker-checker | Unitario/API | JUnit | authorize/reject rechaza cuando `sub == registeredByUserId`, aun con permiso y step-up válido | JUnit |
| TC-CAT-READ-001 | RF-04/RF-05/RF-23/RF-35 | Lectura de maestros | API/Seguridad | JUnit | CATALOG_READ permite GET de productos, categorías, unidades y proveedores sin conceder mutaciones | JUnit |
| TC-INV-CODE-001 | RNF-07 | Código concurrente | Integración | PostgreSQL Testcontainers | `MOV-YYYY-NNNNN`, único bajo concurrencia y sin MAX()+1 | JUnit |
| TC-REP-001 | RF-13/17 | Dashboard/report desde read models | Integración | JUnit | consulta analytics; no escritura Inventory | JUnit |
| TC-REP-002 | RF-13/RF-20 | Proyección MovementConfirmed v1 | Integración/Mensajería | PostgreSQL+RabbitMQ Testcontainers | movimiento y saldos afectados en un commit; duplicado sin efecto; fallo permite redelivery | JUnit |
| TC-REP-003 | RF-13/RNF-07 | ProductUpdated v1 fuera de orden | Integración/Mensajería | PostgreSQL+RabbitMQ Testcontainers | `source_version` impide regresión y `eventId` deduplica | JUnit |
| TC-REP-004 | RF-13/RF-20 | Bootstrap/reconciliación | Integración | WireMock+PostgreSQL Testcontainers | páginas Catalog/Inventory a staging propio; fallo conserva proyección activa; no SQL cross-schema | JUnit |
| TC-REP-005 | RF-13/RF-20 | Dashboard y reportes MVP | API/Seguridad | MockMvc+PostgreSQL Testcontainers | 401/403; `[from,to)` UTC/Lima; vacíos, precisión, página 0/20/100 y orden estable | JUnit |
| TC-NOT-001 | RF-12/RF-32 | API personal de notificaciones | API/Seguridad | MockMvc+PostgreSQL Testcontainers | 401; scope por JWT `sub`; 404 anti-enumeración; página 0/20/100 y orden estable | JUnit |
| TC-NOT-002 | RF-12/RF-32 | Lectura y conteo | Integración PostgreSQL | JUnit/Testcontainers | filtro unread, conteo exacto y `POST read` idempotente conserva el primer `readAt` | JUnit |
| TC-NOT-003 | ADR-007/RF-32 | `MovementConfirmed v1` a Notification | Integración/Mensajería | PostgreSQL+RabbitMQ Testcontainers | destinatario `registeredByUserId`; dedup e insert en un commit; ACK posterior | JUnit |
| TC-NOT-004 | ADR-007/RNF-15 | Redelivery, rollback, retry y DLQ | Integración/Mensajería | PostgreSQL+RabbitMQ Testcontainers | duplicado concurrente sin segunda fila; fallo revierte claim; 3 intentos y DLQ | JUnit |
| TC-NOT-005 | RF-32 | Web Remote Notifications | UI/Integración | Vitest/MSW o smoke remoto | badge, estados, mark-read, polling sin solapamiento/oculto y sin fallback Demo | Reporte UI |
| TC-REP-002 | RF-19/34 | Export incremental | API | REST Assured | nextCheckpoint consistente | report |
| TC-E2E-001 | RF-07/RF-35 | Entrada Web | E2E | Playwright | flujo completo; proveedor visible/validado cuando aplica | artifact |
| TC-MOB-001 | RF-15 | Confirmar movimiento offline | E2E | Maestro | operación bloqueada hasta conexión | screenshot |
| TC-PERF-001 | RNF-08 | 50 users | Load | k6 | P95/errores dentro de thresholds | k6 |
| TC-SEC-001 | RNF-02 | IDOR | Security | ZAP/manual | 403 | report |
| TC-REC-001 | RNF-10 | Restore | Recovery | PostgreSQL/GCS | RPO<=24h; RTO<=4h | plantilla |
