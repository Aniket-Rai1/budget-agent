import os

import pytest
from dotenv import load_dotenv

from db.connection import get_connection, init_db
from db.reset import reset_test_database


@pytest.fixture(scope="session", autouse=True)
def _ensure_test_schema():
    load_dotenv()
    conn = get_connection(os.environ["TEST_DATABASE_URL"])
    init_db(conn)
    conn.close()


@pytest.fixture
def conn():
    reset_test_database()
    c = get_connection(os.environ["TEST_DATABASE_URL"])
    yield c
    c.close()
