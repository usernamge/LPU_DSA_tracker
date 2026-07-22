# Practical SQL Curriculum & Industrial Case Studies

Welcome to the **Practical SQL Curriculum** repository. This comprehensive practical guide contains 44 real-world database scenarios, executable DDL/DML scripts, relational schema setups, advanced SQL queries, optimization strategies, and industrial case studies.

---

## Curriculum Overview & Table of Contents

| Module | Topic | Practical Items | Description | Link |
|---|---|---|---|---|
| **01** | Database Concepts, ER Models & Normalization | 5 | ER diagram translation, primary/foreign/candidate keys, 1NF to 3NF normalization, BCNF, OLTP vs OLAP star schema architecture. | [Module 01](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/01_Database_Concepts_ER_Normalization.md) |
| **02** | DDL, DML, DCL & TCL Commands | 5 | Schema design, batch inserts/updates/UPSERT, role-based access control (`GRANT`/`REVOKE`), transaction management with `SAVEPOINT` and `ROLLBACK`. | [Module 02](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/02_DDL_DML_DCL_TCL.md) |
| **03** | SELECT Queries, Filtering & Sorting | 5 | Column projections, string/date functions, multi-condition `WHERE`, `COALESCE`/`NULLIF` NULL handling, multi-column `ORDER BY`, pagination, and `CASE` expressions. | [Module 03](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/03_SELECT_Filtering_Sorting.md) |
| **04** | Joins & Relational Data Querying | 5 | Multi-table `INNER JOIN`, orphan detection with `LEFT`/`RIGHT JOIN`, cross-product matrices with `CROSS`/`FULL JOIN`, self joins for hierarchies, and complex 5-table joins. | [Module 04](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/04_Joins_and_Relationships.md) |
| **05** | Aggregate Functions & Data Grouping | 5 | Core aggregations (`SUM`, `AVG`, `COUNT`), multi-dimensional `GROUP BY`, `HAVING` vs `WHERE` filtering, `ROLLUP`/`GROUPING SETS`, and conditional pivoting. | [Module 05](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/05_Aggregate_Functions_and_Grouping.md) |
| **06** | Subqueries, Nested Queries & CTEs | 5 | Scalar subqueries, multi-row filtering (`IN`, `ANY`, `ALL`), correlated subqueries, `EXISTS` vs `IN` performance, and Recursive CTEs for organograms. | [Module 06](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/06_Subqueries_and_Nested_Queries.md) |
| **07** | Views, Indexes & Constraints | 4 | Primary/Foreign/Check constraints, security views, updatable views, B-Tree/Composite/Partial/Expression indexes, and `EXPLAIN ANALYZE` tuning. | [Module 07](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/07_Views_Indexes_Constraints.md) |
| **08** | Stored Procedures, Functions & Triggers | 5 | Scalar/Table functions, transactional stored procedures with `TRY...CATCH`, immutable audit triggers, constraint triggers, and stock alerting event triggers. | [Module 08](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/08_Stored_Procedures_Functions_Triggers.md) |
| **09** | Advanced SQL Industrial Case Studies | 5 | E-Commerce RFM Segmentation, Financial Fraud Anomaly Detection, Ride-Sharing Surge Metrics, Healthcare HIPAA Auditing, and SaaS Streaming MRR/Churn Engine. | [Module 09](file:///d:/training/LPU_DSA/LPU_DSA_tracker/SQL/09_Advanced_SQL_Case_Studies.md) |

---

## How to Execute the Queries

All queries are written in **Standard ANSI SQL** compatible with major Relational Database Management Systems:
- **PostgreSQL** (12+) — Full native support for all window functions, CTEs, PL/pgSQL procedures, and triggers.
- **MySQL / MariaDB** (8.0+) — Compatible with standard syntax; procedural blocks use MySQL syntax equivalents.
- **SQLite** (3.25+) — Standard SELECTs, Joins, Aggregates, CTEs, and Window Functions are directly executable.

### Execution Steps
1. Open your SQL Client (e.g. `psql`, `pgAdmin`, `DBeaver`, `VS Code SQL Tools`, or `MySQL Workbench`).
2. Execute the **Practical Setup Schema** SQL script located at the top of each module file to instantiate tables and sample data.
3. Run the individual query tasks and review the problem scenarios, solutions, and explanations.
