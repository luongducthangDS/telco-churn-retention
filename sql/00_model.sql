-- Customer Churn & Retention Model: Grain = 1 row per customer subscription
-- Built in DuckDB from data/raw/telco_churn_raw.csv

CREATE OR REPLACE TABLE fct_subscriptions AS
WITH raw AS (
    SELECT
        TRIM("customerID")                                              AS customer_id,
        TRIM("gender")                                                  AS gender,
        CAST("SeniorCitizen" AS INTEGER) = 1                            AS is_senior_citizen,
        COALESCE("Partner", FALSE)                                      AS has_partner,
        COALESCE("Dependents", FALSE)                                   AS has_dependents,
        CAST("tenure" AS INTEGER)                                       AS tenure_months,
        COALESCE("PhoneService", FALSE)                                 AS has_phone_service,
        TRIM("MultipleLines")                                           AS multiple_lines,
        TRIM("InternetService")                                         AS internet_service,
        TRIM("OnlineSecurity")                                          AS online_security,
        TRIM("OnlineBackup")                                            AS online_backup,
        TRIM("DeviceProtection")                                        AS device_protection,
        TRIM("TechSupport")                                             AS tech_support,
        TRIM("StreamingTV")                                             AS streaming_tv,
        TRIM("StreamingMovies")                                         AS streaming_movies,
        TRIM("Contract")                                                AS contract_type,
        COALESCE("PaperlessBilling", FALSE)                             AS has_paperless_billing,
        TRIM("PaymentMethod")                                           AS payment_method,
        ROUND(CAST("MonthlyCharges" AS DOUBLE), 2)                      AS monthly_charges,
        -- Handle blank strings in TotalCharges for tenure=0 customers
        ROUND(CASE
            WHEN TRIM("TotalCharges") = '' OR "TotalCharges" IS NULL THEN 0.0
            ELSE CAST("TotalCharges" AS DOUBLE)
        END, 2)                                                         AS total_charges,
        COALESCE("Churn", FALSE)                                        AS is_churn
    FROM read_csv_auto('data/raw/telco_churn_raw.csv')
)
SELECT
    r.*,
    -- Tenure lifecycle cohorts
    CASE
        WHEN tenure_months <= 6 THEN '01. 0-6M (Onboarding Cliff)'
        WHEN tenure_months <= 12 THEN '02. 7-12M (Early Life)'
        WHEN tenure_months <= 24 THEN '03. 13-24M (Maturing)'
        WHEN tenure_months <= 48 THEN '04. 25-48M (Established)'
        ELSE '05. 49+M (Loyal Champions)'
    END AS tenure_cohort,
    -- Bundle count of value-added services
    (CASE WHEN online_security = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN online_backup = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN device_protection = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN tech_support = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN streaming_tv = 'Yes' THEN 1 ELSE 0 END +
     CASE WHEN streaming_movies = 'Yes' THEN 1 ELSE 0 END) AS vas_bundle_count,
    tech_support = 'Yes'                                                AS has_tech_support,
    internet_service = 'Fiber optic'                                    AS is_fiber_optic,
    contract_type = 'Month-to-month'                                    AS is_month_to_month,
    payment_method = 'Electronic check'                                 AS is_electronic_check
FROM raw r;
