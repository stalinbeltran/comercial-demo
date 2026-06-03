"""
utils/db_setup.py
Utilidad para ejecutar scripts SQL (DDL) contra una base de datos específica.

Uso como módulo:
    from utils.db_setup import run_sql_file, run_sql

    run_sql_file("scripts/create_resumen_ventas.sql", db_name="comercialaggregated")
    run_sql("CREATE TABLE ...", db_name="comercialaggregated")

Uso como script independiente:
    python utils/db_setup.py --file scripts/create_resumen_ventas.sql --db comercialaggregated
    python utils/db_setup.py --file scripts/create_reporte_ventas.sql --db-env DB_NAME_DESNORM
"""

import os
import re
import sys
import argparse

import mysql.connector
from dotenv import load_dotenv

load_dotenv()

_BASE = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    charset="utf8mb4",
)


def _split_statements(sql: str) -> list[str]:
    """Divide el SQL en sentencias individuales, ignorando comentarios vacíos."""
    # Eliminar comentarios de línea (--)
    sql = re.sub(r"--[^\n]*", "", sql)
    # Eliminar comentarios de bloque (/* */)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return [s.strip() for s in sql.split(";") if s.strip()]


def run_sql(sql: str, db_name: str, verbose: bool = True) -> int:
    """
    Ejecuta una o más sentencias SQL contra db_name.
    Retorna el número de sentencias ejecutadas.
    """
    statements = _split_statements(sql)
    if not statements:
        return 0

    conn = mysql.connector.connect(**_BASE, database=db_name)
    cur = conn.cursor()
    count = 0
    try:
        for stmt in statements:
            cur.execute(stmt)
            conn.commit()
            count += 1
            if verbose:
                preview = stmt[:60].replace("\n", " ")
                print(f"  OK  {preview}{'...' if len(stmt) > 60 else ''}")
    finally:
        cur.close()
        conn.close()

    return count


def run_sql_file(file_path: str, db_name: str, verbose: bool = True) -> int:
    """
    Lee un archivo .sql y ejecuta todas sus sentencias contra db_name.
    Retorna el número de sentencias ejecutadas.
    """
    path = os.path.abspath(file_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    with open(path, encoding="utf-8") as f:
        sql = f.read()

    if verbose:
        print(f"Ejecutando {os.path.basename(path)} en '{db_name}'...")

    count = run_sql(sql, db_name=db_name, verbose=verbose)

    if verbose:
        print(f"\n{count} sentencia(s) ejecutada(s) correctamente.")

    return count


# ─── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser(description="Ejecuta un script SQL en una DB específica")
    p.add_argument("--file",    required=True, metavar="RUTA",
                   help="Ruta al archivo .sql")

    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--db",     metavar="NOMBRE",
                        help="Nombre directo de la base de datos")
    target.add_argument("--db-env", metavar="VAR",
                        help="Variable de entorno que contiene el nombre de la DB "
                             "(ej. DB_NAME_AGG)")
    args = p.parse_args()

    db_name = args.db or os.getenv(args.db_env)
    if not db_name:
        print(f"ERROR: la variable '{args.db_env}' no está definida en el .env")
        sys.exit(1)

    try:
        run_sql_file(args.file, db_name=db_name)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except mysql.connector.Error as e:
        print(f"ERROR de base de datos: {e}")
        sys.exit(1)
