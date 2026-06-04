"""
reportes/ventas_por_categoria/ventas_por_categoria_all.py
Gestiona el ciclo completo del reporte 1.3 — Ventas por producto / categoría.

Uso:
    python reportes/ventas_por_categoria/ventas_por_categoria_all.py
    python reportes/ventas_por_categoria/ventas_por_categoria_all.py --fill-only
    python reportes/ventas_por_categoria/ventas_por_categoria_all.py --drop
    python reportes/ventas_por_categoria/ventas_por_categoria_all.py --create
    python reportes/ventas_por_categoria/ventas_por_categoria_all.py --desde 2025-01-01 --hasta 2025-12-31
"""

import os
import sys
import argparse
import subprocess
from datetime import date

sys.stdout.reconfigure(encoding="utf-8")

_DIR  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_DIR))
sys.path.insert(0, _ROOT)

from dotenv import load_dotenv
from utils.db_setup import drop_tables, run_sql_file

load_dotenv(os.path.join(_ROOT, ".env"))

PYTHON = sys.executable

TABLAS_DESNORM = ["linea_venta"]
TABLAS_AGG     = ["resumen_ventas"]

SQL_DESNORM = os.path.join(_DIR, "create_linea_venta.sql")
SQL_AGG     = os.path.join(_DIR, "create_resumen_ventas.sql")

FILL_DESNORM = os.path.join(_DIR, "fill_linea_venta.py")
FILL_AGG     = os.path.join(_DIR, "fill_resumen_ventas.py")


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
        r = subprocess.run(cmd, cwd=_ROOT)
        if r.returncode != 0:
            sys.exit(r.returncode)

    run("fill desnorm", [PYTHON, FILL_DESNORM, "--full"])
    run("fill agg",     [PYTHON, FILL_AGG, "--desde", desde, "--hasta", hasta])


def main():
    hoy = date.today()
    p = argparse.ArgumentParser(description="Ciclo completo reporte 1.3 — Ventas por categoria")
    p.add_argument("--fill-only", action="store_true", help="Solo recarga datos")
    p.add_argument("--drop",      action="store_true", help="Solo drop tablas")
    p.add_argument("--create",    action="store_true", help="Solo crear tablas")
    p.add_argument("--desde", default=(hoy.replace(year=hoy.year - 2)).isoformat(), metavar="YYYY-MM-DD")
    p.add_argument("--hasta", default=hoy.isoformat(), metavar="YYYY-MM-DD")
    args = p.parse_args()

    if args.drop:
        do_drop()
    elif args.create:
        do_create()
    elif args.fill_only:
        do_fill(args.desde, args.hasta)
    else:
        do_drop()
        do_create()
        do_fill(args.desde, args.hasta)

    print("\nCompletado")


if __name__ == "__main__":
    main()
