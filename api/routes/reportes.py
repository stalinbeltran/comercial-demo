from fastapi import APIRouter, Query, HTTPException
from datetime import date
from decimal import Decimal
from typing import Optional

from api.db import get_conn

router = APIRouter(prefix="/reportes", tags=["Reportes"])

# Cuando un producto está en una subcategoría, cat_raiz es el padre.
# Cuando está directo en una categoría raíz, cat_sub ya es la raíz y cat_raiz queda NULL.
# COALESCE resuelve ambos casos.
_SQL = """
SELECT
    COALESCE(cat_raiz.nombre, cat_sub.nombre)              AS categoria,
    CASE WHEN cat_raiz.id IS NOT NULL
         THEN cat_sub.nombre
         ELSE NULL END                                     AS subcategoria,
    p.codigo_sku                                           AS sku,
    p.nombre                                               AS producto,
    SUM(lp.cantidad)                                       AS unidades_vendidas,
    ROUND(AVG(lp.precio_unitario), 4)                      AS precio_promedio,
    ROUND(SUM(lp.descuento_monto), 2)                      AS total_descuentos,
    ROUND(SUM(lp.subtotal), 2)                             AS ingresos_netos,
    COUNT(DISTINCT lp.pedido_id)                           AS num_pedidos
FROM linea_pedido lp
JOIN pedido       pd         ON pd.id         = lp.pedido_id
JOIN producto     p          ON p.id          = lp.producto_id
LEFT JOIN categoria cat_sub  ON cat_sub.id    = p.categoria_id
LEFT JOIN categoria cat_raiz ON cat_raiz.id   = cat_sub.padre_id
WHERE pd.estado NOT IN ('cancelado', 'anulado', 'borrador')
  AND pd.fecha_pedido >= %s
  AND pd.fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
  AND (%s IS NULL OR pd.sucursal_id = %s)
GROUP BY
    cat_raiz.id, cat_raiz.nombre,
    cat_sub.id,  cat_sub.nombre,
    p.id,        p.codigo_sku,  p.nombre
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

    conn = get_conn()
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
