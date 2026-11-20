"""Null treatment use case: missing value imputation and row dropping pipeline."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.domain.models import ColumnNullStat, NullTreatmentResult
from src.domain.null_rules import RULES_BY_COLUMN, ColumnRule
from src.infrastructure.reporting import build_null_report


class NullTreatmentService:
    """Applies documented null-treatment rules to produce a clean dataset."""

    def _build_column_stats(
        self,
        df: pd.DataFrame,
        total_rows: int,
    ) -> dict[str, ColumnNullStat]:
        """Snapshot null counts per column before any treatment."""
        stats: dict[str, ColumnNullStat] = {}
        for col in df.columns:
            rule: ColumnRule | None = RULES_BY_COLUMN.get(col)
            null_count = int(df[col].isna().sum())
            stats[col] = ColumnNullStat(
                column=col,
                null_count_before=null_count,
                null_pct_before=round(null_count / total_rows * 100, 4) if total_rows else 0.0,
                disposition=rule.disposition if rule else "KEEP",
                strategy=rule.strategy if rule else None,
            )
        return stats

    def _apply_drop_rows(
        self,
        df: pd.DataFrame,
        stats: dict[str, ColumnNullStat],
    ) -> tuple[pd.DataFrame, int]:
        """
        Drop rows where a DROP_ROW column has a null value.
        Returns the cleaned DataFrame and total rows removed.
        """
        drop_cols = [
            col for col, rule in RULES_BY_COLUMN.items()
            if rule.disposition == "DROP_ROW" and col in df.columns
        ]
        mask_any_null = df[drop_cols].isna().any(axis=1)
        rows_dropped = int(mask_any_null.sum())

        for col in drop_cols:
            stats[col].dropped_rows = int(df[col].isna().sum())

        return df[~mask_any_null].copy(), rows_dropped

    def _apply_imputations(
        self,
        df: pd.DataFrame,
        stats: dict[str, ColumnNullStat],
    ) -> pd.DataFrame:
        """
        Fill missing values in IMPUTE columns using the documented strategy.
        Uses .loc for safe, copy-safe assignment to avoid SettingWithCopyWarning.
        """
        df = df.copy()
        for col, rule in RULES_BY_COLUMN.items():
            if rule.disposition != "IMPUTE" or col not in df.columns:
                continue

            null_mask = df[col].isna()
            null_count = int(null_mask.sum())
            if null_count == 0:
                continue

            if rule.strategy == "median":
                fill_value = df[col].median()
            elif rule.strategy == "mode":
                mode_series = df[col].mode()
                fill_value = mode_series.iloc[0] if not mode_series.empty else np.nan
            else:
                continue  # unknown strategy — skip

            df.loc[null_mask, col] = fill_value
            stats[col].imputed_count = null_count

        return df

    def run(
        self,
        csv_path: Path,
        output_csv_path: Path,
        report_path: Path,
    ) -> NullTreatmentResult:
        """
        Execute the full null-treatment pipeline:
          1. Load raw dataset.
          2. Snapshot null counts before treatment.
          3. Drop rows with missing labels (DROP_ROW columns).
          4. Impute missing sensor values (IMPUTE columns).
          5. Write cleaned dataset and audit report.
        """
        df = pd.read_csv(csv_path)
        total_rows = len(df)

        # 1. Snapshot before treatment
        stats = self._build_column_stats(df, total_rows)
        total_nulls_before = sum(s.null_count_before for s in stats.values())
        rows_with_nulls_before = int(df.isna().any(axis=1).sum())

        # 2. Drop rows with missing labels
        df, rows_dropped = self._apply_drop_rows(df, stats)

        # 3. Impute sensor columns
        df = self._apply_imputations(df, stats)

        total_imputed = sum(s.imputed_count for s in stats.values())

        # 4. Write cleaned dataset
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv_path, index=False)

        result = NullTreatmentResult(
            source_file=csv_path.name,
            output_file=output_csv_path.name,
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            rows_before=total_rows,
            rows_after=len(df),
            rows_dropped=rows_dropped,
            total_nulls_before=total_nulls_before,
            total_values_imputed=total_imputed,
            column_stats=list(stats.values()),
            rows_with_nulls_before=rows_with_nulls_before,
        )

        # 5. Write null report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(build_null_report(result), encoding="utf-8")

        return result

    def verify_no_unexpected_nulls(self, csv_path: Path) -> list[str]:
        """
        Post-treatment check: return list of model-required columns that
        still contain nulls. An empty list means the dataset is ready.
        """
        required_cols = [
            col for col, rule in RULES_BY_COLUMN.items()
            if rule.disposition in ("IMPUTE", "DROP_ROW")
        ]
        df = pd.read_csv(csv_path)
        return [
            col for col in required_cols
            if col in df.columns and df[col].isna().any()
        ]

