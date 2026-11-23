# Tasks: Train Baseline Failure-Risk Classifier (HU-08)

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 450–700 authored lines (application service, domain models, storage/reporting, CLI, tests, generated report) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Single PR under size:exception (user-approved 2026-11-22) |
| Delivery strategy | exception-ok |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: size-exception
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Full HU-08 baseline training: foundation, service, CLI, tests, artifacts/report | Single PR (size:exception) | `cd ml_service && python -m unittest tests.test_baseline_training tests.test_cli_train -v` | `cd ml_service && python -m src.cli train --csv ../data/processed/ai4i2020_outlier_analyzed.csv` | All HU-08 code under `ml_service/`, generated `modelo.joblib` / `reports/model_baseline.md`, optional `entrega_sprint1/05_entrenamiento/` edits |

## Phase 1: Foundation

- [ ] 1.1 Add frozen domain result types for metric rows and training run provenance in `ml_service/src/domain/models.py`.
- [ ] 1.2 Extend `ml_service/src/infrastructure/paths.py` with defaults for `ml_service/artifacts/modelo.joblib` and `reports/model_baseline.md`.
- [ ] 1.3 Extend `ml_service/src/infrastructure/storage.py` with save/load helpers for the baseline estimator artifact (no `joblib` usage from application code).
- [ ] 1.4 Add `build_model_baseline_report(...)` in `ml_service/src/infrastructure/reporting.py` that renders accuracy, precision, recall, F1, ROC-AUC for both models plus seed/split/selection provenance.

## Phase 2: Stratified Preparation And Training Service

- [ ] 2.1 Create `ml_service/src/application/baseline_training.py` that loads the labeled CSV and calls `split_dataset(..., test_size=0.25, random_state=42)` without changing `DEFAULT_TEST_SIZE` in `ml_service/src/application/dataset_split.py`.
- [ ] 2.2 In the training service, fit `TransformationService` on the training partition only, transform train/test, and fail with a descriptive error when the CSV is missing/empty.
- [ ] 2.3 Train logistic regression (`class_weight="balanced"`, `max_iter=1000`) and random forest (`class_weight="balanced"`, `n_estimators=300`, `random_state=42`) on transformed training features.
- [ ] 2.4 Generate test-set predictions/probabilities, compute required metrics, select by F1 with recall tie-breaker (deterministic fallback to `random_forest`), persist selected model, and write the baseline report.

## Phase 3: CLI Wiring

- [ ] 3.1 Add thin `run_train_cmd` in `ml_service/src/interfaces/cli/commands.py` that delegates to the training service and returns exit code 0/1.
- [ ] 3.2 Register `train` in `ml_service/src/interfaces/cli/entrypoint.py` with `--csv`, `--model`, and `--report` arguments defaulting to `ProjectPaths`.

## Phase 4: Testing Against Spec Scenarios

- [ ] 4.1 RED then GREEN: in `ml_service/tests/test_baseline_training.py`, cover stratified 75/25 reproducibility and non-stratified fallback from `baseline-model-training` split scenarios.
- [ ] 4.2 RED then GREEN: assert the transformation pipeline is fitted only on train (scaler statistics match train, not full data) and missing/empty input fails without writing `modelo.joblib`.
- [ ] 4.3 RED then GREEN: assert both models are scored, selection follows F1/recall rules, artifact round-trips via storage helpers, and the Markdown report contains the required metric columns and provenance fields.
- [ ] 4.4 RED then GREEN: in `ml_service/tests/test_cli_train.py`, assert `train` exits 0 and creates artifacts on a temp fixture, and exits 1 without a success artifact on missing input.
- [ ] 4.5 Run the focused unit suites and confirm existing HU-06 split tests in `ml_service/tests/test_dataset_split.py` (read-only) still pass with the unchanged 0.20 default.

## Phase 5: Runtime Evidence And Cleanup

- [ ] 5.1 Run `python -m src.cli train` against `data/processed/ai4i2020_outlier_analyzed.csv` (read-only) and verify `ml_service/artifacts/modelo.joblib` plus `reports/model_baseline.md` are produced.
- [ ] 5.2 Update `entrega_sprint1/05_entrenamiento/` docs/config status only if needed so they match the executed HU-08 artifacts without modifying canonical `data/` or `ml_service` sources outside this change.
- [ ] 5.3 Review the diff to ensure `DEFAULT_TEST_SIZE` remains 0.20 and HU-06 `pipeline.joblib` was not accidentally overwritten by the training flow.
