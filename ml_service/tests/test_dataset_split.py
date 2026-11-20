"""HU-06 — Unit tests for reproducible dataset partitioning."""

import unittest

import numpy as np
import pandas as pd

from src.application.dataset_split import split_dataset
from src.application.features import TARGET_COLUMN


def _make_df(n: int = 200) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    return pd.DataFrame({
        "UDI": list(range(1, n + 1)),
        "sensor": rng.normal(size=n),
        TARGET_COLUMN: [0] * (n - 30) + [1] * 30,
    })


class TestDatasetSplit(unittest.TestCase):

    def test_split_is_80_20_and_reproducible(self) -> None:
        df = _make_df()
        first = split_dataset(df)
        second = split_dataset(df)

        self.assertEqual(first.train_rows, 160)
        self.assertEqual(first.test_rows, 40)
        self.assertEqual(first.random_state, 42)
        self.assertTrue(first.stratified)
        pd.testing.assert_frame_equal(first.train, second.train)
        pd.testing.assert_frame_equal(first.test, second.test)

    def test_split_is_stratified_and_disjoint(self) -> None:
        df = _make_df()
        split = split_dataset(df)

        self.assertEqual(
            set(split.train["UDI"]).intersection(split.test["UDI"]), set()
        )
        self.assertEqual(
            set(split.train["UDI"]) | set(split.test["UDI"]), set(df["UDI"])
        )
        train_rate = split.train[TARGET_COLUMN].mean()
        test_rate = split.test[TARGET_COLUMN].mean()
        self.assertAlmostEqual(train_rate, test_rate, places=10)

    def test_missing_target_raises(self) -> None:
        df = _make_df().drop(columns=[TARGET_COLUMN])
        with self.assertRaises(ValueError):
            split_dataset(df)

    def test_invalid_test_size_raises(self) -> None:
        with self.assertRaises(ValueError):
            split_dataset(_make_df(), test_size=0.0)

    def test_single_class_falls_back_to_random_split(self) -> None:
        df = _make_df()
        df[TARGET_COLUMN] = 0
        split = split_dataset(df)

        self.assertFalse(split.stratified)
        self.assertEqual(split.train_rows + split.test_rows, len(df))


if __name__ == "__main__":
    unittest.main()
