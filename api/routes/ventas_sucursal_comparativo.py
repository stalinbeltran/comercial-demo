from fastapi import APIRouter, Query, HTTPException
from datetime import date
from decimal import Decimal
from typing import Optional
import re

from api.db import get_conn_agg
from api.models import RespuestaVentasSucursalComparativo

router = APIRouter(prefix="/reportes", tags=["Reportes"])

_RE_MES = re.compile(r"^\d{4}-\d{2}$")

_SQL = """
SELECT
    a.sucursal_id,
    a.sucursal_nombre,
    a.pais_nombre,
    COALESCE(a.total_ventas, 0)    AS mes_actual,
    COALESCE(b.total_ventas, 0)    AS mes_anterior,
    ROUND(
        (COALESCE(a.total_ventas, 0) /
         NULLIF(COALESCE(b.total_ventas, 0), 0) - 1) * 100,
        2
    )                              AS variacion_pct,
    COALESCE(a.total_pedidos, 0)   AS total_pedidos,
    COALESCE(a.clientes_activos,0) AS clientes_activos
FROM resumen_ventas_sucursal_mes a
LEFT JOIN resumen_ventas_sucursal_mes b
       ON a.sucursal_id = b.sucursal_id
      AND b.mes = %s
WHERE a.mes = %s
ORDER BY mes_actual DESC
"""


def _parse_mes(s: str) -> date:
    if not _RE_MES.match(s):
        raise ValueError(f"Formato inválido '{s}'. Use YYYY-MM")
    year, month = int(s[:4]), int(s[5:7])
    return date(year, month, 1)


def _serialize(row: dict) -> dict:
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}


@router.get(
    "/ventas-sucursal-comparativo",
    response_model=RespuestaVentasSucursalComparativo,
    summary="Ventas por sucursal comparativo (mes actual vs anterior)",
    description=(
        "Compara las ventas por sucursal entre dos meses, calculando la "
        "**variación porcentual**.\n\n"
        "Los datos provienen de `comercialaggregated.resumen_ventas_sucursal_mes`. "
        "Si el resultado viene vacío, ejecutar:\n"
        "```\n"
        "python reportes/ventas_sucursal_comparativo/ventas_sucursal_comparativo_all.py\n"
        "```\n\n"
        "**Nota:** Requiere que `ventas_consolidado` esté poblado como paso previo.\n\n"
        "**Ordenado por** `mes_actual` descendente."
    ),
    responses={
        200: {"description": "Comparativo de ventas por sucursal entre dos meses"},
        400: {"description": "Formato de mes inválido o mes_actual igual a mes_anterior"},
    },
)
def ventas_sucursal_comparativo(
    mes_actual: Optional[str] = Query(
        default=None,
        description="Mes de referencia (YYYY-MM). Default: mes actual.",
        examples={"ejemplo": {"value": "2025-03"}},
    ),
    mes_anterior: Optional[str] = Query(
        default=None,
        description="Mes de comparación (YYYY-MM). Default: mes anterior.",
        examples={"ejemplo": {"value": "2025-02"}},
    ),
):
    hoy = date.today()

    try:
        d_actual   = _parse_mes(mes_actual)   if mes_actual   else hoy.replace(day=1)
        d_anterior = _parse_mes(mes_anterior) if mes_anterior else (
            hoy.replace(day=1, month=hoy.month - 1) if hoy.month > 1
            else hoy.replace(day=1, month=12, year=hoy.year - 1)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if d_actual == d_anterior:
        raise HTTPException(status_code=400, detail="mes_actual y mes_anterior no pueden ser iguales")

    conn = get_conn_agg()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(_SQL, (d_anterior, d_actual))
        rows = [_serialize(r) for r in cur.fetchall()]
        cur.close()
    finally:
        conn.close()

    total_actual   = round(sum(r["mes_actual"]   or 0 for r in rows), 2)
    total_anterior = round(sum(r["mes_anterior"] or 0 for r in rows), 2)
    var_global = (
        round((total_actual / total_anterior - 1) * 100, 2)
        if total_anterior else None
    )

    mes_actual_str   = d_actual.strftime("%Y-%m")
    mes_anterior_str = d_anterior.strftime("%Y-%m")

    return {
        "filtros": {
            "mes_actual":   mes_actual_str,
            "mes_anterior": mes_anterior_str,
        },
        "resumen": {
            "total_sucursales":    len(rows),
            "total_mes_actual":    total_actual,
            "total_mes_anterior":  total_anterior,
            "variacion_global_pct": var_global,
        },
        "datos": rows,
    }
