#!/usr/bin/env python3
"""
Valida que diagramas_render/ sea una derivación visual, no una segunda fuente funcional.
"""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "diagramas"
RENDER = ROOT / "diagramas_render"

META_BEGIN = "' @DERIVADO_VISUAL_META_BEGIN"
META_END = "' @DERIVADO_VISUAL_META_END"
PROFILE_BEGIN = "' @DERIVADO_VISUAL_PROFILE_BEGIN"
PROFILE_END = "' @DERIVADO_VISUAL_PROFILE_END"

def strip_generated_blocks(text: str) -> str:
    lines = text.splitlines()
    result = []
    skipping = None
    for line in lines:
        if line == META_BEGIN:
            skipping = META_END
            continue
        if line == PROFILE_BEGIN:
            skipping = PROFILE_END
            continue
        if skipping:
            if line == skipping:
                skipping = None
            continue
        result.append(line)
    return "\n".join(result) + ("\n" if text.endswith("\n") else "")

def check_puml_structure(path: Path):
    txt = path.read_text(encoding="utf-8")
    errors = []
    if len(re.findall(r"(?m)^\s*@startuml(?:\s|$)", txt)) != 1:
        errors.append(f"{path}: @startuml != 1")
    if len(re.findall(r"(?m)^\s*@enduml\s*$", txt)) != 1:
        errors.append(f"{path}: @enduml != 1")
    if "!includeurl" in txt.lower():
        errors.append(f"{path}: include remoto no permitido")
    if not txt.rstrip().endswith("@enduml"):
        errors.append(f"{path}: no termina en @enduml")
    return errors

def main():
    errors = []
    canon = sorted(p.relative_to(CANON) for p in CANON.rglob("*.puml"))
    render = sorted(p.relative_to(RENDER) for p in RENDER.rglob("*.puml"))
    if canon != render:
        errors.append(f"Conjunto de archivos distinto: canonical={len(canon)} derived={len(render)}")

    for rel in canon:
        cp = CANON / rel
        rp = RENDER / rel
        errors.extend(check_puml_structure(cp))
        if not rp.exists():
            continue
        errors.extend(check_puml_structure(rp))
        raw = rp.read_text(encoding="utf-8")
        if META_BEGIN not in raw or META_END not in raw:
            errors.append(f"{rel}: falta marca DERIVADO VISUAL")
        normalized = strip_generated_blocks(raw)
        original = cp.read_text(encoding="utf-8")
        if normalized != original:
            errors.append(f"{rel}: diferencia semántica/textual fuera de bloques visuales")

    if errors:
        print("FAIL")
        for e in errors:
            print("-", e)
        sys.exit(1)
    print(f"OK: {len(canon)} diagramas canónicos y {len(render)} derivados; paridad exacta tras retirar bloques visuales.")

if __name__ == "__main__":
    main()
