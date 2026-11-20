"""HU-07 — Unit tests for feature matrix validation."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np
import pandas as pd

from src.application.features import EXPECTED_FEATURE_COLUMNS, TARGET_COLUMN
from src.application.matrix_validation import validate_feature_matrix
from src.domain.models import ValidationCheck
from src.infrastructure.reporting import build_matrix_validation_report
from src.interfaces.cli.commands import run_validate_cmd


def _make_valid(n: int = 30) -> tuple[pd.DataFrame, pd.Series]:
    rng = np.random.default_rng(11)
    data = {
        col: rng.normal(size=n) for col in EXPECTED_FEATURE_COLUMNS
    }
    X = pd.DataFrame(data)
    y = pd.Series(rng.integers(0, 2, n), name=TARGET_COLUMN)
    return X, y


def _by_criterion(
    checks: list[ValidationCheck], criterion: int
) -> ValidationCheck:
    return next(check for check in checks if check.criterion == criterion)


class TestMatrixValidation(unittest.TestCase):

    def test_valid_matrix_passes_all_checks(self) -> None:
        X, y = _make_valid()
        result = validate_feature_matrix(X, y, source_file="matrix.csv")

        self.assertTrue(result.passed)
        self.assertEqual(len(result.checks), 6)
        self.assertEqual(result.x_shape, (30, 8))
        self.assertEqual(result.y_shape, (30,))
        self.assertTrue(all(check.passed for check in result.checks))

    def test_missing_documented_column_fails_criterion_one(self) -> None:
        X, y = _make_valid()
        result = validate_feature_matrix(X.drop(columns=["Temp_diff"]), y)
        self.assertFalse(_by_criterion(result.checks, 1).passed)

    def test_target_inside_matrix_fails_separation_and_leakage(self) -> None:
        X, y = _make_valid()
        X[TARGET_COLUMN] = y.values
        result = validate_feature_matrix(X, y)

        self.assertFalse(_by_criterion(result.checks, 2).passed)
        self.assertFalse(_by_criterion(result.checks, 5).passed)

    def test_nulls_fail_criterion_three(self) -> None:
        X, y = _make_valid()
        X.loc[0, "Temp_diff"] = np.nan
        result = validate_feature_matrix(X, y)
        self.assertFalse(_by_criterion(result.checks, 3).passed)

    def test_non_numeric_feature_fails_criterion_four(self) -> None:
        X, y = _make_valid()
        X["Temp_diff"] = X["Temp_diff"].astype(str)
        result = validate_feature_matrix(X, y)
        self.assertFalse(_by_criterion(result.checks, 4).passed)

    def test_forbidden_columns_fail_leakage_check(self) -> None:
        X, y = _make_valid()
        X["UDI"] = np.arange(len(X))
        result = validate_feature_matrix(X.drop(columns=["UDI"]), y)
        self.assertTrue(_by_criterion(result.checks, 5).passed)

        X["TWF"] = 0
        result = validate_feature_matrix(X, y)
        self.assertFalse(_by_criterion(result.checks, 5).passed)

    def test_report_contains_shape_and_checklist(self) -> None:
        X, y = _make_valid()
        result = validate_feature_matrix(X, y, source_file="matrix.csv")
        content = build_matrix_validation_report(result)

        self.assertIn("HU-07", content)
        self.assertIn("(30, 8)", content)
        self.assertIn("(30,)", content)
        self.assertIn("✔", content)
        self.assertIn("Verificación por criterio", content)

    def test_validate_cmd_exports_matrix_without_target(self) -> None:
        X, y = _make_valid()
        df = X.copy()
        df[TARGET_COLUMN] = y.values

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv = root / "transformed.csv"
            matrix = root / "features.csv"
            report = root / "validation.md"
            df.to_csv(csv, index=False)

            with redirect_stdout(io.StringIO()):
                code = run_validate_cmd(csv, matrix, report)

            self.assertEqual(code, 0)
            exported = pd.read_csv(matrix)
            self.assertListEqual(list(exported.columns), EXPECTED_FEATURE_COLUMNS)
            self.assertNotIn(TARGET_COLUMN, exported.columns)
            self.assertIn("(30, 8)", report.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
