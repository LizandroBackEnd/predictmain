"""HU-08 — CLI integration tests for the train command."""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd

from src.application.features import TARGET_COLUMN
from src.interfaces.cli.commands import run_train_cmd
from src.interfaces.cli.entrypoint import main


def _make_df(n: int = 160, seed: int = 3, failures: int = 32) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    target = np.array([0] * (n - failures) + [1] * failures)
    rng.shuffle(target)
    return pd.DataFrame({
        "UDI": list(range(1, n + 1)),
        "Product ID": [f"M{i}" for i in range(n)],
        "Type": rng.choice(["L", "M", "H"], size=n),
        "Air temperature [K]": rng.uniform(296, 304, n),
        "Process temperature [K]": rng.uniform(307, 313, n),
        "Rotational speed [rpm]": rng.integers(1200, 2800, n).astype(float),
        "Torque [Nm]": rng.uniform(10, 70, n),
        "Tool wear [min]": rng.integers(0, 250, n).astype(float),
        TARGET_COLUMN: target,
        "TWF": 0,
        "HDF": 0,
        "PWF": 0,
        "OSF": 0,
        "RNF": 0,
    })


class TestTrainCommand(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.csv = self.root / "input.csv"
        _make_df().to_csv(self.csv, index=False)
        self.model_path = self.root / "modelo.joblib"
        self.report_path = self.root / "model_baseline.md"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_train_cmd_success_writes_artifacts(self) -> None:
        with redirect_stdout(io.StringIO()):
            code = run_train_cmd(self.csv, self.model_path, self.report_path)
        self.assertEqual(code, 0)
        self.assertTrue(self.model_path.is_file())
        self.assertTrue(self.report_path.is_file())
        content = self.report_path.read_text(encoding="utf-8")
        self.assertIn("ROC-AUC", content)
        self.assertIn("Modelo seleccionado", content)

    def test_train_cmd_missing_input_exits_one_without_artifact(self) -> None:
        missing = self.root / "missing.csv"
        stderr = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
            code = run_train_cmd(missing, self.model_path, self.report_path)
        self.assertEqual(code, 1)
        self.assertFalse(self.model_path.exists())
        self.assertIn("not found", stderr.getvalue().lower())

    def test_entrypoint_train_routes_successfully(self) -> None:
        with redirect_stdout(io.StringIO()):
            code = main([
                "train",
                "--csv",
                str(self.csv),
                "--model",
                str(self.model_path),
                "--report",
                str(self.report_path),
            ])
        self.assertEqual(code, 0)
        self.assertTrue(self.model_path.is_file())


if __name__ == "__main__":
    unittest.main()
