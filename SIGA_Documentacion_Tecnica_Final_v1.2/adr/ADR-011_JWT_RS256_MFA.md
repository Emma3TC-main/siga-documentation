# ADR-011 — JWT RS256 + MFA

**Estado:** Aceptado

## Contexto
SIGA requiere consistencia, trazabilidad y viabilidad para cuatro integrantes.

## Decisión
Firma asimétrica, access 30m, refresh 7d, TOTP/step-up. El access JWT RS256 contiene issuer, audience, expiración y `sub = iam.user_account.id` UUID; expone `permissions`, `amr` y, tras MFA, `auth_time` en epoch-seconds. Para autorizar movimiento sensible, Inventory usa el JWT ya validado por Resource Server: exige `MOVEMENT_AUTHORIZE`, `amr` con `otp` y `auth_time` con antigüedad máxima de 300 segundos.

Las mutaciones administrativas de Identity (`POST /users`, `PATCH /users/{id}`, `PUT /users/{id}/roles`, `POST /roles` y `PUT /roles/{id}/permissions`) también requieren `auth_time` con antigüedad máxima de 300 segundos. Las lecturas administrativas no requieren step-up. No se usa ni persiste un token step-up separado y no existe un endpoint dedicado: el administrador reautentica mediante el flujo MFA normal. Rotar el refresh token conserva el instante MFA original y no renueva `auth_time`.

En el MVP, un step-up ausente u obsoleto mantiene `403 AUTH_FORBIDDEN`; no existe un código exclusivo. El cliente puede revisar permiso y `auth_time` antes de una mutación, pero ante un 403 conserva un mensaje genérico de autorización/reauthenticación. Esta limitación se registra como `STEP_UP_ERROR_AMBIGUITY_DEBT`.

## Alternativas
1. Mantener la opción preliminar/simple. 2. Adoptar una alternativa más compleja/administrada. 3. Decisión seleccionada con límites.

## Justificación
Prioriza consistencia, comprensibilidad, capacidad de prueba y cronograma.

## Consecuencias
Mejora claridad y trazabilidad; exige disciplina de contratos/configuración.

## Riesgos
Complejidad operativa y necesidad de actualizar documentación si cambia.

## Revisión
Reabrir solo ante requisito verificable que la decisión actual no satisfaga razonablemente.
