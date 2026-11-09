# Tasks: Python Clean Architecture & Clean Code Refactor

- **Change ID**: `change-python-clean-architecture-refactor`
- **Domain**: `ml_service`
- **Status**: READY FOR IMPLEMENTATION

## Review Workload Forecast

| Field | Value |
| :--- | :--- |
| Estimated changed lines | ~450 lines refactored / reorganized |
| 400-line budget risk | Low (modular file reorganizations) |
| Chained PRs recommended | No |
| Suggested split | Structured atomic batches |
| Delivery strategy | Strict TDD & Verification |

---

## Batch 1: Domain Layer Modernization & Rules Consolidation

- [ ] 1.1 Refactor `src/domain/models.py` to use PEP 585 (`list`, `dict`), PEP 604 (`T | None`), and strict frozen immutability (`frozen=True`).
- [ ] 1.2 Move and refactor `null_treatment/rules.py` to `src/domain/null_rules.py` with strict typing and no I/O dependencies.
- [ ] 1.3 Move and refactor `outlier_analysis/rules.py` to `src/domain/outlier_rules.py` with strict typing and documented physical limits.
- [ ] 1.4 Validate domain models and run test suite (`PYTHONPATH=ml_service ml_service/.venv/bin/python -m unittest discover -s ml_service/tests`).

## Batch 2: Infrastructure Layer Modernization

- [ ] 2.1 Refactor `src/infrastructure/paths.py` ensuring clean type annotations and deterministic root resolution.
- [ ] 2.2 Extract Joblib pipeline persistence logic into `src/infrastructure/storage.py` with explicit exception handling.
- [ ] 2.3 Refactor Markdown report generation logic from `profiling/report_builder.py` into `src/infrastructure/reporting.py`.
- [ ] 2.4 Verify infrastructure adapters with targeted unit tests.

## Batch 3: Application Layer Migration & Pandas Vectorization

- [ ] 3.1 Migrate and refactor `src/ingestion/service.py` to `src/application/ingestion.py` using streaming SHA-256 calculation and clean file reading.
- [ ] 3.2 Migrate and refactor `src/profiling/service.py` to `src/application/profiling.py`:
  - Optimize missing value detection into a single-pass `df.isna().sum()` calculation (eliminating double evaluations).
  - Use vectorized descriptive statistics for numerical columns.
- [ ] 3.3 Migrate and refactor `src/null_treatment/service.py` to `src/application/null_treatment.py`:
  - Use vectorized boolean masking for row dropping.
  - Apply clean `.loc` assignments to avoid `SettingWithCopyWarning`.
- [ ] 3.4 Migrate and refactor `src/outlier_analysis/service.py` to `src/application/outlier_analysis.py`:
  - Use native Pandas `.quantile()` / NumPy linear interpolation and vectorized `.clip()` for Winsorization.
- [ ] 3.5 Migrate and refactor `src/transformation/service.py` and `features.py` to `src/application/transformation.py` and `features.py`:
  - Add explicit PEP 484 type hints to `DerivedFeatureAdder` (`fit(self, X: pd.DataFrame, y: pd.Series | np.ndarray | None = None)`).
- [ ] 3.6 Run full test suite to verify all use cases pass without regression.

## Batch 4: Delivery Layer (Decoupling CLI)

- [ ] 4.1 Create `src/interfaces/cli/commands.py` with modular execution handlers for `ingest`, `profile`, `nulls`, `outliers`, and `transform`.
- [ ] 4.2 Create `src/interfaces/cli/entrypoint.py` with clean `argparse` configuration.
- [ ] 4.3 Replace monolithic `ml_service/src/cli.py` with a thin backward-compatible forwarder delegating to `src/interfaces/cli/entrypoint.py`.
- [ ] 4.4 Test all CLI commands end-to-end (`python -m src.cli --help`, `ingest`, `profile`, etc.).

## Batch 5: Test Suite Modernization & Final Verification

- [ ] 5.1 Update test imports in `ml_service/tests/` to target new Clean Architecture paths while verifying backwards-compatibility shims.
- [ ] 5.2 Execute complete test suite (`PYTHONPATH=ml_service ml_service/.venv/bin/python -m unittest discover -s ml_service/tests`) and verify all 40 tests pass.
- [ ] 5.3 Remove obsolete empty legacy folders in `ml_service/src/` (`ingestion/`, `profiling/`, `null_treatment/`, `outlier_analysis/`, `transformation/`).
- [ ] 5.4 Run linter and formatting checks to ensure 100% clean code compliance.
