"""
reportes/ventas_sucursal_comparativo/ventas_sucursal_comparativo_all.py
Gestiona el ciclo completo del reporte 1.2 — Ventas por sucursal comparativo.

NOTA: Este reporte no tiene tabla desnorm propia.
      Reutiliza comercialdesnormalized.ventas_consolidado como fuente.
      Asegurarse de que ventas_consolidado esté poblado antes de correr el fill.

Uso:
    python reportes/ventas_sucursal_comparativo/ventas_sucursal_comparativo_all.py
    python reportes/ventas_sucursal_comparativo/ventas_sucursal_comparativo_all.py --fill-only
    python reportes/ventas_sucursal_comparativo/ventas_sucursal_comparativo_all.py --drop
    python reportes/ventas_sucursal_comparativo/ventas_sucursal_comparativo_all.py --create
    python reportes/ventas_sucursal_comparativo/ventas_sucursal_comparativo_all.py --desde 2025-01-01 --hasta 2025-12-31
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

TABLAS_AGG = ["resumen_ventas_sucursal_mes"]
SQL_AGG    = os.path.join(_DIR, "create_resumen_ventas_sucursal_mes.sql")
FILL_AGG   = os.path.join(_DIR, "fill_resumen_ventas_sucursal_mes.py")


def do_drop():
    print(f"\nDrop en {os.getenv('DB_NAME_AGG')}")
    drop_tables(TABLAS_AGG, db_name=os.getenv("DB_NAME_AGG"))


def do_create():
    print(f"\nCreate en {os.getenv('DB_NAME_AGG')}")
    run_sql_file(SQL_AGG, db_name=os.getenv("DB_NAME_AGG"))


def do_fill(desde: str, hasta: str):
    def run(label, cmd):
        print(f"\n── {label}")
        r = subprocess.run(cmd, cwd=_ROOT)
        if r.returncode != 0:
            sys.exit(r.returncode)

    run("fill agg", [PYTHON, FILL_AGG, "--desde", desde, "--hasta", hasta])


def main():
    hoy = date.today()
    p = argparse.ArgumentParser(description="Ciclo completo reporte 1.2 — Ventas sucursal comparativo")
    p.add_argument("--fill-only", action="store_true", help="Solo recarga datos")
    p.add_argument("--drop",      action="store_true", help="Solo drop tabla agg")
    p.add_argument("--create",    action="store_true", help="Solo crear tabla agg")
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
