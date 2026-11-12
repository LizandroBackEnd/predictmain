"""Profiling use case: statistical analysis and dataset quality reporting."""

from pathlib import Path

import pandas as pd

from src.domain.models import ColumnMetric, DatasetSummary, QualityReport
from src.infrastructure.reporting import build_profiling_report


class ProfilingService:
    """Computes dataset statistics and renders Markdown documentation."""

    NUMERICAL_COLS = [
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
    ]

    FAILURE_MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]

    # Rangos físicos según la especificación UCI AI4I 2020
    UCI_RANGES: dict[str, tuple[float, float]] = {
        "Air temperature [K]":      (295.3,  304.5),
        "Process temperature [K]":  (305.7,  313.8),
        "Rotational speed [rpm]":   (1168.0, 2886.0),
        "Torque [Nm]":              (3.8,    76.6),
        "Tool wear [min]":          (0.0,    253.0),
    }

    VALID_TYPES = {"L", "M", "H"}
    BINARY_COLS = ["Machine failure", "TWF", "HDF", "PWF", "OSF", "RNF"]

    def _check_quality(self, df: pd.DataFrame) -> QualityReport:
        """
        Detect data quality issues:
        - Duplicate rows
        - Null / missing values per column (single-pass vectorized)
        - Values outside the UCI physical range specification
        - Invalid values in categorical / binary columns
        """
        # 1. Duplicados (fila completa)
        duplicate_rows = int(df.duplicated().sum())

        # 2. Nulos por columna — una sola pasada, sin doble evaluación
        null_series = df.isna().sum()
        null_counts: dict[str, int] = {
            col: int(cnt) for col, cnt in null_series.items() if cnt > 0
        }

        # 3. Valores fuera de rango (índices basados en 0)
        out_of_range: dict[str, list[int]] = {}
        for col, (low, high) in self.UCI_RANGES.items():
            if col in df.columns:
                mask = (df[col] < low) | (df[col] > high)
                bad_indices = df.index[mask].tolist()
                if bad_indices:
                    out_of_range[col] = bad_indices

        # 4. Valores inválidos en columnas categóricas / binarias
        invalid_type_values: dict[str, int] = {}
        if "Type" in df.columns:
            bad = int((~df["Type"].isin(self.VALID_TYPES)).sum())
            if bad > 0:
                invalid_type_values["Type"] = bad

        for col in self.BINARY_COLS:
            if col in df.columns:
                bad = int((~df[col].isin([0, 1])).sum())
                if bad > 0:
                    invalid_type_values[col] = bad

        total_issues = (
            duplicate_rows
            + sum(null_counts.values())
            + sum(len(v) for v in out_of_range.values())
            + sum(invalid_type_values.values())
        )

        return QualityReport(
            duplicate_rows=duplicate_rows,
            null_counts=null_counts,
            out_of_range=out_of_range,
            invalid_type_values=invalid_type_values,
            total_issues=total_issues,
        )

    def analyze_dataset(self, df: pd.DataFrame) -> DatasetSummary:
        """Compute statistical summary across all columns."""
        column_metrics: list[ColumnMetric] = []

        for col in df.columns:
            null_count = int(df[col].isna().sum())
            metric = ColumnMetric(
                name=col,
                dtype=str(df[col].dtype),
                non_null_count=int(df[col].count()),
                null_count=null_count,
                unique_count=int(df[col].nunique()),
            )

            if pd.api.types.is_numeric_dtype(df[col]) and col in self.NUMERICAL_COLS:
                metric.min_value = float(df[col].min())
                metric.max_value = float(df[col].max())
                metric.mean_value = float(df[col].mean())
                metric.median_value = float(df[col].median())
                metric.std_value = float(df[col].std())

            if df[col].dtype == "object" or col == "Type":
                metric.distribution = {
                    str(k): int(v) for k, v in df[col].value_counts().items()
                }

            column_metrics.append(metric)

        target_dist: dict[str, int] = {}
        if "Machine failure" in df.columns:
            target_dist = {
                str(k): int(v) for k, v in df["Machine failure"].value_counts().items()
            }

        modes_dist: dict[str, int] = {
            mode: int((df[mode] == 1).sum())
            for mode in self.FAILURE_MODES
            if mode in df.columns
        }

        return DatasetSummary(
            total_rows=len(df),
            total_columns=len(df.columns),
            columns=column_metrics,
            target_distribution=target_dist,
            failure_modes_distribution=modes_dist,
            quality_report=self._check_quality(df),
        )

    def run_profiling(self, csv_path: Path, output_report_path: Path) -> DatasetSummary:
        """Load dataset, generate summary, and persist Markdown report."""
        if not csv_path.exists():
            raise FileNotFoundError(f"Cannot profile missing dataset at: {csv_path}")

        df = pd.read_csv(csv_path)
        summary = self.analyze_dataset(df)

        report_content = build_profiling_report(summary, csv_path.name)
        output_report_path.parent.mkdir(parents=True, exist_ok=True)
        output_report_path.write_text(report_content, encoding="utf-8")

        return summary

