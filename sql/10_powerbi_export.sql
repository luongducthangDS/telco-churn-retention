-- Power BI Star Schema Export for Telco Churn

CREATE OR REPLACE TABLE pbi_dim_customer_demographics AS
SELECT
    customer_id,
    gender,
    is_senior_citizen,
    has_partner,
    has_dependents
FROM fct_subscriptions;

CREATE OR REPLACE TABLE pbi_dim_service_plan AS
SELECT DISTINCT
    md5(internet_service || '|' || multiple_lines || '|' || online_security || '|' ||
        online_backup || '|' || device_protection || '|' || tech_support || '|' ||
        streaming_tv || '|' || streaming_movies) AS plan_id,
    internet_service,
    multiple_lines,
    online_security,
    online_backup,
    device_protection,
    tech_support,
    streaming_tv,
    streaming_movies
FROM fct_subscriptions;

CREATE OR REPLACE TABLE pbi_dim_contract AS
SELECT DISTINCT
    md5(contract_type || '|' || CAST(has_paperless_billing AS VARCHAR) || '|' || payment_method) AS contract_id,
    contract_type,
    has_paperless_billing,
    payment_method
FROM fct_subscriptions;

CREATE OR REPLACE TABLE pbi_fact_subscriptions AS
SELECT
    s.customer_id,
    md5(s.internet_service || '|' || s.multiple_lines || '|' || s.online_security || '|' ||
        s.online_backup || '|' || s.device_protection || '|' || s.tech_support || '|' ||
        s.streaming_tv || '|' || s.streaming_movies) AS plan_id,
    md5(s.contract_type || '|' || CAST(s.has_paperless_billing AS VARCHAR) || '|' || s.payment_method) AS contract_id,
    s.tenure_months,
    s.tenure_cohort,
    s.monthly_charges,
    s.total_charges,
    s.vas_bundle_count,
    s.is_fiber_optic,
    s.has_tech_support,
    s.is_month_to_month,
    s.is_electronic_check,
    s.is_churn
FROM fct_subscriptions s;
