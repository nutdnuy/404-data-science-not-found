# Training-only EDA

Synthetic data. Target exploration is restricted to the training partition: n=630; observed churn rate=0.2048. No final-test target exploration informed model or threshold choice.

| Feature | Missing after cleanup | Median |
|---|---:|---:|
| tenure_months | 0 | 24.0000 |
| sessions_30d | 31 | 13.0000 |
| support_tickets_30d | 0 | 1.0000 |
| monthly_price | 0 | 19.0000 |
| auto_renew | 0 | 1.0000 |

Source intentionally includes an exact post-outcome proxy. Its known generation semantics exclude it before fitting. Feature distribution summaries above are descriptive, not causal.
