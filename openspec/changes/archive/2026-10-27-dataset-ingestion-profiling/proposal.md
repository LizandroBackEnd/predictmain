# Proposal: Dataset Ingestion and Profiling Pipeline

## Intent

The current project requires a robust, reproducible, and clean data foundation for the AI4I 2020 Predictive Maintenance Dataset, satisfying the requirements of **HU-01** (Raw Data Ingestion) and **HU-02** (Telemetry Profiling).

An external prototype exists at `/home/lizdev/Escritorio/projects/refactor/PredictMain`, containing initial scripts (`create_manifest.py` and `profile_data.py`). However, those scripts are procedural, tightly coupled to hardcoded paths, and lack modular architecture.

This proposal defines how to adapt, refactor, and elevate those scripts into the official PredictMain codebase following **Clean Architecture** principles in Python, while simplifying execution into a unified, developer-friendly interface.

---

## Scope

### In Scope
- **Raw Data Ingestion (HU-01):** Placement of the official `ai4i2020.csv` in `data/raw/` in an immutable, read-only state.
- **Clean Architecture Python Pipeline:** Modularization of the ingestion and profiling logic within `ml_service/src/`:
  - Domain models (e.g., `Manifest`, `ColumnMetadata`, `DataProfileSummary`) using strict typing and validation.
  - Use cases (e.g., `IngestDatasetUseCase`, `ProfileDatasetUseCase`) decoupled from I/O details.
  - Adapters for CSV reading, SHA-256 calculation, JSON manifest writing, and Markdown report rendering.
- **Unified & Simplified Execution:** A single CLI/runner entrypoint in `ml_service` (e.g., `python -m src.cli ingest` / `python -m src.cli profile` or `--all`) with clear logging and zero path ambiguities.
- **Idempotency & Integrity:** Verification that repeated executions preserve existing manifests and fail fast if file checksum drift occurs.
- **Documentation & Trazability:** Generation of `data/raw/manifest.json` and updating data profiling in `docs/03-analysis/data-profile.md`.

### Out of Scope
- Data cleaning, imputation of missing values, and outlier treatment (**HU-03** and **HU-04**).
- Feature engineering, One-Hot Encoding, and transformation pipeline construction (**HU-05** and **HU-06**).
- Model training, evaluation, and FastAPI REST endpoint implementation (**HU-07**).
- Next.js Web UI visualization.

---

## Capabilities

### New Capabilities
- `dataset-ingestion`: Automated verification of the raw dataset, idempotency checks, SHA-256 hash calculation, and manifest generation in `data/raw/manifest.json`.
- `telemetry-profiling`: Automated calculation of descriptive statistics, schema validation against UCI specifications, cardinality analysis, and generation of the technical data profile report.

### Modified Capabilities
*None*

---

## Approach

1. **Architecture Decoupling:**
   Structure `ml_service/src/` into distinct layers:
   - `domain/`: Value objects and dataclasses (`ManifestMetadata`, `DatasetSummary`, `ColumnProfile`).
   - `ingestion/`: Business rules for raw data validation, file integrity verification, and manifest building.
   - `profiling/`: Statistical analyzers, distribution extractors, and markdown report formatters.
   - `infrastructure/` & `cli.py`: Dynamic project path resolution, CLI arguments parsing, and file system I/O.
2. **Simplified Developer Experience:**
   Provide a central runner script so that running the pipeline does not require navigating internal directory structures:
   ```bash
   # Ingest raw dataset and generate manifest
   python -m src.cli ingest

   # Profile dataset and generate docs report
   python -m src.cli profile

   # Execute full pipeline end-to-end
   python -m src.cli all
   ```
3. **Data Parity with Reference Implementation:**
   Verify against `/home/lizdev/Escritorio/projects/refactor/PredictMain/data/raw/ai4i2020.csv` to ensure the SHA-256 matches `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e`.

---

## Affected Areas

| Area | Impact | Description |
| :--- | :---: | :--- |
| `data/raw/ai4i2020.csv` | New | Copy of the official raw dataset in read-only form. |
| `data/raw/manifest.json` | New | Ingestion manifest with checksum, row count, and metadata. |
| `ml_service/src/domain/` | New | Domain models for manifest and dataset profiling. |
| `ml_service/src/ingestion/` | New | Clean Architecture service for data ingestion and hashing. |
| `ml_service/src/profiling/` | New | Clean Architecture service for statistical profiling. |
| `ml_service/src/cli.py` | New | Unified CLI entrypoint for running ingestion and profiling. |
| `docs/03-analysis/data-profile.md` | New | Auto-generated markdown profiling report based on dataset. |

---

## Risks

| Risk | Likelihood | Mitigation |
| :--- | :---: | :--- |
| Working directory discrepancy when invoking Python from project root vs `ml_service` | Medium | Implement robust path resolution using `Path(__file__).resolve()` anchored to the workspace root. |
| Missing Python dependencies in `.venv` | Low | Ensure `pandas>=2.2.0`, `pydantic>=2.6.0`, and `python-dotenv` are present in `ml_service/requirements.txt`. |
| Unintended modification of raw data | Low | Enforce read-only file permissions and strict SHA-256 validation checks before write attempts. |

---

## Rollback Plan

All changes are additive within `ml_service/src/` and `data/raw/`. In case of failure or regression, the files in `data/raw/` and `ml_service/src/` can be safely removed or reverted via `git clean -fd` without affecting the web platform or database layer.

---

## Dependencies

- Python 3.11+
- Virtual environment in `ml_service/.venv`
- `pandas` and standard library (`hashlib`, `csv`, `json`, `pathlib`, `dataclasses`)

---

## Success Criteria

- [ ] `data/raw/ai4i2020.csv` is present and verified with SHA-256 `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e`.
- [ ] Ingestion script is idempotent: running it multiple times preserves the existing manifest and raises no errors.
- [ ] Ingestion and profiling are executable via a single simplified command (`python -m src.cli all`).
- [ ] `data/raw/manifest.json` is generated with 10,000 rows, 14 columns, and full metadata.
- [ ] `docs/03-analysis/data-profile.md` is generated with complete statistical breakdown and class distributions.
