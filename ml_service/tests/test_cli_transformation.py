"""HU-06 — CLI integration tests for transformation commands."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd

from src.application.dataset_split import split_dataset
from src.application.features import EXPECTED_FEATURE_COLUMNS, TARGET_COLUMN
from src.application.transformation import TransformationService
from src.infrastructure.storage import load_pipeline
from src.interfaces.cli.commands import run_apply_cmd, run_transform_cmd


def _make_df(n: int = 120, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    types = rng.choice(["L", "M", "H"], size=n)
    return pd.DataFrame({
        "UDI": list(range(1, n + 1)),
        "Product ID": [f"L{i}" for i in range(n)],
        "Type": types,
        "Air temperature [K]": rng.uniform(296, 304, n),
        "Process temperature [K]": rng.uniform(307, 313, n),
        "Rotational speed [rpm]": rng.integers(1200, 2800, n).astype(float),
        "Torque [Nm]": rng.uniform(10, 70, n),
        "Tool wear [min]": rng.integers(0, 250, n).astype(float),
        TARGET_COLUMN: rng.integers(0, 2, n),
        "TWF": rng.integers(0, 2, n),
        "HDF": rng.integers(0, 2, n),
        "PWF": rng.integers(0, 2, n),
        "OSF": rng.integers(0, 2, n),
        "RNF": rng.integers(0, 2, n),
    })


class TestTransformationCommands(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.df = _make_df()
        self.csv = self.root / "input.csv"
        self.df.to_csv(self.csv, index=False)
        self.output = self.root / "transformed.csv"
        self.pipeline_path = self.root / "pipeline.joblib"
        self.report_path = self.root / "transformation_report.md"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _fit(self) -> None:
        with redirect_stdout(io.StringIO()):
            code = run_transform_cmd(
                self.csv, self.output, self.pipeline_path, self.report_path
            )
        self.assertEqual(code, 0)

    def test_transform_cmd_fits_only_on_train_and_reports_it(self) -> None:
        self._fit()

        transformed = pd.read_csv(self.output)
        self.assertEqual(len(transformed), len(self.df))
        self.assertListEqual(
            list(transformed.columns), EXPECTED_FEATURE_COLUMNS + [TARGET_COLUMN]
        )

        content = self.report_path.read_text(encoding="utf-8")
        self.assertIn("Anti-leakage", content)
        self.assertIn("Registros usados en `fit`", content)

        split = split_dataset(self.df)
        X_train, _ = TransformationService.split_features_target(split.train)
        pipeline = load_pipeline(self.pipeline_path)
        scaler = (
            pipeline.named_steps["col_transformer"]
            .named_transformers_["scaler"]
        )
        self.assertAlmostEqual(
            scaler.mean_[0], X_train["Air temperature [K]"].mean(), places=10
        )

    def test_apply_cmd_uses_saved_pipeline_without_refitting(self) -> None:
        self._fit()
        before = load_pipeline(self.pipeline_path)
        before_scaler = (
            before.named_steps["col_transformer"]
            .named_transformers_["scaler"]
            .mean_.copy()
        )

        new_df = _make_df(n=8, seed=99)
        new_csv = self.root / "new.csv"
        new_df.to_csv(new_csv, index=False)
        new_output = self.root / "applied.csv"

        with redirect_stdout(io.StringIO()):
            code = run_apply_cmd(new_csv, new_output, self.pipeline_path)
        self.assertEqual(code, 0)

        applied = pd.read_csv(new_output)
        self.assertEqual(len(applied), len(new_df))
        self.assertListEqual(
            list(applied.columns), EXPECTED_FEATURE_COLUMNS + [TARGET_COLUMN]
        )

        after = load_pipeline(self.pipeline_path)
        after_scaler = (
            after.named_steps["col_transformer"]
            .named_transformers_["scaler"]
            .mean_
        )
        np.testing.assert_array_equal(before_scaler, after_scaler)


if __name__ == "__main__":
    unittest.main()
