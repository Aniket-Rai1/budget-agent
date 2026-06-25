def get_sync_state(conn, institution):
    row = conn.execute(
        "SELECT * FROM sync_state WHERE institution = %s",
        (institution,),
    ).fetchone()
    return dict(row) if row else None


def upsert_sync_state(conn, institution, cursor, last_synced_at):
    conn.execute(
        """
        INSERT INTO sync_state (institution, cursor, last_synced_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (institution)
        DO UPDATE SET
            cursor = EXCLUDED.cursor,
            last_synced_at = EXCLUDED.last_synced_at
        """,
        (institution, cursor, last_synced_at),
    )
    conn.commit()
