"""Small, reproducible example. All people, behavior, and outcomes are synthetic."""
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, f1_score, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 42
FEATURES = ["tenure_months", "sessions_30d", "support_tickets_30d", "monthly_price", "auto_renew"]
TARGET = "churn_next_30d"
EXCLUDED = ["customer_id", "as_of", "outcome_available_at", "extracted_at", "cancellation_confirmed_after_30d", TARGET]
SCHEMA = FEATURES + EXCLUDED


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def generate_data(n=1200, seed=SEED):
    if n < 300:
        raise ValueError("At least 300 daily rows are required for maturity-aware splits")
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2021-01-01", periods=n)
    tenure = rng.integers(1, 49, n)
    sessions = rng.poisson(np.maximum(4, 14 - 3 * np.arange(n) / n))
    tickets = rng.poisson(1.3, n)
    price = rng.choice([9.0, 19.0, 29.0], n)
    renew = rng.binomial(1, 0.65, n)
    logits = 0.8 - 0.17 * sessions + 0.5 * tickets - 0.025 * tenure + 0.015 * price - 0.65 * renew
    target = rng.binomial(1, 1 / (1 + np.exp(-logits)))
    frame = pd.DataFrame(dict(zip(FEATURES, [tenure, sessions.astype(float), tickets, price, renew])))
    frame.loc[rng.choice(n, n // 25, replace=False), "sessions_30d"] = np.nan
    frame.loc[rng.choice(n, n // 100, replace=False), "sessions_30d"] = -1
    frame["customer_id"] = [f"synthetic-{i:05d}" for i in range(n)]
    frame["as_of"] = dates.strftime("%Y-%m-%d")
    frame["outcome_available_at"] = pd.DatetimeIndex(dates.to_numpy() + np.timedelta64(30, "D")).strftime("%Y-%m-%d")
    frame["extracted_at"] = str(dates[-1].to_datetime64().astype("datetime64[D]") + np.timedelta64(15, "D"))
    frame["cancellation_confirmed_after_30d"] = target  # Intentional leakage trap.
    frame[TARGET] = target
    return frame[SCHEMA]


def prepare(raw):
    if raw.columns.duplicated().any() or set(raw.columns) != set(SCHEMA):
        raise ValueError("Training columns must exactly match the documented synthetic schema")
    data = raw.copy()
    if data.customer_id.isna().any() or data.customer_id.duplicated().any():
        raise ValueError("One unique customer per row is required")
    for col in ["as_of", "outcome_available_at", "extracted_at"]:
        data[col] = pd.to_datetime(data[col], errors="raise")
        if data[col].isna().any():
            raise ValueError("Timestamps cannot be missing")
    if not data[TARGET].isin([0, 1]).all():
        raise ValueError("Target must be binary and nonmissing")
    if (data.outcome_available_at.to_numpy() < data.as_of.to_numpy() + np.timedelta64(30, "D")).any():
        raise ValueError("Outcome maturity must be at least 30 days after observation")
    for col in FEATURES:
        data[col] = pd.to_numeric(data[col], errors="raise")
    if np.isinf(data[FEATURES].to_numpy(dtype=float)).any():
        raise ValueError("Infinite values are invalid")
    data.loc[data.sessions_30d < 0, "sessions_30d"] = np.nan
    # The teaching source permits missing sessions; serving has a stricter contract.
    if data[FEATURES].drop(columns="sessions_30d").isna().any().any():
        raise ValueError("Only source sessions_30d may be missing")
    # Validate every row. This temporary placeholder is never used for fitting.
    validate_inference(data[FEATURES].fillna({"sessions_30d": 0}))
    return data.sort_values(["as_of", "customer_id"], kind="stable").reset_index(drop=True)


def split_data(data):
    val_start = data.as_of.iloc[int(len(data) * 0.55)]
    test_start = data.as_of.iloc[int(len(data) * 0.75)]
    mature = data.outcome_available_at <= data.extracted_at
    masks = {
        "train": mature & (data.as_of < val_start) & (data.outcome_available_at < val_start),
        "validation": mature & (data.as_of >= val_start) & (data.as_of < test_start) & (data.outcome_available_at < test_start),
        "test": mature & (data.as_of >= test_start),
    }
    splits = {name: data.loc[mask].copy() for name, mask in masks.items()}
    if any(len(part) < 20 for part in splits.values()):
        raise ValueError("Each temporal partition needs >=20 rows")
    if any(splits[name][TARGET].nunique() != 2 for name in ["train", "validation"]):
        raise ValueError("Train and validation require both target classes")
    manifest = {name: {"count": len(part), "ids": part.customer_id.tolist(), "as_of_min": str(part.as_of.min().date()), "as_of_max": str(part.as_of.max().date()), "last_label_available": str(part.outcome_available_at.max().date())} for name, part in splits.items()}
    assigned = masks["train"] | masks["validation"] | masks["test"]
    manifest["excluded"] = {"count": int((~assigned).sum()), "ids": data.loc[~assigned, "customer_id"].tolist(), "reason": "30-day maturity purge before validation/test, or not yet mature at extraction"}
    manifest["boundaries"] = {"validation_start": str(val_start.date()), "test_start": str(test_start.date()), "label_horizon_days": 30}
    return splits, manifest


def score(y, probabilities, threshold):
    if y.nunique() != 2:
        raise ValueError("ROC-AUC evaluation requires both target classes")
    return {"roc_auc": float(roc_auc_score(y, probabilities)), "average_precision": float(average_precision_score(y, probabilities)), "brier_score": float(brier_score_loss(y, probabilities)), "f1": float(f1_score(y, probabilities >= threshold, zero_division=0)), "n": len(y), "prevalence": float(y.mean()), "threshold": float(threshold)}


def validate_inference(frame):
    if len(frame) == 0 or frame.columns.duplicated().any() or set(frame.columns) != set(FEATURES):
        raise ValueError("Inference requires nonempty rows with exactly these columns: " + ", ".join(FEATURES))
    if any(frame[col].dtype.kind not in "iuf" for col in FEATURES):
        raise ValueError("All inference values must be numeric")
    values = frame[FEATURES].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Missing or nonfinite inference values are invalid")
    if (values < 0).any() or (frame.monthly_price <= 0).any() or not frame.auto_renew.isin([0, 1]).all():
        raise ValueError("Features must be nonnegative; monthly_price > 0; auto_renew in {0, 1}")
    return values


def validate_model(model):
    if model.get("format") != "retention-logistic-v1" or model.get("features") != FEATURES:
        raise ValueError("Unsupported model schema")
    for key in ["imputer_medians", "scaler_mean", "scaler_scale", "coefficients"]:
        values = np.asarray(model[key], dtype=float)
        if values.shape != (len(FEATURES),) or not np.isfinite(values).all():
            raise ValueError("Invalid model parameters: " + key)
    if (np.asarray(model["scaler_scale"]) <= 0).any() or not 0 <= model["threshold"] <= 1 or not np.isfinite(model["intercept"]):
        raise ValueError("Invalid scale, intercept, or threshold")


def predict(frame, model):
    values = validate_inference(frame)
    validate_model(model)
    scaled = (values - model["scaler_mean"]) / model["scaler_scale"]
    logits = scaled @ np.asarray(model["coefficients"]) + model["intercept"]
    probabilities = 1 / (1 + np.exp(-np.clip(logits, -700, 700)))
    return pd.DataFrame({"churn_probability": probabilities, "review_flag": (probabilities >= model["threshold"]).astype(int)})


def load_model(path):
    def reject_constant(value):
        raise ValueError("Invalid JSON numeric constant: " + value)
    model = json.loads(Path(path).read_text(), parse_constant=reject_constant)
    validate_model(model)
    return model


def train_file(data_path, output_dir, seed=SEED):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(data_path)
    data = prepare(raw)
    splits, manifest = split_data(data)
    train, val = splits["train"], splits["validation"]
    if train[FEATURES].isna().all().any():
        raise ValueError("Every training feature needs at least one observed value")
    candidates = {}
    validation = {}
    for c in [0.1, 1.0]:
        name = f"logistic_C={c}"
        candidate = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(C=c, max_iter=1000, random_state=seed))
        candidate.fit(train[FEATURES], train[TARGET])
        candidates[name] = candidate
        validation[name] = score(val[TARGET], candidate.predict_proba(val[FEATURES])[:, 1], 0.5)
    selected = max(candidates, key=lambda name: validation[name]["roc_auc"])
    fitted = candidates[selected]
    val_prob = fitted.predict_proba(val[FEATURES])[:, 1]
    # Prespecified threshold grid; ties favor the first (lower) threshold.
    threshold = max(np.round(np.arange(0.2, 0.801, 0.05), 2), key=lambda t: f1_score(val[TARGET], val_prob >= t, zero_division=0))
    imputer, scaler, logistic = fitted.steps[0][1], fitted.steps[1][1], fitted.steps[2][1]
    model = {"format": "retention-logistic-v1", "features": FEATURES, "imputer_medians": imputer.statistics_.tolist(), "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(), "coefficients": logistic.coef_[0].tolist(), "intercept": float(logistic.intercept_[0]), "threshold": float(threshold), "selected": selected, "fit_row_ids_sha256": hashlib.sha256("\n".join(train.customer_id).encode()).hexdigest()}
    write_json(output / "model.json", model)  # Freeze before accessing final test outcomes.
    dummy = DummyClassifier(strategy="prior").fit(train[FEATURES], train[TARGET])
    metrics = {"seed": seed, "selected": selected, "selection_metric": "validation ROC-AUC", "threshold_selection": "validation F1, fixed grid 0.20:0.05:0.80", "validation_candidates": validation, "partitions": {}, "excluded_features": EXCLUDED}
    for name in ["validation", "test"]:
        part = splits[name]
        probs = fitted.predict_proba(part[FEATURES])[:, 1]
        # Baseline rules are fixed in source before the experiment; no test tuning.
        rule = ((part.sessions_30d.fillna(imputer.statistics_[1]) <= 6) | (part.support_tickets_30d >= 3)).astype(float)
        metrics["partitions"][name] = {"selected_model": score(part[TARGET], probs, threshold), "dummy_prior": score(part[TARGET], dummy.predict_proba(part[FEATURES])[:, 1], 0.5), "fixed_rule": score(part[TARGET], rule.to_numpy(), 0.5)}
        if name == "test":
            predictions = part[["customer_id", "as_of", TARGET]].copy()
            predictions["churn_probability"] = probs
            predictions["review_flag"] = (probs >= threshold).astype(int)
            predictions.to_csv(output / "predictions.csv", index=False)
            part[FEATURES].dropna().head(12).to_csv(output / "inference_input.csv", index=False)
    write_json(output / "metrics.json", metrics)
    write_json(output / "split_manifest.json", manifest)
    write_reports(output, raw, splits, metrics, model)
    provenance = {"synthetic_only": True, "seed": seed, "input_sha256": digest(data_path), "python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scikit_learn": sklearn.__version__, "source_sha256": {p.name: digest(p) for p in sorted(Path(__file__).parent.glob("*.py"))}, "artifact_sha256": {p.name: digest(p) for p in sorted(output.iterdir()) if p.is_file() and p.name != "provenance.json"}}
    write_json(output / "provenance.json", provenance)
    return metrics, model, manifest


def write_reports(output, raw, splits, metrics, model):
    train, val, test = (splits[name] for name in ["train", "validation", "test"])
    result = metrics["partitions"]["test"]["selected_model"]
    n_bad = int((raw.sessions_30d < 0).sum())
    n_null = int(raw.sessions_30d.isna().sum())
    table = "| Method | ROC-AUC | AP | Brier | F1 |\n|---|---:|---:|---:|---:|\n" + "\n".join(f"| {name} | {s['roc_auc']:.4f} | {s['average_precision']:.4f} | {s['brier_score']:.4f} | {s['f1']:.4f} |" for name, s in metrics["partitions"]["test"].items())
    counts = f"{len(train)} training, {len(val)} validation, and {len(test)} final-test rows"
    insight_table = "| Training cohort | Rows (denominator) | Churned rows | Churn rate |\n|---|---:|---:|---:|\n"
    for label, mask in [("Support tickets >= 3", train.support_tickets_30d >= 3), ("Support tickets < 3", train.support_tickets_30d < 3)]:
        cohort = train.loc[mask, TARGET]
        rate = f"{cohort.mean():.4f}" if len(cohort) else "n/a (no rows)"
        insight_table += f"| {label} | {len(cohort)} | {int(cohort.sum())} | {rate} |\n"
    proxy_matches = int((train.cancellation_confirmed_after_30d == train[TARGET]).sum())
    reports = {
        "requirement.md": "# Requirement\n\n- **Decision:** rank voluntary subscription churn within 30 days to help a human review a fictional retention queue.\n- **Owners:** fictional product and data-owner roles.\n- **Success:** a reproducible run, honest fixed-baseline comparison, and visible leakage controls.\n- **Scope:** locally generated synthetic subscriptions; no real customers, intervention, profit claim, or automated action.\n- **Unresolved for real use:** capacity, intervention cost, consent, and deployment approval.\n",
        "req_analysis.md": "# Requirement analysis\n\n- **Observation unit:** one unique synthetic customer at a dated snapshot.\n- **Target:** churn within the next 30 days. All approved features are observable at the snapshot.\n- **Split:** chronological boundaries at 55% and 75% of source rows. Labels must mature strictly before the next partition; final-test labels must be mature at extraction.\n- **Baselines:** training-prevalence dummy and fixed rule (sessions <= 6 OR tickets >= 3).\n- **Candidates:** logistic regression C=0.1 and C=1.0.\n- **Selection:** validation ROC-AUC selects C; validation F1 on a prespecified grid selects the threshold.\n- **Freeze:** save the model before test scoring; no refit on validation.\n- **Interpretation:** synthetic F1 is a teaching objective, not a business utility estimate.\n",
        "eda_analysis.md": f"# Training-only EDA\n\nSynthetic data. Target exploration is restricted to the training partition: n={len(train)}; observed churn rate={train[TARGET].mean():.4f}. No final-test target exploration informed model or threshold choice.\n\n" + "| Feature | Missing after cleanup | Median |\n|---|---:|---:|\n" + "\n".join(f"| {col} | {train[col].isna().sum()} | {train[col].median():.4f} |" for col in FEATURES) + "\n\nSource intentionally includes an exact post-outcome proxy. Its known generation semantics exclude it before fitting. Feature distribution summaries above are descriptive, not causal.\n",
        "data_quality.md": f"# Data quality\n\nSource: {len(raw)} synthetic rows, unique customer IDs, 30-day outcome timestamps. Structural source checks cover all rows; target EDA covers training only. Sessions include {n_null} missing and {n_bad} negative sentinel values. Negative sessions become missing under a fixed domain rule; the median imputer learns from training only. Inference rejects missing/nonfinite inputs so callers must repair them upstream. Split retains {counts}; {len(raw)-len(train)-len(val)-len(test)} rows are excluded for label maturity. See split_manifest.json for all IDs and dates. No duplicate removal or target-dependent cleaning is used.\n",
        "insight.md": f"# Training-only synthetic insight\n\nQuestion: how does observed churn differ between snapshots with at least three support tickets in the preceding 30 days and those with fewer? Scope: the {len(train)} training rows only, from {train.as_of.min().date()} to {train.as_of.max().date()}. Each row is one unique synthetic customer; denominators include every training row in its cohort.\n\n{insight_table}\nThis is a descriptive association, not a causal effect of support tickets or evidence that a retention intervention works. The generator explicitly gives ticket count a positive coefficient in its outcome probability, so an association is expected by construction. No confidence interval or population inference is claimed; an empty cohort has no estimable rate. This summary did not select features, model parameters, or thresholds.\n\nNext evidence for a real project: confirm point-in-time ticket availability and label maturity; estimate cohort uncertainty and assess tenure, usage, and plan differences in a separate prospective cohort. Test any retention intervention with an appropriately designed experiment before claiming lift.\n",
        "leakage_audit.md": f"# Leakage audit: bounded synthetic evidence\n\nScope: this documented generator and this execution, not a universal leakage-free certification.\n\n| Check | Evidence in this run |\n|---|---|\n| Planted future proxy | The generator assigns cancellation_confirmed_after_30d from the future target. It matches the target in {proxy_matches}/{len(train)} training rows; availability semantics exclude it regardless of that match rate. |\n| Feature allowlist | The fitted model contains only {', '.join(model['features'])}. Target, IDs, future proxy, and audit timestamps are absent. |\n| Training label maturity | Latest retained training label: {train.outcome_available_at.max().date()}; first validation snapshot: {val.as_of.min().date()}. |\n| Validation label maturity | Latest retained validation label: {val.outcome_available_at.max().date()}; first test snapshot: {test.as_of.min().date()}. |\n| Final label maturity | {(test.outcome_available_at <= test.extracted_at).sum()}/{len(test)} retained test labels are available by their extraction date. |\n| Fit boundaries | Imputer, scaler, logistic candidates, and prevalence dummy fit only {len(train)} training rows. model.json records medians, scaling parameters, and the hash of fitted row IDs. |\n| Selection boundaries | Validation selects {model['selected']} and threshold {model['threshold']:.2f}; model.json is written before final-test scoring, with no validation refit. |\n\nTrace the exact row IDs and timestamps in split_manifest.json, parameter values in model.json, candidate comparisons in experiment_log.md, and source/data/artifact hashes in provenance.json. Behavioral tests check train-only fitted statistics and verify that changing final-test outcomes or the planted proxy cannot change the saved model.\n\nLimits: the example does not establish real-world feature lineage, event-time correctness, hidden proxies, repeat-customer handling, or operational data availability. For new data, independently audit each feature's origin and availability, joins and aggregates, entity boundaries, and target definition before accepting any leakage conclusion.\n",
        "feature_dictionary.md": "# Feature dictionary\n\n| Field | Meaning / availability | Decision |\n|---|---|---|\n| tenure_months | Nonnegative subscription age at snapshot | Include |\n| sessions_30d | Sessions in preceding 30 days | Include; source missing values imputed from train median |\n| support_tickets_30d | Tickets in preceding 30 days | Include |\n| monthly_price | Fictional positive plan price at snapshot | Include |\n| auto_renew | 0 or 1 at snapshot | Include |\n| customer_id | Unique synthetic identifier | Exclude; bookkeeping only |\n| as_of, outcome_available_at, extracted_at | Snapshot, label-maturity, extraction dates | Split/audit only |\n| cancellation_confirmed_after_30d | Exact future outcome proxy intentionally planted | Exclude: leakage |\n| churn_next_30d | Future 30-day outcome | Target only |\n\nTraining-derived features: median-imputed, standardized numeric values; no feature selection or transformations use validation/test fit statistics.\n",
        "experiment_log.md": "# Experiment log\n\nPrespecified candidates: logistic regression C=0.1 and C=1.0; fixed seed; train-fit median imputer and scaler in each pipeline. No iterative test-driven optimization.\n\n" + "\n".join(f"- {name}: validation ROC-AUC={s['roc_auc']:.4f}." for name, s in metrics["validation_candidates"].items()) + f"\n\nSelected {metrics['selected']} using validation ROC-AUC (ties: first candidate). Threshold={model['threshold']:.2f} selected by validation F1 from 0.20 to 0.80 in 0.05 increments (ties: lower threshold). Model JSON was written before final-test scoring.\n",
        "evaluation.md": f"# Final test evaluation\n\nSynthetic, untouched final temporal holdout: n={len(test)}, prevalence={test[TARGET].mean():.4f}. Choice and threshold were frozen before scoring.\n\n{table}\n\nAP = average precision. Higher ROC-AUC/AP/F1 and lower Brier are preferable. Point estimates only: no uncertainty intervals or production-readiness assertion. Threshold is chosen on synthetic validation F1; performance may change with time. Future real work requires cohort uncertainty, calibration, capacity-aware utility and prospective monitoring.\n",
        "model_card.md": f"# Model card\n\nModel: {metrics['selected']}; threshold={model['threshold']:.2f}. Synthetic educational churn ranking; human review only. Inputs are the five snapshot numeric features in feature_dictionary.md. Pipeline parameters fit exclusively to training. Saved as plain JSON containing coefficients and scaler statistics; no pickle or executable model loading.\n\nNot validated for real customers or operational decisions. Generator embeds associations by construction and modest temporal drift; they are not causal discoveries. No subgroup fairness assessment is possible because this teaching dataset defines no relevant groups. A real model needs a data/label audit, subgroup assessment, uncertainty, monitoring thresholds, ownership and approval. Distribution drift and real-world calibration remain untested.\n",
        "inference_contract.md": "# Inference contract\n\nInput CSV must be nonempty and contain exactly the five FEATURES columns listed in model.json. Column order may vary; names may not. Each value must be a finite number; all features >=0, monthly_price >0, auto_renew in {0,1}. Missing cells, extra target/ID/leakage columns, nonnumeric text, NaN and infinities are rejected. Inputs describe information already available at prediction time; the CLI cannot verify real-world lineage.\n\nOutput: churn_probability in [0,1] and review_flag using the frozen threshold. No intervention is triggered. JSON model format retention-logistic-v1 is schema-checked; no pickle is loaded. Use only reviewed artifacts with a verified provenance hash. The training source allows a controlled sessions missingness demonstration, but serving requires complete rows.\n",
        "report.md": f"# Subscription retention: evidence before prediction\n\n**Synthetic demonstration; no real business inference.**\n\nA complete run retained {counts}. It discarded immature labels, excluded an intentionally planted future-outcome proxy, and fit all preprocessing exclusively on training rows.\n\nValidation selected **{metrics['selected']}** with a frozen threshold of **{model['threshold']:.2f}**. Final-test ROC-AUC: **{result['roc_auc']:.4f}**; AP: **{result['average_precision']:.4f}**; Brier: **{result['brier_score']:.4f}**; F1: **{result['f1']:.4f}**.\n\n{table}\n\nThese measurements describe one seeded generator and temporal holdout, with no confidence intervals. They do not establish customer retention lift, causality or production readiness. Next step for a real project: approve the decision, label availability, evaluation costs, cohorts and monitoring plan before collecting customer data.\n\nEvidence: metrics.json, split_manifest.json, predictions.csv, model.json and provenance.json.\n",
    }
    for name, body in reports.items():
        if name == "model_card.md":
            body += "\n## Model interpretation\n\nStandardized logistic coefficients are changes in fitted log-odds per training-standard-deviation change, holding other inputs fixed. These describe fitted associations, not causal effects or stable feature importance.\n\n| Feature | Coefficient |\n|---|---:|\n" + "\n".join(f"| {feature} | {coefficient:.4f} |" for feature, coefficient in zip(FEATURES, model["coefficients"])) + "\n"
        (output / name).write_text(body)
