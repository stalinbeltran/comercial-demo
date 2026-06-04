"""
scripts/run_query.py
Ejecuta cualquier query SQL contra las bases del proyecto y muestra los resultados.

Uso:
    python scripts/run_query.py --query "SELECT * FROM cliente LIMIT 5"
    python scripts/run_query.py --query "SELECT * FROM cliente WHERE id = %s" --params 3
    python scripts/run_query.py --file mi_query.sql --params "2025-01-01" "2025-12-31"
    python scripts/run_query.py --from-py api/routes/ventas_consolidado.py --db agg
    python scripts/run_query.py --from-py api/routes/algún_reporte.py --index 1 --params "2025-01-01"
    python scripts/run_query.py --query "SELECT ..." --db agg
    python scripts/run_query.py --query "SELECT ..." --format json
    python scripts/run_query.py --query "SELECT ..." --format csv
    python scripts/run_query.py --query "SELECT ..." --debug
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

DB_MAP = {
    "main":   os.getenv("DB_NAME"),
    "agg":    os.getenv("DB_NAME_AGG"),
    "desnorm": os.getenv("DB_NAME_DESNORM"),
}

_CONN_BASE = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    charset="utf8mb4",
)


def _get_conn(db_key: str):
    db_name = DB_MAP.get(db_key)
    if not db_name:
        raise ValueError(f"Base de datos desconocida: '{db_key}'. Opciones: {list(DB_MAP)}")
    return mysql.connector.connect(database=db_name, **_CONN_BASE)


def _print_table(rows: list[dict], columns: list[str]) -> None:
    if not rows:
        print("(sin resultados)")
        return
    widths = {col: len(col) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(str(row[col]) if row[col] is not None else "NULL"))
    sep = "+" + "+".join("-" * (w + 2) for w in widths.values()) + "+"
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


def main() -> None:
    p = argparse.ArgumentParser(description="Ejecuta un query SQL contra las bases del proyecto")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--query", "-q", help="SQL inline")
    src.add_argument("--file",  "-f", type=Path, help="Archivo .sql con el query")
    src.add_argument("--from-py", dest="from_py", type=Path,
                     help="Archivo .py del que se extrae y ejecuta el query")

    p.add_argument(
        "--index", type=int, default=0,
        help="Índice del query a usar cuando --from-py encuentra varios (default: 0)",
    )
    p.add_argument(
        "--params", "-p", nargs="*", default=[],
        help="Parámetros posicionales para los %%s del query (en orden)",
    )
    p.add_argument(
        "--db", default="main",
        choices=list(DB_MAP),
        help="Base de datos: main (comercial) | agg (aggregated) | desnorm (desnormalized). Default: main",
    )
    p.add_argument(
        "--format", dest="fmt", default="table",
        choices=["table", "json", "csv"],
        help="Formato de salida. Default: table",
    )
    p.add_argument(
        "--limit", "-l", type=int, default=None,
        help="Limita la cantidad de filas mostradas",
    )
    p.add_argument(
        "--debug", action="store_true",
        help="Muestra el query formateado con sqlglot antes de ejecutar",
    )
    args = p.parse_args()

    # ── Rama --from-py: extrae query del archivo Python y ejecuta ─────────────
    if args.from_py:
        try:
            sys.path.insert(0, str(ROOT))
            from utils.sql_extract import extract_and_run, extract_sql_strings
            source = args.from_py.read_text(encoding="utf-8")
            queries = extract_sql_strings(source)
            if not queries:
                print(f"No se encontraron queries SQL en {args.from_py}", file=sys.stderr)
                sys.exit(1)
            q = queries[args.index]
            print(f"Archivo : {args.from_py}")
            print(f"Query   : #{args.index + 1}  línea {q['line']}" +
                  (f"  |  {q['variable']}" if q["variable"] else ""))
            print()
            params_clean = tuple(None if p.lower() == "null" else p for p in args.params)
            rows = extract_and_run(args.from_py, args.db, params_clean, args.index)
        except (FileNotFoundError, IndexError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except mysql.connector.Error as e:
            print(f"Error MySQL [{e.errno}]: {e.msg}", file=sys.stderr)
            sys.exit(1)

        if rows and "affected_rows" in rows[0]:
            print(f"Query ejecutado. Filas afectadas: {rows[0]['affected_rows']}")
            return

        columns = list(rows[0].keys()) if rows else []
        total = len(rows)
        if args.limit:
            rows = rows[: args.limit]
        if args.fmt == "table":
            _print_table(rows, columns)
            print(f"\n{len(rows)} fila(s)", end="")
            if args.limit and total > args.limit:
                print(f" de {total} (limitado a {args.limit})", end="")
            print()
        elif args.fmt == "json":
            _print_json(rows)
        elif args.fmt == "csv":
            _print_csv(rows, columns)
        return

    sql = args.query if args.query else args.file.read_text(encoding="utf-8")

    if args.debug:
        try:
            sys.path.insert(0, str(ROOT))
            from utils.sql_debug import debug_sql
            result = debug_sql(sql)
            print("─" * 60)
            print(result)
            print("─" * 60)
            print()
        except Exception as e:
            print(f"[debug] No se pudo analizar el SQL: {e}\n")

    params = tuple(None if p.lower() == "null" else p for p in args.params)

    try:
        conn = _get_conn(args.db)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or None)

        if cur.description is None:
            print(f"Query ejecutado. Filas afectadas: {cur.rowcount}")
            conn.commit()
            return

        rows = cur.fetchall()
        columns = [d[0] for d in cur.description]
        cur.close()
    except mysql.connector.Error as e:
        print(f"Error MySQL [{e.errno}]: {e.msg}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

    total = len(rows)
    if args.limit:
        rows = rows[: args.limit]

    rows = [{k: v for k, v in row.items()} for row in rows]

    if args.fmt == "table":
        _print_table(rows, columns)
        print(f"\n{len(rows)} fila(s)", end="")
        if args.limit and total > args.limit:
            print(f" de {total} (limitado a {args.limit})", end="")
        print()
    elif args.fmt == "json":
        _print_json(rows)
    elif args.fmt == "csv":
        _print_csv(rows, columns)


if __name__ == "__main__":
    main()
