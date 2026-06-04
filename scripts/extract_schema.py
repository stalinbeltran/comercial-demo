"""
scripts/extract_schema.py
Recorre los archivos .sql de la carpeta reportes/, extrae los CREATE TABLE
y guarda el resultado en output/schema_creates.json.

Uso:
    python scripts/extract_schema.py
    python scripts/extract_schema.py --dir reportes
"""

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from utils.schema_reader import extract_creates, save_creates


def main() -> None:
    p = argparse.ArgumentParser(description="Extrae CREATE TABLE de los reportes y guarda en JSON")
    p.add_argument("--dir", default=str(ROOT / "reportes"),
                   help="Carpeta raíz de reportes (default: reportes/)")
    args = p.parse_args()

    reportes_dir = Path(args.dir)
    if not reportes_dir.is_dir():
        print(f"Error: no existe el directorio '{reportes_dir}'", file=sys.stderr)
        sys.exit(1)

    data = extract_creates(reportes_dir)

    total_tablas = sum(len(t) for t in data.values())
    print(f"Reportes encontrados : {len(data)}")
    print(f"Tablas extraídas     : {total_tablas}")
    print()

    for reporte, tablas in data.items():
        print(f"  {reporte}/")
        for tabla in tablas:
            print(f"    └─ {tabla}")

    output = save_creates(reportes_dir)
    print(f"\nGuardado en: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
