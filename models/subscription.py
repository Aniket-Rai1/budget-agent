from datetime import date, timedelta

ALLOWED_UPDATE_FIELDS = {
    "name",
    "amount",
    "cycle",
    "next_billing_date",
    "category",
    "active",
    "notes",
}

_CYCLE_TO_MONTHLY = {
    "weekly": 52 / 12,
    "monthly": 1,
    "quarterly": 1 / 3,
    "annual": 1 / 12,
}


def add_subscription(
    conn,
    name,
    amount,
    cycle,
    next_billing_date,
    category=None,
    active=1,
    notes=None,
):
    row = conn.execute(
        """
        INSERT INTO subscriptions (name, amount, cycle, next_billing_date, category, active, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (name, amount, cycle, next_billing_date, category, active, notes),
    ).fetchone()
    conn.commit()
    return get_subscription(conn, row["id"])


def get_subscription(conn, id):
    row = conn.execute(
        "SELECT * FROM subscriptions WHERE id = %s",
        (id,),
    ).fetchone()
    return dict(row) if row else None


def list_subscriptions(conn, active_only=True):
    if active_only:
        rows = conn.execute(
            "SELECT * FROM subscriptions WHERE active = 1 ORDER BY next_billing_date, id"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM subscriptions ORDER BY next_billing_date, id"
        ).fetchall()
    return [dict(row) for row in rows]


def update_subscription(conn, id, **fields):
    updates = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_FIELDS}
    if not updates:
        return get_subscription(conn, id)

    set_clause = ", ".join(f"{col} = %s" for col in updates)
    values = list(updates.values()) + [id]
    cursor = conn.execute(
        f"UPDATE subscriptions SET {set_clause} WHERE id = %s",
        values,
    )
    conn.commit()
    if cursor.rowcount == 0:
        return None
    return get_subscription(conn, id)


def delete_subscription(conn, id):
    cursor = conn.execute("DELETE FROM subscriptions WHERE id = %s", (id,))
    conn.commit()
    return cursor.rowcount > 0


def subscriptions_due_soon(conn, within_days=7):
    cutoff = (date.today() + timedelta(days=within_days)).isoformat()
    rows = conn.execute(
        """
        SELECT * FROM subscriptions
        WHERE active = 1 AND next_billing_date <= %s
        ORDER BY next_billing_date, id
        """,
        (cutoff,),
    ).fetchall()
    return [dict(row) for row in rows]


def monthly_subscription_total(conn):
    rows = conn.execute(
        "SELECT amount, cycle FROM subscriptions WHERE active = 1"
    ).fetchall()
    total = 0.0
    for row in rows:
        total += row["amount"] * _CYCLE_TO_MONTHLY[row["cycle"]]
    return total
