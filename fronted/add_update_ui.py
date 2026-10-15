import streamlit as st
from datetime import datetime
import api_client

def add_update_tab():
    st.subheader("Add or Update Daily Expenses")
    selected_date = st.date_input("Select Date", datetime(2024, 8, 1))

    existing_expenses, source = api_client.fetch_expenses(selected_date)

    categories = ["Rent", "Food", "Shopping", "Entertainment", "glasses", "vehicle", "Other"]

    with st.form(key="Expense_form"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Amount**")
        with col2:
            st.markdown("**Category**")
        with col3:
            st.markdown("**Notes**")

        expenses = []
        for i in range(5):
            if i < len(existing_expenses):
                amount = float(existing_expenses[i].get('amount', 0.0))
                category = existing_expenses[i].get("category", "Shopping")
                notes = existing_expenses[i].get("notes") or ""
            else:
                amount = 0.0
                category = "Shopping"
                notes = ""

            col1, col2, col3 = st.columns(3)
            with col1:
                amount_input = st.number_input(
                    label=f"Amount {i+1}", min_value=0.0, step=1.0, value=amount, key=f"amount_{i}", label_visibility="collapsed"
                )
            with col2:
                cat_index = categories.index(category) if category in categories else 0
                category_input = st.selectbox(
                    label=f"Category {i+1}", options=categories, index=cat_index, key=f"category_{i}", label_visibility="collapsed"
                )
            with col3:
                notes_input = st.text_input(
                    label=f"Notes {i+1}", value=notes, key=f"notes_{i}", label_visibility="collapsed"
                )

            expenses.append({
                "amount": amount_input,
                "category": category_input,
                "notes": notes_input
            })

        submit_button = st.form_submit_button("💾 Save Expenses")
        if submit_button:
            filtered_expense = [expense for expense in expenses if expense['amount'] > 0]
            success, message, _ = api_client.save_expenses(selected_date, filtered_expense)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)