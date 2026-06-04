"""
reportes/ventas_por_categoria/fill_linea_venta.py
Lee de 'comercial' e inserta en 'comercialdesnormalized.linea_venta'.

Uso:
    python reportes/ventas_por_categoria/fill_linea_venta.py --full
    python reportes/ventas_por_categoria/fill_linea_venta.py --desde 2025-01-01
    python reportes/ventas_por_categoria/fill_linea_venta.py --desde 2025-01-01 --hasta 2025-12-31
"""

import os
import sys
import argparse
from datetime import date

import mysql.connector
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, _ROOT)
load_dotenv(os.path.join(_ROOT, ".env"))

BATCH_SIZE = 500

_BASE = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "charset":  "utf8mb4",
}

def conn_source():
    return mysql.connector.connect(**_BASE, database=os.getenv("DB_NAME"))

def conn_target():
    return mysql.connector.connect(**_BASE, database=os.getenv("DB_NAME_DESNORM"))


_SQL_SELECT_RANGO = """
SELECT
    lp.id                                                    AS linea_id,
    lp.pedido_id,
    pd.numero_pedido,
    pd.fecha_pedido,
    pd.fecha_requerida,
    pd.estado                                                AS estado_pedido,
    pd.moneda,
    cl.id                                                    AS cliente_id,
    cl.nombre                                                AS cliente_nombre,
    cl.tipo                                                  AS cliente_tipo,
    cl.identificacion                                        AS cliente_identificacion,
    gc.nombre                                                AS grupo_cliente,
    su.id                                                    AS sucursal_id,
    su.nombre                                                AS sucursal_nombre,
    ci.nombre                                                AS ciudad_sucursal,
    COALESCE(cat_raiz.nombre, cat_sub.nombre)                AS categoria,
    CASE WHEN cat_raiz.id IS NOT NULL
         THEN cat_sub.nombre ELSE NULL END                   AS subcategoria,
    p.id                                                     AS producto_id,
    p.codigo_sku                                             AS sku,
    p.nombre                                                 AS producto,
    p.unidad_medida,
    p.precio_oficial,
    bo.id                                                    AS bodega_id,
    bo.nombre                                                AS bodega_nombre,
    bo.tipo                                                  AS tipo_bodega,
    lp.cantidad,
    lp.precio_unitario,
    lp.descuento_pct,
    lp.descuento_monto,
    lp.subtotal,
    CASE WHEN lp.promocion_id IS NOT NULL THEN 1 ELSE 0 END  AS con_promocion,
    fa.id                                                    AS factura_id,
    fa.numero_fiscal,
    fa.estado                                                AS estado_factura,
    fa.fecha_emision,
    fa.impuesto_pct
FROM linea_pedido lp
JOIN pedido            pd         ON pd.id        = lp.pedido_id
JOIN cliente           cl         ON cl.id        = pd.cliente_id
LEFT JOIN grupo_cliente gc        ON gc.id        = cl.grupo_cliente_id
JOIN sucursal          su         ON su.id        = pd.sucursal_id
LEFT JOIN ciudad       ci         ON ci.id        = su.ciudad_id
JOIN producto          p          ON p.id         = lp.producto_id
LEFT JOIN categoria    cat_sub    ON cat_sub.id   = p.categoria_id
LEFT JOIN categoria    cat_raiz   ON cat_raiz.id  = cat_sub.padre_id
JOIN bodega            bo         ON bo.id        = lp.bodega_id
LEFT JOIN factura      fa         ON fa.pedido_id = pd.id
WHERE pd.fecha_pedido >= %s
  AND pd.fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
ORDER BY lp.id
"""

_SQL_SELECT_FULL = """
SELECT
    lp.id                                                    AS linea_id,
    lp.pedido_id,
    pd.numero_pedido,
    pd.fecha_pedido,
    pd.fecha_requerida,
    pd.estado                                                AS estado_pedido,
    pd.moneda,
    cl.id                                                    AS cliente_id,
    cl.nombre                                                AS cliente_nombre,
    cl.tipo                                                  AS cliente_tipo,
    cl.identificacion                                        AS cliente_identificacion,
    gc.nombre                                                AS grupo_cliente,
    su.id                                                    AS sucursal_id,
    su.nombre                                                AS sucursal_nombre,
    ci.nombre                                                AS ciudad_sucursal,
    COALESCE(cat_raiz.nombre, cat_sub.nombre)                AS categoria,
    CASE WHEN cat_raiz.id IS NOT NULL
         THEN cat_sub.nombre ELSE NULL END                   AS subcategoria,
    p.id                                                     AS producto_id,
    p.codigo_sku                                             AS sku,
    p.nombre                                                 AS producto,
    p.unidad_medida,
    p.precio_oficial,
    bo.id                                                    AS bodega_id,
    bo.nombre                                                AS bodega_nombre,
    bo.tipo                                                  AS tipo_bodega,
    lp.cantidad,
    lp.precio_unitario,
    lp.descuento_pct,
    lp.descuento_monto,
    lp.subtotal,
    CASE WHEN lp.promocion_id IS NOT NULL THEN 1 ELSE 0 END  AS con_promocion,
    fa.id                                                    AS factura_id,
    fa.numero_fiscal,
    fa.estado                                                AS estado_factura,
    fa.fecha_emision,
    fa.impuesto_pct
FROM linea_pedido lp
JOIN pedido            pd         ON pd.id        = lp.pedido_id
JOIN cliente           cl         ON cl.id        = pd.cliente_id
LEFT JOIN grupo_cliente gc        ON gc.id        = cl.grupo_cliente_id
JOIN sucursal          su         ON su.id        = pd.sucursal_id
LEFT JOIN ciudad       ci         ON ci.id        = su.ciudad_id
JOIN producto          p          ON p.id         = lp.producto_id
LEFT JOIN categoria    cat_sub    ON cat_sub.id   = p.categoria_id
LEFT JOIN categoria    cat_raiz   ON cat_raiz.id  = cat_sub.padre_id
JOIN bodega            bo         ON bo.id        = lp.bodega_id
LEFT JOIN factura      fa         ON fa.pedido_id = pd.id
ORDER BY lp.id
"""

_SQL_UPSERT = """
INSERT INTO linea_venta (
    linea_id, pedido_id, numero_pedido, fecha_pedido, fecha_requerida,
    estado_pedido, moneda,
    cliente_id, cliente_nombre, cliente_tipo, cliente_identificacion, grupo_cliente,
    sucursal_id, sucursal_nombre, ciudad_sucursal,
    categoria, subcategoria,
    producto_id, sku, producto, unidad_medida, precio_oficial,
    bodega_id, bodega_nombre, tipo_bodega,
    cantidad, precio_unitario, descuento_pct, descuento_monto, subtotal, con_promocion,
    factura_id, numero_fiscal, estado_factura, fecha_emision, impuesto_pct
) VALUES (
    %(linea_id)s, %(pedido_id)s, %(numero_pedido)s, %(fecha_pedido)s, %(fecha_requerida)s,
    %(estado_pedido)s, %(moneda)s,
    %(cliente_id)s, %(cliente_nombre)s, %(cliente_tipo)s, %(cliente_identificacion)s, %(grupo_cliente)s,
    %(sucursal_id)s, %(sucursal_nombre)s, %(ciudad_sucursal)s,
    %(categoria)s, %(subcategoria)s,
    %(producto_id)s, %(sku)s, %(producto)s, %(unidad_medida)s, %(precio_oficial)s,
    %(bodega_id)s, %(bodega_nombre)s, %(tipo_bodega)s,
    %(cantidad)s, %(precio_unitario)s, %(descuento_pct)s, %(descuento_monto)s, %(subtotal)s, %(con_promocion)s,
    %(factura_id)s, %(numero_fiscal)s, %(estado_factura)s, %(fecha_emision)s, %(impuesto_pct)s
)
ON DUPLICATE KEY UPDATE
    numero_pedido          = VALUES(numero_pedido),
    fecha_pedido           = VALUES(fecha_pedido),
    fecha_requerida        = VALUES(fecha_requerida),
    estado_pedido          = VALUES(estado_pedido),
    cliente_nombre         = VALUES(cliente_nombre),
    cliente_tipo           = VALUES(cliente_tipo),
    cliente_identificacion = VALUES(cliente_identificacion),
    grupo_cliente          = VALUES(grupo_cliente),
    sucursal_nombre        = VALUES(sucursal_nombre),
    ciudad_sucursal        = VALUES(ciudad_sucursal),
    categoria              = VALUES(categoria),
    subcategoria           = VALUES(subcategoria),
    sku                    = VALUES(sku),
    producto               = VALUES(producto),
    unidad_medida          = VALUES(unidad_medida),
    precio_oficial         = VALUES(precio_oficial),
    bodega_nombre          = VALUES(bodega_nombre),
    tipo_bodega            = VALUES(tipo_bodega),
    cantidad               = VALUES(cantidad),
    precio_unitario        = VALUES(precio_unitario),
    descuento_pct          = VALUES(descuento_pct),
    descuento_monto        = VALUES(descuento_monto),
    subtotal               = VALUES(subtotal),
    con_promocion          = VALUES(con_promocion),
    factura_id             = VALUES(factura_id),
    numero_fiscal          = VALUES(numero_fiscal),
    estado_factura         = VALUES(estado_factura),
    fecha_emision          = VALUES(fecha_emision),
    impuesto_pct           = VALUES(impuesto_pct),
    fecha_carga            = NOW()
"""


def cargar(src, tgt, sql: str, params: tuple = ()):
    src_cur = src.cursor(dictionary=True)
    src_cur.execute(sql, params)
    tgt_cur = tgt.cursor()
    total = 0
    while True:
        batch = src_cur.fetchmany(BATCH_SIZE)
        if not batch:
            break
        tgt_cur.executemany(_SQL_UPSERT, batch)
        tgt.commit()
        total += len(batch)
        print(f"  {total} filas procesadas...", end="\r")
    src_cur.close()
    tgt_cur.close()
    print(f"  {total} filas upserted          ")
    return total


def main():
    p = argparse.ArgumentParser(description="Fill linea_venta en comercialdesnormalized")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--full",  action="store_true", help="Carga completa")
    mode.add_argument("--desde", type=date.fromisoformat, metavar="YYYY-MM-DD")
    p.add_argument("--hasta", type=date.fromisoformat, default=date.today(), metavar="YYYY-MM-DD")
    args = p.parse_args()

    src = conn_source()
    tgt = conn_target()
    print(f"Origen : {os.getenv('DB_NAME')}@{_BASE['host']}")
    print(f"Destino: {os.getenv('DB_NAME_DESNORM')}@{_BASE['host']}")

    if args.full:
        print("\nModo: carga completa")
        cargar(src, tgt, _SQL_SELECT_FULL)
    else:
        print(f"\nModo: incremental  {args.desde} - {args.hasta}")
        cargar(src, tgt, _SQL_SELECT_RANGO, (args.desde, args.hasta))

    src.close()
    tgt.close()
    print("Completado")


if __name__ == "__main__":
    main()
