import os
import sys

# Ensure root, fronted, and backend directories are in sys.path
_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
_FRONTED_DIR = os.path.join(_ROOT_DIR, "fronted")
_BACKEND_DIR = os.path.join(_ROOT_DIR, "backend")

for path in [_ROOT_DIR, _FRONTED_DIR, _BACKEND_DIR]:
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
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom header styling
st.title("💸 Expense Management System")

# Check backend status in the sidebar
with st.sidebar:
    st.header("⚙️ System Status")
    backend_online = api_client.is_backend_online()
    if backend_online:
        st.success("🟢 FastAPI API: Connected")
        st.caption(f"Endpoint: {api_client.get_api_url()}")
    else:
        st.info("🔵 Standalone Cloud Mode: Active")
        st.caption("Running with direct database connection (MySQL / SQLite fallback).")

    st.divider()
    st.markdown("### 📊 Features")
    st.markdown("- **Daily Expenses**: Record & edit daily expenses")
    st.markdown("- **Category Analytics**: Spending breakdown")
    st.markdown("- **Monthly Trends**: Yearly distribution")

    st.divider()
    st.markdown("### ☁️ Deployment Info")
    st.caption("Ready for Streamlit Community Cloud. Works out-of-the-box with automated database fallback or cloud MySQL.")

# Streamlit tab creation
tab1, tab2, tab3 = st.tabs([
    "📝 Add / Update Expenses",
    "📊 Analytics By Categories",
    "📅 Analytics By Months"
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
