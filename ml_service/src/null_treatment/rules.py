"""
HU-04 — Null treatment rules for the AI4I 2020 Predictive Maintenance Dataset.

Each column is assigned one of three dispositions:
  - KEEP      : column is an identifier or label; handled separately, never imputed.
  - IMPUTE    : missing values are filled using a statistically justified strategy.
  - DROP_ROW  : if a value is missing in this column the entire record is discarded
                because no imputation preserves physical meaning.

Imputation strategies
---------------------
  median      : robust against skewed distributions and outliers (used for
                continuous sensor variables).
  mode        : most frequent category (used for the product-type column).

Justification per column
------------------------
UDI               KEEP   — sequential identifier; not a model feature.
Product ID        KEEP   — composite identifier; not a model feature.
Type              IMPUTE (mode)  — categorical with 3 known classes (L/M/H);
                                   most-frequent imputation preserves the
                                   empirical class prior.
Air temp [K]      IMPUTE (median)— continuous sensor reading; median is robust
                                   to sensor spikes that may have caused the gap.
Process temp [K]  IMPUTE (median)— same rationale as air temperature.
RPM               IMPUTE (median)— continuous; median avoids inflating the mean
                                   when the motor was stopped (RPM=0 spike).
Torque [Nm]       IMPUTE (median)— continuous; median is preferred because the
                                   distribution has a long right tail.
Tool wear [min]   IMPUTE (median)— cumulative counter; median of surrounding
                                   values is the most conservative estimate.
Machine failure   DROP_ROW       — target label; a missing label makes the
                                   record useless for supervised learning.
TWF               DROP_ROW       — failure-mode label; same rationale.
HDF               DROP_ROW       — failure-mode label.
PWF               DROP_ROW       — failure-mode label.
OSF               DROP_ROW       — failure-mode label.
RNF               DROP_ROW       — failure-mode label.
"""

from dataclasses import dataclass
from typing import Literal

Disposition = Literal["KEEP", "IMPUTE", "DROP_ROW"]
Strategy = Literal["median", "mode", None]


@dataclass(frozen=True)
class ColumnRule:
    """Treatment rule for a single dataset column."""

    column: str
    disposition: Disposition
    strategy: Strategy
    justification: str


# Ordered to match the original CSV column order
COLUMN_RULES: list[ColumnRule] = [
    ColumnRule(
        column="UDI",
        disposition="KEEP",
        strategy=None,
        justification="Sequential identifier — not a model feature; never imputed.",
    ),
    ColumnRule(
        column="Product ID",
        disposition="KEEP",
        strategy=None,
        justification="Composite identifier — not a model feature; never imputed.",
    ),
    ColumnRule(
        column="Type",
        disposition="IMPUTE",
        strategy="mode",
        justification=(
            "Categorical variable with 3 known classes (L, M, H). "
            "Most-frequent (mode) imputation preserves the empirical class prior "
            "without introducing an artificial new category."
        ),
    ),
    ColumnRule(
        column="Air temperature [K]",
        disposition="IMPUTE",
        strategy="median",
        justification=(
            "Continuous sensor reading measured in Kelvin. "
            "Median is robust to transient sensor spikes that may have caused the gap "
            "and avoids inflating the mean under a slightly right-skewed distribution."
        ),
    ),
    ColumnRule(
        column="Process temperature [K]",
        disposition="IMPUTE",
        strategy="median",
        justification=(
            "Continuous process sensor. Same rationale as air temperature: "
            "median guards against outlier influence while preserving the central tendency."
        ),
    ),
    ColumnRule(
        column="Rotational speed [rpm]",
        disposition="IMPUTE",
        strategy="median",
        justification=(
            "Continuous motor speed variable. Median avoids inflating the estimate "
            "when the motor was at standstill (RPM ≈ 0) during the missing period."
        ),
    ),
    ColumnRule(
        column="Torque [Nm]",
        disposition="IMPUTE",
        strategy="median",
        justification=(
            "Continuous mechanical variable with a long right tail. "
            "Median is more representative of typical operating torque than the mean."
        ),
    ),
    ColumnRule(
        column="Tool wear [min]",
        disposition="IMPUTE",
        strategy="median",
        justification=(
            "Cumulative tool-use counter. Median of the distribution provides "
            "a conservative and physically plausible estimate for a missing cycle."
        ),
    ),
    ColumnRule(
        column="Machine failure",
        disposition="DROP_ROW",
        strategy=None,
        justification=(
            "Primary target label for supervised learning. "
            "A missing label makes the record untrainable and undefinable; "
            "the row must be discarded entirely."
        ),
    ),
    ColumnRule(
        column="TWF",
        disposition="DROP_ROW",
        strategy=None,
        justification="Failure-mode label — same rationale as Machine failure.",
    ),
    ColumnRule(
        column="HDF",
        disposition="DROP_ROW",
        strategy=None,
        justification="Failure-mode label — same rationale as Machine failure.",
    ),
    ColumnRule(
        column="PWF",
        disposition="DROP_ROW",
        strategy=None,
        justification="Failure-mode label — same rationale as Machine failure.",
    ),
    ColumnRule(
        column="OSF",
        disposition="DROP_ROW",
        strategy=None,
        justification="Failure-mode label — same rationale as Machine failure.",
    ),
    ColumnRule(
        column="RNF",
        disposition="DROP_ROW",
        strategy=None,
        justification="Failure-mode label — same rationale as Machine failure.",
    ),
]

# Fast lookup by column name
RULES_BY_COLUMN: dict[str, ColumnRule] = {r.column: r for r in COLUMN_RULES}
