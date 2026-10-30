# Physical Counts MVP

## Alcance y autoridad

Inventory es dueño del conteo físico y de sus líneas. Un conteo cubre exactamente una ubicación y toma, al crearse, un snapshot de todas las dimensiones de saldo existentes en esa ubicación. Una dimensión es la combinación `productId`/`lotId`/`assetId`; lote y activo conservan sus referencias canónicas cuando correspondan.

El conteo registra la diferencia entre la existencia esperada en ese snapshot y la cantidad observada. Nunca modifica `stock_balance`. Una regularización posterior es una acción explícita del usuario y usa los movimientos existentes `ADJUST_POSITIVE` o `ADJUST_NEGATIVE`.

## Permiso y actores

Todas las operaciones del recurso exigen `INVENTORY_COUNT`, UUID canónico `10000000-0000-0000-0000-000000000015`. El permiso se asigna a `ADMIN`, `ENCARGADO` y `SUPERVISOR`; no se crea un permiso separado para cerrar o cancelar.

Los actores se obtienen exclusivamente del `sub` UUID del JWT validado. El cliente no envía creador, contador, completador ni cancelador. Un usuario con el permiso puede continuar un conteo iniciado por otro usuario; cada transición conserva su actor real.

## Ciclo de vida

- `DRAFT`: el conteo y su snapshot fueron creados, pero todavía no se registró ninguna observación.
- `IN_PROGRESS`: se registró al menos una cantidad contada.
- `COMPLETED`: todas las líneas tienen cantidad contada y el usuario cerró el conteo. Es terminal.
- `CANCELLED`: un conteo `DRAFT` o `IN_PROGRESS` fue cancelado con motivo. Es terminal.

`POST /api/v1/counts` crea `DRAFT`. La primera captura de línea cambia implícitamente a `IN_PROGRESS`. `POST /api/v1/counts/{id}/close` cambia `IN_PROGRESS` a `COMPLETED`; no se permite cerrar con líneas pendientes. Un snapshot sin líneas puede cerrar directamente `DRAFT -> COMPLETED` para registrar que la ubicación fue verificada vacía. `POST /api/v1/counts/{id}/cancel` cambia `DRAFT` o `IN_PROGRESS` a `CANCELLED`.

## Snapshot, líneas y concurrencia

La creación ejecuta una transacción corta: valida la ubicación, lee el snapshot de `stock_balance` y crea las líneas. No mantiene locks durante el trabajo físico. Un producto inesperado que no formó parte del snapshot puede agregarse mientras el conteo está abierto; su `systemQuantity` es cero.

Cada línea persiste producto, lote/activo opcionales, cantidad de sistema, cantidad contada nullable, notas opcionales, actor y fecha de captura. `differenceQuantity` es derivada por PostgreSQL como `countedQuantity - systemQuantity` y permanece null mientras la línea no fue contada. Para un activo serializado, las cantidades admitidas son cero o uno.

El encabezado usa `version` optimista. Toda captura, alta de dimensión inesperada, cierre o cancelación exige `expectedVersion`; primero se comprueba la versión y luego el estado. Una versión obsoleta responde `409 VERSION_CONFLICT`. La cantidad de sistema nunca se recalcula. Movimientos posteriores no invalidan ni reescriben el snapshot histórico y el cierre no relee el stock vigente.

## Regularización

El cierre no crea movimientos. Después de revisar un conteo completado, el usuario puede registrar explícitamente ajustes mediante el API normal de movimientos:

- diferencia positiva: `ADJUST_POSITIVE` por el valor absoluto de la diferencia;
- diferencia negativa: `ADJUST_NEGATIVE` por el valor absoluto de la diferencia;
- diferencia cero: no requiere ajuste.

Las líneas conservan producto, ubicación, lote y activo. La referencia del movimiento identifica el conteo (`referenceDocType = PHYSICAL_COUNT`, `referenceDocNumber = countId`). Si se agrupan líneas, como máximo se prepara un movimiento por signo; el usuario revisa y registra cada movimiento, y el conteo no los confirma automáticamente.

El ajuste conserva sus reglas existentes: `INVENTORY_ADJUST`, sensibilidad, maker-checker, `MOVEMENT_AUTHORIZE`, step-up cuando corresponda y Evidence con `ownerType=MOVEMENT`. El conteo no requiere Evidence y no introduce el owner type `PHYSICAL_COUNT`.

## API MVP

- `POST /api/v1/counts`
- `GET /api/v1/counts?page=0&size=20`
- `GET /api/v1/counts/{id}`
- `PUT /api/v1/counts/{id}/lines/{lineId}`
- `POST /api/v1/counts/{id}/lines` para una dimensión inesperada
- `POST /api/v1/counts/{id}/close`
- `POST /api/v1/counts/{id}/cancel`

Los comandos POST requieren `Idempotency-Key`. La lista usa `page >= 0`, `size` entre 1 y 100, default 20, y orden fijo `createdAt DESC, id DESC`. No hay orden arbitrario ni filtros adicionales en el MVP.

Errores: `400` request/cantidad inválida o cierre incompleto; `401` autenticación; `403` falta de `INVENTORY_COUNT`; `404` conteo/línea/ubicación/referencia inexistente; `409` versión o transición incompatible.

## Eventos y auditoría

El MVP no introduce `PhysicalCountCreated`, `PhysicalCountCompleted` ni `InventoryAdjusted`: no existe consumidor aprobado y `InventoryAdjusted` permanece fuera de alcance. La cabecera y las líneas conservan actores y timestamps como rastro operacional del conteo. Si existe regularización, la confirmación del ajuste emite el `MovementConfirmed v1` existente y alimenta Audit/Reporting sin un evento adicional.

## Web y Mobile

REMOTE usa `ApiPhysicalCountRepository` y el `ApiClient` compartido; DEMO puede conservar `DemoPhysicalCountRepository`. No existe fallback REMOTE a DEMO. La UI lista y abre conteos, crea el snapshot por ubicación, captura líneas, muestra diferencias, cierra/cancela y permite iniciar manualmente el flujo de ajuste existente.

Mobile queda fuera del alcance de este slice. No existe contrato mobile-first aprobado para captura de conteos.
