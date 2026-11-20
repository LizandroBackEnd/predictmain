# Delta for ML Pipeline

## ADDED Requirements

### Requirement: Delivery Pipeline Synchronization

The Sprint 1 delivery copy of the Python ML pipeline MUST match the canonical pipeline source files and MUST include the requirements and loadable serialized pipeline artifact needed to reproduce the documented processing stages.

#### Scenario: Pipeline copy is synchronized

- GIVEN canonical pipeline source files and delivery copies exist
- WHEN synchronization validation runs
- THEN every expected source file MUST match by checksum or documented content comparison
- AND the delivery artifact MUST be loadable in the documented Python environment.

#### Scenario: Pipeline copy is stale

- GIVEN a delivery source file or serialized artifact differs from the canonical version
- WHEN synchronization validation runs
- THEN it MUST report the stale path
- AND MUST fail until the delivery copy is synchronized.

## MODIFIED Requirements

### Requirement: Decoupled Application Use Cases

All pipeline orchestrations and business use cases MUST reside under `ml_service/src/application/`, and the Sprint 1 delivery copy MUST expose the same use-case behavior and output contracts as the canonical pipeline.
(Previously: the requirement applied only to the canonical `ml_service/src/application/` tree.)

#### Scenario: Ingestion Use Case

- GIVEN a raw CSV dataset file
- WHEN `IngestionService.run_ingestion` is executed from the canonical or synchronized delivery pipeline
- THEN it SHALL validate dataset structure (10,000 rows, 14 columns)
- AND it SHALL compute the SHA-256 cryptographic digest via buffered byte-streaming
- AND it SHALL create or verify the applicable manifest idempotently.

#### Scenario: Null Treatment Use Case

- GIVEN raw or dirty telemetry data
- WHEN `NullTreatmentService.run` is executed from the canonical or synchronized delivery pipeline
- THEN it SHALL drop rows with missing target or failure mode labels using boolean mask indexing
- AND it SHALL impute continuous sensor features using vectorized median replacement
- AND it SHALL impute categorical `Type` using mode.

#### Scenario: Sklearn Transformation Pipeline

- GIVEN cleaned feature data
- WHEN `PipelineService.build_and_fit` is executed from the canonical or synchronized delivery pipeline
- THEN it SHALL calculate `Temp_diff = Process temperature [K] - Air temperature [K]`
- AND the output schema and serialized pipeline behavior MUST match the canonical pipeline.
