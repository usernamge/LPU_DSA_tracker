# Module 6: Subqueries, Nested Queries & CTEs

This module covers scalar subqueries, multi-row/multi-column subqueries (`IN`, `ANY`, `ALL`), correlated subqueries, `EXISTS` vs `IN` optimization, Common Table Expressions (CTEs), and Recursive CTEs.

---

## Practical Setup Schema: Corporate Payroll & Hierarchy

```sql
CREATE TABLE departments (
    dept_id INT PRIMARY KEY,
    dept_name VARCHAR(50) NOT NULL,
    location VARCHAR(50)
);

CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100) NOT NULL,
    dept_id INT REFERENCES departments(dept_id),
    manager_id INT REFERENCES employees(emp_id),
    salary DECIMAL(10, 2),
    hire_date DATE
);

INSERT INTO departments VALUES
(10, 'Engineering', 'San Francisco'),
(20, 'Marketing', 'New York'),
(30, 'Sales', 'Chicago'),
(40, 'Research', 'Boston');

INSERT INTO employees VALUES
(1, 'Alice Smith', 10, NULL, 150000.00, '2018-03-01'), -- CTO
(2, 'Bob Jones', 10, 1, 110000.00, '2019-06-15'),      -- Reports to Alice
(3, 'Charlie Brown', 10, 1, 125000.00, '2020-01-10'),   -- Reports to Alice
(4, 'Diana Prince', 20, NULL, 135000.00, '2017-11-20'),  -- CMO
(5, 'Evan Wright', 20, 4, 85000.00, '2021-04-12'),      -- Reports to Diana
(6, 'Fiona Gallagher', 30, NULL, 95000.00, '2019-08-30');-- Sales Dir
-- Note: Department 40 (Research) has 0 employees.
```

---

## Practical Problem 1: Scalar Subqueries in SELECT & WHERE Clauses

### Scenario
Find all employees who earn more than the global average salary across all departments. Display employee name, salary, global average salary, and difference.

### Query
```sql
SELECT 
    emp_name,
    salary,
    (SELECT ROUND(AVG(salary), 2) FROM employees) AS global_avg_salary,
    ROUND(salary - (SELECT AVG(salary) FROM employees), 2) AS salary_above_avg
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees)
ORDER BY salary DESC;
```

---

## Practical Problem 2: Multi-Row Subqueries (`IN`, `ANY`, `ALL`)

### Scenario
1. **Using `IN`**: Find all employees working in departments located in 'San Francisco' or 'New York'.
2. **Using `ALL`**: Find employees whose salary is higher than ALL salaries in the Sales department (dept_id = 30).

### Query 1: `IN` Multi-Row Filtering
```sql
SELECT emp_id, emp_name, salary, dept_id
FROM employees
WHERE dept_id IN (
    SELECT dept_id 
    FROM departments 
    WHERE location IN ('San Francisco', 'New York')
);
```

### Query 2: `ALL` Comparison
```sql
SELECT emp_id, emp_name, salary
FROM employees
WHERE salary > ALL (
    SELECT salary 
    FROM employees 
    WHERE dept_id = 30
);
```

---

## Practical Problem 3: Correlated Subqueries — Departmental Benchmarks

### Scenario
Find employees who earn more than the average salary of THEIR OWN specific department.

### Key Concept
A correlated subquery references columns from the outer query table (`e1.dept_id`), executing once for every row evaluated by the outer query.

### Query
```sql
SELECT 
    e1.emp_id,
    e1.emp_name,
    e1.dept_id,
    e1.salary,
    dept_avg.avg_dept_salary
FROM employees e1
CROSS JOIN LATERAL (
    SELECT ROUND(AVG(e2.salary), 2) AS avg_dept_salary
    FROM employees e2
    WHERE e2.dept_id = e1.dept_id
) dept_avg
WHERE e1.salary > dept_avg.avg_dept_salary;
```

---

## Practical Problem 4: `EXISTS` vs `NOT EXISTS` Performance Optimization

### Scenario
Find all departments that currently have NO assigned employees (detecting empty departments).

### Optimization Note
`NOT EXISTS` is generally preferred over `NOT IN` because `NOT IN` returns 0 rows if the subquery contains any NULL values.

### Query
```sql
SELECT 
    d.dept_id,
    d.dept_name,
    d.location
FROM departments d
WHERE NOT EXISTS (
    SELECT 1 
    FROM employees e 
    WHERE e.dept_id = d.dept_id
);
```

### Output
| dept_id | dept_name | location |
|---|---|---|
| 40 | Research | Boston |

---

## Practical Problem 5: Non-Recursive & Recursive Common Table Expressions (CTEs)

### Scenario
1. **Non-Recursive CTE**: Calculate department salary totals and filter departments exceeding $200,000 in total payroll.
2. **Recursive CTE**: Traverse the employee management tree starting from top executives (manager_id IS NULL) to compute organizational reporting depth/levels.

### Query 1: Non-Recursive Modular CTE
```sql
WITH dept_payroll AS (
    SELECT 
        dept_id,
        COUNT(emp_id) AS total_staff,
        SUM(salary) AS total_dept_salary,
        ROUND(AVG(salary), 2) AS avg_dept_salary
    FROM employees
    GROUP BY dept_id
)
SELECT 
    d.dept_name,
    dp.total_staff,
    dp.total_dept_salary,
    dp.avg_dept_salary
FROM dept_payroll dp
INNER JOIN departments d ON dp.dept_id = d.dept_id
WHERE dp.total_dept_salary > 200000.00;
```

### Query 2: Recursive CTE (Org Structure Hierarchy Depth)
```sql
WITH RECURSIVE org_hierarchy AS (
    -- Anchor Member: Top Managers (Level 1)
    SELECT 
        emp_id,
        emp_name,
        manager_id,
        1 AS hierarchy_level,
        CAST(emp_name AS VARCHAR(255)) AS management_chain
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive Member: Subordinates
    SELECT 
        e.emp_id,
        e.emp_name,
        e.manager_id,
        h.hierarchy_level + 1,
        CAST(h.management_chain || ' -> ' || e.emp_name AS VARCHAR(255))
    FROM employees e
    INNER JOIN org_hierarchy h ON e.manager_id = h.emp_id
)
SELECT 
    emp_id,
    emp_name,
    hierarchy_level,
    management_chain
FROM org_hierarchy
ORDER BY hierarchy_level, emp_id;
```
