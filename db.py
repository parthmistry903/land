import mysql.connector
from mysql.connector import Error, ClientFlag
import os
import sys


DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "port": int(os.environ.get("DB_PORT", 3306)),
    "database": os.environ.get("DB_NAME", "landdata"),
    "user": os.environ.get("DB_USER", "root"),
    "password": os.environ.get("DB_PASSWORD", "cbeXHgtZsNnRTznMkaqNXsaWXrzWeGPh"),
    "ssl_disabled": True,
    "client_flags": [ClientFlag.FOUND_ROWS],
}


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
        print(f"Database query failed: {e}", file=sys.stderr)
        return [] if fetch_all else False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def execute_transaction(queries):
    conn = get_db_connection()
    if not conn:
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        conn.start_transaction()

        for sql, params in queries:
            cursor.execute(sql, params)
            if sql.strip().upper().startswith("UPDATE") and cursor.rowcount == 0:
                raise Exception()

        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
