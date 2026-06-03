"""
scripts/ventas_consolidado_all.py
Gestiona el ciclo completo del reporte 1.1 — Resumen de ventas consolidado.

Uso:
    python scripts/ventas_consolidado_all.py                # solo fill
    python scripts/ventas_consolidado_all.py --recreate     # drop + create + fill
    python scripts/ventas_consolidado_all.py --drop         # solo drop tablas
    python scripts/ventas_consolidado_all.py --create       # solo crear tablas
    python scripts/ventas_consolidado_all.py --desde 2025-01-01 --hasta 2025-12-31
"""

import os
import sys
import argparse
import subprocess
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from utils.db_setup import drop_tables, run_sql_file

load_dotenv()

PYTHON = sys.executable
ROOT   = os.path.dirname(os.path.dirname(__file__))

TABLAS_DESNORM = ["ventas_consolidado"]
TABLAS_AGG     = ["resumen_ventas_consolidado"]

SQL_DESNORM    = "scripts/create_ventas_consolidado.sql"
SQL_AGG        = "scripts/create_resumen_ventas_consolidado.sql"

FILL_DESNORM   = ["scripts/fill_ventas_consolidado.py", "--full"]


def do_drop():
    print(f"\nDrop en {os.getenv('DB_NAME_DESNORM')}")
    drop_tables(TABLAS_DESNORM, db_name=os.getenv("DB_NAME_DESNORM"))
    print(f"Drop en {os.getenv('DB_NAME_AGG')}")
    drop_tables(TABLAS_AGG, db_name=os.getenv("DB_NAME_AGG"))


def do_create():
    print(f"\nCreate en {os.getenv('DB_NAME_DESNORM')}")
    run_sql_file(SQL_DESNORM, db_name=os.getenv("DB_NAME_DESNORM"))
    print(f"\nCreate en {os.getenv('DB_NAME_AGG')}")
    run_sql_file(SQL_AGG, db_name=os.getenv("DB_NAME_AGG"))


def do_fill(desde: str, hasta: str):
    def run(label, cmd):
        print(f"\n── {label}")
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            sys.exit(r.returncode)

    run("fill desnorm", [PYTHON] + FILL_DESNORM)
    run("fill agg",     [PYTHON, "scripts/fill_resumen_ventas_consolidado.py",
                         "--desde", desde, "--hasta", hasta])


def main():
    hoy = date.today()
    p = argparse.ArgumentParser(description="Ciclo completo reporte 1.1 — Ventas consolidado")
    p.add_argument("--recreate", action="store_true", help="Drop + create + fill")
    p.add_argument("--drop",     action="store_true", help="Solo drop tablas")
    p.add_argument("--create",   action="store_true", help="Solo crear tablas")
    p.add_argument("--desde", default=(hoy.replace(year=hoy.year - 2)).isoformat(), metavar="YYYY-MM-DD")
    p.add_argument("--hasta", default=hoy.isoformat(), metavar="YYYY-MM-DD")
    args = p.parse_args()

    if args.drop:
        do_drop()
    elif args.create:
        do_create()
    elif args.recreate:
        do_drop()
        do_create()
        do_fill(args.desde, args.hasta)
    else:
        do_fill(args.desde, args.hasta)

    print("\n✓ Completado")


if __name__ == "__main__":
    main()
