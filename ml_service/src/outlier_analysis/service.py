"""
HU-05 — Outlier detection and analysis service.

Responsibilities
----------------
1. Detect outliers per column using IQR (1.5×) and percentile (P1/P99) methods (#30).
2. Apply the documented decision rule (KEEP / CAP / EXCLUDE) without auto-removing (#30).
3. Generate a quantitative summary: detected, modified, excluded per column (#31).
4. Write the outlier report to reports/outlier_report.md (#31).
5. Outliers are NEVER eliminated automatically — each decision is rule-driven.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.outlier_analysis.rules import OUTLIER_RULES, RULES_BY_COLUMN, OutlierRule


# ---------------------------------------------------------------------------
# Domain value objects
# ---------------------------------------------------------------------------

@dataclass
class ColumnOutlierStat:
    """Outlier detection results for a single sensor column."""

    column: str
    decision: str
    outlier_type: str
    detection_method: str

    # IQR stats
    q1: float
    q3: float
    iqr: float
    iqr_fence_low: float
    iqr_fence_high: float
    iqr_outliers_count: int

    # Percentile stats
    p1: float
    p99: float
    percentile_outliers_count: int

    # UCI physical range
    uci_physical_min: float
    uci_physical_max: float
    outside_physical_range: int

    # Post-decision counts
    records_detected: int   # union of IQR + percentile outliers
    records_modified: int   # how many were CAP-ped
    records_excluded: int   # how many rows were dropped


@dataclass
class OutlierAnalysisResult:
    """Full outcome of the outlier analysis pipeline."""

    source_file: str
    executed_at: str
    rows_input: int
    rows_output: int
    total_detected: int
    total_modified: int
    total_excluded: int
    column_stats: list[ColumnOutlierStat]


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

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

        # IQR fence — Q1 = 25th percentile, Q3 = 75th percentile
        q1 = float(np.percentile(arr, 25, method="linear"))
        q3 = float(np.percentile(arr, 75, method="linear"))
        iqr = q3 - q1
        fence_low = q1 - rule.iqr_factor * iqr
        fence_high = q3 + rule.iqr_factor * iqr

        # Percentile bounds — P1 and P99 (values in [0, 100])
        p_low_q  = rule.percentile_low  * 100   # e.g. 0.01 → 1
        p_high_q = rule.percentile_high * 100   # e.g. 0.99 → 99
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
            # Winsorize: clip to IQR fences
            result_series = result_series.clip(lower=fence_low, upper=fence_high)
            modified = detected_count

        elif rule.decision == "EXCLUDE":
            # Mark rows for exclusion (returned as NaN so caller can drop)
            result_series[mask_detected] = np.nan
            excluded = detected_count

        # KEEP: series is unchanged
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
          1. Load clean dataset from data/processed/.
          2. Detect outliers per column (IQR + percentile).
          3. Apply documented rule decision (KEEP / CAP / EXCLUDE).
          4. Save output dataset and generate markdown report.
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"Input CSV not found: {csv_path}")

        df = pd.read_csv(csv_path)
        rows_input = len(df)
        column_stats: list[ColumnOutlierStat] = []

        for rule in OUTLIER_RULES:
            if rule.column not in df.columns:
                continue
            stat, modified_series = self._analyze_column(df[rule.column], rule)
            df[rule.column] = modified_series
            column_stats.append(stat)

        # Drop rows marked for EXCLUDE (where series was set to NaN)
        exclude_cols = [
            r.column for r in OUTLIER_RULES if r.decision == "EXCLUDE"
        ]
        if exclude_cols:
            df = df.dropna(subset=[c for c in exclude_cols if c in df.columns])

        rows_output = len(df)

        result = OutlierAnalysisResult(
            source_file=csv_path.name,
            executed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            rows_input=rows_input,
            rows_output=rows_output,
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


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join([":---"] * len(headers)) + " |"
    body = ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join([header, sep] + body)


def build_outlier_report(result: OutlierAnalysisResult) -> str:
    """Render the outlier analysis audit report as Markdown."""
    lines: list[str] = [
        "# Reporte de Análisis de Valores Atípicos — HU-05",
        "",
        "> Generado automáticamente por el pipeline de análisis de PredictMain.",
        "",
        "---",
        "",
        "## 1. Resumen Ejecutivo",
        "",
        "| Métrica | Valor |",
        "| :--- | :--- |",
        f"| Archivo analizado | `{result.source_file}` |",
        f"| Fecha de ejecución | {result.executed_at} |",
        f"| Registros de entrada | {result.rows_input:,} |",
        f"| Registros de salida | {result.rows_output:,} |",
        f"| Total outliers detectados (unión IQR+P1/P99) | {result.total_detected:,} |",
        f"| Total valores modificados (CAP) | {result.total_modified:,} |",
        f"| Total filas excluidas | {result.total_excluded:,} |",
        "",
        "> **Principio:** Los outliers NO se eliminan automáticamente. "
        "Cada decisión está justificada con criterios del dominio físico.",
        "",
        "---",
        "",
        "## 2. Detección por Columna — IQR y Percentiles",
        "",
        _md_table(
            ["Variable", "Q1", "Q3", "IQR", "Fence Low", "Fence High",
             "IQR outliers", "P1", "P99", "P1/P99 outliers", "Fuera rango UCI"],
            [
                [
                    f"`{s.column}`",
                    f"{s.q1:.2f}", f"{s.q3:.2f}", f"{s.iqr:.2f}",
                    f"{s.iqr_fence_low:.2f}", f"{s.iqr_fence_high:.2f}",
                    str(s.iqr_outliers_count),
                    f"{s.p1:.2f}", f"{s.p99:.2f}",
                    str(s.percentile_outliers_count),
                    str(s.outside_physical_range),
                ]
                for s in result.column_stats
            ],
        ),
        "",
        "---",
        "",
        "## 3. Decisión por Variable — Regla → Decisión → Conteos",
        "",
        _md_table(
            ["Variable", "Tipo de atípico", "Detección", "Decisión",
             "Detectados", "Modificados", "Excluidos"],
            [
                [
                    f"`{s.column}`",
                    s.outlier_type,
                    s.detection_method,
                    f"**{s.decision}**",
                    str(s.records_detected),
                    str(s.records_modified),
                    str(s.records_excluded),
                ]
                for s in result.column_stats
            ],
        ),
        "",
        "---",
        "",
        "## 4. Justificación Técnica por Variable",
        "",
    ]

    for rule in OUTLIER_RULES:
        lines += [
            f"### `{rule.column}`",
            "",
            f"- **Decisión:** {rule.decision}",
            f"- **Tipo:** {rule.outlier_type}",
            f"- **Rango físico UCI:** [{rule.uci_physical_min}, {rule.uci_physical_max}]",
            f"- **Justificación:** {rule.rationale}",
            "",
        ]

    lines += [
        "---",
        "",
        "## 5. Conclusión",
        "",
        f"Se analizaron **{len(result.column_stats)} variables** de sensores. "
        f"Se detectaron **{result.total_detected:,} valores atípicos** en total "
        f"(unión de IQR 1.5× y percentiles P1/P99). ",
    ]

    if result.total_modified > 0:
        lines.append(
            f"Se aplicó Winsorización (CAP) a **{result.total_modified:,} valores**."
        )
    if result.total_excluded > 0:
        lines.append(
            f"Se excluyeron **{result.total_excluded:,} filas** por valores físicamente imposibles."
        )
    if result.total_modified == 0 and result.total_excluded == 0:
        lines.append(
            "**Todos los outliers fueron conservados (KEEP):** representan señales "
            "físicas válidas o precursores de falla con valor predictivo para el modelo."
        )

    lines += ["", "---", "", f"> **Reporte generado:** {result.executed_at}", ""]
    return "\n".join(lines)
