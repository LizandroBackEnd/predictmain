# Delta for Dataset Ingestion

## ADDED Requirements

### Requirement: Delivery Manifest Reconciliation

The Sprint 1 delivery package MUST expose a manifest whose file metadata, dimensions, columns, and SHA-256 digest match the canonical project manifest for the immutable raw dataset.

#### Scenario: Matching delivery manifest

- GIVEN the canonical manifest and delivery manifest are present
- WHEN reconciliation runs
- THEN their file identity, dimensions, columns, and SHA-256 MUST match
- AND the result MUST record successful reconciliation.

#### Scenario: Delivery manifest mismatch

- GIVEN the delivery manifest differs from the canonical manifest
- WHEN reconciliation runs
- THEN it MUST fail and identify each mismatched field
- AND MUST NOT modify the canonical raw dataset.

## MODIFIED Requirements

### Requirement: Raw Dataset Verification and Placement

The system MUST verify that the raw dataset file exists in `data/raw/ai4i2020.csv` and in the Sprint 1 delivery location, contains the exact CSV structure, and is never altered or transformed in place.
(Previously: verification applied only to the project-level raw dataset location.)

#### Scenario: Successful raw dataset validation

- GIVEN the canonical file `data/raw/ai4i2020.csv` and delivery file `entrega_sprint1/03_dataset/data/raw/ai4i2020.csv` exist and are non-empty
- WHEN the ingestion and delivery reconciliation process validates both files
- THEN each file SHALL contain exactly 10,000 data rows and 14 header columns
- AND the delivery file SHA-256 MUST equal the canonical file SHA-256.

#### Scenario: Missing or empty dataset file

- GIVEN either the canonical or delivery raw dataset file is missing or has a file size of 0 bytes
- WHEN the ingestion and delivery reconciliation process executes
- THEN it MUST abort with a descriptive error naming the missing or empty file
- AND MUST NOT overwrite the available source file.

### Requirement: Idempotent Manifest Generation

The system SHALL generate or verify an immutable manifest at `data/raw/manifest.json` and a synchronized copy at `entrega_sprint1/03_dataset/data/raw/manifest.json`, describing the origin, dimensions, columns, byte size, and SHA-256 hash of the canonical dataset.
(Previously: the system generated and verified only `data/raw/manifest.json`.)

#### Scenario: Initial manifest creation

- GIVEN the canonical raw dataset exists with valid rows and columns
- AND either manifest does not exist
- WHEN the ingestion process runs
- THEN it MUST write the missing manifest with `file_name`, `sha256`, `n_rows`, `n_columns`, `columns`, `size_bytes`, and `ingestion_date`
- AND the delivery manifest MUST describe the same canonical file.

#### Scenario: Idempotent execution with matching hash

- GIVEN both manifests exist with the canonical SHA-256
- WHEN ingestion and reconciliation execute again
- THEN the process MUST detect matching hashes
- AND MUST NOT alter either manifest unnecessarily
- AND MUST exit with code 0.

#### Scenario: Integrity violation on file modification

- GIVEN either raw file or manifest hash differs from the canonical source
- WHEN reconciliation executes
- THEN it MUST abort immediately with an integrity violation error
- AND MUST NOT overwrite the canonical manifest or raw dataset.
