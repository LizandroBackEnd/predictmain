"""
HU-06 — Transformation pipeline service.

Responsibilities
----------------
#33 — Build sklearn Pipeline with ColumnTransformer:
       Step 1: add derived feature Temp_diff (FunctionTransformer)
       Step 2: StandardScaler on continuous columns
       Step 3: OneHotEncoder(drop='first') on categorical column Type
#34 — Serialize / deserialize the fitted pipeline with joblib.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.transformation.features import (
    CATEGORICAL_COLUMNS,
    CONTINUOUS_COLUMNS,
    DERIVED_FEATURE_NAME,
    EXCLUDE_COLUMNS,
    EXPECTED_FEATURE_COLUMNS,
    TARGET_COLUMN,
    DERIVED_FEATURES,
)


# ---------------------------------------------------------------------------
# Custom transformer — derived feature engineering
# ---------------------------------------------------------------------------

class DerivedFeatureAdder:
    """
    Sklearn-compatible transformer that adds engineered columns
    BEFORE the ColumnTransformer runs.

    fit()           : no-op (stateless transformation).
    transform(X)    : returns a copy of X with new columns appended.
    fit_transform() : calls fit then transform.

    Implements the estimator interface manually (no BaseEstimator inheritance)
    to avoid sklearn version coupling while remaining fully compatible with
    sklearn Pipeline as the first step.
    """

    def fit(self, X: pd.DataFrame, y=None) -> "DerivedFeatureAdder":
        return self  # stateless — nothing to learn

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        # Temp_diff = Process temperature [K] - Air temperature [K]
        X[DERIVED_FEATURE_NAME] = (
            X["Process temperature [K]"] - X["Air temperature [K]"]
        )
        return X

    def fit_transform(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        return self.fit(X, y).transform(X)

    def get_params(self, deep: bool = True) -> dict:
        return {}

    def set_params(self, **params) -> "DerivedFeatureAdder":
        return self


# ---------------------------------------------------------------------------
# Result value object
# ---------------------------------------------------------------------------

@dataclass
class TransformationResult:
    """Outcome of a pipeline fit_transform or transform call."""

    rows: int
    feature_columns: list[str]
    pipeline_path: str | None   # None if not saved yet


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------

class TransformationService:
    """
    Builds, fits, applies, saves, and loads the feature transformation pipeline.

    Usage
    -----
    Build and fit on training data only:
        service = TransformationService()
        X_train, y_train = service.split_features_target(df_train)
        X_transformed = service.fit_transform(X_train)
        service.save(paths.pipeline_path)

    Apply to new data (test or live):
        service = TransformationService()
        service.load(paths.pipeline_path)
        X_transformed = service.transform(df_new)
    """

    def __init__(self) -> None:
        self._pipeline: Pipeline | None = None

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    @staticmethod
    def split_features_target(
        df: pd.DataFrame,
    ) -> tuple[pd.DataFrame, pd.Series]:
        """
        Separate feature DataFrame from target series.
        Drops excluded columns (identifiers and failure-mode labels).
        """
        X = df.drop(columns=[c for c in EXCLUDE_COLUMNS if c in df.columns])
        y = df[TARGET_COLUMN] if TARGET_COLUMN in df.columns else pd.Series(dtype=int)
        return X, y

    # ------------------------------------------------------------------
    # Pipeline construction (internal)
    # ------------------------------------------------------------------

    def _build_pipeline(self) -> Pipeline:
        """
        Construct the transformation pipeline.

        Step 1 — DerivedFeatureAdder (stateless):
            Adds Temp_diff = Process_temp - Air_temp.

        Step 2 — ColumnTransformer (fitted on training data only):
            - StandardScaler  → continuous sensor columns + Temp_diff
            - OneHotEncoder   → Type  (drop='first' → columns: Type_M, Type_H)
        """
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
            remainder="drop",   # drops any column not listed above
            verbose_feature_names_out=False,
        )

        pipeline = Pipeline(
            steps=[
                ("feature_adder", DerivedFeatureAdder()),
                ("col_transformer", col_transformer),
            ]
        )
        return pipeline

    # ------------------------------------------------------------------
    # fit_transform  (#33 — fits ONLY on training data)
    # ------------------------------------------------------------------

    def fit_transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Fit the pipeline on X and return the transformed feature matrix.
        Must be called only with training data.
        """
        self._pipeline = self._build_pipeline()

        # Step 1 is stateless; Step 2 (ColumnTransformer) is fitted here
        X_after_add = self._pipeline.named_steps["feature_adder"].fit_transform(X)
        self._pipeline.named_steps["col_transformer"].fit(X_after_add)

        return self._apply_full_pipeline(X)

    # ------------------------------------------------------------------
    # transform  (#33 — applies without re-fitting)
    # ------------------------------------------------------------------

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Apply the already-fitted pipeline to new data (test or live).
        Raises RuntimeError if fit_transform or load has not been called first.
        """
        if self._pipeline is None:
            raise RuntimeError(
                "Pipeline is not fitted. Call fit_transform() or load() first."
            )
        return self._apply_full_pipeline(X)

    def _apply_full_pipeline(self, X: pd.DataFrame) -> pd.DataFrame:
        """Run feature_adder then col_transformer and return a named DataFrame."""
        adder = self._pipeline.named_steps["feature_adder"]
        transformer = self._pipeline.named_steps["col_transformer"]

        X_with_derived = adder.transform(X)
        X_array = transformer.transform(X_with_derived)

        # Reconstruct column names from the ColumnTransformer
        feature_names = self._get_feature_names()
        return pd.DataFrame(X_array, columns=feature_names, index=X.index)

    def _get_feature_names(self) -> list[str]:
        """Extract output column names from the fitted ColumnTransformer."""
        ct = self._pipeline.named_steps["col_transformer"]
        continuous_names = CONTINUOUS_COLUMNS + [DERIVED_FEATURE_NAME]
        ohe_names = list(
            ct.named_transformers_["ohe"].get_feature_names_out(CATEGORICAL_COLUMNS)
        )
        return continuous_names + ohe_names

    # ------------------------------------------------------------------
    # Save / Load  (#34)
    # ------------------------------------------------------------------

    def save(self, path: Path) -> None:
        """Serialize the fitted pipeline to disk using joblib."""
        if self._pipeline is None:
            raise RuntimeError("Cannot save an unfitted pipeline.")
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._pipeline, path)

    def load(self, path: Path) -> None:
        """Deserialize a previously saved pipeline from disk."""
        if not path.exists():
            raise FileNotFoundError(f"Pipeline artifact not found: {path}")
        self._pipeline = joblib.load(path)

    # ------------------------------------------------------------------
    # Post-transform validation
    # ------------------------------------------------------------------

    def verify_output(self, X_transformed: pd.DataFrame) -> list[str]:
        """
        Return list of expected feature columns that are missing from output.
        An empty list means the matrix is complete.
        """
        return [
            col for col in EXPECTED_FEATURE_COLUMNS
            if col not in X_transformed.columns
        ]
