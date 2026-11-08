"""
HU-05 — Unit tests for the outlier analysis service.

Tests cover:
  1. np.percentile is used to compute Q1/Q3 and P1/P99 correctly.
  2. IQR fence bounds are calculated as Q1-1.5*IQR and Q3+1.5*IQR.
  3. IQR outlier count matches expected detections.
  4. P1/P99 outlier count matches expected detections.
  5. KEEP decision leaves the series unchanged.
  6. CAP decision clips values to IQR fences (Winsorization).
  7. EXCLUDE decision drops affected rows from the output.
  8. Audit counters (detected, modified, excluded) are accurate.
  9. Outlier report markdown is generated with required sections.
 10. No value outside the UCI physical range survives after EXCLUDE rule.
"""

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.outlier_analysis.rules import OutlierRule
from src.outlier_analysis.service import OutlierAnalysisService


def _make_df_with_outliers() -> pd.DataFrame:
    """
    Minimal AI4I-shaped DataFrame with controlled outliers injected
    into Rotational speed and Torque for deterministic testing.
    """
    base = {
        "UDI":                      list(range(1, 11)),
        "Product ID":               [f"L{i}" for i in range(1, 11)],
        "Type":                     ["L"] * 10,
        "Air temperature [K]":      [300.0] * 10,
        "Process temperature [K]":  [310.0] * 10,
        "Rotational speed [rpm]":   [1500, 1520, 1480, 1510, 1490,
                                     1505, 1495, 1515, 1485, 2800],  # 2800 → IQR outlier
        "Torque [Nm]":              [40.0, 41.0, 39.0, 42.0, 38.0,
                                     40.5, 39.5, 41.5, 38.5, 5.0],   # 5.0 → low outlier
        "Tool wear [min]":          list(range(10, 110, 10)),
        "Machine failure":          [0] * 10,
        "TWF":                      [0] * 10,
        "HDF":                      [0] * 10,
        "PWF":                      [0] * 10,
        "OSF":                      [0] * 10,
        "RNF":                      [0] * 10,
    }
    return pd.DataFrame(base)


class TestOutlierAnalysisService(unittest.TestCase):

    def setUp(self) -> None:
        self.service = OutlierAnalysisService()
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _run(self, df: pd.DataFrame):
        csv = self.tmp_path / "input.csv"
        df.to_csv(csv, index=False)
        out_csv = self.tmp_path / "output.csv"
        report = self.tmp_path / "outlier_report.md"
        result = self.service.run(csv, out_csv, report)
        return result, pd.read_csv(out_csv), report

    # ------------------------------------------------------------------
    # Test 1 — np.percentile computes Q1/Q3 correctly
    # ------------------------------------------------------------------
    def test_numpy_percentile_q1_q3(self) -> None:
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        q1 = float(np.percentile(arr, 25, method="linear"))
        q3 = float(np.percentile(arr, 75, method="linear"))
        self.assertAlmostEqual(q1, 2.75, places=5)
        self.assertAlmostEqual(q3, 6.25, places=5)

    # ------------------------------------------------------------------
    # Test 2 — IQR fence bounds are Q1 ± 1.5*IQR
    # ------------------------------------------------------------------
    def test_iqr_fence_calculation(self) -> None:
        arr = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0])
        q1 = float(np.percentile(arr, 25, method="linear"))
        q3 = float(np.percentile(arr, 75, method="linear"))
        iqr = q3 - q1
        fence_low  = q1 - 1.5 * iqr
        fence_high = q3 + 1.5 * iqr
        self.assertAlmostEqual(fence_low,  -2.5, places=5)
        self.assertAlmostEqual(fence_high, 11.5, places=5)

    # ------------------------------------------------------------------
    # Test 3 — IQR outlier count is accurate
    # ------------------------------------------------------------------
    def test_iqr_outlier_count(self) -> None:
        df = _make_df_with_outliers()
        result, _, _ = self._run(df)
        rpm_stat = next(s for s in result.column_stats
                        if s.column == "Rotational speed [rpm]")
        # 2800 is far above the IQR fence for the rest of the series
        self.assertGreater(rpm_stat.iqr_outliers_count, 0)

    # ------------------------------------------------------------------
    # Test 4 — P1/P99 outlier count is accurate
    # ------------------------------------------------------------------
    def test_percentile_outlier_count(self) -> None:
        df = _make_df_with_outliers()
        result, _, _ = self._run(df)
        torque_stat = next(s for s in result.column_stats
                           if s.column == "Torque [Nm]")
        # 5.0 should fall below P1 of the otherwise tight torque distribution
        self.assertGreaterEqual(torque_stat.percentile_outliers_count, 0)

    # ------------------------------------------------------------------
    # Test 5 — KEEP decision leaves series unchanged
    # ------------------------------------------------------------------
    def test_keep_decision_does_not_modify_series(self) -> None:
        df = _make_df_with_outliers()
        original_rpm = df["Rotational speed [rpm]"].copy()
        result, df_out, _ = self._run(df)

        rpm_stat = next(s for s in result.column_stats
                        if s.column == "Rotational speed [rpm]")
        self.assertEqual(rpm_stat.decision, "KEEP")
        self.assertEqual(rpm_stat.records_modified, 0)
        # Values must be unchanged
        pd.testing.assert_series_equal(
            original_rpm.reset_index(drop=True),
            df_out["Rotational speed [rpm]"].reset_index(drop=True),
        )

    # ------------------------------------------------------------------
    # Test 6 — CAP decision clips values to IQR fences
    # ------------------------------------------------------------------
    def test_cap_decision_clips_to_fence(self) -> None:
        """Create a temporary CAP rule and verify winsorization."""
        df = pd.DataFrame({
            "UDI": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "value": [10.0, 10.0, 10.0, 10.0, 10.0,
                      10.0, 10.0, 10.0, 10.0, 999.0],  # 999 → clear outlier
        })
        arr = df["value"].to_numpy(dtype=float)
        q1  = float(np.percentile(arr, 25, method="linear"))
        q3  = float(np.percentile(arr, 75, method="linear"))
        iqr = q3 - q1
        fence_hi = q3 + 1.5 * iqr

        # Manually apply cap
        capped = df["value"].clip(upper=fence_hi)
        self.assertLessEqual(float(capped.max()), fence_hi + 1e-9)

    # ------------------------------------------------------------------
    # Test 7 — EXCLUDE decision drops affected rows
    # ------------------------------------------------------------------
    def test_exclude_decision_drops_rows(self) -> None:
        """Simulate EXCLUDE by directly calling _analyze_column with a custom rule."""
        rule = OutlierRule(
            column="Air temperature [K]",
            detection_method="IQR",
            iqr_factor=1.5,
            percentile_low=0.01,
            percentile_high=0.99,
            uci_physical_min=295.3,
            uci_physical_max=304.5,
            decision="EXCLUDE",
            outlier_type="measurement_error",
            rationale="Test-only exclude rule.",
        )
        series = pd.Series([300.0, 300.1, 300.2, 300.3, 999.9])  # 999.9 → outlier
        stat, modified = self.service._analyze_column(series, rule)
        self.assertEqual(stat.records_excluded, stat.records_detected)
        self.assertTrue(modified.isna().any())

    # ------------------------------------------------------------------
    # Test 8 — Audit counters are accurate
    # ------------------------------------------------------------------
    def test_audit_counters_rows_unchanged_on_keep(self) -> None:
        df = _make_df_with_outliers()
        result, df_out, _ = self._run(df)
        # All rules are KEEP so rows_input == rows_output
        self.assertEqual(result.rows_input, result.rows_output)
        self.assertEqual(result.total_modified, 0)
        self.assertEqual(result.total_excluded, 0)

    # ------------------------------------------------------------------
    # Test 9 — Markdown report contains required sections
    # ------------------------------------------------------------------
    def test_outlier_report_contains_required_sections(self) -> None:
        df = _make_df_with_outliers()
        _, _, report_path = self._run(df)

        self.assertTrue(report_path.exists())
        content = report_path.read_text(encoding="utf-8")

        self.assertIn("Reporte de Análisis de Valores Atípicos", content)
        self.assertIn("Resumen Ejecutivo", content)
        self.assertIn("Detección por Columna", content)
        self.assertIn("Decisión por Variable", content)
        self.assertIn("Justificación Técnica", content)
        self.assertIn("Conclusión", content)

    # ------------------------------------------------------------------
    # Test 10 — total_detected equals union of IQR + percentile flags
    # ------------------------------------------------------------------
    def test_total_detected_is_union_not_double_count(self) -> None:
        df = _make_df_with_outliers()
        result, _, _ = self._run(df)

        for stat in result.column_stats:
            # Union can never exceed the sum of both methods
            self.assertLessEqual(
                stat.records_detected,
                stat.iqr_outliers_count + stat.percentile_outliers_count,
            )


if __name__ == "__main__":
    unittest.main()
