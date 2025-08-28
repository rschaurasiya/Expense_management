from backend import db_helper

def test_fetch_expense_for_date():
    expenses = db_helper.fetch_expenses_for_date("2024-08-15")

    assert len(expenses)==1
    assert expenses[0]["amount"]==10.0
    assert expenses[0]["category"]=="Shopping"
    assert expenses[0]["notes"]=="Bought potatoes"
     
def test_delete_expenses_for_date():
    insertion=db_helper.delete_expenses_for_date()

    