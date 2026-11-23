"""HU-08 — Baseline failure-risk classifier training use case."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline

from src.application.dataset_split import split_dataset
from src.application.features import TARGET_COLUMN
from src.application.transformation import TransformationService
from src.domain.models import BaselineTrainingResult, ModelMetricRow
from src.infrastructure.reporting import build_model_baseline_report
from src.infrastructure.storage import save_estimator

HU08_TEST_SIZE = 0.25
HU08_RANDOM_STATE = 42


def select_baseline_model(metrics: list[ModelMetricRow]) -> str:
    """Select by F1, then recall; deterministic fallback prefers random_forest."""
    if not metrics:
        raise ValueError("Cannot select a model without metrics.")
    return max(
        metrics,
        key=lambda row: (row.f1, row.recall, row.name == "random_forest"),
    ).name


class BaselineTrainingService:
    """Train baseline classifiers with a leakage-free HU-06 transform fit."""

    def run(
        self,
        csv_path: Path,
        model_path: Path,
        report_path: Path,
    ) -> BaselineTrainingResult:
        """Execute split → transform → train → evaluate → persist → report."""
        if not csv_path.is_file():
            raise FileNotFoundError(f"Training CSV not found: {csv_path}")
        if csv_path.stat().st_size == 0:
            raise ValueError(f"Training CSV is empty: {csv_path}")

        df = pd.read_csv(csv_path)
        if TARGET_COLUMN not in df.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' is required.")

        split = split_dataset(
            df,
            test_size=HU08_TEST_SIZE,
            random_state=HU08_RANDOM_STATE,
        )
        X_train, y_train = TransformationService.split_features_target(split.train)
        X_test, y_test = TransformationService.split_features_target(split.test)
        if y_train.empty or y_test.empty:
            raise ValueError("Training and test partitions must include the target.")

        transformer = TransformationService()
        X_train_t = transformer.fit_transform(X_train)
        X_test_t = transformer.transform(X_test)
        # Fit classifiers on ndarray so the composite Pipeline (preprocess →
        # classifier) does not mix DataFrame feature names with array outputs.
        X_train_arr = X_train_t.to_numpy()
        X_test_arr = X_test_t.to_numpy()

        candidates: dict[str, object] = {
            "logistic_regression": LogisticRegression(
                class_weight="balanced",
                max_iter=1000,
            ),
            "random_forest": RandomForestClassifier(
                class_weight="balanced",
                n_estimators=300,
                random_state=HU08_RANDOM_STATE,
            ),
        }

        metrics: list[ModelMetricRow] = []
        fitted: dict[str, object] = {}
        for name, estimator in candidates.items():
            estimator.fit(X_train_arr, y_train)
            fitted[name] = estimator
            metrics.append(self._score(name, estimator, X_test_arr, y_test))

        selected = select_baseline_model(metrics)
        composite = Pipeline(
            steps=[
                ("preprocess", transformer.pipeline),
                ("classifier", fitted[selected]),
            ]
        )
        save_estimator(composite, model_path)

        executed_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        result = BaselineTrainingResult(
            source_file=csv_path.name,
            executed_at=executed_at,
            train_rows=split.train_rows,
            test_rows=split.test_rows,
            test_size=split.test_size,
            random_state=split.random_state,
            stratified=split.stratified,
            metrics=metrics,
            selected_model=selected,
            model_path=str(model_path),
            report_path=str(report_path),
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(build_model_baseline_report(result), encoding="utf-8")
        return result

    @staticmethod
    def _score(
        name: str,
        estimator: object,
        X_test: object,
        y_test: pd.Series,
    ) -> ModelMetricRow:
        y_pred = estimator.predict(X_test)
        if not hasattr(estimator, "predict_proba"):
            raise ValueError(f"Estimator '{name}' must expose predict_proba.")
        y_proba = estimator.predict_proba(X_test)[:, 1]
        if y_test.nunique() < 2:
            raise ValueError(
                "ROC-AUC requires both classes in the test set; "
                f"found {sorted(y_test.unique())}."
            )
        return ModelMetricRow(
            name=name,
            accuracy=float(accuracy_score(y_test, y_pred)),
            precision=float(precision_score(y_test, y_pred, zero_division=0)),
            recall=float(recall_score(y_test, y_pred, zero_division=0)),
            f1=float(f1_score(y_test, y_pred, zero_division=0)),
            roc_auc=float(roc_auc_score(y_test, y_proba)),
        )
