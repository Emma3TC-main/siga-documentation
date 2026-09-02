# Guía de Handoff Figma / UX-UI — SIGA

## 1. Propósito

Esta guía convierte los requisitos técnicos y administrativos de SIGA en un **brief de diseño ejecutable por Figma Make o un especialista UX/UI**. El diseño visual puede evolucionar; los IDs de vista, campos, permisos, estados y reglas no deben alterarse sin actualizar requisitos/ADR.

## 2. Foundations recomendadas

| Área | Baseline |
|---|---|
| Locale | `es-PE` |
| Zona visual | `America/Lima`; backend persiste UTC |
| Desktop primario | 1280 px o superior |
| Laptop/tablet landscape | 1024 px o superior |
| Smartphone web | consulta/adaptación; operación móvil principal es React Native |
| Grid/spacing | escala 4/8 px |
| Accesibilidad | WCAG 2.1 AA como referencia, no certificación |
| Component library | Material UI (MUI) + Data Grid Community |
| Estados | texto + icono + color; nunca color únicamente |

Para Figma, crear variables/tokens semánticos (no colores de negocio hardcodeados): `surface`, `text-primary`, `text-muted`, `status-success`, `status-warning`, `status-danger`, `focus`, etc. El equipo podrá ajustar la identidad visual sin romper la semántica de estados.

## 3. UI Kit / Atomic Design pragmático

**Átomos:** Button, IconButton, TextField, Select, Checkbox, Radio, Switch, Chip, Badge, Icon, Tooltip, Divider, Spinner/Skeleton.

**Moléculas:** SearchField, FilterBar, StockBadge, StateChip, ProductSelector, QuantityInput, UnitSelector, LocationSelector jerárquico, LotSelector, AssetSelector, CurrencyInput, DateRange, FilePreview, ConfirmAction.

**Organismos:** InventoryTable, ProductForm, MovementHeader, MovementDetailGrid, AuthorizationSummary, EvidenceUploader, LocationTree, DashboardGrid, AuditTable, ReportFilterPanel, NotificationPanel.

**Templates:** AuthLayout, DashboardLayout, ManagementLayout, TransactionLayout, DetailLayout, MobileStack.

El kit debe incluir variantes `default/hover/focus/disabled/error/loading` y tamaños. Los componentes destructivos o sensibles deben tener variante semántica explícita y confirmación.

## 4. Reglas UX transversales

1. **Frontend no es autoridad de stock.** Aunque muestre stock=10, una confirmación puede devolver 409 si otra operación consumió stock. Mostrar mensaje y refrescar.
2. **No optimistic update en transacciones críticas.** Movimiento, stock, costo, autorización y evidencia oficial muestran éxito solo después de respuesta backend.
3. **Operación sensible:** resumen → confirmación → step-up TOTP cuando aplica → ejecución → resultado.
4. **Estados obligatorios por vista:** loading/skeleton, empty, success, validation error, domain error, unauthorized, forbidden, unexpected con `correlationId`.
5. **Errores de campo** junto al control; **dominio** en alert/dialog; **temporales** con reintento; nunca stack trace.
6. Tablas grandes: paginación/filtro/sort server-side. No diseñar “cargar todo”.
7. Formularios multi-detalle deben permitir añadir/quitar líneas antes de confirmar y mostrar validación por línea.
8. En móvil, las transacciones requieren conectividad; si solo existe cache mostrar etiqueta **Datos guardados / pueden estar desactualizados**.

## 5. Navegación Web propuesta

- Autenticación: `/login`, `/mfa`.
- Operación: `/dashboard`, `/inventory`, `/movements`, `/movements/new`, `/movements/:id`, `/locations`, `/lots`, `/assets`, `/counts`, `/adjustments`.
- Catálogo: `/catalog/categories`, `/catalog/products`, `/catalog/units`.
- Administración: `/users`, `/roles`, `/settings`.
- Control: `/reports`, `/audit`.
- Notificaciones: panel/drawer global.

Los menús se ocultan/deshabilitan por permisos para UX, pero la autorización real se ejecuta en backend.

## 6. Matriz de vistas Web

| ID | Vista / frame Figma | Contenido mínimo | Acciones | Estados/variantes críticas |
|---|---|---|---|---|
| UI-W01 | Login | usuario/email, contraseña, recordar solo preferencia no token | ingresar | inválidas, bloqueo, rate limit |
| UI-W02 | MFA | 6 dígitos TOTP, contador informativo, reintento | verificar/cancelar | OTP inválido, expirado, límite |
| UI-W03 | Dashboard | 6–8 KPI, alertas, entradas/salidas, disponibilidad | filtrar período, navegar detalle | sin data, parcial, servicio analítico degradado |
| UI-W04 | Usuarios | tabla, estado, rol(es), búsqueda | alta, editar, desactivar | no borrado físico, permisos |
| UI-W05 | Roles | roles + matriz de permisos | crear/editar/asignar | rol protegido/conflicto |
| UI-W06 | Categorías | código, nombre, tipo, estado | CRUD lógico | duplicado/inactiva |
| UI-W07 | Productos | SKU, nombre, categoría, UoM, flags trazabilidad, stock mínimo, atributos técnicos | crear/editar/desactivar | campos dinámicos por tipo |
| UI-W08 | Unidades | código, símbolo, magnitud, conversiones por producto | crear/editar | factor >0/incompatible |
| UI-W09 | Inventario | DataGrid producto, total, ubicación, lote/serie, mínimo, costo si permiso | filtrar, detalle, iniciar movimiento | stale/refetch, sin stock, bajo mínimo |
| UI-W10 | Ubicaciones | árbol jerárquico almacén/patio→posición | alta/editar/desactivar | prevenir ciclos; stock existente |
| UI-W11 | Lotes/Activos | tabs/lists lote-colada-vencimiento / activo-serie-estado | registrar, mover, consultar historial | serie duplicada/vencido |
| UI-W12 | Nuevo movimiento | cabecera + grid N detalles + documento + responsable + centro costo | guardar borrador, submit, confirmar | validación por línea; autorización requerida |
| UI-W13 | Detalle movimiento | código, estado, actores, detalles, costos autorizados, evidencia, historial de estado | confirmar/acciones según estado | inmutable si CONFIRMADO |
| UI-W14 | Autorizar | resumen de riesgo/valor/activo, evidencia y motivo | aprobar/rechazar | step-up TOTP; estado cambió |
| UI-W15 | Transferencia | origen/destino por detalle | validar/confirmar | origen=destino, stock insuficiente |
| UI-W16 | Ajuste | +/- , motivo obligatorio, evidencia, diferencia | submit/autorizar | privilegio especial; resultado no negativo |
| UI-W17 | Conteo | ubicación/alcance, esperado vs contado, diferencia | guardar/cerrar/generar solicitud de ajuste | conteo cerrado/duplicado |
| UI-W18 | Evidencia contextual | drag/drop/select, preview, tipo doc, hash/estado tras upload | subir/quitar antes de confirmar/ver | MIME/tamaño/storage error |
| UI-W19 | Historial | tabla paginada con filtros por fecha/tipo/producto/usuario/doc | ver detalle/exportar | solo lectura |
| UI-W20 | Reportes | catálogo de reportes, filtros, formato | generar/descargar/ver persistidos | job en progreso/fallido |
| UI-W21 | Auditoría | eventos, actor, recurso, resultado, correlationId | filtrar/ver detalle | acceso restringido |
| UI-W22 | Notificaciones | drawer/lista, tipo, fecha, leído | marcar leído/navegar origen | polling/reintento |

## 7. Frames Mobile (React Native / Expo)

| ID | Vista | Elementos para prototipo | Reglas |
|---|---|---|---|
| UI-M01 | Login | usuario, contraseña, CTA | access memoria; no persistir secreto |
| UI-M02 | OTP | input 6 dígitos, estado | TOTP/step-up |
| UI-M03 | Inventario | búsqueda, filtros rápidos, lista/cards, estado de cache | consulta online; cache read-only |
| UI-M04 | Detalle | stock por ubicación, lote/serie, estado activo | indicar última actualización |
| UI-M05 | Movimiento | tipo, producto, qty, origen/destino, lote/activo, documento | **conexión obligatoria**; confirmación backend |
| UI-M06 | Evidencia | cámara, galería, PDF, preview y progreso | imagen≤10MB, PDF≤20MB baseline |
| UI-M07 | Notificaciones | lista/estado leído | polling MVP |
| UI-M08 | Perfil | identidad/roles visibles, logout | refresh token en SecureStore |

Para patio/maquinaria, el detalle del activo debe mostrar como mínimo código interno, serie/VIN/PIN, producto/modelo, estado operativo y ubicación. La acción de movimiento debe permitir fotografía de evidencia.

## 8. Movimiento multi-detalle — frame prioritario

Diseñar el formulario en tres zonas:

1. **Cabecera:** tipo, fecha efectiva si aplica, responsable/solicitante, centro de costo, tipo/número de documento, observación, moneda/tipo de cambio para entrada valorizada.
2. **Detalle editable:** producto, cantidad, UoM, origen/destino, lote/serie/activo, costo en entrada. Mostrar errores por línea y permitir N filas.
3. **Resumen/confirmación:** número de líneas, cantidades/valor autorizado, operaciones sensibles, evidencia, botón Guardar borrador / Enviar a autorización / Confirmar según estado.

Nunca mezclar `AUTORIZADO` con `CONFIRMADO`: la pantalla debe mostrar que una autorización aún no ha afectado stock.

## 9. Dashboard

Máximo aproximado 6–8 tarjetas/alertas principales: valor total de inventario, disponibilidad de activos, bajo stock, sin stock, próximos a vencer, entradas/salidas del período y movimientos sensibles. La analítica profunda pertenece a Reportes/BI. Recharts se usa para visualizaciones sencillas y siempre debe existir una alternativa textual/tabla cuando el dato sea importante.

## 10. Evidencias

Flujo Figma: **seleccionar → preview → validar → progreso → almacenada/disponible → consultar**. Mostrar nombre original, tipo, tamaño, fecha y estado; no exponer `object_key` interno como si fuera URL pública. Las URLs firmadas son evolución; MVP usa backend multipart.

## 11. Handoff obligatorio por frame

Cada frame/componente final debe incluir una anotación o página de specs con: `UI-ID`, actor/rol, ruta, CUS/HU, endpoint(s), permiso(s), campos y formatos, reglas de validación, estados, mensajes de dominio esperables, breakpoint/responsive, acciones sensibles y caso de prueba principal. Esto evita que el diseño visual introduzca un flujo contradictorio al Manual Técnico.

## 12. Flujo Wireframe → Mockup → Implementación

- **Wireframe lógico:** estructura y comportamiento; puede existir desde Sprint 1.
- **Mockup Figma aprobado:** componentes/tokens/estados y prototipo navegable.
- **Captura real:** evidencia de implementación; se sustituye/añade al informe cuando la pantalla ya existe.

Usar IDs estables como `FIG-UI-W12-MOCKUP` y `FIG-UI-W12-IMPLEMENTACION`. La guía `Guia_Imagenes_Informe_SIGA.md` indica la colocación en el informe.
