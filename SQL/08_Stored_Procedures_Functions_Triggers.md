# Module 8: Stored Procedures, Functions & Triggers

This module covers programmatic database logic including User-Defined Functions (UDFs), Stored Procedures with transaction control and error handling, `BEFORE` and `AFTER` Triggers, and automated event-driven audit log generation.

---

## Practical Setup Schema: E-Commerce Inventory & Accounting

```sql
CREATE TABLE inventory_items (
    item_id INT PRIMARY KEY,
    item_name VARCHAR(100) NOT NULL,
    stock_quantity INT NOT NULL CHECK (stock_quantity >= 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    reorder_threshold INT DEFAULT 10
);

CREATE TABLE customer_balances (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    credit_limit DECIMAL(12, 2) DEFAULT 1000.00,
    current_balance DECIMAL(12, 2) DEFAULT 0.00
);

CREATE TABLE system_audit_logs (
    log_id SERIAL PRIMARY KEY,
    table_name VARCHAR(50),
    operation_type VARCHAR(20),
    record_id INT,
    old_values JSONB,
    new_values JSONB,
    performed_by VARCHAR(100) DEFAULT CURRENT_USER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE inventory_alerts (
    alert_id SERIAL PRIMARY KEY,
    item_id INT,
    message VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Practical Problem 1: User-Defined Functions (Scalar & Table-Valued)

### Scenario
1. **Scalar Function**: Write a function `fn_calculate_tax(amount DECIMAL, tax_rate DECIMAL)` that returns rounded tax amounts.
2. **Table-Valued Function**: Write a function `fn_get_low_stock_items(threshold INT)` that returns a result set of inventory items needing restock.

### Solution SQL
```sql
-- 1. Scalar Function
CREATE OR REPLACE FUNCTION fn_calculate_tax(
    amount DECIMAL(10, 2), 
    tax_rate DECIMAL(4, 2)
) 
RETURNS DECIMAL(10, 2) AS $$
BEGIN
    RETURN ROUND(amount * (tax_rate / 100.00), 2);
END;
$$ LANGUAGE plpgsql;

-- Usage Example:
-- SELECT item_name, unit_price, fn_calculate_tax(unit_price, 8.25) AS tax FROM inventory_items;

-- 2. Table-Valued Function (Returns Table Set)
CREATE OR REPLACE FUNCTION fn_get_low_stock_items(min_stock INT)
RETURNS TABLE (
    product_id INT,
    product_name VARCHAR(100),
    current_stock INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT item_id, item_name, stock_quantity
    FROM inventory_items
    WHERE stock_quantity <= min_stock;
END;
$$ LANGUAGE plpgsql;

-- Usage Example:
-- SELECT * FROM fn_get_low_stock_items(15);
```

---

## Practical Problem 2: Stored Procedure with Transactions & Exception Handling

### Scenario
Build a stored procedure `sp_process_order_purchase` that deducts inventory stock and updates customer balance inside an isolated transaction with exception rollback handling.

### Solution SQL
```sql
CREATE OR REPLACE PROCEDURE sp_process_order_purchase(
    p_customer_id INT,
    p_item_id INT,
    p_quantity INT,
    OUT p_status VARCHAR(100)
)
LANGUAGE plpgsql AS $$
DECLARE
    v_unit_price DECIMAL(10, 2);
    v_total_cost DECIMAL(10, 2);
    v_current_stock INT;
    v_customer_balance DECIMAL(12, 2);
    v_credit_limit DECIMAL(12, 2);
BEGIN
    -- Check Stock Availability
    SELECT stock_quantity, unit_price INTO v_current_stock, v_unit_price
    FROM inventory_items WHERE item_id = p_item_id FOR UPDATE;

    IF v_current_stock IS NULL THEN
        RAISE EXCEPTION 'Item ID % does not exist.', p_item_id;
    ELSIF v_current_stock < p_quantity THEN
        RAISE EXCEPTION 'Insufficient stock. Required: %, Available: %', p_quantity, v_current_stock;
    END IF;

    v_total_cost := v_unit_price * p_quantity;

    -- Check Customer Balance
    SELECT current_balance, credit_limit INTO v_customer_balance, v_credit_limit
    FROM customer_balances WHERE customer_id = p_customer_id FOR UPDATE;

    IF (v_customer_balance + v_total_cost) > v_credit_limit THEN
        RAISE EXCEPTION 'Credit limit exceeded. Transaction declined.';
    END IF;

    -- Perform Mutations
    UPDATE inventory_items 
    SET stock_quantity = stock_quantity - p_quantity 
    WHERE item_id = p_item_id;

    UPDATE customer_balances 
    SET current_balance = current_balance + v_total_cost 
    WHERE customer_id = p_customer_id;

    p_status := 'SUCCESS: Order processed successfully.';

EXCEPTION
    WHEN OTHERS THEN
        p_status := 'FAILED: ' || SQLERRM;
END;
$$;
```

---

## Practical Problem 3: `AFTER UPDATE` Immutable Audit Trail Trigger

### Scenario
Automatically log all mutations on `inventory_items` (capturing old vs new values in JSON format) whenever an item's price or stock quantity changes.

### Solution SQL
```sql
CREATE OR REPLACE FUNCTION trg_fn_audit_inventory_changes()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO system_audit_logs (
        table_name,
        operation_type,
        record_id,
        old_values,
        new_values
    )
    VALUES (
        'inventory_items',
        TG_OP,
        NEW.item_id,
        to_jsonb(OLD),
        to_jsonb(NEW)
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_audit_inventory_update
AFTER UPDATE ON inventory_items
FOR EACH ROW
WHEN (OLD.unit_price IS DISTINCT FROM NEW.unit_price OR OLD.stock_quantity IS DISTINCT FROM NEW.stock_quantity)
EXECUTE FUNCTION trg_fn_audit_inventory_changes();
```

---

## Practical Problem 4: `BEFORE INSERT/UPDATE` Business Validation Trigger

### Scenario
Prevent any insert or update on `customer_balances` that would result in a negative credit limit or balance exceeding 2x the credit limit.

### Solution SQL
```sql
CREATE OR REPLACE FUNCTION trg_fn_validate_customer_balance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.credit_limit < 0 THEN
        RAISE EXCEPTION 'Validation Error: Credit limit cannot be negative.';
    END IF;

    IF NEW.current_balance > (NEW.credit_limit * 2.0) THEN
        RAISE EXCEPTION 'Validation Error: Balance cannot exceed twice the credit limit.';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_balance_before
BEFORE INSERT OR UPDATE ON customer_balances
FOR EACH ROW
EXECUTE FUNCTION trg_fn_validate_customer_balance();
```

---

## Practical Problem 5: Event-Driven Automated Inventory Alert Trigger System

### Scenario
Create an automated event trigger on `inventory_items` that monitors stock drops. When `stock_quantity` drops below `reorder_threshold`, automatically insert an item restock alert into `inventory_alerts`.

### Solution SQL
```sql
CREATE OR REPLACE FUNCTION trg_fn_low_stock_alert()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.stock_quantity <= NEW.reorder_threshold AND OLD.stock_quantity > NEW.reorder_threshold THEN
        INSERT INTO inventory_alerts (item_id, message)
        VALUES (
            NEW.item_id, 
            'ALERT: Stock for item ' || NEW.item_name || ' (ID: ' || NEW.item_id || ') dropped to ' || NEW.stock_quantity || '. Restock required.'
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_stock_threshold
AFTER UPDATE OF stock_quantity ON inventory_items
FOR EACH ROW
EXECUTE FUNCTION trg_fn_low_stock_alert();
```
