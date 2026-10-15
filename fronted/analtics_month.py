from datetime import datetime
import streamlit as st
import pandas as pd
import calendar
import api_client

def analytics_by_month_tab():
    st.subheader("Monthly Expense Analytics")
    current_year = datetime.now().year
    years = list(range(2020, 2031))
    default_year = 2024 if 2024 in years else current_year
    selected_year = st.selectbox("Select Year", years, index=years.index(default_year), key="select_year_analytics")

    if st.button("Get Analytics by Month", key="btn_month_analytics"):
        data, source = api_client.fetch_monthly_analytics(selected_year)

        if data:
            df = pd.DataFrame(data)
            # Convert month number to month name
            df["Month"] = df["Month"].apply(lambda x: calendar.month_name[int(x)])
            df_sorted = df.sort_values(by="Percentage_of_Total", ascending=False)

            st.markdown(f"### Expenses Analytics for {selected_year}")
            st.bar_chart(data=df_sorted.set_index("Month")["Total_Expenses_By_Month"])

            df_display = df_sorted.copy()
            df_display["Total_Expenses_By_Month"] = df_display["Total_Expenses_By_Month"].map("{:.2f}".format)
            df_display["Percentage_of_Total"] = df_display["Percentage_of_Total"].map("{:.2f}%".format)

            st.dataframe(df_display, use_container_width=True)
        else:
            st.warning(f"No expenses found for year {selected_year}.")
