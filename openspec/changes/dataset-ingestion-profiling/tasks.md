# Tasks: Dataset Ingestion and Profiling Pipeline

## Review Workload Forecast

| Field | Value |
| :--- | :--- |
| Estimated changed lines | ~320 lines of authored Python code (excluding raw CSV) |
| 400-line budget risk | Low |
| Chained PRs recommended | No |
| Suggested split | Single deliverable work unit |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
| :---: | :--- | :---: | :--- | :--- | :--- |
| 1 | Ingestion, profiling service, unified CLI, and data report | Single PR | `python -m unittest discover -s ml_service/tests` | `python -m src.cli all` | Revert `ml_service/src/` and `data/raw/` |

---

## Phase 1: Raw Data & Infrastructure Setup

- [x] 1.1 Copy official dataset from `/home/lizdev/Escritorio/projects/refactor/PredictMain/data/raw/ai4i2020.csv` (read-only) to `data/raw/ai4i2020.csv`
- [x] 1.2 Implement dynamic workspace path resolver in `ml_service/src/infrastructure/paths.py`
- [x] 1.3 Verify dependencies and package definitions in `ml_service/requirements.txt`

## Phase 2: Domain Models & Ingestion Service

- [x] 2.1 Define domain models (`ManifestData`, `ValidationResult`, `DatasetSummary`) in `ml_service/src/domain/models.py`
- [x] 2.2 Implement `IngestionService` with SHA-256 calculation and idempotent manifest generation in `ml_service/src/ingestion/service.py`
- [x] 2.3 Create unit tests for hashing, schema checks, and manifest idempotency in `ml_service/tests/test_ingestion.py`

## Phase 3: Telemetry Profiling Service

- [x] 3.1 Implement `ProfilingService` in `ml_service/src/profiling/service.py` calculating descriptive statistics and class distributions
- [x] 3.2 Implement report generator in `ml_service/src/profiling/report_builder.py` outputting `docs/03-analysis/data-profile.md`
- [x] 3.3 Create unit tests for statistical calculations in `ml_service/tests/test_profiling.py`

## Phase 4: Unified CLI Entrypoint & Verification

- [x] 4.1 Implement unified CLI facade in `ml_service/src/cli.py` with `ingest`, `profile`, and `all` commands
- [x] 4.2 Execute `python -m src.cli all` to generate `data/raw/manifest.json` and `docs/03-analysis/data-profile.md`
- [x] 4.3 Verify that manifest SHA-256 matches the raw file hash (`59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183`) and output complies with HU-01 and HU-02
