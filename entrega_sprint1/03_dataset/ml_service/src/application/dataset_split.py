"""HU-06 — Reproducible stratified partitioning for transformation fitting."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.model_selection import train_test_split

from src.application.features import TARGET_COLUMN

DEFAULT_TEST_SIZE = 0.2
DEFAULT_RANDOM_STATE = 42


@dataclass(frozen=True)
class DatasetSplit:
    """Train/test partitions sharing the original rows without overlap."""

    train: pd.DataFrame
    test: pd.DataFrame
    test_size: float
    random_state: int
    stratified: bool

    @property
    def train_rows(self) -> int:
        return len(self.train)

    @property
    def test_rows(self) -> int:
        return len(self.test)


def split_dataset(
    df: pd.DataFrame,
    target_column: str = TARGET_COLUMN,
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> DatasetSplit:
    """Split a dataset into train/test, stratifying when the target allows it."""
    if target_column not in df.columns:
        raise ValueError(f"Target column '{target_column}' is required to split.")
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must be strictly between 0 and 1.")

    target = df[target_column]
    stratified = target.nunique() > 1 and target.value_counts().min() >= 2
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=random_state,
        stratify=target if stratified else None,
    )

    return DatasetSplit(
        train=train_df.reset_index(drop=True),
        test=test_df.reset_index(drop=True),
        test_size=test_size,
        random_state=random_state,
        stratified=stratified,
    )
