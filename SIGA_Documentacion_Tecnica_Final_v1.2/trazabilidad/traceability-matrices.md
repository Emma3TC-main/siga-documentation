# Matrices de trazabilidad — SIGA

## MTR-01 RF ↔ CUS

| RF | CUS | HU |
|---|---|---|
| RF-01 | CUS-01 | US-01 |
| RF-02 | CUS-02 | US-02 |
| RF-03 | CUS-03 | US-03 |
| RF-04 | CUS-04 | US-04 |
| RF-05 | CUS-05 | US-05 |
| RF-06 | CUS-06 | US-06 |
| RF-07 | CUS-07 | US-07 |
| RF-08 | CUS-08 | US-08 |
| RF-09 | CUS-07/CUS-08 | US-09 |
| RF-10 | CUS-11 | US-10 |
| RF-11 | CUS-12 | US-11 |
| RF-12 | CUS-30 | US-12 |
| RF-13 | CUS-13 | US-13 |
| RF-14 | CUS-14 | US-14 |
| RF-15 | CUS-15 | US-15 |
| RF-16 | CUS-16 | US-16 |
| RF-17 | CUS-17 | US-17 |
| RF-18 | CUS-18 | US-18 |
| RF-19 | CUS-19 | US-19 |
| RF-20 | CUS-20 | US-20 |
| RF-21 | CUS-21 | US-21 |
| RF-22 | CUS-22 | US-22 |
| RF-23 | CUS-23 | US-23 |
| RF-24 | CUS-24 | US-24 |
| RF-25 | CUS-09 | US-25 |
| RF-26 | CUS-10 | US-26 |
| RF-27 | CUS-25 | US-27 |
| RF-28 | CUS-25 | US-28 |
| RF-29 | CUS-27 | US-29 |
| RF-30 | CUS-26 | US-30 |
| RF-31 | CUS-29 | US-31 |
| RF-32 | CUS-30 | US-32 |
| RF-33 | CUS-28 | US-33 |
| RF-34 | CUS-17 | US-34 |
| RF-35 | CUS-31/CUS-07 | US-35 |

## MTR-02 RF ↔ HU

| RF | HU | Módulo |
|---|---|---|
| RF-01 | US-01 | Autenticación |
| RF-02 | US-02 | Usuarios |
| RF-03 | US-03 | Roles y permisos |
| RF-04 | US-04 | Categorías |
| RF-05 | US-05 | Productos |
| RF-06 | US-06 | Inventario |
| RF-07 | US-07 | Entradas |
| RF-08 | US-08 | Salidas |
| RF-09 | US-09 | Actualización de stock |
| RF-10 | US-10 | Historial |
| RF-11 | US-11 | Stock mínimo |
| RF-12 | US-12 | Alertas de stock |
| RF-13 | US-13 | Dashboard |
| RF-14 | US-14 | Consulta móvil |
| RF-15 | US-15 | Movimientos móviles |
| RF-16 | US-16 | Búsqueda y filtros |
| RF-17 | US-17 | Reportes |
| RF-18 | US-18 | Auditoría |
| RF-19 | US-19 | Interoperabilidad |
| RF-20 | US-20 | Indicadores |
| RF-21 | US-21 | Métricas y logs |
| RF-22 | US-22 | Recuperación |
| RF-23 | US-23 | Unidades y conversiones |
| RF-24 | US-24 | Ubicaciones |
| RF-25 | US-25 | Transferencias |
| RF-26 | US-26 | Ajustes |
| RF-27 | US-27 | Lotes/coladas/vencimientos |
| RF-28 | US-28 | Series y activos |
| RF-29 | US-29 | Autorizaciones |
| RF-30 | US-30 | Evidencias |
| RF-31 | US-31 | Multimoneda |
| RF-32 | US-32 | Notificaciones in-app |
| RF-33 | US-33 | Conteos físicos |
| RF-34 | US-34 | Exportación |
| RF-35 | US-35 | Proveedores |

## MTR-03 RNF ↔ Componente

| RNF | Componente | Criterio |
|---|---|---|
| RNF-01 | IAM/Gateway/Todos | Argon2id; nunca texto plano. |
| RNF-02 | IAM/Gateway/Todos | Backend protege toda función por roles/permisos. |
| RNF-03 | IAM/Gateway/Todos | Secretos fuera del código. |
| RNF-04 | IAM/Gateway/Todos | HTTPS externo; servicios internos no públicos. |
| RNF-05 | MS-INV | Nunca stock negativo ni confirmación parcial. |
| RNF-06 | MS-INV | Actor, fecha, ubicación, producto, cantidad, lote/serie y sustento. |
| RNF-07 | Transversal | Contratos versionados y degradación controlada. |
| RNF-08 | Transversal | Lectura P95<=500ms; comando<=1000ms; dashboard<=2000ms a 50 usuarios. |
| RNF-09 | Transversal | SLO objetivo >=99.5% mensual, sin mantenimiento programado. |
| RNF-10 | Transversal | RPO<=24h, RTO<=4h, backup diario y restore test. |
| RNF-11 | Transversal | SOLID, bounded contexts y Clean Architecture. |
| RNF-12 | Transversal | Loading/empty/error y mensajes comprensibles. |
| RNF-13 | Transversal | Chrome/Edge/Firefox últimas 2 versiones; Expo soportado. |
| RNF-14 | MS-INV | @Transactional + FOR UPDATE + constraints; READ COMMITTED. |
| RNF-15 | MS-INV | Idempotency-Key en comandos críticos. |
| RNF-16 | Todos/Observabilidad | Correlation ID, métricas, logs y trazas DEV/QA. |
| RNF-17 | MS-EVI | Object storage privado, SHA-256, MIME/magic bytes. |
| RNF-18 | Infraestructura | Docker Compose baseline; GKE objetivo. |
| RNF-19 | Transversal | WCAG 2.1 AA como referencia baseline. |
| RNF-20 | Transversal | Cobertura y pruebas ACID/concurrencia. |

## MTR-04 HU ↔ Sprint

| HU | Sprint |
|---|---|
| US-01 | Sprint 1 |
| US-02 | Sprint 1 |
| US-03 | Sprint 1 |
| US-04 | Sprint 1 |
| US-05 | Sprint 1 |
| US-06 | Sprint 1 |
| US-07 | Sprint 3 |
| US-08 | Sprint 3 |
| US-09 | Sprint 3 |
| US-10 | Sprint 3 |
| US-11 | Sprint 3 |
| US-12 | Sprint 3 |
| US-13 | Sprint 3 |
| US-14 | Sprint 3 |
| US-15 | Sprint 3 |
| US-16 | Sprint 4 |
| US-17 | Sprint 4 |
| US-18 | Sprint 4 |
| US-19 | Sprint 4 |
| US-20 | Sprint 4 |
| US-21 | Sprint 4 |
| US-22 | Sprint 4 |
| US-23 | Sprint 3-4 |
| US-24 | Sprint 3-4 |
| US-25 | Sprint 3-4 |
| US-26 | Sprint 3-4 |
| US-27 | Sprint 3-4 |
| US-28 | Sprint 3-4 |
| US-29 | Sprint 3-4 |
| US-30 | Sprint 3-4 |
| US-31 | Sprint 3-4 |
| US-32 | Sprint 3-4 |
| US-33 | Sprint 3-4 |
| US-34 | Sprint 3-4 |
| US-35 | Sprint 2-3 |

## MTR-05 CUS ↔ Diagramas

| CUS | Diagramas |
|---|---|
| CUS-01 | SEQ-01, SEQ-02 |
| CUS-07 | BPMN-01, SEQ-04 |
| CUS-08 | BPMN-02, SEQ-05/06, STATE-01 |
| CUS-09 | BPMN-03, SEQ-08 |
| CUS-10 | BPMN-04, SEQ-09 |
| CUS-27 | BPMN-05, SEQ-07 |
| CUS-26 | BPMN-06, SEQ-10, STATE-03 |
| CUS-17 | BPMN-07, SEQ-13 |
| CUS-19 | SEQ-14 |
| CUS-31 | UML-10, DER-05 |
| CUS-07 (proveedor) | BPMN-01, SEQ-04, DER-06 |

## MTR-06 RF/RNF ↔ Prueba

| Requisito | Prueba | Evidencia |
|---|---|---|
| RF-08/RNF-05/14 | JUnit+Testcontainers concurrencia | JUnit/JaCoCo |
| RNF-15 | REST Assured idempotencia | API report |
| RF-30/RNF-17 | Upload/security | Test report |
| RNF-08 | k6 | Performance report |
| RNF-10 | Restore Test | Plantilla/evidencia |
| RNF-01/02 | CodeQL/ZAP/manual | CI artifacts |
| RF-35 | Gestión/proyección/entrada con proveedor | JUnit/API/E2E |

## MTR-07 Vista ↔ API

| Vista | Actor | API |
|---|---|---|
| UI-W01 | Todos | POST /auth/login |
| UI-W02 | MFA | POST /auth/mfa/verify |
| UI-W03 | Admin/Supervisor | GET /dashboard |
| UI-W04 | Admin | /users |
| UI-W05 | Admin | /roles |
| UI-W06 | Admin | /categories |
| UI-W07 | Admin/Encargado | /products |
| UI-W08 | Admin | /units |
| UI-W08B | Admin/Autorizado | /suppliers |
| UI-W09 | Autorizado | GET /inventory |
| UI-W10 | Admin/Supervisor | /locations |
| UI-W11 | Encargado | inventory |
| UI-W12 | Encargado | POST /movements |
| UI-W13 | Autorizado | GET movement |
| UI-W14 | Autorizador | authorize/reject |
| UI-W15 | Encargado/Supervisor | POST movement |
| UI-W16 | Supervisor/Admin | POST movement |
| UI-W17 | Supervisor/Encargado | POST counts |
| UI-W18 | Autorizado | /evidences |
| UI-W19 | Autorizado | GET movements |
| UI-W20 | Autorizado | /reports |
| UI-W21 | Admin/Seguridad | /audit-events |
| UI-W22 | Autorizado | /notifications |
| UI-M01 | Móvil | /auth/login |
| UI-M02 | Móvil | /auth/mfa/verify |
| UI-M03 | Móvil | GET inventory |
| UI-M04 | Móvil | GET inventory |
| UI-M05 | Móvil autorizado | POST movement |
| UI-M06 | Móvil | POST evidences |
| UI-M07 | Móvil | /notifications |
| UI-M08 | Móvil | /auth/logout |

## MTR-08 ADR ↔ Área

| ADR | Área |
|---|---|
| ADR-001 | Arquitectura de microservicios |
| ADR-002 | Seis bounded services |
| ADR-003 | Inventory + Movement transaccional |
| ADR-004 | Schemas PostgreSQL por servicio |
| ADR-005 | JSONB restringido |
| ADR-006 | REST + RabbitMQ selectivo |
| ADR-007 | Transactional Outbox |
| ADR-008 | Lock pesimista |
| ADR-009 | Redis no autoritativo |
| ADR-010 | MinIO/GCS |
| ADR-011 | JWT RS256 + MFA |
| ADR-012 | Spring Cloud Gateway |
| ADR-013 | Compose baseline / K8s objetivo |
| ADR-014 | GCP |
| ADR-015 | Clean Architecture Web/Mobile |
| ADR-016 | Sin transacciones offline |
| ADR-017 | Multirepo + GitFlow simplificado |
| ADR-018 | Modelo de datos canónico y coherencia entre artefactos |


## MTR-09 RF ↔ Entidad física principal

| RF | Entidades principales |
|---|---|
| RF-01/02/03 | `iam.user_account`, `role`, `permission`, `user_role`, `role_permission`, `refresh_token` |
| RF-04/05 | `catalog.category`, `catalog.product` |
| RF-35 | `catalog.supplier`, `inventory.supplier_ref`, `inventory.movement`, `analytics.movement_projection` |
| RF-23 | `catalog.unit_measure`, `catalog.unit_conversion`, `inventory.product_unit_conversion_ref` |
| RF-06/09/11/12 | `inventory.product_ref`, `inventory.stock_balance`, `inventory.location` |
| RF-07/08/10/25/26 | `inventory.movement`, `movement_detail`, `stock_balance`, `outbox_event` |
| RF-27 | `inventory.lot`, `stock_balance`, `movement_detail` |
| RF-28 | `inventory.asset`, `stock_balance`, `movement_detail` |
| RF-29 | `inventory.movement_authorization` |
| RF-30 | `evidence.evidence_metadata`, `evidence.outbox_event` |
| RF-31 | `inventory.movement_detail` (TC snapshot + source) |
| RF-33 | `inventory.physical_count`, `physical_count_line` |
| RF-18/32 | `audit.audit_event`, `audit.notification`, `audit.processed_event` |
| RF-13/17/19/20/34 | `analytics.product_projection`, `inventory_projection`, `movement_projection`, `kpi_snapshot`, `report_job`, `export_checkpoint` |

## MTR-10 Invariante ↔ Artefacto ↔ Prueba

| Invariante | Modelo/Diagrama | Prueba |
|---|---|---|
| No stock negativo / commit all-or-nothing | DER-06, UML-04, SEQ-05/06 | TC-INV-002/003 |
| Activo serializado en una sola ubicación positiva | DER-06, UML-04 | TC-ASSET-001 |
| Lote/activo pertenece al mismo producto | DER-06 | TC-TRACE-001 |
| Conversión histórica reproducible | DER-05/06, SEQ-03 | TC-UOM-001 |
| Inventory confirma sin REST a Catalog | C4-04, SEQ-03/04 | TC-PROJ-001/TC-SUP-002 |
| Recepción externa conserva proveedor histórico | DER-05/06/09, UML-03/04, BPMN-01 | TC-SUP-002/003 |
| Idempotencia de comando | DER-06 | TC-INV-004 |
| Outbox por productor | SEQ-11, ADR-007 | TC-EVT-001 |
| Consumidor idempotente por ownership | SEQ-12 | TC-EVT-002 |
| Evidence owner genérico + SHA-256 | DER-07, UML-05, SEQ-10 | TC-EVI-001/002 |
| Reporting no modifica Inventory | DER-09, SEQ-13/14 | TC-REP-001 |
