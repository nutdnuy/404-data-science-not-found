# Subscription retention: evidence before prediction

**Synthetic demonstration; no real business inference.**

A complete run retained 630 training, 210 validation, and 285 final-test rows. It discarded immature labels, excluded an intentionally planted future-outcome proxy, and fit all preprocessing exclusively on training rows.

Validation selected **logistic_C=1.0** with a frozen threshold of **0.25**. Final-test ROC-AUC: **0.7479**; AP: **0.5097**; Brier: **0.1582**; F1: **0.5072**.

| Method | ROC-AUC | AP | Brier | F1 |
|---|---:|---:|---:|---:|
| selected_model | 0.7479 | 0.5097 | 0.1582 | 0.5072 |
| dummy_prior | 0.5000 | 0.2491 | 0.1890 | 0.0000 |
| fixed_rule | 0.6131 | 0.3234 | 0.2772 | 0.4148 |

These measurements describe one seeded generator and temporal holdout, with no confidence intervals. They do not establish customer retention lift, causality or production readiness. Next step for a real project: approve the decision, label availability, evaluation costs, cohorts and monitoring plan before collecting customer data.

Evidence: metrics.json, split_manifest.json, predictions.csv, model.json and provenance.json.
