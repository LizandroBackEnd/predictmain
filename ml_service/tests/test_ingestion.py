"""Unit tests for the dataset ingestion service."""

import tempfile
import unittest
from pathlib import Path

from src.ingestion.service import IngestionService


class TestIngestionService(unittest.TestCase):
    def setUp(self) -> None:
        self.service = IngestionService()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        # Create sample valid CSV
        self.valid_csv = self.temp_path / "sample.csv"
        self.valid_csv.write_text(
            "col1,col2,col3\n"
            "1,2,3\n"
            "4,5,6\n",
            encoding="utf-8",
        )
        self.manifest_path = self.temp_path / "manifest.json"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_inspect_csv_structure_success(self) -> None:
        n_rows, n_cols, cols = self.service.inspect_csv_structure(self.valid_csv)
        self.assertEqual(n_rows, 2)
        self.assertEqual(n_cols, 3)
        self.assertEqual(cols, ["col1", "col2", "col3"])

    def test_inspect_csv_structure_empty_fails(self) -> None:
        empty_csv = self.temp_path / "empty.csv"
        empty_csv.write_text("", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.service.inspect_csv_structure(empty_csv)

    def test_calculate_sha256(self) -> None:
        h1 = self.service.calculate_sha256(self.valid_csv)
        self.assertTrue(len(h1) == 64)
        # Re-computing should be completely identical
        h2 = self.service.calculate_sha256(self.valid_csv)
        self.assertEqual(h1, h2)

    def test_run_ingestion_idempotency(self) -> None:
        # First run creates manifest
        res1 = self.service.run_ingestion(self.valid_csv, self.manifest_path)
        self.assertTrue(res1.success)
        self.assertTrue(res1.is_new)
        self.assertTrue(self.manifest_path.exists())

        # Second run verifies matching hash without modification
        res2 = self.service.run_ingestion(self.valid_csv, self.manifest_path)
        self.assertTrue(res2.success)
        self.assertFalse(res2.is_new)
        self.assertEqual(res1.manifest.sha256, res2.manifest.sha256)

    def test_run_ingestion_fails_on_hash_mismatch(self) -> None:
        # Initial run
        self.service.run_ingestion(self.valid_csv, self.manifest_path)

        # Alter the CSV file
        self.valid_csv.write_text("col1,col2,col3\n99,99,99\n", encoding="utf-8")

        # Expect integrity violation
        with self.assertRaises(RuntimeError) as ctx:
            self.service.run_ingestion(self.valid_csv, self.manifest_path)
        self.assertIn("Integrity violation", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
