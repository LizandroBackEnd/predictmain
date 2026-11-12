"""
HU-05 — Outlier analysis rules for the AI4I 2020 sensor variables.

Each sensor column gets an OutlierRule that defines:
  - detection_method : IQR (1.5×) and/or percentile (P1/P99)
  - decision         : KEEP | CAP | EXCLUDE
  - rationale        : domain-justified explanation

Decision taxonomy
-----------------
  KEEP    : value is physically valid even if statistically extreme.
            Example: RPM spike during startup, valid failure signal.
  CAP     : value is replaced with the fence boundary (Winsorization).
            Used when the extreme is likely a sensor artifact but the
            record is otherwise valid.
  EXCLUDE : row is dropped. Reserved for physically impossible readings
            (e.g. temperature below absolute zero).

Sensor physical limits (UCI AI4I 2020 spec)
-------------------------------------------
  Air temperature [K]      : [295.3,  304.5]
  Process temperature [K]  : [305.7,  313.8]
  Rotational speed [rpm]   : [1168,   2886]
  Torque [Nm]              : [3.8,    76.6]
  Tool wear [min]          : [0,      253]
"""

from dataclasses import dataclass
from typing import Literal

DetectionMethod = Literal["IQR", "PERCENTILE", "IQR+PERCENTILE"]
OutlierDecision = Literal["KEEP", "CAP", "EXCLUDE"]


@dataclass(frozen=True)
class OutlierRule:
    """Outlier handling specification for one sensor column."""

    column: str
    detection_method: DetectionMethod
    iqr_factor: float          # multiplicador de la cerca IQR (normalmente 1.5)
    percentile_low: float      # límite percentil inferior (p. ej. 0.01)
    percentile_high: float     # límite percentil superior (p. ej. 0.99)
    uci_physical_min: float    # mínimo absoluto según la especificación UCI
    uci_physical_max: float    # máximo absoluto según la especificación UCI
    decision: OutlierDecision
    outlier_type: str          # "measurement_error" | "valid_extreme" | "failure_signal"
    rationale: str


OUTLIER_RULES: list[OutlierRule] = [
    OutlierRule(
        column="Air temperature [K]",
        detection_method="IQR+PERCENTILE",
        iqr_factor=1.5,
        percentile_low=0.01,
        percentile_high=0.99,
        uci_physical_min=295.3,
        uci_physical_max=304.5,
        decision="KEEP",
        outlier_type="valid_extreme",
        rationale=(
            "Air temperature varies naturally with ambient plant conditions. "
            "IQR detects 0 outliers — the distribution is compact (σ≈2K). "
            "P1/P99 detects 162 values but all fall within the UCI physical range "
            "[295.3K–304.5K], confirming they are valid ambient readings, not sensor errors. "
            "Decision: KEEP — no transformation applied."
        ),
    ),
    OutlierRule(
        column="Process temperature [K]",
        detection_method="IQR+PERCENTILE",
        iqr_factor=1.5,
        percentile_low=0.01,
        percentile_high=0.99,
        uci_physical_min=305.7,
        uci_physical_max=313.8,
        decision="KEEP",
        outlier_type="valid_extreme",
        rationale=(
            "Process temperature reflects friction from the manufacturing process. "
            "IQR detects 0 outliers. P1/P99 flags 195 values, all within the UCI "
            "physical range [305.7K–313.8K]. These represent genuine high-friction "
            "operating cycles, not measurement artifacts. "
            "Decision: KEEP — values are physically meaningful."
        ),
    ),
    OutlierRule(
        column="Rotational speed [rpm]",
        detection_method="IQR+PERCENTILE",
        iqr_factor=1.5,
        percentile_low=0.01,
        percentile_high=0.99,
        uci_physical_min=1168.0,
        uci_physical_max=2886.0,
        decision="KEEP",
        outlier_type="failure_signal",
        rationale=(
            "IQR (fence: 1139–1895 rpm) flags 418 records above 1895 rpm. "
            "These high-speed readings correlate with power failure (PWF) events "
            "where the motor overrevs before shutdown. Eliminating them would "
            "remove critical failure-precursor signals. All values are within "
            "the UCI physical range [1168–2886 rpm]. "
            "Decision: KEEP — statistical outliers are domain-valid failure signals."
        ),
    ),
    OutlierRule(
        column="Torque [Nm]",
        detection_method="IQR+PERCENTILE",
        iqr_factor=1.5,
        percentile_low=0.01,
        percentile_high=0.99,
        uci_physical_min=3.8,
        uci_physical_max=76.6,
        decision="KEEP",
        outlier_type="failure_signal",
        rationale=(
            "IQR (fence: 12.8–67.2 Nm) flags 69 records. Low-torque extremes "
            "correspond to PWF (power failure) conditions; high-torque extremes "
            "correspond to OSF (overstrain failure) precursors. Both carry "
            "predictive value for the ML model. All values are within the UCI "
            "physical range [3.8–76.6 Nm]. "
            "Decision: KEEP — extremes represent genuine failure-mode signatures."
        ),
    ),
    OutlierRule(
        column="Tool wear [min]",
        detection_method="IQR+PERCENTILE",
        iqr_factor=1.5,
        percentile_low=0.01,
        percentile_high=0.99,
        uci_physical_min=0.0,
        uci_physical_max=253.0,
        decision="KEEP",
        outlier_type="valid_extreme",
        rationale=(
            "IQR fence is [-110.5, 325.5 min] — wider than the physical range, "
            "so IQR detects 0 outliers. P1/P99 flags 99 high-wear values (>230 min). "
            "High tool wear is physically expected before a TWF (tool wear failure) "
            "event and is the primary feature for that failure mode. All values are "
            "within UCI physical range [0–253 min]. "
            "Decision: KEEP — high wear is a direct failure-precursor feature."
        ),
    ),
]

RULES_BY_COLUMN: dict[str, OutlierRule] = {r.column: r for r in OUTLIER_RULES}

