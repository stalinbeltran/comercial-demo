"""
scripts/fill_resumen_ventas.py
Lee de 'comercialdesnormalized.linea_venta' e inserta en 'comercialaggregated.resumen_ventas'.

Modos:
    # Total de todas las sucursales (sucursal_id = 0), mes actual
    python scripts/fill_resumen_ventas.py

    # Solo una sucursal
    python scripts/fill_resumen_ventas.py --sucursal 3

    # Todas las sucursales individualmente
    python scripts/fill_resumen_ventas.py --todos

    # Con rango de fechas explícito (aplica a cualquier modo)
    python scripts/fill_resumen_ventas.py --desde 2025-01-01 --hasta 2025-12-31
    python scripts/fill_resumen_ventas.py --todos --desde 2025-01-01 --hasta 2025-12-31
"""

import os
import sys
import argparse
from datetime import date

import mysql.connector
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

# ─── CONEXIONES ───────────────────────────────────────────────────────────────

_BASE = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "charset":  "utf8mb4",
}

def conn_source():
    return mysql.connector.connect(**_BASE, database=os.getenv("DB_NAME_DESNORM"))

def conn_target():
    return mysql.connector.connect(**_BASE, database=os.getenv("DB_NAME_AGG"))


# ─── QUERIES ──────────────────────────────────────────────────────────────────

# Agrega todas las sucursales en una sola fila por producto (sucursal_id = 0)
_SQL_TOTAL = """
SELECT
    categoria,
    subcategoria,
    producto_id,
    sku,
    producto,
    SUM(cantidad)                   AS unidades_vendidas,
    ROUND(AVG(precio_unitario), 4)  AS precio_promedio,
    ROUND(SUM(descuento_monto), 2)  AS total_descuentos,
    ROUND(SUM(subtotal), 2)         AS ingresos_netos,
    COUNT(DISTINCT pedido_id)       AS num_pedidos
FROM linea_venta
WHERE estado_pedido NOT IN ('cancelado', 'anulado', 'borrador')
  AND fecha_pedido >= %s
  AND fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
GROUP BY
    categoria, subcategoria,
    producto_id, sku, producto
"""

# Agrega una sucursal específica
_SQL_POR_SUCURSAL = """
SELECT
    categoria,
    subcategoria,
    producto_id,
    sku,
    producto,
    sucursal_id,
    sucursal_nombre,
    SUM(cantidad)                   AS unidades_vendidas,
    ROUND(AVG(precio_unitario), 4)  AS precio_promedio,
    ROUND(SUM(descuento_monto), 2)  AS total_descuentos,
    ROUND(SUM(subtotal), 2)         AS ingresos_netos,
    COUNT(DISTINCT pedido_id)       AS num_pedidos
FROM linea_venta
WHERE estado_pedido NOT IN ('cancelado', 'anulado', 'borrador')
  AND fecha_pedido >= %s
  AND fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
  AND sucursal_id = %s
GROUP BY
    categoria, subcategoria,
    producto_id, sku, producto,
    sucursal_id, sucursal_nombre
"""

_SQL_UPSERT = """
INSERT INTO resumen_ventas (
    periodo_inicio, periodo_fin, sucursal_id, sucursal_nombre,
    categoria, subcategoria, producto_id, sku, producto,
    unidades_vendidas, precio_promedio, total_descuentos, ingresos_netos, num_pedidos
) VALUES (
    %(periodo_inicio)s, %(periodo_fin)s, %(sucursal_id)s, %(sucursal_nombre)s,
    %(categoria)s, %(subcategoria)s, %(producto_id)s, %(sku)s, %(producto)s,
    %(unidades_vendidas)s, %(precio_promedio)s, %(total_descuentos)s,
    %(ingresos_netos)s, %(num_pedidos)s
)
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

_SQL_SUCURSALES = """
SELECT DISTINCT sucursal_id AS id, sucursal_nombre AS nombre
FROM linea_venta
WHERE sucursal_id IS NOT NULL
ORDER BY sucursal_id
"""


# ─── LÓGICA ───────────────────────────────────────────────────────────────────

def _upsert(tgt, rows: list) -> int:
    if not rows:
        return 0
    cur = tgt.cursor()
    cur.executemany(_SQL_UPSERT, rows)
    tgt.commit()
    n = cur.rowcount
    cur.close()
    return n


def fill_total(src, tgt, desde: date, hasta: date) -> int:
    cur = src.cursor(dictionary=True)
    cur.execute(_SQL_TOTAL, (desde, hasta))
    rows = [
        {**r, "periodo_inicio": desde, "periodo_fin": hasta,
         "sucursal_id": 0, "sucursal_nombre": None}
        for r in cur.fetchall()
    ]
    cur.close()
    return _upsert(tgt, rows)


def fill_sucursal(src, tgt, desde: date, hasta: date,
                  sucursal_id: int, sucursal_nombre: str) -> int:
    cur = src.cursor(dictionary=True)
    cur.execute(_SQL_POR_SUCURSAL, (desde, hasta, sucursal_id))
    rows = [
        {**r, "periodo_inicio": desde, "periodo_fin": hasta}
        for r in cur.fetchall()
    ]
    cur.close()
    return _upsert(tgt, rows)


def get_sucursales(src) -> list:
    cur = src.cursor(dictionary=True)
    cur.execute(_SQL_SUCURSALES)
    rows = cur.fetchall()
    cur.close()
    return rows


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    hoy = date.today()
    p = argparse.ArgumentParser(description="Fill resumen_ventas en comercialaggregated")
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

    src = conn_source()
    tgt = conn_target()

    print(f"Origen : {os.getenv('DB_NAME')}@{_BASE['host']}")
    print(f"Destino: {os.getenv('DB_NAME_AGG')}@{_BASE['host']}")
    print(f"Período: {args.desde} → {args.hasta}\n")

    if args.todos:
        sucursales = get_sucursales(src)
        print(f"Modo: todas las sucursales ({len(sucursales)} encontradas)")
        total = 0
        for s in sucursales:
            n = fill_sucursal(src, tgt, args.desde, args.hasta, s["id"], s["nombre"])
            print(f"  sucursal {s['id']:>3} — {s['nombre']:<30} {n:>4} filas upserted")
            total += n
        print(f"\n  total: {total} filas")

    elif args.sucursal is not None:
        sucursales = get_sucursales(src)
        match = next((s for s in sucursales if s["id"] == args.sucursal), None)
        if not match:
            print(f"ERROR: sucursal {args.sucursal} no encontrada o inactiva")
            sys.exit(1)
        print(f"Modo: sucursal {match['id']} — {match['nombre']}")
        n = fill_sucursal(src, tgt, args.desde, args.hasta, match["id"], match["nombre"])
        print(f"  {n} filas upserted")

    else:
        print("Modo: total (todas las sucursales agregadas, sucursal_id = 0)")
        n = fill_total(src, tgt, args.desde, args.hasta)
        print(f"  {n} filas upserted")

    src.close()
    tgt.close()
    print("\n✓ Completado")


if __name__ == "__main__":
    main()
