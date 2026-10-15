import os
import sys
import json
import sqlite3
from datetime import datetime
from contextlib import contextmanager
import pandas as pd

_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from logging_setup import setup_Logger

logger = setup_Logger("db_helper")

# Cache database dialect after first check: 'mysql' or 'sqlite'
_DB_DIALECT = None

def normalize_date(val) -> str:
    """Normalize any date representation to YYYY-MM-DD string."""
    if hasattr(val, "strftime"):
        return val.strftime("%Y-%m-%d")
    s = str(val).strip().replace("/", "-")
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return s

def _get_mysql_config():
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
                    [(normalize_date(s["expense_date"]), float(s["amount"]), s["category"], s.get("notes", "")) for s in samples]
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
    global _DB_DIALECT
    dialect = _DB_DIALECT
    connection = None

    # If dialect is not yet determined, probe MySQL first
    if dialect is None:
        try:
            import mysql.connector
            cfg = _get_mysql_config()
            connection = mysql.connector.connect(
                host=cfg["host"],
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                port=cfg["port"],
                connection_timeout=0.3
            )
            cursor = connection.cursor(dictionary=True)
            _DB_DIALECT = "mysql"
            dialect = "mysql"
        except Exception:
            # MySQL unavailable; permanently switch session to SQLite for zero latency
            _DB_DIALECT = "sqlite"
            dialect = "sqlite"

    if dialect == "mysql" and connection is None:
        try:
            import mysql.connector
            cfg = _get_mysql_config()
            connection = mysql.connector.connect(
                host=cfg["host"],
                user=cfg["user"],
                password=cfg["password"],
                database=cfg["database"],
                port=cfg["port"],
                connection_timeout=1
            )
            cursor = connection.cursor(dictionary=True)
        except Exception:
            _DB_DIALECT = "sqlite"
            dialect = "sqlite"

    if dialect == "sqlite":
        db_path = os.path.join(_BACKEND_DIR, "expenses.db")
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        _init_sqlite_db(connection)
        cursor = SQLiteCursorWrapper(connection.cursor())

    try:
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
    date_str = normalize_date(expense_date)
    logger.info(f"fetch_expenses_for_date called with {date_str}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (date_str,))
        expenses = cursor.fetchall()
        return expenses

def save_expenses_for_date(expense_date, expenses_list):
    """Save expenses for a date in a single fast transaction."""
    date_str = normalize_date(expense_date)
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (date_str,))
        for exp in expenses_list:
            amt = float(exp["amount"])
            if amt > 0:
                cursor.execute(
                    "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
                    (date_str, amt, exp["category"], exp.get("notes", "") or "")
                )

def get_available_years():
    """Retrieve all unique years present in the database."""
    with get_db_cursor() as cursor:
        if getattr(cursor, "dialect", "mysql") == "sqlite":
            query = "SELECT DISTINCT CAST(SUBSTR(REPLACE(expense_date, '/', '-'), 1, 4) AS INTEGER) AS yr FROM expenses WHERE amount > 0 ORDER BY yr DESC"
        else:
            query = "SELECT DISTINCT YEAR(expense_date) AS yr FROM expenses WHERE amount > 0 ORDER BY yr DESC"
        cursor.execute(query)
        rows = cursor.fetchall()
        years = [int(r["yr"]) for r in rows if r.get("yr") is not None and str(r["yr"]).isdigit()]
        curr = datetime.now().year
        if curr not in years:
            years.append(curr)
        years.sort(reverse=True)
        return years

def get_expenses_for_year(year):
    year_int = int(year)
    with get_db_cursor() as cursor:
        if getattr(cursor, "dialect", "mysql") == "sqlite":
            query = '''SELECT 
                CAST(SUBSTR(REPLACE(expense_date, '/', '-'), 6, 2) AS INTEGER) AS month,
                SUM(amount) AS total_expenses
            FROM expenses
            WHERE CAST(SUBSTR(REPLACE(expense_date, '/', '-'), 1, 4) AS INTEGER) = %s
            GROUP BY month
            ORDER BY month'''
            cursor.execute(query, (year_int,))
        else:
            query = '''SELECT 
                MONTH(expense_date) AS month,
                SUM(amount) AS total_expenses
            FROM expenses
            WHERE YEAR(expense_date) = %s
            GROUP BY MONTH(expense_date)
            ORDER BY month'''
            cursor.execute(query, (year_int,))
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
    date_str = normalize_date(expense_date)
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (date_str, float(amount), category, notes or "")
        )

def delete_expenses_for_date(expense_date):
    date_str = normalize_date(expense_date)
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (date_str,))

def fetch_expense_summary(start_date, end_date):
    start_str = normalize_date(start_date)
    end_str = normalize_date(end_date)
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