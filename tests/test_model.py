"""Data quality and integrity tests for Telco Churn analytics model."""
from pathlib import Path
import duckdb
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def con():
    c = duckdb.connect()
    c.execute("SET enable_progress_bar = false")
    c.execute(f"SET file_search_path = '{ROOT}'")
    c.execute((ROOT / "sql" / "00_model.sql").read_text())
    c.execute((ROOT / "sql" / "10_powerbi_export.sql").read_text())
    return c


def one(con, sql):
    return con.execute(sql).fetchone()[0]


def test_row_count(con):
    assert one(con, "SELECT count(*) FROM fct_subscriptions") == 7_043
    assert one(con, "SELECT count(*) - count(DISTINCT customer_id) FROM fct_subscriptions") == 0


def test_blank_total_charges_properly_handled(con):
    assert one(con, "SELECT count(*) FROM fct_subscriptions WHERE total_charges IS NULL") == 0
    # The 11 customers with tenure = 0 should have total_charges = 0
    zero_tenure_charges = one(con, "SELECT sum(total_charges) FROM fct_subscriptions WHERE tenure_months = 0")
    assert zero_tenure_charges == 0.0


def test_churn_rate_reproducible(con):
    rate = one(con, "SELECT round(avg(is_churn::INT) * 100, 2) FROM fct_subscriptions")
    assert rate == 26.54


def test_powerbi_dimensions_unique_keys(con):
    dims = [
        ("pbi_dim_customer_demographics", "customer_id"),
        ("pbi_dim_service_plan", "plan_id"),
        ("pbi_dim_contract", "contract_id"),
    ]
    for table, pk in dims:
        dups = one(con, f"SELECT count(*) - count(DISTINCT {pk}) FROM {table}")
        assert dups == 0, f"Duplicate keys in {table} on {pk}"


def test_referential_integrity(con):
    assert one(con, """
        SELECT count(*) FROM pbi_fact_subscriptions f
        LEFT JOIN pbi_dim_customer_demographics d USING (customer_id)
        WHERE d.customer_id IS NULL
    """) == 0

    assert one(con, """
        SELECT count(*) FROM pbi_fact_subscriptions f
        LEFT JOIN pbi_dim_service_plan p USING (plan_id)
        WHERE p.plan_id IS NULL
    """) == 0

    assert one(con, """
        SELECT count(*) FROM pbi_fact_subscriptions f
        LEFT JOIN pbi_dim_contract c USING (contract_id)
        WHERE c.contract_id IS NULL
    """) == 0
