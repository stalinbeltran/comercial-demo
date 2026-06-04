"""
reportes/ventas_sucursal_comparativo/fill_resumen_ventas_sucursal_dia.py
Lee de 'comercialdesnormalized.ventas_consolidado' y agrega por DÍA
en 'comercialaggregated.resumen_ventas_sucursal_dia'.

Requiere que ventas_consolidado esté poblado previamente.

Uso:
    python reportes/ventas_sucursal_comparativo/fill_resumen_ventas_sucursal_dia.py
    python reportes/ventas_sucursal_comparativo/fill_resumen_ventas_sucursal_dia.py --desde 2025-01-01 --hasta 2025-12-31
    python reportes/ventas_sucursal_comparativo/fill_resumen_ventas_sucursal_dia.py --sucursal 3
    python reportes/ventas_sucursal_comparativo/fill_resumen_ventas_sucursal_dia.py --todos
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


# Agrega por día — todas las sucursales como una sola fila por día (sucursal_id = 0)
_SQL_TOTAL = """
SELECT
    DATE(fecha_pedido)              AS fecha,
    ROUND(SUM(subtotal_linea), 2)   AS total_ventas,
    COUNT(DISTINCT pedido_id)       AS total_pedidos,
    COUNT(DISTINCT cliente_id)      AS clientes_activos
FROM ventas_consolidado
WHERE estado_pedido NOT IN ('cancelado', 'anulado')
  AND fecha_pedido >= %s
  AND fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
GROUP BY DATE(fecha_pedido)
"""

# Agrega por día para una sucursal específica
_SQL_POR_SUCURSAL = """
SELECT
    DATE(fecha_pedido)              AS fecha,
    sucursal_id,
    sucursal_nombre,
    pais_nombre,
    ROUND(SUM(subtotal_linea), 2)   AS total_ventas,
    COUNT(DISTINCT pedido_id)       AS total_pedidos,
    COUNT(DISTINCT cliente_id)      AS clientes_activos
FROM ventas_consolidado
WHERE estado_pedido NOT IN ('cancelado', 'anulado')
  AND fecha_pedido >= %s
  AND fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
  AND sucursal_id = %s
GROUP BY DATE(fecha_pedido), sucursal_id, sucursal_nombre, pais_nombre
"""

_SQL_SUCURSALES = """
SELECT DISTINCT sucursal_id AS id, sucursal_nombre AS nombre
FROM ventas_consolidado WHERE sucursal_id IS NOT NULL ORDER BY sucursal_id
"""

_SQL_UPSERT = """
INSERT INTO resumen_ventas_sucursal_dia (
    fecha, sucursal_id, sucursal_nombre, pais_nombre,
    total_ventas, total_pedidos, clientes_activos
) VALUES (
    %(fecha)s, %(sucursal_id)s, %(sucursal_nombre)s, %(pais_nombre)s,
    %(total_ventas)s, %(total_pedidos)s, %(clientes_activos)s
)
ON DUPLICATE KEY UPDATE
    sucursal_nombre  = VALUES(sucursal_nombre),
    pais_nombre      = VALUES(pais_nombre),
    total_ventas     = VALUES(total_ventas),
    total_pedidos    = VALUES(total_pedidos),
    clientes_activos = VALUES(clientes_activos),
    fecha_actualizacion = NOW()
"""


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
    rows = [{**r, "sucursal_id": 0, "sucursal_nombre": None, "pais_nombre": None}
            for r in cur.fetchall()]
    cur.close()
    return _upsert(tgt, rows)


def fill_sucursal(src, tgt, desde: date, hasta: date,
                  sucursal_id: int, sucursal_nombre: str) -> int:
    cur = src.cursor(dictionary=True)
    cur.execute(_SQL_POR_SUCURSAL, (desde, hasta, sucursal_id))
    rows = cur.fetchall()
    cur.close()
    return _upsert(tgt, rows)


def get_sucursales(src) -> list:
    cur = src.cursor(dictionary=True)
    cur.execute(_SQL_SUCURSALES)
    rows = cur.fetchall()
    cur.close()
    return rows


def main():
    hoy = date.today()
    p = argparse.ArgumentParser(description="Fill resumen_ventas_sucursal_dia")
    p.add_argument("--desde",    type=date.fromisoformat, default=hoy.replace(day=1), metavar="YYYY-MM-DD")
    p.add_argument("--hasta",    type=date.fromisoformat, default=hoy, metavar="YYYY-MM-DD")
    p.add_argument("--sucursal", type=int, default=None, metavar="ID")
    p.add_argument("--todos",    action="store_true")
    args = p.parse_args()

    src = conn_source()
    tgt = conn_target()
    print(f"Origen : {os.getenv('DB_NAME_DESNORM')}@{_BASE['host']}")
    print(f"Destino: {os.getenv('DB_NAME_AGG')}@{_BASE['host']}")
    print(f"Periodo: {args.desde} - {args.hasta}\n")

    if args.todos:
        sucursales = get_sucursales(src)
        total = 0
        for s in sucursales:
            n = fill_sucursal(src, tgt, args.desde, args.hasta, s["id"], s["nombre"])
            print(f"  sucursal {s['id']:>3} — {s['nombre']:<30} {n:>3} filas")
            total += n
        print(f"\n  total: {total} filas")
    elif args.sucursal is not None:
        sucursales = get_sucursales(src)
        match = next((s for s in sucursales if s["id"] == args.sucursal), None)
        if not match:
            print(f"ERROR: sucursal {args.sucursal} no encontrada")
            sys.exit(1)
        n = fill_sucursal(src, tgt, args.desde, args.hasta, match["id"], match["nombre"])
        print(f"  {n} filas upserted")
    else:
        print("Modo: total (todas las sucursales, sucursal_id = 0)")
        n = fill_total(src, tgt, args.desde, args.hasta)
        print(f"  {n} filas upserted")

    src.close()
    tgt.close()
    print("\nCompletado")


if __name__ == "__main__":
    main()
