# Module 7: Views, Indexes & Constraints

This module covers data integrity enforcement via constraints, abstraction and security with SQL Views, performance indexing strategies (B-Tree, Composite, Partial, Expression-based), and query optimization using `EXPLAIN ANALYZE`.

---

## Practical Setup Schema: Financial Accounts & Audit Logs

```sql
CREATE TABLE account_types (
    type_id INT PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO type_names VALUES (1, 'Checking'), (2, 'Savings'), (3, 'Investment');
```

---

## Practical Problem 1: Table Constraints & Referential Integrity Cascades

### Scenario
Build an enterprise customer account schema enforcing domain constraints, check rules, unique keys, and cascading foreign key deletion/update policies.

### Task
Create tables `customers_v7` and `financial_accounts` with strict constraints:
- `email` must be unique and non-null.
- `balance` cannot fall below -$500.00 (overdraft limit).
- Foreign Key cascades: If a customer is deleted, their accounts are automatically deleted (`ON DELETE CASCADE`).

### Solution DDL
```sql
CREATE TABLE customers_v7 (
    customer_id INT PRIMARY KEY,
    ssn_hash VARCHAR(64) UNIQUE NOT NULL, -- Unique Constraint
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,   -- Unique Constraint
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED', 'CLOSED')) -- Check Constraint
);

CREATE TABLE financial_accounts (
    account_number BIGINT PRIMARY KEY,
    customer_id INT NOT NULL,
    type_id INT NOT NULL,
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Check Constraint enforcing overdraft limit
    CONSTRAINT chk_overdraft_limit CHECK (balance >= -500.00),
    -- Foreign Keys with Cascade policies
    CONSTRAINT fk_account_customer FOREIGN KEY (customer_id) 
        REFERENCES customers_v7(customer_id) ON DELETE CASCADE,
    CONSTRAINT fk_account_type FOREIGN KEY (type_id) 
        REFERENCES account_types(type_id) ON DELETE RESTRICT
);
```

---

## Practical Problem 2: Views for Abstraction, Security & Materialization

### Scenario
1. **Security View**: Create a read-only view for customer service reps that hides sensitive SSN hashes and internal database IDs.
2. **Updatable View**: Create a view exposing active checking accounts allowing status updates.
3. **Materialized View**: Create a materialized view for heavy analytical financial reporting that refreshes periodically.

### Query 1: Security View (Data Abstraction)
```sql
CREATE VIEW vw_customer_public_profiles AS
SELECT 
    customer_id,
    full_name,
    email,
    status
FROM customers_v7
WHERE status != 'CLOSED';
```

### Query 2: Updatable View with `WITH CHECK OPTION`
```sql
CREATE VIEW vw_active_customers AS
SELECT customer_id, full_name, email, status
FROM customers_v7
WHERE status = 'ACTIVE'
WITH CHECK OPTION; -- Prevents updates that violate status = 'ACTIVE'
```

### Query 3: Materialized View for Performance
```sql
CREATE MATERIALIZED VIEW mv_customer_financial_summary AS
SELECT 
    c.customer_id,
    c.full_name,
    COUNT(a.account_number) AS total_accounts,
    SUM(a.balance) AS aggregate_balance,
    MAX(a.created_at) AS latest_account_date
FROM customers_v7 c
INNER JOIN financial_accounts a ON c.customer_id = a.customer_id
GROUP BY c.customer_id, c.full_name;

-- Refresh Materialized View command
REFRESH MATERIALIZED VIEW mv_customer_financial_summary;
```

---

## Practical Problem 3: Indexing Strategies (B-Tree, Composite, Partial, Expression)

### Scenario
An online banking database suffers from slow lookup queries as table volume grows past 5,000,000 rows.

### Task
Design optimal indexes for distinct search patterns:
1. Single-column lookups on `email`.
2. Multi-column searching on `(customer_id, created_at)`.
3. Partial indexing for high-priority rows (`status = 'SUSPENDED'`).
4. Expression index for case-insensitive email searching (`LOWER(email)`).

### Solution DDL
```sql
-- 1. Standard B-Tree Unique Index
CREATE UNIQUE INDEX idx_customers_email ON customers_v7(email);

-- 2. Composite Index (Order matters: most selective column first)
CREATE INDEX idx_accounts_customer_created 
ON financial_accounts(customer_id, created_at DESC);

-- 3. Partial Index (Filters index size to only non-active accounts)
CREATE INDEX idx_suspended_customers 
ON customers_v7(customer_id) 
WHERE status = 'SUSPENDED';

-- 4. Expression / Function-Based Index
CREATE INDEX idx_lower_customer_email 
ON customers_v7(LOWER(email));
```

---

## Practical Problem 4: Query Execution Plan Analysis & Tuning (`EXPLAIN ANALYZE`)

### Scenario
Analyze a slow financial ledger query and optimize it using execution plan analysis.

### Unoptimized Query & Execution Plan Analysis
```sql
-- Before Indexing: Causes Full Table Scan (Seq Scan)
EXPLAIN ANALYZE
SELECT account_number, balance
FROM financial_accounts
WHERE LOWER(customer_id::text) = '1005' AND balance > 10000.00;
```

### Execution Plan Result Breakdown
- **Seq Scan on financial_accounts**: Reads every page on disk ($O(N)$ execution time).
- **Execution Time**: `450.12 ms`

### Optimization Step
Add a targeted composite index:
```sql
CREATE INDEX idx_opt_acc_cust_bal ON financial_accounts(customer_id, balance);
```

### Optimized Query Execution Plan
```sql
EXPLAIN ANALYZE
SELECT account_number, balance
FROM financial_accounts
WHERE customer_id = 1005 AND balance > 10000.00;
```

### Improved Execution Result
- **Index Scan using idx_opt_acc_cust_bal**: Direct B-Tree lookup ($O(\log N)$ execution time).
- **Execution Time**: `0.85 ms` (99.8% speedup!)
