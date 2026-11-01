
import sqlite3
from pathlib import Path

# Store the database in the main project folder
DB_PATH = Path(__file__).resolve().parent.parent / "khojsetu.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_type TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                color TEXT,
                location TEXT,
                item_date TEXT,
                identifying_details TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def add_report(report_type, description, category="",
               color="", location="", item_date="",
               identifying_details=""):

    if report_type not in ("lost", "found"):
        raise ValueError("Report type must be lost or found.")

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO reports (
                report_type, description, category,
                color, location, item_date,
                identifying_details
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            report_type, description, category,
            color, location, item_date,
            identifying_details
        ))

        return cursor.lastrowid


def get_reports(report_type=None):
    with get_connection() as conn:
        if report_type:
            rows = conn.execute(
                "SELECT * FROM reports WHERE report_type = ? "
                "ORDER BY created_at DESC",
                (report_type,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM reports ORDER BY created_at DESC"
            ).fetchall()

        return [dict(row) for row in rows]
