"""
Database configuration and connection helper for Placement Management System.
Uses mysql-connector-python.
"""
import mysql.connector
from mysql.connector import Error


# ── Change these values to match your MySQL setup ──
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '@Aq9191819121',          # <-- Enter your MySQL root password here
    'database': 'placement_system',
}


def get_db():
    """Return a new MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] {e}")
        return None
