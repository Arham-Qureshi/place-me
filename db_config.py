"""
Database configuration and connection helper for Placement Management System.
Uses mysql-connector-python.
"""
import mysql.connector
from mysql.connector import Error
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '@Aq9191819121',
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
