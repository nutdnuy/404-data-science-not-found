# Subscription retention, with the evidence attached

A runnable companion to the skills: turn a fictional product brief into a frozen
model and an honest report. Every row is generated locally. No credentials,
downloads, customer data, or external services are needed to run the example.

The dataset deliberately contains a perfect future-outcome proxy. The workflow
excludes it by availability semantics, purges labels that could not yet be known,
and leaves the final temporal holdout untouched until model selection is frozen.

## Run from the repository root

Python 3.10+ is required. The committed sample was generated on Python 3.12.14;
its exact package versions and source hashes are recorded in
[provenance.json](sample-output/provenance.json).

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r examples/subscription-retention/requirements.txt
python examples/subscription-retention/run.py --output-dir outputs/subscription-retention
python -m unittest discover -s tests -p 'test_demo.py' -v
```

On Windows, activate with `.venv\Scripts\activate`. Use `requirements-lock.txt`
instead of `requirements.txt` to reproduce the sample package versions on Python
3.12. Results are deterministic for the same source, seed, and package/runtime
versions; numerical equality across library versions and hardware is not promised.

Read [the generated sample report](sample-output/report.md). The default run
creates 1,200 daily rows, of which 630 train, 210 validate, and 285 form the final
test; 75 are excluded because of label maturity. A deliberately narrow two-model
search keeps the methodology visible. It compares logistic regression at C=0.1
and C=1.0 with a training-prevalence dummy and a prespecified rule baseline.

## Train and score separately

```bash
python examples/subscription-retention/train.py \
  --data outputs/subscription-retention/synthetic_data.csv \
  --output-dir outputs/retention-retrained

python examples/subscription-retention/predict.py \
  --model outputs/subscription-retention/model.json \
  --input outputs/subscription-retention/inference_input.csv \
  --output outputs/retention-inference.csv
```

`train.py` accepts this documented synthetic schema; it is not a universal CSV
trainer. `predict.py` rejects extra or missing columns, missing/nonfinite values,
nonnumeric values, invalid feature ranges, and unsupported model schemas. The
model is plain JSON with validated numeric parameters; it never loads pickle.
Verify the reviewed model against the SHA-256 recorded in `provenance.json`.

## What the run proves

- Dates, label availability, and exact row IDs appear in `split_manifest.json`.
- Training-only EDA appears in `eda_analysis.md`; full-source checks are limited
  to structure and known quality rules.
- `insight.md` records a training-only cohort association with counts, denominators,
  and noncausal qualifications. `leakage_audit.md` connects the planted proxy,
  time boundaries, and train-only fits to this run's evidence.
- The train-fit imputer/scaler, candidate comparison, and validation-selected
  threshold are recorded before final-test scoring. There is no validation refit.
- `predictions.csv`, `metrics.json`, `evaluation.md`, and `report.md` agree with
  the genuine execution; provenance records source, data, and artifact hashes.
- The inference contract, feature dictionary, experiment log, requirements,
  solution analysis, data-quality report, and model card travel with the model.

The train-only pipeline follows scikit-learn's
[official guidance on preprocessing and data leakage](https://scikit-learn.org/stable/common_pitfalls.html#data-leakage).

Training permits controlled missing sessions to demonstrate train-only imputation.
Serving requires complete finite inputs, which callers must repair upstream. The
imputer parameters are still included in the artifact for auditing the fitted
training transformation.

This is educational synthetic data, with no confidence intervals, real customer
claims, causal conclusions, measured business lift, fairness certification, or
production-readiness claim. A real project requires its own decision costs,
capacity constraints, data rights, cohort evaluation, uncertainty, and monitoring.
