CREATE TABLE IF NOT EXISTS transactions (
    id                   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    amount               REAL NOT NULL,
    type                 TEXT NOT NULL CHECK(type IN ('income', 'expense')),
    date                 TEXT NOT NULL,
    merchant             TEXT,
    category             TEXT,
    subcategory          TEXT,
    notes                TEXT,
    source               TEXT DEFAULT 'manual',
    plaid_transaction_id TEXT UNIQUE,
    created_at           TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name              TEXT NOT NULL,
    amount            REAL NOT NULL,
    cycle             TEXT NOT NULL CHECK(cycle IN ('weekly','monthly','quarterly','annual')),
    next_billing_date TEXT NOT NULL,
    category          TEXT,
    active            INTEGER DEFAULT 1,
    notes             TEXT,
    created_at        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS goals (
    id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name       TEXT NOT NULL,
    type       TEXT NOT NULL CHECK(type IN ('savings','investment','spending_limit')),
    target     REAL NOT NULL,
    current    REAL DEFAULT 0.0,
    deadline   TEXT,
    period     TEXT CHECK(period IN ('weekly','monthly','annual',NULL)),
    active     INTEGER DEFAULT 1,
    notes      TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sync_state (
    institution    TEXT PRIMARY KEY,
    cursor         TEXT,
    last_synced_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
CREATE INDEX IF NOT EXISTS idx_transactions_merchant ON transactions(merchant);
CREATE INDEX IF NOT EXISTS idx_transactions_plaid_id ON transactions(plaid_transaction_id);
