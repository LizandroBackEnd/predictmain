"""
HU-06 — Unit tests for the transformation pipeline.

Tests cover:
  1. Temp_diff derived feature exists and has correct values.
  2. One-Hot Encoding produces expected columns (Type_M, Type_H).
  3. Excluded columns (UDI, Product ID, failure modes) are not in output.
  4. transform() on test data does not re-fit the pipeline.
  5. Pipeline saved and reloaded produces identical output.
  6. transform() raises RuntimeError before fit_transform or load.
  7. verify_output() returns empty list on correct output.
  8. StandardScaler output has zero mean on training data.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.transformation.features import (
    DERIVED_FEATURE_NAME,
    EXPECTED_FEATURE_COLUMNS,
    EXCLUDE_COLUMNS,
    TARGET_COLUMN,
)
from src.transformation.service import TransformationService


def _make_df(n: int = 20, seed: int = 42) -> pd.DataFrame:
    """Return a minimal AI4I-shaped DataFrame with deterministic values."""
    rng = np.random.default_rng(seed)
    types = rng.choice(["L", "M", "H"], size=n)
    return pd.DataFrame({
        "UDI":                      list(range(1, n + 1)),
        "Product ID":               [f"L{i}" for i in range(n)],
        "Type":                     types,
        "Air temperature [K]":      rng.uniform(296, 304, n),
        "Process temperature [K]":  rng.uniform(307, 313, n),
        "Rotational speed [rpm]":   rng.integers(1200, 2800, n).astype(float),
        "Torque [Nm]":              rng.uniform(10, 70, n),
        "Tool wear [min]":          rng.integers(0, 250, n).astype(float),
        "Machine failure":          rng.integers(0, 2, n),
        "TWF":                      rng.integers(0, 2, n),
        "HDF":                      rng.integers(0, 2, n),
        "PWF":                      rng.integers(0, 2, n),
        "OSF":                      rng.integers(0, 2, n),
        "RNF":                      rng.integers(0, 2, n),
    })


class TestTransformationService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = TransformationService()
        self.df_train = _make_df(n=60, seed=1)
        self.df_test  = _make_df(n=20, seed=2)
        self.tmp = tempfile.TemporaryDirectory()
        self.pipeline_path = Path(self.tmp.name) / "pipeline.joblib"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _fit(self, df: pd.DataFrame | None = None) -> pd.DataFrame:
        df = df if df is not None else self.df_train
        X, _ = self.service.split_features_target(df)
        return self.service.fit_transform(X)

    # ------------------------------------------------------------------
    # Test 1 — Temp_diff derived feature is correct
    # ------------------------------------------------------------------
    def test_temp_diff_derived_feature_values(self) -> None:
        X_out = self._fit()
        self.assertIn(DERIVED_FEATURE_NAME, X_out.columns)

        X_in, _ = self.service.split_features_target(self.df_train)
        expected = (
            X_in["Process temperature [K]"] - X_in["Air temperature [K]"]
        ).values

        # After StandardScaler the values are scaled, but the relative
        # ordering must be preserved (monotone transformation)
        raw_col = (
            self.df_train["Process temperature [K]"]
            - self.df_train["Air temperature [K]"]
        ).values
        scaler_mean = raw_col.mean()
        scaler_std  = raw_col.std(ddof=0)
        expected_scaled = (raw_col - scaler_mean) / scaler_std

        np.testing.assert_allclose(
            X_out[DERIVED_FEATURE_NAME].values,
            expected_scaled,
            atol=1e-6,
        )

    # ------------------------------------------------------------------
    # Test 2 — One-Hot Encoding produces Type_L and Type_M
    # ------------------------------------------------------------------
    def test_ohe_produces_expected_columns(self) -> None:
        X_out = self._fit()
        # sklearn 1.9 sorts categories alphabetically [H, L, M];
        # drop='first' drops H (reference). Remaining: Type_L, Type_M
        self.assertIn("Type_L", X_out.columns)
        self.assertIn("Type_M", X_out.columns)
        # Type_H must NOT be present (dropped as reference)
        self.assertNotIn("Type_H", X_out.columns)
        # Binary values only
        for col in ("Type_L", "Type_M"):
            unique = set(X_out[col].round(0).astype(int).unique())
            self.assertTrue(unique.issubset({0, 1}))

    # ------------------------------------------------------------------
    # Test 3 — Excluded columns do not appear in output
    # ------------------------------------------------------------------
    def test_excluded_columns_not_in_output(self) -> None:
        X_out = self._fit()
        for col in EXCLUDE_COLUMNS:
            self.assertNotIn(col, X_out.columns, f"{col} should be excluded")
        self.assertNotIn(TARGET_COLUMN, X_out.columns)

    # ------------------------------------------------------------------
    # Test 4 — transform() on test data does not re-fit
    # ------------------------------------------------------------------
    def test_transform_does_not_refit_on_test_data(self) -> None:
        self._fit()  # fit on train

        X_test, _ = self.service.split_features_target(self.df_test)

        # Apply twice — must produce identical results (no stochastic re-fit)
        out1 = self.service.transform(X_test)
        out2 = self.service.transform(X_test)
        pd.testing.assert_frame_equal(out1, out2)

        # Train mean must NOT equal test mean (scaler was fitted on train only)
        X_train, _ = self.service.split_features_target(self.df_train)
        out_train = self.service.transform(X_train)
        # Scaled train data should have mean ≈ 0; test data mean is arbitrary
        train_mean = out_train["Air temperature [K]"].mean()
        self.assertAlmostEqual(train_mean, 0.0, places=10)

    # ------------------------------------------------------------------
    # Test 5 — Saved and reloaded pipeline produces identical output
    # ------------------------------------------------------------------
    def test_save_load_pipeline_identical_output(self) -> None:
        X_out_before = self._fit()
        self.service.save(self.pipeline_path)

        # Load into a fresh service instance
        new_service = TransformationService()
        new_service.load(self.pipeline_path)

        X_in, _ = self.service.split_features_target(self.df_train)
        X_out_after = new_service.transform(X_in)

        pd.testing.assert_frame_equal(
            X_out_before.reset_index(drop=True),
            X_out_after.reset_index(drop=True),
        )

    # ------------------------------------------------------------------
    # Test 6 — transform() raises before fit_transform or load
    # ------------------------------------------------------------------
    def test_transform_raises_if_not_fitted(self) -> None:
        fresh = TransformationService()
        X, _ = fresh.split_features_target(self.df_train)
        with self.assertRaises(RuntimeError):
            fresh.transform(X)

    # ------------------------------------------------------------------
    # Test 7 — verify_output returns empty list on correct output
    # ------------------------------------------------------------------
    def test_verify_output_passes_on_correct_matrix(self) -> None:
        X_out = self._fit()
        missing = self.service.verify_output(X_out)
        self.assertEqual(missing, [], f"Missing columns: {missing}")

    # ------------------------------------------------------------------
    # Test 8 — StandardScaler gives zero mean on training data
    # ------------------------------------------------------------------
    def test_standard_scaler_zero_mean_on_train(self) -> None:
        X_out = self._fit()
        continuous_cols = [
            "Air temperature [K]",
            "Process temperature [K]",
            "Rotational speed [rpm]",
            "Torque [Nm]",
            "Tool wear [min]",
        ]
        for col in continuous_cols:
            mean = X_out[col].mean()
            self.assertAlmostEqual(
                mean, 0.0, places=10,
                msg=f"{col} mean after scaling should be 0, got {mean}"
            )


if __name__ == "__main__":
    unittest.main()
