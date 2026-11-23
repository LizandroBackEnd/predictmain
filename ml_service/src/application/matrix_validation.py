"""HU-07 — Feature matrix validation use case."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from src.application.features import (
    EXCLUDE_COLUMNS,
    EXPECTED_FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from src.domain.models import MatrixValidationResult, ValidationCheck

LEAKAGE_COLUMNS: tuple[str, ...] = tuple(EXCLUDE_COLUMNS)


def validate_feature_matrix(
    X: pd.DataFrame,
    y: pd.Series | None = None,
    *,
    source_file: str = "",
) -> MatrixValidationResult:
    """Check the six HU-07 acceptance criteria on a feature matrix."""
    executed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    y_shape: tuple[int, ...] = () if y is None else (len(y),)

    columns_ok = list(X.columns) == EXPECTED_FEATURE_COLUMNS
    target_absent = TARGET_COLUMN not in X.columns
    target_aligned = y is None or (
        y.name == TARGET_COLUMN and len(y) == len(X)
    )
    null_count = int(X.isna().sum().sum())
    if y is not None:
        null_count += int(y.isna().sum())

    numeric_features = all(
        pd.api.types.is_numeric_dtype(dtype) for dtype in X.dtypes
    )
    numeric_target = y is None or pd.api.types.is_numeric_dtype(y.dtype)
    leaked = [column for column in LEAKAGE_COLUMNS if column in X.columns]
    dims_available = X.shape[0] > 0 and X.shape[1] > 0

    checks = [
        ValidationCheck(
            1,
            "La matriz contiene las variables documentadas",
            columns_ok,
            f"Esperadas {len(EXPECTED_FEATURE_COLUMNS)}; encontradas "
            f"{len(X.columns)}",
        ),
        ValidationCheck(
            2,
            "La variable objetivo está separada de las predictoras",
            target_absent and target_aligned,
            f"`{TARGET_COLUMN}` ausente en X; y={y_shape}",
        ),
        ValidationCheck(
            3,
            "No existen valores nulos inesperados",
            null_count == 0,
            f"{null_count} nulos en X e y",
        ),
        ValidationCheck(
            4,
            "Los tipos de datos son compatibles con el modelo",
            numeric_features and numeric_target,
            "Todas las predictoras y el objetivo son numéricos"
            if numeric_features and numeric_target
            else "Se detectaron columnas no numéricas",
        ),
        ValidationCheck(
            5,
            "No existe fuga de información (data leakage)",
            not leaked,
            "Sin identificadores, modos de falla ni objetivo en X"
            if not leaked
            else f"Columnas prohibidas en X: {leaked}",
        ),
        ValidationCheck(
            6,
            "Las dimensiones quedan registradas para el reporte",
            dims_available,
            f"X={X.shape}, y={y_shape}",
        ),
    ]

    return MatrixValidationResult(
        source_file=source_file,
        executed_at=executed_at,
        x_shape=X.shape,
        y_shape=y_shape,
        feature_columns=list(X.columns),
        target_column=TARGET_COLUMN,
        checks=checks,
    )
