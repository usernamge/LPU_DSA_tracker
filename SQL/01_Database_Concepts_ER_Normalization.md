# Module 1: Database Concepts, ER Models & Normalization

This module covers core relational database concepts, Entity-Relationship (ER) model design, key constraints, table normalization (1NF through BCNF), and OLTP vs OLAP database architecture.

---

## Practical Setup Schema: University Management System

```sql
-- Unnormalized Student Course Registrations (Raw Dump)
CREATE TABLE raw_student_registrations (
    student_id INT,
    student_name VARCHAR(100),
    student_email VARCHAR(100),
    department_name VARCHAR(50),
    department_head VARCHAR(100),
    courses_enrolled VARCHAR(255), -- Comma separated course codes & titles
    advisor_id INT,
    advisor_name VARCHAR(100),
    advisor_office VARCHAR(50)
);

INSERT INTO raw_student_registrations VALUES
(101, 'Alice Smith', 'alice@univ.edu', 'Computer Science', 'Dr. Alan Turing', 'CS101-Intro to CS, CS201-Data Structures', 501, 'Prof. Higgins', 'Tech-301'),
(102, 'Bob Jones', 'bob@univ.edu', 'Mathematics', 'Dr. Emmy Noether', 'MATH101-Calculus I', 502, 'Prof. Gauss', 'Math-102'),
(103, 'Charlie Brown', 'charlie@univ.edu', 'Computer Science', 'Dr. Alan Turing', 'CS101-Intro to CS, CS301-Algorithms, MATH101-Calculus I', 501, 'Prof. Higgins', 'Tech-301');
```

---

## Practical Problem 1: ER Diagram Translation into Relational Schema

### Scenario
An e-commerce business needs to translate an ER Diagram with Entities (`Customer`, `Order`, `Product`), Attributes, and Relationships (`Places` [1:N], `Contains` [M:N]) into a normalized relational schema.
- here [1:N] means one customer can have many orders
- here [M:N] means many customers can have many orders

### Task
Design the DDL statements representing this ER model, ensuring proper primary keys, foreign keys, and junction tables for M:N relationships.

### Solution SQL
```sql
-- 1. Entity: Customer (1)
CREATE TABLE customers (
    customer_id INT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Entity: Product
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL CHECK (unit_price >= 0),
    stock_quantity INT DEFAULT 0
);

-- 3. Entity: Order (1:N relationship with Customer)
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE
);

-- 4. Junction Table for M:N Relationship: Orders <-> Products (Contains)
CREATE TABLE order_items (
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    PRIMARY KEY (order_id, product_id), -- Composite Primary Key
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
```

### Key Concept & Explanation
- **1:N Relationship**: Represented by placing the Primary Key of `customers` as a Foreign Key inside `orders`.
- **M:N Relationship**: Resolved by introducing a bridge/junction table (`order_items`) whose composite primary key is `(order_id, product_id)`.

---

## Practical Problem 2: Primary Keys, Candidate Keys, Foreign Keys & Composite Keys

### Scenario
Analyze a multi-branch store inventory table containing redundant and candidate key columns.

### Task
Identify candidate keys, select the optimal Primary Key, enforce Foreign Key constraints, and create a Composite Candidate Key.

### Solution SQL
```sql
CREATE TABLE store_branches (
    branch_id INT PRIMARY KEY,
    branch_code VARCHAR(10) UNIQUE NOT NULL, -- Candidate Key 1
    branch_name VARCHAR(100) NOT NULL
);

CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY, -- Primary Key (Surrogate)
    branch_id INT NOT NULL,
    sku_code VARCHAR(50) NOT NULL,
    quantity_on_hand INT DEFAULT 0,
    last_restock_date DATE,
    FOREIGN KEY (branch_id) REFERENCES store_branches(branch_id),
    CONSTRAINT uq_branch_sku UNIQUE (branch_id, sku_code) -- Composite Candidate Key
);
```

### Explanation
- **Candidate Keys**: `branch_id` and `branch_code` are both unique minimal identifiers. `branch_id` is selected as the primary key.
- **Composite Key**: `(branch_id, sku_code)` forms a composite unique key to guarantee that a specific product SKU appears only once per store branch.

---

## Practical Problem 3: Normalization Step-by-Step (1NF to 3NF)

### Scenario
Convert the unnormalized `raw_student_registrations` table (shown in schema setup) into Third Normal Form (3NF).

### 1NF: Remove Repeating Groups (Atomicity)
Split multi-valued `courses_enrolled` into individual atomic rows.

```sql
CREATE TABLE student_courses_1nf (
    student_id INT,
    student_name VARCHAR(100),
    student_email VARCHAR(100),
    department_name VARCHAR(50),
    department_head VARCHAR(100),
    course_code VARCHAR(10),
    course_title VARCHAR(100),
    advisor_id INT,
    advisor_name VARCHAR(100),
    PRIMARY KEY (student_id, course_code)
);
```

### 2NF: Remove Partial Dependencies
Ensure all non-key attributes depend on the entire composite primary key `(student_id, course_code)`. Course attributes depend only on `course_code`; Student attributes depend only on `student_id`.

```sql
-- Student Entity Table
CREATE TABLE students_2nf (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100),
    student_email VARCHAR(100),
    department_name VARCHAR(50),
    department_head VARCHAR(100),
    advisor_id INT,
    advisor_name VARCHAR(100)
);

-- Course Entity Table
CREATE TABLE courses_2nf (
    course_code VARCHAR(10) PRIMARY KEY,
    course_title VARCHAR(100)
);

-- Student-Course Enrollment Bridge Table
CREATE TABLE enrollments_2nf (
    student_id INT,
    course_code VARCHAR(10),
    PRIMARY KEY (student_id, course_code),
    FOREIGN KEY (student_id) REFERENCES students_2nf(student_id),
    FOREIGN KEY (course_code) REFERENCES courses_2nf(course_code)
);
```

### 3NF: Remove Transitive Dependencies
In `students_2nf`, `department_head` depends on `department_name` (not directly on `student_id`), and `advisor_name` depends on `advisor_id`.

```sql
CREATE TABLE departments_3nf (
    department_id INT PRIMARY KEY,
    department_name VARCHAR(50) UNIQUE NOT NULL,
    department_head VARCHAR(100)
);

CREATE TABLE advisors_3nf (
    advisor_id INT PRIMARY KEY,
    advisor_name VARCHAR(100),
    office_room VARCHAR(50)
);

CREATE TABLE students_3nf (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100),
    student_email VARCHAR(100),
    department_id INT REFERENCES departments_3nf(department_id),
    advisor_id INT REFERENCES advisors_3nf(advisor_id)
);
```

---

## Practical Problem 4: Boyce-Codd Normal Form (BCNF) Decomposition

### Scenario
Consider a table `advisor_assignments(student_id, subject, advisor_id)` with Functional Dependencies:
1. `(student_id, subject) -> advisor_id`
2. `advisor_id -> subject`

Since `advisor_id` is NOT a superkey, Functional Dependency #2 violates BCNF.

### Task
Decompose `advisor_assignments` into BCNF tables.

### Solution Schema
```sql
-- Table 1: Advisor Specialization (satisfies advisor_id -> subject)
CREATE TABLE advisor_subjects (
    advisor_id INT PRIMARY KEY,
    subject VARCHAR(50) NOT NULL
);

-- Table 2: Student Advisor Pairings
CREATE TABLE student_advisors (
    student_id INT,
    advisor_id INT,
    PRIMARY KEY (student_id, advisor_id),
    FOREIGN KEY (advisor_id) REFERENCES advisor_subjects(advisor_id)
);
```

### Explanation
By splitting into `advisor_subjects` and `student_advisors`, every left-hand side of all functional dependencies becomes a superkey, satisfying BCNF while maintaining lossless decomposition.

---

## Practical Problem 5: OLTP vs OLAP Denormalization Architecture

### Scenario
An enterprise needs to optimize transactions for operational throughput (OLTP) while building a Star Schema for analytical reporting (OLAP).

### Task
Compare and write the DDL for the normalized OLTP order schema vs the denormalized OLAP Data Warehouse Fact/Dimension schema.

### Solution DDL

#### OLTP (Normalized 3NF for fast inserts & updates)
```sql
CREATE TABLE oltp_orders (
    order_id INT PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    status VARCHAR(20)
);

CREATE TABLE oltp_order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT REFERENCES oltp_orders(order_id),
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2)
);
```

#### OLAP Star Schema (Denormalized for high-speed analytical queries)
```sql
-- Dimension: Time
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY, -- Format: YYYYMMDD
    full_date DATE,
    year INT,
    quarter INT,
    month_name VARCHAR(15),
    day_of_week VARCHAR(15)
);

-- Dimension: Customer
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY,
    customer_id INT,
    full_name VARCHAR(100),
    region VARCHAR(50),
    country VARCHAR(50)
);

-- Dimension: Product
CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    product_id INT,
    product_name VARCHAR(150),
    category VARCHAR(50),
    brand VARCHAR(50)
);

-- Fact Table: Sales Performance
CREATE TABLE fact_sales (
    sales_fact_id BIGINT PRIMARY KEY,
    date_key INT REFERENCES dim_date(date_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    product_key INT REFERENCES dim_product(product_key),
    quantity_sold INT,
    total_sales_amount DECIMAL(12, 2),
    discount_amount DECIMAL(10, 2),
    net_profit DECIMAL(12, 2)
);
```

### Summary of Differences
| Feature | OLTP | OLAP |
|---|---|---|
| Focus | Fast Write/Updates, Row operations | Fast Read/Aggregation, Columnar operations |
| Design | Highly Normalized (3NF/BCNF) | Denormalized (Star / Snowflake Schema) |
| Redundancy | Minimal | Intentional (for zero-join speed) |
