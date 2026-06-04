import json
import re
from pathlib import Path

from utils.helpers import walk_files

ROOT = Path(__file__).parent.parent
OUTPUT_FILE = ROOT / "output" / "schema_creates.json"

_CREATE_RE = re.compile(
    r"(CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(.*?\);)",
    re.IGNORECASE | re.DOTALL,
)


def _extract_creates_from_sql(source: str) -> list[dict]:
    """Extrae todos los CREATE TABLE de un string SQL.

    Retorna lista de {"table": str, "sql": str}.
    """
    results = []
    for match in _CREATE_RE.finditer(source):
        results.append({"table": match.group(2).lower(), "sql": match.group(1).strip()})
    return results


def extract_creates(reportes_dir: str | Path) -> dict:
    """Recorre todos los .sql de reportes_dir y extrae los CREATE TABLE.

    Estructura del resultado:
        {
          "reporte_nombre": {
            "tabla_nombre": "CREATE TABLE tabla_nombre (...);",
            ...
          },
          ...
        }

    Args:
        reportes_dir: carpeta raíz de reportes (ej. "reportes/")

    Returns:
        Dict anidado reporte → tabla → CREATE SQL.
    """
    base = Path(reportes_dir)
    result: dict[str, dict[str, str]] = {}

    for sql_file in walk_files(base, ".sql"):
        reporte = sql_file.parent.name          # nombre de la subcarpeta = reporte
        source  = sql_file.read_text(encoding="utf-8")
        creates = _extract_creates_from_sql(source)

        if creates:
            if reporte not in result:
                result[reporte] = {}
            for c in creates:
                result[reporte][c["table"]] = c["sql"]

    return dict(sorted(result.items()))


def save_creates(reportes_dir: str | Path = ROOT / "reportes") -> Path:
    """Ejecuta extract_creates y guarda el resultado en output/schema_creates.json."""
    data = extract_creates(reportes_dir)
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return OUTPUT_FILE


def load_creates() -> dict:
    """Carga el JSON de schemas ya generado. Retorna {} si no existe."""
    if not OUTPUT_FILE.exists():
        return {}
    try:
        return json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def detect_table_dbs(table_names: list[str]) -> dict[str, str]:
    """Consulta INFORMATION_SCHEMA para determinar en qué DB existe cada tabla.

    Usa una sola conexión (main) — el usuario tiene acceso a todos los schemas.

    Args:
        table_names: lista de nombres de tabla a buscar

    Returns:
        {table_name: db_key}  ej. {"resumen_ventas_consolidado": "agg"}
    """
    from utils.sql_runner import DB_MAP, run_query

    if not table_names:
        return {}

    db_name_to_key = {v: k for k, v in DB_MAP.items() if v}
    db_names = list(db_name_to_key.keys())

    t_ph  = ", ".join(["%s"] * len(table_names))
    db_ph = ", ".join(["%s"] * len(db_names))

    sql = f"""
        SELECT TABLE_NAME, TABLE_SCHEMA
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME  IN ({t_ph})
          AND TABLE_SCHEMA IN ({db_ph})
    """

    rows = run_query(sql, "main", tuple(table_names + db_names))

    return {
        row["TABLE_NAME"]: db_name_to_key[row["TABLE_SCHEMA"]]
        for row in rows
        if row["TABLE_SCHEMA"] in db_name_to_key
    }
