from datetime import datetime, timezone
from pathlib import Path

import plaid
from flask import Flask, jsonify, request, send_file
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products

import config

app = Flask(__name__)
_DIR = Path(__file__).parent
_CONNECTIONS_LOG = _DIR / "connections_log.txt"

configuration = plaid.Configuration(
    host=config.get_plaid_environment(),
    api_key={
        "clientId": config.CLIENT_ID,
        "secret": config.SECRET,
    },
)
plaid_client = plaid_api.PlaidApi(plaid.ApiClient(configuration))


def _append_connection_log(institution: str, item_id: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    with _CONNECTIONS_LOG.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp}\t{institution}\t{item_id}\n")


@app.get("/")
def index():
    return send_file(_DIR / "link.html")


@app.post("/create_link_token")
def create_link_token():
    try:
        link_request = LinkTokenCreateRequest(
            products=[Products(p) for p in config.PRODUCTS],
            client_name=config.CLIENT_NAME,
            country_codes=[CountryCode(c) for c in config.COUNTRY_CODES],
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=config.CLIENT_USER_ID),
        )
        response = plaid_client.link_token_create(link_request)
        return jsonify({"link_token": response.link_token})
    except Exception as e:
        print(f"Error creating link token: {e}")
        return jsonify({"error": str(e)}), 500


@app.post("/exchange_public_token")
def exchange_public_token():
    data = request.get_json(silent=True) or {}
    public_token = data.get("public_token")
    institution = data.get("institution", "Unknown")

    if not public_token:
        return jsonify({"error": "public_token is required"}), 400

    try:
        exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(exchange_request)
        access_token = response.access_token
        item_id = response.item_id

        print(f"\nConnected: {institution}")
        print(f"Access Token: {access_token}")
        print(f"Item ID: {item_id}\n")

        _append_connection_log(institution, item_id)
        return jsonify({"ok": True})
    except Exception as e:
        print(f"Error exchanging public token: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
