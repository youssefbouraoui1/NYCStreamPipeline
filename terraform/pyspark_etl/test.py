# pg_test.py
import os
import psycopg2

PG_HOST = os.getenv("PG_HOST", "postgres")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB = os.getenv("PG_DB", "NycTrafficStreamDatabase")
PG_USER = os.getenv("PG_USER", "admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "admin123")

try:
    print(f"Connecting to Postgres at {PG_HOST}:{PG_PORT}, DB: {PG_DB}, user: {PG_USER}")
    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD
    )
    cur = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()
    print("Postgres version:", version)
    cur.close()
    conn.close()
    print("Connection successful!")
except Exception as e:
    print("Failed to connect to Postgres:")
    print(e)
