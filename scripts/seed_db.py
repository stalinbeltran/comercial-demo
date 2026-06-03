"""
scripts/seed_db.py — Seed para ERP Comercial Multi-sucursal, Panamá.

Uso:
    python scripts/seed_db.py
    python scripts/seed_db.py --reset
    python scripts/seed_db.py --counts pedidos=300 clientes=200
"""

import os
import sys
import argparse
import random
from datetime import date, datetime, timedelta

import mysql.connector
from faker import Faker
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv()

fake = Faker("es_MX")
Faker.seed(42)
random.seed(42)

# ─── CONEXIÓN ─────────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "charset":  "utf8mb4",
}

# ─── PARÁMETROS EDITABLES ─────────────────────────────────────────────────────
COUNTS = {
    "sucursales":             5,
    "bodegas_por_sucursal":   2,
    "clientes":             100,
    "dir_entrega_max":        3,
    "precios_especiales":    25,
    "promociones":           12,
    "conductores":           10,
    "camiones":               8,
    "rutas":                  6,
    "recorridos":            20,
    "paradas_por_recorrido":  4,
    "pedidos":              150,
    "lineas_max":             6,
}

ITBMS = 0.07  # Impuesto de Transferencia de Bienes Muebles y Servicios

# ─── DATOS FIJOS PANAMÁ ───────────────────────────────────────────────────────
CIUDADES_PANAMA = [
    ("Ciudad de Panamá", "0801"),
    ("San Miguelito",    "0802"),
    ("Colón",            "0201"),
    ("David",            "0401"),
    ("Santiago",         "0701"),
    ("La Chorrera",      "0101"),
    ("Chitré",           "0601"),
    ("Penonomé",         "0301"),
    ("Aguadulce",        "0302"),
    ("Bocas del Toro",   "1001"),
    ("Arraiján",         "0102"),
    ("Capira",           "0103"),
]

GRUPOS = [
    ("Corporativo", "Empresas grandes con contrato anual"),
    ("Mayorista",   "Clientes con compras en volumen"),
    ("Minorista",   "Clientes particulares y tiendas pequeñas"),
    ("Gobierno",    "Entidades y dependencias gubernamentales"),
]

# (nombre, descripcion, padre_nombre)
CATEGORIAS = [
    ("Electrónica",         "Equipos y dispositivos electrónicos",   None),
    ("Papelería y Oficina", "Artículos de oficina y papelería",       None),
    ("Herramientas",        "Herramientas manuales y eléctricas",     None),
    ("Limpieza e Higiene",  "Productos de limpieza e higiene",        None),
    ("Alimentos",           "Alimentos no perecederos",               None),
    ("Computadoras",        "Equipos de cómputo portátiles y fijos",  "Electrónica"),
    ("Teléfonos",           "Teléfonos móviles y VoIP",               "Electrónica"),
    ("Impresoras",          "Impresoras y multifuncionales",          "Electrónica"),
    ("Accesorios TI",       "Accesorios y periféricos",               "Electrónica"),
    ("Papel",               "Papel y cuadernos",                      "Papelería y Oficina"),
    ("Escritura",           "Instrumentos de escritura",              "Papelería y Oficina"),
    ("Herr. Manuales",      "Herramientas de mano",                   "Herramientas"),
    ("Herr. Eléctricas",    "Herramientas con motor eléctrico",       "Herramientas"),
    ("Limpieza Sup.",       "Limpieza de superficies",                "Limpieza e Higiene"),
    ("Higiene Personal",    "Productos de higiene personal",          "Limpieza e Higiene"),
    ("Granos",              "Granos y cereales",                      "Alimentos"),
    ("Conservas",           "Alimentos enlatados y conservas",        "Alimentos"),
]

# (sku, nombre, subcategoria, precio_usd, peso_kg, vol_m3)
PRODUCTOS = [
    ("LAP-I5-14",  "Laptop 14\" Core i5 8GB",         "Computadoras",    599.99, 2.10, 0.0050),
    ("LAP-I7-15",  "Laptop 15.6\" Core i7 16GB",      "Computadoras",    899.99, 2.40, 0.0060),
    ("DES-I5-MT",  "PC Escritorio Core i5",            "Computadoras",    449.99, 8.00, 0.0200),
    ("TEL-A128",   "Smartphone 128GB Android",          "Teléfonos",       249.99, 0.19, 0.0002),
    ("TEL-A256P",  "Smartphone 256GB Pro",              "Teléfonos",       449.99, 0.21, 0.0002),
    ("TEL-IP-OF",  "Teléfono IP Oficina",               "Teléfonos",        89.99, 0.50, 0.0010),
    ("IMP-MF-INK", "Impresora Multifuncional Tinta",    "Impresoras",      129.99, 4.50, 0.0100),
    ("IMP-LAS-B",  "Impresora Láser Mono",              "Impresoras",      199.99, 6.00, 0.0150),
    ("ACC-MOUSE",  "Mouse Inalámbrico",                 "Accesorios TI",    19.99, 0.10, 0.0002),
    ("ACC-KEYBW",  "Teclado Bluetooth",                 "Accesorios TI",    34.99, 0.40, 0.0005),
    ("ACC-MON24",  "Monitor 24\" FHD",                  "Accesorios TI",   179.99, 4.00, 0.0080),
    ("ACC-WCAM",   "Webcam HD 1080p",                   "Accesorios TI",    49.99, 0.15, 0.0003),
    ("ACC-HUB7",   "Hub USB-C 7 puertos",               "Accesorios TI",    29.99, 0.12, 0.0002),
    ("ACC-HDMI2",  "Cable HDMI 2m",                     "Accesorios TI",     8.99, 0.08, 0.0001),
    ("PAP-A4-75",  "Resma Papel A4 75g 500h",           "Papel",             5.99, 2.30, 0.0030),
    ("PAP-LT-75",  "Resma Papel Carta 75g 500h",        "Papel",             5.49, 2.20, 0.0030),
    ("CUA-U-100",  "Cuaderno universitario 100h",       "Papel",             2.49, 0.20, 0.0003),
    ("CUA-A4-80",  "Block rayado A4 80h",               "Papel",             1.99, 0.15, 0.0002),
    ("BOL-AZ-12",  "Bolígrafos azul caja 12",           "Escritura",         3.99, 0.08, 0.0001),
    ("BOL-NG-12",  "Bolígrafos negro caja 12",          "Escritura",         3.99, 0.08, 0.0001),
    ("MAR-PM-4",   "Marcadores permanentes set 4",      "Escritura",         5.99, 0.12, 0.0002),
    ("LAP-HB-12",  "Lápices HB caja 12",               "Escritura",         2.99, 0.07, 0.0001),
    ("RES-PAS-5",  "Resaltadores pastel set 5",         "Escritura",         4.99, 0.10, 0.0001),
    ("TIJ-OF-21",  "Tijeras de oficina 21cm",           "Escritura",         3.49, 0.09, 0.0001),
    ("HER-MAR-20", "Martillo 20oz mango fibra",         "Herr. Manuales",   18.99, 0.60, 0.0010),
    ("HER-DST-8",  "Set destornilladores 8 pzs",        "Herr. Manuales",   14.99, 0.40, 0.0008),
    ("HER-LLA-12", "Llave ajustable 12\"",              "Herr. Manuales",   12.99, 0.45, 0.0006),
    ("HER-CIN-5",  "Cinta métrica 5m",                  "Herr. Manuales",    7.99, 0.12, 0.0002),
    ("HER-NIV-60", "Nivel de burbuja 60cm",             "Herr. Manuales",    9.99, 0.35, 0.0005),
    ("HER-ALI-8",  "Alicate universal 8\"",             "Herr. Manuales",   11.99, 0.25, 0.0004),
    ("ELE-TAL-70", "Taladro percutor 1/2\" 700W",       "Herr. Eléctricas", 79.99, 2.80, 0.0040),
    ("ELE-AMO-45", "Amoladora angular 4.5\" 850W",      "Herr. Eléctricas", 69.99, 2.50, 0.0030),
    ("ELE-SCI-71", "Sierra circular 7.25\" 1400W",      "Herr. Eléctricas", 99.99, 4.20, 0.0060),
    ("LIM-DES-1L", "Desengrasante multiusos 1L",        "Limpieza Sup.",     4.99, 1.10, 0.0010),
    ("LIM-CLO-1G", "Cloro líquido 1 galón",             "Limpieza Sup.",     3.49, 3.80, 0.0040),
    ("LIM-JAB-2L", "Jabón líquido pisos 2L",            "Limpieza Sup.",     5.99, 2.10, 0.0020),
    ("LIM-TRA-60", "Trapeador algodón 600g",            "Limpieza Sup.",     7.99, 0.60, 0.0010),
    ("LIM-ESC-PL", "Escoba plástica con palo",          "Limpieza Sup.",     6.99, 0.45, 0.0008),
    ("LIM-BAL-12", "Balde plástico 12L",                "Limpieza Sup.",     4.49, 0.40, 0.0020),
    ("HIG-JAB-25", "Jabón antibacterial 250ml x6",      "Higiene Personal",  8.99, 1.50, 0.0020),
    ("HIG-ALC-50", "Alcohol gel 500ml",                 "Higiene Personal",  5.99, 0.55, 0.0006),
    ("HIG-MAS-50", "Mascarillas quirúrgicas caja 50",   "Higiene Personal", 12.99, 0.30, 0.0004),
    ("HIG-PAP-60", "Papel higiénico 60m x4",           "Higiene Personal",  3.99, 0.45, 0.0015),
    ("HIG-TOA-20", "Toallas de papel x200",             "Higiene Personal",  5.49, 0.35, 0.0020),
    ("ALI-ARR-5",  "Arroz blanco 5lb",                  "Granos",            3.99, 2.30, 0.0030),
    ("ALI-FRJ-2",  "Frijoles rojos 2lb",                "Granos",            2.49, 0.90, 0.0010),
    ("ALI-AZU-2",  "Azúcar blanca 2lb",                 "Granos",            1.99, 0.95, 0.0010),
    ("ALI-HAR-2",  "Harina de trigo 2lb",               "Granos",            1.79, 0.95, 0.0010),
    ("ALI-LEN-1",  "Lentejas 1lb",                      "Granos",            1.59, 0.47, 0.0005),
    ("ALI-MIL-2",  "Maíz molido 2lb",                   "Granos",            1.49, 0.95, 0.0010),
    ("CON-ATU-3",  "Atún en agua 160g pack 3",          "Conservas",         4.99, 0.50, 0.0006),
    ("CON-SAS-40", "Salsa de tomate 400g",              "Conservas",         1.49, 0.42, 0.0005),
    ("CON-ACE-1L", "Aceite vegetal 1L",                 "Conservas",         3.29, 0.92, 0.0010),
    ("CON-SAR-12", "Sardinas en aceite 125g",           "Conservas",         1.99, 0.13, 0.0002),
    ("CON-GAR-80", "Garbanzos en agua 800g",            "Conservas",         2.49, 0.85, 0.0009),
    ("CON-MAI-40", "Maíz dulce en lata 400g",           "Conservas",         1.79, 0.43, 0.0005),
]

MARCAS_CAMION = [
    ("Mercedes-Benz", "Actros"),
    ("Volvo",         "FH16"),
    ("Kenworth",      "T680"),
    ("International", "LT625"),
    ("Freightliner",  "Cascadia"),
    ("Hino",          "500 Series"),
    ("Isuzu",         "NQR"),
    ("Mitsubishi",    "Canter"),
]


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def rand_date(start_days_ago: int, end_days_ago: int = 0) -> date:
    return date.today() - timedelta(days=random.randint(end_days_ago, start_days_ago))

def rand_datetime(start_days_ago: int, end_days_ago: int = 0) -> datetime:
    d = rand_date(start_days_ago, end_days_ago)
    return datetime(d.year, d.month, d.day, random.randint(7, 19), random.choice([0, 15, 30, 45]))

def cedula_persona() -> str:
    return f"{random.randint(1,9)}-{random.randint(1,999):03d}-{random.randint(1,9999):04d}"

def ruc_empresa() -> str:
    return f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(100000,999999)}"

def telefono_panama() -> str:
    if random.random() < 0.7:
        return f"+507 6{random.randint(100,999)}-{random.randint(1000,9999)}"
    return f"+507 2{random.randint(10,99)}-{random.randint(1000,9999)}"

def patente_panama() -> str:
    letras = "ABCDEFGHJKLMNPRST"
    return f"{random.choice(letras)}{random.choice(letras)}-{random.randint(1000,9999)}"


# ─── RESET ────────────────────────────────────────────────────────────────────

TABLAS_ORDEN_INVERSO = [
    "factura", "entrega", "linea_pedido", "pedido",
    "parada_recorrido", "recorrido",
    "movimiento_stock", "stock",
    "promocion", "precio_especial",
    "direccion_entrega", "cliente",
    "camion", "conductor", "ruta",
    "bodega", "sucursal",
    "producto", "categoria",
    "grupo_cliente", "ciudad", "pais",
]

def reset_tables(conn):
    cur = conn.cursor()
    cur.execute("SET FOREIGN_KEY_CHECKS = 0")
    for tabla in TABLAS_ORDEN_INVERSO:
        cur.execute(f"TRUNCATE TABLE `{tabla}`")
        print(f"  truncada: {tabla}")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    cur.close()
    print()


# ─── FUNCIONES DE SEED ────────────────────────────────────────────────────────

def seed_pais(conn) -> list:
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO pais (nombre, codigo_iso, moneda_defecto) VALUES (%s, %s, %s)",
        ("Panamá", "PAN", "PAB"),
    )
    ids = [cur.lastrowid]
    conn.commit()
    cur.close()
    print(f"  pais              : 1 registro")
    return ids


def seed_ciudades(conn, pais_ids: list) -> list:
    pais_id = pais_ids[0]
    cur = conn.cursor()
    ids = []
    for nombre, cp in CIUDADES_PANAMA:
        cur.execute(
            "INSERT INTO ciudad (pais_id, nombre, codigo_postal) VALUES (%s, %s, %s)",
            (pais_id, nombre, cp),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  ciudad            : {len(ids)} registros")
    return ids


def seed_grupos_cliente(conn) -> list:
    cur = conn.cursor()
    ids = []
    for nombre, desc in GRUPOS:
        cur.execute(
            "INSERT INTO grupo_cliente (nombre, descripcion) VALUES (%s, %s)",
            (nombre, desc),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  grupo_cliente     : {len(ids)} registros")
    return ids


def seed_sucursales(conn, ciudad_ids: list) -> list:
    nombres = [
        "Sucursal Central", "Sucursal Norte", "Sucursal Sur",
        "Sucursal Este", "Sucursal Oeste", "Sucursal Express",
        "Sucursal Colón", "Sucursal David",
    ]
    cur = conn.cursor()
    ids = []
    for i in range(COUNTS["sucursales"]):
        cur.execute(
            """INSERT INTO sucursal
               (ciudad_id, nombre, direccion, telefono, email, activa, fecha_apertura)
               VALUES (%s, %s, %s, %s, %s, 1, %s)""",
            (
                random.choice(ciudad_ids),
                nombres[i % len(nombres)],
                fake.street_address(),
                telefono_panama(),
                fake.email(),
                rand_date(2000, 365),
            ),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  sucursal          : {len(ids)} registros")
    return ids


def seed_bodegas(conn, sucursal_ids: list) -> list:
    tipos = ["local", "central", "transito", "externa"]
    cur = conn.cursor()
    ids = []
    for suc_id in sucursal_ids:
        for j in range(COUNTS["bodegas_por_sucursal"]):
            tipo = "central" if j == 0 else random.choice(tipos)
            cur.execute(
                """INSERT INTO bodega (sucursal_id, nombre, tipo, capacidad_m3, activa)
                   VALUES (%s, %s, %s, %s, 1)""",
                (suc_id, f"Bodega {tipo.capitalize()} #{j + 1}",
                 tipo, round(random.uniform(50, 500), 2)),
            )
            ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  bodega            : {len(ids)} registros")
    return ids


def seed_categorias(conn) -> dict:
    cur = conn.cursor()
    name_to_id = {}
    for nombre, desc, padre_nombre in CATEGORIAS:
        if padre_nombre is None:
            cur.execute(
                "INSERT INTO categoria (padre_id, nombre, descripcion) VALUES (NULL, %s, %s)",
                (nombre, desc),
            )
            name_to_id[nombre] = cur.lastrowid
    for nombre, desc, padre_nombre in CATEGORIAS:
        if padre_nombre is not None:
            cur.execute(
                "INSERT INTO categoria (padre_id, nombre, descripcion) VALUES (%s, %s, %s)",
                (name_to_id[padre_nombre], nombre, desc),
            )
            name_to_id[nombre] = cur.lastrowid
    conn.commit()
    cur.close()
    print(f"  categoria         : {len(name_to_id)} registros")
    return name_to_id


def seed_productos(conn, cat_ids: dict) -> list:
    cur = conn.cursor()
    prods = []
    for sku, nombre, cat_nombre, precio, peso, volumen in PRODUCTOS:
        cur.execute(
            """INSERT INTO producto
               (categoria_id, codigo_sku, nombre, unidad_medida,
                precio_oficial, moneda, peso_kg, volumen_m3)
               VALUES (%s, %s, %s, 'unidad', %s, 'USD', %s, %s)""",
            (cat_ids.get(cat_nombre), sku, nombre, precio, peso, volumen),
        )
        prods.append({"id": cur.lastrowid, "precio": precio, "sku": sku})
    conn.commit()
    cur.close()
    print(f"  producto          : {len(prods)} registros")
    return prods


def seed_clientes(conn, grupo_ids: list, pais_ids: list) -> list:
    pais_id = pais_ids[0]
    cur = conn.cursor()
    ids = []
    for _ in range(COUNTS["clientes"]):
        tipo = random.choice(["persona", "empresa"])
        if tipo == "persona":
            nombre = fake.name()
            identificacion = cedula_persona()
            limite = random.choice([500.0, 1000.0, 2000.0, 5000.0])
        else:
            nombre = fake.company()
            identificacion = ruc_empresa()
            limite = random.choice([5000.0, 10000.0, 25000.0, 50000.0])
        cur.execute(
            """INSERT INTO cliente
               (grupo_cliente_id, tipo, nombre, identificacion, pais_id,
                email, telefono, limite_credito)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                random.choice(grupo_ids + [None]),
                tipo, nombre, identificacion, pais_id,
                fake.email(), telefono_panama(), limite,
            ),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  cliente           : {len(ids)} registros")
    return ids


def seed_direcciones_entrega(conn, cliente_ids: list, ciudad_ids: list) -> list:
    cur = conn.cursor()
    ids = []
    for cli_id in cliente_ids:
        n = random.randint(1, COUNTS["dir_entrega_max"])
        for j in range(n):
            cur.execute(
                """INSERT INTO direccion_entrega
                   (cliente_id, ciudad_id, direccion, referencia, contacto,
                    telefono, es_principal, activa)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, 1)""",
                (
                    cli_id,
                    random.choice(ciudad_ids),
                    fake.street_address(),
                    fake.secondary_address() if random.random() < 0.4 else None,
                    fake.name() if random.random() < 0.5 else None,
                    telefono_panama() if random.random() < 0.5 else None,
                    1 if j == 0 else 0,
                ),
            )
            ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  direccion_entrega : {len(ids)} registros")
    return ids


def seed_precios_especiales(conn, prods: list, cliente_ids: list, grupo_ids: list):
    cur = conn.cursor()
    for _ in range(COUNTS["precios_especiales"]):
        prod = random.choice(prods)
        precio_esp = round(prod["precio"] * (1 - random.uniform(0.05, 0.25)), 4)
        use_cliente = random.random() < 0.5
        fecha_ini = rand_date(180, 10)
        fecha_fin = fecha_ini + timedelta(days=random.randint(30, 365)) if random.random() < 0.7 else None
        cur.execute(
            """INSERT INTO precio_especial
               (producto_id, cliente_id, grupo_cliente_id, precio, moneda,
                fecha_inicio, fecha_fin, activo)
               VALUES (%s, %s, %s, %s, 'USD', %s, %s, 1)""",
            (
                prod["id"],
                random.choice(cliente_ids) if use_cliente else None,
                None if use_cliente else random.choice(grupo_ids),
                precio_esp, fecha_ini, fecha_fin,
            ),
        )
    conn.commit()
    cur.close()
    print(f"  precio_especial   : {COUNTS['precios_especiales']} registros")


def seed_promociones(conn, prods: list) -> list:
    tipos = ["porcentaje", "monto_fijo", "precio_especial", "2x1", "otro"]
    cur = conn.cursor()
    ids = []
    for i in range(COUNTS["promociones"]):
        prod = random.choice(prods)
        tipo = random.choice(tipos)
        valor = round(random.uniform(5, 30), 4) if tipo == "porcentaje" else (
                round(random.uniform(1, 20), 4) if tipo == "monto_fijo" else None)
        precio_promo = round(prod["precio"] * 0.85, 4) if tipo == "precio_especial" else None
        fecha_ini = rand_date(60, 1)
        fecha_fin = fecha_ini + timedelta(days=random.randint(7, 60)) if random.random() < 0.8 else None
        cur.execute(
            """INSERT INTO promocion
               (producto_id, nombre, tipo, valor_descuento, precio_promocional,
                cantidad_minima, fecha_inicio, fecha_fin, activa)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1)""",
            (
                prod["id"],
                f"Promo {i + 1} — {prod['sku']}",
                tipo, valor, precio_promo,
                random.choice([1, 2, 3, 5, 10]),
                fecha_ini, fecha_fin,
            ),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  promocion         : {len(ids)} registros")
    return ids


def seed_stock(conn, bodega_ids: list, prods: list):
    cur = conn.cursor()
    stock_count = 0
    for bod_id in bodega_ids:
        sample = random.sample(prods, k=int(len(prods) * random.uniform(0.6, 0.9)))
        for prod in sample:
            cantidad = round(random.uniform(10, 500), 0)
            reservada = round(random.uniform(0, min(cantidad * 0.2, 50)), 0)
            cur.execute(
                """INSERT INTO stock (bodega_id, producto_id, cantidad, cantidad_reservada)
                   VALUES (%s, %s, %s, %s)""",
                (bod_id, prod["id"], cantidad, reservada),
            )
            cur.execute(
                """INSERT INTO movimiento_stock
                   (bodega_id, producto_id, tipo, cantidad, stock_resultante,
                    referencia_tipo, notas)
                   VALUES (%s, %s, 'entrada', %s, %s, 'ajuste', 'Stock inicial')""",
                (bod_id, prod["id"], cantidad, cantidad),
            )
            stock_count += 1
    conn.commit()
    cur.close()
    print(f"  stock             : {stock_count} registros")
    print(f"  movimiento_stock  : {stock_count} registros (entradas iniciales)")


def seed_conductores(conn) -> list:
    cur = conn.cursor()
    ids = []
    for _ in range(COUNTS["conductores"]):
        cur.execute(
            """INSERT INTO conductor (nombre, num_licencia, tipo_licencia, telefono, email)
               VALUES (%s, %s, %s, %s, %s)""",
            (
                fake.name(),
                f"PAN-{random.randint(100000, 999999)}",
                random.choice(["C", "D", "E"]),
                telefono_panama(),
                fake.email() if random.random() < 0.6 else None,
            ),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  conductor         : {len(ids)} registros")
    return ids


def seed_camiones(conn, sucursal_ids: list) -> list:
    cur = conn.cursor()
    ids = []
    for i in range(COUNTS["camiones"]):
        marca, modelo = MARCAS_CAMION[i % len(MARCAS_CAMION)]
        cur.execute(
            """INSERT INTO camion
               (patente, marca, modelo, anio, capacidad_kg, capacidad_m3, sucursal_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                patente_panama(),
                marca, modelo,
                random.randint(2015, 2023),
                round(random.uniform(3000, 12000), 2),
                round(random.uniform(15, 60), 2),
                random.choice(sucursal_ids),
            ),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  camion            : {len(ids)} registros")
    return ids


def seed_rutas(conn, ciudad_ids: list) -> list:
    n = COUNTS["rutas"]
    pares = random.sample(
        [(a, b) for a in ciudad_ids for b in ciudad_ids if a != b], n
    )
    cur = conn.cursor()
    ids = []
    for i, (origen_id, destino_id) in enumerate(pares):
        distancia = round(random.uniform(20, 450), 2)
        tiempo = int(distancia / random.uniform(50, 80) * 60)
        cur.execute(
            """INSERT INTO ruta
               (nombre, ciudad_origen_id, ciudad_destino_id, distancia_km,
                tiempo_estimado_min, activa)
               VALUES (%s, %s, %s, %s, %s, 1)""",
            (f"Ruta {i + 1}", origen_id, destino_id, distancia, tiempo),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  ruta              : {len(ids)} registros")
    return ids


def seed_recorridos(conn, camion_ids: list, conductor_ids: list, ruta_ids: list) -> list:
    estados = ["completado", "completado", "completado", "en_curso", "programado", "cancelado"]
    cur = conn.cursor()
    ids = []
    for _ in range(COUNTS["recorridos"]):
        estado = random.choice(estados)
        fecha_sal = rand_datetime(180, 1)
        fecha_ll = fecha_sal + timedelta(hours=random.randint(2, 10)) if estado == "completado" else None
        km_ini = round(random.uniform(10000, 200000), 2)
        km_fin = round(km_ini + random.uniform(50, 500), 2) if estado == "completado" else None
        cur.execute(
            """INSERT INTO recorrido
               (camion_id, conductor_id, ruta_id, fecha_salida, fecha_llegada,
                km_inicial, km_final, estado)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                random.choice(camion_ids),
                random.choice(conductor_ids),
                random.choice(ruta_ids) if random.random() < 0.8 else None,
                fecha_sal, fecha_ll, km_ini, km_fin, estado,
            ),
        )
        ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  recorrido         : {len(ids)} registros")
    return ids


def seed_paradas(conn, recorrido_ids: list, dir_ids: list, sucursal_ids: list) -> list:
    estados = ["completada", "completada", "pendiente", "no_entregada"]
    cur = conn.cursor()
    ids = []
    for rec_id in recorrido_ids:
        for orden in range(1, COUNTS["paradas_por_recorrido"] + 1):
            usa_dir = random.random() < 0.6
            estado = random.choice(estados)
            hora_est = rand_datetime(90)
            hora_llegada = hora_est if estado == "completada" else None
            hora_salida = (hora_est + timedelta(minutes=random.randint(5, 30))
                           if estado == "completada" else None)
            cur.execute(
                """INSERT INTO parada_recorrido
                   (recorrido_id, orden, direccion_entrega_id, sucursal_id,
                    hora_estimada, hora_llegada, hora_salida, estado)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    rec_id, orden,
                    random.choice(dir_ids) if usa_dir else None,
                    None if usa_dir else random.choice(sucursal_ids),
                    hora_est, hora_llegada, hora_salida, estado,
                ),
            )
            ids.append(cur.lastrowid)
    conn.commit()
    cur.close()
    print(f"  parada_recorrido  : {len(ids)} registros")
    return ids


def seed_pedidos(conn, cliente_ids: list, sucursal_ids: list) -> list:
    estados = [
        "confirmado", "confirmado", "confirmado",
        "entregado", "entregado",
        "en_preparacion", "listo",
        "cancelado", "borrador",
    ]
    cur = conn.cursor()
    pedidos = []
    for i in range(COUNTS["pedidos"]):
        estado = random.choice(estados)
        fecha_ped = rand_datetime(365, 1)
        fecha_req = (fecha_ped + timedelta(days=random.randint(1, 14))).date()
        cur.execute(
            """INSERT INTO pedido
               (cliente_id, sucursal_id, numero_pedido, fecha_pedido,
                fecha_requerida, estado, moneda, subtotal, descuento_total,
                impuesto_total, total)
               VALUES (%s, %s, %s, %s, %s, %s, 'USD', 0, 0, 0, 0)""",
            (
                random.choice(cliente_ids),
                random.choice(sucursal_ids),
                f"PED-2025-{i + 1:05d}",
                fecha_ped, fecha_req, estado,
            ),
        )
        pedidos.append({
            "id": cur.lastrowid,
            "estado": estado,
            "fecha": fecha_ped,
        })
    conn.commit()
    cur.close()
    print(f"  pedido            : {len(pedidos)} registros")
    return pedidos


def seed_lineas_pedido(conn, pedidos: list, prods: list, bodega_ids: list, prom_ids: list):
    cur = conn.cursor()
    total = 0
    for ped in pedidos:
        n_lineas = random.randint(1, COUNTS["lineas_max"])
        seleccion = random.sample(prods, min(n_lineas, len(prods)))
        subtotal_ped = 0.0
        desc_total_ped = 0.0
        for prod in seleccion:
            cantidad = float(random.randint(1, 20))
            precio_unit = prod["precio"]
            desc_pct = random.choice([0.0, 0.0, 0.0, 0.05, 0.10, 0.15])
            desc_monto = round(precio_unit * cantidad * desc_pct, 4)
            subtotal_linea = round(precio_unit * cantidad - desc_monto, 4)
            prom_id = random.choice(prom_ids) if prom_ids and random.random() < 0.1 else None
            cur.execute(
                """INSERT INTO linea_pedido
                   (pedido_id, producto_id, bodega_id, promocion_id, cantidad,
                    precio_unitario, descuento_pct, descuento_monto, subtotal)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    ped["id"], prod["id"], random.choice(bodega_ids),
                    prom_id, cantidad, precio_unit,
                    desc_pct, desc_monto, subtotal_linea,
                ),
            )
            subtotal_ped += subtotal_linea
            desc_total_ped += desc_monto
            total += 1
        imp = round(subtotal_ped * ITBMS, 2)
        total_ped = round(subtotal_ped + imp, 2)
        cur.execute(
            """UPDATE pedido SET subtotal=%s, descuento_total=%s,
               impuesto_total=%s, total=%s WHERE id=%s""",
            (round(subtotal_ped, 2), round(desc_total_ped, 2), imp, total_ped, ped["id"]),
        )
        ped["subtotal"] = round(subtotal_ped, 2)
        ped["descuento_total"] = round(desc_total_ped, 2)
        ped["impuesto_total"] = imp
        ped["total"] = total_ped
    conn.commit()
    cur.close()
    print(f"  linea_pedido      : {total} registros")


def seed_entregas(conn, pedidos: list, sucursal_ids: list,
                  recorrido_ids: list, parada_ids: list, dir_ids: list):
    estados_map = {
        "entregado":      "entregada",
        "confirmado":     "pendiente",
        "en_preparacion": "pendiente",
        "listo":          "pendiente",
        "cancelado":      "no_entregada",
        "borrador":       "pendiente",
        "anulado":        "no_entregada",
    }
    tipos = ["retiro_local", "envio_camion", "envio_domicilio"]
    cur = conn.cursor()
    count = 0
    for ped in pedidos:
        if ped["estado"] in ("cancelado", "borrador"):
            continue
        tipo = random.choice(tipos)
        estado_ent = estados_map.get(ped["estado"], "pendiente")
        fecha_est = ped["fecha"] + timedelta(days=random.randint(1, 5))
        fecha_real = fecha_est if estado_ent == "entregada" else None
        suc_ret = rec_id = par_id = dir_id = None
        if tipo == "retiro_local":
            suc_ret = random.choice(sucursal_ids)
        elif tipo == "envio_camion":
            rec_id = random.choice(recorrido_ids)
            par_id = random.choice(parada_ids)
        else:
            dir_id = random.choice(dir_ids)
        cur.execute(
            """INSERT INTO entrega
               (pedido_id, tipo, sucursal_retiro_id, recorrido_id, parada_id,
                direccion_entrega_id, fecha_estimada, fecha_real, estado, receptor_nombre)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                ped["id"], tipo, suc_ret, rec_id, par_id, dir_id,
                fecha_est, fecha_real, estado_ent,
                fake.name() if estado_ent == "entregada" else None,
            ),
        )
        ped["entrega_id"] = cur.lastrowid
        count += 1
    conn.commit()
    cur.close()
    print(f"  entrega           : {count} registros")


def seed_facturas(conn, pedidos: list):
    estados_fac = {
        "entregado":      "pagada",
        "confirmado":     "emitida",
        "en_preparacion": "emitida",
        "listo":          "emitida",
    }
    cur = conn.cursor()
    count = 0
    for i, ped in enumerate(pedidos):
        if ped["estado"] not in estados_fac:
            continue
        fecha_emision = ped["fecha"] + timedelta(hours=random.randint(1, 24))
        fecha_venc = (fecha_emision + timedelta(days=30)).date()
        base_imp = round(ped["subtotal"] - ped["descuento_total"], 2)
        cur.execute(
            """INSERT INTO factura
               (pedido_id, entrega_id, numero_fiscal, serie, fecha_emision,
                fecha_vencimiento, moneda, subtotal, descuento_total, base_imponible,
                impuesto_pct, impuesto_monto, total, estado)
               VALUES (%s, %s, %s, 'A', %s, %s, 'USD', %s, %s, %s, %s, %s, %s, %s)""",
            (
                ped["id"],
                ped.get("entrega_id"),
                f"FAC-2025-{i + 1:05d}",
                fecha_emision, fecha_venc,
                ped["subtotal"], ped["descuento_total"], base_imp,
                ITBMS, ped["impuesto_total"], ped["total"],
                estados_fac[ped["estado"]],
            ),
        )
        count += 1
    conn.commit()
    cur.close()
    print(f"  factura           : {count} registros")


# ─── CLI ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Seed ERP Comercial — Panamá")
    p.add_argument("--reset", action="store_true",
                   help="Trunca todas las tablas antes de insertar")
    p.add_argument("--counts", nargs="*", metavar="KEY=VALUE",
                   help="Sobreescribe parámetros. Ej: --counts pedidos=300 clientes=200")
    return p.parse_args()


def apply_count_overrides(overrides):
    if not overrides:
        return
    for item in overrides:
        k, _, v = item.partition("=")
        k = k.strip()
        if k in COUNTS:
            COUNTS[k] = int(v.strip())
            print(f"  {k} = {COUNTS[k]}")
        else:
            print(f"  ADVERTENCIA: clave desconocida '{k}'")


def main():
    args = parse_args()
    if args.counts:
        print("Overrides aplicados:")
        apply_count_overrides(args.counts)
        print()

    conn = mysql.connector.connect(**DB_CONFIG)
    print(f"Conectado a {DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")

    if args.reset:
        print("Reseteando tablas...")
        reset_tables(conn)

    print("Insertando datos:")
    pais_ids      = seed_pais(conn)
    ciudad_ids    = seed_ciudades(conn, pais_ids)
    grupo_ids     = seed_grupos_cliente(conn)
    sucursal_ids  = seed_sucursales(conn, ciudad_ids)
    bodega_ids    = seed_bodegas(conn, sucursal_ids)
    cat_ids       = seed_categorias(conn)
    prods         = seed_productos(conn, cat_ids)
    cliente_ids   = seed_clientes(conn, grupo_ids, pais_ids)
    dir_ids       = seed_direcciones_entrega(conn, cliente_ids, ciudad_ids)
    seed_precios_especiales(conn, prods, cliente_ids, grupo_ids)
    prom_ids      = seed_promociones(conn, prods)
    seed_stock(conn, bodega_ids, prods)
    conductor_ids = seed_conductores(conn)
    camion_ids    = seed_camiones(conn, sucursal_ids)
    ruta_ids      = seed_rutas(conn, ciudad_ids)
    recorrido_ids = seed_recorridos(conn, camion_ids, conductor_ids, ruta_ids)
    parada_ids    = seed_paradas(conn, recorrido_ids, dir_ids, sucursal_ids)
    pedidos       = seed_pedidos(conn, cliente_ids, sucursal_ids)
    seed_lineas_pedido(conn, pedidos, prods, bodega_ids, prom_ids)
    seed_entregas(conn, pedidos, sucursal_ids, recorrido_ids, parada_ids, dir_ids)
    seed_facturas(conn, pedidos)

    conn.close()
    print("\n✓ Seed completado")


if __name__ == "__main__":
    main()
