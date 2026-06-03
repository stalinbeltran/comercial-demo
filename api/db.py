import os
import mysql.connector.pooling
from dotenv import load_dotenv

load_dotenv()

_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="erp",
    pool_size=5,
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    charset="utf8mb4",
)


def get_conn():
    return _pool.get_connection()
