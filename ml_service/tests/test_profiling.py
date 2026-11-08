"""Unit tests for the telemetry profiling service and report builder."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd
from src.profiling.service import ProfilingService


class TestProfilingService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = ProfilingService()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create realistic miniature DataFrame
        self.sample_data = {
            "UDI": [1, 2, 3, 4],
            "Product ID": ["L01", "M02", "H03", "L04"],
            "Type": ["L", "M", "H", "L"],
            "Air temperature [K]": [298.1, 298.2, 298.3, 298.4],
            "Process temperature [K]": [308.1, 308.2, 308.3, 308.4],
            "Rotational speed [rpm]": [1500, 1400, 1600, 1550],
            "Torque [Nm]": [40.0, 45.0, 38.0, 42.0],
            "Tool wear [min]": [10, 20, 30, 0],
            "Machine failure": [0, 1, 0, 0],
            "TWF": [0, 1, 0, 0],
            "HDF": [0, 0, 0, 0],
            "PWF": [0, 0, 0, 0],
            "OSF": [0, 0, 0, 0],
            "RNF": [0, 0, 0, 0],
        }
        self.df = pd.DataFrame(self.sample_data)
        self.csv_path = self.temp_path / "test_telemetry.csv"
        self.df.to_csv(self.csv_path, index=False)
        self.report_path = self.temp_path / "report.md"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_analyze_dataset(self) -> None:
        summary = self.service.analyze_dataset(self.df)
        self.assertEqual(summary.total_rows, 4)
        self.assertEqual(summary.total_columns, 14)

        # Check target distribution
        self.assertEqual(summary.target_distribution.get("0"), 3)
        self.assertEqual(summary.target_distribution.get("1"), 1)

        # Check failure mode
        self.assertEqual(summary.failure_modes_distribution.get("TWF"), 1)
        self.assertEqual(summary.failure_modes_distribution.get("HDF"), 0)

        # Verify numerical metric extraction
        air_metric = next(c for c in summary.columns if c.name == "Air temperature [K]")
        self.assertAlmostEqual(air_metric.min_value, 298.1)
        self.assertAlmostEqual(air_metric.max_value, 298.4)

    def test_run_profiling_generates_markdown_file(self) -> None:
        summary = self.service.run_profiling(self.csv_path, self.report_path)
        self.assertTrue(self.report_path.exists())

        content = self.report_path.read_text(encoding="utf-8")
        self.assertIn("Reporte de Perfilado de Telemetría Histórica", content)
        self.assertIn("Air temperature [K]", content)
        self.assertIn("Machine failure", content)
        self.assertEqual(summary.total_rows, 4)

    # ── Quality report tests ──────────────────────────────────────────────────

    def test_quality_report_no_duplicates(self) -> None:
        summary = self.service.analyze_dataset(self.df)
        self.assertIsNotNone(summary.quality_report)
        self.assertEqual(summary.quality_report.duplicate_rows, 0)

    def test_quality_report_detects_duplicates(self) -> None:
        df_with_dup = pd.concat([self.df, self.df.iloc[[0]]], ignore_index=True)
        summary = self.service.analyze_dataset(df_with_dup)
        self.assertEqual(summary.quality_report.duplicate_rows, 1)

    def test_quality_report_no_nulls(self) -> None:
        summary = self.service.analyze_dataset(self.df)
        self.assertEqual(summary.quality_report.null_counts, {})

    def test_quality_report_detects_nulls(self) -> None:
        import numpy as np
        df_with_null = self.df.copy()
        df_with_null.loc[0, "Air temperature [K]"] = np.nan
        summary = self.service.analyze_dataset(df_with_null)
        self.assertIn("Air temperature [K]", summary.quality_report.null_counts)
        self.assertEqual(summary.quality_report.null_counts["Air temperature [K]"], 1)

    def test_quality_report_detects_out_of_range(self) -> None:
        df_bad = self.df.copy()
        df_bad.loc[0, "Rotational speed [rpm]"] = 9999  # above UCI max of 2886
        summary = self.service.analyze_dataset(df_bad)
        self.assertIn("Rotational speed [rpm]", summary.quality_report.out_of_range)

    def test_quality_report_detects_invalid_type(self) -> None:
        df_bad = self.df.copy()
        df_bad.loc[0, "Type"] = "X"  # not in {L, M, H}
        summary = self.service.analyze_dataset(df_bad)
        self.assertIn("Type", summary.quality_report.invalid_type_values)

    def test_quality_section_appears_in_markdown(self) -> None:
        self.service.run_profiling(self.csv_path, self.report_path)
        content = self.report_path.read_text(encoding="utf-8")
        self.assertIn("Reporte de Calidad del Dataset", content)
        self.assertIn("Valores Nulos", content)
        self.assertIn("Fuera de Rango Físico", content)


if __name__ == "__main__":
    unittest.main()
