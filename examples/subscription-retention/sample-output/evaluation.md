# Final test evaluation

Synthetic, untouched final temporal holdout: n=285, prevalence=0.2491. Choice and threshold were frozen before scoring.

| Method | ROC-AUC | AP | Brier | F1 |
|---|---:|---:|---:|---:|
| selected_model | 0.7479 | 0.5097 | 0.1582 | 0.5072 |
| dummy_prior | 0.5000 | 0.2491 | 0.1890 | 0.0000 |
| fixed_rule | 0.6131 | 0.3234 | 0.2772 | 0.4148 |

AP = average precision. Higher ROC-AUC/AP/F1 and lower Brier are preferable. Point estimates only: no uncertainty intervals or production-readiness assertion. Threshold is chosen on synthetic validation F1; performance may change with time. Future real work requires cohort uncertainty, calibration, capacity-aware utility and prospective monitoring.
