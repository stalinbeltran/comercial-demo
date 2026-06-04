from dataclasses import dataclass, field

import sqlglot
import sqlglot.errors


@dataclass
class SqlDebugResult:
    original: str
    formatted: str | None
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    dialect: str = "mysql"

    def __str__(self) -> str:
        lines = []
        status = "OK" if self.is_valid else "INVALIDO"
        lines.append(f"[{status}] Dialecto: {self.dialect}")
        if self.errors:
            lines.append("Errores:")
            for e in self.errors:
                lines.append(f"  - {e}")
        lines.append("\nQuery formateado:")
        lines.append(self.formatted or self.original)
        return "\n".join(lines)


def debug_sql(query: str, dialect: str = "mysql") -> SqlDebugResult:
    """Parsea, valida y formatea un SQL. Retorna un SqlDebugResult."""
    errors: list[str] = []
    formatted: str | None = None

    try:
        statements = sqlglot.parse(query, dialect=dialect, error_level=sqlglot.errors.ErrorLevel.RAISE)
        parts = [s.sql(dialect=dialect, pretty=True) for s in statements if s]
        formatted = ";\n\n".join(parts)
        is_valid = True
    except sqlglot.errors.ParseError as e:
        is_valid = False
        for err in e.errors:
            msg = err.get("description", str(err))
            line = err.get("line")
            col = err.get("col")
            loc = f" (línea {line}, col {col})" if line else ""
            errors.append(f"{msg}{loc}")
        try:
            formatted = sqlglot.transpile(query, read=dialect, pretty=True, error_level=sqlglot.errors.ErrorLevel.WARN)[0]
        except Exception:
            formatted = None

    return SqlDebugResult(
        original=query,
        formatted=formatted,
        is_valid=is_valid,
        errors=errors,
        dialect=dialect,
    )
