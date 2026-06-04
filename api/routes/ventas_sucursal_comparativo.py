import calendar
import re
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from api.db import get_conn_agg
from api.models import RespuestaVentasSucursalComparativo

router = APIRouter(prefix="/reportes", tags=["Reportes"])

_RE_MES = re.compile(r"^\d{4}-\d{2}$")

# Agrega los días de un mes para una o todas las sucursales
_SQL_MES = """
SELECT
    sucursal_id,
    sucursal_nombre,
    pais_nombre,
    SUM(total_ventas)     AS total_ventas,
    SUM(total_pedidos)    AS total_pedidos,
    SUM(clientes_activos) AS clientes_activos
FROM resumen_ventas_sucursal_dia
WHERE fecha BETWEEN %s AND %s
  AND (%s IS NULL OR sucursal_id = %s)
GROUP BY sucursal_id, sucursal_nombre, pais_nombre
ORDER BY total_ventas DESC
"""


def _parse_mes(s: str) -> date:
    if not _RE_MES.match(s):
        raise ValueError(f"Formato invalido '{s}'. Use YYYY-MM")
    year, month = int(s[:4]), int(s[5:7])
    return date(year, month, 1)


def _ultimo_dia(d: date) -> date:
    return d.replace(day=calendar.monthrange(d.year, d.month)[1])


def _serialize(row: dict) -> dict:
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}


def _query_mes(cur, primer_dia: date, ultimo_dia: date, sucursal_id) -> dict:
    cur.execute(_SQL_MES, (primer_dia, ultimo_dia, sucursal_id, sucursal_id))
    return {r["sucursal_id"]: _serialize(r) for r in cur.fetchall()}


@router.get(
    "/ventas-sucursal-comparativo",
    response_model=RespuestaVentasSucursalComparativo,
    summary="Ventas por sucursal comparativo (mes actual vs anterior)",
    description=(
        "Compara las ventas por sucursal entre dos meses calculando la "
        "**variación porcentual**.\n\n"
        "Los datos provienen de `comercialaggregated.resumen_ventas_sucursal_dia` "
        "(granularidad diaria). La API agrega los días de cada mes en tiempo real, "
        "lo que permite comparar cualquier par de meses sin re-ejecutar el fill.\n\n"
        "Si el resultado viene vacío, ejecutar:\n"
        "```\n"
        "python reportes/ventas_sucursal_comparativo/ventas_sucursal_comparativo_all.py\n"
        "```\n\n"
        "**Nota:** Requiere que `ventas_consolidado` esté poblado previamente.\n\n"
        "**Ordenado por** ventas del mes actual descendente."
    ),
    responses={
        200: {"description": "Comparativo de ventas por sucursal entre dos meses"},
        400: {"description": "Formato de mes inválido o ambos meses son iguales"},
    },
)
def ventas_sucursal_comparativo(
    mes_actual: Optional[str] = Query(
        default=None,
        description="Mes de referencia (YYYY-MM). Default: mes actual.",
        examples={"ejemplo": {"value": "2025-06"}},
    ),
    mes_anterior: Optional[str] = Query(
        default=None,
        description="Mes de comparación (YYYY-MM). Default: mes anterior.",
        examples={"ejemplo": {"value": "2025-05"}},
    ),
    sucursal_id: Optional[int] = Query(
        default=None,
        description="Filtrar por sucursal (opcional).",
        examples={"ejemplo": {"value": 1}},
    ),
):
    hoy = date.today()

    try:
        d_actual = _parse_mes(mes_actual) if mes_actual else hoy.replace(day=1)
        d_anterior = (
            _parse_mes(mes_anterior) if mes_anterior else (
                hoy.replace(day=1, month=hoy.month - 1) if hoy.month > 1
                else hoy.replace(day=1, month=12, year=hoy.year - 1)
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if d_actual == d_anterior:
        raise HTTPException(status_code=400, detail="mes_actual y mes_anterior no pueden ser iguales")

    conn = get_conn_agg()
    try:
        cur = conn.cursor(dictionary=True)
        map_actual   = _query_mes(cur, d_actual,   _ultimo_dia(d_actual),   sucursal_id)
        map_anterior = _query_mes(cur, d_anterior, _ultimo_dia(d_anterior), sucursal_id)
        cur.close()
    finally:
        conn.close()

    # Unir ambos meses por sucursal_id
    sucursales = {**{k: v for k, v in map_actual.items()},
                  **{k: v for k, v in map_anterior.items() if k not in map_actual}}

    datos = []
    for sid, info in sorted(sucursales.items(),
                             key=lambda x: map_actual.get(x[0], {}).get("total_ventas", 0),
                             reverse=True):
        venta_actual   = float(map_actual.get(sid,   {}).get("total_ventas", 0) or 0)
        venta_anterior = float(map_anterior.get(sid, {}).get("total_ventas", 0) or 0)
        variacion = (
            round((venta_actual / venta_anterior - 1) * 100, 2)
            if venta_anterior else None
        )
        datos.append({
            "sucursal_id":      sid,
            "sucursal_nombre":  info.get("sucursal_nombre"),
            "pais_nombre":      info.get("pais_nombre"),
            "mes_actual":       venta_actual,
            "mes_anterior":     venta_anterior,
            "variacion_pct":    variacion,
            "total_pedidos":    int(map_actual.get(sid, {}).get("total_pedidos", 0) or 0),
            "clientes_activos": int(map_actual.get(sid, {}).get("clientes_activos", 0) or 0),
        })

    total_actual   = round(sum(r["mes_actual"]   for r in datos), 2)
    total_anterior = round(sum(r["mes_anterior"] for r in datos), 2)
    var_global = (
        round((total_actual / total_anterior - 1) * 100, 2)
        if total_anterior else None
    )

    return {
        "filtros": {
            "mes_actual":   d_actual.strftime("%Y-%m"),
            "mes_anterior": d_anterior.strftime("%Y-%m"),
        },
        "resumen": {
            "total_sucursales":     len(datos),
            "total_mes_actual":     total_actual,
            "total_mes_anterior":   total_anterior,
            "variacion_global_pct": var_global,
        },
        "datos": datos,
    }
