"""
scripts/extract_sql.py
Analiza un archivo Python y extrae todos los strings que parezcan queries SQL.

Uso:
    python scripts/extract_sql.py api/routes/ventas_consolidado.py
    python scripts/extract_sql.py api/routes/ventas_consolidado.py --format
    python scripts/extract_sql.py api/routes/ventas_consolidado.py --format --debug
"""

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.sql_extract import extract_sql_strings


def main() -> None:
    p = argparse.ArgumentParser(description="Extrae queries SQL de un archivo Python")
    p.add_argument("file", type=Path, help="Archivo .py a analizar")
    p.add_argument(
        "--format", action="store_true",
        help="Formatea cada query con sqlglot",
    )
    p.add_argument(
        "--debug", action="store_true",
        help="Muestra también errores de sintaxis detectados por sqlglot (requiere --format)",
    )
    args = p.parse_args()

    if not args.file.exists():
        print(f"Archivo no encontrado: {args.file}", file=sys.stderr)
        sys.exit(1)

    source = args.file.read_text(encoding="utf-8")
    queries = extract_sql_strings(source)

    if not queries:
        print("No se encontraron queries SQL en el archivo.")
        return

    print(f"Archivo : {args.file}")
    print(f"Queries : {len(queries)} encontrado(s)")

    if args.format:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from utils.sql_debug import debug_sql

    for i, q in enumerate(queries, 1):
        var = f"  variable : {q['variable']}" if q["variable"] else ""
        print()
        print(f"{'─' * 60}")
        print(f"  #{i}  línea {q['line']}" + (f"  |  {q['variable']}" if q["variable"] else ""))
        print(f"{'─' * 60}")

        if args.format:
            result = debug_sql(q["sql"])
            if args.debug:
                status = "OK" if result.is_valid else "INVALIDO"
                print(f"  [{status}]", end="")
                if result.errors:
                    for e in result.errors:
                        print(f"\n  ! {e}", end="")
                print()
            sql_to_show = result.formatted or q["sql"]
        else:
            sql_to_show = q["sql"]

        for line in sql_to_show.strip().splitlines():
            print(f"  {line}")

    print(f"\n{'─' * 60}")
    print(f"Total: {len(queries)} query(s) extraído(s) de {args.file.name}")


if __name__ == "__main__":
    main()
