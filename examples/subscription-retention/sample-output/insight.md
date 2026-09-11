# Training-only synthetic insight

Question: how does observed churn differ between snapshots with at least three support tickets in the preceding 30 days and those with fewer? Scope: the 630 training rows only, from 2021-01-01 to 2022-09-22. Each row is one unique synthetic customer; denominators include every training row in its cohort.

| Training cohort | Rows (denominator) | Churned rows | Churn rate |
|---|---:|---:|---:|
| Support tickets >= 3 | 80 | 31 | 0.3875 |
| Support tickets < 3 | 550 | 98 | 0.1782 |

This is a descriptive association, not a causal effect of support tickets or evidence that a retention intervention works. The generator explicitly gives ticket count a positive coefficient in its outcome probability, so an association is expected by construction. No confidence interval or population inference is claimed; an empty cohort has no estimable rate. This summary did not select features, model parameters, or thresholds.

Next evidence for a real project: confirm point-in-time ticket availability and label maturity; estimate cohort uncertainty and assess tenure, usage, and plan differences in a separate prospective cohort. Test any retention intervention with an appropriately designed experiment before claiming lift.
