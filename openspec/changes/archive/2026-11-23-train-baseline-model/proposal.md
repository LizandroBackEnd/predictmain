# Proposal: Train Baseline Failure-Risk Classifier (HU-08)

## Intent

Establish the first supervised baseline for PredictMain failure-risk prediction. After HU-06 prepared a reproducible transformation pipeline, the project still lacks a fitted classifier, test-set predictions, and a recorded metrics comparison. Data scientists need a stratified 75/25 split with a fixed seed, at least one trained classifier that reuses the HU-06 transformation pipeline, serialized model output, and a durable metrics report so later evaluation and threshold tuning have a concrete baseline.

## Scope

### In Scope
- Stratified train/test split at 75%/25% with a documented random seed for the imbalanced `Machine failure` target.
- Training of two baseline classifiers (logistic regression and random forest) that consume features produced by the HU-06 transformation pipeline, refitting the pipeline on the training partition only to avoid leakage.
- Initial predictions on the held-out test set for both models.
- Serialization of the selected trained classifier to `ml_service/artifacts/modelo.joblib`.
- Generation of `reports/model_baseline.md` with a comparative table of accuracy, precision, recall, F1, and ROC-AUC for both models, plus enough run metadata to reproduce the result.
- CLI entry point under `ml_service` that executes the flow without errors and records the outcome for later evaluation.
- Focused unit/integration tests for split proportions, stratification, seed reproducibility, artifact persistence, and report generation.

### Out of Scope
- Hyperparameter search, threshold optimization, and cross-validation (already deferred in delivery training config).
- Class rebalancing techniques beyond `class_weight` already planned for the baselines (for example SMOTE).
- Multi-label modeling of failure modes (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) as training targets.
- Next.js UI, FastAPI inference endpoint changes, or wiring the classifier into the web prediction path.
- RAG / LLM agent adaptation and Sprint 1 PDF packaging.
- Retraining or replacing the HU-06 `pipeline.joblib` contract outside the baseline training flow.

## Capabilities

> Contract for the specs phase. Names researched against `openspec/specs/`.

### New Capabilities
- `baseline-model-training`: Stratified 75/25 preparation, baseline classifier training with the HU-06 pipeline, test-set prediction, model serialization to `artifacts/modelo.joblib`, and comparative metrics reporting in `reports/model_baseline.md`.

### Modified Capabilities
- `ml-pipeline`: Extend application/CLI/path contracts so a training use case can load processed data, reuse the transformation pipeline, persist `modelo.joblib`, and write the baseline metrics report without embedding training logic in CLI handlers.

## Approach

Reuse the existing Clean Architecture layout in `ml_service/`:

1. Call the existing `split_dataset()` helper with `test_size=0.25` and a fixed `random_state` (default 42). The current helper default is 0.20 for HU-06 transform fitting; HU-08 must pass 0.25 explicitly rather than silently changing unrelated transform defaults without a deliberate decision in design/tasks.
2. Fit the HU-06 transformation pipeline on the training partition only, transform train and test features, then train logistic regression and random forest with the parameters already anticipated in `entrega_sprint1/05_entrenamiento/config_entrenamiento.json`.
3. Evaluate both models on the test set, select the serialized baseline by primary metric F1 with recall as tie-breaker (documented in that config), and persist the chosen estimator to `ml_service/artifacts/modelo.joblib` via the existing joblib storage adapter pattern.
4. Write `reports/model_baseline.md` with the required comparative metrics table and run provenance (seed, split sizes, stratification flag, selected model).
5. Expose a modular CLI subcommand (for example `train`) that delegates to an application service under `ml_service/src/application/`, keeping I/O and path resolution in infrastructure.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `ml_service/src/application/` | New/Modified | Training use case; may extend `dataset_split` usage for the 75/25 HU-08 contract |
| `ml_service/src/domain/` | Modified | Optional result models for training metrics and selection metadata |
| `ml_service/src/infrastructure/paths.py` | Modified | Paths for `modelo.joblib` and `reports/model_baseline.md` |
| `ml_service/src/infrastructure/storage.py` / reporting | Modified | Persist classifier artifact and render the baseline metrics Markdown report |
| `ml_service/src/interfaces/cli/` | Modified | Add training subcommand and thin command handler |
| `ml_service/artifacts/modelo.joblib` | New | Serialized selected baseline classifier |
| `reports/model_baseline.md` | New | Comparative metrics report for the two baselines |
| `ml_service/tests/` | New/Modified | Cover split, training, serialization, and report contracts |
| `openspec/specs/ml-pipeline` | Modified | Delta requirements for training orchestration |
| `openspec/specs/baseline-model-training` | New | Full capability spec created at archive from this change |
| `entrega_sprint1/05_entrenamiento/` | Modified if required | Align delivery docs/config evidence with executed HU-08 artifacts (no canonical data mutation) |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Data leakage if the HU-06 pipeline is fitted on the full dataset before the 75/25 split | High | Fit/transform only after split; fit preprocessor on train; transform test separately |
| Changing `split_dataset` default from 0.20 to 0.25 breaks HU-06 transform tests/behavior | Med | Prefer explicit `test_size=0.25` for HU-08; only change the shared default if design proves no consumer relies on 0.20 |
| Severe class imbalance makes accuracy misleading | High | Report precision, recall, F1, and ROC-AUC; select by F1 with recall tie-breaker; keep stratification mandatory when feasible |
| Serializing both models under one filename creates ambiguity | Med | Persist only the selected model as `modelo.joblib`; name the selected estimator and both score rows in the report |
| Path helper writes outside intended directories when run without explicit args | Low | Follow existing CLI path patterns; document working directory and default artifact paths |

## Rollback Plan

- Delete generated artifacts `ml_service/artifacts/modelo.joblib` and `reports/model_baseline.md` if the run is invalid.
- Revert code changes under `ml_service/src/` and `ml_service/tests/` via git.
- Leave canonical `data/raw/ai4i2020.csv`, processed CSVs, and `pipeline.joblib` untouched by rollback of training outputs.
- If a delivery-doc sync was included, restore previous Markdown/JSON under `entrega_sprint1/05_entrenamiento/` without altering canonical sources.

## Dependencies

- Completed HU-06 transformation pipeline (`ml_service/artifacts/pipeline.joblib` contract and feature definitions).
- Processed training source available (outlier-analyzed or equivalent documented input expected by the training config).
- Existing `split_dataset()` helper and joblib storage adapter.
- scikit-learn / pandas environment already declared in `ml_service/requirements.txt`.

## Success Criteria

- [ ] Dataset is split 75% train / 25% test with stratification when class imbalance allows, using a documented random seed.
- [ ] At least one classifier trains successfully using the HU-06 transformation pipeline fitted only on the training partition; the deliverable comparison covers both planned baselines.
- [ ] Initial predictions are produced on the test set.
- [ ] `ml_service/artifacts/modelo.joblib` exists, loads, and corresponds to the selected trained classifier.
- [ ] `reports/model_baseline.md` contains a comparative table of accuracy, precision, recall, F1, and ROC-AUC for both models.
- [ ] Training CLI/use case exits 0 on the happy path and records enough provenance for later evaluation.
- [ ] Focused tests covering split reproducibility and artifact/report generation pass.
