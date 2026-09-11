# Requirement analysis

- **Observation unit:** one unique synthetic customer at a dated snapshot.
- **Target:** churn within the next 30 days. All approved features are observable at the snapshot.
- **Split:** chronological boundaries at 55% and 75% of source rows. Labels must mature strictly before the next partition; final-test labels must be mature at extraction.
- **Baselines:** training-prevalence dummy and fixed rule (sessions <= 6 OR tickets >= 3).
- **Candidates:** logistic regression C=0.1 and C=1.0.
- **Selection:** validation ROC-AUC selects C; validation F1 on a prespecified grid selects the threshold.
- **Freeze:** save the model before test scoring; no refit on validation.
- **Interpretation:** synthetic F1 is a teaching objective, not a business utility estimate.
