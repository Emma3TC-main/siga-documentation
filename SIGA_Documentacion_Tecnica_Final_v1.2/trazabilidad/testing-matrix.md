# Matriz de Testing — SIGA v1.2

| ID | Requisito/Regla | Escenario | Nivel | Herramienta | Resultado esperado | Evidencia |
|---|---|---|---|---|---|---|
| TC-INV-001 | RF-08/RNF-05 | Salida válida | Integración | JUnit/Testcontainers | `CONFIRMED` + stock/costo/outbox en un commit | JUnit |
| TC-INV-002 | RNF-14 | Salidas 8 y 7 concurrentes sobre stock 10 | Concurrencia | JUnit/Testcontainers | una confirma; otra 409; stock nunca <0 | JUnit/log |
| TC-INV-003 | RNF-05/14 | Falla tras update parcial | Transacción | Testcontainers | rollback total, sin movimiento/outbox parcial | JUnit |
| TC-INV-004 | RNF-15 | Retry misma Idempotency-Key/payload | API | REST Assured | misma respuesta, un solo efecto | API report |
| TC-INV-005 | RNF-15 | Misma key con payload distinto | API | REST Assured | 409 | API report |
| TC-STATE-001 | RF-29 | Transición inválida | Unit | JUnit | rechazo | JUnit |
| TC-STATE-002 | RF-10 | Intento de editar `CONFIRMED` | Integración | JUnit | rechazado; compensación separada | JUnit |
| TC-ASSET-001 | RF-28 | Mismo asset con stock positivo en dos ubicaciones | DB/Integración | PostgreSQL/Testcontainers | constraint/validación rechaza segundo registro | JUnit |
| TC-ASSET-002 | RF-28 | Asset con cantidad >1 | DB | PostgreSQL | CHECK rechaza | JUnit |
| TC-TRACE-001 | RF-27/28 | Asociar lote/asset de otro producto | DB/Integración | PostgreSQL | FK compuesta/validación rechaza | JUnit |
| TC-UOM-001 | RF-23 | 2 cajas × factor 50 | Integración | JUnit | snapshot entered=2, factor=50, stockQty=100 | JUnit |
| TC-UOM-002 | RF-23 | Cambiar conversión después del movimiento | Integración | JUnit | histórico conserva factor aplicado | JUnit |
| TC-SUP-001 | RF-35 | Alta con taxId/RUC duplicado | API/Integración | REST Assured/JUnit | 409; no crea duplicado | API report |
| TC-SUP-002 | RF-35/RF-07/RNF-06 | Entrada externa con proveedor activo | Integración | JUnit/Testcontainers | valida `supplier_ref`, confirma y conserva snapshot de proveedor | JUnit |
| TC-SUP-003 | RF-35/RF-07 | Entrada externa con proveedor inexistente/inactivo | Integración | JUnit/Testcontainers | 422/409; no modifica stock | JUnit |
| TC-SUP-004 | RF-35/RNF-07 | `SupplierUpdated` redelivered | Mensajería | RabbitMQ/Testcontainers | `processed_event` evita doble proyección | JUnit |
| TC-PROJ-001 | RNF-05/07 | Catalog no disponible durante confirmación | Integración | WireMock/Testcontainers | Inventory usa product_ref/supplier_ref local; no dependencia REST | JUnit |
| TC-PROJ-002 | RNF-07 | ProductUpdated redelivered | Mensajería | RabbitMQ/Testcontainers | processed_event evita doble proyección | JUnit |
| TC-COUNT-001 | RF-33 | Conteo con diferencia | Integración | JUnit | guarda diferencia; stock no cambia hasta ajuste | JUnit |
| TC-EVI-001 | RF-30/RNF-17 | PDF válido owner=MOVEMENT | Integración | MinIO/Testcontainers | metadata + SHA-256 + object + outbox | report |
| TC-EVI-002 | RF-30 | Evidencia owner=ASSET/REPORT | API | REST Assured | ownerType/ownerId conservados | report |
| TC-EVI-003 | RNF-17 | MIME/magic bytes inválidos | Security | REST Assured | 400/rechazo | report |
| TC-EVT-001 | ADR-007 | RabbitMQ caído tras commit en IAM/CAT/INV/EVI | Integración | Testcontainers | negocio confirmado; outbox pendiente/retry | logs/JUnit |
| TC-EVT-002 | RNF-07 | Evento duplicado en INV/AUD/REP | Mensajería | Testcontainers | un solo efecto por processed_event | JUnit |
| TC-AUTH-001 | RF-01 | MFA incorrecto | API | REST Assured | 401/rate/block policy | report |
| TC-AUTH-002 | RF-03 | Permiso insuficiente | API | REST Assured | 403 backend | report |
| TC-REP-001 | RF-13/17 | Dashboard/report desde read models | Integración | JUnit | consulta analytics; no escritura Inventory | JUnit |
| TC-REP-002 | RF-19/34 | Export incremental | API | REST Assured | nextCheckpoint consistente | report |
| TC-E2E-001 | RF-07/RF-35 | Entrada Web | E2E | Playwright | flujo completo; proveedor visible/validado cuando aplica | artifact |
| TC-MOB-001 | RF-15 | Confirmar movimiento offline | E2E | Maestro | operación bloqueada hasta conexión | screenshot |
| TC-PERF-001 | RNF-08 | 50 users | Load | k6 | P95/errores dentro de thresholds | k6 |
| TC-SEC-001 | RNF-02 | IDOR | Security | ZAP/manual | 403 | report |
| TC-REC-001 | RNF-10 | Restore | Recovery | PostgreSQL/GCS | RPO<=24h; RTO<=4h | plantilla |
