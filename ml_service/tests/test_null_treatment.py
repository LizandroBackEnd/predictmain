"""
HU-04 — Unit tests for the null treatment pipeline.

Tests cover:
  1. Pre-treatment null counts are captured correctly.
  2. Rows with missing labels (DROP_ROW columns) are removed.
  3. Feature columns with nulls are imputed with median / mode.
  4. Clean dataset contains zero unexpected nulls after treatment.
  5. Audit counters (imputed, dropped, before/after rows) are accurate.
  6. A dataset without any nulls passes through unchanged.
  7. NullTreatmentResult report is written and contains key sections.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.null_treatment.service import NullTreatmentService


def _make_clean_df() -> pd.DataFrame:
    """Minimal valid AI4I-shaped DataFrame with no nulls."""
    return pd.DataFrame({
        "UDI":                      [1, 2, 3, 4, 5],
        "Product ID":               ["L1", "M2", "H3", "L4", "M5"],
        "Type":                     ["L", "M", "H", "L", "M"],
        "Air temperature [K]":      [300.0, 300.1, 300.2, 300.3, 300.4],
        "Process temperature [K]":  [310.0, 310.1, 310.2, 310.3, 310.4],
        "Rotational speed [rpm]":   [1500, 1520, 1480, 1510, 1490],
        "Torque [Nm]":              [40.0, 41.0, 39.0, 42.0, 38.0],
        "Tool wear [min]":          [10, 20, 30, 40, 50],
        "Machine failure":          [0, 0, 1, 0, 0],
        "TWF":                      [0, 0, 1, 0, 0],
        "HDF":                      [0, 0, 0, 0, 0],
        "PWF":                      [0, 0, 0, 0, 0],
        "OSF":                      [0, 0, 0, 0, 0],
        "RNF":                      [0, 0, 0, 0, 0],
    })


class TestNullTreatmentService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = NullTreatmentService()
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _write_csv(self, df: pd.DataFrame, name: str = "input.csv") -> Path:
        path = self.tmp_path / name
        df.to_csv(path, index=False)
        return path

    def _run(self, df: pd.DataFrame):
        csv = self._write_csv(df)
        out_csv = self.tmp_path / "clean.csv"
        report = self.tmp_path / "null_report.md"
        result = self.service.run(csv, out_csv, report)
        return result, pd.read_csv(out_csv), report

    # ------------------------------------------------------------------
    # Test 1 — Pre-treatment null counts are captured
    # ------------------------------------------------------------------

    def test_null_counts_captured_before_treatment(self) -> None:
        df = _make_clean_df()
        df.loc[0, "Air temperature [K]"] = np.nan
        df.loc[1, "Torque [Nm]"] = np.nan

        result, _, _ = self._run(df)

        air_stat = next(s for s in result.column_stats if s.column == "Air temperature [K]")
        torque_stat = next(s for s in result.column_stats if s.column == "Torque [Nm]")

        self.assertEqual(air_stat.null_count_before, 1)
        self.assertEqual(torque_stat.null_count_before, 1)
        self.assertEqual(result.total_nulls_before, 2)
        self.assertEqual(result.rows_with_nulls_before, 2)

    # ------------------------------------------------------------------
    # Test 2 — Rows with null labels are dropped
    # ------------------------------------------------------------------

    def test_drop_row_on_null_label(self) -> None:
        df = _make_clean_df()
        df.loc[2, "Machine failure"] = np.nan  # row index 2 should be dropped

        result, df_clean, _ = self._run(df)

        self.assertEqual(result.rows_before, 5)
        self.assertEqual(result.rows_dropped, 1)
        self.assertEqual(result.rows_after, 4)
        self.assertFalse(df_clean["Machine failure"].isna().any())

    # ------------------------------------------------------------------
    # Test 3 — Feature columns are imputed with median
    # ------------------------------------------------------------------

    def test_median_imputation_for_continuous_column(self) -> None:
        df = _make_clean_df()
        # Remove row 0 → remaining values: [300.1, 300.2, 300.3, 300.4] → median = 300.25
        df.loc[0, "Air temperature [K]"] = np.nan

        result, df_clean, _ = self._run(df)

        air_stat = next(s for s in result.column_stats if s.column == "Air temperature [K]")
        self.assertEqual(air_stat.imputed_count, 1)
        self.assertAlmostEqual(df_clean.loc[0, "Air temperature [K]"], 300.25, places=4)
        self.assertFalse(df_clean["Air temperature [K]"].isna().any())

    # ------------------------------------------------------------------
    # Test 4 — Categorical column is imputed with mode
    # ------------------------------------------------------------------

    def test_mode_imputation_for_categorical_column(self) -> None:
        df = _make_clean_df()
        # Type distribution: L=2, M=2, H=1 → mode is L or M (first alphabetically by pandas)
        df.loc[4, "Type"] = np.nan

        result, df_clean, _ = self._run(df)

        type_stat = next(s for s in result.column_stats if s.column == "Type")
        self.assertEqual(type_stat.imputed_count, 1)
        self.assertFalse(df_clean["Type"].isna().any())
        self.assertIn(df_clean.loc[4, "Type"], {"L", "M", "H"})

    # ------------------------------------------------------------------
    # Test 5 — Audit counters are accurate
    # ------------------------------------------------------------------

    def test_audit_counters_with_mixed_issues(self) -> None:
        df = _make_clean_df()
        df.loc[0, "Torque [Nm]"] = np.nan       # → imputed
        df.loc[1, "Tool wear [min]"] = np.nan   # → imputed
        df.loc[4, "TWF"] = np.nan               # → row dropped

        result, _, _ = self._run(df)

        self.assertEqual(result.rows_before, 5)
        self.assertEqual(result.rows_dropped, 1)
        self.assertEqual(result.rows_after, 4)
        self.assertEqual(result.total_values_imputed, 2)

    # ------------------------------------------------------------------
    # Test 6 — Clean dataset passes through unchanged
    # ------------------------------------------------------------------

    def test_clean_dataset_passes_through_unchanged(self) -> None:
        df = _make_clean_df()
        result, df_clean, _ = self._run(df)

        self.assertEqual(result.rows_before, 5)
        self.assertEqual(result.rows_after, 5)
        self.assertEqual(result.rows_dropped, 0)
        self.assertEqual(result.total_nulls_before, 0)
        self.assertEqual(result.total_values_imputed, 0)
        self.assertEqual(len(df_clean), 5)

    # ------------------------------------------------------------------
    # Test 7 — Null report markdown is generated with required sections
    # ------------------------------------------------------------------

    def test_null_report_markdown_generated(self) -> None:
        df = _make_clean_df()
        df.loc[0, "Air temperature [K]"] = np.nan

        _, _, report_path = self._run(df)

        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")

        self.assertIn("Reporte de Tratamiento de Valores Nulos", content)
        self.assertIn("Resumen Ejecutivo", content)
        self.assertIn("Detalle por Columna", content)
        self.assertIn("Justificación Técnica", content)
        self.assertIn("Conclusión", content)

    # ------------------------------------------------------------------
    # Test 8 — verify_no_unexpected_nulls passes on clean output
    # ------------------------------------------------------------------

    def test_verify_no_unexpected_nulls_on_clean_output(self) -> None:
        df = _make_clean_df()
        df.loc[0, "Torque [Nm]"] = np.nan

        csv = self._write_csv(df)
        out_csv = self.tmp_path / "clean.csv"
        report = self.tmp_path / "null_report.md"
        self.service.run(csv, out_csv, report)

        remaining = self.service.verify_no_unexpected_nulls(out_csv)
        self.assertEqual(remaining, [], f"Unexpected nulls remain in: {remaining}")


if __name__ == "__main__":
    unittest.main()
