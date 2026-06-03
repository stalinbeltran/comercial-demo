"""
scripts/create_all.py
Crea todas las tablas en las DBs desnormalizada y agregada.

Uso:
    # Solo crear (falla si las tablas ya existen)
    python scripts/create_all.py

    # Borrar primero y luego crear
    python scripts/create_all.py --recreate
"""

import os
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from utils.db_setup import run_sql_file, drop_tables, tables_from_sql_file

load_dotenv()

SCRIPTS = [
    ("scripts/create_reporte_ventas.sql", os.getenv("DB_NAME_DESNORM")),
    ("scripts/create_resumen_ventas.sql", os.getenv("DB_NAME_AGG")),
]


def main():
    p = argparse.ArgumentParser(description="Crea todas las tablas del proyecto")
    p.add_argument("--recreate", action="store_true",
                   help="Elimina las tablas existentes antes de crearlas")
    args = p.parse_args()

    for sql_file, db_name in SCRIPTS:
        print(f"\n{'─' * 50}")
        if args.recreate:
            tablas = tables_from_sql_file(sql_file)
            print(f"Dropping {tablas} en '{db_name}'...")
            drop_tables(tablas, db_name=db_name)
            print()
        run_sql_file(sql_file, db_name=db_name)

    print("\n✓ Create completado")


if __name__ == "__main__":
    main()
