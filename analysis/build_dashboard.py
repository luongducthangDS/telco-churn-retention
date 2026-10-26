"""Build Power BI star schema CSVs and an interactive Plotly HTML dashboard for Telco Churn.

Outputs:
- powerbi/*.csv
- reports/dashboard.html
"""
from pathlib import Path
import duckdb
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
REP = ROOT / "reports"
PBI.mkdir(parents=True, exist_ok=True)
REP.mkdir(parents=True, exist_ok=True)


def main():
    con = duckdb.connect()
    con.execute("SET enable_progress_bar = false")
    con.execute(f"SET file_search_path = '{ROOT}'")
    con.execute((ROOT / "sql" / "00_model.sql").read_text())
    con.execute((ROOT / "sql" / "10_powerbi_export.sql").read_text())

    # 1. Export Power BI CSVs
    pbi_tables = [
        ("pbi_fact_subscriptions", "fact_subscriptions.csv"),
        ("pbi_dim_customer_demographics", "dim_customer_demographics.csv"),
        ("pbi_dim_service_plan", "dim_service_plan.csv"),
        ("pbi_dim_contract", "dim_contract.csv"),
    ]
    for tbl, fname in pbi_tables:
        csv_path = (PBI / fname).as_posix()
        con.execute(f"COPY {tbl} TO '{csv_path}' (HEADER, DELIMITER ',')")
        print(f"Exported {tbl} -> {PBI / fname}")

    # 2. Build Interactive HTML Dashboard
    df_tenure = con.execute("""
        SELECT
            tenure_cohort,
            count(*) AS subs,
            round(avg(is_churn::INT) * 100, 2) AS churn_pct,
            round(sum(CASE WHEN is_churn THEN monthly_charges ELSE 0 END), 2) AS lost_mrr
        FROM fct_subscriptions
        GROUP BY tenure_cohort
        ORDER BY tenure_cohort
    """).fetchdf()

    df_contract = con.execute("""
        SELECT
            contract_type,
            count(*) AS subs,
            round(avg(is_churn::INT) * 100, 2) AS churn_pct,
            round(sum(CASE WHEN is_churn THEN monthly_charges ELSE 0 END), 2) AS lost_mrr
        FROM fct_subscriptions
        GROUP BY contract_type
        ORDER BY churn_pct DESC
    """).fetchdf()

    df_fiber = con.execute("""
        SELECT
            internet_service || ' + ' || CASE WHEN has_tech_support THEN 'With TechSupport' ELSE 'NO TechSupport' END AS bundle_type,
            count(*) AS subs,
            round(avg(is_churn::INT) * 100, 2) AS churn_pct
        FROM fct_subscriptions
        WHERE internet_service IN ('Fiber optic', 'DSL')
        GROUP BY internet_service, has_tech_support
        ORDER BY churn_pct DESC
    """).fetchdf()

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            "Churn Rate by Tenure Cohort (The Onboarding Cliff)",
            "Churn Rate by Contract Type (Month-to-month Risk)",
            "The Fiber Optic Paradox: Impact of Adding Tech Support",
            "Lost MRR ($) by Contract Commitment"
        ),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "pie"}]]
    )

    # 1. Tenure Cohorts
    fig.add_trace(
        go.Bar(
            x=df_tenure["tenure_cohort"],
            y=df_tenure["churn_pct"],
            text=df_tenure["churn_pct"].apply(lambda x: f"{x}%"),
            textposition="auto",
            marker_color=["#EF4444", "#F59E0B", "#3B82F6", "#6366F1", "#10B981"],
            name="Churn Rate %"
        ),
        row=1, col=1
    )

    # 2. Contract Type
    fig.add_trace(
        go.Bar(
            x=df_contract["contract_type"],
            y=df_contract["churn_pct"],
            text=df_contract["churn_pct"].apply(lambda x: f"{x}%"),
            textposition="auto",
            marker_color="#DC2626",
            name="Contract Churn %"
        ),
        row=1, col=2
    )

    # 3. Fiber vs Tech Support
    fig.add_trace(
        go.Bar(
            x=df_fiber["bundle_type"],
            y=df_fiber["churn_pct"],
            text=df_fiber["churn_pct"].apply(lambda x: f"{x}%"),
            textposition="auto",
            marker_color=["#B91C1C", "#D97706", "#2563EB", "#059669"],
            name="Fiber Bundle Churn %"
        ),
        row=2, col=1
    )

    # 4. Lost MRR Pie
    fig.add_trace(
        go.Pie(
            labels=df_contract["contract_type"],
            values=df_contract["lost_mrr"],
            hole=0.45,
            marker_colors=["#EF4444", "#3B82F6", "#10B981"],
            name="Lost MRR Share"
        ),
        row=2, col=2
    )

    fig.update_layout(
        title_text="<b>Telco Customer Churn & Retention Executive Dashboard</b><br><sup>Root Cause Drivers of Subscription Churn, Lost MRR, and Contract Lock-in Opportunities</sup>",
        template="plotly_white",
        height=850,
        showlegend=False
    )

    dashboard_path = REP / "dashboard.html"
    fig.write_html(str(dashboard_path), include_plotlyjs="cdn")
    print(f"Generated interactive dashboard: {dashboard_path}")


if __name__ == "__main__":
    main()
