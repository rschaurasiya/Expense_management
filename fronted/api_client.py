import os
import sys
import requests

# Resolve directories so modules can be imported anywhere
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CURRENT_DIR) if os.path.basename(_CURRENT_DIR) == "fronted" else _CURRENT_DIR
_BACKEND_DIR = os.path.join(_PROJECT_ROOT, "backend")

for p in [_PROJECT_ROOT, _BACKEND_DIR, _CURRENT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from backend import db_helper



def get_api_url() -> str:
    """Retrieve API URL from environment, Streamlit secrets, or default."""
    url = os.getenv("API_URL")
    if not url:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "API_URL" in st.secrets:
                url = st.secrets["API_URL"]
        except Exception:
            pass
    return url or "http://localhost:8000"


def is_backend_online(timeout: float = 1.0) -> bool:
    """Check if the FastAPI backend server is responding."""
    api_url = get_api_url()
    try:
        res = requests.get(f"{api_url}/health", timeout=timeout)
        return res.status_code == 200
    except Exception:
        return False


def fetch_expenses(selected_date):
    """Fetch expenses for a given date from API or directly from DB."""
    api_url = get_api_url()
    date_str = selected_date.strftime("%Y-%m-%d") if hasattr(selected_date, "strftime") else str(selected_date)

    if is_backend_online():
        try:
            res = requests.get(f"{api_url}/expenses/{date_str}", timeout=4)
            if res.status_code == 200:
                return res.json() or [], "api"
        except Exception:
            pass

    # Direct database fallback (MySQL or SQLite)
    records = db_helper.fetch_expenses_for_date(date_str) or []
    return records, "db"


def save_expenses(selected_date, expenses_list):
    """Save expenses for a date via API or directly to DB."""
    api_url = get_api_url()
    date_str = selected_date.strftime("%Y-%m-%d") if hasattr(selected_date, "strftime") else str(selected_date)

    if is_backend_online():
        try:
            res = requests.post(f"{api_url}/expenses/{date_str}", json=expenses_list, timeout=4)
            if res.status_code == 200:
                return True, "Expenses updated successfully via API!", "api"
            else:
                return False, f"Server returned error: status {res.status_code}", "api"
        except Exception:
            pass

    # Direct database fallback (MySQL or SQLite)
    try:
        db_helper.delete_expenses_for_date(date_str)
        for exp in expenses_list:
            db_helper.insert_expense(date_str, float(exp["amount"]), exp["category"], exp.get("notes", ""))
        return True, "Expenses updated successfully in database!", "db"
    except Exception as e:
        return False, f"Failed to save expenses: {e}", "db"


def fetch_category_analytics(start_date, end_date):
    """Fetch category analytics via API or direct DB computation."""
    api_url = get_api_url()
    start_str = start_date.strftime("%Y-%m-%d") if hasattr(start_date, "strftime") else str(start_date)
    end_str = end_date.strftime("%Y-%m-%d") if hasattr(end_date, "strftime") else str(end_date)

    if is_backend_online():
        try:
            payload = {"start_date": start_str, "end_date": end_str}
            res = requests.post(f"{api_url}/analytics/", json=payload, timeout=4)
            if res.status_code == 200:
                return res.json() or {}, "api"
        except Exception:
            pass

    # Direct database computation
    data = db_helper.fetch_expense_summary(start_str, end_str) or []
    total = sum([row["total"] for row in data if row.get("total") is not None]) if data else 0
    breakdown = {}
    for row in data:
        cat = row.get("category", "Other")
        amount = float(row.get("total", 0.0) or 0.0)
        percentage = (amount / total) * 100 if total != 0 else 0
        breakdown[cat] = {
            "total": amount,
            "percentage": percentage
        }
    return breakdown, "db"


def fetch_monthly_analytics(year):
    """Fetch monthly analytics via API or direct DB computation."""
    api_url = get_api_url()

    if is_backend_online():
        try:
            res = requests.get(f"{api_url}/analytics/{year}", timeout=4)
            if res.status_code == 200:
                result = res.json()
                return result.get("data", []) or [], "api"
        except Exception:
            pass

    # Direct database computation
    data = db_helper.get_expenses_for_year(int(year)) or []
    return data, "db"
