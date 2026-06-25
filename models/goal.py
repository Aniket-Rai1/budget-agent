ALLOWED_UPDATE_FIELDS = {
    "name",
    "type",
    "target",
    "current",
    "deadline",
    "period",
    "active",
    "notes",
}


def add_goal(
    conn,
    name,
    type,
    target,
    current=0.0,
    deadline=None,
    period=None,
    active=1,
    notes=None,
):
    row = conn.execute(
        """
        INSERT INTO goals (name, type, target, current, deadline, period, active, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (name, type, target, current, deadline, period, active, notes),
    ).fetchone()
    conn.commit()
    return get_goal(conn, row["id"])


def get_goal(conn, id):
    row = conn.execute(
        "SELECT * FROM goals WHERE id = %s",
        (id,),
    ).fetchone()
    return dict(row) if row else None


def list_goals(conn, active_only=True):
    if active_only:
        rows = conn.execute(
            "SELECT * FROM goals WHERE active = 1 ORDER BY id"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM goals ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]


def update_goal(conn, id, **fields):
    updates = {k: v for k, v in fields.items() if k in ALLOWED_UPDATE_FIELDS}
    if not updates:
        return get_goal(conn, id)

    set_clause = ", ".join(f"{col} = %s" for col in updates)
    values = list(updates.values()) + [id]
    cursor = conn.execute(
        f"UPDATE goals SET {set_clause} WHERE id = %s",
        values,
    )
    conn.commit()
    if cursor.rowcount == 0:
        return None
    return get_goal(conn, id)


def delete_goal(conn, id):
    cursor = conn.execute("DELETE FROM goals WHERE id = %s", (id,))
    conn.commit()
    return cursor.rowcount > 0


def update_goal_progress(conn, id, new_current):
    return update_goal(conn, id, current=new_current)


def goal_progress_summary(conn):
    rows = conn.execute(
        "SELECT id, name, type, target, current FROM goals WHERE active = 1 ORDER BY id"
    ).fetchall()
    summary = []
    for row in rows:
        target = row["target"]
        current = row["current"]
        progress_pct = round(current / target * 100, 2) if target > 0 else 0.0
        summary.append(
            {
                "id": row["id"],
                "name": row["name"],
                "type": row["type"],
                "target": target,
                "current": current,
                "progress_pct": progress_pct,
            }
        )
    return summary
