import ast
import os
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(ROOT / ".env")

SQL_KEYWORDS = {
    "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP",
    "ALTER", "WITH", "EXPLAIN", "SHOW", "TRUNCATE", "REPLACE",
}

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


def _looks_like_sql(s: str) -> bool:
    first = s.strip().split()[0].upper() if s.strip() else ""
    return first in SQL_KEYWORDS


def extract_sql_strings(source: str) -> list[dict]:
    """Parsea un string de código Python y devuelve lista de queries SQL encontrados.

    Cada entrada: {"line": int, "variable": str | None, "sql": str}
    """
    tree = ast.parse(source)
    found: list[dict] = []
    seen: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            var_name = (
                node.targets[0].id
                if isinstance(node.targets[0], ast.Name)
                else None
            )
            value = node.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                text = value.value
                if len(text) >= 10 and _looks_like_sql(text) and text not in seen:
                    seen.add(text)
                    found.append({"line": value.lineno, "variable": var_name, "sql": text})

        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
            if len(text) >= 10 and _looks_like_sql(text) and text not in seen:
                seen.add(text)
                found.append({"line": node.lineno, "variable": None, "sql": text})

    found.sort(key=lambda x: x["line"])
    return found


def extract_and_run(
    py_file: str | Path,
    db_key: str = "main",
    params: tuple = (),
    index: int = 0,
) -> list[dict]:
    """Extrae el query SQL de un archivo Python y lo ejecuta contra la DB.

    Args:
        py_file: ruta al archivo .py
        db_key:  "main" | "agg" | "desnorm"
        params:  parámetros posicionales para los %s del query
        index:   índice del query a ejecutar si el archivo tiene varios (default 0)

    Returns:
        Lista de filas como dicts. Para queries sin resultados (INSERT/UPDATE/DELETE)
        devuelve [{"affected_rows": n}].

    Raises:
        FileNotFoundError: si el archivo no existe
        IndexError: si el índice de query está fuera de rango
        ValueError: si no se encontraron queries en el archivo
        mysql.connector.Error: si MySQL devuelve un error
    """
    path = Path(py_file)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    source = path.read_text(encoding="utf-8")
    queries = extract_sql_strings(source)

    if not queries:
        raise ValueError(f"No se encontraron queries SQL en {path.name}")

    if index >= len(queries):
        raise IndexError(
            f"Índice {index} fuera de rango — el archivo tiene {len(queries)} query(s)"
        )

    sql = queries[index]["sql"]

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
