# Subscription model leakage audit

## Conclusion

The reported **0.99 ROC AUC is not presently suitable evidence of next-month predictive performance**. It is reported in the brief but cannot be reproduced or tied to an evaluated dataset with the supplied artifacts. Static code inspection confirms preprocessing is fitted before the train/test split and that the split does not implement the future-period evaluation required by the intended use. The cancellation join also creates a serious, unresolved feature-availability risk.

This is an artifact review, not an executed model evaluation. No training code was run, no data was invented, and no source files were changed. No corrected score can be estimated from the supplied evidence.

## Prediction contract

| Item | Contract or current uncertainty | Evidence |
| --- | --- | --- |
| Decision | Produce a weekly customer outreach queue. | `brief.md:2` |
| Prediction timestamp | `snapshot_at`. | `brief.md:2–3` |
| Observation unit | A customer at a weekly snapshot; the same customer recurs. | `brief.md:3`, `metadata.json:1` |
| Target | Cancellation within the following 30 days. SQL uses an inclusive `BETWEEN` from `snapshot_at` through `snapshot_at + 30 days`. Treatment of an event exactly at prediction time needs agreement. | `brief.md:3`, `feature_query.sql:3–4` |
| Label availability | At least the end of the 30-day outcome window, plus any cancellation ingestion delay. That delay and completeness of source coverage are unknown. | `metadata.json:1`; no ingestion or available-at field supplied |
| Deployment population | Next month's observations, including existing customers. Entirely unseen-customer performance is not the stated objective. | `brief.md:4` |
| Observation period | Metadata states `2025-01-01 to 2025-12-31`; whether this is exactly the set of snapshot dates was not verified. | `metadata.json:1` |
| Extract date | Metadata states `2026-02-01`. Calendar time would allow a December 31 snapshot's 30-day window to end before extraction, but this does not establish complete outcome ingestion or availability at historical fit dates. | `metadata.json:1` |
| Reported population | 52,000 rows and 1,000 distinct customers according to metadata. These are unverified metadata counts, not inspected row counts. | `metadata.json:1` |
| Metric | Reported ROC AUC of 0.99; score report, prediction outputs, and previous experiment history are unavailable. | `brief.md:5` |

Existing customers can legitimately appear in both earlier training periods and a later evaluation period for this use case. The audit does **not** require a customer-disjoint split by default. It does require chronological information boundaries, mature training labels, and a clear assessment of dependence among recurring observations.

## Coverage and artifact versions

Inspected the complete contents of four files under `input/`. File references below are relative to that directory. SHA-256 hashes identify the exact reviewed versions; no repository revision was supplied.

| Artifact | Lines inspected | SHA-256 |
| --- | --- | --- |
| `brief.md` | 1–5 | `f8927f5271f9c5e0a911f62087b9ca37f2ac2af164ea46b5a342a19fb67aebbc` |
| `feature_query.sql` | 1–8 | `b8283796d06a84f101e0812cc6e3114ad98a4312e59b76d805a9b8188387788c` |
| `metadata.json` | 1 | `e995ea0b3a63f3fc2d6cdd8c584d65e2ab5ed84b48214dffd4bf9fb7ba79c335` |
| `train.py` | 1–13 | `3896bccd326fec99ccc5f49052199f065fe04f33313045c8d69f2c3881c29622` |

`training.csv`, actual source tables, feature lineage, row memberships, trained artifacts, inference contract, score report, and selection history were not supplied. Row-level coverage is zero: no data rows or predictions were available to inspect. Code and metadata findings must not be described as measured row-level effects.

## Confirmed issues in the supplied implementation

“Confirmed” here means directly established by the inspected code or specification. It does not prove that this exact code produced the reported 0.99 score or quantify how much each issue changes performance.

| Severity | Feature or stage | Observed evidence | Information boundary violated or missing | Smallest repair |
| --- | --- | --- | --- | --- |
| High | Learned imputation | `train.py:10` calls `SimpleImputer().fit_transform(X)` before the split at line 11. | The imputer learns from the complete input matrix, including rows later assigned to evaluation. This is a confirmed fit-scope violation; its numerical effect depends on the unavailable missingness pattern. | Split raw rows first. Put imputation in a fitted preprocessing pipeline and fit only on each training partition. Transform validation/test data with that fitted object. |
| High | Evaluation split for future use | The brief specifies next-month observations (`brief.md:4`), but `train.py:9` removes timestamps and line 11 uses `train_test_split` with no chronological membership logic. | The supplied procedure does not enforce training-before-evaluation ordering or a historical fit date. It therefore does not assess the stated forward use. Actual membership and future/earlier row intersections cannot be measured without data. | Retain timestamps for split construction. Define future validation/test periods and a simulated fit date; admit only training rows whose labels had matured and arrived by that date. |
| Moderate | Categorical representation | `train.py:9` applies `pd.get_dummies` to the full dataset before line 11 splits it. | The feature vocabulary is informed by evaluation rows. This is transductive preprocessing, not demonstrated target encoding. Its effect is unknown. | Fit a categorical encoder using each training partition and apply an explicit unknown-category policy to later data. Include the encoder in the saved pipeline. |
| High | Availability controls on joined inputs | `feature_query.sql:5` selects `c.cancellation_reason`; lines 7–8 join cancellations only by `customer_id`, without any prediction-time or availability predicate. `metadata.json:1` states availability timestamps are not recorded. | The query does not enforce that a joined value existed at `snapshot_at`. The absence of this control is confirmed. Actual future-value leakage remains an unresolved risk, described below. | Remove this input from a trustworthy evaluation until its definition and available-at lineage can be established; otherwise rebuild the feature with a point-in-time join using verified availability metadata. Keep outcome creation separate from feature creation. |

## Plausible risks requiring additional evidence

| Severity if realized | Feature or stage | Inspected evidence and why it matters | What is unverified | Practical next check or repair |
| --- | --- | --- | --- | --- |
| Critical | Outcome-derived or late `cancellation_reason` | SQL selects the reason from the same cancellations table used to create the future target (`feature_query.sql:3–5`), without a time restriction. If the resulting column is present in `training.csv`, line 9 of `train.py` retains it as a predictor. | A name and table association do not establish when a reason was created or first available. The CSV columns, actual values, and whether a reason relates to the current or a prior cancellation are unavailable. | Obtain the field definition and creation/ingestion history. Trace representative values to their availability. Exclude values learned after prediction time; if availability cannot be established, exclude the feature from the new evaluation. |
| High | Label maturity and backfilled features | The target uses a 30-day future window, while the supplied split has no simulated fit date or maturity rule (`feature_query.sql:3–4`, `train.py:11`). Availability timestamps are absent (`metadata.json:1`). | Cannot measure which training labels would have been known at a historical fit date, whether cancellations arrived late, or whether snapshot values were later revised. | Require `label_window_end <= fit_time` and verified outcome ingestion completeness by fit time. Account for additional reporting delay. Reconstruct immutable snapshots or available-at history for predictors. |
| High | Repeated rows, related entities, or many-to-many join expansion | Customer records recur weekly (`brief.md:3`). The cancellation join is by customer only (`feature_query.sql:8`). | Recurring customers alone do not establish leakage for this deployment. Actual train/test customer overlap, duplicated snapshots, household dependence, and the number of cancellations per customer cannot be checked. Multiple cancellation records could multiply snapshot rows or create inconsistent target rows, but multiplicity was not observed. | Verify one intended row per customer/snapshot, cancellation cardinality, and cross-boundary duplicates. Define an event-based label, for example a correctly bounded existence check, rather than allowing multiple joined outcomes to multiply rows. Assess uncertainty with the recurring-customer dependence in mind. |
| High | Held-out outcomes used in selection | `brief.md:5` explicitly says previous experiment history and the report are unavailable. `train.py:13` prints a test score. | The supplied script does not show threshold tuning, hyperparameter searches, repeated model choices, or calibration. Their absence here does not prove the test was untouched. No holdout contamination is confirmed. | Recover run logs and decision history, including feature selection and informal test peeking. If test outcomes influenced any choice, use genuinely fresh holdout data or a prospective evaluation. Renaming the same rows is insufficient. |
| High | Training/serving mismatch | Training drops only `snapshot_at` and `customer_id`, retaining other CSV columns (`train.py:9`); no inference schema or serving code is supplied. | Cannot establish that production will provide the same values, types, units, category handling, or feature availability, or that preprocessing will be reused. | Define the prediction-time input contract and compare it to a saved train-only preprocessing/model pipeline. Validate representative inference inputs without refitting. |
| Moderate | Feature construction outside the shown query | The query selects `s.sessions_last_7d` and `s.tenure_days` directly (`feature_query.sql:2,6`). | Their names suggest historical quantities but upstream window logic, refresh timing, and backfills were not supplied. | Inspect upstream queries and available-at records. Verify the session window ends at or before prediction and uses only events available then; verify the tenure reference date is the prediction date. |

## Feature availability assessment

All prediction-time comparisons are against the row's `snapshot_at`. “Unknown” is an evidence status, not permission to use the feature without review.

| Field | Value source | Available-at time | Prediction time | Disposition for the next trustworthy evaluation | Reason |
| --- | --- | --- | --- | --- | --- |
| `customer_id` | `weekly_snapshots.customer_id`, used as join key | Unknown | `snapshot_at` | Allowed as an audit/join identifier; excluded from model by current script | Retain outside the feature matrix for lineage and membership checks. No availability issue was established, but source access and identity stability are unverified. |
| `snapshot_at` | `weekly_snapshots.snapshot_at` | Timestamp exists in query; snapshot materialization time unknown | The field itself defines prediction time | Required as split/audit metadata; excluded from model by current script | An event/snapshot timestamp does not prove the other values were available then. |
| `sessions_last_7d` | Precomputed value in `weekly_snapshots` | Unknown; no upstream lineage or availability timestamp | `snapshot_at` | Unknown pending lineage check | Need verified lookback boundaries and ingestion timing. A past-looking name alone is insufficient. |
| `tenure_days` | Precomputed value in `weekly_snapshots` | Unknown | `snapshot_at` | Unknown pending lineage check | Need to confirm this is computed as of prediction, not extraction. |
| `cancellation_reason` | `cancellations`, customer-only join | Unknown; no availability timestamps recorded | `snapshot_at` | Exclude provisionally until safe timing is proven | Serious risk of outcome-related or future information; no point-in-time restriction. Actual creation timing was not supplied. |
| `cancelled_next_30d` | `CASE` over cancellation event time from `snapshot_at` to `snapshot_at + 30 days` | After the full outcome window and any ingestion delay; exact delay unknown | `snapshot_at` | Excluded as predictor; used as label only when mature | Current script correctly removes this named target from `df` at line 8. That does not prove other fields are free of target information. |

The actual CSV schema was unavailable. This table covers only the query's selected fields, not undisclosed CSV columns or derived values.

## Interpretation of the reported metrics

- **0.99 ROC AUC:** an unverified reported result. The score artifact, evaluated rows, target prevalence, prediction vector, and code-to-result linkage are absent.
- **What the shown code would compute if executed successfully:** ROC AUC on a random held-out subset after full-dataset preprocessing. That describes a compromised retrospective procedure; it does not establish performance on the next month's outreach population.
- **What cannot be inferred:** corrected AUC, the magnitude of score inflation, whether one suspected feature explains the score, confidence intervals, operational precision at outreach capacity, calibrated cancellation probabilities, or business impact.
- **What remains useful now:** the inspected code identifies specific repairs and evidence requests. No supplied numeric metric currently supports an approval to trust forward predictive performance. This audit does not conclude the model has no predictive value.

## Re-evaluation plan

1. **Preserve provenance.** Retain the reviewed code, full experiment/selection history, dataset extract identity, and any stored predictions. Obtain the missing training data through the project's authorized access route; do not export raw customer rows into the report.
2. **Agree the temporal contract.** Keep the stated weekly snapshot unit and future-month use, including existing customers. Specify target boundary semantics, snapshot materialization timing, outcome ingestion delay, and the simulated model fit dates.
3. **Rebuild point-in-time inputs and labels.** Separate target generation from feature joins. Check cancellation cardinality and row uniqueness. Establish upstream feature availability. Exclude `cancellation_reason` unless documented lineage proves it is valid at prediction. Do not treat the February extract date as proof of historical availability.
4. **Construct chronological partitions on raw rows.** Use earlier periods for training and later periods for validation. Purge or omit training snapshots whose 30-day labels, including reporting delay, were not known by the simulated fit date. Retain customers across time when that matches intended deployment; separately report the observed existing/new-customer mix if enough data are available.
5. **Fit every learned transformation within training boundaries.** Put imputation and categorical encoding in the actual training pipeline. During tuning, rebuild them within each training fold. Freeze model, feature, calibration, and decision-threshold choices using validation data only.
6. **Establish an honest final assessment set.** First determine whether the existing test outcomes influenced any choice. If they did, obtain genuinely fresh data or run a prospective assessment. If history cannot establish that a set remained untouched, state that uncertainty and prefer prospective assessment; do not promise independence merely by redrawing a split.
7. **Record evaluation evidence.** Save partition memberships or safe manifests, date ranges, mature-label checks, source availability evidence, class counts, duplicate checks, fitted-transform scope, and prediction artifacts. Evaluate the frozen workflow. Report ROC AUC alongside metrics relevant to the outreach queue and uncertainty that accounts for recurring customers; choose these operational metrics before consulting final outcomes.
8. **Check inference parity.** Validate the saved preprocessing/model artifact against the documented input contract and prediction-time availability. Only then interpret the fresh results against the intended decision.

Execution and remediation were not part of this request. The plan above has not been run, and this report does not claim the model is leakage-free after a hypothetical repair.

## Evidence still needed

- Training dataset/version and selected CSV columns; actual timestamp, label, and membership distributions.
- Upstream feature definitions, creation/ingestion history, snapshot immutability or revision history, and cancellation-table cardinality.
- Outcome coverage and ingestion completeness through each required label window.
- The reported score artifact and the experiment, feature, threshold, calibration, and model-selection history.
- Saved preprocessing/model artifacts and the inference contract.

These gaps do not prevent identifying the confirmed code issues. They prevent quantifying their effects, confirming actual future-feature use, auditing final-holdout independence, and validating the reported performance.
