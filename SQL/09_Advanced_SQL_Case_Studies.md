# Module 9: Advanced SQL Industrial Case Studies

This module features 5 production-grade industrial case studies applying advanced window functions (`LAG`, `LEAD`, `NTILE`, `DENSE_RANK`), CTEs, dynamic aggregation, and analytical data modeling.

---

## Case Study 1: E-Commerce Analytics — RFM Segmentation & Cohort Analysis

### Scenario
An e-commerce retailer wants to segment its customer base into marketing cohorts using **RFM (Recency, Frequency, Monetary)** scores based on customer transaction histories.

### Schema Setup
```sql
CREATE TABLE ecom_customers (
    customer_id INT PRIMARY KEY,
    customer_name VARCHAR(100),
    signup_date DATE
);

CREATE TABLE ecom_orders (
    order_id INT PRIMARY KEY,
    customer_id INT REFERENCES ecom_customers(customer_id),
    order_date DATE,
    order_amount DECIMAL(10, 2)
);

INSERT INTO ecom_customers VALUES
(1, 'Alice', '2023-01-10'), (2, 'Bob', '2023-02-14'), (3, 'Charlie', '2023-03-01'), (4, 'Diana', '2023-04-05');

INSERT INTO ecom_orders VALUES
(101, 1, '2023-06-01', 150.00), (102, 1, '2023-06-20', 300.00), (103, 1, '2023-07-01', 450.00),
(104, 2, '2023-03-10', 80.00),  (105, 3, '2023-06-15', 1200.00),(106, 3, '2023-07-05', 950.00);
```

### Analytical Query: RFM Scoring with `NTILE(4)`
```sql
WITH rfm_metrics AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        CURRENT_DATE - MAX(o.order_date) AS recency_days,
        COUNT(o.order_id) AS frequency_count,
        COALESCE(SUM(o.order_amount), 0.00) AS monetary_value
    FROM ecom_customers c
    LEFT JOIN ecom_orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.customer_name
),
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        recency_days,
        frequency_count,
        monetary_value,
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score, -- Lower recency days = better score
        NTILE(4) OVER (ORDER BY frequency_count ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary_value ASC) AS m_score
    FROM rfm_metrics
)
SELECT 
    customer_id,
    customer_name,
    recency_days,
    frequency_count,
    monetary_value,
    (r_score || '-' || f_score || '-' || m_score) AS rfm_code,
    CASE 
        WHEN r_score >= 3 AND f_score >= 3 AND m_score >= 3 THEN 'CHURN RISK / CHAMPION'
        WHEN f_score >= 3 AND m_score >= 3 THEN 'LOYAL BIG SPENDER'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'AT RISK CUSTOMER'
        ELSE 'REGULAR CUSTOMER'
    END AS customer_segment
FROM rfm_scores
ORDER BY monetary_value DESC;
```

---

## Case Study 2: Financial & Banking Fraud Detection — Rapid Transfer Anomaly Detection

### Scenario
A bank's fraud monitoring team requires a query that flags suspicious transaction patterns: any customer who executes 2 or more transactions within 5 minutes of each other where the total transfer exceeds $5,000.

### Schema Setup
```sql
CREATE TABLE bank_transactions (
    txn_id INT PRIMARY KEY,
    account_id INT,
    txn_timestamp TIMESTAMP,
    amount DECIMAL(12, 2),
    destination_account INT
);

INSERT INTO bank_transactions VALUES
(1001, 8801, '2023-07-20 10:00:00', 3000.00, 9901),
(1002, 8801, '2023-07-20 10:03:30', 2500.00, 9902), -- Suspicious! 3.5 mins later
(1003, 8802, '2023-07-20 11:15:00', 500.00,  9903),
(1004, 8802, '2023-07-20 14:20:00', 400.00,  9904);
```

### Analytical Query: Windowing with `LAG` and Time Difference Calculation
```sql
WITH txn_lags AS (
    SELECT 
        txn_id,
        account_id,
        txn_timestamp,
        amount,
        destination_account,
        LAG(txn_timestamp) OVER (PARTITION BY account_id ORDER BY txn_timestamp) AS prev_txn_time,
        LAG(amount) OVER (PARTITION BY account_id ORDER BY txn_timestamp) AS prev_txn_amount
    FROM bank_transactions
)
SELECT 
    txn_id,
    account_id,
    txn_timestamp,
    amount AS current_amount,
    prev_txn_time,
    prev_txn_amount,
    EXTRACT(EPOCH FROM (txn_timestamp - prev_txn_time)) / 60.0 AS minutes_since_prev_txn,
    (amount + prev_txn_amount) AS combined_transfer_amount
FROM txn_lags
WHERE prev_txn_time IS NOT NULL
  AND EXTRACT(EPOCH FROM (txn_timestamp - prev_txn_time)) <= 300 -- 300 seconds = 5 minutes
  AND (amount + prev_txn_amount) >= 5000.00;
```

---

## Case Study 3: Ride-Sharing Platform — Surge Pricing & Driver Utilization

### Scenario
Calculate rolling 7-day average driver earnings, ride completion rates, and surge pricing factors across different geographic zones.

### Schema Setup
```sql
CREATE TABLE rides (
    ride_id INT PRIMARY KEY,
    driver_id INT,
    zone_id INT,
    request_time TIMESTAMP,
    fare_amount DECIMAL(8, 2),
    surge_multiplier DECIMAL(3, 2) DEFAULT 1.0,
    status VARCHAR(20) -- 'COMPLETED', 'CANCELLED'
);

INSERT INTO rides VALUES
(1, 501, 10, '2023-07-01 08:00:00', 25.00, 1.2, 'COMPLETED'),
(2, 501, 10, '2023-07-02 09:30:00', 40.00, 1.5, 'COMPLETED'),
(3, 501, 10, '2023-07-03 18:00:00', 30.00, 1.0, 'COMPLETED'),
(4, 502, 10, '2023-07-01 08:15:00', 20.00, 1.0, 'CANCELLED');
```

### Analytical Query: Driver Rolling 7-Day Performance & Cancellation Rates
```sql
SELECT 
    driver_id,
    DATE(request_time) AS ride_date,
    COUNT(ride_id) AS total_requests,
    COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) AS completed_rides,
    ROUND(
        (COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END)::DECIMAL / COUNT(ride_id)) * 100.0, 2
    ) AS completion_rate_pct,
    SUM(CASE WHEN status = 'COMPLETED' THEN fare_amount ELSE 0 END) AS daily_earnings,
    -- Rolling 7-Day Window Earnings
    SUM(SUM(CASE WHEN status = 'COMPLETED' THEN fare_amount ELSE 0 END)) OVER (
        PARTITION BY driver_id 
        ORDER BY DATE(request_time) 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day_earnings
FROM rides
GROUP BY driver_id, DATE(request_time)
ORDER BY driver_id, ride_date;
```

---

## Case Study 4: Healthcare & HIPAA Audit Logging — Unusually Frequent EHR Access

### Scenario
Healthcare compliance requires flagging any staff member who accesses more than 10 distinct patient medical records within an 1-hour window to audit potential data privacy leaks.

### Schema Setup
```sql
CREATE TABLE ehr_access_logs (
    access_id SERIAL PRIMARY KEY,
    user_id INT, -- Medical Staff ID
    patient_id INT,
    access_time TIMESTAMP,
    access_reason VARCHAR(100)
);

INSERT INTO ehr_access_logs (user_id, patient_id, access_time, access_reason) VALUES
(201, 1001, '2023-07-22 09:00:00', 'Routine Checkup'),
(201, 1002, '2023-07-22 09:05:00', 'Routine Checkup'),
(201, 1003, '2023-07-22 09:12:00', 'Lab Result Review');
```

### Analytical Query: High-Frequency EHR Patient Record Access Audit
```sql
WITH hourly_access_summary AS (
    SELECT 
        user_id,
        date_trunc('hour', access_time) AS access_hour,
        COUNT(DISTINCT patient_id) AS distinct_patients_accessed,
        COUNT(access_id) AS total_access_events
    FROM ehr_access_logs
    GROUP BY user_id, date_trunc('hour', access_time)
)
SELECT 
    user_id,
    access_hour,
    distinct_patients_accessed,
    total_access_events,
    CASE 
        WHEN distinct_patients_accessed > 10 THEN 'FLAGGED: Potential Security Audit Violation'
        ELSE 'NORMAL'
    END AS compliance_flag
FROM hourly_access_summary
ORDER BY access_hour DESC, distinct_patients_accessed DESC;
```

---

## Case Study 5: SaaS Streaming Analytics — MRR & Churn Rate Metric Engine

### Scenario
A subscription SaaS streaming service needs to compute Monthly Recurring Revenue (MRR), Monthly Churn Rates, and Rank Top Video Content by Watch Time.

### Schema Setup
```sql
CREATE TABLE subscriptions (
    sub_id INT PRIMARY KEY,
    user_id INT,
    plan_name VARCHAR(50),
    monthly_price DECIMAL(8, 2),
    start_date DATE,
    end_date DATE -- NULL if currently active
);

INSERT INTO subscriptions VALUES
(1, 101, 'Premium 4K', 19.99, '2023-01-01', NULL),
(2, 102, 'Basic HD',     9.99, '2023-01-15', '2023-03-31'),
(3, 103, 'Standard',    14.99, '2023-02-01', NULL);
```

### Analytical Query: Monthly MRR & Active vs Churned Metrics
```sql
WITH month_series AS (
    SELECT generate_series(
        '2023-01-01'::DATE, 
        '2023-06-01'::DATE, 
        '1 month'::INTERVAL
    )::DATE AS month_start
),
monthly_metrics AS (
    SELECT 
        ms.month_start,
        COUNT(DISTINCT s.sub_id) AS active_subscriptions,
        SUM(s.monthly_price) AS mrr,
        COUNT(DISTINCT CASE WHEN s.end_date BETWEEN ms.month_start AND (ms.month_start + INTERVAL '1 month' - INTERVAL '1 day') THEN s.sub_id END) AS churned_subscriptions
    FROM month_series ms
    LEFT JOIN subscriptions s 
      ON s.start_date <= (ms.month_start + INTERVAL '1 month' - INTERVAL '1 day')
     AND (s.end_date IS NULL OR s.end_date >= ms.month_start)
    GROUP BY ms.month_start
)
SELECT 
    month_start,
    active_subscriptions,
    COALESCE(mrr, 0.00) AS monthly_recurring_revenue,
    churned_subscriptions,
    ROUND(
        (churned_subscriptions::DECIMAL / NULLIF(active_subscriptions, 0)) * 100.0, 2
    ) AS monthly_churn_rate_pct
FROM monthly_metrics
ORDER BY month_start ASC;
```
