# Module 3: SELECT Queries, Filtering & Sorting

This module covers querying relational data using `SELECT` projections, multi-condition filtering, pattern matching, NULL value handling, custom sorting, pagination, and `CASE` expressions.

---

## Practical Setup Schema: Retail Products & Customers

```sql
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    unit_price DECIMAL(10, 2),
    stock_quantity INT,
    supplier_code VARCHAR(20),
    discontinued BOOLEAN DEFAULT FALSE,
    release_date DATE
);

INSERT INTO products VALUES
(101, 'Pro Wireless Gaming Mouse', 'Electronics', 79.99, 150, 'SUP-A1', FALSE, '2023-01-15'),
(102, 'Mechanical RGB Keyboard', 'Electronics', 129.50, 45, 'SUP-A1', FALSE, '2022-11-20'),
(103, 'Ergonomic Office Chair', 'Furniture', 249.00, 12, 'SUP-B2', FALSE, '2021-05-10'),
(104, 'Standing Desk Converter', 'Furniture', 199.99, 0, NULL, FALSE, '2023-03-01'),
(105, 'UltraWide 34 Monitor', 'Electronics', 499.99, 8, 'SUP-A1', FALSE, '2023-06-12'),
(106, 'Noise Cancelling Headphones', 'Electronics', 180.00, NULL, 'SUP-C3', TRUE, '2020-08-25'),
(107, 'Adjustable Monitor Arm', 'Furniture', 45.00, 85, 'SUP-B2', FALSE, '2022-02-14');
```

---

## Practical Problem 1: Column Projections, Expressions & String Formatting

### Scenario
The inventory team needs a clean report displaying formatted product labels, discounted prices (15% off), total inventory asset value, and years since product release.

### Query
```sql
SELECT 
    product_id,
    UPPER(product_name) AS formatted_name,
    category,
    unit_price,
    ROUND(unit_price * 0.85, 2) AS discounted_price_15pct,
    COALESCE(stock_quantity, 0) AS stock_qty,
    ROUND(unit_price * COALESCE(stock_quantity, 0), 2) AS total_inventory_value,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, release_date)) AS years_on_market
FROM products;
```

### Expected Output Format
| product_id | formatted_name | category | unit_price | discounted_price_15pct | stock_qty | total_inventory_value | years_on_market |
|---|---|---|---|---|---|---|---|
| 101 | PRO WIRELESS GAMING MOUSE | Electronics | 79.99 | 67.99 | 150 | 11998.50 | 3 |
| 102 | MECHANICAL RGB KEYBOARD | Electronics | 129.50 | 110.08 | 45 | 5827.50 | 3 |
| 103 | ERGONOMIC OFFICE CHAIR | Furniture | 249.00 | 211.65 | 12 | 2988.00 | 5 |

---

## Practical Problem 2: Advanced Multi-Condition Filtering & Pattern Matching

### Scenario
Find all active (non-discontinued) products that meet ANY of the following criteria:
1. Category is 'Electronics' and unit price is between $100.00 and $300.00.
2. Product name starts with 'Pro' or contains 'Monitor' (case-insensitive).
3. Supplied by 'SUP-A1' or 'SUP-B2' and stock quantity is greater than 10.

### Query
```sql
SELECT 
    product_id,
    product_name,
    category,
    unit_price,
    stock_quantity,
    supplier_code
FROM products
WHERE discontinued = FALSE
  AND (
        (category = 'Electronics' AND unit_price BETWEEN 100.00 AND 300.00)
     OR (product_name ILIKE 'Pro%' OR product_name ILIKE '%Monitor%')
     OR (supplier_code IN ('SUP-A1', 'SUP-B2') AND stock_quantity > 10)
  );
```

---

## Practical Problem 3: Safe NULL Handling (`COALESCE`, `NULLIF`, `IS NULL`)

### Scenario
Generate a stock audit report where missing stock quantities are treated as 0, missing supplier codes are labeled 'UNKNOWN SUPPLIER', and products with 0 stock return NULL for average item value calculation using `NULLIF`.
- COALESCE is used to replace NULL values with the specified value
- NULLIF is used to return NULL if the specified value is 0
- IS NULL is used to check if a value is NULL

### Query
```sql
SELECT 
    product_name,
    supplier_code,
    COALESCE(supplier_code, 'UNKNOWN SUPPLIER') AS resolved_supplier,
    stock_quantity,
    COALESCE(stock_quantity, 0) AS safe_stock_count,
    -- NULLIF returns NULL if stock_quantity is 0 to prevent Division-by-Zero errors
    ROUND(unit_price / NULLIF(COALESCE(stock_quantity, 0), 0), 2) AS price_per_unit_in_stock,
    CASE 
        WHEN supplier_code IS NULL THEN 'Action Required: Assign Supplier'
        WHEN stock_quantity IS NULL OR stock_quantity = 0 THEN 'Out of Stock'
        ELSE 'In Stock'
    END AS stock_status
FROM products;
```

---

## Practical Problem 4: Multi-Column Sorting, `NULLS LAST` & Pagination

### Scenario
An e-commerce catalog API endpoint requires fetching page 2 of products (5 items per page) sorted primarily by `category` ascending, secondarily by `unit_price` descending, placing items with NULL stock at the very end.

### Query
```sql
SELECT 
    product_id,
    product_name,
    category,
    unit_price,
    stock_quantity
FROM products
ORDER BY 
    category ASC,
    unit_price DESC,
    stock_quantity ASC NULLS LAST
LIMIT 5 OFFSET 5; -- Page 2 (Items 6 to 10)
```

---

## Practical Problem 5: Conditional Logic with `CASE WHEN` Expressions

### Scenario
Categorize products into pricing tiers and determine reorder alerts based on stock thresholds.

### Query
```sql
SELECT 
    product_name,
    category,
    unit_price,
    stock_quantity,
    -- Price Tier Classification
    CASE 
        WHEN unit_price < 50.00 THEN 'Budget Tier'
        WHEN unit_price BETWEEN 50.00 AND 200.00 THEN 'Mid-Range Tier'
        WHEN unit_price > 200.00 THEN 'Premium Tier'
        ELSE 'Unpriced'
    END AS price_tier,
    -- Inventory Health Status
    CASE 
        WHEN stock_quantity IS NULL OR stock_quantity = 0 THEN 'CRITICAL: Reorder Immediately'
        WHEN stock_quantity < 15 THEN 'WARNING: Low Stock'
        WHEN stock_quantity BETWEEN 15 AND 50 THEN 'MODERATE: Healthy Stock'
        ELSE 'OPTIMAL: Well Stocked'
    END AS inventory_health
FROM products
ORDER BY unit_price DESC;
```
