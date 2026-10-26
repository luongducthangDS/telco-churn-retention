# Telco Churn: Rescuing $139k Monthly Lost MRR

Analysis of **7,043 subscriber accounts** ($456k baseline MRR) from the IBM Telco Customer Churn dataset. It moves from business diagnosis, cleans missing billing data in DuckDB SQL, models subscriber retention hazard using Logistic Regression Odds Ratios, and delivers a [one-page decision memo](docs/decision_memo.md) and an interactive dashboard.

## Executive Answer

**Churn is concentrated in the onboarding window and high-speed fiber lines without technical support.** Overall churn stands at **26.54%**, costing **$139,131 in lost MRR every month** (30.5% of gross revenue). 

| Finding | Metric |
|---|---|
| Total Subscriber Base | **7,043 accounts** |
| Total MRR & Lost MRR | **$456,116 MRR** $\to$ **$139,131 Lost MRR/mo** |
| Average Customer Tenure | **32.4 months** |
| Month 0–6 Onboarding Cliff | **53.1% churn rate** (50.8% of all churn occurs in first 6 months) |
| Month-to-Month Contract Risk | **42.7% churn** (Odds Ratio = **2.90x**, $p < 0.001$) vs. 1-2 Year at **7.1%** |
| Fiber Optic without TechSupport | **49.38% churn rate** (high price without support) |
| Fiber Optic WITH TechSupport | **22.78% churn rate** (protective effect cut churn by >50%) |
| Electronic Check Churn | **45.3%** vs. Auto Credit Card at **15.2%** |

**So what:** Stop offering standalone unassisted Fiber Optic plans; automatically bundle 90 days of complimentary Tech Support with Fiber installations; launch automated customer success check-ins at Day 7 and Day 21 to navigate the onboarding cliff.

## Architecture & Method

1. **Model** (`sql/00_model.sql`, DuckDB): Grain is 1 row per subscriber. Handles edge-case blank strings in `TotalCharges` for zero-tenure accounts (`tenure = 0`), builds tenure cohort bands, and constructs service bundle density counts.
2. **Checks** (`tests/test_model.py`, pytest): 5 tests verifying exact row volume (7,043), zero charges for zero tenure, binary churn target flags, dimension surrogate key uniqueness, and star schema referential integrity.
3. **Statistical Analysis** (`analysis/run_analysis.py`):
   - Logistic regression estimating Fisher Information and Odds Ratios for key risk drivers.
   - Cross-feature interaction isolating the protective effect of Tech Support on high-speed Fiber Optic lines.
4. **Outputs**:
   - `reports/results.json` (reproducible metrics).
   - `reports/dashboard.html` (interactive Plotly dashboard).
   - `powerbi/`: Star schema CSVs (`fact_subscriptions.csv`, `dim_customer_demographics.csv`, `dim_service_plan.csv`, `dim_contract.csv`), `measures.dax`, and `power_query.m`.

## How to Run It

```bash
pip install -r requirements.txt
python scripts/get_data.py              # Downloads raw Telco Churn CSV
pytest -q                               # Runs 5 data integrity and referential checks
python analysis/run_analysis.py         # Produces reports/results.json
python analysis/build_dashboard.py      # Exports powerbi/*.csv & reports/dashboard.html
```

## Decisions Worth Defending in an Interview

- **Why Odds Ratios rather than raw correlation coefficients?** Churn is a binary classification target (0/1). Pearson correlation assumes continuous normal distributions and can severely underestimate relationships for binary categories. Odds Ratios from Logistic Regression provide the true multiplicative change in odds of churn while holding all other features constant.
- **Why does Fiber Optic have a higher churn rate than DSL?** Fiber Optic is $33/month more expensive ($91 vs $58) and customers expect pristine performance. Without Tech Support, setup friction and router issues lead to immediate cancellations. When Tech Support is present, Fiber churn drops to 22.8%, proving it is a support issue, not a product issue.
- **How did you clean `TotalCharges`?** 11 rows had blank strings `' '` because the customers had `tenure = 0` (signed up within the last month). Converting directly causes errors; setting them to $0.00 preserves the accounts without dropping valuable new-customer data.

## Interview Questions this Project Prepares For

1. How did you diagnose the root cause of the Fiber Optic paradox?
2. If you built a churn prediction ML model, why would you optimize for Precision/Recall threshold rather than default 0.5 Accuracy?
3. How would you quantify the ROI of offering free Tech Support for 3 months versus the cost of churned MRR?
