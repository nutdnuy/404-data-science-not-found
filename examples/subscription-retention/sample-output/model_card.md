# Model card

Model: logistic_C=1.0; threshold=0.25. Synthetic educational churn ranking; human review only. Inputs are the five snapshot numeric features in feature_dictionary.md. Pipeline parameters fit exclusively to training. Saved as plain JSON containing coefficients and scaler statistics; no pickle or executable model loading.

Not validated for real customers or operational decisions. Generator embeds associations by construction and modest temporal drift; they are not causal discoveries. No subgroup fairness assessment is possible because this teaching dataset defines no relevant groups. A real model needs a data/label audit, subgroup assessment, uncertainty, monitoring thresholds, ownership and approval. Distribution drift and real-world calibration remain untested.

## Model interpretation

Standardized logistic coefficients are changes in fitted log-odds per training-standard-deviation change, holding other inputs fixed. These describe fitted associations, not causal effects or stable feature importance.

| Feature | Coefficient |
|---|---:|
| tenure_months | -0.3595 |
| sessions_30d | -0.6703 |
| support_tickets_30d | 0.5223 |
| monthly_price | 0.1555 |
| auto_renew | -0.2305 |
