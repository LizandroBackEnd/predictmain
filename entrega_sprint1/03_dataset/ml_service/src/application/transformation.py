"""HU-06 — Transformation pipeline application service.

Builds and fits an sklearn Pipeline with ColumnTransformer:
  - Step 1: DerivedFeatureAdder (stateless)
  - Step 2: StandardScaler on continuous columns + OneHotEncoder(drop='first') on Type
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.application.features import (
    CATEGORICAL_COLUMNS,
    CONTINUOUS_COLUMNS,
    DERIVED_FEATURE_NAME,
    EXCLUDE_COLUMNS,
    EXPECTED_FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from src.domain.models import TransformationResult
from src.infrastructure.storage import load_pipeline, save_pipeline


class DerivedFeatureAdder:
    """Sklearn-compatible transformer that adds engineered columns before ColumnTransformer."""

    def fit(
        self,
        X: pd.DataFrame,
        y: pd.Series | np.ndarray | None = None,
    ) -> DerivedFeatureAdder:
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        X[DERIVED_FEATURE_NAME] = (
            X["Process temperature [K]"] - X["Air temperature [K]"]
        )
        return X

    def fit_transform(
        self,
        X: pd.DataFrame,
        y: pd.Series | np.ndarray | None = None,
    ) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

    def get_params(self, deep: bool = True) -> dict[str, object]:
        return {}

    def set_params(self, **params: object) -> DerivedFeatureAdder:
        return self


class TransformationService:
    """Builds, fits, applies, saves, and loads the feature transformation pipeline."""

    def __init__(self) -> None:
        self._pipeline: Pipeline | None = None

    @staticmethod
    def split_features_target(
        df: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """Separate feature DataFrame from target series, dropping excluded columns."""
        X = df.drop(columns=[c for c in EXCLUDE_COLUMNS if c in df.columns])
        y = df[TARGET_COLUMN] if TARGET_COLUMN in df.columns else pd.Series(dtype=int)
        return X, y

    def _build_pipeline(self) -> Pipeline:
        continuous_with_derived = CONTINUOUS_COLUMNS + [DERIVED_FEATURE_NAME]

        col_transformer = ColumnTransformer(
            transformers=[
                (
                    "scaler",
                    StandardScaler(),
                    continuous_with_derived,
                ),
                (
                    "ohe",
                    OneHotEncoder(
                        drop="first",
                        handle_unknown="ignore",
                        sparse_output=False,
                    ),
                    CATEGORICAL_COLUMNS,
                ),
            ],
            remainder="drop",
            verbose_feature_names_out=False,
        )

        return Pipeline(
            steps=[
                ("feature_adder", DerivedFeatureAdder()),
                ("col_transformer", col_transformer),
            ]
        )

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Fit the pipeline on X and return the transformed feature matrix."""
        self._pipeline = self._build_pipeline()
        X_after_add = self._pipeline.named_steps["feature_adder"].fit_transform(X)
        self._pipeline.named_steps["col_transformer"].fit(X_after_add)
        return self._apply_full_pipeline(X)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Apply the already-fitted pipeline to new data."""
        if self._pipeline is None:
            raise RuntimeError(
                "Pipeline is not fitted. Call fit_transform() or load() first."
            )
        return self._apply_full_pipeline(X)

    def _apply_full_pipeline(self, X: pd.DataFrame) -> pd.DataFrame:
        adder = self._pipeline.named_steps["feature_adder"]
        transformer = self._pipeline.named_steps["col_transformer"]

        X_with_derived = adder.transform(X)
        X_array = transformer.transform(X_with_derived)
        feature_names = self._get_feature_names()
        return pd.DataFrame(X_array, columns=feature_names, index=X.index)

    def _get_feature_names(self) -> list[str]:
        ct = self._pipeline.named_steps["col_transformer"]
        continuous_names = CONTINUOUS_COLUMNS + [DERIVED_FEATURE_NAME]
        ohe_names = list(
            ct.named_transformers_["ohe"].get_feature_names_out(CATEGORICAL_COLUMNS)
        )
        return continuous_names + ohe_names

    def save(self, path: Path) -> None:
        """Serialize the fitted pipeline to disk."""
        if self._pipeline is None:
            raise RuntimeError("Cannot save an unfitted pipeline.")
        save_pipeline(self._pipeline, path)

    def load(self, path: Path) -> None:
        """Deserialize a previously saved pipeline from disk."""
        self._pipeline = load_pipeline(path)

    def verify_output(self, X_transformed: pd.DataFrame) -> list[str]:
        """Return list of expected feature columns that are missing from output."""
        return [
            col for col in EXPECTED_FEATURE_COLUMNS
            if col not in X_transformed.columns
        ]

