from fastapi import APIRouter, Query, HTTPException
from datetime import date
from decimal import Decimal
from typing import Optional

from api.db import get_conn_agg
from api.models import RespuestaVentasCategoria

router = APIRouter(prefix="/reportes", tags=["Reportes"])

_SQL = """
SELECT
    categoria,
    subcategoria,
    sku,
    producto,
    SUM(unidades_vendidas)                          AS unidades_vendidas,
    ROUND(AVG(precio_promedio), 4)                  AS precio_promedio,
    ROUND(SUM(total_descuentos), 2)                 AS total_descuentos,
    ROUND(SUM(ingresos_netos), 2)                   AS ingresos_netos,
    SUM(num_pedidos)                                AS num_pedidos
FROM resumen_ventas
WHERE periodo_inicio >= %s
  AND periodo_fin    <= %s
  AND (%s IS NULL OR sucursal_id = %s)
GROUP BY categoria, subcategoria, sku, producto
ORDER BY ingresos_netos DESC
"""


def _serialize(row: dict) -> dict:
    return {k: float(v) if isinstance(v, Decimal) else v for k, v in row.items()}


@router.get(
    "/ventas-por-categoria",
    response_model=RespuestaVentasCategoria,
    summary="Ventas por producto y categoría",
    description=(
        "Devuelve las ventas agrupadas por **categoría → subcategoría → producto** "
        "para el período indicado.\n\n"
        "Los datos se obtienen de `comercialaggregated.resumen_ventas`. "
        "Si la tabla no tiene datos para el rango solicitado, ejecutar "
        "`fill_resumen_ventas.py --desde ... --hasta ...`.\n\n"
        "**Ordenado por** `ingresos_netos` descendente."
    ),
    responses={
        200: {"description": "Listado de productos con métricas agregadas"},
        400: {"description": "fecha_desde es posterior a fecha_hasta"},
    },
)
def ventas_por_categoria(
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
            "total_registros": len(rows),
            "total_ingresos":  round(sum(r["ingresos_netos"] or 0 for r in rows), 2),
            "total_unidades":  round(sum(r["unidades_vendidas"] or 0 for r in rows), 2),
        },
        "datos": rows,
    }
