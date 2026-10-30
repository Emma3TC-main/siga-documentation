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
| Endpoint(s) | `GET /api/v1/users`; `GET/PATCH /api/v1/users/{id}`; `POST /api/v1/users`; `PUT /api/v1/users/{id}/roles` |
| Permiso baseline | `USER_MANAGE` |
| Eventos/asíncronos | Outbox IAM v2: UserCreated/UserUpdated/UserDisabled/UserRolesChanged; compatibilidad v1; consumidor central Audit pendiente |
| Precondiciones | Lectura con `USER_MANAGE`; mutación con MFA y `auth_time` de máximo 300 segundos; `ROLE_MANAGE` para reemplazar/asignar roles |
| Postcondiciones | Usuario creado/actualizado/desactivado sin perder trazabilidad |
| Excepciones relevantes | Duplicado, validación, intento de autodesactivación no permitida por política |
| Diagrama(s) | UML-02 |

**Contrato administrativo MVP:** la lista usa `page=0`, `size=20` (`page >= 0`, `size 1..100`) y orden fijo `username ASC`; no admite búsqueda, filtros por email/estado/rol ni orden arbitrario. El modelo expuesto es `{id, username, email, active, mfaEnabled, roleIds}`. POST exige además una contraseña inicial transitoria de mínimo 12 caracteres; PATCH expone en Web únicamente `email` y `active`, mantiene `username` inmutable y no incluye administración MFA, reset de contraseña, desbloqueo ni borrado. `PUT /users/{id}/roles` reemplaza el conjunto completo, sin versión optimista y con semántica last-write-wins aceptada para el MVP.

Toda mutación exige reautenticación MFA normal cuando `auth_time` supera 300 segundos; refresh no renueva ese instante y no existe token ni endpoint step-up separado. Ausencia o expiración del step-up conserva `403 AUTH_FORBIDDEN`; el cliente puede hacer preflight de permiso y `auth_time`, pero ante un 403 no debe atribuir con certeza la causa. Esta ambigüedad se registra como `STEP_UP_ERROR_AMBIGUITY_DEBT`.

Identity confirma el cambio y `iam.outbox_event` en una transacción y publica de forma durable. El contrato v2 usa aggregate User, `actorUserId` derivado de JWT `sub` y snapshots seguros before/after; `roleIds` representa el conjunto completo. Audit mapeará a `USER_CREATED`, `USER_UPDATED`, `USER_DISABLED` o `USER_ROLES_CHANGED`. Los eventos v1 existentes siguen aceptados. La proyección en `audit.audit_event` no está implementada y queda como `IAM_EVENTS_CENTRAL_AUDIT_CONSUMER`; no se afirma auditoría central vigente ni se crean Notifications.

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
| Eventos/asíncronos | Outbox IAM v2: RoleCreated/RolePermissionsChanged; RoleChanged v1 legacy; consumidor central Audit pendiente |
| Precondiciones | Lecturas con `ROLE_MANAGE`; mutaciones con MFA y `auth_time` de máximo 300 segundos; catálogo de permisos read-only |
| Postcondiciones | RBAC actualizado; sesiones nuevas reflejan permisos |
| Excepciones relevantes | Rol protegido, permiso inexistente, conflicto de asignación |
| Diagrama(s) | UML-02 |

**Contrato RBAC MVP:** los roles son dinámicos: se listan y crean, pero no existe detalle individual, edición genérica, rename, activación/desactivación ni borrado. El catálogo `GET /permissions` es read-only, devuelve `{id, code, description}` en `code ASC` y no ofrece detalle ni mutaciones. `PUT /roles/{id}/permissions` reemplaza el conjunto completo; `ADMIN` permanece protegido por backend. No existe `PATCH /roles`.

El contrato asíncrono v2 distingue `RoleCreated` y `RolePermissionsChanged`, aggregate Role, actor autenticado y snapshots seguros; `permissionIds` es reemplazo completo. Audit mapeará a `ROLE_CREATED` y `ROLE_PERMISSIONS_CHANGED`. No existe `RoleUpdated`. El ambiguo `RoleChanged v1` se acepta únicamente como `IDENTITY_ROLE_CHANGED_LEGACY`, sin consultar IAM para inferir el subtipo.

Los reemplazos de roles y permisos no exponen ETag, `expectedVersion` ni otro token optimista. Se acepta explícitamente `LAST_WRITE_WINS_ACCEPTED_FOR_MVP`: la UI carga el estado vigente al abrir, presenta y confirma el conjunto completo, y recarga la representación autoritativa tras guardar. Dos administradores concurrentes aún pueden sobrescribirse; el control optimista queda como evolución separada.

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

**Consulta de productos aprobada:** `GET /api/v1/products` exige `PRODUCT_WRITE` y responde `200` con `{content, page, size, totalElements}`. `page` es base cero (defecto `0`); `size` tiene defecto `20` y rango `1..100`. `sort` tiene defecto `sku,asc` y admite `sku,asc`, `sku,desc`, `name,asc` y `name,desc`; `id ASC` es desempate estable. Los filtros opcionales `q`, `active`, `categoryId` y `productType` se combinan con AND. `q` busca subcadena sin distinción de mayúsculas en `sku` o `name` y trata `%`/`_` literalmente; al omitir `active` se incluyen registros activos e inactivos. Sin coincidencias devuelve `200` con `content: []` y los metadatos efectivos. `GET /api/v1/products/{id}` devuelve el mismo `ProductResponse` para un producto activo o inactivo; un UUID inexistente devuelve `404 PRODUCT_NOT_FOUND` Problem Details.

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

**Permiso de consulta vigente:** `GET /api/v1/products` y `GET /api/v1/products/{id}` exigen `CATALOG_READ` o, por compatibilidad administrativa, `PRODUCT_WRITE`. Esta regla sustituye la referencia anterior a `PRODUCT_WRITE` exclusivo; las mutaciones conservan `PRODUCT_WRITE`.

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

**D4 costo/evento:** ENTRY exige costo unitario y pondera el saldo destino. La confirmación inserta exclusivamente `MovementConfirmed v1` PENDING dentro del commit local; no emite eventos especializados en paralelo.

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

**Regla de sensibilidad MVP:** una salida es sensible únicamente si al menos un detalle contiene un activo serializado (`assetId`). El servicio lo calcula al enviar el borrador; el cliente no puede declararlo.

**Regla de aprobación por capacidad:** al enviar, `requiresAuthorization = movementIsSensitive OR !actor.hasPermission(MOVEMENT_AUTHORIZE)`. Un actor sin ese permiso queda en `PENDING_AUTHORIZATION` incluso si el movimiento no es sensible. Solo un actor con `MOVEMENT_AUTHORIZE` puede confirmar directamente desde `DRAFT`, y únicamente un movimiento no sensible.

**D4 costo/evento:** EXIT usa el promedio bloqueado del origen, lo conserva como snapshot y no modifica el promedio remanente. La confirmación inserta exclusivamente `MovementConfirmed v1` PENDING dentro del commit local.

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

**Regla de sensibilidad MVP:** una transferencia es sensible únicamente si al menos un detalle contiene un activo serializado (`assetId`). El servicio lo calcula al enviar el borrador; el cliente no puede declararlo.

**Regla de aprobación por capacidad:** aplica la misma fórmula `sensitive OR !MOVEMENT_AUTHORIZE`; la ausencia del permiso lleva a `PENDING_AUTHORIZATION` y bloquea la confirmación directa desde `DRAFT`.

**D4 costo/evento:** TRANSFER transporta el promedio del origen y pondera un destino existente; la confirmación inserta exclusivamente `MovementConfirmed v1` PENDING dentro del commit local.

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

**Regla de sensibilidad MVP:** `ADJUST_POSITIVE` y `ADJUST_NEGATIVE` siempre son sensibles; requieren el flujo submit/autorización antes de confirmar.

**D4 costo/evento:** ajuste positivo valoriza como entrada si aporta costo, o reutiliza promedio solo con saldo positivo; ajuste negativo usa promedio bloqueado como salida. Ambos emiten exclusivamente `MovementConfirmed v1` PENDING al confirmar. `InventoryAdjusted` y `SensitiveMovementConfirmed` quedan fuera de alcance hasta contrato versionado.

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
| Actor principal | Actor autenticado con permiso efectivo; los nombres de rol no autorizan por sí solos |
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

Para Catalog, CUS-05 concreta los parámetros y límites de `GET /api/v1/products`; otros servicios definen sus filtros en su propio contrato OpenAPI.

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
| Endpoint(s) | Diferido después del MVP; sin endpoint activo en `reporting-openapi.yaml` |
| Permiso baseline | `REPORT_READ` |
| Eventos/asíncronos | ReportGenerated opcional |
| Precondiciones | Contrato posterior de formato, storage y ciclo de vida aprobado |
| Postcondiciones | Diferido: PDF/XLSX/CSV temporal o persistente/auditable |
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
| Endpoint(s) | Diferido después del MVP; sin endpoint activo en `reporting-openapi.yaml` |
| Permiso baseline | `ANALYTICS_READ` |
| Eventos/asíncronos | Ninguno |
| Precondiciones | Credencial de integración read-only aún no contratada; `ANALYTICS_READ` permanece separado |
| Postcondiciones | Diferido: export incremental con watermark |
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
| Endpoint(s) | `GET /api/v1/dashboard` |
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
| Postcondiciones | Conjunto completo de cero o más conversiones `from/to/factor>0` persistido y proyectable a Inventory |
| Excepciones relevantes | Factor <=0, unidad incompatible |
| Diagrama(s) | UML-03 |

**Regla de conversión con Product:** cuando la unidad de almacenamiento y la base difieren, existe una conversión activa directa almacenamiento → base y `cantidad_origen × factor = cantidad_destino`. `dimension` solo describe la UoM; no prohíbe conversiones entre dimensiones distintas. “Unidad incompatible” requiere una política futura explícita y no se infiere de `dimension`.

**Reemplazo y proyección aprobados:** el PUT de Product exige el arreglo `conversions` y lo interpreta como snapshot completo. Cada pareja origen/destino es única, sus unidades son distintas, `factor` es positivo con precisión máxima 18,6 y toda referencia nueva o modificada usa UoM activas. Un cambio efectivo incrementa la versión de Product y emite `ProductUpdated v1` con el snapshot completo expresado en códigos UoM; un no-op no reescribe conversiones ni emite evento. La política para desactivar una UoM usada queda fuera de este incremento y no se define aquí.

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

**Permiso de consulta vigente:** `GET /api/v1/units` exige `CATALOG_READ` o, por compatibilidad administrativa, `PRODUCT_WRITE`; las mutaciones conservan `PRODUCT_WRITE`.

## CUS-24 — Gestionar ubicaciones

| Campo | Especificación |
|---|---|
| Actor principal | Administrador/Supervisor |
| RF | RF-24 |
| HU | US-24 |
| Servicio responsable | MS-INV |
| Endpoint(s) | `GET /locations`, `GET /locations/{id}`, `POST /locations`, `PUT /locations/{id}`, `POST /locations/{id}/deactivate`, `POST /locations/{id}/reactivate`; sin PATCH/DELETE |
| Permiso baseline | Lecturas: `INVENTORY_READ` o `LOCATION_MANAGE`; mutaciones: `LOCATION_MANAGE` (`10000000-0000-0000-0000-000000000016`) |
| Eventos/asíncronos | `LocationChanged v1` en `inventory.location.changed.v1`; Audit idempotente, sin notificaciones |
| Precondiciones | Datos válidos, jerarquía acíclica, padre activo para creación/reparent/reactivación y `expectedVersion` vigente en PUT/lifecycle |
| Postcondiciones | Cambio efectivo + Outbox en un commit; versión incrementada una vez; no-op sin escrituras/evento |
| Excepciones relevantes | `VALIDATION_ERROR`, `AUTH_INVALID`, `AUTH_FORBIDDEN`, `LOCATION_NOT_FOUND`, `DATA_CONFLICT`, `VERSION_CONFLICT`, `LOCATION_HIERARCHY_CONFLICT`, `LOCATION_HAS_ACTIVE_DESCENDANTS`, `LOCATION_HAS_STOCK`, `LOCATION_IN_USE`, `LOCATION_INACTIVE` |
| Diagrama(s) | UML-04 |

**Flujo base técnico-funcional:**

1. GET lista sin paginación por `code ASC,id ASC`; `active` es texto `true|false|all`, defecto `true`. El detalle devuelve activos e inactivos.
2. POST recibe solo código, nombre, tipo y padre; crea activo en versión 0 y devuelve 201 con Location. Código es único global, case-sensitive e inmutable.
3. PUT reemplaza nombre, tipo y padre, nunca código/activo/actor. PUT, deactivate y reactivate exigen `expectedVersion>=0`, comprobado antes del no-op.
4. `parentId=null` es raíz; cualquier tipo puede ser raíz y no hay matriz rígida. Padre nuevo debe existir/estar activo; se impiden self-parent, ciclos profundos y ciclos por concurrencia. Un inactivo conserva un padre histórico inactivo si no lo cambia.
5. Desactivar no hace cascade: bloquean descendientes activos, `quantity>0` y conteos DRAFT/IN_PROGRESS en el subárbol; no bloquean cantidad cero, conteos terminales ni movimientos históricos. Reactivar conserva ID/código y exige padre activo.
6. Cambio efectivo incrementa una vez y confirma Location + Outbox. No-op conserva versión/timestamp y no emite. El publisher entrega al menos una vez, usa `eventId` estable y marca PUBLISHED después del confirm.
7. Audit consume idempotentemente y mapea cada `changeType` a la acción `LOCATION_*`, actor desde `actorUserId`, agregado Location y resultado SUCCESS; una mutación rechazada no produce Audit.

**Criterios de prueba mínimos:**

- Crear raíz/hijo; rechazar padre inactivo, self-parent, ciclo profundo y carrera de reparentado.
- Código duplicado, PUT exitoso/no-op, código inmutable y versión obsoleta.
- Desactivar hoja limpia; bloquear descendiente activo, stock positivo y conteo abierto; permitir historial terminal.
- Reactivar y rechazar padre inactivo; comprobar permisos de lectura/mutación.
- Outbox efectivo, ausencia de evento en no-op/rechazo y Audit idempotente.

## CUS-25 — Gestionar lotes, series y activos

| Campo | Especificación |
|---|---|
| Actor principal | Encargado/Supervisor |
| RF | RF-27,RF-28 |
| HU | US-27,US-28 |
| Servicio responsable | MS-INV |
| Endpoint(s) | Selectores `GET /api/v1/lots|assets`; listas admin `GET /api/v1/admin/lots|assets`; detalle/alta/reemplazo/estado en `/api/v1/lots|assets` |
| Permiso baseline | Selector `INVENTORY_READ`; lectura admin `INVENTORY_READ OR TRACEABILITY_MANAGE`; mutación `TRACEABILITY_MANAGE` |
| Eventos/asíncronos | `LotChanged v1`, `AssetChanged v1` hacia Audit; sin Notifications |
| Precondiciones | Producto requiere regla correspondiente |
| Postcondiciones | Lote/activo consistente con producto; la ubicación actual del activo se deriva exclusivamente de stock_balance |
| Excepciones relevantes | Serie duplicada, vencimiento requerido, lote inconsistente |
| Diagrama(s) | STATE-02; UML-04 |

**Selectores operacionales aprobados:** `GET /api/v1/lots` exige `productId`, admite `locationId`, `availableOnly=false`, `page=0` y `size=20` (`1..100`). Devuelve únicamente lotes `ACTIVE` sin vencimiento o con `expiresAt` mayor o igual a la fecha UTC vigente; agrega la cantidad desde `stock_balance`, la restringe por ubicación cuando se envía `locationId` y ordena por `lotNumber`, `heatNumber` e `id` con nulos al final. `GET /api/v1/assets` exige `productId` y `availability=UNASSIGNED|IN_STOCK`, admite `locationId`, `lotId` y la misma paginación; devuelve únicamente activos `OPERATIVO`, ordenados por `assetCode` e `id`. `UNASSIGNED` significa que no existe saldo positivo; `IN_STOCK`, que existe exactamente un saldo positivo con cantidad uno. Ambas consultas requieren `INVENTORY_READ` y no sustituyen las futuras operaciones administrativas protegidas por `TRACEABILITY_MANAGE`.

**Regla de uso en movimientos:** el requisito efectivo de lote es `requiresLot || requiresHeatNumber || requiresExpiry`; el requisito de activo es `requiresSerial`. En `ENTRY` y `ADJUST_POSITIVE`, los IDs seleccionados deben preexistir y corresponder al producto: este incremento no crea lotes ni activos. Un lote o activo previamente creado sin saldo positivo es válido y puede aparecer como no disponible/no asignado; su creación y el movimiento que lo usa son solicitudes independientes, por lo que no forman una única transacción distribuida.

**Administración de Lot:** producto, lote y colada son inmutables; fechas son reemplazables mediante `PUT` con `expectedVersion`. La acción `/status` admite `ACTIVE -> QUARANTINED|BLOCKED`, `QUARANTINED <-> BLOCKED`, retorno a `ACTIVE` si no está vencido y `DEPLETED -> ACTIVE` solo con agregado cero y fecha válida. `EXPIRED` deriva de la fecha UTC y `DEPLETED` del paso de stock agregado positivo a cero; no son targets manuales. El alta no crea stock y no existe DELETE.

**Administración de Asset:** producto, código y serie globalmente únicos son inmutables; marca, modelo y snapshot técnico son reemplazables con versión. Las transiciones manuales son `OPERATIVO -> EN_MANTENIMIENTO|INOPERATIVO`, `EN_MANTENIMIENTO -> OPERATIVO|FUERA_SERVICIO` e `INOPERATIVO -> EN_MANTENIMIENTO|FUERA_SERVICIO`. `EN_TRANSITO` no es control administrativo; `FUERA_SERVICIO` es terminal y exige saldo positivo cero. La ubicación se deriva de `stock_balance`; no se crea stock ni existe DELETE/custodia (`ASSET_CUSTODY_DEFERRED`).

**Concurrencia, errores y auditoría:** la versión se comprueba antes del no-op; solo el cambio efectivo incrementa una vez e inserta Outbox en la misma transacción. Aplican `LOT|ASSET_NOT_FOUND`, `DATA_CONFLICT`, `VERSION_CONFLICT`, `LOT|ASSET_STATUS_CONFLICT` y `LOT|ASSET_NOT_AVAILABLE`, además de Problem Details 400/401/403. Audit consume idempotentemente las acciones `LOT_*` y `ASSET_*`; no se generan Notifications.

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
| Precondiciones | `ownerType=MOVEMENT`; ownerId existente/visible en Inventory; JWT `sub` UUID; permiso Evidence; `Idempotency-Key` UUID para upload |
| Postcondiciones | Objeto privado + metadata/hash + ownerType/ownerId + EvidenceUploaded vía Outbox |
| Excepciones relevantes | Owner inválido/no visible, key conflictiva, MIME/magic/size/metadata inválido, Inventory o storage no disponible; compensación tras rollback |
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

**Contrato cerrado del MVP:** `EVIDENCE_READ` y `EVIDENCE_WRITE` se asignan a `ADMIN`, `ENCARGADO` y `SUPERVISOR`. Evidence valida JWT y toma el actor de `sub`; nunca acepta `uploadedByUserId` del cliente. Antes de almacenar, `OwnerAccessPolicyPort` consulta `GET /api/v1/movements/{ownerId}` con el bearer original. Falta del permiso Evidence produce `403`; owner inexistente o no visible, `404`; owner type distinto de `MOVEMENT`, `400`; timeout/5xx de Inventory, `503`. No existe SQL ni FK cross-schema. Ajustes usan el UUID del movimiento y no el owner type `ADJUSTMENT`; `ASSET`, `ADJUSTMENT` y `REPORT` quedan fuera de esta versión.

**Consulta y descarga:** listar exige juntos `ownerType` y `ownerId`, `page=0`, `size=20` (`1..100`) y orden fijo `uploadedAt DESC, id DESC`; no existe listado global. La descarga transmite el objeto privado desde `GET /api/v1/evidences/{id}/content`, con MIME persistido y nombre original sanitizado como attachment; no expone object key ni URL pública/permanente.

**Upload idempotente e integridad:** `Idempotency-Key` UUID es obligatorio. Misma key + mismo request completado devuelve el `201` original; request distinto o aún en proceso devuelve `409`. Un retry fallido reutiliza `evidenceId` y object key. `metadata` debe ser objeto JSON, máximo 16 KiB UTF-8 y profundidad 5, con hasta 50 propiedades por objeto, 50 elementos por arreglo, claves de 64 y strings de 1024 caracteres; no admite binario/base64 ni secretos. Si storage precede a un rollback DB, Evidence intenta eliminar exactamente el objeto recién creado; una compensación fallida se registra como incidente estructurado. El reconciliador periódico queda diferido.

**Política de movimientos:** evidencia opcional para `ENTRY`, `EXIT` y `TRANSFER`. Todo `ADJUST_POSITIVE` o `ADJUST_NEGATIVE` es sensible y requiere al menos una evidencia `AVAILABLE` asociada al movimiento antes de submit/autorización. Evidence permanece fuera de la transacción ACID de confirmación; no hay transacción distribuida.

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
| Precondiciones | Movimiento PENDIENTE_AUTORIZACION; bearer JWT válido con `MOVEMENT_AUTHORIZE`, `amr` que incluya `otp` y `auth_time` de máximo 300 segundos; `sub != registeredByUserId` |
| Postcondiciones | Estado AUTORIZADO o RECHAZADO sin efecto stock |
| Excepciones relevantes | MFA ausente/no reciente, permiso insuficiente, subject inválido, violación maker-checker, estado inválido |
| Diagrama(s) | SEQ-07; BPMN-05 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV + MS-IAM**. Inventory deriva el autorizador de `sub` UUID del JWT validado; no acepta actor ni step-up token en el body y rechaza authorize/reject si ese `sub` coincide con `registeredByUserId`.
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
| Endpoint(s) | `POST/GET /api/v1/counts`; `GET /api/v1/counts/{id}`; captura de líneas, cierre y cancelación bajo `/api/v1/counts/{id}` |
| Permiso baseline | `INVENTORY_COUNT` |
| Eventos/asíncronos | Ninguno propio; un ajuste posterior confirmado conserva `MovementConfirmed v1` |
| Precondiciones | Ubicación válida; snapshot por ubicación; actor derivado del JWT `sub` |
| Postcondiciones | Conteo cerrado conserva snapshot y diferencias; no modifica stock; ajuste posterior explícito y separado |
| Excepciones relevantes | Versión obsoleta/transición inválida/conteo incompleto/referencia inválida |
| Diagrama(s) | BPMN-04 |

**Flujo base técnico-funcional:**

1. El cliente verifica estado local de formulario/sesión, pero no asume autoridad de negocio.
2. El request entra por API Gateway, recibe/propaga `X-Correlation-ID` y llega a **MS-INV**.
3. El servicio valida autenticación, autorización, DTO y precondiciones de dominio; los errores se devuelven como `application/problem+json`.
4. Si el caso modifica estado, el servicio aplica su frontera transaccional/ownership; si es consulta, aplica paginación/filtros y permisos del recurso.
5. El resultado confirmado se persiste antes de cualquier efecto asíncrono; cuando hay evento, este se entrega de forma confiable mediante Outbox/idempotencia según corresponda.
6. El cliente presenta estado success/error y conserva el `correlationId` para soporte cuando exista un error inesperado.

**Contrato MVP cerrado:** el ciclo es `DRAFT -> IN_PROGRESS -> COMPLETED` o `DRAFT|IN_PROGRESS -> CANCELLED`; una ubicación cuyo snapshot no contiene líneas puede cerrar directamente `DRAFT -> COMPLETED`. La creación toma una copia corta y determinista de todas las dimensiones de saldo de una ubicación; las cantidades contadas se capturan después y la diferencia es `counted - system`. Cada mutación verifica `expectedVersion`. El cierre no relee ni modifica stock y no crea ajustes. La regularización se registra explícitamente con el flujo existente `ADJUST_POSITIVE`/`ADJUST_NEGATIVE`, incluyendo autorización, step-up y Evidence del movimiento cuando correspondan. Véase `Physical_Counts_MVP.md`.

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

**Contrato HTTP v1.2 aprobado:** los GET requieren `CATALOG_READ` o `SUPPLIER_MANAGE`; POST/PUT requieren `SUPPLIER_MANAGE`. POST crea activo y devuelve `201 SupplierResponse`; `active` omitido o `true` es válido y `false` produce `400 VALIDATION_ERROR`. El detalle devuelve activos e inactivos o `404 SUPPLIER_NOT_FOUND`. Autenticación/autorización usa `401 AUTH_INVALID` y `403 AUTH_FORBIDDEN`; duplicar `code` o `taxId` produce `409 DATA_CONFLICT`.

La lista usa `page=0`, `size=20` y rango `1..100`; admite `code,asc|code,desc|businessName,asc|businessName,desc`, defecto `code,asc`, siempre con `id ASC` como desempate. `q` busca una subcadena literal sin distinguir mayúsculas en `code`, `taxId`, `businessName` o `tradeName`; `%` y `_` son literales. Los filtros se combinan con AND y omitir `active` incluye ambos estados. Sin coincidencias retorna `200`, `content: []` y metadatos efectivos.

PUT reemplaza los campos editables y exige `active` y `expectedVersion`. Una versión distinta retorna `409 VERSION_CONFLICT` sin mutación ni evento. Un no-op comprueba versión y devuelve el recurso actual sin incrementar `version` ni insertar Outbox. Una mutación incrementa versión: `true→false` emite `SupplierDisabled`; `false→true` y otros cambios emiten `SupplierUpdated`. No existe DELETE ni consulta a Inventory para autorizar la edición.

Cada mutación efectiva confirma proveedor y Outbox en una transacción. `SupplierCreated`, `SupplierUpdated` y `SupplierDisabled` v1 usan el UUID Outbox como `eventId`, sobre común, `aggregateType=Supplier`, `schemaVersion=1`, `producer=catalog-service` y payload `{supplier:{id,code,taxId,businessName,active,version}}`. Sus routing keys en `siga.events` son `catalog.supplier.created.v1`, `catalog.supplier.updated.v1` y `catalog.supplier.disabled.v1`. La entrega es al menos una vez; el futuro consumidor Inventory deduplica por `eventId`.

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

El binario se almacena en MinIO/GCS; PostgreSQL conserva `owner_type=MOVEMENT`, `owner_id`, `object_key`, nombre original, MIME, tamaño, SHA-256, proveedor, usuario, fecha, estado y metadata JSONB acotada. `owner_id` es referencia UUID externa sin FK cross-schema. `evidence.upload_idempotency` reserva un `evidence_id` estable por request y evita duplicar objeto, metadata y evento. La aplicación valida primero el owner, compensa un objeto si falla el commit y confirma metadata + `evidence.outbox_event` localmente. Los accesos son privados y revalidan owner; el contenido se transmite sin exponer key ni URL.

## CUS-19 — interoperabilidad

El consumidor BI/ETL solo recibe lectura. No existe ruta para actualizar inventario desde BI. Las cargas incrementales utilizan claves estables y watermark/fecha de actualización; las fallas analíticas no interrumpen las transacciones del almacén.


## CUS-05/CUS-23 — conversiones canónicas

`catalog.product` conserva unidad de almacenamiento y unidad base, mientras `catalog.unit_conversion` permite N conversiones por producto. No existe un único `conversion_factor` autoritativo en Product. `ProductCreated/Updated` transporta a Inventory el conjunto necesario para actualizar `product_ref` y `product_unit_conversion_ref`; `inventory.processed_event` impide repetir el efecto ante redelivery.

## CUS-25 — ubicación y serialización

`inventory.asset` identifica la unidad serializada, pero no guarda `current_location_id`. La ubicación actual se obtiene de `stock_balance`. Un `asset_id` solo puede tener una existencia positiva y, cuando se usa en stock, su cantidad efectiva es 0/1. Las asociaciones de lote/activo se verifican contra el mismo `product_id`.

## CUS-28 — conteo no muta stock

`physical_count_line` conserva cantidad del sistema, cantidad contada y diferencia. Completar un conteo no modifica por sí mismo `stock_balance`; una regularización se registra posteriormente como `ADJUST_POSITIVE` o `ADJUST_NEGATIVE`, preservando autorización, motivo y evidencia.
