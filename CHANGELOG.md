# Changelog

All notable changes to PredictMain will be documented in this file.

## [Unreleased]

### Refactor
- **ml-service**: Refactor Python data and ML pipelines into Clean Architecture layers:
  - Isolate domain models and rules under `src/domain/` with PEP 585/604 compliance.
  - Migrate all pipeline use cases to `src/application/` with single-pass Pandas vectorization.
  - Extract Joblib persistence and Markdown reporting to `src/infrastructure/`.
  - Decouple CLI delivery into `src/interfaces/cli/` with modular command handlers and a lightweight backward-compatible forwarder.

