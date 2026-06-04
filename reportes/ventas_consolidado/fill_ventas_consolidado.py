"""
reportes/ventas_consolidado/fill_ventas_consolidado.py
Lee de 'comercial' e inserta en 'comercialdesnormalized.ventas_consolidado'.

Uso:
    python reportes/ventas_consolidado/fill_ventas_consolidado.py --full
    python reportes/ventas_consolidado/fill_ventas_consolidado.py --desde 2025-01-01
    python reportes/ventas_consolidado/fill_ventas_consolidado.py --desde 2025-01-01 --hasta 2025-12-31
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


_SQL_SELECT_FULL = """
SELECT lp.id AS linea_id, lp.pedido_id, pd.numero_pedido, pd.fecha_pedido,
    pd.estado AS estado_pedido, pd.moneda, pd.cliente_id,
    su.id AS sucursal_id, su.nombre AS sucursal_nombre,
    pa.id AS pais_id, pa.nombre AS pais_nombre,
    lp.subtotal AS subtotal_linea
FROM linea_pedido lp
JOIN pedido   pd ON pd.id = lp.pedido_id
JOIN sucursal su ON su.id = pd.sucursal_id
JOIN ciudad   ci ON ci.id = su.ciudad_id
JOIN pais     pa ON pa.id = ci.pais_id
ORDER BY lp.id
"""

_SQL_SELECT_RANGO = """
SELECT lp.id AS linea_id, lp.pedido_id, pd.numero_pedido, pd.fecha_pedido,
    pd.estado AS estado_pedido, pd.moneda, pd.cliente_id,
    su.id AS sucursal_id, su.nombre AS sucursal_nombre,
    pa.id AS pais_id, pa.nombre AS pais_nombre,
    lp.subtotal AS subtotal_linea
FROM linea_pedido lp
JOIN pedido   pd ON pd.id = lp.pedido_id
JOIN sucursal su ON su.id = pd.sucursal_id
JOIN ciudad   ci ON ci.id = su.ciudad_id
JOIN pais     pa ON pa.id = ci.pais_id
WHERE pd.fecha_pedido >= %s
  AND pd.fecha_pedido <  DATE_ADD(%s, INTERVAL 1 DAY)
ORDER BY lp.id
"""

_SQL_UPSERT = """
INSERT INTO ventas_consolidado (
    linea_id, pedido_id, numero_pedido, fecha_pedido, estado_pedido, moneda,
    cliente_id, sucursal_id, sucursal_nombre, pais_id, pais_nombre, subtotal_linea
) VALUES (
    %(linea_id)s, %(pedido_id)s, %(numero_pedido)s, %(fecha_pedido)s,
    %(estado_pedido)s, %(moneda)s,
    %(cliente_id)s, %(sucursal_id)s, %(sucursal_nombre)s,
    %(pais_id)s, %(pais_nombre)s, %(subtotal_linea)s
)
ON DUPLICATE KEY UPDATE
    numero_pedido=VALUES(numero_pedido), fecha_pedido=VALUES(fecha_pedido),
    estado_pedido=VALUES(estado_pedido), sucursal_nombre=VALUES(sucursal_nombre),
    pais_nombre=VALUES(pais_nombre), subtotal_linea=VALUES(subtotal_linea),
    fecha_carga=NOW()
"""


def cargar(src, tgt, sql, params=()):
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
    p = argparse.ArgumentParser(description="Fill ventas_consolidado")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--full",  action="store_true")
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
