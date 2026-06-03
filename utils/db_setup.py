"""
utils/db_setup.py
Utilidad para ejecutar scripts SQL (DDL) contra una base de datos específica.

Uso como módulo:
    from utils.db_setup import run_sql_file, run_sql, drop_tables, tables_from_sql_file

    # Crear tablas
    run_sql_file("scripts/create_resumen_ventas.sql", db_name="comercialaggregated")

    # Borrar tablas específicas
    drop_tables(["resumen_ventas"], db_name="comercialaggregated")

    # Borrar las tablas definidas en un .sql y recrearlas
    drop_tables(tables_from_sql_file("scripts/create_resumen_ventas.sql"), db_name="comercialaggregated")
    run_sql_file("scripts/create_resumen_ventas.sql", db_name="comercialaggregated")

Uso como script independiente:
    # Solo crear
    python utils/db_setup.py --file scripts/create_resumen_ventas.sql --db-env DB_NAME_AGG

    # Borrar y recrear (drop + create)
    python utils/db_setup.py --file scripts/create_resumen_ventas.sql --db-env DB_NAME_AGG --recreate

    # Solo borrar las tablas del archivo
    python utils/db_setup.py --file scripts/create_resumen_ventas.sql --db-env DB_NAME_AGG --drop-only
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


# ─── HELPERS INTERNOS ─────────────────────────────────────────────────────────

def _split_statements(sql: str) -> list[str]:
    sql = re.sub(r"--[^\n]*", "", sql)
    sql = re.sub(r"/\*.*?\*/", "", sql, flags=re.DOTALL)
    return [s.strip() for s in sql.split(";") if s.strip()]


def _connect(db_name: str):
    return mysql.connector.connect(**_BASE, database=db_name)


# ─── API PÚBLICA ──────────────────────────────────────────────────────────────

def tables_from_sql_file(file_path: str) -> list[str]:
    """
    Parsea un archivo .sql y devuelve los nombres de todas las tablas
    definidas en sentencias CREATE TABLE.
    """
    path = os.path.abspath(file_path)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    with open(path, encoding="utf-8") as f:
        sql = f.read()

    return re.findall(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?",
        sql,
        flags=re.IGNORECASE,
    )


def drop_tables(table_names: list[str], db_name: str, verbose: bool = True) -> int:
    """
    Borra las tablas indicadas usando DROP TABLE IF EXISTS.
    Deshabilita FK checks durante el proceso para evitar errores de dependencia.
    Retorna el número de tablas eliminadas.
    """
    if not table_names:
        return 0

    conn = _connect(db_name)
    cur = conn.cursor()
    count = 0
    try:
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in table_names:
            cur.execute(f"DROP TABLE IF EXISTS `{table}`")
            conn.commit()
            count += 1
            if verbose:
                print(f"  DROP  {table}")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()
    finally:
        cur.close()
        conn.close()

    return count


def run_sql(sql: str, db_name: str, verbose: bool = True) -> int:
    """
    Ejecuta una o más sentencias SQL contra db_name.
    Retorna el número de sentencias ejecutadas.
    """
    statements = _split_statements(sql)
    if not statements:
        return 0

    conn = _connect(db_name)
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

    p = argparse.ArgumentParser(
        description="Ejecuta un script SQL DDL en una DB específica",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Ejemplos:\n"
            "  Solo crear:\n"
            "    python utils/db_setup.py --file scripts/create_resumen_ventas.sql --db-env DB_NAME_AGG\n\n"
            "  Borrar y recrear:\n"
            "    python utils/db_setup.py --file scripts/create_resumen_ventas.sql --db-env DB_NAME_AGG --recreate\n\n"
            "  Solo borrar:\n"
            "    python utils/db_setup.py --file scripts/create_resumen_ventas.sql --db-env DB_NAME_AGG --drop-only\n"
        ),
    )
    p.add_argument("--file", required=True, metavar="RUTA",
                   help="Ruta al archivo .sql")

    target = p.add_mutually_exclusive_group(required=True)
    target.add_argument("--db",     metavar="NOMBRE",
                        help="Nombre directo de la base de datos")
    target.add_argument("--db-env", metavar="VAR",
                        help="Variable de entorno con el nombre de la DB (ej. DB_NAME_AGG)")

    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--recreate",  action="store_true",
                      help="Drop de las tablas del archivo y luego CREATE (drop + create)")
    mode.add_argument("--drop-only", action="store_true",
                      help="Solo hace DROP de las tablas definidas en el archivo, sin crear")

    args = p.parse_args()

    db_name = args.db or os.getenv(args.db_env)
    if not db_name:
        print(f"ERROR: la variable '{args.db_env}' no esta definida en el .env")
        sys.exit(1)

    try:
        if args.drop_only or args.recreate:
            tables = tables_from_sql_file(args.file)
            if not tables:
                print("No se encontraron tablas en el archivo.")
                sys.exit(0)
            print(f"Tablas encontradas: {', '.join(tables)}")
            drop_tables(tables, db_name=db_name)
            if args.drop_only:
                print(f"\n{len(tables)} tabla(s) eliminada(s).")
                sys.exit(0)
            print()

        run_sql_file(args.file, db_name=db_name)

    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except mysql.connector.Error as e:
        print(f"ERROR de base de datos: {e}")
        sys.exit(1)
