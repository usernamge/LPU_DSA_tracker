# Module 5: Aggregate Functions & Data Grouping

This module covers summarizing datasets using aggregate functions (`SUM`, `AVG`, `COUNT`, `MIN`, `MAX`), grouping data with `GROUP BY`, filtering groups with `HAVING`, multi-dimensional aggregation (`ROLLUP`, `CUBE`, `GROUPING SETS`), and conditional pivoting.

---

## Practical Setup Schema: Regional Sales Performance

```sql
CREATE TABLE sales_records (
    sale_id INT PRIMARY KEY,
    region VARCHAR(50),
    store_category VARCHAR(50),
    sales_rep VARCHAR(100),
    sale_amount DECIMAL(10, 2),
    sale_date DATE
);

INSERT INTO sales_records VALUES
(1, 'North America', 'Electronics', 'Alice', 1200.00, '2023-01-15'),
(2, 'North America', 'Electronics', 'Bob', 850.00, '2023-01-18'),
(3, 'North America', 'Furniture', 'Alice', 2300.00, '2023-02-10'),
(4, 'Europe', 'Electronics', 'Charlie', 1500.00, '2023-01-22'),
(5, 'Europe', 'Furniture', 'Diana', 950.00, '2023-02-14'),
(6, 'Europe', 'Electronics', 'Charlie', 3100.00, '2023-03-05'),
(7, 'Asia-Pacific', 'Electronics', 'Evan', 4200.00, '2023-01-11'),
(8, 'Asia-Pacific', 'Furniture', 'Evan', 1800.00, '2023-03-20'),
(9, 'North America', 'Electronics', 'Bob', 1400.00, '2023-03-28');
```

---

## Practical Problem 1: Core Aggregate Functions & Distinct Metrics

### Scenario
The executive dashboard requires overall business performance statistics: total revenue, average transaction value, minimum and maximum sale amounts, total sales count, and the number of active sales representatives.

### Query
```sql
SELECT 
    COUNT(*) AS total_transactions,
    COUNT(DISTINCT sales_rep) AS active_sales_reps,
    COUNT(DISTINCT region) AS active_regions,
    SUM(sale_amount) AS gross_revenue,
    ROUND(AVG(sale_amount), 2) AS avg_transaction_value,
    MIN(sale_amount) AS lowest_sale,
    MAX(sale_amount) AS highest_sale
FROM sales_records;
```

---

## Practical Problem 2: Multi-Column Grouping & Revenue Breakdowns

### Scenario
Group sales performance by `region` and `store_category` to calculate regional revenue distribution, average transaction size, and total transaction volume.

### Query
```sql
SELECT 
    region,
    store_category,
    COUNT(sale_id) AS transaction_count,
    SUM(sale_amount) AS category_revenue,
    ROUND(AVG(sale_amount), 2) AS avg_sale_value
FROM sales_records
GROUP BY region, store_category
ORDER BY region ASC, category_revenue DESC;
```

---

## Practical Problem 3: Group Filtering — `HAVING` vs `WHERE` Clause

### Scenario
Find all regions that generated more than $3,000.00 in total revenue, considering ONLY transactions that occurred after January 15, 2023.

### Key Concept
- `WHERE` filters individual rows BEFORE aggregation.
- `HAVING` filters aggregated groups AFTER `GROUP BY` evaluation.

### Query
```sql
SELECT 
    region,
    COUNT(sale_id) AS qualifying_sales_count,
    SUM(sale_amount) AS total_qualifying_revenue
FROM sales_records
WHERE sale_date > '2023-01-15' -- Row-level filter
GROUP BY region
HAVING SUM(sale_amount) > 3000.00 -- Aggregate-level filter
ORDER BY total_qualifying_revenue DESC;
```

---

## Practical Problem 4: Multi-Dimensional Aggregation (`ROLLUP`, `CUBE`, `GROUPING SETS`)

### Scenario
Generate hierarchical subtotals and grand totals across `region` and `store_category` without executing multiple `UNION ALL` queries.

### Query 1: `ROLLUP` (Hierarchical Subtotals: Region Total -> Grand Total)
```sql
SELECT 
    COALESCE(region, 'ALL REGIONS (Grand Total)') AS region,
    COALESCE(store_category, 'ALL CATEGORIES (Subtotal)') AS store_category,
    SUM(sale_amount) AS total_revenue
FROM sales_records
GROUP BY ROLLUP (region, store_category)
ORDER BY region, store_category;
```

### Query 2: `GROUPING SETS` (Custom Subtotal Sets)
```sql
SELECT 
    region,
    store_category,
    SUM(sale_amount) AS total_revenue
FROM sales_records
GROUP BY GROUPING SETS (
    (region, store_category), -- Detail level
    (region),                -- Region subtotal
    ()                       -- Grand total
);
```

---

## Practical Problem 5: Conditional Aggregation & Data Pivoting

### Scenario
Pivot sales records into a quarterly revenue summary report where each row represents a `region` and columns show Q1 revenue, Q2 revenue, and percentage of overall revenue.

### Query
```sql
SELECT 
    region,
    -- Quarterly Aggregations
    SUM(CASE WHEN EXTRACT(MONTH FROM sale_date) BETWEEN 1 AND 3 THEN sale_amount ELSE 0 END) AS q1_revenue,
    SUM(CASE WHEN EXTRACT(MONTH FROM sale_date) BETWEEN 4 AND 6 THEN sale_amount ELSE 0 END) AS q2_revenue,
    SUM(sale_amount) AS total_annual_revenue,
    -- Category Counts Pivoted
    COUNT(CASE WHEN store_category = 'Electronics' THEN 1 END) AS electronics_count,
    COUNT(CASE WHEN store_category = 'Furniture' THEN 1 END) AS furniture_count
FROM sales_records
GROUP BY region
ORDER BY total_annual_revenue DESC;
```
