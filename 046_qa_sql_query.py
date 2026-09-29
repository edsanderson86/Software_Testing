-- sql_queries.sql
-- Run with: sqlite3 practice.db < sql_queries.sql

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total REAL NOT NULL CHECK (total >= 0),
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

INSERT OR IGNORE INTO customers (id, name, email) VALUES
    (1, 'Alex', 'alex@example.test'),
    (2, 'Sam', 'sam@example.test'),
    (3, 'Jo', 'jo@example.test');

INSERT OR IGNORE INTO orders (id, customer_id, total, status) VALUES
    (101, 1, 25.00, 'paid'),
    (102, 1, 80.00, 'pending'),
    (103, 2, 45.00, 'paid');

-- Select specific columns.
SELECT id, name FROM customers;

-- Filter with WHERE.
SELECT id, total FROM orders WHERE status = 'paid';

-- Combine conditions.
SELECT id, total
FROM orders
WHERE status = 'paid' AND total > 30;

-- IN and BETWEEN.
SELECT id, total
FROM orders
WHERE status IN ('paid', 'pending')
  AND total BETWEEN 20 AND 50;

-- Search text.
SELECT name FROM customers WHERE name LIKE 'A%';

-- Sort and limit results.
SELECT id, total
FROM orders
ORDER BY total DESC
LIMIT 2;

-- INNER JOIN: only customers with orders.
SELECT customers.name, orders.id AS order_id, orders.total
FROM customers
INNER JOIN orders ON orders.customer_id = customers.id;

-- LEFT JOIN: include customers with no orders.
SELECT customers.name, orders.id AS order_id
FROM customers
LEFT JOIN orders ON orders.customer_id = customers.id;

-- Aggregate results by customer.
SELECT customers.name,
       COUNT(orders.id) AS order_count,
       COALESCE(SUM(orders.total), 0) AS total_spent
FROM customers
LEFT JOIN orders ON orders.customer_id = customers.id
GROUP BY customers.id, customers.name
ORDER BY total_spent DESC;

-- Filter grouped results.
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) >= 2;

-- Update a row.
UPDATE orders
SET status = 'paid'
WHERE id = 102;

-- Delete a row.
DELETE FROM orders
WHERE id = 103;

-- Verify the final data.
SELECT id, customer_id, total, status
FROM orders
ORDER BY id;