"""Profiling service for statistical analysis and dataset profiling."""

from pathlib import Path
from typing import Dict

import pandas as pd

from src.domain.models import ColumnMetric, DatasetSummary
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
