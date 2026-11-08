"""
HU-04 — Null treatment and missing value pipeline service.

Responsibilities
----------------
1. Count missing values per column and per row BEFORE any treatment (#25).
2. Apply the rules defined in rules.py to impute or drop records (#27).
3. Record how many values were imputed, rows dropped, and rows kept (#28).
4. Write the cleaned dataset to data/processed/ and the null report to reports/.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from src.null_treatment.rules import RULES_BY_COLUMN, ColumnRule


# ---------------------------------------------------------------------------
# Domain value objects
# ---------------------------------------------------------------------------

@dataclass
class ColumnNullStat:
    """Missing-value statistics for one column before treatment."""

    column: str
    null_count_before: int
    null_pct_before: float
    disposition: str
    strategy: str | None
    imputed_count: int = 0
    dropped_rows: int = 0


@dataclass
class NullTreatmentResult:
    """Full outcome of the null-treatment pipeline run."""

    source_file: str
    output_file: str
    executed_at: str
    rows_before: int
    rows_after: int
    rows_dropped: int
    total_nulls_before: int
    total_values_imputed: int
    column_stats: list[ColumnNullStat]
    rows_with_nulls_before: int  # records that had ≥1 null


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

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

        # Record how many rows each DROP_ROW column contributed
        for col in drop_cols:
            col_null_mask = df[col].isna()
            stats[col].dropped_rows = int(col_null_mask.sum())

        return df[~mask_any_null].copy(), rows_dropped

    def _apply_imputations(
        self,
        df: pd.DataFrame,
        stats: dict[str, ColumnNullStat],
    ) -> pd.DataFrame:
        """
        Fill missing values in IMPUTE columns using the documented strategy.
        Modifies df in-place and updates stats with imputed counts.
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
          3. Drop rows with nulls in label columns.
          4. Impute missing values in feature columns.
          5. Save clean dataset and null report.

        Returns a NullTreatmentResult with full audit counters.
        """
        if not csv_path.exists():
            raise FileNotFoundError(f"Source CSV not found: {csv_path}")

        df_raw = pd.read_csv(csv_path)
        rows_before = len(df_raw)
        rows_with_nulls_before = int(df_raw.isna().any(axis=1).sum())
        total_nulls_before = int(df_raw.isna().sum().sum())

        # 1. Build pre-treatment statistics
        stats = self._build_column_stats(df_raw, rows_before)

        # 2. Drop rows with missing labels first
        df_after_drop, rows_dropped = self._apply_drop_rows(df_raw, stats)

        # 3. Impute feature columns
        df_clean = self._apply_imputations(df_after_drop, stats)

        # 4. Persist clean dataset
        output_csv_path.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_csv(output_csv_path, index=False)

        total_imputed = sum(s.imputed_count for s in stats.values())

        result = NullTreatmentResult(
            source_file=csv_path.name,
            output_file=str(output_csv_path),
            executed_at=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            rows_before=rows_before,
            rows_after=len(df_clean),
            rows_dropped=rows_dropped,
            total_nulls_before=total_nulls_before,
            total_values_imputed=total_imputed,
            column_stats=list(stats.values()),
            rows_with_nulls_before=rows_with_nulls_before,
        )

        # 5. Write null report
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            build_null_report(result), encoding="utf-8"
        )

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


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join([":---"] * len(headers)) + " |"
    body = ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join([header, sep] + body)


def build_null_report(result: NullTreatmentResult) -> str:
    """Render the null treatment audit report as Markdown."""
    lines: list[str] = [
        "# Reporte de Tratamiento de Valores Nulos — HU-04",
        "",
        "> Generado automáticamente por el pipeline de tratamiento de PredictMain.",
        "",
        "---",
        "",
        "## 1. Resumen Ejecutivo",
        "",
        f"| Métrica | Valor |",
        f"| :--- | :--- |",
        f"| Archivo fuente | `{result.source_file}` |",
        f"| Archivo depurado | `{result.output_file}` |",
        f"| Fecha de ejecución | {result.executed_at} |",
        f"| Filas antes del tratamiento | {result.rows_before:,} |",
        f"| Filas con al menos un nulo | {result.rows_with_nulls_before:,} |",
        f"| Total de valores nulos encontrados | {result.total_nulls_before:,} |",
        f"| Filas eliminadas (labels nulos) | {result.rows_dropped:,} |",
        f"| Valores imputados | {result.total_values_imputed:,} |",
        f"| Filas en dataset depurado | {result.rows_after:,} |",
        "",
    ]

    # Status badge
    if result.total_nulls_before == 0:
        lines += [
            "> ✅ **El dataset no contenía valores nulos.** "
            "No se realizaron imputaciones ni eliminaciones.",
            "",
        ]
    else:
        lines += [
            f"> ⚠️ Se encontraron **{result.total_nulls_before:,} valores nulos** "
            f"en **{result.rows_with_nulls_before:,} registros**. "
            f"Se aplicaron las reglas documentadas.",
            "",
        ]

    # Per-column detail
    lines += [
        "## 2. Detalle por Columna — Antes y Después",
        "",
        _md_table(
            ["Columna", "Nulos antes", "% Nulos", "Decisión", "Estrategia", "Imputados", "Filas eliminadas"],
            [
                [
                    f"`{s.column}`",
                    str(s.null_count_before),
                    f"{s.null_pct_before:.2f}%",
                    s.disposition,
                    s.strategy or "—",
                    str(s.imputed_count),
                    str(s.dropped_rows),
                ]
                for s in result.column_stats
            ],
        ),
        "",
    ]

    # Rules justification table
    lines += [
        "## 3. Justificación Técnica de las Reglas",
        "",
        _md_table(
            ["Columna", "Decisión", "Justificación"],
            [
                [f"`{rule.column}`", rule.disposition, rule.justification]
                for rule in RULES_BY_COLUMN.values()
            ],
        ),
        "",
        "## 4. Conclusión",
        "",
        (
            f"El dataset depurado contiene **{result.rows_after:,} registros** "
            f"listos para la fase de transformación (HU-05). "
        ),
    ]

    if result.rows_dropped > 0:
        lines.append(
            f"Se eliminaron **{result.rows_dropped:,} filas** por tener etiquetas nulas "
            f"que no pueden ser imputadas sin introducir sesgo."
        )
    if result.total_values_imputed > 0:
        lines.append(
            f"Se imputaron **{result.total_values_imputed:,} valores** usando "
            f"mediana (variables continuas) y moda (variables categóricas)."
        )
    if result.total_nulls_before == 0:
        lines.append("No se requirió ninguna modificación: el dataset estaba completo.")

    lines += ["", "---", "", f"> **Reporte generado:** {result.executed_at}", ""]

    return "\n".join(lines)
