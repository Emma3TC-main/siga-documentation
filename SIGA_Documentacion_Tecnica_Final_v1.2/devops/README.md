# Guía DevOps — SIGA

Estas plantillas acompañan el Manual Técnico y sirven como **baseline reproducible**, no como secretos ni como configuración productiva lista para copiar sin revisión.

## 1. Estrategia por niveles

**Nivel 1 — implementación del proyecto:** Docker Compose, Nginx, microservicios, RabbitMQ/Redis/observabilidad y servicios GCP cuando corresponda. Es la ruta que el equipo debe priorizar para la entrega.

**Nivel 2 — evolución:** GKE/Kubernetes. Se documenta para demostrar portabilidad, escalado, rolling updates y probes; no se convierte en requisito del MVP.

## 2. Multirepositorio

Cada microservicio/Web/Mobile tiene repo y pipeline propio. `siga-infrastructure` concentra Compose, Nginx, observabilidad, scripts y referencias Kubernetes. `siga-documentation` concentra contratos, ADR, matrices y diagramas. Las versiones de OpenAPI/eventos deben coordinarse cuando un consumidor se encuentra en otro repositorio.

## 3. Orden recomendado local

1. Crear `.env` desde `env.example` sin subirlo a Git.
2. Levantar dependencias y servicios mediante Compose.
3. Esperar health/readiness.
4. Ejecutar migraciones Flyway de cada servicio propietario de schema.
5. Cargar datos demo únicamente en DEV/QA.
6. Ejecutar smoke/API tests.
7. Habilitar observabilidad extendida si se necesita (`dev-observability`).

## 4. Seguridad

- Puertos de PostgreSQL, Redis, RabbitMQ management, MinIO console y Actuator sensible no se exponen a Internet.
- CI usa secretos/OIDC; GCP usa Secret Manager.
- No se almacena la JWT private key fuera de Identity.
- `.env`, certificados, claves y service account keys están fuera de Git.

## 5. Migraciones

Flyway vive **en cada repo backend** y solo modifica el schema propiedad de ese servicio. Se evita un repositorio central de migraciones que permita cambios cross-schema.

## 6. Rollback

Las imágenes se etiquetan con versión/SHA inmutable. El rollback de aplicación vuelve al tag anterior. Los cambios de BD deben diseñarse expand/contract para evitar que un rollback del binario quede bloqueado por una migración destructiva.
