ALLOWED_UPDATE_FIELDS = {
    "amount",
    "type",
    "date",
    "merchant",
    "category",
    "subcategory",
    "notes",
    "source",
}


def add_transaction(
    conn,
    amount,
    type,
    date,
    merchant=None,
    category=None,
    subcategory=None,
    notes=None,
    source="manual",
):
    row = conn.execute(
        """
        INSERT INTO transactions (amount, type, date, merchant, category, subcategory, notes, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (amount, type, date, merchant, category, subcategory, notes, source),
    ).fetchone()
    conn.commit()
    return get_transaction(conn, row["id"])


def get_transaction(conn, id):
    row = conn.execute(
        "SELECT * FROM transactions WHERE id = %s",
        (id,),
    ).fetchone()
    return dict(row) if row else None


def list_transactions(
    conn,
    start_date=None,
    end_date=None,
    category=None,
    type=None,
):
    conditions = []
    params = []

    if start_date is not None:
        conditions.append("date >= %s")
        params.append(start_date)
    if end_date is not None:
        conditions.append("date <= %s")
        params.append(end_date)
    if category is not None:
        conditions.append("category = %s")
        params.append(category)
    if type is not None:
        conditions.append("type = %s")
        params.append(type)

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    rows = conn.execute(
        f"SELECT * FROM transactions {where} ORDER BY date DESC, id DESC",
        params,
    ).fetchall()
    return [dict(row) for row in rows]


def update_transaction(conn, id, **fields):
    updates = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_FIELDS}
    if not updates:
        return get_transaction(conn, id)

    set_clause = ", ".join(f"{col} = %s" for col in updates)
    values = list(updates.values()) + [id]
    cursor = conn.execute(
        f"UPDATE transactions SET {set_clause} WHERE id = %s",
        values,
    )
    conn.commit()
    if cursor.rowcount == 0:
        return None
    return get_transaction(conn, id)


def delete_transaction(conn, id):
    cursor = conn.execute("DELETE FROM transactions WHERE id = %s", (id,))
    conn.commit()
    return cursor.rowcount > 0


def upsert_transaction(
    conn,
    plaid_transaction_id,
    amount,
    type,
    date,
    merchant=None,
    category=None,
    source="plaid",
):
    conn.execute(
        """
        INSERT INTO transactions (plaid_transaction_id, amount, type, date, merchant, category, source)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (plaid_transaction_id)
        DO UPDATE SET
            amount = EXCLUDED.amount,
            type = EXCLUDED.type,
            date = EXCLUDED.date,
            merchant = EXCLUDED.merchant,
            source = EXCLUDED.source
        """,
        (plaid_transaction_id, amount, type, date, merchant, category, source),
    )
    conn.commit()


def delete_transaction_by_plaid_id(conn, plaid_transaction_id):
    cursor = conn.execute(
        "DELETE FROM transactions WHERE plaid_transaction_id = %s",
        (plaid_transaction_id,),
    )
    conn.commit()
    return cursor.rowcount > 0


def spending_by_category(conn, start_date=None, end_date=None):
    conditions = ["type = 'expense'"]
    params = []

    if start_date is not None:
        conditions.append("date >= %s")
        params.append(start_date)
    if end_date is not None:
        conditions.append("date <= %s")
        params.append(end_date)

    where = " AND ".join(conditions)
    rows = conn.execute(
        f"""
        SELECT category, SUM(amount) AS total
        FROM transactions
        WHERE {where}
        GROUP BY category
        ORDER BY total DESC, category DESC
        """,
        params,
    ).fetchall()
    return [dict(row) for row in rows]
