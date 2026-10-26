# Power BI Rebuild Guide: Telco Customer Churn & Retention

This directory contains star schema CSVs generated from `sql/10_powerbi_export.sql` via `python analysis/build_dashboard.py`.

## Data Model & Relationships

1. Load the 4 CSV files:
   - `fact_subscriptions.csv` (7,043 rows, subscriber facts and monthly charges)
   - `dim_customer_demographics.csv` (7,043 rows, gender, senior citizen, partner, dependents)
   - `dim_service_plan.csv` (Internet service, streaming, security, tech support)
   - `dim_contract.csv` (Contract type, billing, payment method)

2. Create 1-to-many relationships (Single direction filter):
   - `dim_customer_demographics[customer_id]` 1 ---> 1 `fact_subscriptions[customer_id]`
   - `dim_service_plan[plan_id]` 1 ---> * `fact_subscriptions[plan_id]`
   - `dim_contract[contract_id]` 1 ---> * `fact_subscriptions[contract_id]`

3. Create DAX measures from `measures.dax`.
