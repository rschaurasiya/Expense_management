# Importing module
import streamlit as st
from add_update_ui import add_update_tab
from analytics_ui import analytics_tab
from analtics_month import analytics_by_month_tab


# Streamlit Title
st.title("Expense Track Management")


# Streamlit tab creation
tab1,tab2,tab3=st.tabs(["Add/Update","Analytics By Catogories","Analytics By Months"])

# working with tab1
with tab1:
    add_update_tab()
     
with tab2:
    analytics_tab()

with tab3:
    analytics_by_month_tab()

                   




# st.title("Expense Management system")
# expense_dt=st.date_input("Expense Date: ")
# if expense_dt:
#     st.write(f"Fetching expense for the {expense_dt}")


#Text Element
# st.header("Streamlit core features")
# st.subheader("Text Elements")
# st.text("This is a simple text element.")

# #Data display
# st.subheader("Data display")
# st.write("Here is s simple table:")
# st.table({"Column 1":[1,2,3],"Column 2":[4,5,6]})