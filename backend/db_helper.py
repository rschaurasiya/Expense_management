# CRUD process is performed Here(Create Retrive Update Delete)
import os
import sys
import json
import sqlite3
from contextlib import contextmanager
import pandas as pd

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from logging_setup import setup_Logger

logger = setup_Logger("db_helper")

def _get_mysql_config():
    # 1. Check Streamlit secrets if running inside Streamlit
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "mysql" in st.secrets:
            sec = st.secrets["mysql"]
            return {
                "host": sec.get("host", "localhost"),
                "user": sec.get("user", "root"),
                "password": sec.get("password", ""),
                "database": sec.get("database", "expense_manager"),
                "port": int(sec.get("port", 3306))
            }
    except Exception:
        pass

    # 2. Check environment variables or default to local config
    return {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "radhe123"),
        "database": os.getenv("MYSQL_DATABASE", "expense_manager"),
        "port": int(os.getenv("MYSQL_PORT", 3306))
    }

def _init_sqlite_db(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            notes TEXT
        )
    ''')
    conn.commit()

    # Check if empty, and seed sample data if available
    cursor.execute("SELECT COUNT(*) FROM expenses")
    count = cursor.fetchone()[0]
    if count == 0:
        sample_path = os.path.join(_BACKEND_DIR, "sample_expenses.json")
        if os.path.exists(sample_path):
            try:
                with open(sample_path, "r", encoding="utf-8") as f:
                    samples = json.load(f)
                cursor.executemany(
                    "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (?, ?, ?, ?)",
                    [(s["expense_date"], s["amount"], s["category"], s.get("notes", "")) for s in samples]
                )
                conn.commit()
                logger.info(f"Seeded SQLite with {len(samples)} sample records")
            except Exception as e:
                logger.warning(f"Could not seed sample expenses: {e}")
    cursor.close()

class SQLiteCursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        clean_query = query.replace("%s", "?")
        if params is not None:
            # Convert date objects to string formatted YYYY-MM-DD
            converted = []
            for p in params:
                if hasattr(p, "strftime"):
                    converted.append(p.strftime("%Y-%m-%d"))
                else:
                    converted.append(p)
            return self._cursor.execute(clean_query, tuple(converted))
        return self._cursor.execute(clean_query)

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(row) for row in rows]

    def fetchone(self):
        row = self._cursor.fetchone()
        return dict(row) if row else None

    def close(self):
        self._cursor.close()

@contextmanager
def get_db_cursor(commit=False):
    dialect = "mysql"
    connection = None

    try:
        import mysql.connector
        cfg = _get_mysql_config()
        connection = mysql.connector.connect(
            host=cfg["host"],
            user=cfg["user"],
            password=cfg["password"],
            database=cfg["database"],
            port=cfg["port"],
            connection_timeout=2
        )
        cursor = connection.cursor(dictionary=True)
    except Exception as e:
        logger.info(f"MySQL unavailable ({e}). Using SQLite fallback.")
        dialect = "sqlite"
        db_path = os.path.join(_BACKEND_DIR, "expenses.db")
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        _init_sqlite_db(connection)
        cursor = SQLiteCursorWrapper(connection.cursor())

    try:
        # Attach dialect to cursor for custom SQL syntax branching if needed
        cursor.dialect = dialect
        yield cursor
        if commit:
            connection.commit()
    finally:
        cursor.close()
        connection.close()

def fetch_all_records():
    query = "SELECT * from expenses"
    with get_db_cursor() as cursor:
        cursor.execute(query)
        expenses = cursor.fetchall()
        return expenses

def fetch_expenses_for_date(expense_date):
    date_str = str(expense_date)
    logger.info(f"fetch_expenses_for_date called with {date_str}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (date_str,))
        expenses = cursor.fetchall()
        return expenses

def get_expenses_for_year(year):
    with get_db_cursor() as cursor:
        if getattr(cursor, "dialect", "mysql") == "sqlite":
            query = '''SELECT 
                CAST(strftime('%m', expense_date) AS INTEGER) AS month,
                SUM(amount) AS total_expenses
            FROM expenses
            WHERE strftime('%Y', expense_date) = %s
            GROUP BY month
            ORDER BY month'''
            cursor.execute(query, (str(year),))
        else:
            query = '''SELECT 
                MONTH(expense_date) AS month,
                SUM(amount) AS total_expenses
            FROM expenses
            WHERE YEAR(expense_date) = %s
            GROUP BY MONTH(expense_date)
            ORDER BY month'''
            cursor.execute(query, (year,))
        rows = cursor.fetchall()

    if not rows:
        return []

    df = pd.DataFrame(rows)
    df.rename(columns={
        "month": "Month",
        "total_expenses": "Total_Expenses_By_Month"
    }, inplace=True)

    total = df["Total_Expenses_By_Month"].sum()
    if total > 0:
        df["Percentage_of_Total"] = (df["Total_Expenses_By_Month"] / total * 100).round(2)
    else:
        df["Percentage_of_Total"] = 0

    return df.to_dict(orient="records")

def insert_expense(expense_date, amount, category, notes):
    date_str = str(expense_date)
    logger.info(f"insert_expenses called with date:{date_str}, amount:{amount}, category: {category}, notes: {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (date_str, float(amount), category, notes)
        )

def delete_expenses_for_date(expense_date):
    date_str = str(expense_date)
    logger.info(f"delete_expenses_for_date called with {date_str}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (date_str,))

def fetch_expense_summary(start_date, end_date):
    start_str = str(start_date)
    end_str = str(end_date)
    logger.info(f"fetch_expenses_for_summary called with start_date:{start_str}, end_date: {end_str}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT category, sum(amount) as total
               FROM expenses WHERE expense_date
               BETWEEN %s and %s
               GROUP BY category;''',
            (start_str, end_str)
        )
        data = cursor.fetchall()
        return data

if __name__ == "__main__":
    print("Testing fetch 2024:", get_expenses_for_year(2024))