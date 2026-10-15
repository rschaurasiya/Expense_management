from backend import db_helper

def test_fetch_expense_for_date():
    expenses = db_helper.fetch_expenses_for_date("2024-08-15")
    assert len(expenses) >= 1
    assert expenses[0]["amount"] == 10.0
    assert expenses[0]["category"] == "Shopping"
    assert expenses[0]["notes"] == "Bought potatoes"
     
def test_insert_and_delete_expenses():
    test_date = "9999-12-31"
    db_helper.delete_expenses_for_date(test_date)
    db_helper.insert_expense(test_date, 99.0, "Other", "Automated test item")
    expenses = db_helper.fetch_expenses_for_date(test_date)
    assert len(expenses) == 1
    assert expenses[0]["amount"] == 99.0
    assert expenses[0]["category"] == "Other"
    db_helper.delete_expenses_for_date(test_date)
    assert len(db_helper.fetch_expenses_for_date(test_date)) == 0

    