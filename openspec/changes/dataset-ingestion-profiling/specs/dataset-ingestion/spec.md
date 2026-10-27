# Dataset Ingestion Specification

## Purpose

Defines the requirements and operational contracts for validating, importing, and tracking the immutable raw AI4I 2020 Predictive Maintenance Dataset (`data/raw/ai4i2020.csv`) with cryptographically secure checksum verification and manifest generation.

## Requirements

### Requirement: Raw Dataset Verification and Placement

The system MUST verify that the raw dataset file exists in `data/raw/ai4i2020.csv`, contains exact CSV structure, and is never altered or transformed in place.

#### Scenario: Successful raw dataset validation
- GIVEN the file `data/raw/ai4i2020.csv` exists and is non-empty
- WHEN the ingestion service validates the file structure
- THEN the system SHALL verify that the file contains exactly 10,000 data rows and 14 header columns
- AND the system SHALL calculate the SHA-256 digest of the raw bytes.

#### Scenario: Missing or empty dataset file
- GIVEN the file `data/raw/ai4i2020.csv` is missing or has a file size of 0 bytes
- WHEN the ingestion service attempts execution
- THEN the system MUST abort with a descriptive error message stating that the official raw file is required.

---

### Requirement: Idempotent Manifest Generation

The system SHALL generate an immutable manifest at `data/raw/manifest.json` describing the origin, dimensions, columns, byte size, and SHA-256 hash of the dataset.

#### Scenario: Initial manifest creation
- GIVEN `data/raw/ai4i2020.csv` exists with valid rows and columns
- AND `data/raw/manifest.json` does not exist
- WHEN the ingestion process runs
- THEN the system MUST write `data/raw/manifest.json` containing `file_name`, `sha256`, `n_rows`, `n_columns`, `columns`, `size_bytes`, and `ingestion_date`
- AND the system SHALL exit with code 0 indicating success.

#### Scenario: Idempotent execution with matching hash
- GIVEN `data/raw/manifest.json` exists with recorded SHA-256 `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e`
- WHEN the ingestion process is executed again on the identical raw file
- THEN the system MUST detect that the current file hash matches the manifest
- AND the system MUST NOT overwrite or alter `manifest.json`
- AND the system SHALL exit with code 0.

#### Scenario: Integrity violation on file modification
- GIVEN `data/raw/manifest.json` exists with a recorded SHA-256 hash
- WHEN `data/raw/ai4i2020.csv` has been modified or corrupted so its hash differs
- THEN the system MUST abort immediately with an integrity violation error
- AND the system MUST NOT overwrite `manifest.json`.
