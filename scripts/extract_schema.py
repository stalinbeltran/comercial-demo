"""
scripts/extract_schema.py
Recorre los archivos .sql de reportes/, extrae los CREATE TABLE y:
  1. Guarda output/schema_creates.json  (reporte → tablas → CREATE SQL)
  2. Actualiza api/data/catalogo.json   (añade 'folder' y 'creates' a cada reporte implementado)

Las dos operaciones se coordinan en un solo script para que el catálogo
siempre refleje exactamente lo que hay en disco.

Uso:
    python scripts/extract_schema.py
    python scripts/extract_schema.py --dir reportes
"""

import argparse
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT         = Path(__file__).parent.parent
CATALOGO_JSON = ROOT / "api" / "data" / "catalogo.json"

sys.path.insert(0, str(ROOT))

from utils.schema_reader import extract_creates, save_creates


def _folder_from_endpoint(endpoint: str | None) -> str | None:
    """Deriva el nombre de la subcarpeta desde el endpoint.

    /reportes/ventas-consolidado  →  ventas_consolidado
    """
    if not endpoint:
        return None
    return endpoint.rstrip("/").split("/")[-1].replace("-", "_")


def _update_catalogo(creates_by_folder: dict, reportes_dir: Path) -> dict:
    """Lee catalogo.json, añade/actualiza 'folder' y 'creates' en cada reporte
    implementado, y devuelve el JSON modificado."""

    raw = json.loads(CATALOGO_JSON.read_text(encoding="utf-8"))

    for modulo in raw["modulos"]:
        for reporte in modulo["reportes"]:
            # Respetar folder ya definido manualmente; si no, derivar del endpoint
            folder_name = reporte.get("folder_name") or _folder_from_endpoint(
                reporte.get("endpoint")
            )
            if not folder_name:
                continue

            folder_path = reportes_dir / folder_name
            if not folder_path.is_dir():
                continue

            creates = creates_by_folder.get(folder_name, {})
            reporte["folder"]  = f"reportes/{folder_name}"
            reporte["creates"] = creates

    return raw


def main() -> None:
    p = argparse.ArgumentParser(
        description="Extrae CREATE TABLE de reportes/ y actualiza catalogo.json"
    )
    p.add_argument("--dir", default=str(ROOT / "reportes"),
                   help="Carpeta raíz de reportes (default: reportes/)")
    args = p.parse_args()

    reportes_dir = Path(args.dir)
    if not reportes_dir.is_dir():
        print(f"Error: no existe el directorio '{reportes_dir}'", file=sys.stderr)
        sys.exit(1)

    # ── 1. Extraer creates ────────────────────────────────────────────────────
    creates = extract_creates(reportes_dir)
    total_tablas = sum(len(t) for t in creates.values())

    print(f"Reportes encontrados : {len(creates)}")
    print(f"Tablas extraídas     : {total_tablas}")
    for folder, tablas in creates.items():
        print(f"  {folder}/")
        for tabla in tablas:
            print(f"    └─ {tabla}")

    schema_file = save_creates(reportes_dir)
    print(f"\n[1] Guardado: {schema_file.relative_to(ROOT)}")

    # ── 2. Actualizar catalogo.json ───────────────────────────────────────────
    updated = _update_catalogo(creates, reportes_dir)
    CATALOGO_JSON.write_text(
        json.dumps(updated, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[2] Actualizado: {CATALOGO_JSON.relative_to(ROOT)}")

    # Resumen de reportes actualizados en el catálogo
    actualizados = [
        f"{r['numero']} {r['nombre']}"
        for m in updated["modulos"]
        for r in m["reportes"]
        if "folder" in r
    ]
    print(f"\nReportes con folder/creates en catálogo ({len(actualizados)}):")
    for nombre in actualizados:
        print(f"  • {nombre}")


if __name__ == "__main__":
    main()
