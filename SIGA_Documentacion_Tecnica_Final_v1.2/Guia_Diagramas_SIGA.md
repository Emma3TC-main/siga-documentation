# Guía de Diagramas — SIGA

Esta guía relaciona cada fuente PlantUML con su propósito, ubicación sugerida y lectura esperada. Los `.puml` son **fuente versionable**; la imagen PNG/SVG renderizada debe insertarse en Word/Figma/informe sin sustituir la fuente. Todos usan PlantUML puro y no dependen de includes remotos.

## Convención de trabajo

1. Editar el `.puml` correspondiente en `siga-documentation`. 2. Renderizar a PNG/SVG con PlantUML local/plugin/CI. 3. Verificar legibilidad. 4. Insertar la imagen donde indica esta guía. 5. Mantener el mismo ID en pie de figura, commits y referencias del informe. 6. Si cambia arquitectura/regla crítica, actualizar PlantUML + ADR + matriz asociada.

## Catálogo maestro

| Fuente | Diagrama | Ubicación sugerida | Qué debe explicar el texto que acompaña la figura |
|---|---|---|---|
| `diagramas/bpmn/BPMN_01_Entrada.puml` | BPMN-01 — Proceso de negocio: Entrada / recepción | Capítulo 8 del informe — procesos/CUN | Explicar responsables por swimlane, decisiones de negocio, entradas/salidas y qué actividades son automatizadas por SIGA. |
| `diagramas/bpmn/BPMN_02_Salida.puml` | BPMN-02 — Proceso de negocio: Salida / despacho | Capítulo 8 del informe — procesos/CUN | Explicar responsables por swimlane, decisiones de negocio, entradas/salidas y qué actividades son automatizadas por SIGA. |
| `diagramas/bpmn/BPMN_03_Transferencia.puml` | BPMN-03 — Proceso de negocio: Transferencia interna | Capítulo 8 del informe — procesos/CUN | Explicar responsables por swimlane, decisiones de negocio, entradas/salidas y qué actividades son automatizadas por SIGA. |
| `diagramas/bpmn/BPMN_04_Ajuste.puml` | BPMN-04 — Proceso de negocio: Ajuste de inventario | Capítulo 8 del informe — procesos/CUN | Explicar responsables por swimlane, decisiones de negocio, entradas/salidas y qué actividades son automatizadas por SIGA. |
| `diagramas/bpmn/BPMN_05_Autorizacion_Sensible.puml` | BPMN-05 — Autorización de movimiento sensible | Capítulo 8 del informe — procesos/CUN | Explicar responsables por swimlane, decisiones de negocio, entradas/salidas y qué actividades son automatizadas por SIGA. |
| `diagramas/bpmn/BPMN_06_Evidencia.puml` | BPMN-06 — Gestión de evidencia digital | Capítulo 8 del informe — procesos/CUN | Explicar responsables por swimlane, decisiones de negocio, entradas/salidas y qué actividades son automatizadas por SIGA. |
| `diagramas/bpmn/BPMN_07_Reporte.puml` | BPMN-07 — Generación de reporte / analítica | Capítulo 8 del informe — procesos/CUN | Explicar responsables por swimlane, decisiones de negocio, entradas/salidas y qué actividades son automatizadas por SIGA. |
| `diagramas/c4/C4_01_Contexto.puml` | C4-01 — Contexto del sistema SIGA | Capítulo 3 — Arquitectura del sistema | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/c4/C4_02_Contenedores_Docker_GCP.puml` | C4-02 — Contenedores: baseline Docker Compose sobre GCP | Capítulo 3 — Arquitectura del sistema | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/c4/C4_03_Contenedores_Kubernetes.puml` | C4-03 — Arquitectura objetivo Kubernetes / GKE | Capítulo 3 — Arquitectura del sistema | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/c4/C4_04_Componente_Inventory.puml` | C4-04 — Componentes internos de MS-INV (Inventory Core) | Capítulo 3 — Arquitectura del sistema | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/c4/C4_05_Componente_Identity.puml` | C4-05 — Componentes internos de MS-IAM | Capítulo 3 — Arquitectura del sistema | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/datos/DER_01_Conceptual.puml` | DER-01 — Modelo conceptual global | Capítulos 17-18 — modelo de datos | Explicar entidades de negocio, cardinalidades y relaciones semánticas entre bounded contexts; las líneas cross-context no son FK físicas. |
| `diagramas/datos/DER_02_Logico.puml` | DER-02 — Modelo lógico global por bounded contexts | Capítulos 17-18 — modelo lógico | Mostrar los 40 objetos lógicos agrupados por ownership y diferenciar FK local, UUID externo, evento y proyección. |
| `diagramas/datos/DER_03_Fisico.puml` | DER-03 — PostgreSQL físico por schemas | Capítulo 17 — arquitectura de datos | Mostrar los seis schemas, cantidad de tablas, ownership y flujo de eventos sin saturar con columnas. |
| `diagramas/datos/DER_04_Fisico_IAM.puml` | DER-04 — Físico IAM | Capítulo 17 — seguridad/datos | Usuarios, RBAC, refresh y Outbox; MFA/bloqueo permanecen en user_account. |
| `diagramas/datos/DER_05_Fisico_Catalog.puml` | DER-05 — Físico Catalog | Capítulo 17 — catálogo/datos | Proveedores, productos, UoM y conversiones múltiples con FK locales y Outbox. |
| `diagramas/datos/DER_06_Fisico_Inventory.puml` | DER-06 — Físico Inventory Core | Capítulos 17-18 — núcleo transaccional | Stock, trazabilidad, movimientos, autorizaciones, conteos, idempotencia, processed-event y Outbox; resaltar invariantes ACID. |
| `diagramas/datos/DER_07_Fisico_Evidence.puml` | DER-07 — Físico Evidence | Capítulo 17 — evidencia | owner_type/owner_id, integridad SHA-256, storage provider y Outbox. |
| `diagramas/datos/DER_08_Fisico_Audit_Notification.puml` | DER-08 — Físico Audit/Notification | Capítulo 17 — auditoría | Audit append-only, notificaciones e idempotencia de consumidor. |
| `diagramas/datos/DER_09_Fisico_Reporting_Analytics.puml` | DER-09 — Físico Reporting/Analytics | Capítulo 17 — analítica | Read models, KPI, report jobs, processed-event y export checkpoints; no autoridad de stock. |
| `diagramas/devops/DEVOPS_01_GitFlow.puml` | DEVOPS-01 — GitFlow simplificado por repositorio | Capítulos 13-16 y 22-24 — Git/CI-CD/despliegue/operación | Explicar objetivo operativo, qué corresponde al MVP y qué es evolución; incluir controles de seguridad/rollback/observabilidad pertinentes. |
| `diagramas/devops/DEVOPS_02_CICD.puml` | DEVOPS-02 — Pipeline CI/CD GitHub Actions | Capítulos 13-16 y 22-24 — Git/CI-CD/despliegue/operación | Explicar objetivo operativo, qué corresponde al MVP y qué es evolución; incluir controles de seguridad/rollback/observabilidad pertinentes. |
| `diagramas/devops/DEVOPS_03_Deployment_Docker.puml` | DEVOPS-03 — Deployment baseline Docker Compose | Capítulos 13-16 y 22-24 — Git/CI-CD/despliegue/operación | Explicar objetivo operativo, qué corresponde al MVP y qué es evolución; incluir controles de seguridad/rollback/observabilidad pertinentes. |
| `diagramas/devops/DEVOPS_04_Deployment_K8s.puml` | DEVOPS-04 — Deployment objetivo GKE | Capítulos 13-16 y 22-24 — Git/CI-CD/despliegue/operación | Explicar objetivo operativo, qué corresponde al MVP y qué es evolución; incluir controles de seguridad/rollback/observabilidad pertinentes. |
| `diagramas/devops/DEVOPS_05_Observabilidad.puml` | DEVOPS-05 — Observabilidad | Capítulos 13-16 y 22-24 — Git/CI-CD/despliegue/operación | Explicar objetivo operativo, qué corresponde al MVP y qué es evolución; incluir controles de seguridad/rollback/observabilidad pertinentes. |
| `diagramas/devops/DEVOPS_06_Backup_Restore.puml` | DEVOPS-06 — Backup y Restore Test | Capítulos 13-16 y 22-24 — Git/CI-CD/despliegue/operación | Explicar objetivo operativo, qué corresponde al MVP y qué es evolución; incluir controles de seguridad/rollback/observabilidad pertinentes. |
| `diagramas/devops/DEVOPS_07_Redes_Docker.puml` | DEVOPS-07 — Segmentación lógica de redes Docker | Capítulos 13-16 y 22-24 — Git/CI-CD/despliegue/operación | Explicar objetivo operativo, qué corresponde al MVP y qué es evolución; incluir controles de seguridad/rollback/observabilidad pertinentes. |
| `diagramas/devops/DEVOPS_08_Multirepo.puml` | DEVOPS-08 — Estrategia multirepositorio SIGA | Capítulos 13-16 y 22-24 — Git/CI-CD/despliegue/operación | Explicar objetivo operativo, qué corresponde al MVP y qué es evolución; incluir controles de seguridad/rollback/observabilidad pertinentes. |
| `diagramas/estados/STATE_01_Movimiento.puml` | STATE-01 — Máquina de estados de Movimiento | Capítulo 4.6 — Estados y reglas de ciclo de vida | Describir cada estado, transiciones permitidas/prohibidas, evento disparador y efectos laterales; destacar inmutabilidad cuando aplique. |
| `diagramas/estados/STATE_02_Activo.puml` | STATE-02 — Estados de maquinaria / activo serializado | Capítulo 4.6 — Estados y reglas de ciclo de vida | Describir cada estado, transiciones permitidas/prohibidas, evento disparador y efectos laterales; destacar inmutabilidad cuando aplique. |
| `diagramas/estados/STATE_03_Evidencia.puml` | STATE-03 — Ciclo de vida de evidencia | Capítulo 4.6 — Estados y reglas de ciclo de vida | Describir cada estado, transiciones permitidas/prohibidas, evento disparador y efectos laterales; destacar inmutabilidad cuando aplique. |
| `diagramas/estados/STATE_04_Outbox.puml` | STATE-04 — Ciclo de Outbox Event | Capítulo 4.6 — Estados y reglas de ciclo de vida | Describir cada estado, transiciones permitidas/prohibidas, evento disparador y efectos laterales; destacar inmutabilidad cuando aplique. |
| `diagramas/secuencia/SEQ_01_Login_MFA.puml` | SEQ-01 — Login + MFA TOTP | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_02_Refresh_Token.puml` | SEQ-02 — Rotación de Refresh Token | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_03_Crear_Producto.puml` | SEQ-03 — Crear producto y proyectar referencia en Inventory | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_04_Registrar_Entrada.puml` | SEQ-04 — Registrar y confirmar entrada multi-detalle | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_05_Salida_Exitosa.puml` | SEQ-05 — Confirmar salida exitosa con lock pesimista | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_06_Salida_Stock_Insuficiente.puml` | SEQ-06 — Rechazo por stock insuficiente bajo concurrencia | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_07_Salida_Sensible_Autorizacion.puml` | SEQ-07 — Salida sensible + autorización + step-up MFA | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_08_Transferencia.puml` | SEQ-08 — Transferencia interna atómica | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_09_Ajuste.puml` | SEQ-09 — Ajuste de inventario controlado | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_10_Upload_Evidencia.puml` | SEQ-10 — Upload de evidencia (MVP multipart) | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_11_Transactional_Outbox.puml` | SEQ-11 — Transactional Outbox | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_12_Consumer_Idempotente.puml` | SEQ-12 — Consumidor RabbitMQ idempotente | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_13_Reporte_Persistente.puml` | SEQ-13 — Generación de reporte temporal o persistente | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_14_ETL_BI.puml` | SEQ-14 — Interoperabilidad ETL/BI de solo lectura | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/secuencia/SEQ_15_Frontend_Refresh.puml` | SEQ-15 — Renovación de access token en Web | Capítulos 14-15 del informe / sección de realización de CUS | Recorrer el flujo en orden, indicar validaciones, errores/alternativas y la frontera transaccional; relacionar endpoints, estados y RNF. |
| `diagramas/uml/UML_01_Modelo_Dominio.puml` | UML-01 — Modelo de dominio general SIGA | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/uml/UML_02_Clases_IAM.puml` | UML-02 — Clases MS-IAM | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/uml/UML_03_Clases_Catalog.puml` | UML-03 — Clases MS-CAT | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/uml/UML_04_Clases_Inventory.puml` | UML-04 — Clases MS-INV (detalle del núcleo transaccional) | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/uml/UML_05_Clases_Evidence.puml` | UML-05 — Clases MS-EVI | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/uml/UML_06_Clases_Audit_Reporting.puml` | UML-06 — Clases Audit/Notification y Reporting/Analytics | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/uml/UML_07_Paquetes_Backend.puml` | UML-07 — Dependencias de paquetes backend (Clean/Hexagonal) | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/uml/UML_08_Paquetes_Web.puml` | UML-08 — Paquetes Web React (Clean Architecture + feature-first) | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |
| `diagramas/uml/UML_09_Paquetes_Mobile.puml` | UML-09 — Paquetes Mobile Expo | Capítulo 4 (y 8/9 para paquetes de clientes) — Diseño UML | La relación entre actores/componentes y la decisión técnica representada; señalar precondiciones, responsabilidad y efecto crítico, no limitarse a describir las flechas. |

## Diagramas prioritarios para la sustentación

Si el tiempo de exposición es limitado, priorizar: **C4-01**, **C4-02**, **C4-04**, **UML-01**, **UML-04**, **STATE-01**, **SEQ-05**, **SEQ-06**, **SEQ-11**, **DER-02/03/06/09**, **DEVOPS-02/03/05/06**. Estos muestran la visión global, el núcleo ACID, concurrencia, Outbox, datos, entrega y continuidad.

## Nota sobre BPMN

Los archivos `BPMN_*` están expresados como **activity diagrams con swimlanes en PlantUML** para mantener fuentes autocontenidas. En el informe pueden renderizarse directamente o recrearse con notación BPMN 2.0 estricta en una herramienta especializada manteniendo exactamente el mismo flujo, gateways, responsables y reglas. No debe modificarse el comportamiento al redibujarlos.

## Plantilla de pie de figura

**Figura [n]. [Nombre del diagrama].** El diagrama muestra [...]. La decisión principal es [...]. En particular, [...]. Fuente: elaboración propia a partir del Manual Técnico SIGA.

## Regla de coherencia de datos

Los DER-04..09 son la especificación física legible por bounded context y deben corresponder exactamente a `database/physical_model.sql` y `database/dictionary.md`. DER-02 puede resumir columnas por legibilidad, pero no puede omitir entidades persistentes del modelo canónico.


## Adenda v1.2 — Diagramas de Proveedores

| Archivo | Uso | Cambio mínimo |
|---|---|---|
| `diagramas/uml/UML_10_Casos_Uso_Negocio_Proveedores.puml` | Capítulo 8 | Agrega Proveedor externo a CUN-01 sin alterar los demás CUN. |
| `diagramas/uml/UML_11_Casos_Uso_Sistema_Proveedores.puml` | Capítulo 9 | Agrega CUS-31 Gestionar proveedores y su relación con CUS-07. |
| `diagramas/bpmn/BPMN_01_Entrada.puml` | CUN-01 | Selección/validación de proveedor solo en recepción externa. |
| `diagramas/secuencia/SEQ_04_Registrar_Entrada.puml` | CUS-07 | Valida `supplier_ref` local y guarda snapshot; sin REST a Catalog durante commit. |
| `diagramas/datos/DER_01_Conceptual.puml` / `DER_02_Logico.puml` / `DER_03_Fisico.puml` | Datos globales | Inserta proveedor y referencia local; total físico 40 tablas. |
| `diagramas/datos/DER_05_Fisico_Catalog.puml` | Catalog | Agrega `catalog.supplier`. |
| `diagramas/datos/DER_06_Fisico_Inventory.puml` | Inventory | Agrega `supplier_ref` y vínculo opcional/snapshot en `movement`. |
| `diagramas/datos/DER_09_Fisico_Reporting_Analytics.puml` | Analytics | Expone proveedor en `movement_projection` para filtros/reportes. |
| `diagramas/uml/UML_01_Modelo_Dominio.puml`, `UML_03_Clases_Catalog.puml`, `UML_04_Clases_Inventory.puml`, `UML_06_Clases_Audit_Reporting.puml` | Dominio/clases | Refleja Supplier/SupplierReference y snapshot analítico sin crear nuevo microservicio. |
| `diagramas/c4/C4_04_Componente_Inventory.puml` | Componentes MS-INV | Amplía el consumidor/proyección de Catalog para Supplier events; no cambia el contexto ni los contenedores. |

No requieren cambio C4-01/C4-02/C4-03/C4-05, diagramas de salida/transferencia/ajuste/evidencia, estados, IAM ni DevOps porque el proveedor no opera SIGA directamente y la arquitectura sigue en seis servicios.

## Gobierno de fuentes para renderizado

A partir de v1.2 se distinguen dos árboles:

| Árbol | Estado | Uso |
|---|---|---|
| `diagramas/` | **Canónico** | arquitectura, implementación, agentes de IA, trazabilidad, revisión |
| `diagramas_render/` | **Derivado** | PNG/SVG, Word, informe, sustentación |

Los derivados reutilizan la estética/fixes de v1.1 sin alterar la semántica vigente de v1.2. No deben editarse manualmente. Para regenerar y validar:

```bash
python tools/generar_derivados_visuales.py
python tools/validar_fuentes_y_derivados.py
```

Ver ADR-019 y `AGENTS.md`.
