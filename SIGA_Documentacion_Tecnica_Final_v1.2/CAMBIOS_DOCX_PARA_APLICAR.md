# Cambios puntuales en los DOCX aprobados — Proveedores v1.2

> Objetivo: **no regenerar ni remaquetar** los documentos aprobados. Aplicar solo las inserciones/reemplazos siguientes y actualizar índice/figuras si corresponde.

## A. Informe Curso Integrador II.docx

### 2.4 Alcance del proyecto
**Dónde:** en la enumeración de capacidades, después de “productos”.

**Agregar:** “proveedores;”

**Párrafo complementario al final del alcance funcional:**

> La gestión de proveedores se limita al mantenimiento de un maestro básico y a la identificación del proveedor asociado a las entradas originadas por abastecimiento externo. SIGA conservará la identificación histórica del proveedor en la recepción, sin incorporar órdenes de compra, cotizaciones, cuentas por pagar ni un proceso integral de compras.

**Por qué:** actualmente el alcance enumera catálogo, productos y entradas, pero no identifica el origen comercial de la recepción.

### 2.5 Requerimientos del proyecto
**Reemplazar:** “34 requerimientos funcionales” por **“35 requerimientos funcionales”**.

En la lista de capacidades principales, después de “categorías y productos”, agregar **“proveedores”**.

### 4.2 Objetivos específicos
En el objetivo de catálogo, cambiar:

> “categorías, productos, unidades de medida, conversiones y atributos técnicos…”

por:

> “categorías, productos, proveedores, unidades de medida, conversiones y atributos técnicos…”

### 5 Definición de los requerimientos
**Agregar sin renumerar ningún RF existente:**

| ID | Requerimiento | Definición |
|---|---|---|
| RF-35 | Proveedores | Gestionar proveedores básicos y asociarlos a entradas de abastecimiento externo, preservando su identificación histórica en el movimiento. |

### 6.1 Descripción del proyecto / arquitectura
En la responsabilidad de **Catalog Service**, cambiar a:

> Categorías, productos, proveedores, unidades, conversiones y atributos del catálogo.

No agregar un nuevo microservicio.

### 6.2 CUN-01 — Recepcionar y almacenar
**Reemplazar el inicio por:**

> Este proceso comienza con la recepción de materiales, insumos, repuestos o maquinaria. Cuando la recepción corresponda a abastecimiento externo, el proveedor constituye un actor externo del proceso y el encargado selecciona un proveedor activo registrado en SIGA. El encargado identifica además el producto, cantidad, unidad de medida, ubicación de destino, información de trazabilidad y documento de referencia. Al confirmar la entrada se conserva la identificación histórica del proveedor junto con el movimiento.

Mantener sin cambios las reglas actuales de lote/colada/vencimiento/serie, costo promedio, evidencia, ACID y auditoría.

### 6.3 Aspectos dentro del alcance
En **Catálogo industrial**, agregar:

- proveedores básicos y estado activo/inactivo;

En **Movimientos**, agregar:

- asociación de proveedor a recepciones de abastecimiento externo;
- snapshot de razón social e identificador tributario para trazabilidad histórica.

### 6.4 Aspectos fuera del alcance
No eliminar la exclusión del ERP completo. Aclararla con esta redacción:

> La gestión básica de proveedores sí forma parte de SIGA; continúan fuera del alcance la gestión integral de compras, órdenes de compra, solicitudes de cotización, comparación de ofertas, cuentas por pagar, homologación avanzada, portal de proveedores y demás funciones propias de un ERP/SRM.

### 8 / 8.1 Casos de uso del negocio
Mantener los **7 CUN**. No crear un octavo proceso solo para proveedor.

Modificar CUN-01:

- Actor de negocio: **Proveedor externo, Encargado / Recepción**.
- Entrada: **Proveedor, documento, producto, cantidad, costo y trazabilidad**.
- Resultado: **Existencia ubicada y recepción trazable con origen identificado**.
- CUS relacionados: agregar **CUS-31**.

Insertar `diagramas/uml/UML_10_Casos_Uso_Negocio_Proveedores.puml` como figura complementaria del impacto.

### 9 / 9.1 Casos de uso del sistema
Cambiar la línea base de **30 CUS** a **31 CUS** y agregar, sin renumerar CUS-01..CUS-30:

| ID | Caso de uso | Actor principal |
|---|---|---|
| CUS-31 | Gestionar proveedores | Administrador / usuario de catálogo autorizado |

En **Grupo 2 — Catálogo**, agregar CUS-31. El proveedor externo **no** es actor del sistema porque no inicia sesión ni opera SIGA.

Insertar `diagramas/uml/UML_11_Casos_Uso_Sistema_Proveedores.puml`.

### 10–12 Requisitos / trazabilidad / HU
Agregar **RF-35 ↔ US-35 ↔ CUS-31/CUS-07**. No cambiar IDs existentes.

Historia de usuario sugerida:

> **US-35 — Gestión de proveedores.** Como administrador o usuario de catálogo autorizado, quiero registrar, consultar, actualizar y desactivar proveedores para identificar de forma trazable el origen de las recepciones externas.

### 17–18 Modelo de datos / DER
Actualizar las figuras por las versiones v1.2 del paquete técnico. El total pasa a **40 tablas**:

- IAM 7
- Catalog 6
- Inventory 15
- Evidence 2
- Audit 3
- Analytics 7

Mantener **0 FK cross-schema**.

---

## B. Manual_Administrativo_SIGA_Final(2).docx

### 2. Actores
Agregar:

| Actor | Responsabilidades principales |
|---|---|
| Proveedor externo | Entregar materiales, insumos, repuestos o maquinaria y su documentación de sustento. Es actor del proceso de recepción, pero no usuario autenticado de SIGA en el MVP. |

### 3. Principios de negocio
Agregar un principio:

> Las entradas originadas por abastecimiento externo deben permitir identificar al proveedor y conservar su identidad histórica, aun cuando posteriormente sea actualizado o desactivado.

### 4. Proceso general de gestión
En “Configuración de datos maestros”, agregar **proveedores**.

En “Registro de entradas”, cambiar a:

> Recepción, identificación de proveedor cuando corresponda, validación, ubicación, sustento documental y actualización de existencias.

### Nueva subsección breve después de Gestión de productos (o antes de Inventario)
**Título sugerido: Gestión de proveedores**

> SIGA mantiene un maestro básico de proveedores para identificar el origen de las recepciones externas. Como mínimo debe conservar código interno, RUC u otro identificador tributario, razón social, nombre comercial opcional, datos de contacto, dirección y estado activo/inactivo. La desactivación es lógica y no elimina referencias históricas. Esta gestión no incluye órdenes de compra, cotizaciones, cuentas por pagar ni homologación avanzada.

### 10. Entrada de productos
En el flujo administrativo, después de “Selecciona el producto”, agregar:

> Si la entrada corresponde a abastecimiento externo, selecciona un proveedor activo.

Antes de confirmar, agregar la validación:

> El sistema valida que el proveedor exista y se encuentre activo cuando la recepción externa lo requiera.

En reglas, agregar:

> Al confirmar una recepción asociada a proveedor, SIGA conserva su identificador y un snapshot de razón social e identificador tributario para que cambios posteriores en el maestro no alteren la trazabilidad histórica.

### 14.2 Información obligatoria del movimiento
En **Datos de responsabilidad/origen**, agregar:

- proveedor cuando corresponda;
- razón social e identificador tributario preservados como snapshot histórico en recepciones externas.

### 18.3 Integraciones futuras
**Reemplazar** “ERP para compras/proveedores” por:

> ERP/SRM o gestión integral de compras y proveedores: órdenes de compra, cotizaciones, comparación de ofertas, cuentas por pagar, homologación avanzada, portal de proveedores y flujos bidireccionales.

Así el documento deja de contradecir el nuevo maestro básico de proveedores dentro de SIGA.

### 21. Planificación por sprints
- Sprint 2: agregar **maestro básico de proveedores**.
- Sprint 3: agregar **asociación proveedor–entrada y snapshot histórico**.

### 23. Controles administrativos consolidados
Agregar:

| Área | Control | Regla principal |
|---|---|---|
| Proveedores | Estado e identificación | Recepción externa usa proveedor activo; desactivación no rompe historial. |

---


## C. Manual_Tecnico_SIGA_Final.docx

> El DOCX técnico del paquete original se conserva para no alterar su maquetación. Estas son las modificaciones puntuales que deben trasladarse desde `Manual_Tecnico_SIGA_Final.md` v1.2.

### 2.2 Requerimientos funcionales
Agregar al final de la tabla de RF, sin renumerar los anteriores:

| ID | Requerimiento | Resumen | HU | CUS |
|---|---|---|---|---|
| RF-35 | Proveedores | Maestro básico y vínculo trazable con entradas externas. | US-35 | CUS-31 / CUS-07 |

### 5.1 Modelo físico / ownership PostgreSQL
Cambiar los conteos:

- `catalog`: **5 → 6 tablas**.
- `inventory`: **14 → 15 tablas**.
- total físico: **38 → 40 tablas**.

Mantener sin cambios IAM 7 / Evidence 2 / Audit 3 / Analytics 7 y **0 FK cross-schema**.

### 5.4 Transacción crítica de Inventory
En el paso donde actualmente se cargan `product_ref/conversion_ref`, reemplazar por:

> Cargar detalles y reglas desde `product_ref`/`conversion_ref` y, cuando aplique, `supplier_ref` locales.

Agregar la aclaración:

> La validación del proveedor durante la confirmación utiliza `inventory.supplier_ref`; el commit no depende de una llamada REST síncrona a Catalog.

### 5.7 Soft delete e inmutabilidad
Cambiar:

> Usuarios/categorías/productos/ubicaciones/UoM se desactivan.

por:

> Usuarios/categorías/productos/**proveedores**/ubicaciones/UoM se desactivan.

### Adenda v1.2 — Gestión de proveedores
Agregar al final del Manual Técnico:

> La revisión docente incorpora **proveedores** con un cambio deliberadamente acotado. `catalog-service` es owner de `catalog.supplier`; `inventory-service` mantiene `inventory.supplier_ref` por eventos de Catalog para validar entradas sin REST síncrono durante el commit. Las recepciones de abastecimiento externo guardan `supplier_id`, `supplier_name_snapshot` y `supplier_tax_id_snapshot` en `inventory.movement`; Reporting replica estos campos en `analytics.movement_projection`.
>
> El alcance se limita a alta, consulta, actualización y desactivación lógica de proveedores y a su asociación trazable con entradas. Permanecen fuera del MVP las órdenes de compra, cotizaciones, cuentas por pagar, homologación avanzada, portal de proveedor y un ERP de compras completo. Se conservan **seis servicios**, ownership por schema, cero FK cross-schema y la frontera ACID de Inventory.
>
> Artefactos impactados: RF-35/US-35/CUS-31, CUN-01/CUS-07, Catalog OpenAPI, Inventory OpenAPI, modelo físico/lógico/diccionario, DER-01/02/03/05/06/09, UML-01/03/04/06/10/11, C4-04, BPMN-01, SEQ-04 y matrices de pruebas/trazabilidad.

---

## D. Archivos que NO deben tocarse por este cambio

No se requiere modificar el diseño de salidas, transferencias, ajustes, evidencia, estados, IAM, DevOps ni el C4 de contexto/contendedores. **Sí cambia C4-04 Componentes de Inventory**, porque ya mostraba explícitamente las proyecciones locales provenientes de Catalog y ahora debe incluir `SupplierReference`.

## E. Artefactos derivados que deben regenerarse antes de entregar

- `diagramas/datos/DER_02_L#U00f3gico (dbDiagram).svg`: el SVG del ZIP original corresponde a v1.1. Regenerarlo desde el script DBML actualizado si se desea seguir usando esa exportación visual.
- `Manual_Tecnico_SIGA_Final.docx`: no se sobrescribe en este delta para respetar la maquetación aprobada. La fuente Markdown v1.2 y esta guía indican exactamente qué incorporar si se decide actualizar el DOCX.
