import sqlite3
import logging

logger = logging.getLogger(__name__)

DATABASE_FILE = "torrents.db"

def create_table_if_not_exists(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Magnets (
        id INTEGER PRIMARY KEY,
        magnet_url TEXT,
        name TEXT
    )
    """)

def add_missing_columns(cursor):
    columns_to_add = {
        "magnet_url": "TEXT",
        "name": "TEXT",
        # Add more columns as needed
    }

    cursor.execute("PRAGMA table_info(Magnets)")
    existing_columns = {column[1] for column in cursor.fetchall()}

    for column_name, column_type in columns_to_add.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE Magnets ADD COLUMN {column_name} {column_type}")

def init_database():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        create_table_if_not_exists(cursor)
        add_missing_columns(cursor)

        conn.commit()
        logger.info("Database prepared with necessary columns.")
        return conn
    except Exception as e:
        logger.error(f"Error preparing the database: {str(e)}")
        return None

def close_database(conn: sqlite3.Connection):
    try:
        conn.close()
        logger.info("Database connection closed.")
    except Exception as e:
        logger.error(f"Error closing database connection: {str(e)}")

def search_magnet(query: str):
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        query = query.replace("-", " ").replace("_", " ")
        cursor.execute("SELECT magnet_url, name FROM Magnets WHERE name LIKE ?", ('%' + query,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        logger.error(f"Error searching for magnets by name: {str(e)}")
        return []
    finally:
        if conn is not None:
            conn.close()

class DatabaseConnection:
    def __init__(self, conn):
        self.conn = conn
