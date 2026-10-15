from datetime import datetime
import streamlit as st
import pandas as pd
import calendar
import api_client

def analytics_by_month_tab():
    st.subheader("Monthly Expense Analytics")
    
    # Dynamically fetch available years from database
    available_years = api_client.get_available_years()
    if not available_years:
        available_years = [2024, datetime.now().year]

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_year = st.selectbox("Select Year", available_years, index=0, key="select_year_analytics")
    with col2:
        st.write("")
        st.write("")
        refresh_clicked = st.button("Refresh", key="btn_month_analytics")

    # Automatically fetch and display analytics for the selected year
    data, source = api_client.fetch_monthly_analytics(selected_year)

    if data:
        df = pd.DataFrame(data)
        # Convert month integer to full month name
        df["Month"] = df["Month"].apply(lambda x: calendar.month_name[int(x)])
        df_sorted = df.sort_values(by="Percentage_of_Total", ascending=False)

        st.markdown(f"### Expenses Analytics for {selected_year}")
        st.bar_chart(data=df_sorted.set_index("Month")["Total_Expenses_By_Month"])

        df_display = df_sorted.copy()
        df_display["Total_Expenses_By_Month"] = df_display["Total_Expenses_By_Month"].map("{:.2f}".format)
        df_display["Percentage_of_Total"] = df_display["Percentage_of_Total"].map("{:.2f}%".format)

        st.dataframe(df_display, use_container_width=True)
    else:
        st.info(f"No expenses found for year {selected_year}.")
