"""Ingestion use case and integrity validation services."""

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from src.domain.models import IngestionResult, ManifestData, ValidationResult


class IngestionService:
    """Manages the raw data intake, checksumming, and manifest generation."""

    SOURCE_URL = (
        "https://archive.ics.uci.edu/static/public/601/"
        "ai4i+2020+predictive+maintenance+dataset.zip"
    )
    EXPECTED_FILE_NAME = "ai4i2020.csv"
    EXPECTED_COLUMNS = 14

    @staticmethod
    def calculate_sha256(file_path: Path) -> str:
        """Compute SHA-256 hash across the raw bytes of a file."""
        hasher = hashlib.sha256()
        with file_path.open("rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def inspect_csv_structure(file_path: Path) -> tuple[int, int, list[str]]:
        """
        Inspect CSV row count, column count, and headers without loading entire data to RAM.
        """
        with file_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            try:
                headers = next(reader)
            except StopIteration as exc:
                raise ValueError("Dataset CSV file is empty.") from exc

            if not headers or any(h.strip() == "" for h in headers):
                raise ValueError("Dataset headers contain empty column names.")

            row_count = 0
            for line_idx, row in enumerate(reader, start=2):
                if len(row) != len(headers):
                    raise ValueError(
                        f"Inconsistent column count at row {line_idx}. "
                        f"Expected {len(headers)}, found {len(row)}."
                    )
                row_count += 1

        return row_count, len(headers), headers

    def validate_dataset(self, file_path: Path) -> ValidationResult:
        """Perform technical validation of file existence, structure, and hash."""
        if not file_path.exists():
            return ValidationResult(
                is_valid=False,
                n_rows=0,
                n_columns=0,
                columns=[],
                size_bytes=0,
                sha256="",
                error_message=f"File not found: {file_path}",
            )

        if file_path.stat().st_size == 0:
            return ValidationResult(
                is_valid=False,
                n_rows=0,
                n_columns=0,
                columns=[],
                size_bytes=0,
                sha256="",
                error_message="Dataset file is 0 bytes.",
            )

        try:
            n_rows, n_cols, columns = self.inspect_csv_structure(file_path)
            sha256 = self.calculate_sha256(file_path)
            size_bytes = file_path.stat().st_size
            return ValidationResult(
                is_valid=True,
                n_rows=n_rows,
                n_columns=n_cols,
                columns=columns,
                size_bytes=size_bytes,
                sha256=sha256,
            )
        except (OSError, ValueError) as exc:
            return ValidationResult(
                is_valid=False,
                n_rows=0,
                n_columns=0,
                columns=[],
                size_bytes=0,
                sha256="",
                error_message=str(exc),
            )

    def run_ingestion(self, csv_path: Path, manifest_path: Path) -> IngestionResult:
        """
        Execute ingestion idempotently: verifies integrity and creates/preserves manifest.
        """
        val = self.validate_dataset(csv_path)
        if not val.is_valid:
            raise RuntimeError(f"Dataset validation failed: {val.error_message}")

        # Check existing manifest for idempotency and integrity drift
        if manifest_path.exists():
            try:
                existing_data = json.loads(manifest_path.read_text(encoding="utf-8"))
                previous_hash = existing_data.get("sha256")
                if previous_hash != val.sha256:
                    raise RuntimeError(
                        f"Integrity violation: CSV hash ({val.sha256}) does not match "
                        f"manifest hash ({previous_hash}). Refusing to overwrite."
                    )

                manifest = ManifestData(**existing_data)
                return IngestionResult(
                    success=True,
                    is_new=False,
                    manifest=manifest,
                    message="Existing manifest verified and preserved. Hash matches.",
                )
            except json.JSONDecodeError as exc:
                raise ValueError(f"Existing manifest is malformed JSON: {manifest_path}") from exc

        # Create new manifest
        now_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        manifest = ManifestData(
            manifest_version="1.0",
            source_url=self.SOURCE_URL,
            file_name=csv_path.name,
            ingestion_date=now_utc,
            n_rows=val.n_rows,
            n_columns=val.n_columns,
            columns=val.columns,
            size_bytes=val.size_bytes,
            sha256=val.sha256,
        )

        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        return IngestionResult(
            success=True,
            is_new=True,
            manifest=manifest,
            message="New manifest created successfully.",
        )
