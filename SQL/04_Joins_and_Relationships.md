# Module 4: Joins & Relational Data Querying

This module covers joining tables using `INNER JOIN`, `LEFT JOIN`, `RIGHT JOIN`, `FULL OUTER JOIN`, `CROSS JOIN`, and `SELF JOIN` for multi-table data synthesis.

---

## Practical Setup Schema: E-Commerce Store

```sql
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL
);

CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100) NOT NULL,
    dept_id INT REFERENCES departments(dept_id),
    manager_id INT REFERENCES employees(emp_id),
    salary DECIMAL(10, 2)
);

CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    city VARCHAR(50)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    order_date DATE,
    total_amount DECIMAL(10, 2)
);

INSERT INTO departments VALUES 
(1, 'Engineering'), (2, 'Sales'), (3, 'Marketing'), (4, 'Human Resources');

INSERT INTO employees VALUES
(101, 'Sarah Connor', 1, NULL, 120000.00), -- Executive Manager
(102, 'Kyle Reese', 1, 101, 85000.00),     -- Reports to Sarah
(103, 'John Connor', 1, 101, 95000.00),     -- Reports to Sarah
(104, 'Ellen Ripley', 2, NULL, 110000.00),  -- Sales Manager
(105, 'James Bond', 2, 104, 115000.00);    -- Reports to Ellen (Salary > Manager!)

INSERT INTO customers VALUES
(1, 'Alice Smith', 'New York'),
(2, 'Bob Jones', 'Chicago'),
(3, 'Charlie Brown', 'Los Angeles'),
(4, 'Diana Prince', 'New York');

INSERT INTO orders VALUES
(501, 1, '2023-05-10', 450.00),
(502, 1, '2023-06-15', 200.00),
(503, 2, '2023-06-20', 1200.00);
-- Note: Customers 3 & 4 have placed 0 orders.
```

---

## Practical Problem 1: INNER JOIN Multi-Table Master Order Detail Query

### Scenario
Generate an itemized invoice statement showing customer name, city, order ID, order date, and total order amount for all fulfilled orders.

### Query
```sql
SELECT 
    c.customer_id,
    c.customer_name,
    c.city,
    o.order_id,
    o.order_date,
    o.total_amount
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
ORDER BY o.order_date DESC;
```

---

## Practical Problem 2: LEFT OUTER JOIN — Identifying Customers Without Orders (Orphans)

### Scenario
The marketing team wants to run a re-engagement campaign targeting registered customers who have never placed an order.

### Query
```sql
SELECT 
    c.customer_id,
    c.customer_name,
    c.city,
    o.order_id
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;
```

### Output
| customer_id | customer_name | city | order_id |
|---|---|---|---|
| 3 | Charlie Brown | Los Angeles | NULL |
| 4 | Diana Prince | New York | NULL |

---

## Practical Problem 3: FULL OUTER JOIN & CROSS JOIN

### Scenario
1. **Full Outer Join**: Compare `departments` and `employees` to find departments with no employees AND employees unassigned to any department.
2. **Cross Join**: Produce a matrix of all possible city and department combinations for market expansion analysis.

### Query 1: Full Outer Join
```sql
SELECT 
    d.dept_id,
    d.dept_name,
    e.emp_id,
    e.emp_name
FROM departments d
FULL OUTER JOIN employees e ON d.dept_id = e.dept_id;
```

### Query 2: Cross Join (Cartesian Product Matrix)
```sql
SELECT DISTINCT
    c.city,
    d.dept_name
FROM customers c
CROSS JOIN departments d
ORDER BY c.city, d.dept_name;
```

---

## Practical Problem 4: SELF JOIN — Employee-Manager Hierarchy & Anomaly Detection

### Scenario
1. Display each employee alongside their direct manager's name and manager's salary.
2. Find all employees who earn a higher salary than their direct manager.

### Query 1: Organizational Hierarchy
```sql
SELECT 
    e.emp_id,
    e.emp_name AS employee_name,
    e.salary AS employee_salary,
    COALESCE(m.emp_name, 'TOP EXECUTIVE / NO MANAGER') AS manager_name,
    m.salary AS manager_salary
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.emp_id;
```

### Query 2: Salary Anomaly (Employee Salary > Manager Salary)
```sql
SELECT 
    e.emp_name AS employee_name,
    e.salary AS employee_salary,
    m.emp_name AS manager_name,
    m.salary AS manager_salary,
    (e.salary - m.salary) AS salary_difference
FROM employees e
INNER JOIN employees m ON e.manager_id = m.emp_id
WHERE e.salary > m.salary;
```

---

## Practical Problem 5: Complex 5-Table Join Optimization

### Scenario
An e-commerce reporting pipeline needs to assemble complete order line-item breakdowns linking `customers`, `orders`, `order_items`, `products`, and `suppliers`.

### Query
```sql
SELECT 
    c.customer_name,
    c.city,
    o.order_id,
    o.order_date,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_item_total,
    s.supplier_name
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
INNER JOIN order_items oi ON o.order_id = oi.order_id
INNER JOIN products p ON oi.product_id = p.product_id
INNER JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE o.order_date >= '2023-01-01'
ORDER BY o.order_date DESC, oi.order_id;
```
