"""
scripts/fill_reporte_ventas.py — Llena reporte_ventas_producto.

Modos de uso:
    # Total de todas las sucursales (sucursal_id = 0), mes actual
    python scripts/fill_reporte_ventas.py

    # Solo una sucursal
    python scripts/fill_reporte_ventas.py --sucursal 3

    # Todas las sucursales individualmente (una pasada por cada una)
    python scripts/fill_reporte_ventas.py --todos

    # Con rango de fechas explícito
    python scripts/fill_reporte_ventas.py --desde 2025-01-01 --hasta 2025-12-31
    python scripts/fill_reporte_ventas.py --todos --desde 2025-01-01 --hasta 2025-12-31
"""

import os
import sys
import argparse
from datetime import date, timedelta

import mysql.connector
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset":  "utf8mb4",
}

# ─── QUERIES ──────────────────────────────────────────────────────────────────

# Mismos JOINs y WHERE del reporte de la API.
# Agrega p.id y, opcionalmente, sucursal_id / sucursal_nombre al SELECT.

_SQL_TOTAL = """
SELECT
    COALESCE(cat_raiz.nombre, cat_sub.nombre)              AS categoria,
    CASE WHEN cat_raiz.id IS NOT NULL
         THEN cat_sub.nombre
         ELSE NULL END                                     AS subcategoria,
    p.id                                                   AS producto_id,
    p.codigo_sku                                           AS sku,
    p.nombre                                               AS producto,
    SUM(lp.cantidad)                                       AS unidades_vendidas,
    ROUND(AVG(lp.precio_unitario), 4)                      AS precio_promedio,
    ROUND(SUM(lp.descuento_monto), 2)                      AS total_descuentos,
    ROUND(SUM(lp.subtotal), 2)                             AS ingresos_netos,
    COUNT(DISTINCT lp.pedido_id)                           AS num_pedidos
FROM linea_pedido lp
JOIN pedido       pd         ON pd.id        = lp.pedido_id
JOIN producto     p          ON p.id         = lp.producto_id
LEFT JOIN categoria cat_sub  ON cat_sub.id   = p.categoria_id
LEFT JOIN categoria cat_raiz ON cat_raiz.id  = cat_sub.padre_id
WHERE pd.estado NOT IN ('cancelado', 'anulado', 'borrador')
  AND pd.fecha_pedido >= %s
  AND pd.fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
GROUP BY
    cat_raiz.id, cat_raiz.nombre,
    cat_sub.id,  cat_sub.nombre,
    p.id,        p.codigo_sku,  p.nombre
"""

_SQL_POR_SUCURSAL = """
SELECT
    COALESCE(cat_raiz.nombre, cat_sub.nombre)              AS categoria,
    CASE WHEN cat_raiz.id IS NOT NULL
         THEN cat_sub.nombre
         ELSE NULL END                                     AS subcategoria,
    p.id                                                   AS producto_id,
    p.codigo_sku                                           AS sku,
    p.nombre                                               AS producto,
    pd.sucursal_id                                         AS sucursal_id,
    s.nombre                                               AS sucursal_nombre,
    SUM(lp.cantidad)                                       AS unidades_vendidas,
    ROUND(AVG(lp.precio_unitario), 4)                      AS precio_promedio,
    ROUND(SUM(lp.descuento_monto), 2)                      AS total_descuentos,
    ROUND(SUM(lp.subtotal), 2)                             AS ingresos_netos,
    COUNT(DISTINCT lp.pedido_id)                           AS num_pedidos
FROM linea_pedido lp
JOIN pedido       pd         ON pd.id        = lp.pedido_id
JOIN producto     p          ON p.id         = lp.producto_id
LEFT JOIN sucursal s         ON s.id         = pd.sucursal_id
LEFT JOIN categoria cat_sub  ON cat_sub.id   = p.categoria_id
LEFT JOIN categoria cat_raiz ON cat_raiz.id  = cat_sub.padre_id
WHERE pd.estado NOT IN ('cancelado', 'anulado', 'borrador')
  AND pd.fecha_pedido >= %s
  AND pd.fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
  AND pd.sucursal_id = %s
GROUP BY
    cat_raiz.id, cat_raiz.nombre,
    cat_sub.id,  cat_sub.nombre,
    p.id,        p.codigo_sku,  p.nombre,
    pd.sucursal_id, s.nombre
"""

_SQL_INSERT = """
INSERT INTO reporte_ventas_producto
    (periodo_inicio, periodo_fin, sucursal_id, sucursal_nombre,
     categoria, subcategoria, producto_id, sku, producto,
     unidades_vendidas, precio_promedio, total_descuentos, ingresos_netos, num_pedidos)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    sucursal_nombre     = VALUES(sucursal_nombre),
    categoria           = VALUES(categoria),
    subcategoria        = VALUES(subcategoria),
    sku                 = VALUES(sku),
    producto            = VALUES(producto),
    unidades_vendidas   = VALUES(unidades_vendidas),
    precio_promedio     = VALUES(precio_promedio),
    total_descuentos    = VALUES(total_descuentos),
    ingresos_netos      = VALUES(ingresos_netos),
    num_pedidos         = VALUES(num_pedidos),
    fecha_actualizacion = NOW()
"""

_SQL_SUCURSALES_ACTIVAS = "SELECT id, nombre FROM sucursal WHERE activa = 1 ORDER BY id"


# ─── LÓGICA ───────────────────────────────────────────────────────────────────

def fill_total(conn, desde: date, hasta: date):
    """Agrega ventas de todas las sucursales en una sola fila por producto."""
    cur = conn.cursor(dictionary=True)
    cur.execute(_SQL_TOTAL, (desde, hasta))
    rows = cur.fetchall()
    cur.close()

    if not rows:
        print("  sin datos para el período indicado")
        return 0

    registros = [
        (desde, hasta, 0, None,
         r["categoria"], r["subcategoria"],
         r["producto_id"], r["sku"], r["producto"],
         r["unidades_vendidas"], r["precio_promedio"],
         r["total_descuentos"], r["ingresos_netos"], r["num_pedidos"])
        for r in rows
    ]
    cur = conn.cursor()
    cur.executemany(_SQL_INSERT, registros)
    conn.commit()
    inserted = cur.rowcount
    cur.close()
    return inserted


def fill_sucursal(conn, desde: date, hasta: date, sucursal_id: int, sucursal_nombre: str):
    """Agrega ventas de una sucursal específica."""
    cur = conn.cursor(dictionary=True)
    cur.execute(_SQL_POR_SUCURSAL, (desde, hasta, sucursal_id))
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return 0

    registros = [
        (desde, hasta, sucursal_id, sucursal_nombre,
         r["categoria"], r["subcategoria"],
         r["producto_id"], r["sku"], r["producto"],
         r["unidades_vendidas"], r["precio_promedio"],
         r["total_descuentos"], r["ingresos_netos"], r["num_pedidos"])
        for r in rows
    ]
    cur = conn.cursor()
    cur.executemany(_SQL_INSERT, registros)
    conn.commit()
    inserted = cur.rowcount
    cur.close()
    return inserted


def get_sucursales(conn) -> list[dict]:
    cur = conn.cursor(dictionary=True)
    cur.execute(_SQL_SUCURSALES_ACTIVAS)
    rows = cur.fetchall()
    cur.close()
    return rows


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    hoy = date.today()
    p = argparse.ArgumentParser(description="Fill reporte_ventas_producto")
    p.add_argument("--desde",    type=date.fromisoformat, default=hoy.replace(day=1),
                   metavar="YYYY-MM-DD", help="Inicio del período (default: 1° del mes actual)")
    p.add_argument("--hasta",    type=date.fromisoformat, default=hoy,
                   metavar="YYYY-MM-DD", help="Fin del período (default: hoy)")
    p.add_argument("--sucursal", type=int, default=None,
                   metavar="ID",       help="Llenar solo para esta sucursal")
    p.add_argument("--todos",    action="store_true",
                   help="Llenar individualmente para cada sucursal activa")
    return p.parse_args()


def main():
    args = parse_args()

    if args.desde > args.hasta:
        print("ERROR: --desde no puede ser mayor que --hasta")
        sys.exit(1)

    conn = mysql.connector.connect(**DB_CONFIG)
    print(f"Conectado a {DB_CONFIG['database']}@{DB_CONFIG['host']}")
    print(f"Período: {args.desde} → {args.hasta}\n")

    if args.todos:
        sucursales = get_sucursales(conn)
        print(f"Modo: todas las sucursales ({len(sucursales)} encontradas)")
        total = 0
        for s in sucursales:
            n = fill_sucursal(conn, args.desde, args.hasta, s["id"], s["nombre"])
            print(f"  sucursal {s['id']:>3} — {s['nombre']:<30} {n:>4} filas upserted")
            total += n
        print(f"\n  total filas: {total}")

    elif args.sucursal is not None:
        sucursales = get_sucursales(conn)
        match = next((s for s in sucursales if s["id"] == args.sucursal), None)
        if not match:
            print(f"ERROR: sucursal {args.sucursal} no encontrada o inactiva")
            sys.exit(1)
        print(f"Modo: sucursal {match['id']} — {match['nombre']}")
        n = fill_sucursal(conn, args.desde, args.hasta, match["id"], match["nombre"])
        print(f"  {n} filas upserted")

    else:
        print("Modo: total (todas las sucursales agregadas)")
        n = fill_total(conn, args.desde, args.hasta)
        print(f"  {n} filas upserted")

    conn.close()
    print("\n✓ Completado")


if __name__ == "__main__":
    main()
