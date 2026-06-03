from fastapi import APIRouter, Query, HTTPException
from datetime import date
from decimal import Decimal
from typing import Optional

from api.db import get_conn_agg

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


@router.get("/ventas-por-categoria", summary="Ventas por producto y categoría")
def ventas_por_categoria(
    fecha_desde: Optional[date] = Query(default=None, description="Inicio del período (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(default=None, description="Fin del período (YYYY-MM-DD)"),
    sucursal_id: Optional[int] = Query(default=None, description="Filtrar por sucursal"),
):
    hoy = date.today()
    if fecha_desde is None:
        fecha_desde = hoy.replace(day=1)
    if fecha_hasta is None:
        fecha_hasta = hoy

    if fecha_desde > fecha_hasta:
        raise HTTPException(status_code=400, detail="fecha_desde no puede ser mayor que fecha_hasta")

    conn = get_conn_agg()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(_SQL, (fecha_desde, fecha_hasta, sucursal_id, sucursal_id))
        rows = [_serialize(r) for r in cur.fetchall()]
        cur.close()
    finally:
        conn.close()

    total_ingresos = round(sum(r["ingresos_netos"] or 0 for r in rows), 2)
    total_unidades = round(sum(r["unidades_vendidas"] or 0 for r in rows), 2)

    return {
        "filtros": {
            "fecha_desde": fecha_desde.isoformat(),
            "fecha_hasta": fecha_hasta.isoformat(),
            "sucursal_id": sucursal_id,
        },
        "resumen": {
            "total_registros": len(rows),
            "total_ingresos":  total_ingresos,
            "total_unidades":  total_unidades,
        },
        "datos": rows,
    }
