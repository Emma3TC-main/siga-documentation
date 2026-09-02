# Requerimientos SIGA

## RF
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
| RF-35 | Proveedores | Gestionar proveedores básicos y asociarlos a entradas de abastecimiento externo preservando identificación histórica. | US-35 | CUS-31/CUS-07 |

## RNF
| ID | Categoría | Criterio | Sprint |
|---|---|---|---|
| RNF-01 | Credenciales | Argon2id; nunca texto plano. | Sprint 2 |
| RNF-02 | Autorización | Backend protege toda función por roles/permisos. | Sprint 2 |
| RNF-03 | Config segura | Secretos fuera del código. | Sprint 2-4 |
| RNF-04 | Comunicación | HTTPS externo; servicios internos no públicos. | Sprint 3-4 |
| RNF-05 | Integridad | Nunca stock negativo ni confirmación parcial. | Sprint 3 |
| RNF-06 | Trazabilidad | Actor, fecha, ubicación, producto, cantidad, lote/serie, proveedor cuando aplique y sustento. | Sprint 3 |
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
