"""
scripts/drop_all.py
Elimina todas las tablas creadas en las DBs desnormalizada y agregada.

Uso:
    python scripts/drop_all.py
"""

import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from dotenv import load_dotenv
from utils.db_setup import drop_tables

load_dotenv()

TABLAS = {
    os.getenv("DB_NAME_DESNORM"): ["linea_venta"],
    os.getenv("DB_NAME_AGG"):     ["resumen_ventas"],
}


def main():
    for db_name, tablas in TABLAS.items():
        print(f"\n{db_name}")
        drop_tables(tablas, db_name=db_name)

    print("\n✓ Drop completado")


if __name__ == "__main__":
    main()
