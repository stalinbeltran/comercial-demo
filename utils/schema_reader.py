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
