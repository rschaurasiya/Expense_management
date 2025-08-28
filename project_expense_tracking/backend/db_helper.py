# CRUD process is performed Here(Create Retrive Update Delete) 
import mysql.connector
from contextlib import contextmanager
from logging_setup import setup_Logger
import pandas as pd

logger=setup_Logger("db_helper")
@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="radhe123",
        database="expense_manager"
    )

    cursor = connection.cursor(dictionary=True)
    yield cursor
    if commit:
        connection.commit()
    print("Closing cursor")
    cursor.close()
    connection.close()


def fetch_all_records():
    query = "SELECT * from expenses"

    with get_db_cursor() as cursor:
        cursor.execute(query)
        expenses = cursor.fetchall()
        for expense in expenses:
            print(expense)


def fetch_expenses_for_date(expense_date):
    logger.info(f"fetch_expenses_for_date called with {expense_date}")
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses WHERE expense_date = %s", (expense_date,))
        expenses = cursor.fetchall()
        for expense in expenses:
            print(expense)
        return expenses
    
def get_expenses_for_year(year):
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT 
                MONTH(expense_date) AS month,
                SUM(amount) AS total_expenses
            FROM expenses
            WHERE YEAR(expense_date) = %s
            GROUP BY MONTH(expense_date)
            ORDER BY month
        ''',
            (year,)
        )
        rows = cursor.fetchall()
    df = pd.DataFrame(rows)
    # Rename columns to nicer names
    df.rename(columns={
        "month": "Month",
        "total_expenses": "Total_Expenses_By_Month"
    }, inplace=True)

    # Calculate percentage of total
    total = df["Total_Expenses_By_Month"].sum()
    if total > 0:   # to avoid division by zero
        df["Percentage_of_Total"] = (df["Total_Expenses_By_Month"] / total * 100).round(2)
    else:
        df["Percentage_of_Total"] = 0

    result= df.to_dict(orient="records")
    print(result)
    return result


def insert_expense(expense_date, amount, category, notes):
    logger.info(f"insert_expenses called with date:{expense_date}, amount:{amount}, category: {category}, notes: {notes}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes)
        )


def delete_expenses_for_date(expense_date):
    logger.info(f"delete_expenses_for_date called with {expense_date}")
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))


def fetch_expense_summary(start_date,end_date):
    logger.info(f"fetch_expenses_for_summary called with start_date:{start_date}, end_date: {end_date}")
    with get_db_cursor() as cursor:
        cursor.execute(
            '''SELECT category,sum(amount) as total
               FROM expenses WHERE expense_date
               BETWEEN %s and %s
               GROUP BY category;''',
               (start_date,end_date)
        )
        data=cursor.fetchall()
        return data
    


if __name__ == "__main__":
    # fetch_all_records()

    # expenses=fetch_expenses_for_date("2024-08-01")
    # print(expenses)

    get_expenses_for_year(2024)
    # print(data)
    # insert_expense("2024-08-28", 300, "Food", "chicken")
    # delete_expenses_for_date("2024-08-01")
    # fetch_expenses_for_date("2024-08-20")
   
#    print(fetch_expense_summary("2024-08-05","2024-08-10"))

    # summary=fetch_expense_summary("2024-08-05","2024-08-10")
    # for record in summary:
    #     print(record)

    