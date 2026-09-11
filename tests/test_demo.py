"""Behavioral checks for the synthetic reference workflow."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "subscription-retention"
SPEC = importlib.util.spec_from_file_location("retention_workflow", EXAMPLE / "workflow.py")
wf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(wf)


class DemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.source = cls.root / "synthetic.csv"
        wf.generate_data().to_csv(cls.source, index=False)
        cls.output = cls.root / "first"
        cls.metrics, cls.model, cls.manifest = wf.train_file(cls.source, cls.output)
        cls.data = wf.prepare(pd.read_csv(cls.source))
        cls.splits, _ = wf.split_data(cls.data)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_disjoint_chronology_and_label_maturity(self):
        train, val, test = (self.splits[name] for name in ["train", "validation", "test"])
        self.assertLess(train.outcome_available_at.max(), val.as_of.min())
        self.assertLess(val.outcome_available_at.max(), test.as_of.min())
        ids = [set(self.manifest[name]["ids"]) for name in ["train", "validation", "test", "excluded"]]
        self.assertEqual(sum(map(len, ids)), len(set.union(*ids)))
        self.assertEqual(len(set.union(*ids)), 1200)
        self.assertTrue((test.outcome_available_at <= test.extracted_at).all())
        self.assertEqual([len(train), len(val), len(test)], [630, 210, 285])

    def test_preprocessing_learned_only_from_training(self):
        train = self.splits["train"][wf.FEATURES]
        medians = train.median().to_numpy()
        np.testing.assert_allclose(self.model["imputer_medians"], medians)
        np.testing.assert_allclose(self.model["scaler_mean"], train.fillna(train.median()).mean().to_numpy())
        self.assertFalse(np.allclose(self.model["scaler_mean"], self.data[wf.FEATURES].fillna(self.data[wf.FEATURES].median()).mean()))
        self.assertTrue(set(wf.EXCLUDED).isdisjoint(self.model["features"]))
        expected = hashlib.sha256("\n".join(self.splits["train"].customer_id).encode()).hexdigest()
        self.assertEqual(self.model["fit_row_ids_sha256"], expected)

    def test_test_outcomes_and_planted_leak_cannot_change_model(self):
        raw = pd.read_csv(self.source)
        test_ids = set(self.manifest["test"]["ids"])
        raw.loc[raw.customer_id.isin(test_ids), wf.TARGET] = 1 - raw.loc[raw.customer_id.isin(test_ids), wf.TARGET]
        raw["cancellation_confirmed_after_30d"] = 999
        changed = self.root / "changed.csv"
        raw.to_csv(changed, index=False)
        _, model, _ = wf.train_file(changed, self.root / "changed")
        self.assertEqual(self.model, model)

    def test_reports_metrics_and_predictions_agree(self):
        predictions = pd.read_csv(self.output / "predictions.csv")
        result = self.metrics["partitions"]["test"]["selected_model"]
        self.assertAlmostEqual(result["roc_auc"], roc_auc_score(predictions[wf.TARGET], predictions.churn_probability))
        report = (self.output / "report.md").read_text()
        for metric in ["roc_auc", "average_precision", "brier_score", "f1"]:
            self.assertIn(f"{result[metric]:.4f}", report)
        insight = (self.output / "insight.md").read_text()
        train = self.splits["train"]
        for label, mask in [("Support tickets >= 3", train.support_tickets_30d >= 3), ("Support tickets < 3", train.support_tickets_30d < 3)]:
            cohort = train.loc[mask, wf.TARGET]
            self.assertIn(f"| {label} | {len(cohort)} | {int(cohort.sum())} | {cohort.mean():.4f} |", insight)
        audit = (self.output / "leakage_audit.md").read_text()
        self.assertIn(f"{len(train)}/{len(train)} training rows", audit)
        self.assertIn(str(train.outcome_available_at.max().date()), audit)
        np.testing.assert_array_equal(predictions.review_flag, (predictions.churn_probability >= self.model["threshold"]).astype(int))
        provenance = json.loads((self.output / "provenance.json").read_text())
        for name, expected in provenance["artifact_sha256"].items():
            self.assertEqual(wf.digest(self.output / name), expected)

    def test_json_scoring_matches_training_predictions(self):
        frame = self.splits["test"].dropna(subset=wf.FEATURES)
        scored = wf.predict(frame[wf.FEATURES], wf.load_model(self.output / "model.json"))
        saved = pd.read_csv(self.output / "predictions.csv").set_index("customer_id")
        np.testing.assert_allclose(scored.churn_probability, saved.loc[frame.customer_id, "churn_probability"], rtol=1e-12)

    def test_inference_rejects_invalid_contract(self):
        valid = pd.read_csv(self.output / "inference_input.csv")
        cases = [valid.drop(columns=wf.FEATURES[0]), valid.assign(unexpected=1), valid.iloc[:0]]
        for bad in [np.nan, np.inf, -np.inf, "oops", -1]:
            cases.append(valid.assign(sessions_30d=bad))
        cases.extend([valid.assign(monthly_price=0), valid.assign(auto_renew=2)])
        for frame in cases:
            with self.subTest(columns=frame.columns.tolist()), self.assertRaises(ValueError):
                wf.predict(frame, self.model)

    def test_missing_sessions_do_not_bypass_other_training_constraints(self):
        raw = pd.read_csv(self.source)
        raw.loc[0, "sessions_30d"] = np.nan
        self.assertTrue(pd.isna(wf.prepare(raw).loc[0, "sessions_30d"]))
        for column, value in [("monthly_price", -100), ("monthly_price", 0), ("auto_renew", 7), ("tenure_months", -5), ("support_tickets_30d", -1)]:
            invalid = raw.copy()
            invalid.loc[0, column] = value
            with self.subTest(column=column, value=value), self.assertRaises(ValueError):
                wf.prepare(invalid)
        raw.loc[0, "sessions_30d"] = -np.inf
        with self.assertRaisesRegex(ValueError, "Infinite"):
            wf.prepare(raw)

    def test_training_cannot_fit_a_wholly_missing_feature(self):
        raw = pd.read_csv(self.source)
        raw.loc[raw.customer_id.isin(self.manifest["train"]["ids"]), "sessions_30d"] = np.nan
        source = self.root / "missing_training_sessions.csv"
        raw.to_csv(source, index=False)
        with self.assertRaisesRegex(ValueError, "at least one observed"):
            wf.train_file(source, self.root / "missing_training_sessions")

    def test_same_inputs_produce_identical_artifacts(self):
        second = self.root / "second"
        wf.train_file(self.source, second)
        for path in self.output.iterdir():
            self.assertEqual(path.read_bytes(), (second / path.name).read_bytes(), path.name)

    def test_standalone_train_and_predict_commands(self):
        out = self.root / "cli"
        subprocess.run([sys.executable, str(EXAMPLE / "train.py"), "--data", str(self.source), "--output-dir", str(out)], check=True, capture_output=True)
        result = self.root / "cli_predictions.csv"
        subprocess.run([sys.executable, str(EXAMPLE / "predict.py"), "--model", str(out / "model.json"), "--input", str(out / "inference_input.csv"), "--output", str(result)], check=True, capture_output=True)
        self.assertEqual(len(pd.read_csv(result)), 12)
        self.assertEqual(json.loads((out / "model.json").read_text()), self.model)


if __name__ == "__main__":
    unittest.main()
