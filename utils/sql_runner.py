import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

DB_MAP = {
    "main":    os.getenv("DB_NAME"),
    "agg":     os.getenv("DB_NAME_AGG"),
    "desnorm": os.getenv("DB_NAME_DESNORM"),
}

_CONN_BASE = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    charset="utf8mb4",
)


def run_query(sql: str, db_key: str = "main", params: tuple = ()) -> list[dict]:
    """Ejecuta un query SQL y devuelve los resultados como lista de dicts.

    Args:
        sql:    query SQL a ejecutar
        db_key: "main" | "agg" | "desnorm"
        params: parámetros posicionales para los %s del query

    Returns:
        Lista de filas como dicts. Para queries sin resultados (INSERT/UPDATE/DELETE)
        devuelve [{"affected_rows": n}].

    Raises:
        ValueError: si db_key no es válido
        mysql.connector.Error: si MySQL devuelve un error
    """
    db_name = DB_MAP.get(db_key)
    if not db_name:
        raise ValueError(f"DB desconocida: '{db_key}'. Opciones: {list(DB_MAP)}")

    conn = mysql.connector.connect(database=db_name, **_CONN_BASE)
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or None)

        if cur.description is None:
            conn.commit()
            return [{"affected_rows": cur.rowcount}]

        rows = list(cur.fetchall())
        cur.close()
    finally:
        conn.close()

    return rows
