#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, sys, yaml

ROOT=Path(__file__).resolve().parents[1]

errors=[]
notes=[]

# 1) Canonical diagram hashes
baseline=json.loads((ROOT/"canonical_hashes_v1.2.json").read_text(encoding="utf-8"))
current={}
for p in sorted((ROOT/"diagramas").rglob("*.puml")):
    rel=p.relative_to(ROOT/"diagramas").as_posix()
    current[rel]=hashlib.sha256(p.read_bytes()).hexdigest()
if current != baseline["sha256"]:
    missing=set(baseline["sha256"])-set(current)
    extra=set(current)-set(baseline["sha256"])
    changed=[k for k in set(current)&set(baseline["sha256"]) if current[k]!=baseline["sha256"][k]]
    errors.append(f"Diagramas canónicos modificados: missing={sorted(missing)} extra={sorted(extra)} changed={sorted(changed)}")
else:
    notes.append(f"61 diagramas canónicos conservan SHA-256 de la base v1.2.")

# 2) Derived parity
import subprocess
r=subprocess.run([sys.executable, str(ROOT/"tools"/"validar_fuentes_y_derivados.py")],capture_output=True,text=True)
if r.returncode:
    errors.append("Paridad derivados: "+r.stdout+r.stderr)
else:
    notes.append(r.stdout.strip())

# 3) SQL table inventory
sql=(ROOT/"database"/"physical_model.sql").read_text(encoding="utf-8")
tables=re.findall(r'(?im)^\s*CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-z_]+)\.([a-z_][a-z0-9_]*)',sql)
dist={}
for schema,table in tables:
    dist[schema]=dist.get(schema,0)+1
expected={"iam":7,"catalog":6,"inventory":15,"evidence":2,"audit":3,"analytics":7}
if len(tables)!=40 or dist!=expected:
    errors.append(f"SQL tablas: total={len(tables)} dist={dist}, esperado 40 {expected}")
else:
    notes.append("SQL: 40 tablas = IAM 7 / Catalog 6 / Inventory 15 / Evidence 2 / Audit 3 / Analytics 7.")

# 4) Cross-schema FK
# Track current table through CREATE TABLE block and inspect REFERENCES.
cross=[]
for m in re.finditer(r'(?is)CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-z_]+)\.([a-z_][a-z0-9_]*)\s*\((.*?)\);',sql):
    src_schema,src_table,body=m.group(1),m.group(2),m.group(3)
    for rs,rt in re.findall(r'(?i)REFERENCES\s+([a-z_]+)\.([a-z_][a-z0-9_]*)',body):
        if rs!=src_schema:
            cross.append((f"{src_schema}.{src_table}",f"{rs}.{rt}"))
if cross:
    errors.append(f"FK cross-schema detectadas: {cross}")
else:
    notes.append("FK cross-schema: 0.")

# 5) Supplier structures
need_sql=[
    "catalog.supplier",
    "inventory.supplier_ref",
    "supplier_name_snapshot",
    "supplier_tax_id_snapshot",
]
for token in need_sql:
    if token not in sql:
        errors.append(f"SQL no contiene {token}")
if all(t in sql for t in need_sql):
    notes.append("Proveedor: catalog.supplier + inventory.supplier_ref + snapshots presentes.")

# 6) Dictionary table names
dictionary=(ROOT/"database"/"dictionary.md").read_text(encoding="utf-8")
sql_names={f"{s}.{t}" for s,t in tables}
dict_names=set(re.findall(r'(?m)^#{2,3}\s+`?([a-z_]+\.[a-z_][a-z0-9_]*)`?\s*$',dictionary))
# Fall back to inline table headings if format differs
if not dict_names:
    dict_names=set(re.findall(r'`([a-z_]+\.[a-z_][a-z0-9_]*)`',dictionary))
missing_dict=sorted(sql_names-dict_names)
if missing_dict:
    errors.append(f"Diccionario no menciona tablas SQL: {missing_dict}")
else:
    notes.append("Diccionario: menciona las 40 tablas SQL.")

# 7) OpenAPI
api_files=sorted((ROOT/"api").glob("*.yaml"))
if len(api_files)!=6:
    errors.append(f"OpenAPI: {len(api_files)} archivos, esperado 6")
apis={}
for p in api_files:
    try:
        d=yaml.safe_load(p.read_text(encoding="utf-8"))
        apis[p.name]=d
    except Exception as e:
        errors.append(f"{p.name}: YAML inválido {e}")
if "catalog-openapi.yaml" in apis:
    paths=apis["catalog-openapi.yaml"].get("paths",{})
    for route in ["/suppliers","/suppliers/{id}"]:
        if route not in paths:
            errors.append(f"Catalog OpenAPI sin {route}")
if "inventory-openapi.yaml" in apis:
    txt=(ROOT/"api"/"inventory-openapi.yaml").read_text(encoding="utf-8")
    if "supplierId" not in txt and "supplier_id" not in txt:
        errors.append("Inventory OpenAPI no expone supplierId/supplier_id")
if not any(e.startswith("OpenAPI") or "openapi" in e.lower() for e in errors):
    notes.append("OpenAPI: 6 YAML válidos; Catalog/Inventory incluyen Proveedores.")

# 8) Traceability
checks={
    "trazabilidad/requirements.md":["RF-35","US-35","CUS-31"],
    "trazabilidad/traceability-matrices.md":["RF-35","US-35","CUS-31"],
    "especificaciones/CUS_Detallados.md":["CUS-31","Gestionar proveedores"],
    "especificaciones/CUN_Detallados.md":["CUN-01","Proveedor externo","CUS-31"],
}
for rel,tokens in checks.items():
    txt=(ROOT/rel).read_text(encoding="utf-8")
    miss=[x for x in tokens if x not in txt]
    if miss:
        errors.append(f"{rel}: faltan {miss}")
if not any("trazabilidad/" in e or "especificaciones/" in e for e in errors):
    notes.append("Trazabilidad: RF-35 / US-35 / CUS-31 / CUN-01 sincronizados.")

# 9) Six-service guard
manual=(ROOT/"Manual_Tecnico_SIGA_Final.md").read_text(encoding="utf-8")
if "seis microservicios" not in manual.lower() and "seis servicios" not in manual.lower():
    errors.append("Manual Técnico no conserva decisión de seis servicios")
if re.search(r'(?i)supplier-service|proveedor-service|séptimo microservicio',manual):
    errors.append("Se detectó indicio de microservicio de proveedor no aprobado")
else:
    notes.append("Arquitectura: se conservan 6 servicios; no existe Supplier Service.")

# 10) Agent governance
for rel in [
    "AGENTS.md",
    "adr/ADR-019_Fuentes_PlantUML_Canonicas_y_Derivados_Visuales.md",
    "diagramas/README_CANONICO.md",
    "diagramas_render/README.md",
]:
    if not (ROOT/rel).exists():
        errors.append(f"Falta gobierno: {rel}")
if not any("Falta gobierno" in e for e in errors):
    notes.append("Gobierno IA/render: AGENTS.md + ADR-019 + README canónico/render presentes.")

print("VALIDACIÓN INTERNA SIGA v1.2")
print("="*52)
for n in notes:
    print("[OK]",n)
if errors:
    for e in errors:
        print("[ERROR]",e)
    sys.exit(1)
print("[OK] VALIDACIÓN COMPLETA")
