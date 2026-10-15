from datetime import datetime
import streamlit as st
import pandas as pd

try:
    from fronted import api_client
except (ImportError, KeyError):
    import api_client

def analytics_tab():
    st.subheader("Category-wise Expense Analytics")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime(2024, 8, 1))
    with col2:
        end_date = st.date_input("End Date", datetime(2024, 8, 5))

    st.button("Get Analytics", key="btn_cat_analytics")

    if start_date > end_date:
        st.error("Start Date must be before or equal to End Date.")
        return

    result, source = api_client.fetch_category_analytics(start_date, end_date)

    if not result:
        st.info("No expenses found for the selected date range.")
    else:
        data = {
            "Category": list(result.keys()),
            "Total": [result[category]["total"] for category in result],
            "Percentage": [result[category]["percentage"] for category in result]
        }

        df = pd.DataFrame(data)
        df_sorted = df.sort_values(by="Percentage", ascending=False)

        st.markdown("### Expense Breakdown By Category (%)")
        st.bar_chart(data=df_sorted.set_index("Category")["Percentage"])

        df_display = df_sorted.copy()
        df_display["Total"] = df_display["Total"].map("{:.2f}".format)
        df_display["Percentage"] = df_display["Percentage"].map("{:.2f}%".format)

        st.dataframe(df_display, use_container_width=True)