"""Profiling service for statistical analysis and dataset profiling."""

from pathlib import Path
from typing import Dict, List

import pandas as pd

from src.domain.models import ColumnMetric, DatasetSummary, QualityReport
from src.profiling.report_builder import build_markdown_report


class ProfilingService:
    """Computes dataset statistics and renders markdown documentation."""

    NUMERICAL_COLS = [
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
    ]

    FAILURE_MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]

    # Physical ranges from UCI AI4I 2020 specification
    UCI_RANGES: Dict[str, tuple[float, float]] = {
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
        - Null / missing values per column
        - Values outside the UCI physical range specification
        - Invalid values in categorical / binary columns
        """
        # 1. Duplicates (full-row)
        duplicate_rows = int(df.duplicated().sum())

        # 2. Nulls per column
        null_counts: Dict[str, int] = {
            col: int(df[col].isna().sum())
            for col in df.columns
            if df[col].isna().sum() > 0
        }

        # 3. Out-of-range values (indices, 0-based)
        out_of_range: Dict[str, List[int]] = {}
        for col, (low, high) in self.UCI_RANGES.items():
            if col in df.columns:
                mask = (df[col] < low) | (df[col] > high)
                bad_indices = df.index[mask].tolist()
                if bad_indices:
                    out_of_range[col] = bad_indices

        # 4. Invalid categorical / binary values
        invalid_type_values: Dict[str, int] = {}
        if "Type" in df.columns:
            bad = (~df["Type"].isin(self.VALID_TYPES)).sum()
            if bad > 0:
                invalid_type_values["Type"] = int(bad)

        for col in self.BINARY_COLS:
            if col in df.columns:
                bad = (~df[col].isin([0, 1])).sum()
                if bad > 0:
                    invalid_type_values[col] = int(bad)

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
            dtype_str = str(df[col].dtype)
            null_count = int(df[col].isna().sum())
            non_null_count = int(df[col].count())
            unique_count = int(df[col].nunique())

            metric = ColumnMetric(
                name=col,
                dtype=dtype_str,
                non_null_count=non_null_count,
                null_count=null_count,
                unique_count=unique_count,
            )

            # Numerical variables statistics
            if pd.api.types.is_numeric_dtype(df[col]) and col in self.NUMERICAL_COLS:
                metric.min_value = float(df[col].min())
                metric.max_value = float(df[col].max())
                metric.mean_value = float(df[col].mean())
                metric.median_value = float(df[col].median())
                metric.std_value = float(df[col].std())

            # Categorical distribution
            if df[col].dtype == "object" or col == "Type":
                metric.distribution = {
                    str(k): int(v) for k, v in df[col].value_counts().items()
                }

            column_metrics.append(metric)

        # Target distribution
        target_dist: Dict[str, int] = {}
        if "Machine failure" in df.columns:
            target_dist = {
                str(k): int(v) for k, v in df["Machine failure"].value_counts().items()
            }

        # Failure modes distribution
        modes_dist: Dict[str, int] = {}
        for mode in self.FAILURE_MODES:
            if mode in df.columns:
                modes_dist[mode] = int((df[mode] == 1).sum())

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

        report_content = build_markdown_report(summary, csv_path.name)
        output_report_path.parent.mkdir(parents=True, exist_ok=True)
        output_report_path.write_text(report_content, encoding="utf-8")

        return summary
