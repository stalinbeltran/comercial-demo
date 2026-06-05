import ast
import re
from pathlib import Path

from utils.sql_runner import DB_MAP, run_query

SQL_KEYWORDS = {
    "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP",
    "ALTER", "WITH", "EXPLAIN", "SHOW", "TRUNCATE", "REPLACE",
}

# Palabras reservadas SQL que nunca son nombres de tabla
_SQL_RESERVED = {
    "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
    "FULL", "CROSS", "ON", "AND", "OR", "NOT", "IN", "IS", "NULL", "AS",
    "BY", "GROUP", "ORDER", "HAVING", "LIMIT", "OFFSET", "UNION", "ALL",
    "DISTINCT", "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE",
    "CREATE", "DROP", "ALTER", "TABLE", "INDEX", "VIEW", "PROCEDURE",
    "FUNCTION", "TRIGGER", "DATABASE", "SCHEMA", "WITH", "EXISTS",
    "BETWEEN", "LIKE", "CASE", "WHEN", "THEN", "ELSE", "END", "IF",
    "EXPLAIN", "SHOW", "TRUNCATE", "REPLACE", "USING", "NATURAL",
    "STRAIGHT_JOIN", "SUBQUERY",
}

_TABLE_PATTERN = re.compile(
    r"""
    (?:
        (?:FROM|JOIN|INNER\s+JOIN|LEFT\s+(?:OUTER\s+)?JOIN|RIGHT\s+(?:OUTER\s+)?JOIN
          |FULL\s+(?:OUTER\s+)?JOIN|CROSS\s+JOIN|STRAIGHT_JOIN)
        \s+
        (`?[\w]+`?(?:\.`?[\w]+`?)*)   # tabla, opcionalmente db.tabla
    |
        (?:UPDATE|INTO)
        \s+
        (`?[\w]+`?(?:\.`?[\w]+`?)*)
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)


def extract_tables_from_sql(sql: str) -> list[str]:
    """Devuelve la lista de tablas consultadas en un query SQL."""
    tables: list[str] = []
    seen: set[str] = set()

    for match in _TABLE_PATTERN.finditer(sql):
        raw = match.group(1) or match.group(2) or ""
        # Quitar backticks y tomar solo la parte del nombre de tabla (sin schema prefix)
        name = raw.replace("`", "").split(".")[-1].strip()
        upper = name.upper()
        if name and upper not in _SQL_RESERVED and not upper.startswith("("):
            if name not in seen:
                seen.add(name)
                tables.append(name)

    return tables


def _looks_like_sql(s: str) -> bool:
    first = s.strip().split()[0].upper() if s.strip() else ""
    return first in SQL_KEYWORDS


# ─── INFERENCIA DE TIPOS DE PARÁMETROS ────────────────────────────────────────

# Tipos SQL ordenados: variantes largas primero para evitar coincidencias parciales
_SQL_TYPE_TOKENS = (
    "BIGINT", "MEDIUMINT", "SMALLINT", "TINYINT", "INT",
    "DECIMAL", "NUMERIC", "DOUBLE", "FLOAT", "REAL",
    "VARCHAR", "CHAR",
    "LONGTEXT", "MEDIUMTEXT", "TINYTEXT", "TEXT",
    "DATETIME", "DATE", "TIMESTAMP", "TIME", "YEAR",
    "BOOLEAN", "BOOL", "BIT",
    "LONGBLOB", "MEDIUMBLOB", "TINYBLOB", "BLOB",
    "JSON", "ENUM", "SET",
)

_COL_DEF_RE = re.compile(
    r"^\s{2,}`?(\w+)`?\s+"
    r"((?:" + "|".join(_SQL_TYPE_TOKENS) + r")"
    r"(?:\s*\(\s*\d+(?:\s*,\s*\d+)?\s*\))?"
    r"(?:\s+UNSIGNED)?(?:\s+ZEROFILL)?)",
    re.IGNORECASE | re.MULTILINE,
)

_NAMED_PARAM_RE = re.compile(r"%\((\w+)\)s")


def build_col_types(catalogo: dict) -> dict[str, str]:
    """Construye un dict col_name→tipo_sql a partir de los CREATE TABLE del catálogo.

    Claves: "tabla.columna" (canónico) y "columna" (fallback sin tabla).
    """
    col_types: dict[str, str] = {}
    for module in catalogo.get("modulos", []):
        for reporte in module.get("reportes", []):
            for table, ddl in reporte.get("creates", {}).items():
                for m in _COL_DEF_RE.finditer(ddl):
                    col = m.group(1).lower()
                    tipo = re.sub(r"\s+", " ", m.group(2).strip()).upper()
                    col_types[f"{table.lower()}.{col}"] = tipo
                    col_types.setdefault(col, tipo)
    return col_types


def _strip_alias(col_ref: str) -> str:
    """'pd.fecha_pedido' → 'fecha_pedido'"""
    return col_ref.split(".")[-1]


def _get_col_type(column: str, tables: list[str], col_types: dict) -> str | None:
    col = column.lower()
    for table in tables:
        t = col_types.get(f"{table.lower()}.{col}")
        if t:
            return t
    return col_types.get(col)


def _find_column_for_param(sql: str, pos: int) -> tuple[str | None, bool]:
    """Dada la posición de un %s en el SQL, devuelve (columna, es_nullable).

    Reconoce los patrones:
      col OP DATE_ADD(%s, ...)
      %s IS NULL OR col = %s   (primer y segundo %s)
      col BETWEEN %s AND %s    (primer y segundo %s)
      col OP %s                (comparación general)
      %s OP col
    """
    before = sql[max(0, pos - 120): pos]
    after  = sql[pos + 2: pos + 120]

    # col OP DATE_ADD(%s, ...)
    m = re.search(
        r"(\w+(?:\.\w+)?)\s*(?:>=|<=|!=|<>|=|>|<)\s*DATE_ADD\s*\(\s*$",
        before, re.IGNORECASE,
    )
    if m:
        return _strip_alias(m.group(1)), False

    # Primer %s de: %s IS NULL OR col = %s
    m = re.match(r"\s*IS\s+NULL\s+OR\s+(\w+(?:\.\w+)?)\s*=\s*%s", after, re.IGNORECASE)
    if m:
        return _strip_alias(m.group(1)), True

    # Segundo %s de: %s IS NULL OR col = %s
    m = re.search(
        r"%s\s+IS\s+NULL\s+OR\s+(\w+(?:\.\w+)?)\s*=\s*$", before, re.IGNORECASE,
    )
    if m:
        return _strip_alias(m.group(1)), False

    # Primer %s de: col BETWEEN %s AND %s
    m = re.search(r"(\w+(?:\.\w+)?)\s+BETWEEN\s+$", before, re.IGNORECASE)
    if m:
        return _strip_alias(m.group(1)), False

    # Segundo %s de: col BETWEEN %s AND %s
    m = re.search(
        r"(\w+(?:\.\w+)?)\s+BETWEEN\s+%s\s+AND\s+$", before, re.IGNORECASE,
    )
    if m:
        return _strip_alias(m.group(1)), False

    # col OP %s  (comparación general)
    m = re.search(
        r"(\w+(?:\.\w+)?)\s*(?:>=|<=|!=|<>|=|>|<|LIKE|NOT\s+LIKE)\s*$",
        before, re.IGNORECASE,
    )
    if m:
        return _strip_alias(m.group(1)), False

    # %s OP col
    m = re.match(r"\s*(?:>=|<=|!=|<>|=|>|<)\s*(\w+(?:\.\w+)?)", after, re.IGNORECASE)
    if m:
        return _strip_alias(m.group(1)), False

    return None, False


def infer_params(sql: str, tables: list[str], col_types: dict) -> list[dict]:
    """Infiere tipos de parámetros %s (posicionales) o %(name)s (nombrados).

    Devuelve lista de dicts con keys: pos|name, column (posicional), type, nullable.
    """
    if _NAMED_PARAM_RE.search(sql):
        result = []
        for m in _NAMED_PARAM_RE.finditer(sql):
            col = m.group(1)
            t = _get_col_type(col, tables, col_types)
            entry: dict = {"name": col}
            if t:
                entry["type"] = t
            result.append(entry)
        return result

    positions = [m.start() for m in re.finditer(r"%s", sql)]
    if not positions:
        return []

    result = []
    for i, pos in enumerate(positions, 1):
        col, nullable = _find_column_for_param(sql, pos)
        t = _get_col_type(col, tables, col_types) if col else None
        entry: dict = {"pos": i}
        if col:
            entry["column"] = col
        if t:
            entry["type"] = t
        if nullable:
            entry["nullable"] = True
        result.append(entry)

    return result


def extract_sql_strings(source: str, col_types: dict | None = None) -> list[dict]:
    """Parsea código Python y devuelve los queries SQL encontrados.

    Cada entrada: {"line": int, "variable": str|None, "sql": str,
                   "tables": list[str], "params": list[dict]}
    """
    tree = ast.parse(source)
    found: list[dict] = []
    seen: set[str] = set()
    _col_types = col_types or {}

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
                    tables = extract_tables_from_sql(text)
                    found.append({
                        "line": value.lineno,
                        "variable": var_name,
                        "sql": text,
                        "tables": tables,
                        "params": infer_params(text, tables, _col_types),
                    })

        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
            if len(text) >= 10 and _looks_like_sql(text) and text not in seen:
                seen.add(text)
                tables = extract_tables_from_sql(text)
                found.append({
                    "line": node.lineno,
                    "variable": None,
                    "sql": text,
                    "tables": tables,
                    "params": infer_params(text, tables, _col_types),
                })

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
        index:   índice del query si el archivo tiene varios (default 0)

    Returns:
        Lista de filas como dicts. Para DML devuelve [{"affected_rows": n}].

    Raises:
        FileNotFoundError: si el archivo no existe
        IndexError: si el índice está fuera de rango
        ValueError: si no hay queries o db_key es inválido
        mysql.connector.Error: si MySQL devuelve un error
    """
    path = Path(py_file)
    if not path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {path}")

    queries = extract_sql_strings(path.read_text(encoding="utf-8"))

    if not queries:
        raise ValueError(f"No se encontraron queries SQL en {path.name}")
    if index >= len(queries):
        raise IndexError(
            f"Índice {index} fuera de rango — el archivo tiene {len(queries)} query(s)"
        )

    return run_query(queries[index]["sql"], db_key, params)
