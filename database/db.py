
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "database" / "waste_management.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"

def get_db_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def initialize_database():
    connection = get_db_connection()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as file:
        connection.executescript(file.read())

    connection.commit()
    connection.close()

if __name__ == "__main__":
    initialize_database()
    print("Database created successfully!")
