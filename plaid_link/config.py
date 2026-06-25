import os

import plaid
from dotenv import load_dotenv

load_dotenv()

PRODUCTS = ["transactions"]
COUNTRY_CODES = ["US"]
CLIENT_NAME = "Budget Agent"
CLIENT_USER_ID = "local-user-1"

CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
SECRET = os.getenv("PLAID_SECRET")
ENV = os.getenv("PLAID_ENV", "production")

_ENV_MAP = {
    "production": plaid.Environment.Production,
    "sandbox": plaid.Environment.Sandbox,
    "development": plaid.Environment.Sandbox,
}


def get_plaid_environment() -> plaid.Environment:
    return _ENV_MAP.get(ENV.lower(), plaid.Environment.Production)
