# Leakage audit: bounded synthetic evidence

Scope: this documented generator and this execution, not a universal leakage-free certification.

| Check | Evidence in this run |
|---|---|
| Planted future proxy | The generator assigns cancellation_confirmed_after_30d from the future target. It matches the target in 630/630 training rows; availability semantics exclude it regardless of that match rate. |
| Feature allowlist | The fitted model contains only tenure_months, sessions_30d, support_tickets_30d, monthly_price, auto_renew. Target, IDs, future proxy, and audit timestamps are absent. |
| Training label maturity | Latest retained training label: 2022-10-22; first validation snapshot: 2022-10-23. |
| Validation label maturity | Latest retained validation label: 2023-06-19; first test snapshot: 2023-06-20. |
| Final label maturity | 285/285 retained test labels are available by their extraction date. |
| Fit boundaries | Imputer, scaler, logistic candidates, and prevalence dummy fit only 630 training rows. model.json records medians, scaling parameters, and the hash of fitted row IDs. |
| Selection boundaries | Validation selects logistic_C=1.0 and threshold 0.25; model.json is written before final-test scoring, with no validation refit. |

Trace the exact row IDs and timestamps in split_manifest.json, parameter values in model.json, candidate comparisons in experiment_log.md, and source/data/artifact hashes in provenance.json. Behavioral tests check train-only fitted statistics and verify that changing final-test outcomes or the planted proxy cannot change the saved model.

Limits: the example does not establish real-world feature lineage, event-time correctness, hidden proxies, repeat-customer handling, or operational data availability. For new data, independently audit each feature's origin and availability, joins and aggregates, entity boundaries, and target definition before accepting any leakage conclusion.
