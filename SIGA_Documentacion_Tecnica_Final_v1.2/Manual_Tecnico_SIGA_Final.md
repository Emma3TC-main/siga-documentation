# Manual Técnico — SIGA

## Sistema Integral de Gestión de Almacén para el Sector Mecánico/Minero

**Versión:** 1.2 — Consolidada y coherente con modelo de datos canónico y gestión de proveedores  
**Backend:** Java 21 + Spring Boot 3.x  
**Clientes:** React 19 + TypeScript + Vite / React Native + Expo  
**Persistencia:** PostgreSQL + Redis + Object Storage  
**Integración:** REST + RabbitMQ (eventos selectivos)  
**Infraestructura baseline:** Docker Compose sobre GCP  
**Arquitectura objetivo:** Kubernetes/GKE  
**Metodología:** Scrum, cuatro sprints principales  
**Documento relacionado:** Manual Administrativo — SIGA

> Este documento traduce a arquitectura, diseño, contratos, datos, seguridad, DevOps y pruebas las reglas aprobadas en el Manual Administrativo. ISO/IEC 25010, ISO/IEC 27001, OWASP y WCAG se usan como referencias, no como certificaciones.

## Control documental

| Elemento | Definición |
|---|---|
| Documento | Manual Técnico — SIGA |
| Propósito | Especificación implementable y verificable, sin ambigüedades entre colaboradores. |
| Alcance | Microservicios, datos, API, web, móvil, seguridad, evidencia, eventos, DevOps, observabilidad, continuidad y testing. |
| Fuente de verdad | PostgreSQL. Redis nunca sustituye stock/costo/movimientos/lotes/series/auditoría. |
| Regla central | Inventario + Movimientos en un solo núcleo transaccional ACID. |
| Estado | Línea base final; cambios arquitectónicos mediante ADR. |

# Índice de contenido

1. Introducción, contexto y objetivos  
2. Ingeniería de requisitos, CUN/CUS y trazabilidad  
3. Arquitectura del sistema  
4. Diseño de dominio y UML  
5. Arquitectura de datos y persistencia  
6. Diseño backend y contratos API  
7. Seguridad e identidad  
8. Diseño del Frontend Web  
9. Diseño de la aplicación móvil  
10. Evidencias, documentos y multimedia  
11. Eventos, mensajería y notificaciones  
12. Reportes, analítica e interoperabilidad  
13. Gestión de repositorios, GitFlow y CI/CD  
14. Infraestructura y despliegue  
15. Observabilidad y operación  
16. Continuidad, respaldo y recuperación  
17. Testing y calidad  
18. Diseño UX/UI y matriz maestra  
19. OpenAPI, contratos y eventos  
20. ADR, riesgos y escalabilidad  
21. Jira y GitHub  
22. Implementación por Sprint  
23. Cobertura del informe final  
24. Cierre y gobierno documental  
Anexo A. Especificaciones detalladas de CUS  
Anexo B. Casos de uso del negocio

> El documento usa estilos de encabezado para facilitar navegación en Word. Las fuentes PlantUML, contratos y matrices se entregan también como archivos independientes en el paquete.

# 1. Introducción, contexto y objetivos

## 1.1 Descripción breve
SIGA es una solución web y móvil para almacenes mecánico/mineros. Administra materiales, insumos, repuestos y maquinaria, incluyendo stock por ubicación, lotes/coladas, vencimientos, series/activos, costo promedio, evidencias, autorizaciones, auditoría y analítica.

## 1.2 Problemática
La información dispersa, la dificultad de conocer disponibilidad real, los errores de entrada/salida y la falta de trazabilidad generan riesgo operativo. El riesgo técnico más crítico es una operación concurrente o parcialmente fallida que deje inventario inconsistente; por ello ACID y trazabilidad son prioridades.

## 1.3 Objetivo general
Diseñar e implementar una plataforma distribuida y mantenible que centralice inventario industrial, preserve consistencia transaccional, soporte web/móvil y habilite evidencia, auditoría, reportes e interoperabilidad sin comprometer el núcleo operacional.

## 1.4 Objetivos técnicos
- Seis microservicios delimitados.
- Inventario + Movimientos en único núcleo ACID.
- Clean Architecture feature-first en Web/Mobile.
- JWT RS256, refresh rotativo, TOTP y RBAC.
- Idempotencia, locking y Transactional Outbox.
- Flyway/OpenAPI/ADR versionados.
- CI/CD, observabilidad, backup/restore.
- Docker Compose baseline y GKE objetivo.

## 1.5 Alcance
Dentro: usuarios/roles, catálogo y proveedores, multiubicación, movimientos, lotes/series, autorizaciones, evidencias, reportes, auditoría, móvil, BI read-only y continuidad. Fuera: ERP/CMMS completo, facturación integral, movimientos offline, multi-región y Kubernetes obligatorio.

## 1.6 Equipo y responsabilidades

| Rol | Responsabilidad |
|---|---|
| Líder / Arquitecto | Gobierno arquitectónico, ADR, integración multirepo, calidad y documentación. |
| Backend / Datos | Spring Boot, PostgreSQL, Flyway, ACID, OpenAPI, eventos. |
| Frontend Web / UX | React/TS, MUI, Figma, accesibilidad, pruebas web. |
| Mobile / QA / DevOps | Expo, QA, CI/CD, Docker/GCP, observabilidad. |
| Seguridad de Información / TI | Permisos, auditoría, secretos, alertas, continuidad. |

## 1.7 Metodología y cronograma
Scrum con cuatro sprints: S1 base/CRUD/contratos; S2 integración funcional; S3 núcleo operativo; S4 calidad/interoperabilidad/observabilidad/cierre. La documentación evoluciona con cada incremento.

# 2. Ingeniería de requisitos, CUN/CUS y trazabilidad

## 2.1 Política de IDs
Se conservan RF-01..22 y RNF-01..13 del preliminar para no romper Jira/HU/evidencias. Nuevos requisitos se agregan desde RF-23 y RNF-14. Las HU existentes no se renumeran.

## 2.2 Requerimientos funcionales

| ID | Módulo | Especificación | HU | CUS |
|---|---|---|---|---|
| RF-01 | Autenticación | Inicio de sesión y segundo factor cuando corresponda. | US-01 | CUS-01 |
| RF-02 | Usuarios | Listar, registrar, actualizar y desactivar usuarios. | US-02 | CUS-02 |
| RF-03 | Roles y permisos | RBAC dinámico Rol-Permiso. | US-03 | CUS-03 |
| RF-04 | Categorías | Gestionar categorías industriales. | US-04 | CUS-04 |
| RF-05 | Productos | Gestionar catálogo y atributos técnicos. | US-05 | CUS-05 |
| RF-06 | Inventario | Consultar disponibilidad consolidada y por ubicación. | US-06 | CUS-06 |
| RF-07 | Entradas | Registrar ingresos, ubicación, costo, trazabilidad y sustento. | US-07 | CUS-07 |
| RF-08 | Salidas | Registrar salidas validando existencia y autorizaciones. | US-08 | CUS-08 |
| RF-09 | Actualización de stock | Actualizar stock atómicamente tras movimiento válido. | US-09 | CUS-07/CUS-08 |
| RF-10 | Historial | Consultar movimientos inmutables. | US-10 | CUS-11 |
| RF-11 | Stock mínimo | Configurar umbral por producto. | US-11 | CUS-12 |
| RF-12 | Alertas de stock | Identificar stock bajo/sin stock. | US-12 | CUS-30 |
| RF-13 | Dashboard | Visualizar salud operativa. | US-13 | CUS-13 |
| RF-14 | Consulta móvil | Consultar inventario desde móvil. | US-14 | CUS-14 |
| RF-15 | Movimientos móviles | Registrar movimientos autorizados desde móvil. | US-15 | CUS-15 |
| RF-16 | Búsqueda y filtros | Filtrar productos, activos, lotes y movimientos. | US-16 | CUS-16 |
| RF-17 | Reportes | Generar reportes operativos/auditables. | US-17 | CUS-17 |
| RF-18 | Auditoría | Registrar/consultar eventos funcionales. | US-18 | CUS-18 |
| RF-19 | Interoperabilidad | Exponer información a consumidores externos controlados. | US-19 | CUS-19 |
| RF-20 | Indicadores | Visualizar KPIs. | US-20 | CUS-20 |
| RF-21 | Métricas y logs | Métricas/logs técnicos. | US-21 | CUS-21 |
| RF-22 | Recuperación | Health checks, respaldo y recuperación. | US-22 | CUS-22 |
| RF-23 | Unidades y conversiones | Unidad de almacén/base y conversiones múltiples por producto. | US-23 | CUS-23 |
| RF-24 | Ubicaciones | Jerarquía flexible y stock multiubicación. | US-24 | CUS-24 |
| RF-25 | Transferencias | Trasladar stock sin alterar total. | US-25 | CUS-09 |
| RF-26 | Ajustes | Ajustes +/- con motivo, autorización y evidencia. | US-26 | CUS-10 |
| RF-27 | Lotes/coladas/vencimientos | Trazabilidad agrupada y caducidad. | US-27 | CUS-25 |
| RF-28 | Series y activos | Maquinaria individual y repuesto serializable. | US-28 | CUS-25 |
| RF-29 | Autorizaciones | Autorización condicional de movimientos sensibles. | US-29 | CUS-27 |
| RF-30 | Evidencias | Asociar PDF/JPG/PNG a movimiento, activo, ajuste o reporte con integridad documental. | US-30 | CUS-26 |
| RF-31 | Multimoneda | Costo de entrada PEN/otra moneda y TC histórico. | US-31 | CUS-29 |
| RF-32 | Notificaciones in-app | Alertas relevantes a usuarios. | US-32 | CUS-30 |
| RF-33 | Conteos físicos | Conteo, diferencias y exactitud. | US-33 | CUS-28 |
| RF-34 | Exportación | PDF/XLSX/CSV. | US-34 | CUS-17 |
| RF-35 | Proveedores | Maestro básico y vínculo trazable con entradas externas. | US-35 | CUS-31/CUS-07 |

## 2.3 Requerimientos no funcionales

| ID | Categoría | Criterio | Sprint |
|---|---|---|---|
| RNF-01 | Credenciales | Argon2id; nunca texto plano. | Sprint 2 |
| RNF-02 | Autorización | Backend protege toda función por roles/permisos. | Sprint 2 |
| RNF-03 | Config segura | Secretos fuera del código. | Sprint 2-4 |
| RNF-04 | Comunicación | HTTPS externo; servicios internos no públicos. | Sprint 3-4 |
| RNF-05 | Integridad | Nunca stock negativo ni confirmación parcial. | Sprint 3 |
| RNF-06 | Trazabilidad | Actor, fecha, ubicación, producto, cantidad, lote/serie y sustento. | Sprint 3 |
| RNF-07 | Interoperabilidad | Contratos versionados y degradación controlada. | Sprint 4 |
| RNF-08 | Rendimiento | Lectura P95<=500ms; comando<=1000ms; dashboard<=2000ms a 50 usuarios. | Sprint 4 |
| RNF-09 | Disponibilidad | SLO objetivo >=99.5% mensual, sin mantenimiento programado. | Sprint 4 |
| RNF-10 | Recuperación | RPO<=24h, RTO<=4h, backup diario y restore test. | Sprint 4 |
| RNF-11 | Mantenibilidad | SOLID, bounded contexts y Clean Architecture. | Sprint 1-4 |
| RNF-12 | Usabilidad | Loading/empty/error y mensajes comprensibles. | Sprint 1-4 |
| RNF-13 | Compatibilidad | Chrome/Edge/Firefox últimas 2 versiones; Expo soportado. | Sprint 4 |
| RNF-14 | Concurrencia | @Transactional + FOR UPDATE + constraints; READ COMMITTED. | Sprint 3-4 |
| RNF-15 | Idempotencia | Idempotency-Key en comandos críticos. | Sprint 3-4 |
| RNF-16 | Observabilidad | Correlation ID, métricas, logs y trazas DEV/QA. | Sprint 4 |
| RNF-17 | Integridad documental | Object storage privado, SHA-256, MIME/magic bytes. | Sprint 4 |
| RNF-18 | Portabilidad | Docker Compose baseline; GKE objetivo. | Sprint 3-4 |
| RNF-19 | Accesibilidad | WCAG 2.1 AA como referencia baseline. | Sprint 1-4 |
| RNF-20 | Calidad | Cobertura y pruebas ACID/concurrencia. | Sprint 2-4 |

## 2.4 Diferencia CUN vs CUS

| Criterio | CUN | CUS |
|---|---|---|
| Enfoque | Proceso empresarial. | Interacción actor-sistema. |
| Pregunta | ¿Cómo opera el negocio? | ¿Qué hace SIGA? |
| Ejemplo | Despachar recurso. | Registrar salida + autorizar + evidencia. |
| Diagrama | BPMN/actividad. | Use Case/actividad/secuencia/estado. |

## 2.5 Catálogo de CUS

| ID | Caso de uso | Actor |
|---|---|---|
| CUS-01 | Autenticarse y validar MFA | Usuario |
| CUS-02 | Gestionar usuarios | Administrador |
| CUS-03 | Gestionar roles y permisos | Administrador |
| CUS-04 | Gestionar categorías | Administrador |
| CUS-05 | Gestionar productos | Administrador/Encargado |
| CUS-06 | Consultar inventario | Autorizado |
| CUS-07 | Registrar entrada | Encargado |
| CUS-08 | Registrar salida | Encargado |
| CUS-09 | Transferir existencia | Encargado/Supervisor |
| CUS-10 | Ajustar inventario | Supervisor/Admin |
| CUS-11 | Consultar historial | Autorizado |
| CUS-12 | Configurar stock mínimo | Administrador |
| CUS-13 | Consultar dashboard | Admin/Supervisor |
| CUS-14 | Consultar inventario móvil | Usuario móvil |
| CUS-15 | Registrar movimiento móvil | Móvil autorizado |
| CUS-16 | Buscar y filtrar | Autorizado |
| CUS-17 | Generar/exportar reporte | Autorizado |
| CUS-18 | Consultar auditoría | Admin/Seguridad TI |
| CUS-19 | Consumir integración analítica | BI/Analista |
| CUS-20 | Consultar indicadores | Admin/Supervisor |
| CUS-21 | Monitorear plataforma | DevOps/TI |
| CUS-22 | Ejecutar recuperación | DevOps/TI |
| CUS-23 | Gestionar unidades y conversiones | Administrador |
| CUS-24 | Gestionar ubicaciones | Admin/Supervisor |
| CUS-25 | Gestionar lotes, series y activos | Encargado/Supervisor |
| CUS-26 | Adjuntar/consultar evidencia | Autorizado |
| CUS-27 | Autorizar movimiento sensible | Autorizador |
| CUS-28 | Registrar conteo físico | Supervisor/Encargado |
| CUS-29 | Registrar tipo de cambio | Autorizado |
| CUS-30 | Consultar notificaciones | Autorizado |
| CUS-31 | Gestionar proveedores | Administrador/Usuario de catálogo autorizado |

## 2.6 CUN base

| ID | Proceso | CUS |
|---|---|---|
| CUN-01 | Recepcionar y almacenar | CUS-07,24,25,26,31 |
| CUN-02 | Despachar/consumir | CUS-08,27,26 |
| CUN-03 | Transferir inventario | CUS-09,24 |
| CUN-04 | Regularizar inventario | CUS-10,28,27 |
| CUN-05 | Controlar trazabilidad/activos | CUS-06,11,25 |
| CUN-06 | Supervisar/auditar | CUS-13,17,18,20 |
| CUN-07 | Explotar/interoperar | CUS-19,29,30 |

## 2.7 Plantilla de CUS
ID, objetivo, actores, disparador, pre/postcondiciones, flujo básico, alternativos, excepciones, reglas, permisos, datos, estados, endpoints, eventos, entidades, RF/HU/RNF y pruebas. Los CUS críticos incorporan actividad, secuencia, estados y explicación transaccional.

### 2.7.1 CUS-08 Registrar salida — referencia
Precondiciones: autenticación, permiso MOVEMENT_CREATE, producto/ubicación válidos y trazabilidad requerida. Flujo: borrador multi-detalle → validación → sensibilidad → autorización si aplica → confirmación → locks → revalidación → costo → stock/movimiento/outbox → commit. Errores: 409 stock/estado/idempotencia, 403 permiso. Nunca queda stock sin movimiento coherente.

# 3. Arquitectura del sistema

## 3.1 Visión
SIGA adopta seis microservicios para separar responsabilidades y facilitar pruebas/SOLID. Se evita fragmentación excesiva: Inventory y Movement permanecen juntos para localizar la transacción crítica y evitar Saga/distributed transaction en stock.

## 3.2 Principios
1) PostgreSQL autoridad. 2) Ownership exclusivo de schema. 3) Sin escritura SQL cross-schema. 4) REST síncrono + RabbitMQ selectivo. 5) Outbox. 6) Redis efímero. 7) Object storage para archivos. 8) Gateway sin lógica de negocio. 9) Contratos versionados. 10) Compose baseline/K8s objetivo.

## 3.3 Microservicios definitivos

| Código | Servicio | Contexto | Responsabilidad |
|---|---|---|---|
| MS-IAM | identity-service | Identidad y acceso | Usuarios, roles, permisos, JWT RS256, refresh token, MFA/TOTP y revocación. |
| MS-CAT | catalog-service | Catálogo maestro | Categorías, productos, proveedores, UoM, conversiones, trazabilidad configurable y atributos técnicos. |
| MS-INV | inventory-service | Núcleo transaccional | Existencias, ubicaciones, lotes, activos, movimientos, autorizaciones, ajustes, costo, conteos e idempotencia. |
| MS-EVI | evidence-service | Evidencias | Metadatos, validación, hash y MinIO/GCS. |
| MS-AUD | audit-notification-service | Auditoría y notificaciones | Auditoría funcional, consumidores RabbitMQ y notificaciones in-app. |
| MS-REP | reporting-analytics-service | Reportes y analítica | Dashboard, reportes, KPIs, exportaciones y preparación ETL/BI. |

### 3.3.1 Frontera crítica MS-INV
Entrada, salida, transferencia, ajuste, costo y outbox se confirman en una transacción PostgreSQL local. No se crea movement-service separado. ADR-003.

## 3.4 Estrategia multirepositorio

| Repositorio | Contenido | Artefacto |
|---|---|---|
| siga-identity-service | MS-IAM + Flyway/OpenAPI/tests | Imagen identity |
| siga-catalog-service | MS-CAT | Imagen catalog |
| siga-inventory-service | MS-INV + pruebas ACID | Imagen inventory |
| siga-evidence-service | MS-EVI | Imagen evidence |
| siga-audit-notification-service | MS-AUD | Imagen audit-notification |
| siga-reporting-analytics-service | MS-REP | Imagen reporting |
| siga-web | React/TS/Vite | Bundle/imagen web |
| siga-mobile | Expo | App Expo |
| siga-infrastructure | Compose/Nginx/monitoring/K8s | Infra |
| siga-documentation | Manual/diagramas/ADR/matrices | Docs |

## 3.5 C4
Se entregan Context, Container Docker/GCP, Container Kubernetes objetivo y Component para Inventory e Identity. C4 se expresa con PlantUML puro para evitar includes remotos.

# 4. Diseño de dominio y UML

## 4.1 Bounded contexts

| Contexto | Conceptos persistentes / de dominio | Responsabilidad |
|---|---|---|
| IAM | Usuario, Rol, Permiso, asignaciones, RefreshToken, Outbox | Identidad/autorización |
| Catálogo | Categoría, Producto, Proveedor, UoM, Conversión por producto, Outbox | Maestros |
| Inventario | SupplierRef, ProductRef, ConversionRef, Existencia, Ubicación, Lote, Activo, Movimiento, Detalle, Autorización, Conteo, Idempotencia, ProcessedEvent, Outbox | Verdad operacional |
| Evidencia | EvidenceMetadata, Outbox | Metadata/archivos |
| Audit/Notification | AuditEvent, Notification, ProcessedEvent | Auditoría/notificación |
| Reporting | Product/Inventory/Movement Projection, KPI, ReportJob, ProcessedEvent, ExportCheckpoint | Lectura/BI |

## 4.2 Producto vs Activo
Producto describe el tipo; Activo es una unidad física serializada. Relación lógica 1:N. Maquinaria requiere código/serie; un repuesto puede serializarse condicionalmente. **La ubicación actual no se duplica en Activo**: `inventory.stock_balance` es la única autoridad de cantidad, costo y ubicación; un activo serializado solo puede tener cantidad efectiva 0/1 y una única existencia positiva.

## 4.3 Lotes y existencias
Un lote pertenece a un `product_ref` y puede existir en varias ubicaciones. Existencia = producto + ubicación + lote opcional + activo opcional + cantidad/costo. Las FK locales compuestas `(lot_id, product_id)` y `(asset_id, product_id)` evitan asociar trazabilidad de otro producto. Las reglas `requires_lot`, `requires_heat_number`, `requires_serial` y `requires_expiry` se evalúan desde la proyección local de Catálogo.

## 4.4 Ubicación jerárquica
Entidad recursiva `location(parent_id)`. Tipos: ALMACEN, PATIO, ZONA, PASILLO, RACK, NIVEL, POSICION, TALLER, RECEPCION, CUARENTENA, DESPACHO.

```text
ALM-01
└── ZONA-A
    └── PAS-01
        └── RACK-03
            └── NIVEL-02
                └── POS-04
PATIO-01
└── ZONA-MAQ
    └── POS-M08
```

## 4.5 Movimiento multi-detalle
Una cabecera puede contener múltiples líneas. Cada detalle conserva **snapshot histórico** de `entered_quantity`, `unit_code`, `conversion_factor` y `stock_quantity`, además de ubicaciones, lote/activo y costos. Esto permite reproducir un movimiento aunque posteriormente cambie una conversión del catálogo.

Los actores se separan en `registered_by_user_id` y `requested_by_user_id`; el centro de costo se conserva como `cost_center_code` + `cost_center_name_snapshot`. En recepciones externas, la cabecera conserva `supplier_id`, `supplier_name_snapshot` y `supplier_tax_id_snapshot`. La autorización vive exclusivamente en `movement_authorization` y la idempotencia en `idempotency_record`, evitando dos fuentes de verdad.

## 4.6 Máquina de estados

| Estado interno | Etiqueta UI | Acción/condición | Destino | Stock |
|---|---|---|---|---|
| DRAFT | BORRADOR | submit sensible o actor sin `MOVEMENT_AUTHORIZE` | PENDING_AUTHORIZATION | Sin efecto |
| DRAFT | BORRADOR | confirm por actor con `MOVEMENT_AUTHORIZE`, no sensible + válido | CONFIRMED | Atómico |
| DRAFT | BORRADOR | cancel antes de confirmar | CANCELLED | Sin efecto |
| PENDING_AUTHORIZATION | PENDIENTE_AUTORIZACION | authorize + permiso + step-up + checker distinto del maker | AUTHORIZED | Sin efecto |
| PENDING_AUTHORIZATION | PENDIENTE_AUTORIZACION | reject + permiso + step-up + checker distinto del maker | REJECTED | Sin efecto |
| PENDING_AUTHORIZATION | PENDIENTE_AUTORIZACION | cancel según política | CANCELLED | Sin efecto |
| AUTHORIZED | AUTORIZADO | confirm + revalidación | CONFIRMED | Atómico |
| AUTHORIZED | AUTORIZADO | cancel antes del commit | CANCELLED | Sin efecto |
| CONFIRMED | CONFIRMADO | corregir | Movimiento compensatorio | Nuevo efecto trazable |

`CONFIRMED` es inmutable. `CANCELLED` solo aplica antes de la confirmación; no se usa para borrar historia. Los CUS pueden emplear las etiquetas españolas, mientras BD/OpenAPI usan los códigos internos anteriores.

## 4.7 Diagramas
El paquete contiene dominio general + clases por bounded context + paquetes backend/web/mobile + estados + secuencias. Para datos se mantienen tres niveles: **DER-01 conceptual global**, **DER-02 lógico global**, **DER-03 físico por schemas**, y se agregan **DER-04..DER-09 físicos por bounded context**. El diagrama global evita saturación; los físicos específicos contienen columnas, PK/FK locales, referencias externas e invariantes.
# 5. Arquitectura de datos y persistencia

## 5.1 PostgreSQL y schemas
PostgreSQL se selecciona por ACID, locking, `NUMERIC`, `TIMESTAMPTZ`, índices y JSONB. Una instancia académica contiene `iam`, `catalog`, `inventory`, `evidence`, `audit`, `analytics`. Cada servicio solo escribe su schema.

```text
PostgreSQL
├── iam       <- identity-service                  (7 tablas)
├── catalog   <- catalog-service                   (6 tablas)
├── inventory <- inventory-service                (15 tablas)
├── evidence  <- evidence-service                  (2 tablas)
├── audit     <- audit-notification-service        (3 tablas)
└── analytics <- reporting-analytics-service       (7 tablas)
```

El modelo físico canónico contiene **40 tablas**. No se crean schemas compartidos para Outbox o `processed_event`: cada productor/consumidor mantiene sus tablas dentro de su ownership.

## 5.2 JSONB
Solo atributos técnicos/metadatos extensibles y payloads de integración. Prohibido para stock, costo, cantidad, serie, lote, ubicación, vencimiento, movimiento, autorización y relaciones críticas.

## 5.3 Identificadores
PK UUID + códigos humanos independientes (`SKU`, `MOV-YYYY-NNNNN`, `MAQ-NNNN`). `movement_code` lo genera Inventory al persistir el borrador: toma una secuencia PostgreSQL global propia, usa el año UTC de creación y formatea el correlativo con ancho mínimo de cinco dígitos. La secuencia no se reinicia por año, admite huecos por rollback y nunca se calcula con `MAX()+1`; el `UNIQUE` de la tabla es la defensa final. Los UUID que referencian otro bounded context se conservan como columnas sin FK cross-schema.

## 5.4 Convenciones
`snake_case`; UUID; `TIMESTAMPTZ` UTC; `NUMERIC(18,6)` para cantidades/costos; ISO 4217; `active` para soft delete; `version` para optimistic locking de maestros/proyecciones cuando corresponda. `FOR UPDATE` continúa en stock.

## 5.5 ACID y locking

```text
BEGIN;
1. Validar movimiento/estado/idempotencia.
2. Cargar detalles y reglas desde product_ref/conversion_ref y, cuando aplique, supplier_ref locales.
3. SELECT stock ... FOR UPDATE.
4. Revalidar stock/lote/activo/ubicación/trazabilidad.
5. Calcular conversiones y costo.
6. UPDATE stock_balance.
7. Persistir movimiento/detalles/autorización aplicable.
8. INSERT inventory.outbox_event.
COMMIT;
Cualquier excepción => ROLLBACK.
```

Spring usa `@Transactional`; READ COMMITTED base. Locks solo sobre filas afectadas y `CHECK(quantity>=0)` como segunda barrera. No se usa SERIALIZABLE global ni llamada REST a Catalog dentro del commit crítico.

## 5.6 Concurrencia
Stock=10; salidas 8 y 7 concurrentes. Una bloquea/commit; la otra reevalúa stock=2 y recibe 409. La UI nunca es autoridad. Para activos serializados, la BD además impide más de una existencia positiva del mismo `asset_id`.

## 5.7 Soft delete e inmutabilidad
Usuarios/categorías/productos/proveedores/ubicaciones/UoM se desactivan. Movimientos `CONFIRMED`, auditoría y costos históricos no se eliminan. `stock_balance` es la única fuente de ubicación actual de un activo; `asset` no duplica ese dato.

## 5.8 Multimoneda
PEN base; entradas pueden registrar USD/EUR/otra moneda con `original_currency`, `original_unit_cost`, `exchange_rate`, `exchange_rate_date`, `exchange_rate_source`, `base_unit_cost_pen` y `applied_avg_cost_pen`. Se conserva la tasa histórica y su fuente. `ExchangeRatePort` mantiene BCRP como referencia futura y carga manual autorizada como fallback MVP.

## 5.9 Flyway
Migraciones por servicio en `db/migration`; jamás modifican schema ajeno. `V001__...`; cambios delicados con expand/contract. El `physical_model.sql` es modelo consolidado de documentación; cada repo extrae de él las migraciones de su ownership.

## 5.10 Modelo canónico, DER y diccionario
La cadena de coherencia es:

```text
Manual/ADR y reglas aprobadas
        ↓
database/logical_model.md
        ↓
database/physical_model.sql
        ↓
database/dictionary.md
        ↓
DER-01..DER-09 + UML + OpenAPI + tests
```

Las FK sólidas existen solo dentro del mismo schema. Las relaciones externas se representan en DER conceptual/lógico como UUID/evento/proyección, pero **no se convierten en FK cross-schema**.

## 5.11 Proyecciones de Catálogo en Inventory
`inventory.product_ref` contiene SKU, tipo, unidades, stock mínimo y flags de trazabilidad necesarios para confirmar movimientos sin dependencia REST. `inventory.product_unit_conversion_ref` conserva conversiones aplicables. `inventory.supplier_ref` conserva la referencia mínima de proveedor requerida para validar recepciones externas. Estas proyecciones se actualizan con eventos de Catalog (`ProductCreated/Updated` y `SupplierCreated/Updated/Disabled`); `inventory.processed_event` hace idempotente el consumidor. `ProductCreated v1` transporta códigos de UoM, no sus IDs internos, y usa la versión del producto como `source_version` de ambas proyecciones. `ProductUpdated v1` transporta un snapshot completo: `product.version` alimenta `source_version`, el `eventId` alimenta `analytics.product_projection.source_event_id` y el consumidor reemplaza transaccionalmente el conjunto de conversiones solo para una versión fuente más nueva.

Estas tablas **no son un segundo maestro**: Catalog sigue siendo autoridad y `source_version` permite detectar/reconciliar desactualización.

## 5.12 Invariantes físicas prioritarias
- FK local de producto desde lote, activo, stock, detalle y conteo hacia `inventory.product_ref`.
- FK compuesta lote/activo + producto para impedir trazabilidad cruzada.
- Activo serializado: cantidad 0/1 y una sola existencia positiva.
- `lot_number` único por producto cuando exista.
- Estados/tipos mediante `CHECK`.
- Cantidades de detalle siempre positivas; el sentido depende de `movement_type`.
- ENTRY exige destino, EXIT origen, TRANSFER ambos distintos; estas reglas multiatributo/tipo se refuerzan en dominio + pruebas de integración.
- Conteo físico almacena `difference_quantity`; el ajuste posterior es un movimiento separado.


# 6. Diseño backend y contratos API

## 6.1 Stack
Java 21, Spring Boot 3.x, Web, Validation, Security, Data JPA, PostgreSQL, Flyway, springdoc-openapi, Actuator/Micrometer, JUnit5, Mockito, AssertJ, Testcontainers; Spring AMQP donde aplica.

## 6.2 Estructura por servicio

```text
src/main/java/com/siga/<service>/
├── domain/{model,repository,service,event}
├── application/{usecase,command,query,port}
├── infrastructure/{persistence,messaging,security,external}
└── interfaces/rest/{controller,dto,mapper}
```

El dominio no depende de framework. Se evita multiplicar capas/clases sin valor; SOLID guía, no sobreingeniería.

## 6.3 Gateway
Spring Cloud Gateway: routing, CORS, rate limit, correlation ID, tamaño request y validación preliminar JWT. La autorización de dominio se repite en cada servicio. Docker Compose usa DNS interno, sin Eureka. Kubernetes usa Service/DNS.

## 6.4 REST
Versionado /api/v1. Recursos en sustantivos; comandos de dominio explícitos como /movements/{id}/confirm. Paginación page/size/sort y filtros server-side.

## 6.5 Endpoints principales

| Método | Ruta | Servicio | Uso |
|---|---|---|---|
| POST | /api/v1/auth/login | IAM | Login/MFA challenge |
| POST | /api/v1/auth/mfa/verify | IAM | Verificar TOTP |
| POST | /api/v1/auth/refresh | IAM | Rotar refresh |
| GET/POST | /api/v1/users | IAM | Lista paginada y alta de usuarios |
| GET/PATCH | /api/v1/users/{id} | IAM | Detalle y actualización/desactivación |
| PUT | /api/v1/users/{id}/roles | IAM | Reemplazo completo de roles |
| GET/POST | /api/v1/roles | IAM | Lista y alta de roles |
| PUT | /api/v1/roles/{id}/permissions | IAM | Reemplazo completo de permisos |
| GET | /api/v1/permissions | IAM | Catálogo read-only por código |
| GET/POST | /api/v1/products | CAT | Consulta paginada y alta de producto |
| GET/PUT | /api/v1/products/{id} | CAT | Consulta o reemplazo completo con `expectedVersion`; desactivación/reactivación lógica y conversiones incluidas |
| GET/POST | /api/v1/categories | CAT | GET: arreglo directo `{id,code,name,categoryType,active}`, activos/inactivos, `code ASC`, sin filtros/paginación |
| GET/POST | /api/v1/units | CAT | GET: arreglo directo `{id,code,name,symbol,dimension,active}`, activos/inactivos, `code ASC`, sin filtros/paginación |
| GET/POST | /api/v1/suppliers | CAT | Proveedores |
| GET/PUT | /api/v1/suppliers/{id} | CAT | Consulta/actualización de proveedor |
| GET | /api/v1/inventory | INV | Stock |
| GET/POST | /api/v1/locations | INV | Lista filtrada o alta de ubicación |
| GET/PUT | /api/v1/locations/{id} | INV | Detalle o reemplazo de campos editables |
| POST | /api/v1/locations/{id}/deactivate, /reactivate | INV | Lifecycle lógico con `expectedVersion` |
| GET | /api/v1/lots | INV | Lotes/coladas/vencimientos |
| GET | /api/v1/assets | INV | Activos serializados |
| POST | /api/v1/movements | INV | Borrador multi-detalle |
| POST | /api/v1/movements/{id}/submit | INV | Evaluar autorización |
| POST | /api/v1/movements/{id}/authorize | INV | Autorizar |
| POST | /api/v1/movements/{id}/confirm | INV | Commit idempotente |
| POST | /api/v1/movements/{id}/reject | INV | Rechazar |
| POST | /api/v1/movements/{id}/cancel | INV | Cancelar antes de confirmar |
| GET/POST | /api/v1/counts[/{id}] | INV | Lista, crea y consulta conteo físico |
| PUT/POST | /api/v1/counts/{id}/lines[/{lineId}] | INV | Captura observaciones del conteo |
| POST | /api/v1/counts/{id}/close, /cancel | INV | Cierra o cancela sin mutar stock |
| POST | /api/v1/evidences | EVI | Upload multipart |
| GET | /api/v1/evidences | EVI | Lista paginada scoped por owner |
| GET | /api/v1/evidences/{id} | EVI | Metadata autorizada |
| GET | /api/v1/evidences/{id}/content | EVI | Stream privado autorizado |
| GET | /api/v1/audit-events | AUD | Auditoría |
| GET | /api/v1/notifications | AUD | Notificaciones personales paginadas |
| GET | /api/v1/notifications/unread-count | AUD | Conteo personal no leído |
| POST | /api/v1/notifications/{id}/read | AUD | Marcado idempotente como leído |
| GET | /api/v1/dashboard | REP | Dashboard operacional MVP |
| GET | /api/v1/reports/movements | REP | Movimientos confirmados |
| GET | /api/v1/reports/inventory-valuation | REP | Valorización actual proyectada |
| GET | /api/v1/reports/adjustments | REP | Ajustes confirmados |
| POST | /api/v1/admin/reconciliation | REP | Bootstrap/reconciliación de proyecciones por APIs canónicas |

## 6.6 OpenAPI
Un YAML por microservicio, consolidado en versión 1.1. Los contratos incluyen DTOs de IAM/RBAC, conversiones múltiples, movimientos con snapshots, conteos, Evidence con owner genérico, filtros de auditoría y read models/report jobs. Frontend puede generar tipos; `generated` no se edita. Cambios de contrato actualizan tests/consumidores. Swagger UI solo DEV/QA o restringido.

## 6.7 Problem Details
application/problem+json: type,title,status,code,detail,instance,correlationId. 400 validación, 401,403,404,409 dominio/idempotencia,422 opcional,429,500,503. Sin stack traces.

## 6.8 Idempotencia
Comandos críticos aceptan Idempotency-Key UUID. Se persiste request hash + respuesta. Misma key/payload devuelve resultado previo sin segundo efecto; misma key/payload distinto =>409. Retención/limpieza configurables.

# 7. Seguridad e identidad

## 7.1 JWT RS256
MS-IAM firma con clave privada; Gateway/servicios validan pública/JWKS. Access 30 min; refresh 7 días con rotación y revocación. Usuario desactivado no renueva. El access JWT usa `sub` como UUID estable de `iam.user_account.id`, `permissions` como permisos efectivos, `amr` como métodos de autenticación y `auth_time` como epoch-seconds de autenticación MFA cuando exista; mantiene issuer y audiencia configurados. Los servicios validan firma, issuer, audiencia, expiración y `sub` antes de derivar el actor autenticado. El actor registrador/autorizador es server-controlled y nunca se acepta desde el body.

## 7.2 TOTP/step-up
TOTP RFC 6238: 30s, ventana ±1, 5 intentos baseline. MFA obligatorio para privilegiados y configurable. Para autorizar un movimiento sensible, el access JWT es la evidencia de step-up: `amr` debe incluir `otp` y `auth_time` no puede superar 300 segundos. IAM valida TOTP; Inventory, tras la validación normal Resource Server, comprueba esos claims, `MOVEMENT_AUTHORIZE` y el estado del movimiento.

Las mutaciones administrativas de Identity —crear o actualizar usuario, reemplazar sus roles, crear rol y reemplazar sus permisos— también exigen `auth_time` de máximo 300 segundos. Las lecturas administrativas no exigen step-up. No existe token ni endpoint step-up separado y el refresh conserva el instante MFA original, por lo que el administrador reautentica mediante el flujo MFA normal. El rechazo por step-up ausente/obsoleto conserva `403 AUTH_FORBIDDEN`; `STEP_UP_ERROR_AMBIGUITY_DEBT` registra que el cliente no puede distinguirlo con certeza de otro rechazo de autorización. No se persisten JWT, OTP ni secretos.

## 7.3 Argon2id
Principal para contraseñas. Parámetros se calibran por entorno. Fallback BCrypt solo por incompatibilidad. Política baseline: mínimo 12 caracteres, passphrases permitidas, sin rotación arbitraria periódica.

## 7.4 RBAC
Usuario N:M Rol N:M Permiso. Ejemplos INVENTORY_READ, INVENTORY_COUNT, MOVEMENT_CREATE, MOVEMENT_AUTHORIZE, INVENTORY_ADJUST, CATALOG_READ, PRODUCT_WRITE, SUPPLIER_MANAGE, AUDIT_READ, REPORT_READ, ANALYTICS_READ, USER_MANAGE, ROLE_MANAGE. `ENCARGADO` recibe el mínimo operativo `INVENTORY_READ`, `MOVEMENT_CREATE`, `CATALOG_READ` e `INVENTORY_COUNT`; no recibe autorización ni administración. `SUPERVISOR` recibe `INVENTORY_READ`, `MOVEMENT_AUTHORIZE`, `CATALOG_READ`, `REPORT_READ` e `INVENTORY_COUNT`. `ADMIN` recibe también `INVENTORY_COUNT`. `ANALYTICS_READ` es una capacidad separada reservada para integración BI y solo se asigna a `ADMIN` en el MVP; su incorporación operativa requiere una migración versionada posterior.

## 7.5 Baseline configurable

| Control | Valor |
|---|---|
| Access | 30 min |
| Refresh | 7 días |
| TOTP | 30 s ±1 |
| Intentos login | 5 |
| Bloqueo | 15 min |
| Intentos OTP | 5 |
| Rate limit login | 10 req/min/IP baseline |
| MFA | Privilegiados + step-up sensibles |

## 7.6 Web tokens
Access en memoria; refresh HttpOnly/Secure/SameSite. CORS explícito. CSRF evaluado para endpoints de cookie.

## 7.7 Mobile tokens
Access en memoria; refresh Expo SecureStore. No AsyncStorage para secretos. Logout revoca y limpia.

## 7.8 Archivos
Extensión, MIME, magic bytes, size, SHA-256, object key interno; storage privado. ClamAV queda hardening futuro.

## 7.9 Auditoría vs logging
Auditoría = quién/qué/cuándo/resultado. Logging = diagnóstico técnico. Nunca contraseña/TOTP/JWT completo/refresh/secreto en logs. Seguridad/TI revisa permisos, alertas, secretos y continuidad.


# 8. Diseño del Frontend Web

## 8.1 Stack
React 19 + TypeScript + Vite; MUI Core/Icons/Data Grid Community; React Router; TanStack Query; Zustand; Axios encapsulado; React Hook Form + Zod; Recharts; Vitest/RTL/MSW; Playwright. No se usa Next.js porque SSR/SEO no es requisito de una SPA administrativa.

## 8.2 Clean Architecture + feature-first

```text
src/
├── app/                    # bootstrap/providers/router
├── features/
│   ├── auth/{domain,application,infrastructure,presentation}
│   ├── catalog/{...}
│   ├── inventory/{...}
│   ├── movements/{...}
│   ├── evidence/{...}
│   ├── reports/{...}
│   └── audit/{...}
├── shared/{ui,api,errors,hooks,utils,types}
└── generated/              # tipos OpenAPI, no editar
```

Presentation→Application→Domain; Infrastructure implementa puertos. Domain no importa React/Axios/MUI. Feature-first reduce conflictos y facilita reparto de trabajo.

## 8.3 TanStack Query + Zustand
TanStack Query administra server state, cache/refetch/loading/error de productos/inventario/movimientos/reportes. Zustand solo estado de UI/cliente (sidebar, preferencias, filtros locales). No se duplica server state.

## 8.4 Cliente HTTP
Axios se encapsula en ApiClient/repositories: base URL, Bearer, timeout, Problem Details, refresh coordinado y cancelación. Componentes no llaman Axios directamente. Tipos de transporte pueden generarse desde OpenAPI.

## 8.5 Formularios
React Hook Form + Zod. La validación cliente mejora UX, pero backend revalida todo; stock visible nunca garantiza confirmación.

## 8.6 Rutas

```text
/login /mfa /dashboard
/users /roles
/catalog/categories /catalog/products /catalog/units
/inventory /inventory/:productId /locations /lots /assets
/movements /movements/new /movements/:id /movements/:id/authorize
/adjustments /counts /reports /audit /settings
```

Route guards son UX; backend mantiene autoridad.

## 8.7 MUI, UI Kit y Figma
MUI es baseline conceptual. Foundations: tipografía, spacing, breakpoints, elevación, bordes, estados. Átomos: Button/Input/Select/Chip/Icon/Tooltip. Moléculas: SearchField/FilterBar/StockBadge/ProductSelector/QuantityInput/LocationSelector. Organismos: InventoryTable/MovementForm/DashboardGrid/EvidenceUploader/AuditTable. Templates: Auth/Dashboard/Management/Transaction. Ver Guía Figma.

## 8.8 Estados y errores
Toda vista contempla Loading, Empty, Success, Error, Unauthorized, Forbidden. Estados de negocio usan texto+icono+color. Problem Details se mapea a mensaje; error inesperado muestra correlation ID. ErrorBoundary evita caída total.

## 8.9 Operaciones sensibles
Ajuste, autorización, salida de maquinaria y permisos críticos muestran resumen, confirmación y step-up MFA cuando corresponda. No optimistic update para stock/costos/movimientos/autorizaciones.

## 8.10 Responsive/localización/accesibilidad
Desktop>=1280 prioridad; laptop/tablet>=1024; smartphone web solo adaptación básica porque el cliente operativo es móvil. Chrome/Edge/Firefox últimas 2 versiones. es-PE, America/Lima en presentación, UTC en backend. WCAG 2.1 AA es baseline de referencia.

# 9. Diseño de la aplicación móvil

## 9.1 Stack
React Native + Expo + TypeScript + Expo Router. Misma Clean Architecture feature-first; TanStack Query server state, Zustand UI y SecureStore secretos.

## 9.2 Árbol recomendado

```text
app/
├── (auth)/{login.tsx,otp.tsx}
└── (app)/
    ├── index.tsx
    ├── inventory/
    ├── movements/
    ├── evidences/
    ├── notifications/
    └── profile/
src/
├── features/{auth,inventory,movements,evidence}/
└── shared/
```

## 9.3 Política offline
Consultas pueden usar cache limitada marcada como posiblemente desactualizada. Entrada/salida/transferencia/ajuste/autorización requieren conexión y confirmación backend. No se encolan movimientos offline para preservar ACID y evitar doble consumo.

## 9.4 Alcance MVP
Login, OTP, búsqueda inventario, detalle/stock por ubicación, lotes/series básicos, entrada/salida/transferencia autorizada, evidencia/foto, historial reciente, alertas básicas, perfil/logout. Fuera: administración completa, auditoría completa y dashboard analítico avanzado.

## 9.5 Maquinaria/evidencia
Buscar activo, ver serie/código/estado/ubicación, registrar movimiento y fotografía. Cámara/galería/PDF con preview y validación. Upload inicial multipart al Evidence Service; signed URLs evolución. Límites base: imagen 10MB, PDF 20MB, configurables.

## 9.6 Notificaciones/realtime
MVP in-app personal según `especificaciones/Notifications_MVP.md`. Cada usuario consulta únicamente sus filas mediante el UUID de `JWT sub`; no hay permiso IAM adicional. Web usa polling cada 30 segundos solo autenticado, sin solicitudes solapadas, pausado con la pestaña oculta y con refresco tras marcar leído. SSE queda como evolución. Móvil usa refresh/polling/pull-to-refresh. No se incorpora WebSocket, correo, SMS, push ni motor de reglas en este slice.

# 10. Evidencias, documentos y multimedia

## 10.1 Almacenamiento
No MongoDB/GridFS ni otra NoSQL solo por archivos. La necesidad es object storage: `ObjectStoragePort` con MinIO local/dev y GCS objetivo. PostgreSQL guarda metadata/JSONB opcional; Redis no guarda documentos.

## 10.2 Metadata y propiedad
`evidence.evidence_metadata` conserva: UUID, `owner_type`, `owner_id`, `object_key`, nombre original, MIME, tamaño, SHA-256, proveedor, `uploaded_by_user_id`, estado, timestamps y metadata JSONB opcional.

El contrato MVP admite exclusivamente `owner_type=MOVEMENT`; `owner_id` es el UUID externo de `inventory.movement`, deliberadamente sin FK cross-schema. Un ajuste usa el UUID de su movimiento `ADJUST_POSITIVE` o `ADJUST_NEGATIVE`, no un owner type separado. `ASSET`, `ADJUSTMENT` y `REPORT` quedan reservados para una versión posterior que defina una interfaz canónica de existencia y autorización por ID.

Toda operación exige el permiso grueso `EVIDENCE_READ` o `EVIDENCE_WRITE` y obtiene el actor exclusivamente de `sub` UUID del JWT RS256 validado conforme a ADR-011. El baseline configurable usa issuer `siga-identity`, audience `siga-api` y claim `permissions`; se validan además firma, expiración y `sub`. `uploadedByUserId` nunca se acepta desde el cliente. `OwnerAccessPolicyPort` reenvía el bearer al `GET /api/v1/movements/{ownerId}` de Inventory antes de crear o leer el objeto. Un owner inexistente o no visible se responde `404` para no revelar su existencia; falta del permiso Evidence produce `403`; owner type distinto de `MOVEMENT`, `400`; timeout/5xx de Inventory, `503`. No se usa SQL ni FK cross-schema.

`metadata` es un objeto JSON opcional de máximo 16 KiB UTF-8 serializados y profundidad 5. Admite objetos, arreglos y primitivas JSON; cada objeto admite hasta 50 propiedades, cada arreglo hasta 50 elementos, las claves hasta 64 caracteres y los strings hasta 1024. Se rechaza raíz no objeto, binario/base64, claves o valores destinados a secretos, tokens o credenciales. Los logs registran solo resultado, tamaños e identificadores seguros, nunca el JSON completo.

## 10.3 Organización

```text
siga-evidences/
├── movements/<year>/<movement-id>/<evidence-id>.<ext>
```

Object keys se generan internamente. GCS aplica IAM/versioning/lifecycle/cifrado administrado. MinIO puede versionar en desarrollo.

## 10.4 Reportes persistentes vs temporales
Reportes normales pueden ser temporales. La asociación de reportes oficiales con Evidence queda diferida hasta versionar el owner type `REPORT` y su interfaz de autorización. SEQ-13 describe el flujo objetivo, no una capacidad del MVP Evidence.

## 10.5 Consistencia de evidencia
El owner se valida antes de tocar almacenamiento. El alta de metadata y `evidence.outbox_event` se confirma en una misma transacción local; `EvidenceUploaded` se publica por Outbox. Si storage falla no se escribe metadata. Si el objeto se almacena y luego falla el commit, se intenta borrar exactamente el object key recién generado. Si esa compensación falla, se emite log estructurado y métrica con `correlationId`, `evidenceId` y object key interno como incidente de huérfano, sin exponerlos al cliente. El reconciliador periódico queda diferido y no bloquea el MVP. SHA-256, MIME y magic bytes son controles de integridad, no sustitutos de autorización.

El upload exige `Idempotency-Key` UUID. `evidence.upload_idempotency` reserva de forma durable un `evidence_id` antes del almacenamiento. El fingerprint SHA-256 cubre owner, metadata canónica, nombre sanitizado, MIME validado y hash del archivo; el hash del archivo aislado no es clave idempotente. Misma key y mismo request completado devuelve la respuesta `201` original; misma key con request distinto o aún `PROCESSING` devuelve `409`. Un retry de `FAILED` reutiliza el mismo `evidence_id` y object key y no crea otro objeto, metadata ni Outbox.

La descarga canónica es `GET /api/v1/evidences/{id}/content`: Evidence transmite desde storage privado con MIME validado y `Content-Disposition: attachment` usando nombre sanitizado. No expone `object_key`, URL pública, URL permanente ni URL firmada. Metadata y contenido requieren autorización vigente del owner.


# 11. Eventos, mensajería y notificaciones

## 11.1 RabbitMQ
Elegido sobre Kafka porque SIGA requiere mensajería confiable de volumen moderado, no streaming masivo. Menor complejidad y soporte de exchanges/colas/ACK/retry/DLQ.

## 11.2 Eventos base

| Evento | Productor | Consumidor | Uso |
|---|---|---|---|
| UserCreated/Updated/Disabled | IAM | Diferido | Publicación durable; consumidor Audit central pendiente |
| RoleChanged | IAM | Diferido | Publicación durable; consumidor Audit central pendiente |
| ProductCreated/Updated | CAT | INV, REP | Proyección local |
| SupplierCreated/Updated/Disabled | CAT | INV, REP | Proyección local de proveedor |
| StockBelowMinimum | INV | AUD, REP | Alerta/dashboard |
| StockDepleted | INV | AUD, REP | Alerta crítica |
| MovementConfirmed | INV | AUD (auditoría y notificaciones), REP | Auditoría/notificación personal/analytics |
| SensitiveMovementConfirmed | INV | AUD | Control reforzado |
| InventoryAdjusted | INV | AUD, REP | Control ajuste |
| LotChanged | INV | AUD | Alta, metadata y lifecycle de lote |
| AssetChanged | INV | AUD | Registro, metadata y lifecycle de activo |
| EvidenceUploaded | EVI | AUD | Trazabilidad documental |
| ProductExpiringSoon | INV | AUD, REP | Alerta programada |
| IntegrationFailed | Cualquiera | AUD | Visibilidad operativa |

Identity publica sus eventos existentes mediante `iam.outbox_event` y RabbitMQ, pero el servicio Audit vigente no los consume. `IAM_EVENTS_CENTRAL_AUDIT_CONSUMER` identifica este gap diferido; hasta cerrarlo no se afirma que las mutaciones IAM aparezcan en `audit.audit_event`.

## 11.3 Envelope

```json
{
  "eventId":"uuid","eventType":"MovementConfirmed","schemaVersion":1,
  "aggregateType":"Movement","aggregateId":"uuid","occurredAt":"ISO-8601",
  "correlationId":"uuid","causationId":"uuid","producer":"inventory-service","payload":{}
}
```

`ProductCreated v1` se define en `api/product-created-v1.schema.json`: `eventId` es el UUID de `catalog.outbox_event.id`, `aggregateType=Product`, `aggregateId` es el producto, `schemaVersion=1` y `producer=catalog-service`. `correlationId` es el UUID ya resuelto para el request: Catalog conserva un `X-Correlation-ID` UUID válido o genera uno cuando falta/no es UUID; no introduce conversión o rechazo adicional. `causationId` puede omitirse para un comando HTTP raíz. Los números `minStock` y `factor` son decimales con escala máxima seis.

`ProductUpdated v1` se define en `api/product-updated-v1.schema.json` y usa el mismo sobre. Su payload es un snapshot completo del estado proyectable después de un cambio efectivo: el bloque `product` cubre todos los campos de `inventory.product_ref` y `analytics.product_projection`, mientras `conversions` cubre `inventory.product_unit_conversion_ref`. El mapeo es explícito: `product.id → product_id`, `product.version → source_version`, `eventId → analytics.source_event_id`; categoría y nombre se incluyen para Reporting. `technicalAttributes` no se transporta porque ninguna de esas proyecciones lo contiene. El evento no se crea para un no-op.

**Pendiente separado de Reporting:** `ProductCreated v1` permanece intacto y carece de `name`, `categoryCode` y `categoryName`, por lo que no permite poblar por sí solo `analytics.product_projection` para altas nunca modificadas. `ProductUpdated v1` no corrige esas altas. Antes de implementar el consumidor Reporting se deberá aprobar `ProductCreated v2` con snapshot enriquecido o un bootstrap/reconciliación explícito, sin inferir una llamada REST síncrona.

`SupplierCreated`, `SupplierUpdated` y `SupplierDisabled` v1 se definen en `api/supplier-*-v1.schema.json`. Comparten el sobre: `eventId` es el UUID estable de Outbox, `aggregateType=Supplier`, `aggregateId` identifica al proveedor, `schemaVersion=1`, `producer=catalog-service`, `correlationId` conserva el request y `causationId` es opcional. El payload `{supplier:{id,code,taxId,businessName,active,version}}` corresponde exactamente a `inventory.supplier_ref`; `version` alimenta `source_version`.

`EvidenceUploaded v1` se define en `api/evidence-uploaded-v1.schema.json` y se publica en exchange `siga.events` con routing key `evidence.uploaded.v1`. Usa `eventId=evidence.outbox_event.id`, `eventType=EvidenceUploaded`, `schemaVersion=1`, `aggregateType=Evidence`, `aggregateId=evidence.id`, `producer=evidence-service` y conserva `correlationId`; `causationId` es opcional. El payload contiene solo `id`, `ownerType`, `ownerId`, `uploadedByUserId`, `contentType`, `sizeBytes`, `sha256`, `status=AVAILABLE` y `uploadedAt`. No transporta binario, metadata arbitraria, filename, object key, URL, JWT, OTP ni credenciales.

## 11.4 Transactional Outbox por productor
El patrón aplica a todo servicio que produce eventos relevantes: `iam.outbox_event`, `catalog.outbox_event`, `inventory.outbox_event` y `evidence.outbox_event`. Cada tabla pertenece al mismo schema que el agregado modificado. No existe Outbox compartido.

En Inventory, el mismo commit que stock/movimiento inserta `inventory.outbox_event`. En Catalog, cada mutación efectiva de Product confirma producto, conjunto completo de conversiones y Outbox; cada mutación efectiva de Supplier confirma proveedor y Outbox. Un PUT sin cambios con versión vigente no incrementa versión ni genera evento. En IAM, usuario/RBAC + outbox; en Evidence, metadata + outbox. Si RabbitMQ cae, el negocio confirmado permanece correcto y el publisher reintenta, eliminando la ventana DB-commit/event-lost. El append `PENDING` es transaccional; el publisher posterior publica al menos una vez, por lo que los consumidores deduplican.

## 11.5 Consumidor idempotente por ownership
RabbitMQ puede redeliver. Cada consumidor registra `event_id` procesado en **su propio schema** y los duplicados se ACK sin repetir efectos: `inventory.processed_event` para la proyección de Catalog, `audit.processed_event` para auditoría/notificaciones y `analytics.processed_event` para read models. Ningún consumidor escribe la tabla `processed_event` de otro servicio.

## 11.6 Confiabilidad
Durable exchange/queue, persistent messages, publisher confirms, ACK manual, retry/backoff y DLQ. DLQ>0 genera alerta. Para Product v1, el exchange topic durable es `siga.events`: `ProductCreated` usa `catalog.product.created.v1` y `ProductUpdated` usa `catalog.product.updated.v1`. Supplier v1 usa el mismo exchange con `catalog.supplier.created.v1`, `catalog.supplier.updated.v1` y `catalog.supplier.disabled.v1`; su payload transporta `{supplier:{id,code,taxId,businessName,active,version}}`. Esta topología entrega al menos una vez, no exactamente una vez.

`MovementConfirmed v1` se define en `api/movement-confirmed-v1.schema.json`. Inventory lo emite exclusivamente para cada confirmación D4 de ENTRY, EXIT, TRANSFER y ambos ajustes; los eventos especializados permanecen fuera de alcance hasta tener contrato versionado. Usa `siga.events` con routing `inventory.movement.confirmed.v1`, `aggregateType=Movement`, `schemaVersion=1` y el UUID de `inventory.outbox_event` como `eventId`. El payload contiene el movimiento confirmado —incluidos registrador, confirmador, solicitante opcional, centro de costo, snapshot de proveedor, referencia, motivo, sensibilidad y autorizador cuando apliquen—, sus detalles con snapshots de costo y únicamente los `stockBalances` afectados después del commit. Reporting proyecta movimiento/saldos y Audit conserva trazabilidad; no se transportan JWT, OTP, secretos ni notas libres. Un worker programado reclama PENDING, registra el fallo sin payload y conserva retry/backoff; PUBLISHED solo se marca tras publisher confirm.

`LotChanged v1` y `AssetChanged v1` se definen en `api/lot-changed-v1.schema.json` y `api/asset-changed-v1.schema.json`. Usan `siga.events`, routings `inventory.lot.changed.v1` e `inventory.asset.changed.v1`, snapshots maestros `before/after` y actor nullable para transiciones automáticas. No duplican stock, ubicación o custodia; Audit los consume idempotentemente y no existe consumidor de Notifications.

Notifications reutiliza sin cambios el mismo `MovementConfirmed v1`. Una cola durable independiente `notifications.movement.confirmed.v1`, enlazada a `siga.events` por `inventory.movement.confirmed.v1`, crea una notificación informativa únicamente para `registeredByUserId`. La reclamación en `audit.processed_event` y la inserción en `audit.notification` son una transacción local; el ACK ocurre después del commit, con tres intentos configurables y DLQ `notifications.movement.confirmed.v1.dlq`. No consulta IAM ni otros schemas.

## 11.7 Correlation ID
Gateway crea/propaga X-Correlation-ID; servicios/eventos lo conservan. Sirve para reconstruir Web→Gateway→Inventory→RabbitMQ→Audit y se incluye en Problem Details/logs.

# 12. Reportes, analítica e interoperabilidad

## 12.1 OLTP vs analítica
MS-REP no modifica inventario ni consulta `inventory.stock_balance` como autoridad de escritura. Sus lecturas principales provienen de read models eventualmente consistentes:

- `analytics.product_projection`
- `analytics.inventory_projection`
- `analytics.movement_projection`
- `analytics.kpi_snapshot`
- `analytics.report_job`
- `analytics.processed_event`
- `analytics.export_checkpoint`

La lista anterior describe el modelo objetivo. El MVP materializa `product_projection`, `inventory_projection`, `movement_projection` y `processed_event`; las otras tres tablas quedan diferidas. Los consumidores actualizan las proyecciones a partir de eventos versionados. `analytics.processed_event` evita duplicados. Una caída de Reporting no bloquea la confirmación de stock.

### 12.1.1 Contrato Reporting / Analytics MVP

El contrato cerrado se detalla en `especificaciones/Reporting_Analytics_MVP.md` y `api/reporting-openapi.yaml`. Reporting posee únicamente `analytics.*`; no consulta otros schemas. Consume `MovementConfirmed v1` y `ProductUpdated v1`, usa entrega al menos una vez con deduplicación transaccional por `eventId` y ofrece dashboard, movimientos, valorización y ajustes de solo lectura. `ProductCreated v1` permanece insuficiente y se cubre mediante reconciliación explícita por las APIs paginadas de Catalog e Inventory, con el bearer del operador autorizado, staging propio y reemplazo solo después de un barrido completo.

Los períodos usan límites `[from,to)`, instantes UTC y fronteras de negocio `America/Lima`. Cada respuesta expone `dataUpdatedAt`. PDF/XLSX/CSV, `report_job`, exportación BI incremental, kardex completo y demás reportes especializados quedan diferidos y no forman parte del OpenAPI MVP.

## 12.2 Reportes
El MVP expone movimientos confirmados, valorización actual y ajustes mediante consultas paginadas con filtros server-side. Inventario consolidado avanzado, Kardex, activos, lotes/vencimientos, reposición, consumo por centro de costo, ubicación, exactitud y generación PDF/XLSX/CSV permanecen como catálogo objetivo diferido. `movement_projection` conserva los snapshots ya disponibles para habilitar esas evoluciones sin consultar el OLTP.

## 12.3 ETL/ELT e interoperabilidad
UUID estables, timestamps, dimensiones Producto/Categoría/Ubicación/CentroCosto/Fecha y hechos Movimiento/Existencia/Valorización. Soft delete e historia preservan cargas incrementales. Moneda original/TC/PEN enriquecen análisis.

`export_checkpoint` y la extracción incremental quedan diferidos. Cuando se implementen, BI/ETL recibirá acceso read-only vía API/export y nunca credenciales de escritura a Inventory. En una evolución se pueden añadir read replica/materialized views sin cambiar la autoridad del OLTP.

## 12.4 Tipo de cambio
`ExchangeRatePort` desacopla proveedor. BCRP es referencia conceptual futura; MVP puede usar carga manual autorizada. En cada línea afectada se conserva `exchange_rate_source`, fecha y tasa snapshot. No se acopla dominio a endpoint externo concreto.


# 13. Gestión de repositorios, GitFlow y CI/CD

## 13.1 Multirepo
Cada componente es repo independiente. Para evitar divergencia: convenciones comunes, OpenAPI/event contracts, ADR, tags y release matrix en infrastructure/docs.

## 13.2 Maven
Cada backend tiene pom.xml propio y mvn clean verify. Sin mega-POM. Surefire/Failsafe/JaCoCo/PIT selectivo/Flyway según repo.

## 13.3 GitFlow simplificado
main=releases; develop=integración; feature/* desde develop; hotfix/* desde main y merge a main+develop. Convención feature/SIGA-123-US-08-register-exit. Conventional Commits.

## 13.4 PR
main/develop protegidas, sin push directo. CI verde, review, Jira, tests, OpenAPI/Flyway/docs actualizados y no secretos.

## 13.5 GitHub Actions
PR: build→unit→integration selectiva→coverage→Sonar/CodeQL→secret/dependency scans. Develop: imagen dev. Main/tag: imagen inmutable y deploy controlado.

## 13.6 Artifact Registry
Registry oficial GCP; tags versionados, no depender de latest. Rollback usa versión anterior compatible.

## 13.7 Secretos
Local .env ignorado + .env.example; CI GitHub Secrets/OIDC; GCP Secret Manager. Nunca en frontend/imagen/repo/log.

# 14. Infraestructura y despliegue

## 14.1 Dos niveles
Nivel 1 implementable: Docker Compose local/Compute Engine con Gateway, servicios, Redis, RabbitMQ, MinIO/observabilidad y PostgreSQL local o Cloud SQL/GCS según entorno. Nivel 2 objetivo: GKE con Deployments/Services/Ingress/HPA/ConfigMaps/Secrets, Cloud SQL/GCS/Memorystore. Kubernetes no es requisito MVP.

## 14.2 Ambientes

| Entorno | Propósito | Servicios | Política |
|---|---|---|---|
| LOCAL | Dev individual | Docker Postgres/Redis/RabbitMQ/MinIO | Seed/debug |
| DEV | Integración | Compose integrado | Deploy develop |
| QA/STAGING | Release candidate | Cercano a PROD | ZAP/E2E/load |
| PROD | Demo/objetivo | GCP Cloud SQL/GCS + VM Compose inicialmente | Release/tag/observabilidad |

## 14.3 PostgreSQL
Local/DEV container; QA container o Cloud SQL; PROD objetivo Cloud SQL. Los schemas no cambian.

## 14.4 Redis
Local Docker; PROD Memorystore cuando sea viable. Caída de Redis puede perder cache/estado efímero, nunca stock.

## 14.5 RabbitMQ
Baseline contenedor persistente; K8s StatefulSet/PV o managed futuro. No cambiar a Pub/Sub solo por afinidad GCP.

## 14.6 Nginx/HTTPS
Internet: 80 redirect y 443. Nginx TLS→Gateway. DB/Redis/RabbitMQ/MinIO/micros no públicos. Let's Encrypt baseline; Ingress+cert-manager futuro.

## 14.7 Redes Docker
edge, backend, data y observability. React jamás a DB; Internet jamás a broker/DB. Solo conexiones necesarias.

## 14.8 Update/rollback
Compose: pull versión + docker compose up -d. K8s: RollingUpdate. No copiar JAR manual. DB usa expand/contract. Rollback por tag anterior.

## 14.9 Jobs
Spring Scheduler + ShedLock para expiraciones, cleanup idempotency, outbox polling si aplica y sesiones. Backups preferentemente infraestructura/managed.

# 15. Observabilidad y operación

## 15.1 Métricas
Actuator+Micrometer→Prometheus→Grafana. HTTP/P95/JVM/CPU/threads/pool DB/RabbitMQ/Redis + custom: movements_confirmed, stock_conflicts, outbox_pending, evidence_failures.

## 15.2 Logging
JSON logs con timestamp, level, service, correlationId, traceId; Loki vía Alloy/Promtail y Grafana. ELK se evita por recursos. Logging no es auditoría.

## 15.3 Tracing
OpenTelemetry + Jaeger DEV/QA. Falla de tracing no bloquea negocio.

## 15.4 Health
/actuator/health, /liveness, /readiness. Dependencia no crítica como analytics/tracing no tumba Inventory.

## 15.5 Alertas
DOWN, error rate, P95, pool DB, backlog RabbitMQ, DLQ>0, outbox pendiente, backup fallido, disco>80%, memoria y restore fallido. Grafana canal inicial.

## 15.6 SLO/Rendimiento
99.5% mensual objetivo, no SLA contractual. P95 lectura<=500ms, comando<=1000ms, dashboard<=2000ms, error técnico<1% a 50 usuarios. 100+ es stress, no objetivo.

# 16. Continuidad, respaldo y recuperación

## 16.1 Objetivos
RPO<=24h y RTO<=4h.

## 16.2 PostgreSQL Docker
Job pg_dump protegido→bucket de backup. Diario 30 días y mensual según política; registrar resultado y alertar fallo.

## 16.3 Cloud SQL
Backups automáticos, PITR si habilitado y exportación complementaria cuando corresponda.

## 16.4 GCS/MinIO
Versioning+lifecycle+IAM; MinIO puede versionar. pg_dump no respalda objetos.

## 16.5 Restore Test
1 seleccionar backup; 2 entorno limpio; 3 restaurar; 4 verificar migraciones; 5 integridad/conteos; 6 auth; 7 inventario/movimientos; 8 evidencias; 9 medir; 10 RPO/RTO; 11 incidencias; 12 aprobar/corregir.

## 16.6 Plantilla Restore

| Campo | Contenido |
|---|---|
| Fecha | AAAA-MM-DD |
| Responsable | Rol |
| Backup | ID/fecha |
| Inicio/Fin | Timestamp |
| RTO real | Duración |
| Último dato | Timestamp |
| RPO real | Diferencia |
| Checks | Usuarios/inventario/movimientos/evidencias |
| Resultado | PASS/FAIL |
| Incidencias | Ticket/acción |

# 17. Testing y calidad

## 17.1 Pirámide
Muchas unitarias/caja blanca; integración real; API/contrato crítico; pocos E2E; performance/security especializados. Cobertura no sustituye aserciones.

## 17.2 Backend
JUnit5+Mockito+AssertJ. Probar branches, excepciones, estados, reglas, Inventory/Movement/Authorization/Cost/Idempotency.

## 17.3 Coverage
Global backend line>=80%, branch>=70%; núcleo crítico line>=90%, branch>=80%. Frontend >=70% de lógica testeable. JaCoCo produce gate; DTO/config/generated pueden excluirse justificadamente.

## 17.4 SonarCloud
Principal; SonarQube local opcional. No issues críticas nuevas, cobertura, duplicación controlada, hotspots revisados; priorizar new code.

## 17.5 Testcontainers
PostgreSQL/Redis/RabbitMQ/MinIO reales para JSONB/Flyway/locks/constraints/transacciones.

## 17.6 ACID/concurrencia e integridad obligatorias
Dos salidas concurrentes sin stock negativo; falla intermedia rollback; CHECK cantidad; transferencia origen/destino consistente; multi-detalle all-or-nothing. Se agregan pruebas de: activo serializado no duplicado en dos ubicaciones positivas, lote/activo del mismo producto, conversión snapshot reproducible, `product_ref` disponible sin REST a Catalog y conteo físico que no modifica stock directamente.

## 17.7 Mutation testing
PIT solo Inventory/Movement/Cost/Authorization, preferiblemente manual/nocturno/pre-release si el tiempo lo permite. No perseguir score artificial global.

## 17.8 API/contratos
MockMvc controllers; REST Assured integración; Postman demo/manual y Newman selectivo; OpenAPI contrato público; Spring Cloud Contract solo interacciones críticas; WireMock para externos.

## 17.9 Web/Mobile/E2E
Web Vitest+RTL+MSW; Playwright en flujos críticos. Mobile Jest+RNTL; Maestro por menor costo temporal.

## 17.10 Datos de prueba
Dataset versionado con roles, A36, rodamiento, lubricante, excavadora, ubicaciones, lotes/activos y límites. Seeds solo DEV/TEST.

## 17.11 Estado/idempotencia/outbox
Matriz canónica `DRAFT/PENDING_AUTHORIZATION/AUTHORIZED/CONFIRMED/REJECTED/CANCELLED`; `CONFIRMED` inmutable. Idempotency-Key duplicada con mismo payload no repite; payload distinto => 409. Outbox se prueba por productor (IAM/CAT/INV/EVI), con broker up/down/retry. Consumidor duplicado se valida por ownership en Inventory, Audit y Reporting mediante sus respectivas tablas `processed_event`.

## 17.12 Performance
k6 smoke/load/stress/spike. Load 50 usuarios con RNF; stress 100+. Lighthouse orientativo: Performance>=80, Accessibility>=90, Best Practices>=90 bajo condiciones controladas.

## 17.13 Seguridad simplificada
CodeQL, Dependabot/Dependency-Check/npm audit, Trivy, Gitleaks, ZAP Baseline QA. Prioridades manuales: JWT/refresh/MFA/RBAC/IDOR/SQLi/XSS/archivo/path traversal/replay. OWASP Top10/ASVS como referencia. ClamAV futuro.

## 17.14 Evidencias/DoD
Actions conserva JUnit/JaCoCo/Playwright/k6/ZAP/Trivy relevantes. HU termina si criterios, review, tests aplicables, CI verde, sin crítico conocido, OpenAPI/Flyway/docs actualizados y evidencia. Herramientas avanzadas se aplican sin comprometer sprint.

# 18. Diseño UX/UI y matriz maestra

## 18.1 Flujo
Login→MFA→Dashboard→módulo. Inventario: búsqueda→producto/activo→ubicación/lote/serie→movimiento→validación→autorización si sensible→confirmación→resultado/historial.

## 18.2 Vistas para Figma/UX

| ID | Vista | Ruta | Actor | Elementos | API |
|---|---|---|---|---|---|
| UI-W01 | Login | /login | Todos | Credenciales/validación | POST /auth/login |
| UI-W02 | MFA | /mfa | MFA | OTP/reintento | POST /auth/mfa/verify |
| UI-W03 | Dashboard | /dashboard | Admin/Supervisor | KPIs/alertas | GET /dashboard |
| UI-W04 | Usuarios | /users | Admin | Tabla/CRUD lógico | /users |
| UI-W05 | Roles | /roles | Admin | Roles/permisos | /roles |
| UI-W06 | Categorías | /catalog/categories | Admin | CRUD; lista code ASC, activos/inactivos | /categories |
| UI-W07 | Productos | /catalog/products | Admin/Encargado | SKU/UoM/JSONB/trazabilidad; alta y reemplazo completo con versión; activación lógica | GET/POST /products; GET/PUT /products/{id} |
| UI-W08 | Unidades | /catalog/units | Admin | UoM/conversión; lista code ASC, activos/inactivos | /units |
| UI-W09 | Inventario | /inventory | Autorizado | Stock/filtros/ubicación | GET /inventory |
| UI-W10 | Ubicaciones | /locations | Admin/Supervisor | Árbol jerárquico | /locations |
| UI-W11 | Lotes/Activos | /lots /assets | Encargado | Lote/serie/estado | inventory |
| UI-W12 | Nuevo movimiento | /movements/new | Encargado | Cabecera + N detalles | POST /movements |
| UI-W13 | Detalle | /movements/:id | Autorizado | Estado/detalles/evidencia | GET movement |
| UI-W14 | Autorizar | /movements/:id/authorize | Autorizador | Resumen/step-up | authorize/reject |
| UI-W15 | Transferencia | /movements/new?type=TRANSFER | Encargado/Supervisor | Origen/destino | POST movement |
| UI-W16 | Ajuste | /adjustments | Supervisor/Admin | Motivo/evidencia | POST movement |
| UI-W17 | Conteo | /counts | Supervisor/Encargado | Snapshot, captura, diferencia y cierre | API counts completa |
| UI-W18 | Evidencia | contextual | Autorizado | Upload/preview | /evidences |
| UI-W19 | Historial | /movements | Autorizado | Paginación/filtros | GET movements |
| UI-W20 | Reportes | /reports | Autorizado | PDF/XLSX/CSV | /reports |
| UI-W21 | Auditoría | /audit | Admin/Seguridad | Eventos/correlation | /audit-events |
| UI-W22 | Notificaciones | panel | Autorizado | Alertas | /notifications |
| UI-M01 | Login móvil | /(auth)/login | Móvil | Credenciales | /auth/login |
| UI-M02 | OTP móvil | /(auth)/otp | Móvil | TOTP | /auth/mfa/verify |
| UI-M03 | Inventario móvil | /inventory | Móvil | Buscar/cache state | GET inventory |
| UI-M04 | Detalle móvil | /inventory/:id | Móvil | Ubic/lote/serie | GET inventory |
| UI-M05 | Movimiento móvil | /movements/new | Móvil autorizado | Online only | POST movement |
| UI-M06 | Evidencia móvil | modal | Móvil | Cámara/galería/PDF | POST evidences |
| UI-M07 | Notificaciones móvil | /notifications | Móvil | Lista/leer | /notifications |
| UI-M08 | Perfil | /profile | Móvil | Logout | /auth/logout |

## 18.3 Handoff Figma
Cada vista: objetivo, actor, jerarquía, campos/formatos, acciones, estados loading/empty/error/forbidden, validaciones, confirmaciones, responsive, Problem Details y permisos. Ver Guia_Figma_UI_UX_SIGA.md.

## 18.4 Wireframe→Mockup→Captura
Separar estructura lógica, Figma aprobado y evidencia real. IDs FIG-UI permanecen estables para insertar imágenes sin renumerar.

# 19. OpenAPI, contratos y eventos

Los seis OpenAPI del paquete son base editable para alinear rutas, payloads, permisos y errores. El código final debe mantenerlos sincronizados. Eventos versionan schemaVersion y tienen productor/consumidor/routing/retry/DLQ explícitos.

# 20. ADR, riesgos y escalabilidad

## 20.1 ADR
18 ADR cubren microservicios, seis servicios, Inventory+Movement, schemas, JSONB, REST+RabbitMQ, Outbox por productor, locking, Redis, object storage, JWT/MFA, Gateway, Compose/K8s, GCP, Clean Architecture, no offline, multirepo/GitFlow y el **modelo de datos canónico/coherencia entre artefactos (ADR-018)**.

## 20.2 Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Microservicios | Retraso | Solo 6, contracts, Compose |
| Locks | Latencia | Filas específicas/transacciones cortas |
| Evento perdido/duplicado | Inconsistencia secundaria | Outbox+confirm+idempotencia |
| Contratos multirepo | Integración rota | OpenAPI/contract tests/release matrix |
| Secretos | Incidente | Secret Manager/Gitleaks |
| Costo GCP | Limitación | Local/Compose y recursos mínimos |
| Sobre-QA | No terminar | Herramientas avanzadas selectivas |
| Cache vieja | Dato visual viejo | PostgreSQL autoridad/refetch |
| Archivo malicioso | Riesgo | MIME/magic/size/hash; AV futuro |

## 20.3 Escalabilidad futura
Servicios stateless escalan horizontalmente; Inventory se optimiza con índices/pool/partición futura; Reporting puede usar read replicas/models. GKE HPA/rolling. Schemas pueden evolucionar a DB físicas. Signed URLs/CDN/managed broker/HA solo ante demanda.

# 21. Jira y GitHub

Épica→HU→Task/Subtask→Branch→Commit→PR→Release. Jira SIGA-123; branch feature/SIGA-123-US-08-register-exit; PR [SIGA-123] Implement register exit. Guía de imágenes define capturas de backlog/roadmap/PR.

# 22. Implementación por Sprint

| Sprint | Resultado | Foco |
|---|---|---|
| 1 | Repos/Gateway/IAM/Catalog/Web base | Arquitectura, contratos, login, CRUD, UI kit |
| 2 | Primer módulo funcional | Postgres/Flyway/JWT/MFA/API/React |
| 3 | Núcleo almacén | Inventory Core, multi-detalle, locking, idempotencia, ubic/lote/serie, móvil, HTTPS |
| 4 | Calidad/cierre | Evidence, RabbitMQ/Outbox, BI, audit, observabilidad, security, backup/restore, CI/CD |

# 23. Cobertura del informe final

| Capítulo informe | Fuente |
|---|---|
| 1 Introducción | 1,23 |
| 2 Plan | 1.5-1.7,22 |
| 3 Empresa | Manual Administrativo |
| 4 Objetivos | 1.3-1.4 |
| 5 Requisitos | 2 |
| 6 Alcance | 1.5,3 |
| 7 Cronograma | 1.7,22 |
| 8 CUN | 2.4-2.6+BPMN |
| 9 CUS | 2.5-2.7+UML |
| 10 Análisis requisitos | 2 |
| 11 RF vs CUS | trazabilidad MTR-01 |
| 12 RF vs HU | MTR-02 |
| 13 Solución | 3,20 |
| 14 Especificación CUS | 2.7 |
| 15 Diagramas análisis | 3-4+diagramas |
| 16 Estructura software | 6,8,9,ADR |
| 17 Modelo datos | 5+database+DER-01..09 |
| 18 Calidad BD | 5+dictionary/sql+DER físicos por schema |
| 19 Jira/GitHub | 13,21 |
| 20 Mockups | 18+Guia Figma |
| 21 Evidencias | Guia imágenes |
| 22 Elaboración/despliegue | 14+devops |
| 23 Componentes | c4/uml |
| 24 Despliegue | 14+devops diagrams |
| 25 Pruebas | 17+testing matrix |
| 26 Manual usuario | Guia Manual Usuario |

## 23.1 No duplicación
Lean Canvas, misión/visión, descripción comercial y bases administrativas permanecen en el informe general/Manual Administrativo; aquí se referencia su impacto técnico.

# 24. Cierre y gobierno documental

Esta versión 1.1 fija la línea técnica y el modelo de datos canónico. Cambios en fronteras, transacción de stock, persistencia, autenticación, contrato, evento o despliegue requieren ADR y actualización de matrices/diagramas. Parámetros operativos se calibran por entorno sin alterar principios.

**Regla final:** ningún cliente, cache, broker, reporte o integración reemplaza a PostgreSQL como autoridad del inventario; ninguna optimización puede permitir salida mayor a existencia ni movimiento parcial.


---

# Anexo A. Especificaciones detalladas de CUS


Estas especificaciones son la referencia técnica-funcional para implementación, diagramas y pruebas. Los flujos críticos se complementan con los `.puml` indicados. Los endpoints son baseline contractual y deben mantenerse alineados con OpenAPI.

## CUS-01 — Autenticarse y validar MFA

| Campo | Especificación |
|---|---|
| Actor principal | Usuario |
| RF | RF-01 |
| HU | US-01 |
| Servicio responsable | MS-IAM |
| Endpoint(s) | `POST /api/v1/auth/login; POST /api/v1/auth/mfa/verify` |
| Permiso baseline | `AUTHENTICATE` |
| Eventos/asíncronos | Ninguno |
| Precondiciones | Usuario activo; no bloqueado; credenciales disponibles |
| Postcondiciones | Sesión autenticada; access token emitido; refresh session registrada |
| Excepciones relevantes | Credencial inválida, bloqueo temporal, MFA requerido/incorrecto, rate limit |
| Diagrama(s) | SEQ-01 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-IAM**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-02 — Gestionar usuarios

| Campo | Especificación |
|---|---|
| Actor principal | Administrador |
| RF | RF-02 |
| HU | US-02 |
| Servicio responsable | MS-IAM |
| Endpoint(s) | `GET /api/v1/users`; `GET/PATCH /api/v1/users/{id}`; `POST /api/v1/users`; `PUT /api/v1/users/{id}/roles` |
| Permiso baseline | `USER_MANAGE` |
| Eventos/asíncronos | Outbox IAM: UserCreated/UserUpdated/UserDisabled/RoleChanged; consumidor central Audit diferido |
| Precondiciones | Lectura con `USER_MANAGE`; mutación con MFA y `auth_time` de máximo 300 segundos; `ROLE_MANAGE` para reemplazar/asignar roles |
| Postcondiciones | Usuario creado/actualizado/desactivado sin perder trazabilidad |
| Excepciones relevantes | Duplicado, validación, intento de autodesactivación no permitida por política |
| Diagrama(s) | UML-02 |

**Contrato administrativo MVP:** la lista usa página 0, tamaño 20 (`page >= 0`, `size 1..100`) y `username ASC`, sin búsqueda, filtros ni orden arbitrario. El modelo es `{id,username,email,active,mfaEnabled,roleIds}`. La creación exige contraseña inicial y admite roles; Web trata la contraseña como dato transitorio y no la persiste. Web permite editar solo email/estado, presenta `mfaEnabled` como lectura y no expone administración MFA, reset/desbloqueo ni borrado. Los roles de usuario se reemplazan como conjunto completo, sin versión optimista y con last-write-wins aceptado para el MVP.

Identity confirma cada mutación y su `iam.outbox_event` local de forma transaccional. La publicación durable está vigente; el consumo de eventos IAM por el servicio central Audit no está implementado y queda registrado como `IAM_EVENTS_CENTRAL_AUDIT_CONSUMER`.

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-IAM**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-03 — Gestionar roles y permisos

| Campo | Especificación |
|---|---|
| Actor principal | Administrador |
| RF | RF-03 |
| HU | US-03 |
| Servicio responsable | MS-IAM |
| Endpoint(s) | `GET/POST /api/v1/roles`; `PUT /api/v1/roles/{id}/permissions`; `GET /api/v1/permissions` |
| Permiso baseline | `ROLE_MANAGE` |
| Eventos/asíncronos | Outbox IAM: RoleChanged; consumidor central Audit diferido |
| Precondiciones | Lecturas con `ROLE_MANAGE`; mutaciones con MFA y `auth_time` de máximo 300 segundos; catálogo de permisos read-only |
| Postcondiciones | RBAC actualizado; sesiones nuevas reflejan permisos |
| Excepciones relevantes | Rol protegido, permiso inexistente, conflicto de asignación |
| Diagrama(s) | UML-02 |

**Contrato RBAC MVP:** se listan y crean roles y se reemplaza el conjunto completo de permisos de un rol; no existe `PATCH /roles`, detalle individual, edición genérica, rename, activación/desactivación ni borrado. `GET /permissions` lista `{id,code,description}` por `code ASC`; el catálogo es read-only. `ADMIN` permanece protegido por backend. Los reemplazos de roles/permisos no usan ETag ni `expectedVersion`: `LAST_WRITE_WINS_ACCEPTED_FOR_MVP` exige cargar el estado vigente, confirmar el conjunto completo y recargar tras guardar, pero acepta como riesgo residual que dos administradores concurrentes puedan sobrescribirse.

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-IAM**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-04 — Gestionar categorías

| Campo | Especificación |
|---|---|
| Actor principal | Administrador |
| RF | RF-04 |
| HU | US-04 |
| Servicio responsable | MS-CAT |
| Endpoint(s) | `GET/POST/PATCH /api/v1/categories` |
| Permiso baseline | `PRODUCT_WRITE` |
| Eventos/asíncronos | Product/Category metadata event selectivo |
| Precondiciones | Categoría no duplicada |
| Postcondiciones | Categoría activa/desactivada conservando historial |
| Excepciones relevantes | Código duplicado, categoría referenciada no se elimina físicamente |
| Diagrama(s) | UML-03 |

**Contrato de consulta aprobado:** `GET /api/v1/categories` exige `CATALOG_READ` (o `PRODUCT_WRITE` por compatibilidad administrativa) y responde `200 application/json` con un arreglo directo de `{id, code, name, categoryType, active}`. Incluye categorías activas e inactivas, ordenadas por `code ASC`, sin paginación ni filtros en esta versión.

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-CAT**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-05 — Gestionar productos

| Campo | Especificación |
|---|---|
| Actor principal | Administrador/Encargado |
| RF | RF-05,RF-23,RF-27,RF-28 |
| HU | US-05 |
| Servicio responsable | MS-CAT |
| Endpoint(s) | `GET/POST /api/v1/products; GET/PUT /api/v1/products/{id}` |
| Permiso baseline | `PRODUCT_WRITE` |
| Eventos/asíncronos | ProductCreated; ProductUpdated |
| Precondiciones | `PRODUCT_WRITE`; referencias nuevas/modificadas activas; todas activas si el estado final es activo |
| Postcondiciones | Producto persistido y proyectable a Inventory |
| Excepciones relevantes | SKU duplicado, factor inválido |
| Diagrama(s) | SEQ-03; UML-03 |

**Regla de selectores aprobada:** los selectores de categoría y UoM para Product muestran solo registros activos. Cuando se implemente Product, MS-CAT deberá validar también en backend que `categoryId`, `storageUnitId` y `baseUnitId` correspondan a maestros activos.

**Alta y conversiones aprobadas:** si `storageUnitId` y `baseUnitId` difieren, el request debe incluir una conversión activa directa `storageUnitId → baseUnitId`. `factor` significa `cantidad_origen × factor = cantidad_destino`. `dimension` es informativa y no invalida por sí sola una conversión entre dos UoM activas. Cada UoM usada por una conversión debe existir y estar activa; se mantienen `factor > 0`, unidades distintas y unicidad por producto/origen/destino.

**Flags de trazabilidad v1.2:** `requiresLot`, `requiresHeatNumber`, `requiresExpiry` y `requiresSerial` son booleanos independientes. Cualquier combinación de sus valores es válida, incluidos `requiresHeatNumber=true` con `requiresLot=false`; cada requisito se aplica individualmente en Inventory cuando corresponde. Se retira “flags contradictorios” de las excepciones porque las fuentes v1.2 no definen ninguna combinación incompatible.

**Edición integral aprobada:** `PUT /api/v1/products/{id}` reemplaza el estado editable completo. El request exige `sku`, `name`, `categoryId`, `productType`, `storageUnitId`, `baseUnitId`, `minStock`, los cuatro flags de trazabilidad, `technicalAttributes`, `conversions`, `active` y `expectedVersion`; omitir cualquiera devuelve `400` y nunca significa conservar el valor anterior. `conversions` es el conjunto completo, por lo que las parejas omitidas dejan de pertenecer al producto. SKU, categoría, tipo, unidades, umbral, atributos, flags y estado son editables; v1.2 no impone inmutabilidad de SKU, igualdad entre `categoryType` y `productType` ni restricciones síncronas basadas en existencias de Inventory.

**Concurrencia y no-op aprobados:** MS-CAT comprueba primero que el producto existe y luego compara `expectedVersion` con la versión persistida. Una versión obsoleta devuelve siempre `409 VERSION_CONFLICT`, incluso si el contenido coincide. Con versión vigente, la igualdad semántica del producto y del conjunto de conversiones devuelve `200` con la representación actual sin modificar producto, conversiones, `updated_at`, versión ni Outbox. Un cambio efectivo usa actualización condicional por `id + version`, incrementa la versión exactamente en uno y confirma producto, reemplazo de conversiones y `ProductUpdated v1` PENDING en una sola transacción.

**Referencias durante edición y cambio de estado:** un no-op válido no se rechaza porque una categoría o UoM histórica, sin cambios, haya sido desactivada después. En cambios efectivos, toda referencia nueva o modificada debe existir y estar activa y el estado resultante debe cumplir las invariantes de conversiones. Si el resultado queda activo —incluida la reactivación— todas las referencias propuestas deben cumplir las reglas vigentes. Para desactivar o editar manteniendo inactivo un producto, se permite conservar referencias existentes ahora inactivas, pero no introducir ni sustituir una referencia por otra inactiva; así la desactivación no queda bloqueada por cambios previos de maestros. No se consulta Inventory, no se elimina el producto y no se alteran stock ni movimientos históricos.

**Referencias y eventos:** categoría o UoM inexistente devuelve `404` Problem Details; una referencia nueva/modificada inactiva o una referencia inactiva en un estado final activo devuelve `409` Problem Details. En el alta se inserta `ProductCreated v1`; en cada edición efectiva, desactivación o reactivación se inserta `ProductUpdated v1`. Ambos registros Outbox se confirman con el agregado local, se publican después al menos una vez e Inventory deduplica por `eventId` en `inventory.processed_event`. Los contratos son `api/product-created-v1.schema.json` y `api/product-updated-v1.schema.json`; un no-op no produce evento.

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-CAT**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-06 — Consultar inventario

| Campo | Especificación |
|---|---|
| Actor principal | Usuario autorizado |
| RF | RF-06,RF-16 |
| HU | US-06 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `GET /api/v1/inventory` |
| Permiso baseline | `INVENTORY_READ` |
| Eventos/asíncronos | Ninguno |
| Precondiciones | Producto/proyección disponible |
| Postcondiciones | Respuesta paginada con stock consolidado y por ubicación |
| Excepciones relevantes | Filtros inválidos, acceso no autorizado |
| Diagrama(s) | DER-02 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-07 — Registrar entrada

| Campo | Especificación |
|---|---|
| Actor principal | Encargado |
| RF | RF-07,RF-09,RF-27,RF-28,RF-31,RF-35 |
| HU | US-07 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `POST /api/v1/movements; POST /movements/{id}/confirm` |
| Permiso baseline | `MOVEMENT_CREATE` |
| Eventos/asíncronos | MovementConfirmed; StockBelowMinimum no usual; outbox |
| Precondiciones | Producto/ubicación activos; costo/trazabilidad según flags; proveedor activo cuando la recepción sea externa |
| Postcondiciones | Stock incrementado, costo promedio actualizado, movimiento CONFIRMADO |
| Excepciones relevantes | UoM/lote/serie/TC/proveedor inválido; rollback total |
| Diagrama(s) | SEQ-04; BPMN-01 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-08 — Registrar salida

| Campo | Especificación |
|---|---|
| Actor principal | Encargado |
| RF | RF-08,RF-09,RF-29 |
| HU | US-08 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `POST /api/v1/movements; /submit; /confirm` |
| Permiso baseline | `MOVEMENT_CREATE` |
| Eventos/asíncronos | MovementConfirmed; StockBelowMinimum; StockDepleted; SensitiveMovementConfirmed |
| Precondiciones | Stock potencial disponible; ubicación/lote/activo definido |
| Postcondiciones | Stock descontado atómicamente o rechazo sin efecto |
| Excepciones relevantes | Stock insuficiente, sensible sin autorización, idempotencia conflictiva |
| Diagrama(s) | SEQ-05; SEQ-06; BPMN-02 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-09 — Transferir existencia

| Campo | Especificación |
|---|---|
| Actor principal | Encargado/Supervisor |
| RF | RF-25,RF-09 |
| HU | US-25 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `POST /api/v1/movements; /confirm` |
| Permiso baseline | `MOVEMENT_CREATE` |
| Eventos/asíncronos | MovementConfirmed |
| Precondiciones | Origen y destino válidos y distintos |
| Postcondiciones | Origen disminuye y destino aumenta en el mismo commit; total global constante |
| Excepciones relevantes | Stock insuficiente, trazabilidad incompatible, deadlock/retry controlado |
| Diagrama(s) | SEQ-08; BPMN-03 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-10 — Ajustar inventario

| Campo | Especificación |
|---|---|
| Actor principal | Supervisor/Administrador |
| RF | RF-26,RF-29,RF-30 |
| HU | US-26 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `POST /api/v1/movements; /submit; /authorize; /confirm` |
| Permiso baseline | `INVENTORY_ADJUST` |
| Eventos/asíncronos | InventoryAdjusted; SensitiveMovementConfirmed |
| Precondiciones | Motivo obligatorio; privilegio; evidencia según política |
| Postcondiciones | Ajuste +/- trazable sin editar histórico |
| Excepciones relevantes | Resultado negativo, autorización faltante, motivo ausente |
| Diagrama(s) | SEQ-09; BPMN-04 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-11 — Consultar historial

| Campo | Especificación |
|---|---|
| Actor principal | Usuario autorizado |
| RF | RF-10,RF-16 |
| HU | US-10 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `GET /api/v1/movements; GET /movements/{id}` |
| Permiso baseline | `MOVEMENT_READ` |
| Eventos/asíncronos | Ninguno |
| Precondiciones | Permiso de consulta |
| Postcondiciones | Historial paginado/inmutable visible |
| Excepciones relevantes | Filtro inválido, movimiento inexistente |
| Diagrama(s) | STATE-01 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-12 — Configurar stock mínimo

| Campo | Especificación |
|---|---|
| Actor principal | Administrador |
| RF | RF-11 |
| HU | US-11 |
| Servicio responsable | MS-CAT |
| Endpoint(s) | `PUT /api/v1/products/{id}` |
| Permiso baseline | `PRODUCT_WRITE` |
| Eventos/asíncronos | ProductUpdated |
| Precondiciones | Producto existente y `expectedVersion` vigente |
| Postcondiciones | Umbral persistido y proyectado |
| Excepciones relevantes | Valor negativo/incompatible |
| Diagrama(s) | UML-03 |

**Contrato aprobado:** el umbral se modifica como parte del reemplazo completo de Product mediante `PUT /api/v1/products/{id}`; no existe un PATCH parcial adicional en v1.2. `minStock` es obligatorio, usa precisión máxima 18,6 y debe ser mayor o igual que cero. Se aplican el mismo `expectedVersion`, no-op y `ProductUpdated v1` de CUS-05.

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-CAT**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-13 — Consultar dashboard

| Campo | Especificación |
|---|---|
| Actor principal | Cualquier actor autenticado con el permiso efectivo requerido; no se autoriza por nombre de rol |
| RF | RF-13,RF-20 |
| HU | US-13 |
| Servicio responsable | MS-REP |
| Endpoint(s) | `GET /api/v1/dashboard` |
| Permiso baseline | `REPORT_READ` |
| Eventos/asíncronos | Consume proyecciones |
| Precondiciones | Read models disponibles o fallback controlado |
| Postcondiciones | KPIs operativos y alertas resumidas |
| Excepciones relevantes | Dato parcial marcado; dependencia analítica caída no bloquea Inventory |
| Diagrama(s) | C4-02 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-REP**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-14 — Consultar inventario móvil

| Campo | Especificación |
|---|---|
| Actor principal | Usuario móvil |
| RF | RF-14,RF-16 |
| HU | US-14 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `GET /api/v1/inventory` |
| Permiso baseline | `INVENTORY_READ` |
| Eventos/asíncronos | Ninguno |
| Precondiciones | Sesión móvil; red o caché previa |
| Postcondiciones | Datos actuales online; cache stale claramente indicada offline |
| Excepciones relevantes | Sin conexión sin cache, 401/403 |
| Diagrama(s) | UML-09 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-15 — Registrar movimiento móvil

| Campo | Especificación |
|---|---|
| Actor principal | Usuario móvil autorizado |
| RF | RF-15,RF-07,RF-08,RF-25 |
| HU | US-15 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `POST /api/v1/movements; /submit; /confirm` |
| Permiso baseline | `MOVEMENT_CREATE` |
| Eventos/asíncronos | Mismos eventos que Web |
| Precondiciones | Conexión obligatoria |
| Postcondiciones | Movimiento central confirmado; sin cola transaccional offline |
| Excepciones relevantes | Sin red, stock cambió, permisos/step-up |
| Diagrama(s) | SEQ-05 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-16 — Buscar y filtrar

| Campo | Especificación |
|---|---|
| Actor principal | Usuario autorizado |
| RF | RF-16 |
| HU | US-16 |
| Servicio responsable | MS-CAT/MS-INV/MS-REP |
| Endpoint(s) | `GET con page,size,sort y filtros` |
| Permiso baseline | `Permiso del recurso` |
| Eventos/asíncronos | Ninguno |
| Precondiciones | Parámetros permitidos |
| Postcondiciones | Resultados server-side paginados |
| Excepciones relevantes | Filtro no soportado/consulta inválida |
| Diagrama(s) | N/A |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-CAT/MS-INV/MS-REP**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-17 — Generar/exportar reporte

| Campo | Especificación |
|---|---|
| Actor principal | Usuario autorizado |
| RF | RF-17,RF-34 |
| HU | US-17 |
| Servicio responsable | MS-REP |
| Endpoint(s) | `POST /api/v1/reports; GET /reports/{id}` |
| Permiso baseline | `REPORT_READ` |
| Eventos/asíncronos | ReportGenerated opcional |
| Precondiciones | Filtros y formato válidos |
| Postcondiciones | PDF/XLSX/CSV temporal o persistente/auditable |
| Excepciones relevantes | Sin datos, formato no soportado, generación falla |
| Diagrama(s) | SEQ-13; BPMN-07 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-REP**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-18 — Consultar auditoría

| Campo | Especificación |
|---|---|
| Actor principal | Administrador/Seguridad TI |
| RF | RF-18 |
| HU | US-18 |
| Servicio responsable | MS-AUD |
| Endpoint(s) | `GET /api/v1/audit-events` |
| Permiso baseline | `AUDIT_READ` |
| Eventos/asíncronos | Consume eventos funcionales |
| Precondiciones | Permiso sensible |
| Postcondiciones | Eventos consultables con actor, recurso, resultado, correlationId |
| Excepciones relevantes | Acceso negado, filtro inválido |
| Diagrama(s) | UML-06 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-AUD**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-19 — Consumir integración analítica

| Campo | Especificación |
|---|---|
| Actor principal | BI/Analista técnico |
| RF | RF-19 |
| HU | US-19 |
| Servicio responsable | MS-REP |
| Endpoint(s) | `GET /api/v1/analytics/exports` |
| Permiso baseline | `ANALYTICS_READ` |
| Eventos/asíncronos | Ninguno |
| Precondiciones | Credencial de integración read-only |
| Postcondiciones | Export incremental con watermark |
| Excepciones relevantes | Watermark inválido, autorización, servicio temporalmente no disponible |
| Diagrama(s) | SEQ-14 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-REP**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-20 — Consultar indicadores

| Campo | Especificación |
|---|---|
| Actor principal | Administrador/Supervisor |
| RF | RF-20 |
| HU | US-20 |
| Servicio responsable | MS-REP |
| Endpoint(s) | `GET /api/v1/dashboard; GET /api/v1/kpis` |
| Permiso baseline | `REPORT_READ` |
| Eventos/asíncronos | Proyecciones |
| Precondiciones | Datos suficientes |
| Postcondiciones | Indicadores con período y fecha de corte |
| Excepciones relevantes | Indicador no calculable se reporta como no disponible, no se inventa |
| Diagrama(s) | C4-02 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-REP**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-21 — Monitorear plataforma

| Campo | Especificación |
|---|---|
| Actor principal | DevOps/TI |
| RF | RF-21 |
| HU | US-21 |
| Servicio responsable | Todos |
| Endpoint(s) | `/actuator/health; /actuator/prometheus (restringido)` |
| Permiso baseline | `OPS_MONITOR` |
| Eventos/asíncronos | Logs/métricas/trazas |
| Precondiciones | Acceso técnico autorizado |
| Postcondiciones | Estado operativo visible y alertable |
| Excepciones relevantes | Endpoint sensible expuesto públicamente = configuración inválida |
| Diagrama(s) | DEVOPS-05 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **Todos**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-22 — Ejecutar recuperación

| Campo | Especificación |
|---|---|
| Actor principal | DevOps/TI |
| RF | RF-22 |
| HU | US-22 |
| Servicio responsable | Infra/DB |
| Endpoint(s) | `Procedimiento operativo, no API pública` |
| Permiso baseline | `OPS_RECOVERY` |
| Eventos/asíncronos | Audit de restore test |
| Precondiciones | Backup válido y entorno controlado |
| Postcondiciones | Servicio restaurado y evidencia RPO/RTO |
| Excepciones relevantes | Backup corrupto, RTO excedido, evidencia faltante |
| Diagrama(s) | DEVOPS-06 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **Infra/DB**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-23 — Gestionar unidades y conversiones

| Campo | Especificación |
|---|---|
| Actor principal | Administrador |
| RF | RF-23 |
| HU | US-23 |
| Servicio responsable | MS-CAT |
| Endpoint(s) | `GET/POST /api/v1/units; conversiones reemplazadas/versionadas mediante PUT /api/v1/products/{id}` |
| Permiso baseline | `PRODUCT_WRITE` |
| Eventos/asíncronos | ProductUpdated |
| Precondiciones | Magnitud/unidad válidas |
| Postcondiciones | Conjunto completo de cero o más conversiones from/to/factor>0 persistido y proyectable a Inventory |
| Excepciones relevantes | Factor <=0, unidad incompatible |
| Diagrama(s) | UML-03 |

**Reemplazo y proyección aprobados:** el PUT de Product exige el arreglo `conversions` y lo interpreta como snapshot completo. Cada pareja origen/destino es única, sus unidades son distintas, `factor` es positivo con precisión máxima 18,6 y toda referencia nueva o modificada usa UoM activas. Un cambio efectivo incrementa la versión de Product y emite `ProductUpdated v1` con el snapshot completo expresado en códigos UoM; un no-op no reescribe conversiones ni emite evento. La política para desactivar una UoM usada queda fuera de este incremento y no se define aquí.

**Regla de conversión con Product:** cuando la unidad de almacenamiento y la base difieren, existe una conversión activa directa almacenamiento → base y `cantidad_origen × factor = cantidad_destino`. `dimension` solo describe la UoM; no prohíbe conversiones entre dimensiones distintas. “Unidad incompatible” requiere una política futura explícita y no se infiere de `dimension`.

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-CAT**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-24 — Gestionar ubicaciones

| Campo | Especificación |
|---|---|
| Actor principal | Administrador/Supervisor |
| RF | RF-24 |
| HU | US-24 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `GET /locations`, `GET /locations/{id}`, `POST /locations`, `PUT /locations/{id}`, `POST /locations/{id}/deactivate`, `POST /locations/{id}/reactivate`; no existe PATCH ni DELETE |
| Permiso baseline | Lectura: `INVENTORY_READ` o `LOCATION_MANAGE`; mutación: `LOCATION_MANAGE` (`10000000-0000-0000-0000-000000000016`) |
| Eventos/asíncronos | `LocationChanged v1`, routing `inventory.location.changed.v1`; Audit central idempotente por `eventId` |
| Precondiciones | Jerarquía válida, versión esperada en PUT/lifecycle y padre activo cuando se introduce, cambia o reactiva |
| Postcondiciones | Árbol persistido sin ciclos; mutación efectiva y Outbox en el mismo commit |
| Excepciones relevantes | 400 `VALIDATION_ERROR`; 401 `AUTH_INVALID`; 403 `AUTH_FORBIDDEN`; 404 `LOCATION_NOT_FOUND`; 409 de datos, versión, jerarquía, descendientes, stock, uso o ubicación inactiva |
| Diagrama(s) | UML-04 |

**Flujo base técnico-funcional:**

1. La lista plana no pagina, ordena `code ASC,id ASC` y acepta solo `active=true|false|all` (defecto `true`); el detalle incluye activos e inactivos.
2. POST crea `active=true`, `version=0`. `code` es obligatorio, máximo 80, globalmente único, sensible a mayúsculas e inmutable; nombre es obligatorio y máximo 160. PUT reemplaza solo nombre, tipo y padre.
3. `parentId=null` define raíz y cualquier tipo canónico puede ser raíz; no existe matriz rígida de tipos. Al crear, reasignar o reactivar, el padre debe existir y estar activo. Se impiden auto-parent y ciclos profundos, también bajo escrituras concurrentes.
4. PUT, deactivate y reactivate exigen `expectedVersion>=0`; primero verifican versión y después no-op. Una versión obsoleta devuelve `VERSION_CONFLICT`. El no-op no cambia versión, `updatedAt` ni Outbox; una mutación efectiva incrementa versión exactamente una vez.
5. Desactivar no hace cascade y se rechaza si hay descendientes activos, stock positivo en el nodo o descendientes, o conteos `DRAFT`/`IN_PROGRESS` sobre ellos. Cantidad cero, conteos terminales y movimientos históricos no bloquean. Un nodo inactivo puede conservar un padre histórico inactivo sin cambios.
6. Reactivar conserva ID/código y exige padre activo y jerarquía válida. Cada mutación efectiva persiste Location + `LocationChanged v1` en una transacción; no-op o rechazo no emiten evento. La publicación es al menos una vez, con `eventId` estable y estado PUBLISHED solo tras confirm del broker.
7. Audit deduplica por `eventId` y mapea CREATED/UPDATED/DEACTIVATED/REACTIVATED a `LOCATION_CREATED`/`LOCATION_UPDATED`/`LOCATION_DEACTIVATED`/`LOCATION_REACTIVATED`, agregado `Location`, resultado `SUCCESS` y actor desde `actorUserId`. No genera notificaciones.

**Criterios de prueba mínimos:**

- Raíz/hijo válidos, padre inactivo, auto-parent, ciclo profundo y carrera de reparentado.
- Código duplicado/inmutable; actualización, no-op y versión obsoleta.
- Desactivación limpia; bloqueo por descendiente activo, stock positivo o conteo abierto; conteo histórico permitido.
- Reactivación y bloqueo por padre inactivo; lectura con ambos permisos y mutación solo con `LOCATION_MANAGE`.
- Outbox solo para cambio efectivo, publisher confirm/retry y Audit idempotente.

## CUS-25 — Gestionar lotes, series y activos

| Campo | Especificación |
|---|---|
| Actor principal | Encargado/Supervisor |
| RF | RF-27,RF-28 |
| HU | US-27,US-28 |
| Servicio responsable | MS-INV |
| Endpoint(s) | Operacional: `GET /api/v1/lots`, `GET /api/v1/assets`; administración: `/api/v1/admin/lots`, `/api/v1/admin/assets`, `POST/GET/PUT /api/v1/lots`, `POST/GET/PUT /api/v1/assets` y acciones `/status` |
| Permiso baseline | Selectores: `INVENTORY_READ`; lectura administrativa: `INVENTORY_READ OR TRACEABILITY_MANAGE`; mutación: `TRACEABILITY_MANAGE` |
| Eventos/asíncronos | `LotChanged v1` y `AssetChanged v1` hacia Audit; sin Notifications |
| Precondiciones | Producto requiere regla correspondiente |
| Postcondiciones | Lote/activo consistente con producto; ubicación actual del activo derivada de stock_balance |
| Excepciones relevantes | Serie duplicada, vencimiento requerido, lote inconsistente |
| Diagrama(s) | STATE-02; UML-04 |

**Selectores operacionales aprobados:** `GET /api/v1/lots` exige `productId`, admite `locationId`, `availableOnly=false`, `page=0` y `size=20` (`1..100`). Devuelve únicamente lotes `ACTIVE` sin vencimiento o con `expiresAt` mayor o igual a la fecha UTC vigente; agrega la cantidad desde `stock_balance`, la restringe por ubicación cuando se envía `locationId` y ordena por `lotNumber`, `heatNumber` e `id` con nulos al final. `GET /api/v1/assets` exige `productId` y `availability=UNASSIGNED|IN_STOCK`, admite `locationId`, `lotId` y la misma paginación; devuelve únicamente activos `OPERATIVO`, ordenados por `assetCode` e `id`. `UNASSIGNED` significa que no existe saldo positivo; `IN_STOCK`, que existe exactamente un saldo positivo con cantidad uno. Ambas consultas requieren `INVENTORY_READ` y no sustituyen las futuras operaciones administrativas protegidas por `TRACEABILITY_MANAGE`.

**Regla de uso en movimientos:** el requisito efectivo de lote es `requiresLot || requiresHeatNumber || requiresExpiry`; el requisito de activo es `requiresSerial`. En `ENTRY` y `ADJUST_POSITIVE`, los IDs seleccionados deben preexistir y corresponder al producto: este incremento no crea lotes ni activos. Un lote o activo previamente creado sin saldo positivo es válido y puede aparecer como no disponible/no asignado; su creación y el movimiento que lo usa son solicitudes independientes, por lo que no forman una única transacción distribuida.

**Administración de lotes aprobada:** `GET /api/v1/admin/lots` lista todos los estados con filtros opcionales `productId`, `status`, `expired`, `locationId`, `page=0` y `size=20` (`1..100`), en orden `createdAt DESC, id DESC`; `GET /api/v1/lots/{id}` obtiene detalle. `POST /api/v1/lots` crea sin stock en versión 0 y valida los flags locales del producto. `PUT /api/v1/lots/{id}` reemplaza únicamente fechas y exige `expectedVersion`; producto, lote y colada son inmutables. `POST /api/v1/lots/{id}/status` admite las transiciones manuales entre `ACTIVE`, `QUARANTINED` y `BLOCKED`, y `DEPLETED -> ACTIVE` solo con agregado cero y fecha válida. `EXPIRED` se deriva exclusivamente de `expiresAt < current UTC date`; `DEPLETED`, de una confirmación que lleva el agregado positivo a cero. Ninguno se selecciona manualmente. No existe DELETE.

**Administración de activos aprobada:** `GET /api/v1/admin/assets` lista todos los estados con filtros opcionales de producto, estado, disponibilidad, ubicación y lote; `GET /api/v1/assets/{id}` deriva ubicación/lote desde el único saldo positivo. `POST /api/v1/assets` registra en versión 0 y `OPERATIVO`, sin stock; `PUT /api/v1/assets/{id}` reemplaza marca, modelo y snapshot técnico. Producto, código y serie son inmutables. La acción `/status` aplica STATE-02 excepto que `EN_TRANSITO` queda reservado al futuro flujo asíncrono y nunca es target administrativo; `FUERA_SERVICIO` es terminal y exige saldo positivo cero. No hay DELETE, ubicación editable ni custodia (`ASSET_CUSTODY_DEFERRED`).

**Concurrencia y eventos:** toda mutación administrativa comprueba `expectedVersion` antes del no-op, incrementa una vez por cambio efectivo y devuelve `409 VERSION_CONFLICT` si está obsoleta. No-op, rechazo y conflicto no escriben Outbox. El cambio efectivo y `LotChanged v1` (`inventory.lot.changed.v1`) o `AssetChanged v1` (`inventory.asset.changed.v1`) se confirman en la misma transacción. Audit deduplica por `eventId` y mapea a `LOT_CREATED|LOT_UPDATED|LOT_STATUS_CHANGED` o `ASSET_REGISTERED|ASSET_UPDATED|ASSET_STATUS_CHANGED`; no se generan notificaciones.

**Deuda Web planificada:** `ApiLotRepository` y `ApiAssetRepository` continúan siendo adaptadores de selectores operacionales; no representan todavía la administración contratada. La futura integración Remote debe usar un puerto/adaptador administrativo explícito, sin fallback Demo. La pantalla de Maquinaria tampoco puede derivar activos físicos desde Product ni usar `DemoResponsibleRepository` como autoridad: custodia, responsable, asignación y devolución permanecen diferidos.

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-26 — Adjuntar/consultar evidencia

| Campo | Especificación |
|---|---|
| Actor principal | Usuario autorizado |
| RF | RF-30 |
| HU | US-30 |
| Servicio responsable | MS-EVI |
| Endpoint(s) | `POST /api/v1/evidences; GET /evidences?ownerType&ownerId&page&size; GET /evidences/{id}; GET /evidences/{id}/content` |
| Permiso baseline | `EVIDENCE_WRITE/EVIDENCE_READ` |
| Eventos/asíncronos | EvidenceUploaded |
| Precondiciones | `ownerType=MOVEMENT`; ownerId existente y visible en Inventory; JWT `sub` UUID y permiso Evidence; Idempotency-Key UUID en upload |
| Postcondiciones | Objeto privado + metadata/hash + ownerType/ownerId + EvidenceUploaded vía Outbox |
| Excepciones relevantes | owner inválido/inaccesible, key conflictiva, MIME/magic/size/metadata inválido, owner service o storage no disponible; compensación de objeto tras rollback |
| Diagrama(s) | SEQ-10; BPMN-06 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-EVI**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-27 — Autorizar movimiento pendiente

| Campo | Especificación |
|---|---|
| Actor principal | Autorizador |
| RF | RF-29 |
| HU | US-29 |
| Servicio responsable | MS-INV + MS-IAM |
| Endpoint(s) | `POST /movements/{id}/authorize|reject` |
| Permiso baseline | `MOVEMENT_AUTHORIZE` |
| Eventos/asíncronos | SensitiveMovementConfirmed solo al confirmar |
| Precondiciones | Movimiento PENDIENTE_AUTORIZACION; `MOVEMENT_AUTHORIZE`; step-up válido; autorizador distinto de `registered_by_user_id` |
| Postcondiciones | Estado AUTORIZADO o RECHAZADO sin efecto stock |
| Excepciones relevantes | MFA no reciente, permiso insuficiente, violación maker-checker, estado inválido |
| Diagrama(s) | SEQ-07; BPMN-05 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV + MS-IAM**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-28 — Registrar conteo físico

| Campo | Especificación |
|---|---|
| Actor principal | Supervisor/Encargado |
| RF | RF-33 |
| HU | US-33 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `POST/GET /api/v1/counts`; detalle, captura de líneas, cierre y cancelación bajo `/api/v1/counts/{id}` |
| Permiso baseline | `INVENTORY_COUNT` |
| Eventos/asíncronos | Ninguno propio; ajuste confirmado conserva `MovementConfirmed v1` |
| Precondiciones | Ubicación válida; snapshot por ubicación; actor desde JWT `sub` |
| Postcondiciones | Diferencias históricas almacenadas sin mutar stock; ajuste posterior explícito y separado |
| Excepciones relevantes | Versión obsoleta/transición inválida/conteo incompleto/referencia inválida |
| Diagrama(s) | BPMN-04 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Contrato MVP cerrado:** `DRAFT -> IN_PROGRESS -> COMPLETED` o cancelación desde estado abierto; un snapshot vacío puede cerrar directamente `DRAFT -> COMPLETED`. La creación captura todas las dimensiones de saldo de una ubicación; `countedQuantity` se completa por línea y PostgreSQL deriva `differenceQuantity`. Las mutaciones usan versión optimista. El cierre no relee ni modifica stock, no crea un ajuste y no exige autorización adicional. La regularización posterior es una acción explícita mediante el flujo existente de ajustes. `INVENTORY_COUNT` (`10000000-0000-0000-0000-000000000015`) corresponde a `ADMIN`, `ENCARGADO` y `SUPERVISOR`; los actores se derivan exclusivamente de `sub`.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-29 — Registrar tipo de cambio

| Campo | Especificación |
|---|---|
| Actor principal | Usuario autorizado |
| RF | RF-31 |
| HU | US-31 |
| Servicio responsable | MS-INV / adapter externo |
| Endpoint(s) | `GET external vía ExchangeRatePort; entrada permite manual` |
| Permiso baseline | `EXCHANGE_RATE_WRITE` |
| Eventos/asíncronos | Audit de fuente/override |
| Precondiciones | Moneda != PEN y fecha válida |
| Postcondiciones | TC, fuente y fecha quedan snapshot en movimiento |
| Excepciones relevantes | Proveedor no disponible => fallback manual autorizado |
| Diagrama(s) | SEQ-04 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV / adapter externo**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Criterios de prueba mínimos:**

- Camino exitoso con permisos válidos.
- Validación de entrada y permiso insuficiente.
- Estado/recurso inexistente o conflicto de dominio cuando aplique.
- Reintento/idempotencia/concurrencia si el caso produce efectos críticos.
- Verificación de auditoría/evento cuando sea parte de la postcondición.

## CUS-30 — Consultar notificaciones

| Campo | Especificación |
|---|---|
| Actor principal | Usuario autorizado |
| RF | RF-12,RF-32 |
| HU | US-32 |
| Servicio responsable | MS-AUD |
| Endpoint(s) | `GET /api/v1/notifications`; `GET /api/v1/notifications/unread-count`; `POST /api/v1/notifications/{id}/read` |
| Permiso baseline | `AUTHENTICATED` |
| Eventos/asíncronos | MVP consume `MovementConfirmed v1` (`inventory.movement.confirmed.v1`) |
| Precondiciones | Usuario activo |
| Postcondiciones | El registrador recibe una notificación personal; `readAt` representa leído/no leído; polling MVP |
| Excepciones relevantes | 400 paginación inválida; 401 sin autenticación; 404 para ID inexistente o ajeno; evento duplicado no duplica notificación |
| Diagrama(s) | SEQ-12 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-AUD**.
3. El servicio valida el JWT y deriva el usuario exclusivamente de `sub`; no existe permiso IAM adicional ni usuario actuante declarado por el cliente.
4. Lista y cuenta solo filas propias, con página 0/20, máximo 100 y orden `createdAt DESC, id DESC`.
5. `POST /notifications/{id}/read` asigna `readAt` una sola vez; una repetición es exitosa y un ID ajeno se trata como 404.
6. El consumidor crea una notificación para `registeredByUserId` dentro de la misma transacción que reclama `processed_event`; hace ACK después del commit.

**Criterios de prueba mínimos:**

- 401 sin JWT y aislamiento estricto por `sub`.
- Lista vacía, filtro unread, conteo, paginación y orden estable.
- 400 para página/tamaño inválidos y 404 anti-enumeración para un ID ajeno.
- Marcado repetido conserva el primer `readAt`.
- Redelivery/concurrencia no duplica la notificación; rollback revierte dedup y fila.
- Retry acotado, DLQ y ACK solo después del commit.

# Anexo — Reglas reforzadas de CUS críticos

## CUS-07/CUS-08/CUS-09/CUS-10 — frontera ACID

Para entrada, salida, transferencia y ajuste, **stock, costo aplicado, movimiento, detalles e inserción del evento Outbox deben formar parte del mismo commit local de `inventory-service`**. Las salidas/transferencias/ajustes que consumen existencia bloquean las filas concretas mediante `SELECT ... FOR UPDATE`; después del lock se revalida cantidad, lote, serie/activo y ubicación. El aislamiento base es `READ COMMITTED`; no se eleva todo PostgreSQL a `SERIALIZABLE`. Toda excepción antes de `COMMIT` produce rollback.

## CUS-27 — autorización no reserva stock

`AUTORIZADO` expresa aprobación humana/técnica, no reserva inventario. Entre autorización y confirmación puede cambiar el stock; por eso la confirmación revalida y puede devolver 409. Esto evita que el sistema prometa una existencia que ya no está disponible.

## CUS-26 — integridad y owner de archivo

El binario se almacena en MinIO/GCS; PostgreSQL conserva `owner_type`, `owner_id`, `object_key`, nombre original, MIME, tamaño, SHA-256, proveedor, usuario, fecha, estado y metadata JSONB opcional. `owner_id` es referencia UUID externa sin FK cross-schema. La aplicación debe evitar objetos huérfanos y referencias sin objeto; metadata + `evidence.outbox_event` se confirman localmente y los accesos son privados/autorizados.

## CUS-05/CUS-23 — conversiones canónicas

`catalog.product` conserva unidad de almacenamiento/base y `catalog.unit_conversion` permite N conversiones por producto. `ProductCreated/Updated` actualiza `inventory.product_ref` y `inventory.product_unit_conversion_ref`; `SupplierCreated/Updated/Disabled` actualiza `inventory.supplier_ref`. `inventory.processed_event` evita repetir el efecto.

## CUS-25 — ubicación y serialización

`inventory.asset` no guarda ubicación actual. Esta se obtiene de `stock_balance`; un activo solo puede tener una existencia positiva y cantidad 0/1. Lote/activo siempre deben corresponder al mismo `product_id`.

## CUS-28 — conteo no muta stock

El conteo conserva cantidad sistema, cantidad contada y diferencia. Una regularización posterior usa `ADJUST_POSITIVE`/`ADJUST_NEGATIVE`; el conteo no altera directamente `stock_balance`.

## CUS-19 — interoperabilidad

El consumidor BI/ETL solo recibe lectura. No existe ruta para actualizar inventario desde BI. Las cargas incrementales utilizan claves estables y watermark/fecha de actualización; las fallas analíticas no interrumpen las transacciones del almacén.


---

# Anexo B. Casos de uso del negocio


| ID | Proceso | Actor de negocio | Entrada | Resultado | CUS que lo automatizan |
|---|---|---|---|---|---|
| CUN-01 | Recepcionar y almacenar | Proveedor externo, Encargado / recepción | Proveedor, documento, producto, cantidad, costo, trazabilidad | Existencia ubicada y recepción trazable con origen identificado | CUS-07, CUS-24, CUS-25, CUS-26, CUS-31 |
| CUN-02 | Despachar/consumir | Solicitante, Encargado, Autorizador | Solicitud, destino/centro de costo, stock | Salida confirmada o rechazo controlado | CUS-08, CUS-27, CUS-26 |
| CUN-03 | Transferir inventario | Encargado/Supervisor | Origen, destino, cantidad | Nueva distribución sin variar stock total | CUS-09, CUS-24 |
| CUN-04 | Regularizar inventario | Supervisor/Encargado | Conteo, diferencia, motivo | Ajuste autorizado y trazable | CUS-10, CUS-28, CUS-27 |
| CUN-05 | Controlar trazabilidad/activos | Almacén/Supervisión | Producto/lote/serie/ubicación | Reconstrucción física e histórica | CUS-06, CUS-11, CUS-25 |
| CUN-06 | Supervisar/auditar | Administración/Seguridad TI | Movimientos, logs funcionales, períodos | Indicadores, reportes y auditoría | CUS-13, CUS-17, CUS-18, CUS-20 |
| CUN-07 | Explotar/interoperar | Analista/BI | Datos transaccionales aprobados | Dataset/reporting read-only | CUS-19, CUS-29, CUS-30 |

## Diferencia metodológica

El **CUN** modela el proceso de la empresa sin asumir una pantalla o endpoint; el **CUS** modela la interacción concreta con SIGA. Un CUN puede involucrar varios CUS y actores. Por esa razón las matrices RF vs CUS y los BPMN se mantienen separadas de las especificaciones REST.

## Reglas para diagramar

- BPMN/activity: swimlanes por actor/unidad y SIGA cuando automatiza una actividad.
- Gateways solo para decisiones reales: stock suficiente, sensibilidad/autorización, validación de evidencia, etc.
- El resultado de un CUN no debe contradecir las reglas administrativas de inmutabilidad, trazabilidad o multiubicación.


## Gobierno de fuentes PlantUML — ADR-019

Los `.puml` ubicados en `diagramas/` son las **fuentes canónicas** para implementación, trazabilidad y agentes de IA. Los archivos de `diagramas_render/` son derivados de presentación y no deben utilizarse para inferir requisitos, relaciones, endpoints, eventos ni decisiones de dominio. Toda modificación funcional se realiza primero en el original v1.2, luego se regeneran los derivados con `tools/generar_derivados_visuales.py` y se valida la paridad con `tools/validar_fuentes_y_derivados.py`.

## Adenda v1.2 — Gestión de proveedores

La revisión docente incorpora **proveedores** con un cambio deliberadamente acotado. `catalog-service` es owner de `catalog.supplier`; `inventory-service` mantiene `inventory.supplier_ref` por eventos de Catalog para validar entradas sin REST síncrono durante el commit. Las recepciones de abastecimiento externo guardan `supplier_id`, `supplier_name_snapshot` y `supplier_tax_id_snapshot` en `inventory.movement`; Reporting replica estos campos en `analytics.movement_projection`.

El alcance se limita a alta/consulta/actualización/desactivación lógica de proveedores y a su asociación trazable con entradas. Permanecen fuera del MVP las órdenes de compra, cotizaciones, cuentas por pagar, homologación avanzada, portal de proveedor y un ERP de compras completo. Se conservan **seis servicios**, ownership por schema, cero FK cross-schema y la frontera ACID de Inventory.

Artefactos impactados: RF-35/US-35/CUS-31, CUN-01/CUS-07, Catalog OpenAPI, Inventory OpenAPI, modelo físico/lógico/diccionario, DER-01/02/03/05/06/09, UML-01/03/04/06/10/11, C4-04, BPMN-01, SEQ-04 y matrices de pruebas/trazabilidad.
