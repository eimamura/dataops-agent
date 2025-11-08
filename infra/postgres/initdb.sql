BEGIN;

CREATE SCHEMA IF NOT EXISTS dataops;
SET search_path TO dataops, public;

CREATE TABLE IF NOT EXISTS dataops.users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dataops.products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS dataops.sales (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES dataops.users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES dataops.products(id) ON DELETE CASCADE,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    total NUMERIC(12, 2) NOT NULL CHECK (total >= 0),
    sold_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO dataops.users (username, email)
VALUES
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('carol', 'carol@example.com')
ON CONFLICT DO NOTHING;

INSERT INTO dataops.products (name, description, price)
VALUES
    ('DataOps Handbook', 'Digital guide for operating data platforms.', 49.99),
    ('Pipeline Support', 'Monthly support subscription.', 199.00),
    ('Training Credits', 'Credits for team enablement sessions.', 999.00)
ON CONFLICT DO NOTHING;

WITH new_sales(user_id, product_id, quantity) AS (
    VALUES
        (1, 1, 1),
        (2, 2, 2),
        (3, 3, 1),
        (1, 3, 1)
)
INSERT INTO dataops.sales (user_id, product_id, quantity, unit_price, total)
SELECT
    ns.user_id,
    ns.product_id,
    ns.quantity,
    p.price AS unit_price,
    p.price * ns.quantity AS total
FROM new_sales ns
JOIN dataops.products p ON p.id = ns.product_id
ON CONFLICT DO NOTHING;

COMMIT;
