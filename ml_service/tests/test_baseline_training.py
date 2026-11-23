"""HU-08 — Unit tests for baseline training use case."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.application.baseline_training import (
    HU08_RANDOM_STATE,
    HU08_TEST_SIZE,
    BaselineTrainingService,
    select_baseline_model,
)
from src.application.dataset_split import DEFAULT_TEST_SIZE, split_dataset
from src.application.features import TARGET_COLUMN
from src.application.transformation import TransformationService
from src.domain.models import ModelMetricRow
from src.infrastructure.storage import load_estimator


def _make_df(n: int = 200, seed: int = 7, failures: int = 40) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    types = rng.choice(["L", "M", "H"], size=n)
    target = np.array([0] * (n - failures) + [1] * failures)
    rng.shuffle(target)
    return pd.DataFrame({
        "UDI": list(range(1, n + 1)),
        "Product ID": [f"L{i}" for i in range(n)],
        "Type": types,
        "Air temperature [K]": rng.uniform(296, 304, n),
        "Process temperature [K]": rng.uniform(307, 313, n),
        "Rotational speed [rpm]": rng.integers(1200, 2800, n).astype(float),
        "Torque [Nm]": rng.uniform(10, 70, n),
        "Tool wear [min]": rng.integers(0, 250, n).astype(float),
        TARGET_COLUMN: target,
        "TWF": rng.integers(0, 2, n),
        "HDF": rng.integers(0, 2, n),
        "PWF": rng.integers(0, 2, n),
        "OSF": rng.integers(0, 2, n),
        "RNF": rng.integers(0, 2, n),
    })


class TestBaselineTraining(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.csv = self.root / "train.csv"
        self.model_path = self.root / "modelo.joblib"
        self.report_path = self.root / "model_baseline.md"
        self.df = _make_df()
        self.df.to_csv(self.csv, index=False)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_hu08_split_is_75_25_stratified_and_reproducible(self) -> None:
        first = split_dataset(
            self.df, test_size=HU08_TEST_SIZE, random_state=HU08_RANDOM_STATE
        )
        second = split_dataset(
            self.df, test_size=HU08_TEST_SIZE, random_state=HU08_RANDOM_STATE
        )

        self.assertEqual(first.train_rows, 150)
        self.assertEqual(first.test_rows, 50)
        self.assertTrue(first.stratified)
        self.assertEqual(first.random_state, HU08_RANDOM_STATE)
        pd.testing.assert_frame_equal(first.train, second.train)
        pd.testing.assert_frame_equal(first.test, second.test)
        self.assertEqual(DEFAULT_TEST_SIZE, 0.2)

    def test_single_class_falls_back_without_stratification(self) -> None:
        df = self.df.copy()
        df[TARGET_COLUMN] = 0
        split = split_dataset(
            df, test_size=HU08_TEST_SIZE, random_state=HU08_RANDOM_STATE
        )
        self.assertFalse(split.stratified)
        self.assertEqual(split.train_rows + split.test_rows, len(df))

    def test_missing_csv_fails_without_writing_model(self) -> None:
        missing = self.root / "missing.csv"
        with self.assertRaises(FileNotFoundError):
            BaselineTrainingService().run(missing, self.model_path, self.report_path)
        self.assertFalse(self.model_path.exists())

    def test_empty_csv_fails_without_writing_model(self) -> None:
        empty = self.root / "empty.csv"
        empty.write_text("", encoding="utf-8")
        with self.assertRaises(ValueError):
            BaselineTrainingService().run(empty, self.model_path, self.report_path)
        self.assertFalse(self.model_path.exists())

    def test_pipeline_fitted_only_on_train(self) -> None:
        split = split_dataset(
            self.df, test_size=HU08_TEST_SIZE, random_state=HU08_RANDOM_STATE
        )
        X_train, _ = TransformationService.split_features_target(split.train)
        service = TransformationService()
        service.fit_transform(X_train)
        scaler = (
            service.pipeline.named_steps["col_transformer"]
            .named_transformers_["scaler"]
        )
        train_air_mean = (
            X_train["Process temperature [K]"] - X_train["Air temperature [K]"]
        )
        # First continuous columns include Air temperature; check its mean matches train.
        air_idx = 0
        self.assertAlmostEqual(
            scaler.mean_[air_idx],
            X_train["Air temperature [K]"].mean(),
            places=10,
        )
        self.assertNotAlmostEqual(
            scaler.mean_[air_idx],
            self.df["Air temperature [K]"].mean(),
            places=6,
        )
        self.assertGreater(len(train_air_mean), 0)

    def test_training_writes_artifact_report_and_selects_by_metrics(self) -> None:
        result = BaselineTrainingService().run(
            self.csv, self.model_path, self.report_path
        )

        self.assertTrue(self.model_path.is_file())
        self.assertTrue(self.report_path.is_file())
        self.assertEqual(result.test_size, HU08_TEST_SIZE)
        self.assertEqual(result.random_state, HU08_RANDOM_STATE)
        self.assertEqual({row.name for row in result.metrics}, {
            "logistic_regression",
            "random_forest",
        })
        self.assertEqual(
            result.selected_model,
            select_baseline_model(result.metrics),
        )

        report = self.report_path.read_text(encoding="utf-8")
        for header in ("Accuracy", "Precision", "Recall", "F1", "ROC-AUC"):
            self.assertIn(header, report)
        self.assertIn(f"`{result.selected_model}`", report)
        self.assertIn(str(result.random_state), report)

        model = load_estimator(self.model_path)
        X, _ = TransformationService.split_features_target(self.df.head(5))
        preds = model.predict(X)
        self.assertEqual(len(preds), 5)

    def test_selection_prefers_higher_f1_then_recall_then_random_forest(self) -> None:
        rows = [
            ModelMetricRow("logistic_regression", 0.9, 0.5, 0.4, 0.5, 0.8),
            ModelMetricRow("random_forest", 0.9, 0.5, 0.4, 0.6, 0.8),
        ]
        self.assertEqual(select_baseline_model(rows), "random_forest")

        tied_f1 = [
            ModelMetricRow("logistic_regression", 0.9, 0.5, 0.7, 0.6, 0.8),
            ModelMetricRow("random_forest", 0.9, 0.5, 0.4, 0.6, 0.8),
        ]
        self.assertEqual(select_baseline_model(tied_f1), "logistic_regression")

        full_tie = [
            ModelMetricRow("logistic_regression", 0.9, 0.5, 0.5, 0.6, 0.8),
            ModelMetricRow("random_forest", 0.9, 0.5, 0.5, 0.6, 0.8),
        ]
        self.assertEqual(select_baseline_model(full_tie), "random_forest")


if __name__ == "__main__":
    unittest.main()
