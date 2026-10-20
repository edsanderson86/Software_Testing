-- sql_queries.sql
-- Run with: sqlite3 practice.db < sql_queries.sql
-- Demonstrate related tables, filtering, joins, aggregation, and data changes.
-- Updates and deletions persist in practice.db.

-- Enforce foreign-key relationships for this database connection.
PRAGMA foreign_keys = ON;

-- Store customers with unique IDs and email addresses.
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

-- Link each order to an existing customer and reject negative totals.
-- REAL is sufficient for this exercise; integer minor units are preferable
-- when exact monetary calculations are required.
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total REAL NOT NULL CHECK (total >= 0),
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

-- Add sample customers, skipping rows that violate applicable constraints.
-- Existing records are not reset to these sample values.
INSERT OR IGNORE INTO customers (id, name, email) VALUES
    (1, 'Alex', 'alex@example.test'),
    (2, 'Sam', 'sam@example.test'),
    (3, 'Jo', 'jo@example.test');

-- Add orders for Alex and Sam, leaving Jo without an order.
INSERT OR IGNORE INTO orders (id, customer_id, total, status) VALUES
    (101, 1, 25.00, 'paid'),
    (102, 1, 80.00, 'pending'),
    (103, 2, 45.00, 'paid');

-- Retrieve selected customer attributes.
-- Without ORDER BY, result order is not guaranteed.
SELECT id, name
FROM customers;

-- Return only orders whose status is paid.
SELECT id, total
FROM orders
WHERE status = 'paid';

-- Require both a paid status and a total greater than 30.
SELECT id, total
FROM orders
WHERE status = 'paid'
  AND total > 30;

-- Match either listed status and an inclusive total range from 20 to 50.
SELECT id, total
FROM orders
WHERE status IN ('paid', 'pending')
  AND total BETWEEN 20 AND 50;

-- Find names beginning with A; % matches any following characters.
SELECT name
FROM customers
WHERE name LIKE 'A%';

-- Return the two largest order totals.
SELECT id, total
FROM orders
ORDER BY total DESC
LIMIT 2;

-- Match customers to their orders.
-- Customers without orders are excluded; multiple orders produce multiple rows.
SELECT customers.name, orders.id AS order_id, orders.total
FROM customers
INNER JOIN orders ON orders.customer_id = customers.id;

-- Retain every customer, including those without orders.
-- An unmatched customer's order_id is NULL.
SELECT customers.name, orders.id AS order_id
FROM customers
LEFT JOIN orders ON orders.customer_id = customers.id;

-- Summarize orders for each customer.
-- COUNT(orders.id) excludes NULL, giving customers without orders a count of zero.
-- COALESCE replaces a NULL sum with zero.
-- The total_spent alias includes all order statuses, including pending orders.
SELECT customers.name,
       COUNT(orders.id) AS order_count,
       COALESCE(SUM(orders.total), 0) AS total_spent
FROM customers
LEFT JOIN orders ON orders.customer_id = customers.id
GROUP BY customers.id, customers.name
ORDER BY total_spent DESC;

-- Filter after grouping to return customers with at least two orders.
-- HAVING applies to groups; WHERE filters individual rows before grouping.
SELECT customer_id, COUNT(*) AS order_count
FROM orders
GROUP BY customer_id
HAVING COUNT(*) >= 2;

-- Change only order 102 to paid.
UPDATE orders
SET status = 'paid'
WHERE id = 102;

-- Remove only order 103, preserving its customer record.
DELETE FROM orders
WHERE id = 103;

-- Inspect the remaining orders after the update and deletion.
SELECT id, customer_id, total, status
FROM orders
ORDER BY id;