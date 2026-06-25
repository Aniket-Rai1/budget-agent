# Plaid Link — one-time bank connection

Run this flow once per bank to obtain Plaid access tokens and item IDs. After all three banks are connected, you do not need to run this again unless reconnecting a bank.

## Prerequisites

Add to `.env` in the repo root:

```
PLAID_CLIENT_ID=<your client id>
PLAID_SECRET=<your production secret>
PLAID_ENV=production
```

## Steps

1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python plaid_link/server.py`
3. Open **http://localhost:5000** in a browser (do not open `link.html` directly — CORS will block `fetch()` from `file://`)
4. Click **Connect Bank Account**, search for and select your bank in Plaid Link, complete login + MFA
5. Terminal prints:
   ```
   Connected: <institution from Plaid>
   Access Token: ...
   Item ID: ...
   ```
6. Copy the access token and item ID into `.env` using the matching variable names:

   | Institution (from terminal) | Access token var | Item ID var |
   |-----------------------------|------------------|-------------|
   | Bank of America | `PLAID_ACCESS_TOKEN_BOA` | `PLAID_ITEM_ID_BOA` |
   | Capital One | `PLAID_ACCESS_TOKEN_CAPONE` | `PLAID_ITEM_ID_CAPONE` |
   | Chase | `PLAID_ACCESS_TOKEN_CHASE` | `PLAID_ITEM_ID_CHASE` |

7. Repeat steps 4–6 for the remaining two banks (3 connections total)
8. Stop the server — phase done

## Security notes

- Access tokens are printed to the terminal only — copy them into `.env` manually
- `connections_log.txt` (if created) stores timestamp, institution, and item_id only — never access tokens
- `.env` and `connections_log.txt` are gitignored
