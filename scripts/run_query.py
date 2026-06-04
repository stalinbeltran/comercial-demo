"""
scripts/run_query.py  —  CLI fino sobre utils.sql_runner.run_query

Uso:
    python scripts/run_query.py --query "SELECT * FROM cliente LIMIT 5"
    python scripts/run_query.py --query "SELECT * FROM cliente WHERE id = %s" --params 3
    python scripts/run_query.py --file mi_query.sql --params "2025-01-01" "2025-12-31"
    python scripts/run_query.py --from-py api/routes/ventas_consolidado.py --db agg --params "2024-06-04" "2026-06-04" "null" "null"
    python scripts/run_query.py --query "SELECT ..." --db agg --format json
    python scripts/run_query.py --query "SELECT ..." --format csv
    python scripts/run_query.py --query "SELECT ..." --debug
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import mysql.connector

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from utils.sql_runner import DB_MAP, run_query
from utils.sql_extract import extract_and_run, extract_sql_strings


def _print_table(rows: list[dict], columns: list[str]) -> None:
    if not rows:
        print("(sin resultados)")
        return
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row[col]) if row[col] is not None else "NULL"))
    sep    = "+" + "+".join("-" * (w + 2) for w in widths.values()) + "+"
    header = "|" + "|".join(f" {col:<{widths[col]}} " for col in columns) + "|"
    print(sep)
    print(header)
    print(sep)
    for row in rows:
        line = "|" + "|".join(
            f" {str(row[col]) if row[col] is not None else 'NULL':<{widths[col]}} "
            for col in columns
        ) + "|"
        print(line)
    print(sep)


def _print_json(rows: list[dict]) -> None:
    print(json.dumps(rows, indent=2, default=str, ensure_ascii=False))


def _print_csv(rows: list[dict], columns: list[str]) -> None:
    writer = csv.DictWriter(sys.stdout, fieldnames=columns)
    writer.writeheader()
    for row in rows:
        writer.writerow({k: ("" if v is None else v) for k, v in row.items()})


def _display(rows: list[dict], fmt: str, limit: int | None) -> None:
    if rows and "affected_rows" in rows[0]:
        print(f"Query ejecutado. Filas afectadas: {rows[0]['affected_rows']}")
        return
    columns = list(rows[0].keys()) if rows else []
    total = len(rows)
    if limit:
        rows = rows[:limit]
    if fmt == "table":
        _print_table(rows, columns)
        print(f"\n{len(rows)} fila(s)", end="")
        if limit and total > limit:
            print(f" de {total} (limitado a {limit})", end="")
        print()
    elif fmt == "json":
        _print_json(rows)
    elif fmt == "csv":
        _print_csv(rows, columns)


def _parse_params(raw: list[str]) -> tuple:
    return tuple(None if p.lower() == "null" else p for p in raw)


def main() -> None:
    p = argparse.ArgumentParser(description="Ejecuta un query SQL contra las bases del proyecto")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--query",   "-q", help="SQL inline")
    src.add_argument("--file",    "-f", type=Path, help="Archivo .sql con el query")
    src.add_argument("--from-py", dest="from_py", type=Path,
                     help="Archivo .py del que se extrae y ejecuta el query")

    p.add_argument("--index",  type=int, default=0,
                   help="Índice del query cuando --from-py encuentra varios (default: 0)")
    p.add_argument("--params", "-p", nargs="*", default=[],
                   help="Parámetros para los %%s del query. Usar 'null' para NULL.")
    p.add_argument("--db", default="main", choices=list(DB_MAP),
                   help="Base de datos: main | agg | desnorm  (default: main)")
    p.add_argument("--format", dest="fmt", default="table",
                   choices=["table", "json", "csv"], help="Formato de salida (default: table)")
    p.add_argument("--limit", "-l", type=int, default=None,
                   help="Limita filas mostradas")
    p.add_argument("--debug", action="store_true",
                   help="Muestra el query formateado con sqlglot antes de ejecutar")
    args = p.parse_args()

    params = _parse_params(args.params)

    try:
        if args.from_py:
            queries = extract_sql_strings(args.from_py.read_text(encoding="utf-8"))
            if not queries:
                print(f"No se encontraron queries en {args.from_py}", file=sys.stderr)
                sys.exit(1)
            q = queries[args.index]
            print(f"Archivo : {args.from_py}")
            print(f"Query   : #{args.index + 1}  línea {q['line']}" +
                  (f"  |  {q['variable']}" if q["variable"] else ""))
            print()
            rows = extract_and_run(args.from_py, args.db, params, args.index)
        else:
            sql = args.query if args.query else args.file.read_text(encoding="utf-8")
            if args.debug:
                from utils.sql_debug import debug_sql
                r = debug_sql(sql)
                print("─" * 60)
                print(r)
                print("─" * 60 + "\n")
            rows = run_query(sql, args.db, params)

    except (FileNotFoundError, IndexError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except mysql.connector.Error as e:
        print(f"Error MySQL [{e.errno}]: {e.msg}", file=sys.stderr)
        sys.exit(1)

    _display(rows, args.fmt, args.limit)


if __name__ == "__main__":
    main()
