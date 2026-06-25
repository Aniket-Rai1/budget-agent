# Budget Sync — AWS Lambda deployment

This folder packages a Lambda function that syncs Plaid transactions into Supabase Postgres on a daily schedule. Build the zip locally; deploy manually in the AWS Console.

## Build

From the repo root:

```bash
bash sync/build_deployment_package.sh
```

Produces `sync/deployment_package.zip`. This phase does not automate AWS deployment.

## AWS Console setup

### 1. Build the package

Run the command above.

### 2. Create the Lambda function

AWS Console → Lambda → Create function → Author from scratch

- Runtime: **Python 3.12**
- Name: `budget-sync`

### 3. Upload code

Code source → Upload from → .zip file → select `sync/deployment_package.zip`

### 4. Set the handler

Configuration → Runtime settings → Edit handler:

```
lambda_function.lambda_handler
```

### 5. Environment variables

Configuration → Environment variables → add:

| Variable | Required | Notes |
|----------|----------|-------|
| `DATABASE_URL` | yes | Supabase Postgres connection string |
| `PLAID_CLIENT_ID` | yes | |
| `PLAID_SECRET` | yes | |
| `PLAID_ENV` | yes | e.g. `production` |
| `LINKED_ACCOUNTS` | yes | JSON array — see example below |
| `INITIAL_SYNC_DAYS` | no | Defaults to `90` if unset |
| `PLAID_ACCESS_TOKEN_BOA` | yes* | *Required if referenced in `LINKED_ACCOUNTS` |
| `PLAID_ACCESS_TOKEN_CAPONE` | yes* | |
| `PLAID_ACCESS_TOKEN_CHASE` | yes* | |
| `PLAID_ITEM_ID_BOA` | no | For reference / future use; handler does not read these |
| `PLAID_ITEM_ID_CAPONE` | no | |
| `PLAID_ITEM_ID_CHASE` | no | |

Example `LINKED_ACCOUNTS` value:

```
[{"institution":"BOA","access_token_env":"PLAID_ACCESS_TOKEN_BOA"},{"institution":"CAPONE","access_token_env":"PLAID_ACCESS_TOKEN_CAPONE"},{"institution":"CHASE","access_token_env":"PLAID_ACCESS_TOKEN_CHASE"}]
```

Adding a 4th bank later: add its access token env var and update `LINKED_ACCOUNTS` — no code change required.

Paste values from your local `.env`.

### 6. Increase timeout

Configuration → General configuration → Edit → Timeout → **60 seconds**

(Default 3 seconds is too short for Plaid pagination and DB writes.)

### 7. Manual test

Test tab → Create test event (input body is ignored) → Test

Check the execution result and CloudWatch logs. Each institution should log a structured entry with `added`, `modified`, `removed`, and `first_sync` counts.

### 8. EventBridge schedule

Add trigger → EventBridge (CloudWatch Events) → Create a new rule → Schedule expression:

```
cron(0 11 * * ? *)
```

This is 6am EST in UTC. EventBridge cron is always UTC, so during daylight saving time the run shifts by one hour (EDT). Known limitation — adjust the cron expression twice a year if you need a fixed local time.

### 9. Confirm trigger enabled

Save and verify the EventBridge trigger shows as enabled.

## Verification

After a successful manual test:

- Rows appear in Supabase `transactions` with `source='plaid'` and populated `plaid_transaction_id`
- `sync_state` rows updated with `cursor` and `last_synced_at` per institution
- CloudWatch logs show structured `logger.info` entries per institution (no `print` output)
