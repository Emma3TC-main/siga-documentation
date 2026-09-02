# Guía para elaborar el Manual de Usuario — SIGA

## Objetivo

El Manual de Usuario se produce **después de que las pantallas estén implementadas**. Este archivo define la estructura, capturas y mensajes que deben documentarse sin convertir el Manual Técnico en un tutorial de usuario prematuro.

## Estructura recomendada

1. Portada/control documental.
2. Propósito y alcance.
3. Requisitos de acceso y perfiles.
4. Inicio de sesión y MFA.
5. Navegación general Web.
6. Consulta de inventario.
7. Productos/catálogos según rol.
8. Entrada.
9. Salida ordinaria.
10. Salida sensible y autorización.
11. Transferencia.
12. Ajuste/conteo.
13. Lotes/series/activos.
14. Evidencias.
15. Historial.
16. Dashboard/reportes.
17. Auditoría (perfil autorizado).
18. Aplicación móvil.
19. Errores/mensajes frecuentes.
20. Cierre de sesión y buenas prácticas.

## Plantilla por procedimiento

| Campo | Contenido |
|---|---|
| Objetivo | Qué logra el usuario |
| Perfil | Rol/permisos necesarios |
| Precondiciones | Datos/estado/conectividad |
| Ruta | Menú/pantalla |
| Pasos | Secuencia numerada |
| Resultado esperado | Qué confirma SIGA |
| Mensajes frecuentes | Validación/403/409/etc. explicados al usuario |
| Capturas | IDs de figuras |
| Consideración de seguridad | MFA/step-up/evidencia cuando aplique |

## Capturas prioritarias

`UI-W01` Login, `UI-W02` MFA, `UI-W03` Dashboard, `UI-W09` Inventario, `UI-W12` Movimiento, `UI-W13` Detalle, `UI-W14` Autorizar, `UI-W15` Transferencia, `UI-W16` Ajuste, `UI-W18` Evidencia, `UI-W20` Reportes, `UI-M03` Inventario móvil, `UI-M05` Movimiento móvil, `UI-M06` Evidencia móvil.

La captura debe anonimizar credenciales, tokens, correos reales y cualquier secreto. No capturar consola con claves ni panel de RabbitMQ/DB con credenciales.

## Mensajes de usuario que deben explicarse

- **Stock insuficiente:** el stock pudo cambiar desde la consulta; refrescar y seleccionar otra cantidad/ubicación.
- **Pendiente de autorización:** aún no se modificó el inventario.
- **Sesión expirada:** el cliente intentará renovar; si no es posible, solicitará login.
- **Movimiento duplicado/reintento:** SIGA usa idempotencia para evitar doble efecto.
- **Sin conexión móvil:** se puede ver cache previa si existe, pero no confirmar entradas/salidas/transferencias/ajustes.
- **Evidencia rechazada:** formato/tamaño/contenido no permitido; seleccionar archivo válido.

## Mobile

Explicar que la app React Native/Expo comparte el backend central. El inventario mostrado desde cache debe marcarse como potencialmente desactualizado y **no autoriza** una transacción offline. El refresh token se almacena de manera segura por la aplicación; el usuario nunca lo gestiona manualmente.

## Relación con documentos técnicos

Usar la Matriz de Interfaces (cap. 18), `Guia_Figma_UI_UX_SIGA.md`, OpenAPI para mensajes/estados y `especificaciones/CUS_Detallados.md` como fuente para pre/postcondiciones. El manual de usuario no debe describir detalles internos como `FOR UPDATE`, Outbox o schemas PostgreSQL salvo en un anexo técnico dirigido a soporte.
