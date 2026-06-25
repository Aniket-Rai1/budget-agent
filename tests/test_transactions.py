from models.transaction import (
    add_transaction,
    delete_transaction,
    get_transaction,
    list_transactions,
    spending_by_category,
    update_transaction,
)


def test_add_and_get_transaction(conn):
    txn = add_transaction(
        conn,
        amount=50.0,
        type="expense",
        date="2025-06-01",
        merchant="Coffee Shop",
        category="food",
    )
    assert txn["amount"] == 50.0
    assert txn["type"] == "expense"
    assert txn["merchant"] == "Coffee Shop"
    assert txn["source"] == "manual"

    fetched = get_transaction(conn, txn["id"])
    assert fetched == txn


def test_get_transaction_missing(conn):
    assert get_transaction(conn, 999) is None


def test_list_transactions_with_filters(conn):
    add_transaction(conn, 100.0, "expense", "2025-06-01", category="food")
    add_transaction(conn, 200.0, "expense", "2025-06-15", category="transport")
    add_transaction(conn, 3000.0, "income", "2025-06-20", category="salary")

    all_txns = list_transactions(conn)
    assert len(all_txns) == 3

    expenses = list_transactions(conn, type="expense")
    assert len(expenses) == 2

    june = list_transactions(conn, start_date="2025-06-01", end_date="2025-06-10")
    assert len(june) == 1
    assert june[0]["category"] == "food"

    food = list_transactions(conn, category="food")
    assert len(food) == 1


def test_update_transaction_only_changes_passed_fields(conn):
    txn = add_transaction(
        conn,
        amount=50.0,
        type="expense",
        date="2025-06-01",
        merchant="Coffee Shop",
        category="food",
        notes="morning coffee",
    )
    updated = update_transaction(conn, txn["id"], amount=75.0)
    assert updated["amount"] == 75.0
    assert updated["merchant"] == "Coffee Shop"
    assert updated["category"] == "food"
    assert updated["notes"] == "morning coffee"


def test_update_transaction_missing(conn):
    assert update_transaction(conn, 999, amount=10.0) is None


def test_delete_transaction(conn):
    txn = add_transaction(conn, 25.0, "expense", "2025-06-01")
    assert delete_transaction(conn, txn["id"]) is True
    assert get_transaction(conn, txn["id"]) is None
    assert delete_transaction(conn, txn["id"]) is False


def test_spending_by_category(conn):
    add_transaction(conn, 50.0, "expense", "2025-06-01", category="food")
    add_transaction(conn, 30.0, "expense", "2025-06-05", category="food")
    add_transaction(conn, 100.0, "expense", "2025-06-10", category="transport")
    add_transaction(conn, 5000.0, "income", "2025-06-15", category="salary")
    add_transaction(conn, 20.0, "expense", "2025-07-01", category="food")

    totals = spending_by_category(conn)
    assert len(totals) == 2
    assert totals[0]["category"] == "transport"
    assert totals[0]["total"] == 100.0
    assert totals[1]["category"] == "food"
    assert totals[1]["total"] == 100.0

    june_totals = spending_by_category(conn, start_date="2025-06-01", end_date="2025-06-30")
    assert len(june_totals) == 2
    food_total = next(t for t in june_totals if t["category"] == "food")
    assert food_total["total"] == 80.0
