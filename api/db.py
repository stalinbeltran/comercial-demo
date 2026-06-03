import os
import mysql.connector.pooling
from dotenv import load_dotenv

load_dotenv()

_BASE = dict(
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    charset="utf8mb4",
)

_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="erp_transaccional",
    database=os.getenv("DB_NAME"),
    **_BASE,
)

_pool_agg = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="erp_aggregated",
    database=os.getenv("DB_NAME_AGG"),
    **_BASE,
)


def get_conn():
    return _pool.get_connection()


def get_conn_agg():
    return _pool_agg.get_connection()
