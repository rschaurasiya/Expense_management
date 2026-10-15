import os
import sys

# Ensure fronted and project root are in sys.path
_FRONTED_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_FRONTED_DIR)

for path in [_FRONTED_DIR, _PROJECT_ROOT, os.path.join(_PROJECT_ROOT, "backend")]:
    if path not in sys.path:
        sys.path.insert(0, path)

import streamlit as st
import api_client
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab
from analtics_month import analytics_by_month_tab

# Page configuration
st.set_page_config(
    page_title="Expense Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("Expense Management System")

# Minimal sidebar showing only essential status
with st.sidebar:
    st.markdown("### System Status")
    backend_online = api_client.is_backend_online()
    if backend_online:
        st.success("FastAPI API: Connected")
        st.caption(f"Endpoint: {api_client.get_api_url()}")
    else:
        st.info("Database: SQLite Active")

# Clean tab creation without emojis
tab1, tab2, tab3 = st.tabs([
    "Add / Update Expenses",
    "Analytics By Categories",
    "Analytics By Months"
])

# Tab 1: Add or Update
with tab1:
    add_update_tab()

# Tab 2: Category Analytics
with tab2:
    analytics_tab()

# Tab 3: Monthly Analytics
with tab3:
    analytics_by_month_tab()