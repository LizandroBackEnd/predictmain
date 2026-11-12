"""Outlier analysis use case: detection and rule-driven handling of sensor anomalies."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.domain.models import ColumnOutlierStat, OutlierAnalysisResult
from src.domain.outlier_rules import OUTLIER_RULES, RULES_BY_COLUMN, OutlierRule
from src.infrastructure.reporting import build_outlier_report


class OutlierAnalysisService:
    """Detects and handles outliers using documented domain rules."""

    def _analyze_column(
        self,
        series: pd.Series,
        rule: OutlierRule,
    ) -> tuple[ColumnOutlierStat, pd.Series]:
        """
        Run IQR + percentile detection and apply the rule decision.
        Returns the stat object and the (possibly modified) series.

        Percentile calculation uses numpy.percentile() with method='linear'
        (the default), consistent with the NumPy v2 specification:
        https://numpy.org/doc/stable/reference/generated/numpy.percentile.html

        np.percentile(a, q) accepts q in [0, 100], while pandas .quantile()
        accepts q in [0, 1].  Both are equivalent but we use np.percentile
        explicitly so the implementation is traceable to the referenced tool.
        """
        arr: np.ndarray = series.to_numpy(dtype=float)

        # Cerca IQR — Q1 = percentil 25, Q3 = percentil 75
        q1 = float(np.percentile(arr, 25, method="linear"))
        q3 = float(np.percentile(arr, 75, method="linear"))
        iqr = q3 - q1
        fence_low = q1 - rule.iqr_factor * iqr
        fence_high = q3 + rule.iqr_factor * iqr

        # Límites por percentiles — P1 y P99 (valores en [0, 100])
        p_low_q  = rule.percentile_low  * 100   # p. ej. 0.01 → 1
        p_high_q = rule.percentile_high * 100   # p. ej. 0.99 → 99
        p1  = float(np.percentile(arr, p_low_q,  method="linear"))
        p99 = float(np.percentile(arr, p_high_q, method="linear"))

        mask_iqr = (series < fence_low) | (series > fence_high)
        mask_pct = (series < p1) | (series > p99)
        mask_physical = (series < rule.uci_physical_min) | (series > rule.uci_physical_max)
        mask_detected = mask_iqr | mask_pct

        iqr_count = int(mask_iqr.sum())
        pct_count = int(mask_pct.sum())
        physical_count = int(mask_physical.sum())
        detected_count = int(mask_detected.sum())

        modified = 0
        excluded = 0
        result_series = series.copy()

        if rule.decision == "CAP":
            # Winsorizar: recortar a las cercas IQR
            result_series = result_series.clip(lower=fence_low, upper=fence_high)
            modified = detected_count

        elif rule.decision == "EXCLUDE":
            # Marcar filas para exclusión (se devuelven como NaN para que el llamador las elimine)
            result_series[mask_detected] = np.nan
            excluded = detected_count

        # KEEP: la serie no cambia
        stat = ColumnOutlierStat(
            column=rule.column,
            decision=rule.decision,
            outlier_type=rule.outlier_type,
            detection_method=rule.detection_method,
            q1=q1,
            q3=q3,
            iqr=iqr,
            iqr_fence_low=fence_low,
            iqr_fence_high=fence_high,
            iqr_outliers_count=iqr_count,
            p1=p1,
            p99=p99,
            percentile_outliers_count=pct_count,
            uci_physical_min=rule.uci_physical_min,
            uci_physical_max=rule.uci_physical_max,
            outside_physical_range=physical_count,
            records_detected=detected_count,
            records_modified=modified,
            records_excluded=excluded,
        )

        return stat, result_series

    def run(
        self,
        csv_path: Path,
        output_csv_path: Path,
        report_path: Path,
    ) -> OutlierAnalysisResult:
        """
        Execute the full outlier analysis pipeline:
          1. Load cleaned dataset.
          2. Analyze each sensor column per its documented rule.
          3. Apply decisions (KEEP / CAP / EXCLUDE).
          4. Write output dataset and audit report.
        """
        df = pd.read_csv(csv_path)
        rows_input = len(df)
        executed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        column_stats: list[ColumnOutlierStat] = []

        for rule in OUTLIER_RULES:
            if rule.column not in df.columns:
                continue
            stat, modified_series = self._analyze_column(df[rule.column], rule)
            df[rule.column] = modified_series
            column_stats.append(stat)

        # Eliminar filas donde la decisión EXCLUDE dejó NaN
        exclude_cols = [
            rule.column for rule in OUTLIER_RULES
            if rule.decision == "EXCLUDE" and rule.column in df.columns
        ]
        if exclude_cols:
            df = df.dropna(subset=exclude_cols).reset_index(drop=True)

        result = OutlierAnalysisResult(
            source_file=csv_path.name,
            executed_at=executed_at,
            rows_input=rows_input,
            rows_output=len(df),
            total_detected=sum(s.records_detected for s in column_stats),
            total_modified=sum(s.records_modified for s in column_stats),
            total_excluded=sum(s.records_excluded for s in column_stats),
            column_stats=column_stats,
        )

        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv_path, index=False)

        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(build_outlier_report(result), encoding="utf-8")

        return result

