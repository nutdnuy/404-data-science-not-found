# Feature dictionary

| Field | Meaning / availability | Decision |
|---|---|---|
| tenure_months | Nonnegative subscription age at snapshot | Include |
| sessions_30d | Sessions in preceding 30 days | Include; source missing values imputed from train median |
| support_tickets_30d | Tickets in preceding 30 days | Include |
| monthly_price | Fictional positive plan price at snapshot | Include |
| auto_renew | 0 or 1 at snapshot | Include |
| customer_id | Unique synthetic identifier | Exclude; bookkeeping only |
| as_of, outcome_available_at, extracted_at | Snapshot, label-maturity, extraction dates | Split/audit only |
| cancellation_confirmed_after_30d | Exact future outcome proxy intentionally planted | Exclude: leakage |
| churn_next_30d | Future 30-day outcome | Target only |

Training-derived features: median-imputed, standardized numeric values; no feature selection or transformations use validation/test fit statistics.
