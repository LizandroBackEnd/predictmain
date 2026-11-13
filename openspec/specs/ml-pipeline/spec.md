# Specification: Python Clean Architecture & Clean Code Refactor

- **Change ID**: `change-python-clean-architecture-refactor`
- **Domain**: `ml_service` (Data Processing & ML Pipeline)
- **Status**: SPECIFIED

---

## 1. Purpose

This specification establishes the functional and non-functional requirements for refactoring `ml_service/src/` to adhere to **Clean Architecture**, **Clean Code**, and **KISS** (Keep It Simple, Stupid) principles, aligning with modern Python best practices (PEP 8, PEP 585, PEP 604, PEP 484) and `.agents/skills/python/SKILL.md`.

Beyond folder reorganization, this change mandates an in-depth **code-level refactor**: eliminating iterative anti-patterns, using **Pandas idiomatic vectorized methods** efficiently, and removing code smells across all services while guaranteeing 100% test compatibility.

---

## 2. Code-Level & Architectural Requirements

### REQ-01: Idiomatic & Vectorized Pandas Best Practices

All data transformations, quality audits, profiling, and outlier operations MUST use vectorized, idiomatic Pandas/NumPy operations instead of manual loops or redundant computations.

#### Scenario: Single-Pass Missing Value Auditing
- **GIVEN** a telemetry DataFrame
- **WHEN** computing null counts across columns
- **THEN** the system SHALL compute `isna().sum()` in a single vectorized pass
- **AND** the system SHALL NOT compute `isna().sum()` multiple times inside comprehension filters.

#### Scenario: Vectorized Aggregations in Profiling
- **GIVEN** continuous sensor features in `analyze_dataset`
- **WHEN** computing statistical metrics (min, max, mean, median, std)
- **THEN** the system SHALL leverage vectorized aggregation (`.agg()` or `.describe()`)
- **AND** avoid repetitive individual scalar queries in sequential loops where vectorization applies.

#### Scenario: Vectorized Outlier Analysis & Winsorization
- **GIVEN** continuous telemetry variables
- **WHEN** detecting IQR fences and percentiles
- **THEN** the system SHALL use native `.quantile()` or NumPy methods vectorially
- **AND** Winsorization capping SHALL use `.clip(lower=..., upper=...)` directly on Pandas Series without element-wise branching.

#### Scenario: SettingWithCopy & Pure Transformations
- **GIVEN** data transformations in ingestion, null treatment, and pipeline services
- **WHEN** generating transformed or imputed datasets
- **THEN** transformations SHALL operate on explicit copies or use `.loc` indexing to avoid `SettingWithCopyWarning`.

---

### REQ-02: Pure Domain Layer Isolation

The domain layer MUST reside in `ml_service/src/domain/` and MUST contain zero dependencies on external frameworks (e.g., no Sklearn, no I/O, no CLI dependencies).

#### Scenario: Strict Typing and Invariant Enforcement
- **GIVEN** domain entities and value objects defined in `src/domain/models.py`
- **WHEN** any model is instantiated
- **THEN** it SHALL use PEP 585 native generic collections (`list[str]`, `dict[str, Any]`) instead of legacy `typing` imports
- **AND** it SHALL use PEP 604 union syntax (`str | None`) instead of `Optional[str]`
- **AND** it SHALL enforce immutability using `frozen=True` (via Pydantic v2 `ConfigDict` or frozen dataclasses).

#### Scenario: Domain Rules Consolidation
- **GIVEN** column null treatment policies and sensor outlier limits
- **WHEN** rules are defined in `src/domain/null_rules.py` and `src/domain/outlier_rules.py`
- **THEN** they SHALL represent pure domain rules and constants decoupled from file-reading or logging logic.

---

### REQ-03: Decoupled Application Use Cases

All pipeline orchestrations and business use cases MUST reside under `ml_service/src/application/`, and the Sprint 1 delivery copy MUST expose the same use-case behavior and output contracts as the canonical pipeline.

#### Scenario: Ingestion Use Case
- **GIVEN** a raw CSV dataset file
- **WHEN** `IngestionService.run_ingestion` is executed from the canonical or synchronized delivery pipeline
- **THEN** it SHALL validate dataset structure (10,000 rows, 14 columns)
- **AND** it SHALL compute the SHA-256 cryptographic digest via buffered byte-streaming (1MB chunks) without loading raw CSV entirely into memory
- **AND** it SHALL create or verify the applicable manifest idempotently.

#### Scenario: Null Treatment Use Case
- **GIVEN** raw or dirty telemetry data
- **WHEN** `NullTreatmentService.run` is executed from the canonical or synchronized delivery pipeline
- **THEN** it SHALL drop rows with missing target or failure mode labels using boolean mask indexing
- **AND** it SHALL impute continuous sensor features using vectorized median replacement
- **AND** it SHALL impute categorical `Type` using mode (most frequent category).

#### Scenario: Sklearn Transformation Pipeline
- **GIVEN** cleaned feature data
- **WHEN** `PipelineService.build_and_fit` is executed from the canonical or synchronized delivery pipeline
- **THEN** it SHALL apply `DerivedFeatureAdder` to calculate `Temp_diff = Process temperature [K] - Air temperature [K]`
- **AND** all estimator signatures (e.g. `fit(X, y=None)`) SHALL be strictly typed with PEP 484 annotations
- **AND** the output schema and serialized pipeline behavior MUST match the canonical pipeline.

---

### REQ-04: Infrastructure Adapters & Path Resolution

File I/O, Joblib persistence, and Markdown report rendering MUST be isolated in `ml_service/src/infrastructure/`.

#### Scenario: Dynamic Root Anchor
- **GIVEN** CLI commands executed from either the project root or inside `ml_service/`
- **WHEN** `paths` in `src/infrastructure/paths.py` resolves directories
- **THEN** it SHALL dynamically detect the workspace root via parent markers (`docker-compose.yml`, `package.json`)
- **AND** it SHALL provide deterministic absolute paths for `data/raw/`, `data/processed/`, `reports/`, and `ml_service/artifacts/`.

#### Scenario: Pipeline Serialization
- **GIVEN** a fitted Sklearn pipeline
- **WHEN** persisted to `ml_service/artifacts/pipeline.joblib`
- **THEN** it SHALL be serializable and deserializable via a dedicated `JoblibStorage` adapter.

---

### REQ-05: Modular CLI Delivery Layer

The CLI interface MUST be decoupled from business logic and reside under `ml_service/src/interfaces/cli/`.

#### Scenario: Unified CLI Routing
- **GIVEN** command line invocations `python -m src.cli <command>`
- **WHEN** subcommands `ingest`, `profile`, `nulls`, `outliers`, `transform`, or `all` are invoked
- **THEN** the CLI router SHALL delegate directly to application services
- **AND** it SHALL return exit code 0 on success and exit code 1 with clean stderr logging on handled exceptions
- **AND** no business logic or dataset transformation code SHALL live in CLI command files.

---

### REQ-06: Delivery Pipeline Synchronization

The Sprint 1 delivery copy of the Python ML pipeline MUST match the canonical pipeline source files and MUST include the requirements and loadable serialized pipeline artifact needed to reproduce the documented processing stages.

#### Scenario: Pipeline copy is synchronized
- **GIVEN** canonical pipeline source files and delivery copies exist
- **WHEN** synchronization validation runs
- **THEN** every expected source file MUST match by checksum or documented content comparison
- **AND** the delivery artifact MUST be loadable in the documented Python environment.

#### Scenario: Pipeline copy is stale
- **GIVEN** a delivery source file or serialized artifact differs from the canonical version
- **WHEN** synchronization validation runs
- **THEN** it MUST report the stale path
- **AND** it MUST fail until the delivery copy is synchronized.

---

## 3. Non-Functional Requirements

- **NFR-01 (Strict Typing)**: Zero untyped public methods; strict adherence to PEP 484, PEP 585, and PEP 604.
- **NFR-02 (Test Preservation)**: 100% pass rate on all 40 existing unit tests in `ml_service/tests/`.
- **NFR-03 (Performance & Memory)**: Streaming CSV hash calculation; vectorized single-pass Pandas routines.
- **NFR-04 (KISS / Clean Code)**: Clean functions $<30$ lines, cyclomatic complexity per method $<10$; removal of redundant dictionary wrappers.

---

## 4. Acceptance Criteria Checklist

- [ ] All 40 unit tests in `ml_service/tests/` pass with `OK`.
- [ ] No double-evaluations like `df[col].isna().sum()` in loops; vectorized Pandas idioms used throughout.
- [ ] `ml_service/src/` divided into `domain/`, `application/`, `infrastructure/`, and `interfaces/cli/`.
- [ ] All legacy `typing.List`, `typing.Dict`, `typing.Optional` eliminated.
- [ ] `cli.py` reduced from monolithic 269 lines to modular subcommands.
- [ ] CLI runs end-to-end (`python -m src.cli --help` and subcommands) cleanly.
