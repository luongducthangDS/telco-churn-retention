// Power Query M script for loading Telco Churn Star Schema CSVs
let
    SourceDir = "D:\github\go to offer\data-analyst\telco-churn-retention\powerbi\",
    LoadFact = Csv.Document(File.Contents(SourceDir & "fact_subscriptions.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    PromotedFact = Table.PromoteHeaders(LoadFact, [PromoteAllScalars=true]),
    TypedFact = Table.TransformColumnTypes(PromotedFact, {
        {"customer_id", type text},
        {"plan_id", type text},
        {"contract_id", type text},
        {"tenure_months", Int64.Type},
        {"tenure_cohort", type text},
        {"monthly_charges", type number},
        {"total_charges", type number},
        {"vas_bundle_count", Int64.Type},
        {"is_fiber_optic", type logical},
        {"has_tech_support", type logical},
        {"is_month_to_month", type logical},
        {"is_electronic_check", type logical},
        {"is_churn", type logical}
    })
in
    TypedFact
