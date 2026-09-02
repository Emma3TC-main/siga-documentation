-- SIGA demo seed aligned with physical_model.sql v1.1
-- DEV/TEST only. Password hash is a placeholder and must be replaced by an Argon2id hash in application bootstrap.

INSERT INTO iam.permission(id,code,description) VALUES
('10000000-0000-0000-0000-000000000001','INVENTORY_READ','Consultar inventario'),
('10000000-0000-0000-0000-000000000002','MOVEMENT_CREATE','Crear movimientos'),
('10000000-0000-0000-0000-000000000003','MOVEMENT_AUTHORIZE','Autorizar movimientos sensibles'),
('10000000-0000-0000-0000-000000000004','INVENTORY_ADJUST','Registrar ajustes'),
('10000000-0000-0000-0000-000000000005','PRODUCT_WRITE','Gestionar catálogo'),
('10000000-0000-0000-0000-000000000006','AUDIT_READ','Consultar auditoría'),
('10000000-0000-0000-0000-000000000007','REPORT_READ','Consultar reportes'),
('10000000-0000-0000-0000-000000000008','USER_MANAGE','Gestionar usuarios'),
('10000000-0000-0000-0000-000000000009','ROLE_MANAGE','Gestionar roles');

INSERT INTO iam.role(id,code,name) VALUES
('11000000-0000-0000-0000-000000000001','ADMIN','Administrador'),
('11000000-0000-0000-0000-000000000002','ENCARGADO','Encargado de almacén'),
('11000000-0000-0000-0000-000000000003','SUPERVISOR','Supervisor');

INSERT INTO iam.role_permission(role_id,permission_id)
SELECT '11000000-0000-0000-0000-000000000001'::uuid,id FROM iam.permission;

INSERT INTO iam.user_account(id,username,email,password_hash,mfa_enabled)
VALUES ('12000000-0000-0000-0000-000000000001','admin.demo','admin.demo@siga.local',
        '$argon2id$DEMO_REPLACE_WITH_REAL_HASH',false);

INSERT INTO iam.user_role(user_id,role_id)
VALUES ('12000000-0000-0000-0000-000000000001','11000000-0000-0000-0000-000000000001');

-- Proveedor demo para recepción externa (RF-35 / CUS-31)
INSERT INTO catalog.supplier (id, code, tax_id, business_name, trade_name, contact_name, phone, email, address) VALUES
('70000000-0000-0000-0000-000000000001','PRV-001','20123456789','Suministros Industriales Andinos S.A.C.','SIA','María Quispe','+51 999 111 222','ventas@sia.example','Lima, Perú')
ON CONFLICT DO NOTHING;

INSERT INTO catalog.category(id,code,name,category_type) VALUES
('20000000-0000-0000-0000-000000000001','MAT-ACERO','Aceros y aleaciones','MATERIAL'),
('20000000-0000-0000-0000-000000000002','REP-ROD','Rodamientos y retenes','REPUESTO'),
('20000000-0000-0000-0000-000000000003','INS-LUB','Lubricantes industriales','INSUMO'),
('20000000-0000-0000-0000-000000000004','MAQ-TIERRA','Movimiento de tierras','MAQUINARIA');

INSERT INTO catalog.unit_measure(id,code,name,symbol,dimension) VALUES
('21000000-0000-0000-0000-000000000001','KG','Kilogramo','kg','MASS'),
('21000000-0000-0000-0000-000000000002','T','Tonelada','t','MASS'),
('21000000-0000-0000-0000-000000000003','PZA','Pieza','pza','COUNT'),
('21000000-0000-0000-0000-000000000004','CAJA','Caja','caja','LOGISTIC'),
('21000000-0000-0000-0000-000000000005','L','Litro','L','VOLUME');

INSERT INTO catalog.product(id,sku,name,category_id,product_type,storage_unit_id,base_unit_id,min_stock,
 requires_lot,requires_heat_number,requires_expiry,requires_serial,technical_attributes) VALUES
('22000000-0000-0000-0000-000000000001','A36-PL-10','Plancha acero A36 10 mm','20000000-0000-0000-0000-000000000001','MATERIAL',
 '21000000-0000-0000-0000-000000000002','21000000-0000-0000-0000-000000000001',500,true,true,false,false,'{"grade":"A36","thickness_mm":10}'),
('22000000-0000-0000-0000-000000000002','ROD-6205','Rodamiento 6205','20000000-0000-0000-0000-000000000002','REPUESTO',
 '21000000-0000-0000-0000-000000000004','21000000-0000-0000-0000-000000000003',20,true,false,false,false,'{"designation":"6205"}'),
('22000000-0000-0000-0000-000000000003','LUB-H46','Aceite hidráulico ISO VG 46','20000000-0000-0000-0000-000000000003','INSUMO',
 '21000000-0000-0000-0000-000000000005','21000000-0000-0000-0000-000000000005',100,true,false,true,false,'{"viscosity":"ISO VG 46"}'),
('22000000-0000-0000-0000-000000000004','EXC-320','Excavadora 320 demo','20000000-0000-0000-0000-000000000004','MAQUINARIA',
 '21000000-0000-0000-0000-000000000003','21000000-0000-0000-0000-000000000003',0,false,false,false,true,'{"class":"excavator"}');

INSERT INTO catalog.unit_conversion(id,product_id,from_unit_id,to_unit_id,factor) VALUES
('23000000-0000-0000-0000-000000000001','22000000-0000-0000-0000-000000000001','21000000-0000-0000-0000-000000000002','21000000-0000-0000-0000-000000000001',1000),
('23000000-0000-0000-0000-000000000002','22000000-0000-0000-0000-000000000002','21000000-0000-0000-0000-000000000004','21000000-0000-0000-0000-000000000003',10);

-- Inventory local Catalog projection (normally populated by ProductCreated/Updated events).
INSERT INTO inventory.supplier_ref (supplier_id, code, tax_id, business_name, active, source_version) VALUES
('70000000-0000-0000-0000-000000000001','PRV-001','20123456789','Suministros Industriales Andinos S.A.C.',true,1)
ON CONFLICT DO NOTHING;

INSERT INTO inventory.product_ref(product_id,sku,product_type,storage_unit_code,base_unit_code,min_stock,
 requires_lot,requires_heat_number,requires_serial,requires_expiry,source_version) VALUES
('22000000-0000-0000-0000-000000000001','A36-PL-10','MATERIAL','T','KG',500,true,true,false,false,0),
('22000000-0000-0000-0000-000000000002','ROD-6205','REPUESTO','CAJA','PZA',20,true,false,false,false,0),
('22000000-0000-0000-0000-000000000003','LUB-H46','INSUMO','L','L',100,true,false,false,true,0),
('22000000-0000-0000-0000-000000000004','EXC-320','MAQUINARIA','PZA','PZA',0,false,false,true,false,0);

INSERT INTO inventory.product_unit_conversion_ref(product_id,from_unit_code,to_unit_code,factor) VALUES
('22000000-0000-0000-0000-000000000001','T','KG',1000),
('22000000-0000-0000-0000-000000000002','CAJA','PZA',10);

INSERT INTO inventory.location(id,code,name,location_type,parent_id) VALUES
('30000000-0000-0000-0000-000000000001','ALM-01','Almacén principal','ALMACEN',NULL),
('30000000-0000-0000-0000-000000000002','ZONA-A','Zona de materiales','ZONA','30000000-0000-0000-0000-000000000001'),
('30000000-0000-0000-0000-000000000003','POS-A01','Posición A01','POSICION','30000000-0000-0000-0000-000000000002'),
('30000000-0000-0000-0000-000000000004','PATIO-01','Patio de maquinaria','PATIO',NULL),
('30000000-0000-0000-0000-000000000005','POS-M01','Posición maquinaria M01','POSICION','30000000-0000-0000-0000-000000000004');

INSERT INTO inventory.lot(id,product_id,lot_number,heat_number,received_at,status) VALUES
('31000000-0000-0000-0000-000000000001','22000000-0000-0000-0000-000000000001','LOT-A36-001','COL-2026-001',CURRENT_DATE,'ACTIVE'),
('31000000-0000-0000-0000-000000000002','22000000-0000-0000-0000-000000000002','LOT-6205-001',NULL,CURRENT_DATE,'ACTIVE');

INSERT INTO inventory.asset(id,product_id,asset_code,serial_number,brand,model,operational_status) VALUES
('32000000-0000-0000-0000-000000000001','22000000-0000-0000-0000-000000000004','MAQ-0001','SER-DEMO-EXC-001','Demo','320','OPERATIVO');

INSERT INTO inventory.stock_balance(id,product_id,location_id,lot_id,asset_id,quantity,avg_cost_pen) VALUES
('33000000-0000-0000-0000-000000000001','22000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000003','31000000-0000-0000-0000-000000000001',NULL,2500,4.25),
('33000000-0000-0000-0000-000000000002','22000000-0000-0000-0000-000000000002','30000000-0000-0000-0000-000000000003','31000000-0000-0000-0000-000000000002',NULL,50,35.00),
('33000000-0000-0000-0000-000000000003','22000000-0000-0000-0000-000000000004','30000000-0000-0000-0000-000000000005',NULL,'32000000-0000-0000-0000-000000000001',1,450000);

-- Reporting read models (normally maintained by RabbitMQ consumers).
INSERT INTO analytics.product_projection(product_id,sku,name,category_code,category_name,product_type,base_unit_code,storage_unit_code,min_stock,active,source_version)
SELECT p.id,p.sku,p.name,c.code,c.name,p.product_type,ub.code,us.code,p.min_stock,p.active,p.version
FROM catalog.product p JOIN catalog.category c ON c.id=p.category_id
JOIN catalog.unit_measure ub ON ub.id=p.base_unit_id
JOIN catalog.unit_measure us ON us.id=p.storage_unit_id;

INSERT INTO analytics.inventory_projection(stock_balance_id,product_id,location_id,lot_id,asset_id,quantity,avg_cost_pen,min_stock)
SELECT s.id,s.product_id,s.location_id,s.lot_id,s.asset_id,s.quantity,s.avg_cost_pen,p.min_stock
FROM inventory.stock_balance s JOIN inventory.product_ref p ON p.product_id=s.product_id;
