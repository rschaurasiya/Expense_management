from datetime import datetime
import streamlit as st
import requests
import pandas as pd
import calendar

API_URL = "http://localhost:8000"

def analytics_by_month_tab():
    # Get the current year
    current_year = datetime.now().year

    # Create a dropdown (selectbox) for years
    years = list(range(2000, 2101))  # Years from 2000 to 2100
    selected_year = st.selectbox("Select Year", years, index=years.index(current_year))

    if st.button("Get Analytics by Month"):
        try:
            # Call FastAPI backend
            response = requests.get(f"{API_URL}/analytics/{selected_year}")

            if response.status_code == 200:
                result = response.json()

                # Extract the "data" part
                data = result.get("data", [])

                if data:
                    # Convert API response to DataFrame
                    df = pd.DataFrame(data)

                    #Convert month number to month name
                    df["Month"] = df["Month"].apply(lambda x: calendar.month_name[x])
                    # Sort by percentage
                    df_sorted = df.sort_values(by="Percentage_of_Total", ascending=False)

                    # Show title
                    st.subheader(f"Expenses Analytics for {selected_year}")

                    # Show bar chart (Month vs Total Expenses)
                    st.bar_chart(data=df_sorted.set_index("Month")["Total_Expenses_By_Month"])

                    # Format numbers
                    df_sorted["Total_Expenses_By_Month"] = df_sorted["Total_Expenses_By_Month"].map("{:.2f}".format)
                    df_sorted["Percentage_of_Total"] = df_sorted["Percentage_of_Total"].map("{:.2f}".format)

                    # Show final table
                    st.write(df_sorted)
                else:
                    st.warning("No expenses found for this year.")
            else:
                st.error(f"Failed to fetch data: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {str(e)}")

    st.write("You selected year:", selected_year)


