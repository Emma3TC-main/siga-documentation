# Guía de Imágenes y Evidencias para el Informe — SIGA

Esta guía define **qué imagen insertar, dónde colocarla y qué explicar debajo**. Los diagramas de arquitectura/UML/BPMN/DER se renderizan desde `diagramas/**/*.puml`; las capturas de UI, testing, Jira y despliegue se agregan durante la implementación.

## 1. Convención

- `FIG-ARCH-*`: C4/arquitectura.
- `FIG-UML-*`: dominio, clases y paquetes.
- `FIG-SEQ-*`: secuencias.
- `FIG-STATE-*`: estados.
- `FIG-BPMN-*`: procesos de negocio.
- `FIG-DATA-*`: DER/modelo de datos.
- `FIG-DEVOPS-*`: GitFlow, CI/CD, despliegue, redes, observabilidad, backup.
- `FIG-UI-*`: Figma/mockup/captura real.
- `FIG-TEST-*`: resultados de prueba.
- `FIG-JIRA-*`: gestión Scrum/Jira/GitHub.

Usar pie: **Figura N. [Nombre]. Fuente: elaboración propia.** Después agregar uno o dos párrafos: propósito, lectura principal y decisión/regla que demuestra.

## 2. Arquitectura y análisis

| Evidencia | Fuente | Ubicación del informe | Descripción mínima |
|---|---|---|---|
| FIG-ARCH-01 | `diagramas/c4/C4_01_Contexto.puml` | 15.1 / C4 contexto | actores, SIGA y sistemas externos |
| FIG-ARCH-02 | `C4_02_Contenedores_Docker_GCP.puml` | arquitectura/contenedores | baseline implementable Compose+GCP |
| FIG-ARCH-03 | `C4_03_Contenedores_Kubernetes.puml` | escalabilidad futura | objetivo GKE, no requisito MVP |
| FIG-ARCH-04 | `C4_04_Componente_Inventory.puml` | realización/estructura | frontera ACID Inventory+Movement |
| FIG-UML-01 | `diagramas/uml/UML_01_Modelo_Dominio.puml` | modelo de dominio | conceptos y relaciones principales |
| FIG-STATE-01 | `diagramas/estados/STATE_01_Movimiento.puml` | diagramas de estados | autorización vs confirmación/inmutabilidad |
| FIG-SEQ-05/06 | secuencias salida | realización CUS-08 | éxito y concurrencia/stock insuficiente |
| FIG-SEQ-11/12 | Outbox/consumer | integración/eventos | confiabilidad e idempotencia |

El catálogo completo está en `Guia_Diagramas_SIGA.md`.

## 3. Base de datos

Insertar `DER_01_Conceptual`, `DER_02_Logico`, `DER_03_Fisico` en los capítulos 17-18. Acompañar el físico con una referencia a `database/dictionary.md` y `database/physical_model.sql`. No intentar colocar el diccionario completo como imagen; debe permanecer como tabla/texto.

## 4. UI / Figma / implementación

Capturas prioritarias:

| ID | Pantalla | Momento recomendado |
|---|---|---|
| FIG-UI-01 | Login | mockup + implementación |
| FIG-UI-02 | MFA | mockup + implementación |
| FIG-UI-03 | Dashboard | implementación Sprint 3/4 |
| FIG-UI-04 | Inventario | mockup + implementación |
| FIG-UI-05 | Producto | mockup + implementación |
| FIG-UI-06 | Entrada multi-detalle | prototipo + implementación |
| FIG-UI-07 | Salida | prototipo + implementación |
| FIG-UI-08 | Autorización sensible | prototipo + implementación |
| FIG-UI-09 | Transferencia | prototipo/implementación |
| FIG-UI-10 | Ajuste/Conteo | prototipo/implementación |
| FIG-UI-11 | Evidencia | Web/Mobile |
| FIG-UI-12 | Reportes | implementación |
| FIG-UI-13 | Auditoría | implementación |
| FIG-UI-14 | Inventario móvil | Expo |
| FIG-UI-15 | Movimiento + evidencia móvil | Expo |

Para cada una indicar `UI-ID`, actor, CUS/HU y regla clave. Seguir `Guia_Figma_UI_UX_SIGA.md`.

## 5. Testing

| ID sugerido | Evidencia | Qué debe demostrar |
|---|---|---|
| FIG-TEST-01 | JaCoCo | coverage global y núcleo crítico |
| FIG-TEST-02 | Test concurrencia | dos salidas compiten; stock nunca negativo |
| FIG-TEST-03 | Rollback | fallo intermedio no deja efecto parcial |
| FIG-TEST-04 | GitHub Actions | pipeline CI verde |
| FIG-TEST-05 | SonarCloud | quality gate / issues relevantes |
| FIG-TEST-06 | k6 | P95/error rate bajo carga baseline |
| FIG-TEST-07 | Playwright/Maestro | E2E crítico |
| FIG-TEST-08 | Trivy/Gitleaks/CodeQL | seguridad CI selectiva |
| FIG-TEST-09 | ZAP QA | baseline DAST no destructivo |
| FIG-TEST-10 | Restore Test | RPO/RTO y restauración válida |

No insertar decenas de capturas repetitivas: elegir evidencias representativas y dejar reportes completos como anexos/artifacts.

## 6. Jira y GitHub

- `FIG-JIRA-01`: Backlog/épicas/HU.
- `FIG-JIRA-02`: Sprint board.
- `FIG-JIRA-03`: Roadmap/progreso.
- `FIG-JIRA-04`: issue `SIGA-xxx` vinculada a branch/PR.
- `FIG-JIRA-05`: PR con checks de CI/review.

Anonimizar tokens, correos personales o secretos en capturas.

## 7. DevOps

Priorizar `DEVOPS_01_GitFlow`, `DEVOPS_02_CICD`, `DEVOPS_03_Deployment_Docker`, `DEVOPS_05_Observabilidad`, `DEVOPS_06_Backup_Restore` y `DEVOPS_08_Multirepo`. El diagrama Kubernetes se coloca en **escalabilidad futura**, dejando explícito que Docker Compose es la baseline evaluable del proyecto.
