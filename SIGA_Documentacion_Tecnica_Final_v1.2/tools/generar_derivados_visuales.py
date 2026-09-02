#!/usr/bin/env python3
"""
Genera diagramas_render/ desde diagramas/ sin modificar las fuentes canónicas.

Regla:
- El contenido canónico se copia íntegro.
- Se agrega metadata de derivación.
- UML_10 y UML_11 reciben un perfil visual basado en la familia UML v1.1.
- No se agregan entidades, relaciones, CUS, RF, HU, endpoints ni eventos.
"""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "diagramas"
RENDER = ROOT / "diagramas_render"

META_BEGIN = "' @DERIVADO_VISUAL_META_BEGIN"
META_END = "' @DERIVADO_VISUAL_META_END"
PROFILE_BEGIN = "' @DERIVADO_VISUAL_PROFILE_BEGIN"
PROFILE_END = "' @DERIVADO_VISUAL_PROFILE_END"

UML_USECASE_PROFILE = """\
' @DERIVADO_VISUAL_PROFILE_BEGIN
' Perfil visual heredado de convenciones UML v1.1.
skinparam shadowing true
skinparam roundcorner 24
skinparam defaultFontName "Segoe UI", Helvetica, Arial, sans-serif
skinparam defaultFontSize 13
skinparam BackgroundColor #F8F9FA
skinparam ArrowColor #2C3E50
skinparam ArrowThickness 1.5
skinparam actor {
  BackgroundColor #FDEDEC
  BorderColor #E74C3C
  FontColor #922B21
}
skinparam usecase {
  BackgroundColor #FFFFFF
  BorderColor #1976D2
  FontColor #0D47A1
  BorderThickness 1.5
}
skinparam rectangle {
  BackgroundColor #FAFAFC
  BorderColor #546E7A
  FontColor #263238
  BorderThickness 1.5
}
skinparam note {
  BackgroundColor #FFF9C4
  BorderColor #FBC02D
  FontColor #3E2723
}
' @DERIVADO_VISUAL_PROFILE_END
"""

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def relative_canonical_hint(rel: Path) -> str:
    return f"diagramas/{rel.as_posix()}"

def make_derived(rel: Path, src: str) -> str:
    lines = src.splitlines()
    if not lines or not lines[0].strip().startswith("@startuml"):
        raise ValueError(f"{rel}: no comienza con @startuml")
    meta = [
        META_BEGIN,
        "' SIGA v1.2 — DERIVADO VISUAL / RENDER ONLY / NO CANÓNICO",
        f"' Fuente canónica: {relative_canonical_hint(rel)}",
        "' Uso: informe, Word, sustentación y exportación PNG/SVG.",
        "' Prohibido usar como fuente de implementación, requisitos o contexto de agentes/IA.",
        "' Generado por: tools/generar_derivados_visuales.py",
        META_END,
    ]
    out_lines = [lines[0], *meta, *lines[1:]]

    # Los dos diagramas nuevos no tenían equivalente v1.1. Se añade únicamente
    # una capa de skinparam coherente con la familia UML ya optimizada en v1.1.
    if rel.as_posix() in {
        "uml/UML_10_Casos_Uso_Negocio_Proveedores.puml",
        "uml/UML_11_Casos_Uso_Sistema_Proveedores.puml",
    }:
        # Insertar después de packageStyle, o después de la configuración inicial.
        insert_at = 1
        for i, line in enumerate(out_lines):
            if "skinparam packageStyle rectangle" in line:
                insert_at = i + 1
                break
        profile_lines = UML_USECASE_PROFILE.rstrip("\n").splitlines()
        out_lines[insert_at:insert_at] = profile_lines

    return "\n".join(out_lines) + ("\n" if src.endswith("\n") else "")

def main():
    RENDER.mkdir(parents=True, exist_ok=True)
    # Conservar README.
    for old in list(RENDER.rglob("*.puml")):
        old.unlink()

    manifest = []
    for src_path in sorted(CANON.rglob("*.puml")):
        rel = src_path.relative_to(CANON)
        dst = RENDER / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        src_text = src_path.read_text(encoding="utf-8")
        derived = make_derived(rel, src_text)
        dst.write_text(derived, encoding="utf-8")
        manifest.append({
            "canonical": f"diagramas/{rel.as_posix()}",
            "derived": f"diagramas_render/{rel.as_posix()}",
            "canonical_sha256": sha256_bytes(src_path.read_bytes()),
            "derived_sha256": sha256_bytes(dst.read_bytes()),
            "visual_source": "v1.1 same-path style" if rel.as_posix() not in {
                "uml/UML_10_Casos_Uso_Negocio_Proveedores.puml",
                "uml/UML_11_Casos_Uso_Sistema_Proveedores.puml",
            } else "v1.1 UML family profile",
            "canonical": True,
            "derived_render_only": True
        })

    (ROOT / "manifest_diagramas_v1.2.json").write_text(
        json.dumps({
            "version": "1.2",
            "canonical_root": "diagramas/",
            "derived_root": "diagramas_render/",
            "policy": "ADR-019",
            "count": len(manifest),
            "items": manifest,
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Generados {len(manifest)} derivados visuales.")

if __name__ == "__main__":
    main()
