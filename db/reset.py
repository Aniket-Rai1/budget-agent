import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row


def reset_test_database() -> None:
    load_dotenv()
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        raise RuntimeError("TEST_DATABASE_URL is not set")

    conn = psycopg.connect(url, row_factory=dict_row)
    conn.execute(
        "TRUNCATE transactions, subscriptions, goals, sync_state "
        "RESTART IDENTITY CASCADE"
    )
    conn.commit()
    conn.close()
