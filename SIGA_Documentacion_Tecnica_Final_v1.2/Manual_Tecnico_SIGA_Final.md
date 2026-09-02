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
| DRAFT | BORRADOR | submit sensible | PENDING_AUTHORIZATION | Sin efecto |
| DRAFT | BORRADOR | confirm no sensible + válido | CONFIRMED | Atómico |
| DRAFT | BORRADOR | cancel antes de confirmar | CANCELLED | Sin efecto |
| PENDING_AUTHORIZATION | PENDIENTE_AUTORIZACION | authorize + permiso + step-up | AUTHORIZED | Sin efecto |
| PENDING_AUTHORIZATION | PENDIENTE_AUTORIZACION | reject | REJECTED | Sin efecto |
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
PK UUID + códigos humanos independientes (`SKU`, `MOV-YYYY-NNNNN`, `MAQ-NNNN`). Los UUID que referencian otro bounded context se conservan como columnas sin FK cross-schema.

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
`inventory.product_ref` contiene SKU, tipo, unidades, stock mínimo y flags de trazabilidad necesarios para confirmar movimientos sin dependencia REST. `inventory.product_unit_conversion_ref` conserva conversiones aplicables. `inventory.supplier_ref` conserva la referencia mínima de proveedor requerida para validar recepciones externas. Estas proyecciones se actualizan con eventos de Catalog (`ProductCreated/Updated` y `SupplierCreated/Updated/Disabled`); `inventory.processed_event` hace idempotente el consumidor.

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
| GET/POST | /api/v1/users | IAM | Usuarios |
| GET/POST | /api/v1/roles | IAM | Roles/permisos |
| GET/POST | /api/v1/products | CAT | Productos |
| GET/POST | /api/v1/categories | CAT | Categorías |
| GET/POST | /api/v1/units | CAT | UoM |
| GET/POST | /api/v1/suppliers | CAT | Proveedores |
| GET/PUT | /api/v1/suppliers/{id} | CAT | Consulta/actualización de proveedor |
| GET | /api/v1/inventory | INV | Stock |
| GET/POST | /api/v1/locations | INV | Ubicaciones |
| GET | /api/v1/lots | INV | Lotes/coladas/vencimientos |
| GET | /api/v1/assets | INV | Activos serializados |
| POST | /api/v1/movements | INV | Borrador multi-detalle |
| POST | /api/v1/movements/{id}/submit | INV | Evaluar autorización |
| POST | /api/v1/movements/{id}/authorize | INV | Autorizar |
| POST | /api/v1/movements/{id}/confirm | INV | Commit idempotente |
| POST | /api/v1/movements/{id}/reject | INV | Rechazar |
| POST | /api/v1/movements/{id}/cancel | INV | Cancelar antes de confirmar |
| POST | /api/v1/counts | INV | Conteo |
| POST | /api/v1/evidences | EVI | Upload multipart |
| GET | /api/v1/audit-events | AUD | Auditoría |
| GET | /api/v1/notifications | AUD | Notificaciones |
| GET | /api/v1/dashboard | REP | Dashboard |
| POST | /api/v1/reports | REP | Reporte |
| GET | /api/v1/analytics/exports | REP | ETL read-only |

## 6.6 OpenAPI
Un YAML por microservicio, consolidado en versión 1.1. Los contratos incluyen DTOs de IAM/RBAC, conversiones múltiples, movimientos con snapshots, conteos, Evidence con owner genérico, filtros de auditoría y read models/report jobs. Frontend puede generar tipos; `generated` no se edita. Cambios de contrato actualizan tests/consumidores. Swagger UI solo DEV/QA o restringido.

## 6.7 Problem Details
application/problem+json: type,title,status,code,detail,instance,correlationId. 400 validación, 401,403,404,409 dominio/idempotencia,422 opcional,429,500,503. Sin stack traces.

## 6.8 Idempotencia
Comandos críticos aceptan Idempotency-Key UUID. Se persiste request hash + respuesta. Misma key/payload devuelve resultado previo sin segundo efecto; misma key/payload distinto =>409. Retención/limpieza configurables.

# 7. Seguridad e identidad

## 7.1 JWT RS256
MS-IAM firma con clave privada; Gateway/servicios validan pública/JWKS. Access 30 min; refresh 7 días con rotación y revocación. Usuario desactivado no renueva.

## 7.2 TOTP/step-up
TOTP RFC 6238: 30s, ventana ±1, 5 intentos baseline. MFA obligatorio para privilegiados y configurable; operaciones sensibles pueden pedir step-up reciente.

## 7.3 Argon2id
Principal para contraseñas. Parámetros se calibran por entorno. Fallback BCrypt solo por incompatibilidad. Política baseline: mínimo 12 caracteres, passphrases permitidas, sin rotación arbitraria periódica.

## 7.4 RBAC
Usuario N:M Rol N:M Permiso. Ejemplos INVENTORY_READ, MOVEMENT_CREATE, MOVEMENT_AUTHORIZE, INVENTORY_ADJUST, PRODUCT_WRITE, AUDIT_READ, REPORT_READ, USER_MANAGE, ROLE_MANAGE.

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
MVP in-app. Web: polling inicial, SSE futuro. Móvil: refresh/polling/pull-to-refresh. No WebSocket sin necesidad bidireccional.

# 10. Evidencias, documentos y multimedia

## 10.1 Almacenamiento
No MongoDB/GridFS ni otra NoSQL solo por archivos. La necesidad es object storage: `ObjectStoragePort` con MinIO local/dev y GCS objetivo. PostgreSQL guarda metadata/JSONB opcional; Redis no guarda documentos.

## 10.2 Metadata y propiedad
`evidence.evidence_metadata` conserva: UUID, `owner_type`, `owner_id`, `object_key`, nombre original, MIME, tamaño, SHA-256, proveedor, `uploaded_by_user_id`, estado, timestamps y metadata JSONB opcional.

`owner_type` admite `MOVEMENT`, `ASSET`, `ADJUSTMENT` y `REPORT`. `owner_id` es una referencia UUID externa deliberadamente sin FK cross-schema. Así la evidencia deja de estar acoplada únicamente a Movement y cubre las rutas de almacenamiento ya definidas.

## 10.3 Organización

```text
siga-evidences/
├── movements/<year>/<movement-id>/<evidence-id>.<ext>
├── assets/<asset-id>/...
├── adjustments/<movement-id>/...
└── reports/<year>/<report-id>.<ext>
```

Object keys se generan internamente. GCS aplica IAM/versioning/lifecycle/cifrado administrado. MinIO puede versionar en desarrollo.

## 10.4 Reportes persistentes vs temporales
Reportes normales pueden ser temporales. Reportes oficiales/auditables se guardan con filtros, usuario, fecha, hash y metadata. La relación con Evidence usa `owner_type=REPORT`. SEQ-13 documenta el flujo.

## 10.5 Consistencia de evidencia
El alta de metadata y `evidence.outbox_event` se confirma localmente; `EvidenceUploaded` se publica por Outbox. Si la escritura del objeto o la persistencia de metadata falla, el caso debe compensar/limpiar el objeto según política para evitar huérfanos. SHA-256, MIME y magic bytes son controles de integridad, no sustitutos de autorización.


# 11. Eventos, mensajería y notificaciones

## 11.1 RabbitMQ
Elegido sobre Kafka porque SIGA requiere mensajería confiable de volumen moderado, no streaming masivo. Menor complejidad y soporte de exchanges/colas/ACK/retry/DLQ.

## 11.2 Eventos base

| Evento | Productor | Consumidor | Uso |
|---|---|---|---|
| ProductCreated/Updated | CAT | INV, REP | Proyección local |
| SupplierCreated/Updated/Disabled | CAT | INV, REP | Proyección local de proveedor |
| StockBelowMinimum | INV | AUD, REP | Alerta/dashboard |
| StockDepleted | INV | AUD, REP | Alerta crítica |
| MovementConfirmed | INV | AUD, REP | Auditoría/analytics |
| SensitiveMovementConfirmed | INV | AUD | Control reforzado |
| InventoryAdjusted | INV | AUD, REP | Control ajuste |
| EvidenceUploaded | EVI | AUD | Trazabilidad documental |
| ProductExpiringSoon | INV | AUD, REP | Alerta programada |
| IntegrationFailed | Cualquiera | AUD | Visibilidad operativa |

## 11.3 Envelope

```json
{
  "eventId":"uuid","eventType":"MovementConfirmed","schemaVersion":1,
  "aggregateType":"Movement","aggregateId":"uuid","occurredAt":"ISO-8601",
  "correlationId":"uuid","causationId":"uuid","producer":"inventory-service","payload":{}
}
```

## 11.4 Transactional Outbox por productor
El patrón aplica a todo servicio que produce eventos relevantes: `iam.outbox_event`, `catalog.outbox_event`, `inventory.outbox_event` y `evidence.outbox_event`. Cada tabla pertenece al mismo schema que el agregado modificado. No existe Outbox compartido.

En Inventory, el mismo commit que stock/movimiento inserta `inventory.outbox_event`. En Catalog, producto/conversiones + outbox se confirman localmente; en IAM, usuario/RBAC + outbox; en Evidence, metadata + outbox. Si RabbitMQ cae, el negocio confirmado permanece correcto y el publisher reintenta, eliminando la ventana DB-commit/event-lost.

## 11.5 Consumidor idempotente por ownership
RabbitMQ puede redeliver. Cada consumidor registra `event_id` procesado en **su propio schema** y los duplicados se ACK sin repetir efectos: `inventory.processed_event` para la proyección de Catalog, `audit.processed_event` para auditoría/notificaciones y `analytics.processed_event` para read models. Ningún consumidor escribe la tabla `processed_event` de otro servicio.

## 11.6 Confiabilidad
Durable exchange/queue, persistent messages, publisher confirms, ACK manual, retry/backoff y DLQ. DLQ>0 genera alerta. Management no público.

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

Los consumidores actualizan las proyecciones a partir de eventos versionados. `analytics.processed_event` evita duplicados. Una caída de Reporting no bloquea la confirmación de stock.

## 12.2 Reportes
Inventario consolidado, Kardex, activos, lotes/vencimientos, movimientos, reposición, consumo por centro de costo, ajustes/sensibles, valorización, ubicación y exactitud. PDF/XLSX/CSV, filtros server-side. `movement_projection` conserva el snapshot de centro de costo requerido para ese análisis.

## 12.3 ETL/ELT e interoperabilidad
UUID estables, timestamps, dimensiones Producto/Categoría/Ubicación/CentroCosto/Fecha y hechos Movimiento/Existencia/Valorización. Soft delete e historia preservan cargas incrementales. Moneda original/TC/PEN enriquecen análisis.

`export_checkpoint` permite extracción incremental controlada. BI/ETL recibe acceso read-only vía API/export; no credenciales de escritura a Inventory. En una evolución se pueden añadir read replica/materialized views sin cambiar la autoridad del OLTP.

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
| UI-W06 | Categorías | /catalog/categories | Admin | CRUD | /categories |
| UI-W07 | Productos | /catalog/products | Admin/Encargado | SKU/UoM/JSONB/trazabilidad | /products |
| UI-W08 | Unidades | /catalog/units | Admin | UoM/conversión | /units |
| UI-W09 | Inventario | /inventory | Autorizado | Stock/filtros/ubicación | GET /inventory |
| UI-W10 | Ubicaciones | /locations | Admin/Supervisor | Árbol jerárquico | /locations |
| UI-W11 | Lotes/Activos | /lots /assets | Encargado | Lote/serie/estado | inventory |
| UI-W12 | Nuevo movimiento | /movements/new | Encargado | Cabecera + N detalles | POST /movements |
| UI-W13 | Detalle | /movements/:id | Autorizado | Estado/detalles/evidencia | GET movement |
| UI-W14 | Autorizar | /movements/:id/authorize | Autorizador | Resumen/step-up | authorize/reject |
| UI-W15 | Transferencia | /movements/new?type=TRANSFER | Encargado/Supervisor | Origen/destino | POST movement |
| UI-W16 | Ajuste | /adjustments | Supervisor/Admin | Motivo/evidencia | POST movement |
| UI-W17 | Conteo | /counts | Supervisor/Encargado | Conteo/diferencia | POST counts |
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
| Endpoint(s) | `GET/POST/PATCH /api/v1/users` |
| Permiso baseline | `USER_MANAGE` |
| Eventos/asíncronos | Audit: UserCreated/UserUpdated/UserDisabled |
| Precondiciones | Sesión privilegiada |
| Postcondiciones | Usuario creado/actualizado/desactivado sin perder trazabilidad |
| Excepciones relevantes | Duplicado, validación, intento de autodesactivación no permitida por política |
| Diagrama(s) | UML-02 |

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
| Endpoint(s) | `GET/POST/PATCH /api/v1/roles; /permissions` |
| Permiso baseline | `ROLE_MANAGE` |
| Eventos/asíncronos | Audit: RoleChanged |
| Precondiciones | MFA privilegiado; catálogo de permisos |
| Postcondiciones | RBAC actualizado; sesiones nuevas reflejan permisos |
| Excepciones relevantes | Rol protegido, permiso inexistente, conflicto de asignación |
| Diagrama(s) | UML-02 |

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
| Endpoint(s) | `GET/POST/PATCH /api/v1/products` |
| Permiso baseline | `PRODUCT_WRITE` |
| Eventos/asíncronos | ProductCreated; ProductUpdated |
| Precondiciones | Categoría/UoM válidas |
| Postcondiciones | Producto persistido y proyectable a Inventory |
| Excepciones relevantes | SKU duplicado, factor inválido, flags contradictorios |
| Diagrama(s) | SEQ-03; UML-03 |

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
| Endpoint(s) | `PATCH /api/v1/products/{id}` |
| Permiso baseline | `PRODUCT_WRITE` |
| Eventos/asíncronos | ProductUpdated |
| Precondiciones | Producto activo |
| Postcondiciones | Umbral persistido y proyectado |
| Excepciones relevantes | Valor negativo/incompatible |
| Diagrama(s) | UML-03 |

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
| Actor principal | Administrador/Supervisor |
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
| Endpoint(s) | `GET/POST/PATCH /api/v1/units; conversiones versionadas con Product` |
| Permiso baseline | `PRODUCT_WRITE` |
| Eventos/asíncronos | ProductUpdated |
| Precondiciones | Magnitud/unidad válidas |
| Postcondiciones | Una o más conversiones from/to/factor>0 persistidas y proyectables a Inventory |
| Excepciones relevantes | Factor <=0, unidad incompatible |
| Diagrama(s) | UML-03 |

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
| Endpoint(s) | `GET/POST/PATCH /api/v1/locations` |
| Permiso baseline | `LOCATION_MANAGE` |
| Eventos/asíncronos | Audit de cambio maestro |
| Precondiciones | Jerarquía válida |
| Postcondiciones | Árbol persistido sin ciclos |
| Excepciones relevantes | parent inválido, ciclo, desactivar ubicación con stock según política |
| Diagrama(s) | UML-04 |

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

## CUS-25 — Gestionar lotes, series y activos

| Campo | Especificación |
|---|---|
| Actor principal | Encargado/Supervisor |
| RF | RF-27,RF-28 |
| HU | US-27,US-28 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `GET/POST /lots; GET/POST/PATCH /assets` |
| Permiso baseline | `TRACEABILITY_MANAGE` |
| Eventos/asíncronos | Eventos/audit selectivos |
| Precondiciones | Producto requiere regla correspondiente |
| Postcondiciones | Lote/activo consistente con producto; ubicación actual del activo derivada de stock_balance |
| Excepciones relevantes | Serie duplicada, vencimiento requerido, lote inconsistente |
| Diagrama(s) | STATE-02; UML-04 |

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
| Endpoint(s) | `POST /api/v1/evidences; GET /evidences/{id}` |
| Permiso baseline | `EVIDENCE_WRITE/EVIDENCE_READ` |
| Eventos/asíncronos | EvidenceUploaded |
| Precondiciones | ownerType MOVEMENT/ASSET/ADJUSTMENT/REPORT y ownerId autorizados |
| Postcondiciones | Objeto privado + metadata/hash + ownerType/ownerId + EvidenceUploaded vía Outbox |
| Excepciones relevantes | MIME/magic/size inválido, storage falla; no metadata huérfana |
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

## CUS-27 — Autorizar movimiento sensible

| Campo | Especificación |
|---|---|
| Actor principal | Autorizador |
| RF | RF-29 |
| HU | US-29 |
| Servicio responsable | MS-INV + MS-IAM |
| Endpoint(s) | `POST /movements/{id}/authorize|reject` |
| Permiso baseline | `MOVEMENT_AUTHORIZE` |
| Eventos/asíncronos | SensitiveMovementConfirmed solo al confirmar |
| Precondiciones | Movimiento PENDIENTE_AUTORIZACION; step-up válido |
| Postcondiciones | Estado AUTORIZADO o RECHAZADO sin efecto stock |
| Excepciones relevantes | MFA no reciente, permiso insuficiente, estado inválido |
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
| Endpoint(s) | `POST /api/v1/counts` |
| Permiso baseline | `INVENTORY_COUNT` |
| Eventos/asíncronos | InventoryAdjusted si deriva ajuste |
| Precondiciones | Ubicación/alcance del conteo definidos |
| Postcondiciones | Diferencias almacenadas; ajuste posterior separado |
| Excepciones relevantes | Conteo duplicado/estado cerrado/dato inválido |
| Diagrama(s) | BPMN-04 |

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
| Endpoint(s) | `GET /api/v1/notifications; PATCH read` |
| Permiso baseline | `AUTHENTICATED` |
| Eventos/asíncronos | Consume StockBelowMinimum/ProductExpiringSoon/etc. |
| Precondiciones | Usuario activo |
| Postcondiciones | Notificaciones in-app leídas/no leídas; polling MVP |
| Excepciones relevantes | Evento duplicado no duplica notificación por idempotencia |
| Diagrama(s) | SEQ-12 |

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
