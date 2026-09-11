# Inference contract

Input CSV must be nonempty and contain exactly the five FEATURES columns listed in model.json. Column order may vary; names may not. Each value must be a finite number; all features >=0, monthly_price >0, auto_renew in {0,1}. Missing cells, extra target/ID/leakage columns, nonnumeric text, NaN and infinities are rejected. Inputs describe information already available at prediction time; the CLI cannot verify real-world lineage.

Output: churn_probability in [0,1] and review_flag using the frozen threshold. No intervention is triggered. JSON model format retention-logistic-v1 is schema-checked; no pickle is loaded. Use only reviewed artifacts with a verified provenance hash. The training source allows a controlled sessions missingness demonstration, but serving requires complete rows.
