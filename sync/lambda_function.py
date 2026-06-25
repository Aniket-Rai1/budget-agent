import json
import logging
import os
from datetime import date, datetime, timedelta, timezone

from db.connection import get_connection
from models.sync_state import get_sync_state, upsert_sync_state
from models.transaction import delete_transaction_by_plaid_id, upsert_transaction
from plaid_client import get_transactions_sync

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

INITIAL_SYNC_DAYS = int(os.getenv("INITIAL_SYNC_DAYS", 90))


def _map_plaid_transaction(txn):
    plaid_amount = txn.amount
    return {
        "plaid_transaction_id": txn.transaction_id,
        "amount": abs(plaid_amount),
        "type": "expense" if plaid_amount > 0 else "income",
        "date": str(txn.date),
        "merchant": txn.merchant_name or txn.name,
        "category": None,
        "source": "plaid",
    }


def _sync_institution(conn, institution, access_token):
    state = get_sync_state(conn, institution)
    cursor = state["cursor"] if state else None
    first_sync = cursor is None

    added, modified, removed, next_cursor = get_transactions_sync(access_token, cursor)

    if first_sync:
        cutoff = (date.today() - timedelta(days=INITIAL_SYNC_DAYS)).isoformat()
        added = [txn for txn in added if str(txn.date) >= cutoff]

    for txn in added:
        upsert_transaction(conn, **_map_plaid_transaction(txn))

    for txn in modified:
        upsert_transaction(conn, **_map_plaid_transaction(txn))

    for txn in removed:
        delete_transaction_by_plaid_id(conn, txn.transaction_id)

    upsert_sync_state(conn, institution, next_cursor, datetime.now(timezone.utc))

    logger.info(
        {
            "institution": institution,
            "added": len(added),
            "modified": len(modified),
            "removed": len(removed),
            "first_sync": first_sync,
        }
    )

    return {
        "added": len(added),
        "modified": len(modified),
        "removed": len(removed),
        "first_sync": first_sync,
    }


def lambda_handler(event, context):
    linked_accounts = json.loads(os.environ["LINKED_ACCOUNTS"])
    summary = {}

    conn = get_connection(os.environ["DATABASE_URL"])
    try:
        for entry in linked_accounts:
            institution = entry["institution"]
            access_token_env = entry["access_token_env"]
            if access_token_env not in os.environ:
                raise KeyError(
                    f"Missing environment variable {access_token_env} "
                    f"for institution {institution}"
                )
            access_token = os.environ[access_token_env]
            summary[institution] = _sync_institution(conn, institution, access_token)
    finally:
        conn.close()

    return summary
