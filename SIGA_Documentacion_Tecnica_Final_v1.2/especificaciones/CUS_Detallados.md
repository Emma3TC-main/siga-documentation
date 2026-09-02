# Especificaciones Detalladas de Casos de Uso del Sistema — SIGA

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
| RF | RF-07,RF-09,RF-27,RF-28,RF-31 |
| HU | US-07 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `POST /api/v1/movements; POST /movements/{id}/confirm` |
| Permiso baseline | `MOVEMENT_CREATE` |
| Eventos/asíncronos | MovementConfirmed; StockBelowMinimum no usual; outbox |
| Precondiciones | Producto/ubicación activos; costo/trazabilidad según flags |
| Postcondiciones | Stock incrementado, costo promedio actualizado, movimiento CONFIRMADO |
| Excepciones relevantes | UoM/lote/serie/TC inválido; rollback total |
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

**Regla adicional v1.2:** para una recepción de abastecimiento externo, `supplierId` se valida contra `inventory.supplier_ref` dentro de MS-INV; no se consulta Catalog por REST durante el commit. Al confirmar se copian razón social y RUC/identificador como snapshot del movimiento.

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
| Endpoint(s) | `GET/POST/PATCH /api/v1/units; conversiones incluidas/versionadas con Product` |
| Permiso baseline | `PRODUCT_WRITE` |
| Eventos/asíncronos | ProductUpdated |
| Precondiciones | Magnitud/unidad válidas |
| Postcondiciones | Una o más conversiones `from/to/factor>0` persistidas por producto y proyectables a Inventory |
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
| Postcondiciones | Lote/activo consistente con producto; la ubicación actual del activo se deriva exclusivamente de stock_balance |
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
| Precondiciones | `ownerType` MOVEMENT/ASSET/ADJUSTMENT/REPORT y `ownerId` autorizados |
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

## CUS-31 — Gestionar proveedores

| Campo | Especificación |
|---|---|
| Actor principal | Administrador / usuario de catálogo autorizado |
| RF | RF-35 |
| HU | US-35 |
| Servicio responsable | MS-CAT |
| Endpoint(s) | `GET/POST/PUT /api/v1/suppliers; GET /api/v1/suppliers/{id}` |
| Permiso baseline | `SUPPLIER_MANAGE` |
| Eventos/asíncronos | `SupplierCreated`, `SupplierUpdated`, `SupplierDisabled` vía Catalog Outbox |
| Precondiciones | Código e identificador tributario no duplicados |
| Postcondiciones | Maestro actualizado; Inventory recibe/actualiza `supplier_ref`; historial previo no se elimina |
| Excepciones relevantes | RUC/taxId duplicado, formato inválido, proveedor inactivo seleccionado en nueva recepción |
| Diagrama(s) | UML-03, UML-10, DER-05 |

**Flujo base técnico-funcional:**

1. El usuario autorizado crea, consulta, actualiza o desactiva un proveedor desde el módulo de catálogo.
2. MS-CAT valida unicidad de código e identificador tributario y persiste el cambio en `catalog.supplier`.
3. En la misma transacción local registra el evento correspondiente en `catalog.outbox_event`.
4. Inventory consume el evento de forma idempotente y actualiza `inventory.supplier_ref`.
5. Un proveedor desactivado conserva su historial, pero no debe seleccionarse para una nueva recepción externa.

**Criterios de prueba mínimos:**

- Alta y actualización válidas.
- Rechazo de código/taxId duplicado.
- Desactivación lógica sin romper movimientos históricos.
- Proyección idempotente hacia `inventory.supplier_ref`.
- Entrada externa rechazada si el proveedor está inactivo o no existe en la proyección local.


# Anexo — Reglas reforzadas de CUS críticos

## CUS-07/CUS-08/CUS-09/CUS-10 — frontera ACID

Para entrada, salida, transferencia y ajuste, **stock, costo aplicado, movimiento, detalles e inserción del evento Outbox deben formar parte del mismo commit local de `inventory-service`**. Las salidas/transferencias/ajustes que consumen existencia bloquean las filas concretas mediante `SELECT ... FOR UPDATE`; después del lock se revalida cantidad, lote, serie/activo y ubicación. El aislamiento base es `READ COMMITTED`; no se eleva todo PostgreSQL a `SERIALIZABLE`. Toda excepción antes de `COMMIT` produce rollback.

## CUS-27 — autorización no reserva stock

`AUTORIZADO` expresa aprobación humana/técnica, no reserva inventario. Entre autorización y confirmación puede cambiar el stock; por eso la confirmación revalida y puede devolver 409. Esto evita que el sistema prometa una existencia que ya no está disponible.

## CUS-26 — integridad y owner de archivo

El binario se almacena en MinIO/GCS; PostgreSQL conserva `owner_type`, `owner_id`, `object_key`, nombre original, MIME, tamaño, SHA-256, proveedor, usuario, fecha, estado y metadata JSONB opcional. `owner_id` es referencia UUID externa sin FK cross-schema. La aplicación debe evitar objetos huérfanos y referencias sin objeto; metadata + `evidence.outbox_event` se confirman localmente y los accesos son privados/autorizados.

## CUS-19 — interoperabilidad

El consumidor BI/ETL solo recibe lectura. No existe ruta para actualizar inventario desde BI. Las cargas incrementales utilizan claves estables y watermark/fecha de actualización; las fallas analíticas no interrumpen las transacciones del almacén.


## CUS-05/CUS-23 — conversiones canónicas

`catalog.product` conserva unidad de almacenamiento y unidad base, mientras `catalog.unit_conversion` permite N conversiones por producto. No existe un único `conversion_factor` autoritativo en Product. `ProductCreated/Updated` transporta a Inventory el conjunto necesario para actualizar `product_ref` y `product_unit_conversion_ref`; `inventory.processed_event` impide repetir el efecto ante redelivery.

## CUS-25 — ubicación y serialización

`inventory.asset` identifica la unidad serializada, pero no guarda `current_location_id`. La ubicación actual se obtiene de `stock_balance`. Un `asset_id` solo puede tener una existencia positiva y, cuando se usa en stock, su cantidad efectiva es 0/1. Las asociaciones de lote/activo se verifican contra el mismo `product_id`.

## CUS-28 — conteo no muta stock

`physical_count_line` conserva cantidad del sistema, cantidad contada y diferencia. Completar un conteo no modifica por sí mismo `stock_balance`; una regularización se registra posteriormente como `ADJUST_POSITIVE` o `ADJUST_NEGATIVE`, preservando autorización, motivo y evidencia.
