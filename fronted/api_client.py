import os
import sys
import requests
from backend import db_helper

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_CURRENT_DIR) if os.path.basename(_CURRENT_DIR) == "fronted" else _CURRENT_DIR
_BACKEND_DIR = os.path.join(_PROJECT_ROOT, "backend")

for p in [_PROJECT_ROOT, _BACKEND_DIR, _CURRENT_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

# Cached status for backend server to prevent repeated socket timeouts
_BACKEND_STATUS = None

def get_api_url() -> str:
    url = os.getenv("API_URL")
    if not url:
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "API_URL" in st.secrets:
                url = st.secrets["API_URL"]
        except Exception:
            pass
    return url or "http://localhost:8000"

def is_backend_online(timeout: float = 0.3) -> bool:
    global _BACKEND_STATUS
    api_url = get_api_url()

    # If already verified offline on localhost, return immediately without blocking
    if _BACKEND_STATUS is False and "localhost" in api_url:
        return False

    try:
        res = requests.get(f"{api_url}/health", timeout=timeout)
        _BACKEND_STATUS = (res.status_code == 200)
    except Exception:
        _BACKEND_STATUS = False

    return _BACKEND_STATUS

def fetch_expenses(selected_date):
    date_str = db_helper.normalize_date(selected_date)
    api_url = get_api_url()

    if is_backend_online():
        try:
            res = requests.get(f"{api_url}/expenses/{date_str}", timeout=2)
            if res.status_code == 200:
                return res.json() or [], "api"
        except Exception:
            pass

    records = db_helper.fetch_expenses_for_date(date_str) or []
    return records, "sqlite" if getattr(db_helper, "_DB_DIALECT", "sqlite") == "sqlite" else "mysql"

def save_expenses(selected_date, expenses_list):
    date_str = db_helper.normalize_date(selected_date)
    api_url = get_api_url()

    if is_backend_online():
        try:
            res = requests.post(f"{api_url}/expenses/{date_str}", json=expenses_list, timeout=3)
            if res.status_code == 200:
                return True, "Expenses updated successfully via API.", "api"
            else:
                return False, f"Server returned error: status {res.status_code}", "api"
        except Exception:
            pass

    try:
        db_helper.save_expenses_for_date(date_str, expenses_list)
        storage_type = "sqlite" if getattr(db_helper, "_DB_DIALECT", "sqlite") == "sqlite" else "mysql"
        return True, "Expenses updated successfully in database.", storage_type
    except Exception as e:
        return False, f"Failed to save expenses: {e}", "database"

def fetch_category_analytics(start_date, end_date):
    start_str = db_helper.normalize_date(start_date)
    end_str = db_helper.normalize_date(end_date)
    api_url = get_api_url()

    if is_backend_online():
        try:
            payload = {"start_date": start_str, "end_date": end_str}
            res = requests.post(f"{api_url}/analytics/", json=payload, timeout=3)
            if res.status_code == 200:
                return res.json() or {}, "api"
        except Exception:
            pass

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
    api_url = get_api_url()

    if is_backend_online():
        try:
            res = requests.get(f"{api_url}/analytics/{int(year)}", timeout=3)
            if res.status_code == 200:
                result = res.json()
                return result.get("data", []) or [], "api"
        except Exception:
            pass

    data = db_helper.get_expenses_for_year(int(year)) or []
    return data, "db"

def get_available_years():
    return db_helper.get_available_years()
