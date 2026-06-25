import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def get_connection(database_url: str | None = None) -> psycopg.Connection:
    if load_dotenv is not None:
        load_dotenv()
    url = database_url or os.environ["DATABASE_URL"]
    return psycopg.connect(url, row_factory=dict_row)


def init_db(conn: psycopg.Connection | None = None) -> None:
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    schema = _SCHEMA_PATH.read_text()
    for statement in schema.split(";"):
        stmt = statement.strip()
        if stmt:
            conn.execute(stmt)
    conn.commit()

    if close_after:
        conn.close()
