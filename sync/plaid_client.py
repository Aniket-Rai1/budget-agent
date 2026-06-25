import os

import plaid
from plaid.api import plaid_api
from plaid.model.transactions_sync_request import TransactionsSyncRequest

_ENV_MAP = {
    "production": plaid.Environment.Production,
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Sandbox,
}


def _get_plaid_environment() -> plaid.Environment:
    env = os.environ.get("PLAID_ENV", "production").lower()
    return _ENV_MAP.get(env, plaid.Environment.Production)


_configuration = plaid.Configuration(
    host=_get_plaid_environment(),
    api_key={
        "clientId": os.environ["PLAID_CLIENT_ID"],
        "secret": os.environ["PLAID_SECRET"],
    },
)
_client = plaid_api.PlaidApi(plaid.ApiClient(_configuration))


def get_transactions_sync(access_token, cursor=None):
    all_added = []
    all_modified = []
    all_removed = []
    next_cursor = cursor

    while True:
        request = TransactionsSyncRequest(
            access_token=access_token,
            cursor=next_cursor,
        )
        response = _client.transactions_sync(request)

        all_added.extend(response.added)
        all_modified.extend(response.modified)
        all_removed.extend(response.removed)
        next_cursor = response.next_cursor

        if not response.has_more:
            break

    return all_added, all_modified, all_removed, next_cursor
