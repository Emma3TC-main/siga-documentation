# Diccionario de datos — SIGA (modelo canónico)
## Convenciones

- PostgreSQL 16+, `snake_case`, PK UUID y `TIMESTAMPTZ` en UTC.
- Cantidades/costos: `NUMERIC(18,6)` salvo KPI.
- `JSONB` solo para atributos técnicos, payloads y metadata extensible; nunca reemplaza stock, cantidad, lote, serie, ubicación, autorización o relaciones críticas.
- `active` representa desactivación lógica de maestros; movimientos confirmados y auditoría son inmutables.
- Una FK se define solo dentro del ownership del servicio. Los campos comentados como `external ... reference` son UUID deliberadamente **sin FK cross-schema**.
- Este archivo se deriva del `physical_model.sql` consolidado; ambos deben modificarse en el mismo cambio.
## iam.user_account
**Owner:** `identity-service`  
**Propósito:** Cuenta de usuario y estado de autenticación/MFA/bloqueo.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `username` | `varchar(100) NOT NULL UNIQUE` |
| `email` | `varchar(254) NOT NULL UNIQUE` |
| `password_hash` | `varchar(255) NOT NULL` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `mfa_enabled` | `boolean NOT NULL DEFAULT false` |
| `mfa_secret_encrypted` | `text` |
| `failed_login_attempts` | `integer NOT NULL DEFAULT 0 CHECK (failed_login_attempts >= 0)` |
| `locked_until` | `timestamptz` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `CHECK (NOT mfa_enabled OR mfa_secret_encrypted IS NOT NULL)`

## iam.role
**Owner:** `identity-service`  
**Propósito:** Rol RBAC administrable.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `code` | `varchar(80) NOT NULL UNIQUE` |
| `name` | `varchar(120) NOT NULL` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

## iam.permission
**Owner:** `identity-service`  
**Propósito:** Permiso atómico usado por autorización backend.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `code` | `varchar(120) NOT NULL UNIQUE` |
| `description` | `varchar(255) NOT NULL` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |

## iam.user_role
**Owner:** `identity-service`  
**Propósito:** Asignación N:M de usuarios a roles.
| Columna | Definición física |
|---|---|
| `user_id` | `uuid NOT NULL REFERENCES iam.user_account(id)` |
| `role_id` | `uuid NOT NULL REFERENCES iam.role(id)` |
| `assigned_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `PRIMARY KEY (user_id, role_id)`

## iam.role_permission
**Owner:** `identity-service`  
**Propósito:** Asignación N:M de roles a permisos.
| Columna | Definición física |
|---|---|
| `role_id` | `uuid NOT NULL REFERENCES iam.role(id)` |
| `permission_id` | `uuid NOT NULL REFERENCES iam.permission(id)` |
| `assigned_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `PRIMARY KEY (role_id, permission_id)`

## iam.refresh_token
**Owner:** `identity-service`  
**Propósito:** Sesión refresh rotativa/revocable; almacena hash, JTI y familia.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `user_id` | `uuid NOT NULL REFERENCES iam.user_account(id)` |
| `token_hash` | `varchar(255) NOT NULL UNIQUE` |
| `jti` | `uuid NOT NULL UNIQUE` |
| `family_id` | `uuid NOT NULL` |
| `expires_at` | `timestamptz NOT NULL` |
| `revoked_at` | `timestamptz` |
| `replaced_by_jti` | `uuid` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `CHECK (expires_at > created_at)`

**Índices relevantes:**
- `idx_refresh_token_user_active ON iam.refresh_token(user_id, expires_at) WHERE revoked_at IS NULL`
- `idx_refresh_token_family ON iam.refresh_token(family_id)`

## iam.outbox_event
**Owner:** `identity-service`  
**Propósito:** Eventos IAM pendientes de publicación confiable a RabbitMQ.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `aggregate_type` | `varchar(80) NOT NULL` |
| `aggregate_id` | `uuid NOT NULL` |
| `event_type` | `varchar(120) NOT NULL` |
| `schema_version` | `integer NOT NULL DEFAULT 1 CHECK (schema_version > 0)` |
| `correlation_id` | `uuid` |
| `causation_id` | `uuid` |
| `payload` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `status` | `varchar(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','PUBLISHED','FAILED'))` |
| `attempts` | `integer NOT NULL DEFAULT 0 CHECK (attempts >= 0)` |
| `next_attempt_at` | `timestamptz` |
| `occurred_at` | `timestamptz NOT NULL DEFAULT now()` |
| `published_at` | `timestamptz` |

**Índices relevantes:**
- `idx_iam_outbox_pending ON iam.outbox_event(status, next_attempt_at, occurred_at) WHERE status='PENDING'`

## catalog.category
**Owner:** `catalog-service`  
**Propósito:** Categoría industrial de materiales, insumos, repuestos o maquinaria.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `code` | `varchar(50) NOT NULL UNIQUE` |
| `name` | `varchar(120) NOT NULL` |
| `category_type` | `varchar(40) NOT NULL CHECK (category_type IN ('MATERIAL','INSUMO','REPUESTO','MAQUINARIA'))` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

## catalog.supplier
**Owner:** `catalog-service`  
**Propósito:** Maestro básico de proveedores usados para identificar el origen comercial de entradas, sin cubrir órdenes de compra, cotizaciones ni cuentas por pagar.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `code` | `varchar(50) NOT NULL UNIQUE` |
| `tax_id` | `varchar(20) NOT NULL UNIQUE` |
| `business_name` | `varchar(200) NOT NULL` |
| `trade_name` | `varchar(200)` |
| `contact_name` | `varchar(160)` |
| `phone` | `varchar(40)` |
| `email` | `varchar(254)` |
| `address` | `varchar(300)` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Índices relevantes:**
- `idx_supplier_business_name ON catalog.supplier(business_name)`

## catalog.unit_measure
**Owner:** `catalog-service`  
**Propósito:** Unidad de medida científica/logística.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `code` | `varchar(20) NOT NULL UNIQUE` |
| `name` | `varchar(80) NOT NULL` |
| `symbol` | `varchar(20) NOT NULL` |
| `dimension` | `varchar(40) NOT NULL` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

## catalog.product
**Owner:** `catalog-service`  
**Propósito:** Maestro de producto, configuración de trazabilidad y stock mínimo.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `sku` | `varchar(80) NOT NULL UNIQUE` |
| `name` | `varchar(200) NOT NULL` |
| `category_id` | `uuid NOT NULL REFERENCES catalog.category(id)` |
| `product_type` | `varchar(40) NOT NULL CHECK (product_type IN ('MATERIAL','INSUMO','REPUESTO','MAQUINARIA'))` |
| `storage_unit_id` | `uuid NOT NULL REFERENCES catalog.unit_measure(id)` |
| `base_unit_id` | `uuid NOT NULL REFERENCES catalog.unit_measure(id)` |
| `min_stock` | `numeric(18,6) NOT NULL DEFAULT 0 CHECK (min_stock >= 0)` |
| `requires_lot` | `boolean NOT NULL DEFAULT false` |
| `requires_heat_number` | `boolean NOT NULL DEFAULT false` |
| `requires_expiry` | `boolean NOT NULL DEFAULT false` |
| `requires_serial` | `boolean NOT NULL DEFAULT false` |
| `technical_attributes` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Índices relevantes:**
- `idx_product_category ON catalog.product(category_id)`
- `idx_product_technical_attributes ON catalog.product USING gin(technical_attributes)`

## catalog.unit_conversion
**Owner:** `catalog-service`  
**Propósito:** Conversiones múltiples por producto entre unidades válidas.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `product_id` | `uuid NOT NULL REFERENCES catalog.product(id)` |
| `from_unit_id` | `uuid NOT NULL REFERENCES catalog.unit_measure(id)` |
| `to_unit_id` | `uuid NOT NULL REFERENCES catalog.unit_measure(id)` |
| `factor` | `numeric(18,6) NOT NULL CHECK (factor > 0)` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `UNIQUE (product_id, from_unit_id, to_unit_id)`
- `CHECK (from_unit_id <> to_unit_id)`

**Índices relevantes:**
- `idx_unit_conversion_product ON catalog.unit_conversion(product_id)`

## catalog.outbox_event
**Owner:** `catalog-service`  
**Propósito:** Eventos de catálogo (ProductCreated/Updated, etc.) publicados por Outbox.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `aggregate_type` | `varchar(80) NOT NULL` |
| `aggregate_id` | `uuid NOT NULL` |
| `event_type` | `varchar(120) NOT NULL` |
| `schema_version` | `integer NOT NULL DEFAULT 1 CHECK (schema_version > 0)` |
| `correlation_id` | `uuid` |
| `causation_id` | `uuid` |
| `payload` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `status` | `varchar(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','PUBLISHED','FAILED'))` |
| `attempts` | `integer NOT NULL DEFAULT 0 CHECK (attempts >= 0)` |
| `next_attempt_at` | `timestamptz` |
| `occurred_at` | `timestamptz NOT NULL DEFAULT now()` |
| `published_at` | `timestamptz` |

**Índices relevantes:**
- `idx_catalog_outbox_pending ON catalog.outbox_event(status, next_attempt_at, occurred_at) WHERE status='PENDING'`

## inventory.location
**Owner:** `inventory-service`  
**Propósito:** Jerarquía física recursiva del almacén/patio/taller.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `code` | `varchar(80) NOT NULL UNIQUE` |
| `name` | `varchar(160) NOT NULL` |
| `location_type` | `varchar(30) NOT NULL CHECK (location_type IN ( 'ALMACEN','PATIO','ZONA','PASILLO','RACK','NIVEL','POSICION', 'TALLER','RECEPCION','CUARENTENA','DESPACHO' ))` |
| `parent_id` | `uuid REFERENCES inventory.location(id)` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `CHECK (parent_id IS NULL OR parent_id <> id)`

**Índices relevantes:**
- `idx_location_parent ON inventory.location(parent_id)`

## inventory.supplier_ref
**Owner:** `inventory-service`  
**Propósito:** Proyección local mínima del proveedor para validar y confirmar una entrada sin depender de una llamada REST síncrona a Catalog.
| Columna | Definición física |
|---|---|
| `supplier_id` | `uuid PRIMARY KEY` |
| `code` | `varchar(50) NOT NULL UNIQUE` |
| `tax_id` | `varchar(20) NOT NULL UNIQUE` |
| `business_name` | `varchar(200) NOT NULL` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `source_version` | `bigint NOT NULL DEFAULT 0` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

## inventory.product_ref
**Owner:** `inventory-service`  
**Propósito:** Proyección local de producto necesaria para reglas de Inventory sin llamada síncrona a Catalog.
| Columna | Definición física |
|---|---|
| `product_id` | `uuid PRIMARY KEY` |
| `sku` | `varchar(80) NOT NULL UNIQUE` |
| `product_type` | `varchar(40) NOT NULL CHECK (product_type IN ('MATERIAL','INSUMO','REPUESTO','MAQUINARIA'))` |
| `storage_unit_code` | `varchar(20) NOT NULL` |
| `base_unit_code` | `varchar(20) NOT NULL` |
| `min_stock` | `numeric(18,6) NOT NULL DEFAULT 0 CHECK (min_stock >= 0)` |
| `requires_lot` | `boolean NOT NULL DEFAULT false` |
| `requires_heat_number` | `boolean NOT NULL DEFAULT false` |
| `requires_serial` | `boolean NOT NULL DEFAULT false` |
| `requires_expiry` | `boolean NOT NULL DEFAULT false` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `source_version` | `bigint NOT NULL DEFAULT 0` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

## inventory.product_unit_conversion_ref
**Owner:** `inventory-service`  
**Propósito:** Proyección local de conversiones de unidad del producto.
| Columna | Definición física |
|---|---|
| `product_id` | `uuid NOT NULL REFERENCES inventory.product_ref(product_id)` |
| `from_unit_code` | `varchar(20) NOT NULL` |
| `to_unit_code` | `varchar(20) NOT NULL` |
| `factor` | `numeric(18,6) NOT NULL CHECK (factor > 0)` |
| `active` | `boolean NOT NULL DEFAULT true` |
| `source_version` | `bigint NOT NULL DEFAULT 0` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `PRIMARY KEY (product_id, from_unit_code, to_unit_code)`
- `CHECK (from_unit_code <> to_unit_code)`

## inventory.lot
**Owner:** `inventory-service`  
**Propósito:** Lote/colada y vencimiento asociado a un producto.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `product_id` | `uuid NOT NULL REFERENCES inventory.product_ref(product_id)` |
| `lot_number` | `varchar(120)` |
| `heat_number` | `varchar(120)` |
| `manufactured_at` | `date` |
| `received_at` | `date` |
| `expires_at` | `date` |
| `status` | `varchar(30) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','QUARANTINED','EXPIRED','DEPLETED','BLOCKED'))` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `UNIQUE (id, product_id)`
- `CHECK (expires_at IS NULL OR manufactured_at IS NULL OR expires_at >= manufactured_at)`

**Índices relevantes:**
- `uq_lot_product_number ON inventory.lot(product_id, lot_number) WHERE lot_number IS NOT NULL`
- `idx_lot_product ON inventory.lot(product_id)`
- `idx_lot_expiry ON inventory.lot(expires_at) WHERE expires_at IS NOT NULL`

## inventory.asset
**Owner:** `inventory-service`  
**Propósito:** Unidad física serializada (maquinaria o repuesto serializable). No duplica ubicación actual.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `product_id` | `uuid NOT NULL REFERENCES inventory.product_ref(product_id)` |
| `asset_code` | `varchar(80) NOT NULL UNIQUE` |
| `serial_number` | `varchar(160) NOT NULL UNIQUE` |
| `brand` | `varchar(100)` |
| `model` | `varchar(100)` |
| `operational_status` | `varchar(40) NOT NULL DEFAULT 'OPERATIVO' CHECK (operational_status IN ( 'OPERATIVO','EN_MANTENIMIENTO','EN_TRANSITO','INOPERATIVO','FUERA_SERVICIO' ))` |
| `technical_snapshot` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `UNIQUE (id, product_id)`

**Índices relevantes:**
- `idx_asset_product ON inventory.asset(product_id)`

## inventory.stock_balance
**Owner:** `inventory-service`  
**Propósito:** Fuente autoritativa de existencia, ubicación, lote/activo y costo promedio.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `product_id` | `uuid NOT NULL REFERENCES inventory.product_ref(product_id)` |
| `location_id` | `uuid NOT NULL REFERENCES inventory.location(id)` |
| `lot_id` | `uuid` |
| `asset_id` | `uuid` |
| `quantity` | `numeric(18,6) NOT NULL CHECK (quantity >= 0)` |
| `avg_cost_pen` | `numeric(18,6) NOT NULL DEFAULT 0 CHECK (avg_cost_pen >= 0)` |
| `version` | `bigint NOT NULL DEFAULT 0` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `FOREIGN KEY (lot_id, product_id) REFERENCES inventory.lot(id, product_id)`
- `FOREIGN KEY (asset_id, product_id) REFERENCES inventory.asset(id, product_id)`
- `CHECK (asset_id IS NULL OR quantity IN (0,1))`

**Índices relevantes:**
- `idx_stock_product_location ON inventory.stock_balance(product_id, location_id)`
- `idx_stock_lot ON inventory.stock_balance(lot_id) WHERE lot_id IS NOT NULL`

## inventory.movement
**Owner:** `inventory-service`  
**Propósito:** Cabecera inmutable al confirmar; registra tipo, estado, actores, centro de costo, proveedor de recepción cuando aplique y sensibilidad.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `movement_code` | `varchar(80) NOT NULL UNIQUE` |
| `movement_type` | `varchar(30) NOT NULL CHECK (movement_type IN ( 'ENTRY','EXIT','TRANSFER','ADJUST_POSITIVE','ADJUST_NEGATIVE' ))` |
| `status` | `varchar(40) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ( 'DRAFT','PENDING_AUTHORIZATION','AUTHORIZED','CONFIRMED','REJECTED','CANCELLED' ))` |
| `registered_by_user_id` | `uuid NOT NULL` |
| `requested_by_user_id` | `uuid` |
| `cost_center_code` | `varchar(80)` |
| `cost_center_name_snapshot` | `varchar(160)` |
| `supplier_id` | `uuid REFERENCES inventory.supplier_ref(supplier_id)` |
| `supplier_name_snapshot` | `varchar(200)` |
| `supplier_tax_id_snapshot` | `varchar(20)` |
| `reference_doc_type` | `varchar(40)` |
| `reference_doc_number` | `varchar(120)` |
| `reason` | `varchar(255)` |
| `notes` | `text` |
| `is_sensitive` | `boolean NOT NULL DEFAULT false` |
| `sensitivity_reason` | `varchar(255)` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `submitted_at` | `timestamptz` |
| `confirmed_at` | `timestamptz` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `CHECK (NOT is_sensitive OR sensitivity_reason IS NOT NULL)`
- `CHECK (supplier_id IS NULL OR movement_type = 'ENTRY')`
- `CHECK (supplier_id IS NULL OR (supplier_name_snapshot IS NOT NULL AND supplier_tax_id_snapshot IS NOT NULL))`

**Índices relevantes:**
- `idx_movement_status_created ON inventory.movement(status, created_at DESC)`
- `idx_movement_type_created ON inventory.movement(movement_type, created_at DESC)`
- `idx_movement_actor ON inventory.movement(registered_by_user_id, created_at DESC)`
- `idx_movement_supplier ON inventory.movement(supplier_id, created_at DESC) WHERE supplier_id IS NOT NULL`
- `idx_movement_cost_center ON inventory.movement(cost_center_code, created_at DESC) WHERE cost_center_code IS NOT NULL`

## inventory.movement_detail
**Owner:** `inventory-service`  
**Propósito:** Líneas con snapshot de cantidades/unidad/conversión, trazabilidad, ubicaciones y costos/TC.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `movement_id` | `uuid NOT NULL REFERENCES inventory.movement(id)` |
| `line_number` | `integer NOT NULL CHECK (line_number > 0)` |
| `product_id` | `uuid NOT NULL REFERENCES inventory.product_ref(product_id)` |
| `entered_quantity` | `numeric(18,6) NOT NULL CHECK (entered_quantity > 0)` |
| `unit_code` | `varchar(20) NOT NULL` |
| `conversion_factor` | `numeric(18,6) NOT NULL DEFAULT 1 CHECK (conversion_factor > 0)` |
| `stock_quantity` | `numeric(18,6) NOT NULL CHECK (stock_quantity > 0)` |
| `origin_location_id` | `uuid REFERENCES inventory.location(id)` |
| `destination_location_id` | `uuid REFERENCES inventory.location(id)` |
| `lot_id` | `uuid` |
| `asset_id` | `uuid` |
| `original_currency` | `char(3) NOT NULL DEFAULT 'PEN'` |
| `original_unit_cost` | `numeric(18,6) CHECK (original_unit_cost IS NULL OR original_unit_cost >= 0)` |
| `exchange_rate` | `numeric(18,6) CHECK (exchange_rate IS NULL OR exchange_rate > 0)` |
| `exchange_rate_date` | `date` |
| `exchange_rate_source` | `varchar(40)` |
| `base_unit_cost_pen` | `numeric(18,6) CHECK (base_unit_cost_pen IS NULL OR base_unit_cost_pen >= 0)` |
| `applied_avg_cost_pen` | `numeric(18,6) CHECK (applied_avg_cost_pen IS NULL OR applied_avg_cost_pen >= 0)` |

**Restricciones de tabla:**
- `FOREIGN KEY (lot_id, product_id) REFERENCES inventory.lot(id, product_id)`
- `FOREIGN KEY (asset_id, product_id) REFERENCES inventory.asset(id, product_id)`
- `UNIQUE (movement_id, line_number)`
- `CHECK (origin_location_id IS NULL OR destination_location_id IS NULL OR origin_location_id <> destination_location_id)`
- `CHECK (         original_currency = 'PEN'         OR (exchange_rate IS NOT NULL AND exchange_rate_date IS NOT NULL AND exchange_rate_source IS NOT NULL)     )`

**Índices relevantes:**
- `idx_movement_detail_product ON inventory.movement_detail(product_id)`
- `idx_movement_detail_origin ON inventory.movement_detail(origin_location_id) WHERE origin_location_id IS NOT NULL`
- `idx_movement_detail_destination ON inventory.movement_detail(destination_location_id) WHERE destination_location_id IS NOT NULL`

## inventory.movement_authorization
**Owner:** `inventory-service`  
**Propósito:** Decisión de autorización sensible y step-up MFA.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `movement_id` | `uuid NOT NULL REFERENCES inventory.movement(id)` |
| `requested_at` | `timestamptz NOT NULL DEFAULT now()` |
| `decided_at` | `timestamptz` |
| `authorized_by_user_id` | `uuid` |
| `decision` | `varchar(20) CHECK (decision IS NULL OR decision IN ('APPROVED','REJECTED'))` |
| `step_up_verified` | `boolean NOT NULL DEFAULT false` |
| `reason` | `varchar(255)` |

**Restricciones de tabla:**
- `CHECK (         (decision IS NULL AND decided_at IS NULL)         OR (decision IS NOT NULL AND decided_at IS NOT NULL AND authorized_by_user_id IS NOT NULL)     )`

**Índices relevantes:**
- `idx_authorization_pending ON inventory.movement_authorization(movement_id, requested_at DESC) WHERE decision IS NULL`

## inventory.physical_count
**Owner:** `inventory-service`  
**Propósito:** Cabecera de conteo físico por ubicación.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `location_id` | `uuid NOT NULL REFERENCES inventory.location(id)` |
| `status` | `varchar(30) NOT NULL DEFAULT 'DRAFT' CHECK (status IN ('DRAFT','IN_PROGRESS','COMPLETED','CANCELLED'))` |
| `counted_by_user_id` | `uuid NOT NULL` |
| `notes` | `text` |
| `started_at` | `timestamptz NOT NULL DEFAULT now()` |
| `completed_at` | `timestamptz` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `CHECK (completed_at IS NULL OR completed_at >= started_at)`

## inventory.physical_count_line
**Owner:** `inventory-service`  
**Propósito:** Diferencias físico vs sistema por producto/lote/activo.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `count_id` | `uuid NOT NULL REFERENCES inventory.physical_count(id)` |
| `product_id` | `uuid NOT NULL REFERENCES inventory.product_ref(product_id)` |
| `lot_id` | `uuid` |
| `asset_id` | `uuid` |
| `system_quantity` | `numeric(18,6) NOT NULL CHECK (system_quantity >= 0)` |
| `counted_quantity` | `numeric(18,6) NOT NULL CHECK (counted_quantity >= 0)` |
| `difference_quantity` | `numeric(18,6) GENERATED ALWAYS AS (counted_quantity - system_quantity) STORED` |

**Restricciones de tabla:**
- `FOREIGN KEY (lot_id, product_id) REFERENCES inventory.lot(id, product_id)`
- `FOREIGN KEY (asset_id, product_id) REFERENCES inventory.asset(id, product_id)`

**Índices relevantes:**
- `idx_count_line_count ON inventory.physical_count_line(count_id)`
- `idx_count_line_product ON inventory.physical_count_line(product_id)`

## inventory.idempotency_record
**Owner:** `inventory-service`  
**Propósito:** Resultado persistido de comandos críticos por Idempotency-Key.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `idempotency_key` | `uuid NOT NULL UNIQUE` |
| `request_hash` | `char(64) NOT NULL` |
| `resource_type` | `varchar(80) NOT NULL` |
| `resource_id` | `uuid` |
| `response_status` | `integer NOT NULL CHECK (response_status BETWEEN 100 AND 599)` |
| `response_body` | `jsonb` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `expires_at` | `timestamptz NOT NULL` |

**Restricciones de tabla:**
- `CHECK (expires_at > created_at)`

**Índices relevantes:**
- `idx_idempotency_expiry ON inventory.idempotency_record(expires_at)`

## inventory.processed_event
**Owner:** `inventory-service`  
**Propósito:** Deduplicación de eventos de Catalog consumidos por Inventory.
| Columna | Definición física |
|---|---|
| `event_id` | `uuid NOT NULL` |
| `consumer` | `varchar(120) NOT NULL` |
| `processed_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `PRIMARY KEY (event_id, consumer)`

## inventory.outbox_event
**Owner:** `inventory-service`  
**Propósito:** Eventos Inventory insertados en el mismo commit que stock/movimiento.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `aggregate_type` | `varchar(80) NOT NULL` |
| `aggregate_id` | `uuid NOT NULL` |
| `event_type` | `varchar(120) NOT NULL` |
| `schema_version` | `integer NOT NULL DEFAULT 1 CHECK (schema_version > 0)` |
| `correlation_id` | `uuid` |
| `causation_id` | `uuid` |
| `payload` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `status` | `varchar(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','PUBLISHED','FAILED'))` |
| `attempts` | `integer NOT NULL DEFAULT 0 CHECK (attempts >= 0)` |
| `next_attempt_at` | `timestamptz` |
| `occurred_at` | `timestamptz NOT NULL DEFAULT now()` |
| `published_at` | `timestamptz` |

**Índices relevantes:**
- `idx_inventory_outbox_pending ON inventory.outbox_event(status, next_attempt_at, occurred_at) WHERE status='PENDING'`

## evidence.evidence_metadata
**Owner:** `evidence-service`  
**Propósito:** Metadata e integridad de archivo con propietario genérico MOVEMENT/ASSET/ADJUSTMENT/REPORT.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `owner_type` | `varchar(30) NOT NULL CHECK (owner_type IN ('MOVEMENT','ASSET','ADJUSTMENT','REPORT'))` |
| `owner_id` | `uuid NOT NULL` |
| `object_key` | `varchar(500) NOT NULL UNIQUE` |
| `original_filename` | `varchar(255) NOT NULL` |
| `content_type` | `varchar(120) NOT NULL` |
| `size_bytes` | `bigint NOT NULL CHECK (size_bytes > 0)` |
| `sha256` | `char(64) NOT NULL CHECK (sha256 ~ '^[0-9a-fA-F]{64}$')` |
| `storage_provider` | `varchar(30) NOT NULL CHECK (storage_provider IN ('MINIO','GCS'))` |
| `uploaded_by_user_id` | `uuid NOT NULL` |
| `status` | `varchar(30) NOT NULL DEFAULT 'RECEIVED' CHECK (status IN ('RECEIVED','VALIDATING','STORED','AVAILABLE','REJECTED','ARCHIVED'))` |
| `metadata` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `uploaded_at` | `timestamptz NOT NULL DEFAULT now()` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Índices relevantes:**
- `idx_evidence_owner ON evidence.evidence_metadata(owner_type, owner_id)`
- `idx_evidence_uploader ON evidence.evidence_metadata(uploaded_by_user_id, uploaded_at DESC)`
- `idx_evidence_sha256 ON evidence.evidence_metadata(sha256)`

## evidence.outbox_event
**Owner:** `evidence-service`  
**Propósito:** Eventos de evidencia publicados confiablemente.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `aggregate_type` | `varchar(80) NOT NULL` |
| `aggregate_id` | `uuid NOT NULL` |
| `event_type` | `varchar(120) NOT NULL` |
| `schema_version` | `integer NOT NULL DEFAULT 1 CHECK (schema_version > 0)` |
| `correlation_id` | `uuid` |
| `causation_id` | `uuid` |
| `payload` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `status` | `varchar(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','PUBLISHED','FAILED'))` |
| `attempts` | `integer NOT NULL DEFAULT 0 CHECK (attempts >= 0)` |
| `next_attempt_at` | `timestamptz` |
| `occurred_at` | `timestamptz NOT NULL DEFAULT now()` |
| `published_at` | `timestamptz` |

**Índices relevantes:**
- `idx_evidence_outbox_pending ON evidence.outbox_event(status, next_attempt_at, occurred_at) WHERE status='PENDING'`

## audit.audit_event
**Owner:** `audit-notification-service`  
**Propósito:** Auditoría funcional append-only de quién/qué/cuándo/resultado.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `event_type` | `varchar(120) NOT NULL` |
| `actor_id` | `uuid` |
| `aggregate_type` | `varchar(80)` |
| `aggregate_id` | `uuid` |
| `action` | `varchar(120) NOT NULL` |
| `result` | `varchar(30) NOT NULL` |
| `correlation_id` | `uuid` |
| `details` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `occurred_at` | `timestamptz NOT NULL DEFAULT now()` |

**Índices relevantes:**
- `idx_audit_occurred ON audit.audit_event(occurred_at DESC)`
- `idx_audit_correlation ON audit.audit_event(correlation_id) WHERE correlation_id IS NOT NULL`
- `idx_audit_aggregate ON audit.audit_event(aggregate_type, aggregate_id, occurred_at DESC)`
- `idx_audit_actor ON audit.audit_event(actor_id, occurred_at DESC) WHERE actor_id IS NOT NULL`

## audit.notification
**Owner:** `audit-notification-service`  
**Propósito:** Notificaciones in-app por usuario.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `user_id` | `uuid NOT NULL` |
| `type` | `varchar(80) NOT NULL` |
| `title` | `varchar(160) NOT NULL` |
| `message` | `text NOT NULL` |
| `reference_type` | `varchar(80)` |
| `reference_id` | `uuid` |
| `read_at` | `timestamptz` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |

**Índices relevantes:**
- `idx_notification_user_unread ON audit.notification(user_id, created_at DESC) WHERE read_at IS NULL`
- `idx_notification_user_created ON audit.notification(user_id, created_at DESC)`

## audit.processed_event
**Owner:** `audit-notification-service`  
**Propósito:** Deduplicación de eventos consumidos por Audit/Notification.
| Columna | Definición física |
|---|---|
| `event_id` | `uuid NOT NULL` |
| `consumer` | `varchar(120) NOT NULL` |
| `processed_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `PRIMARY KEY (event_id, consumer)`

## analytics.product_projection
**Owner:** `reporting-analytics-service`  
**Propósito:** Read model de producto para reporting.
| Columna | Definición física |
|---|---|
| `product_id` | `uuid PRIMARY KEY` |
| `sku` | `varchar(80) NOT NULL` |
| `name` | `varchar(200) NOT NULL` |
| `category_code` | `varchar(50)` |
| `category_name` | `varchar(120)` |
| `product_type` | `varchar(40) NOT NULL` |
| `base_unit_code` | `varchar(20) NOT NULL` |
| `storage_unit_code` | `varchar(20) NOT NULL` |
| `min_stock` | `numeric(18,6) NOT NULL DEFAULT 0` |
| `active` | `boolean NOT NULL` |
| `source_version` | `bigint NOT NULL DEFAULT 0` |
| `source_event_id` | `uuid` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Índices relevantes:**
- `idx_product_projection_category ON analytics.product_projection(category_code, active)`

## analytics.inventory_projection
**Owner:** `reporting-analytics-service`  
**Propósito:** Read model de existencia/valorización para dashboard y reportes.
| Columna | Definición física |
|---|---|
| `stock_balance_id` | `uuid PRIMARY KEY` |
| `product_id` | `uuid NOT NULL` |
| `location_id` | `uuid NOT NULL` |
| `lot_id` | `uuid` |
| `asset_id` | `uuid` |
| `quantity` | `numeric(18,6) NOT NULL` |
| `avg_cost_pen` | `numeric(18,6) NOT NULL` |
| `min_stock` | `numeric(18,6) NOT NULL DEFAULT 0` |
| `source_event_id` | `uuid` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Índices relevantes:**
- `idx_inventory_projection_product ON analytics.inventory_projection(product_id)`
- `idx_inventory_projection_location ON analytics.inventory_projection(location_id)`
- `idx_inventory_projection_low_stock ON analytics.inventory_projection(product_id) WHERE quantity <= min_stock`

## analytics.movement_projection
**Owner:** `reporting-analytics-service`  
**Propósito:** Read model de movimientos para consumo, valorización y análisis por centro de costo/proveedor.
| Columna | Definición física |
|---|---|
| `movement_id` | `uuid PRIMARY KEY` |
| `movement_code` | `varchar(80) NOT NULL` |
| `movement_type` | `varchar(30) NOT NULL` |
| `status` | `varchar(40) NOT NULL` |
| `registered_by_user_id` | `uuid` |
| `requested_by_user_id` | `uuid` |
| `cost_center_code` | `varchar(80)` |
| `cost_center_name_snapshot` | `varchar(160)` |
| `supplier_id` | `uuid` |
| `supplier_name_snapshot` | `varchar(200)` |
| `supplier_tax_id_snapshot` | `varchar(20)` |
| `total_base_cost_pen` | `numeric(18,6) NOT NULL DEFAULT 0` |
| `confirmed_at` | `timestamptz` |
| `source_event_id` | `uuid` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

**Índices relevantes:**
- `idx_movement_projection_confirmed ON analytics.movement_projection(confirmed_at DESC)`
- `idx_movement_projection_supplier ON analytics.movement_projection(supplier_id, confirmed_at DESC) WHERE supplier_id IS NOT NULL`
- `idx_movement_projection_cost_center ON analytics.movement_projection(cost_center_code, confirmed_at DESC) WHERE cost_center_code IS NOT NULL`

## analytics.kpi_snapshot
**Owner:** `reporting-analytics-service`  
**Propósito:** Snapshots históricos de KPIs.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `metric_code` | `varchar(80) NOT NULL` |
| `dimension_key` | `varchar(160) NOT NULL DEFAULT 'GLOBAL'` |
| `metric_value` | `numeric(20,6) NOT NULL` |
| `measured_at` | `timestamptz NOT NULL` |
| `source_event_id` | `uuid` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `UNIQUE (metric_code, dimension_key, measured_at)`

**Índices relevantes:**
- `idx_kpi_metric_time ON analytics.kpi_snapshot(metric_code, measured_at DESC)`

## analytics.report_job
**Owner:** `reporting-analytics-service`  
**Propósito:** Solicitud/estado/resultado de reportes y exportaciones.
| Columna | Definición física |
|---|---|
| `id` | `uuid PRIMARY KEY DEFAULT gen_random_uuid()` |
| `report_type` | `varchar(80) NOT NULL` |
| `requested_by_user_id` | `uuid NOT NULL` |
| `format` | `varchar(10) NOT NULL CHECK (format IN ('PDF','XLSX','CSV'))` |
| `filters` | `jsonb NOT NULL DEFAULT '{}'::jsonb` |
| `persist_result` | `boolean NOT NULL DEFAULT false` |
| `status` | `varchar(30) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING','RUNNING','COMPLETED','FAILED'))` |
| `object_key` | `varchar(500)` |
| `sha256` | `char(64)` |
| `error_message` | `text` |
| `created_at` | `timestamptz NOT NULL DEFAULT now()` |
| `started_at` | `timestamptz` |
| `completed_at` | `timestamptz` |

**Índices relevantes:**
- `idx_report_job_user_created ON analytics.report_job(requested_by_user_id, created_at DESC)`

## analytics.processed_event
**Owner:** `reporting-analytics-service`  
**Propósito:** Deduplicación de eventos consumidos por Reporting.
| Columna | Definición física |
|---|---|
| `event_id` | `uuid NOT NULL` |
| `consumer` | `varchar(120) NOT NULL` |
| `processed_at` | `timestamptz NOT NULL DEFAULT now()` |

**Restricciones de tabla:**
- `PRIMARY KEY (event_id, consumer)`

## analytics.export_checkpoint
**Owner:** `reporting-analytics-service`  
**Propósito:** Checkpoint de exportación/ETL incremental.
| Columna | Definición física |
|---|---|
| `consumer` | `varchar(120) PRIMARY KEY` |
| `last_event_id` | `uuid` |
| `last_occurred_at` | `timestamptz` |
| `updated_at` | `timestamptz NOT NULL DEFAULT now()` |

