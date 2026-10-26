"""Statistical and business analysis of Telco Customer Churn & Retention.

Outputs:
- reports/results.json (reproducible metrics quoted in decision memo & README)
"""
import json
from pathlib import Path
import duckdb
import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reports"
REP.mkdir(parents=True, exist_ok=True)


def load_model():
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute(f"SET file_search_path = '{ROOT}'")
    con.execute((ROOT / "sql" / "00_model.sql").read_text())
    con.execute((ROOT / "sql" / "10_powerbi_export.sql").read_text())
    return con


def run():
    con = load_model()

    # 1. Headline KPIs
    kpi_query = """
    SELECT
        count(*)                                                    AS total_subscribers,
        count(CASE WHEN is_churn THEN 1 END)                        AS churned_subscribers,
        round(avg(is_churn::INT) * 100, 2)                          AS churn_rate_pct,
        round(sum(monthly_charges), 2)                              AS total_mrr,
        round(sum(CASE WHEN is_churn THEN monthly_charges ELSE 0 END), 2) AS lost_mrr,
        round(sum(CASE WHEN is_churn THEN monthly_charges ELSE 0 END) * 100.0 / sum(monthly_charges), 2) AS lost_mrr_pct,
        round(avg(monthly_charges), 2)                              AS avg_monthly_arpu,
        round(avg(tenure_months), 1)                                AS avg_tenure_months
    FROM fct_subscriptions;
    """
    kpis = con.execute(kpi_query).fetchdf().to_dict(orient="records")[0]

    # 2. Tenure Cohort Breakdown (The Onboarding Cliff)
    tenure_query = """
    SELECT
        tenure_cohort,
        count(*)                                                    AS subscribers,
        count(CASE WHEN is_churn THEN 1 END)                        AS churned,
        round(avg(is_churn::INT) * 100, 2)                          AS churn_rate_pct,
        round(sum(monthly_charges), 2)                              AS mrr,
        round(sum(CASE WHEN is_churn THEN monthly_charges ELSE 0 END), 2) AS lost_mrr
    FROM fct_subscriptions
    GROUP BY tenure_cohort
    ORDER BY tenure_cohort;
    """
    tenure_cohorts = con.execute(tenure_query).fetchdf().to_dict(orient="records")

    # 3. Contract Type Impact
    contract_query = """
    SELECT
        contract_type,
        count(*)                                                    AS subscribers,
        round(avg(is_churn::INT) * 100, 2)                          AS churn_rate_pct,
        round(sum(CASE WHEN is_churn THEN monthly_charges ELSE 0 END), 2) AS lost_mrr
    FROM fct_subscriptions
    GROUP BY contract_type
    ORDER BY churn_rate_pct DESC;
    """
    contracts = con.execute(contract_query).fetchdf().to_dict(orient="records")

    # 4. Fiber Optic vs Tech Support Interaction (The Paradox Unraveled)
    interaction_query = """
    SELECT
        internet_service,
        has_tech_support,
        count(*)                                                    AS subscribers,
        round(avg(monthly_charges), 2)                              AS avg_monthly_fee,
        round(avg(is_churn::INT) * 100, 2)                          AS churn_rate_pct,
        round(sum(CASE WHEN is_churn THEN monthly_charges ELSE 0 END), 2) AS lost_mrr
    FROM fct_subscriptions
    WHERE internet_service IN ('Fiber optic', 'DSL')
    GROUP BY internet_service, has_tech_support
    ORDER BY internet_service, has_tech_support DESC;
    """
    interactions = con.execute(interaction_query).fetchdf().to_dict(orient="records")

    # 5. Payment Method Impact
    payment_query = """
    SELECT
        payment_method,
        count(*)                                                    AS subscribers,
        round(avg(is_churn::INT) * 100, 2)                          AS churn_rate_pct
    FROM fct_subscriptions
    GROUP BY payment_method
    ORDER BY churn_rate_pct DESC;
    """
    payments = con.execute(payment_query).fetchdf().to_dict(orient="records")

    # 6. Logistic Regression for Odds Ratios (using scipy.optimize)
    # Predict Churn from: is_month_to_month, is_fiber_optic, has_tech_support, is_electronic_check, tenure_months
    model_data = con.execute("""
        SELECT
            is_churn::INT,
            is_month_to_month::INT,
            is_fiber_optic::INT,
            has_tech_support::INT,
            is_electronic_check::INT,
            tenure_months
        FROM fct_subscriptions
    """).fetchall()

    y = np.array([r[0] for r in model_data])
    X = np.column_stack([
        np.ones(len(model_data)),
        [r[1] for r in model_data],  # Month-to-month
        [r[2] for r in model_data],  # Fiber optic
        [r[3] for r in model_data],  # Tech support
        [r[4] for r in model_data],  # Electronic check
        [r[5] / 12.0 for r in model_data], # Tenure (years)
    ])

    feature_names = ["Intercept", "Month-to-month Contract", "Fiber Optic Internet", "Tech Support Active", "Electronic Check Payment", "Tenure (Years)"]

    def neg_log_lik(beta):
        logits = np.clip(X @ beta, -30, 30)
        p = 1.0 / (1.0 + np.exp(-logits))
        eps = 1e-15
        p = np.clip(p, eps, 1.0 - eps)
        return -np.sum(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))

    res = minimize(neg_log_lik, np.zeros(X.shape[1]), method="BFGS")
    beta = res.x
    # Fisher Information matrix -> Standard Errors
    logits = np.clip(X @ beta, -30, 30)
    p = 1.0 / (1.0 + np.exp(-logits))
    W = p * (1.0 - p)
    info_matrix = X.T @ (X * W[:, None])
    vcov = np.linalg.pinv(info_matrix)
    se = np.sqrt(np.diag(vcov))

    odds_ratios = []
    for i in range(1, len(feature_names)):
        coef = beta[i]
        odds = np.exp(coef)
        ci_low = np.exp(coef - 1.96 * se[i])
        ci_high = np.exp(coef + 1.96 * se[i])
        odds_ratios.append({
            "feature": feature_names[i],
            "odds_ratio": round(float(odds), 3),
            "ci_95_pct": [round(float(ci_low), 3), round(float(ci_high), 3)],
            "interpretation": "Increases churn risk" if odds > 1.0 else "Reduces churn risk (Protective)"
        })

    results = {
        "kpis": kpis,
        "tenure_cohorts": tenure_cohorts,
        "contracts": contracts,
        "fiber_techsupport_interaction": interactions,
        "payments": payments,
        "logistic_odds_ratios": odds_ratios
    }

    out_file = REP / "results.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Telco Churn analysis completed! Saved to {out_file}")
    print("\n--- Headline Findings ---")
    print(f"Total Subscribers: {kpis['total_subscribers']:,} | Churn Rate: {kpis['churn_rate_pct']}%")
    print(f"Lost MRR: ${kpis['lost_mrr']:,.2f} ({kpis['lost_mrr_pct']}% of total revenue)")
    print(f"Fiber without TechSupport Churn: {interactions[1]['churn_rate_pct']}% vs Fiber WITH TechSupport: {interactions[0]['churn_rate_pct']}%")
    print(f"Month-to-month Contract Odds Ratio: {odds_ratios[0]['odds_ratio']}x churn risk!")


if __name__ == "__main__":
    run()
