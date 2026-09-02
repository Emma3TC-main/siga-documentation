# Especificación de Casos de Uso del Negocio — SIGA

| ID | Proceso | Actor de negocio | Entrada | Resultado | CUS que lo automatizan |
|---|---|---|---|---|---|
| CUN-01 | Recepcionar y almacenar | Proveedor externo, Encargado / recepción | Proveedor, documento, producto, cantidad, costo, trazabilidad | Existencia ubicada y recepción trazable con origen identificado | CUS-07, CUS-24, CUS-25, CUS-26, CUS-31 |
| CUN-02 | Despachar/consumir | Solicitante, Encargado, Autorizador | Solicitud, destino/centro de costo, stock | Salida confirmada o rechazo controlado | CUS-08, CUS-27, CUS-26 |
| CUN-03 | Transferir inventario | Encargado/Supervisor | Origen, destino, cantidad | Nueva distribución sin variar stock total | CUS-09, CUS-24 |
| CUN-04 | Regularizar inventario | Supervisor/Encargado | Conteo, diferencia, motivo | Ajuste autorizado y trazable | CUS-10, CUS-28, CUS-27 |
| CUN-05 | Controlar trazabilidad/activos | Almacén/Supervisión | Producto/lote/serie/ubicación | Reconstrucción física e histórica | CUS-06, CUS-11, CUS-25 |
| CUN-06 | Supervisar/auditar | Administración/Seguridad TI | Movimientos, logs funcionales, períodos | Indicadores, reportes y auditoría | CUS-13, CUS-17, CUS-18, CUS-20 |
| CUN-07 | Explotar/interoperar | Analista/BI | Datos transaccionales aprobados | Dataset/reporting read-only | CUS-19, CUS-29, CUS-30 |

## Diferencia metodológica

El **CUN** modela el proceso de la empresa sin asumir una pantalla o endpoint; el **CUS** modela la interacción concreta con SIGA. Un CUN puede involucrar varios CUS y actores. Por esa razón las matrices RF vs CUS y los BPMN se mantienen separadas de las especificaciones REST.

## Reglas para diagramar

- BPMN/activity: swimlanes por actor/unidad y SIGA cuando automatiza una actividad.
- Gateways solo para decisiones reales: stock suficiente, sensibilidad/autorización, validación de evidencia, etc.
- El resultado de un CUN no debe contradecir las reglas administrativas de inmutabilidad, trazabilidad o multiubicación.


### CUN-01 — impacto de proveedor (v1.2)

El **Proveedor externo** participa como actor de negocio en la recepción, pero no como usuario del sistema: entrega el recurso y su sustento documental. El Encargado/Recepción selecciona en SIGA un proveedor activo cuando la entrada corresponde a abastecimiento externo. La recepción conserva `supplier_id`, razón social y RUC/identificador tributario como snapshot histórico. Devoluciones u otros ingresos internos pueden no requerir proveedor según la política de origen del movimiento.
