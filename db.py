import mysql.connector
from mysql.connector import Error, ClientFlag
import os
import sys

# Read variables with safe defaults for local development
DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "database": os.environ.get("DB_NAME", "landdata"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "Parth@123"),
    "ssl_disabled": True,
    "client_flags": [ClientFlag.FOUND_ROWS],
}

# Print configuration info on startup (excluding password for security)
print(f"Database config: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, database={DB_CONFIG['database']}, user={DB_CONFIG['user']}", file=sys.stderr)

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Database connection failed: {e}", file=sys.stderr)
        return None
    return None

def execute_query(sql, params=None, fetch_all=False):
    conn = get_db_connection()
    if not conn:
        print(f"Could not get database connection for query: {sql[:50]}", file=sys.stderr)
        return [] if fetch_all else False

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())

        if sql.strip().upper().startswith("SELECT"):
            return cursor.fetchall() if fetch_all else cursor.fetchone()
        else:
            conn.commit()
            return True
    except Error as e:
        print(f"Database query failed: {e} | SQL: {sql[:100]}", file=sys.stderr)
        return [] if fetch_all else False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_transaction(queries):
    conn = get_db_connection()
    if not conn:
        print("Could not get database connection for transaction", file=sys.stderr)
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        conn.start_transaction()

        for sql, params in queries:
            cursor.execute(sql, params)
            if sql.strip().upper().startswith("UPDATE") and cursor.rowcount == 0:
                raise Exception(f"Update affected 0 rows: {sql[:50]}")

        conn.commit()
        return True
    except Exception as e:
        print(f"Transaction failed: {e}", file=sys.stderr)
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
