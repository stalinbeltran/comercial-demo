from fastapi import APIRouter, Query, HTTPException
from datetime import date
from decimal import Decimal
from typing import Optional

from api.db import get_conn_agg
from api.models import RespuestaVentasConsolidado

router = APIRouter(prefix="/reportes", tags=["Reportes"])

_SQL = """
SELECT
    sucursal_id,
    sucursal_nombre,
    pais_nombre,
    SUM(total_ventas)     AS total_ventas,
    SUM(total_pedidos)    AS total_pedidos,
    SUM(clientes_activos) AS clientes_activos
FROM resumen_ventas_consolidado
WHERE periodo_inicio >= %s
  AND periodo_fin    <= %s
  AND (%s IS NULL OR sucursal_id = %s)
GROUP BY sucursal_id, sucursal_nombre, pais_nombre
ORDER BY total_ventas DESC
"""


def _serialize(row: dict) -> dict:
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}


@router.get(
    "/ventas-consolidado",
    response_model=RespuestaVentasConsolidado,
    summary="Resumen de ventas consolidado",
    description=(
        "Devuelve el resumen de ventas agrupado por **sucursal y país** "
        "para el período indicado.\n\n"
        "Los datos provienen de `comercialaggregated.resumen_ventas_consolidado`. "
        "Si el resultado viene vacío, ejecutar:\n"
        "```\n"
        "python scripts/fill_ventas_consolidado.py --full\n"
        "python scripts/fill_resumen_ventas_consolidado.py --desde YYYY-MM-DD --hasta YYYY-MM-DD\n"
        "```\n\n"
        "Excluye pedidos con estado `cancelado` o `anulado`. "
        "**Ordenado por** `total_ventas` descendente."
    ),
    responses={
        200: {"description": "Resumen de ventas por sucursal y país"},
        400: {"description": "fecha_desde es posterior a fecha_hasta"},
    },
)
def ventas_consolidado(
    fecha_desde: Optional[date] = Query(
        default=None,
        description="Inicio del período (YYYY-MM-DD). Default: primer día del mes actual.",
        examples={"ejemplo": {"value": "2025-01-01"}},
    ),
    fecha_hasta: Optional[date] = Query(
        default=None,
        description="Fin del período (YYYY-MM-DD). Default: hoy.",
        examples={"ejemplo": {"value": "2025-12-31"}},
    ),
    sucursal_id: Optional[int] = Query(
        default=None,
        description="ID de sucursal. Omitir para obtener el total de todas las sucursales.",
        examples={"ejemplo": {"value": 1}},
    ),
):
    hoy = date.today()
    if fecha_desde is None:
        fecha_desde = hoy.replace(day=1)
    if fecha_hasta is None:
        fecha_hasta = hoy

    if fecha_desde > fecha_hasta:
        raise HTTPException(
            status_code=400,
            detail="fecha_desde no puede ser posterior a fecha_hasta",
        )

    conn = get_conn_agg()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(_SQL, (fecha_desde, fecha_hasta, sucursal_id, sucursal_id))
        rows = [_serialize(r) for r in cur.fetchall()]
        cur.close()
    finally:
        conn.close()

    return {
        "filtros": {
            "fecha_desde": fecha_desde.isoformat(),
            "fecha_hasta": fecha_hasta.isoformat(),
            "sucursal_id": sucursal_id,
        },
        "resumen": {
            "total_registros":  len(rows),
            "total_ventas":     round(sum(r["total_ventas"] or 0 for r in rows), 2),
            "total_pedidos":    int(sum(r["total_pedidos"] or 0 for r in rows)),
            "clientes_activos": int(sum(r["clientes_activos"] or 0 for r in rows)),
        },
        "datos": rows,
    }
