from datetime import date, timedelta

from models.subscription import (
    add_subscription,
    delete_subscription,
    get_subscription,
    list_subscriptions,
    monthly_subscription_total,
    subscriptions_due_soon,
    update_subscription,
)


def test_add_and_get_subscription(conn):
    sub = add_subscription(
        conn,
        name="Netflix",
        amount=15.99,
        cycle="monthly",
        next_billing_date="2025-07-01",
        category="entertainment",
    )
    assert sub["name"] == "Netflix"
    assert sub["amount"] == 15.99
    assert sub["active"] == 1

    fetched = get_subscription(conn, sub["id"])
    assert fetched == sub


def test_get_subscription_missing(conn):
    assert get_subscription(conn, 999) is None


def test_list_subscriptions_active_only(conn):
    active = add_subscription(
        conn, "Spotify", 9.99, "monthly", "2025-07-01"
    )
    add_subscription(conn, "Old Gym", 30.0, "monthly", "2025-07-01", active=0)

    active_only = list_subscriptions(conn, active_only=True)
    assert len(active_only) == 1
    assert active_only[0]["id"] == active["id"]

    all_subs = list_subscriptions(conn, active_only=False)
    assert len(all_subs) == 2


def test_update_subscription_only_changes_passed_fields(conn):
    sub = add_subscription(
        conn,
        name="Netflix",
        amount=15.99,
        cycle="monthly",
        next_billing_date="2025-07-01",
        category="entertainment",
        notes="family plan",
    )
    updated = update_subscription(conn, sub["id"], amount=19.99)
    assert updated["amount"] == 19.99
    assert updated["name"] == "Netflix"
    assert updated["category"] == "entertainment"
    assert updated["notes"] == "family plan"


def test_update_subscription_missing(conn):
    assert update_subscription(conn, 999, amount=10.0) is None


def test_delete_subscription(conn):
    sub = add_subscription(conn, "Hulu", 7.99, "monthly", "2025-07-01")
    assert delete_subscription(conn, sub["id"]) is True
    assert get_subscription(conn, sub["id"]) is None
    assert delete_subscription(conn, sub["id"]) is False


def test_subscriptions_due_soon(conn):
    today = date.today()
    due_date = (today + timedelta(days=3)).isoformat()
    far_date = (today + timedelta(days=30)).isoformat()
    past_date = (today - timedelta(days=1)).isoformat()

    due = add_subscription(conn, "Due Soon", 10.0, "monthly", due_date)
    add_subscription(conn, "Far Away", 20.0, "monthly", far_date)
    add_subscription(conn, "Inactive Due", 5.0, "monthly", due_date, active=0)
    overdue = add_subscription(conn, "Overdue", 8.0, "monthly", past_date)

    results = subscriptions_due_soon(conn, within_days=7)
    ids = {s["id"] for s in results}
    assert due["id"] in ids
    assert overdue["id"] in ids
    assert len(results) == 2


def test_monthly_subscription_total(conn):
    add_subscription(conn, "Weekly", 10.0, "weekly", "2025-07-01")
    add_subscription(conn, "Monthly", 30.0, "monthly", "2025-07-01")
    add_subscription(conn, "Quarterly", 90.0, "quarterly", "2025-07-01")
    add_subscription(conn, "Annual", 120.0, "annual", "2025-07-01")
    add_subscription(conn, "Inactive", 100.0, "monthly", "2025-07-01", active=0)

    total = monthly_subscription_total(conn)
    expected = 10.0 * (52 / 12) + 30.0 + 90.0 / 3 + 120.0 / 12
    assert abs(total - expected) < 0.01
