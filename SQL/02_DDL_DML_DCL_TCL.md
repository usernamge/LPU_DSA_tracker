# Module 2: DDL, DML, DCL & TCL Commands

This module covers Data Definition Language (DDL), Data Manipulation Language (DML), Data Control Language (DCL), and Transaction Control Language (TCL) with practical scenarios.

---

## Practical Problem 1: DDL — Schema Creation, Alteration & Maintenance

### Scenario
An HR management application requires establishing employee structures, modifying table schemas as business requirements change, and maintaining table lifecycles.

### Task
Write standard SQL DDL statements to:
1. Create an `employees` table with proper data types and default values.
2. Alter the table to add a new `phone_number` column and modify `salary` precision.
3. Rename the column `dept` to `department_name`.
4. Truncate temporary test data without dropping table definitions.

### Solution DDL
```sql
-- 1. Initial Table Creation
CREATE TABLE hr_employees (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hire_date DATE DEFAULT CURRENT_DATE,
    salary DECIMAL(8, 2) NOT NULL,
    dept VARCHAR(50)
);

-- 2. Alter Table: Add phone column & increase salary precision
ALTER TABLE hr_employees 
    ADD COLUMN phone_number VARCHAR(20);

ALTER TABLE hr_employees 
    ALTER COLUMN salary TYPE DECIMAL(12, 2);

-- 3. Rename Column
ALTER TABLE hr_employees 
    RENAME COLUMN dept TO department_name;

-- 4. Truncate Data (Removes all rows, resets identity sequence, keeps schema structure)
TRUNCATE TABLE hr_employees RESTART IDENTITY;
```

---

## Practical Problem 2: DML — Batch Insert, Conditional Updates & UPSERT (ON CONFLICT)

### Scenario
A warehouse inventory sync receives daily stock feeds. Some products are new (need insertion), while existing products require stock quantity updates.

### Task
Write DML queries for batch insertion, conditional salary increases based on department, conditional deletion of inactive accounts, and an UPSERT statement.

### Solution DML
```sql
-- Setup Sample Data
INSERT INTO hr_employees (employee_id, first_name, last_name, email, hire_date, salary, department_name, phone_number) 
VALUES
(1, 'John', 'Doe', 'john.doe@company.com', '2021-03-15', 60000.00, 'Engineering', '555-0101'),
(2, 'Jane', 'Smith', 'jane.smith@company.com', '2019-06-20', 85000.00, 'Engineering', '555-0102'),
(3, 'Robert', 'Johnson', 'robert.j@company.com', '2022-01-10', 45000.00, 'Sales', '555-0103'),
(4, 'Emily', 'Davis', 'emily.d@company.com', '2018-11-05', 92000.00, 'Executive', '555-0104');

-- 1. Conditional Update: Give a 10% raise to Engineering employees earning under $80,000
UPDATE hr_employees
SET salary = salary * 1.10
WHERE department_name = 'Engineering' AND salary < 80000.00;

-- 2. Conditional Delete: Delete records hired before 2020 in Sales department
DELETE FROM hr_employees
WHERE department_name = 'Sales' AND hire_date < '2020-01-01';

-- 3. UPSERT (Insert or Update on Primary Key conflict)
INSERT INTO hr_employees (employee_id, first_name, last_name, email, hire_date, salary, department_name)
VALUES (1, 'John', 'Doe', 'john.doe@company.com', '2021-03-15', 68000.00, 'Engineering')
ON CONFLICT (employee_id) 
DO UPDATE SET 
    salary = EXCLUDED.salary,
    department_name = EXCLUDED.department_name;
```

---

## Practical Problem 3: DCL — Role-Based Access Control (RBAC), GRANT & REVOKE

### Scenario
A enterprise database administrator needs to create database roles (`analyst_role`, `hr_admin_role`), assign specific permissions on `hr_employees`, delegate grant privileges, and revoke permissions when security policies change.

### Task
Write DCL statements to grant read/write access to analyst roles, restrict access to sensitive salary data, and revoke privileges.

### Solution DCL
```sql
-- 1. Create Roles
CREATE ROLE analyst_role;
CREATE ROLE hr_admin_role;

-- 2. Grant SELECT access on specific non-sensitive columns to analyst_role
GRANT SELECT (employee_id, first_name, last_name, hire_date, department_name) 
ON hr_employees TO analyst_role;

-- 3. Grant ALL privileges on hr_employees to hr_admin_role WITH GRANT OPTION
GRANT ALL PRIVILEGES ON hr_employees TO hr_admin_role WITH GRANT OPTION;

-- 4. Create User and Assign Role
CREATE USER analyst_user WITH PASSWORD 'SecurePass123!';
GRANT analyst_role TO analyst_user;

-- 5. Revoke SELECT permission from analyst_role
REVOKE SELECT ON hr_employees FROM analyst_role;
```

---

## Practical Problem 4: TCL — Transaction Control, Savepoints & Error Rollback

### Scenario
A core banking application performs account transfers. If an account deduction succeeds but the destination deposit fails, the entire sequence must safely roll back to maintain financial integrity.

### Task
Simulate a fund transfer transaction with `BEGIN TRANSACTION`, `SAVEPOINT`, `ROLLBACK TO SAVEPOINT`, and `COMMIT`.

### Setup Schema & Data
```sql
CREATE TABLE bank_accounts (
    account_id INT PRIMARY KEY,
    account_holder VARCHAR(100) NOT NULL,
    balance DECIMAL(12, 2) NOT NULL CHECK (balance >= 0)
);

INSERT INTO bank_accounts VALUES 
(1001, 'Alice', 5000.00),
(1002, 'Bob', 1200.00);
```

### Solution TCL
```sql
-- Start Atomic Transaction
BEGIN TRANSACTION;

-- Step 1: Deduct $500 from Alice (Account 1001)
UPDATE bank_accounts
SET balance = balance - 500.00
WHERE account_id = 1001;

-- Create Savepoint after deduction
SAVEPOINT after_deduction;

-- Step 2: Attempt Deposit to Bob (Account 1002)
UPDATE bank_accounts
SET balance = balance + 500.00
WHERE account_id = 1002;

-- Check logic: If any constraint fails (e.g. invalid target account), rollback to savepoint
-- ROLLBACK TO SAVEPOINT after_deduction;

-- Commit entire transaction if all steps succeed
COMMIT;
```

---

## Practical Problem 5: Integrated End-to-End Workflow (DDL + DML + DCL + TCL)

### Scenario
An e-commerce order processing engine needs an integrated pipeline:
1. DDL: Create `store_orders` and `audit_log` tables.
2. DCL: Grant insert permissions to `order_processor` user.
3. TCL & DML: Execute order creation, audit logging, and savepoint management inside a transaction block.

### Solution SQL
```sql
-- Step 1: DDL Schema
CREATE TABLE store_orders (
    order_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    amount DECIMAL(10, 2),
    status VARCHAR(20) DEFAULT 'PENDING'
);

CREATE TABLE order_audit_log (
    log_id INT PRIMARY KEY,
    order_id INT,
    action VARCHAR(50),
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 2: DCL Security Configuration
CREATE ROLE order_processor;
GRANT SELECT, INSERT, UPDATE ON store_orders TO order_processor;
GRANT INSERT ON order_audit_log TO order_processor;

-- Step 3: TCL + DML Execution Workflow
BEGIN TRANSACTION;

-- Insert New Order
INSERT INTO store_orders (order_id, customer_name, amount, status)
VALUES (5001, 'Charlie Brown', 249.99, 'PROCESSING');

SAVEPOINT order_created;

-- Audit Log Entry
INSERT INTO order_audit_log (log_id, order_id, action)
VALUES (1, 5001, 'Order created and payment processing initiated');

-- Finalize Order Status
UPDATE store_orders
SET status = 'COMPLETED'
WHERE order_id = 5001;

-- Commit Transaction
COMMIT;
```
