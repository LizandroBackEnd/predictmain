"""
HU-06 — Feature definitions and transformation rules.

Defines which columns are excluded, which are encoded, which are scaled,
and which derived features are created — all with technical justification.

Derived features
----------------
Temp_diff = Process temperature [K] - Air temperature [K]
    Justification: The UCI documentation states that Heat Dissipation Failure
    (HDF) occurs when this difference falls below 8.6 K combined with low RPM.
    Making the difference explicit as a feature gives the model a direct signal
    for that failure mode without relying on the model to learn the subtraction.

Encoding
--------
Type (categorical: L / M / H)
    Strategy: One-Hot Encoding via sklearn OneHotEncoder(drop='first',
    handle_unknown='ignore', sparse_output=False).
    Justification: OHE is the standard for nominal categories with no ordinal
    relationship. drop='first' removes one column to avoid multicollinearity
    (dummy variable trap). handle_unknown='ignore' ensures the pipeline does
    not raise errors on unseen categories at inference time.
    Result columns: Type_M, Type_H  (Type_L is the dropped reference).

Scaling
-------
Continuous sensor variables are standardized with StandardScaler
(zero mean, unit variance).
    Justification: Tree-based models are invariant to scale, but StandardScaler
    is applied here so the pipeline is compatible with future linear or distance-
    based models without modification.

Excluded columns (never enter the feature matrix)
--------------------------------------------------
UDI             — sequential identifier, no predictive signal.
Product ID      — composite identifier, no predictive signal.
TWF, HDF, PWF, OSF, RNF — failure-mode labels only known after a failure event;
                            using them as features would introduce data leakage.
Machine failure — target variable, never a feature.
"""

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# Column role constants
# ---------------------------------------------------------------------------

TARGET_COLUMN = "Machine failure"

EXCLUDE_COLUMNS: list[str] = [
    "UDI",
    "Product ID",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF",
    TARGET_COLUMN,
]

CATEGORICAL_COLUMNS: list[str] = ["Type"]

CONTINUOUS_COLUMNS: list[str] = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

# Derived feature specification
DERIVED_FEATURE_NAME = "Temp_diff"
DERIVED_FEATURE_FORMULA = "Process temperature [K] - Air temperature [K]"


@dataclass(frozen=True)
class DerivedFeature:
    """Specification of a single derived feature."""

    name: str
    formula: str
    justification: str


DERIVED_FEATURES: list[DerivedFeature] = [
    DerivedFeature(
        name=DERIVED_FEATURE_NAME,
        formula=DERIVED_FEATURE_FORMULA,
        justification=(
            "Direct signal for Heat Dissipation Failure (HDF): UCI spec states "
            "HDF occurs when Process_temp - Air_temp < 8.6 K at low RPM. "
            "Exposing this difference explicitly avoids the model having to "
            "implicitly learn the subtraction from correlated individual temperatures."
        ),
    ),
]

# Final feature columns after all transformations
# (used for validation after pipeline output)
# OHE with drop='first' sorts categories alphabetically [H, L, M]
# and drops 'H' (first). Resulting columns: Type_L, Type_M
EXPECTED_FEATURE_COLUMNS: list[str] = (
    CONTINUOUS_COLUMNS
    + [DERIVED_FEATURE_NAME]
    + ["Type_L", "Type_M"]          # OHE result with drop='first' (H is reference)
)
