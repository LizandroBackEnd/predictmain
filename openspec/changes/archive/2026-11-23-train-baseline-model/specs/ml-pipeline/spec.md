# Delta for ML Pipeline

## ADDED Requirements

### REQ-07: Baseline Training Use Case

A baseline training orchestration MUST reside under `ml_service/src/application/` and MUST compose dataset splitting, HU-06 transformation fitting on train only, classifier training, test prediction, model selection, artifact persistence, and metrics reporting without embedding that logic in CLI handlers.

#### Scenario: Training Use Case Happy Path
- **GIVEN** a processed labeled CSV suitable for HU-08 training
- **WHEN** the baseline training use case is executed
- **THEN** it SHALL split the data 75/25 with a documented seed and stratification when feasible
- **AND** it SHALL fit the HU-06 transformation pipeline on the training partition only
- **AND** it SHALL train logistic regression and random forest baselines, evaluate them on the transformed test set, persist the selected model to `ml_service/artifacts/modelo.joblib`, and write `reports/model_baseline.md`.

#### Scenario: Training Use Case Failure
- **GIVEN** missing inputs, invalid labels, or an evaluation failure
- **WHEN** the baseline training use case is executed
- **THEN** it SHALL raise or return a handled failure
- **AND** it SHALL NOT claim that a successful baseline artifact was produced.

## MODIFIED Requirements

### REQ-03: Decoupled Application Use Cases

All pipeline orchestrations and business use cases MUST reside under `ml_service/src/application/`, and the Sprint 1 delivery copy MUST expose the same use-case behavior and output contracts as the canonical pipeline.
(Previously: covered ingestion, null treatment, and transformation only; now also requires a baseline training use case under application/)

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

#### Scenario: Baseline Training Use Case
- **GIVEN** a processed labeled dataset and the HU-06 transformation contract
- **WHEN** the baseline training application service is executed
- **THEN** training orchestration SHALL live under `ml_service/src/application/`
- **AND** it SHALL reuse `split_dataset` with an explicit 75/25 contract for HU-08 without requiring business logic in the CLI layer.

### REQ-04: Infrastructure Adapters & Path Resolution

File I/O, Joblib persistence, and Markdown report rendering MUST be isolated in `ml_service/src/infrastructure/`.
(Previously: resolved raw/processed/reports/pipeline paths only; now also resolves baseline model and metrics-report paths)

#### Scenario: Dynamic Root Anchor
- **GIVEN** CLI commands executed from either the project root or inside `ml_service/`
- **WHEN** `paths` in `src/infrastructure/paths.py` resolves directories
- **THEN** it SHALL dynamically detect the workspace root via parent markers (`docker-compose.yml`, `package.json`)
- **AND** it SHALL provide deterministic absolute paths for `data/raw/`, `data/processed/`, `reports/`, and `ml_service/artifacts/`.

#### Scenario: Pipeline Serialization
- **GIVEN** a fitted Sklearn pipeline
- **WHEN** persisted to `ml_service/artifacts/pipeline.joblib`
- **THEN** it SHALL be serializable and deserializable via a dedicated `JoblibStorage` adapter.

#### Scenario: Baseline Model And Metrics Paths
- **GIVEN** a successful baseline training run
- **WHEN** infrastructure paths and adapters are used
- **THEN** they SHALL resolve `ml_service/artifacts/modelo.joblib` and `reports/model_baseline.md`
- **AND** persistence and report rendering SHALL remain outside the application/CLI business rules.

### REQ-05: Modular CLI Delivery Layer

The CLI interface MUST be decoupled from business logic and reside under `ml_service/src/interfaces/cli/`.
(Previously: routed ingest/profile/nulls/outliers/transform/apply/validate/all; now also routes `train`)

#### Scenario: Unified CLI Routing
- **GIVEN** command line invocations `python -m src.cli <command>`
- **WHEN** subcommands `ingest`, `profile`, `nulls`, `outliers`, `transform`, `apply`, `validate`, `train`, or `all` are invoked
- **THEN** the CLI router SHALL delegate directly to application services
- **AND** it SHALL return exit code 0 on success and exit code 1 with clean stderr logging on handled exceptions
- **AND** no business logic or dataset transformation code SHALL live in CLI command files.

#### Scenario: Train Subcommand
- **GIVEN** a valid processed CSV path and default artifact destinations
- **WHEN** `python -m src.cli train` is invoked
- **THEN** the CLI SHALL delegate to the baseline training use case
- **AND** on success it SHALL exit 0 after the model artifact and metrics report are written
- **AND** on handled failure it SHALL exit 1 without embedding training logic in the command file.
