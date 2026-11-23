# Design: Train Baseline Failure-Risk Classifier (HU-08)

## Technical Approach

Implement HU-08 inside the existing `ml_service` Clean Architecture. Reuse `split_dataset()`, `TransformationService`, joblib storage, Markdown reporting, and the modular CLI. A new application service orchestrates: load processed labeled CSV → 75/25 stratified split with seed 42 → fit HU-06 pipeline on train only → train logistic regression and random forest → score the same test set → select by F1 (recall tie-breaker) → persist `modelo.joblib` → write `reports/model_baseline.md`.

This maps directly to the proposal and to `baseline-model-training` plus the `ml-pipeline` delta (REQ-07 and updated path/CLI contracts).

## Architecture Decisions

### Decision: Keep training orchestration in `application/`, not `src/training/`

**Choice**: Add `ml_service/src/application/baseline_training.py` (or equivalent) as a use-case service.
**Alternatives considered**: Populate the empty `ml_service/src/training/` package; put training logic in CLI commands.
**Rationale**: Current HUs live under `application/` with thin CLI handlers. An empty `training/` directory would introduce a second convention without benefit.

### Decision: Pass `test_size=0.25` explicitly; do not change the shared default

**Choice**: Call `split_dataset(..., test_size=0.25, random_state=42)` from the training use case.
**Alternatives considered**: Change `DEFAULT_TEST_SIZE` from 0.20 to 0.25 globally.
**Rationale**: Existing HU-06 tests assert the 80/20 default. Changing it would break unrelated transform-fitting behavior. HU-08 needs an explicit contract, not a silent default swap.

### Decision: Refit the HU-06 pipeline on the training partition during HU-08

**Choice**: Instantiate/fit `TransformationService` on training features only, then `transform` train and test.
**Alternatives considered**: Load the existing `pipeline.joblib` fitted on a previous partition; transform the already-written `ai4i2020_transformed.csv` and split after scaling.
**Rationale**: Delivery config and HU-06 reports already require anti-leakage. Fitting after the HU-08 split is the only safe baseline. The stored `pipeline.joblib` remains the HU-06 artifact; HU-08 may keep a fitted preprocessor in memory (and optionally beside the classifier later) without overwriting the HU-06 contract unless explicitly designed later.

### Decision: Serialize only the selected classifier as `modelo.joblib`

**Choice**: Persist one selected estimator (or a thin wrapper that applies the fitted preprocessor + classifier if needed for inference). Prefer a joblib payload that can predict from the same feature matrix the training flow produced after transformation.
**Alternatives considered**: Save both models; overwrite `pipeline.joblib`; save only probabilities CSV.
**Rationale**: Acceptance deliverable names a single `artifacts/modelo.joblib`. The comparative report carries both models' metrics. Selection uses F1 then recall.

### Decision: Extend storage helper for generic estimators

**Choice**: Add estimator save/load helpers next to `save_pipeline`/`load_pipeline` in `storage.py` (or generalize the existing helpers) rather than importing `joblib` from application code.
**Alternatives considered**: Call `joblib.dump` inside the application service.
**Rationale**: Infrastructure already owns persistence; application must stay free of raw I/O adapters.

### Decision: Report via `reporting.py` Markdown builder

**Choice**: Add `build_model_baseline_report(...)` following `build_transformation_report` style and write through the CLI/use-case the same way other reports are written.
**Alternatives considered**: Inline Markdown strings in the application service; write CSV-only metrics.
**Rationale**: Existing HU reports are Markdown under `reports/` with provenance tables. The deliverable explicitly requires `reports/model_baseline.md`.

## Data Flow

```text
processed labeled CSV (e.g. ai4i2020_outlier_analyzed.csv)
        │
        ▼
split_dataset(test_size=0.25, random_state=42, stratify when feasible)
        │
        ├── train DF ──► TransformationService.fit_transform(X_train)
        │                         │
        │                         ▼
        │               transform X_test (no refit)
        │                         │
        └── test DF ──────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
         LogisticRegression              RandomForestClassifier
         (class_weight=balanced)         (class_weight=balanced, n_estimators=300, seed=42)
                    │                           │
                    └──────── predict_proba / predict on X_test ──┘
                                  │
                    compute accuracy, precision, recall, F1, ROC-AUC
                                  │
                    select by F1, tie-break recall
                                  │
                    ┌─────────────┴──────────────┐
                    ▼                            ▼
         artifacts/modelo.joblib        reports/model_baseline.md
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `ml_service/src/application/baseline_training.py` | Create | Training use-case orchestration |
| `ml_service/src/domain/models.py` | Modify | Add frozen result types for metrics rows and training run provenance |
| `ml_service/src/infrastructure/paths.py` | Modify | Add `model_path` (`modelo.joblib`) and `model_baseline_report_path` |
| `ml_service/src/infrastructure/storage.py` | Modify | Save/load generic estimator artifacts without leaking joblib into application |
| `ml_service/src/infrastructure/reporting.py` | Modify | Build `model_baseline.md` Markdown |
| `ml_service/src/interfaces/cli/commands.py` | Modify | Thin `run_train_cmd` handler |
| `ml_service/src/interfaces/cli/entrypoint.py` | Modify | Register `train` subcommand and route it |
| `ml_service/tests/test_baseline_training.py` | Create | Unit/integration coverage for split contract, leakage-free fit, metrics, artifacts |
| `ml_service/tests/test_cli_train.py` | Create | CLI happy-path and failure exit codes |
| `ml_service/artifacts/modelo.joblib` | Create (generated) | Selected baseline classifier artifact |
| `reports/model_baseline.md` | Create (generated) | Comparative metrics report |
| `entrega_sprint1/05_entrenamiento/*` | Modify if required | Sync status/evidence with executed HU-08 outputs after the run |

## Interfaces / Contracts

```python
@dataclass(frozen=True)
class ModelMetricRow:
    name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float

@dataclass(frozen=True)
class BaselineTrainingResult:
    source_file: str
    executed_at: str
    train_rows: int
    test_rows: int
    test_size: float
    random_state: int
    stratified: bool
    metrics: list[ModelMetricRow]
    selected_model: str
    model_path: str
    report_path: str
```

CLI contract:

```text
python -m src.cli train \
  --csv <processed-labeled-csv> \
  --model <ml_service/artifacts/modelo.joblib> \
  --report <reports/model_baseline.md>
```

Defaults resolve through `ProjectPaths`. Exit 0 on success; exit 1 on handled failures.

Selection contract: highest F1 wins; if F1 ties, higher recall wins; if still tied, prefer `random_forest` for a deterministic documented fallback.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | 75/25 proportions, seed reproducibility, stratification flag, selection by F1/recall | Extend/cover via training service tests using synthetic imbalanced frames; do not change HU-06 default-split assertions |
| Unit | Pipeline fitted only on train | Assert scaler means match train feature means, not full-data means |
| Unit | Metrics report content | Assert required columns and provenance fields exist in rendered Markdown |
| Integration | Artifact round-trip | Train on temp fixture, load `modelo.joblib`, predict on held-out rows |
| CLI | `train` success/failure | Temp workspace with fixture CSV; assert exit codes and file creation/absence |

## Threat Matrix

N/A — this change does not add or modify routing of untrusted paths beyond existing CLI `Path` arguments, shell-command construction, subprocess invocation, VCS/PR automation, executable-file classification, or process-integration boundaries. The new `train` subcommand follows the existing argparse delegation pattern.

## Migration / Rollout

No database migration or feature flag is required. Rollout is local/ML-service only:

1. Land code + tests.
2. Run `python -m src.cli train` against the documented processed CSV.
3. Commit generated `reports/model_baseline.md` if the repository tracks evidence reports; treat `modelo.joblib` per existing artifact policy (binary artifact under `ml_service/artifacts/`).
4. Optionally sync delivery training docs under `entrega_sprint1/05_entrenamiento/`.

Rollback: delete generated model/report artifacts and revert the `ml_service` code/tests. Canonical raw/processed CSVs and HU-06 `pipeline.joblib` remain untouched by training outputs.

## Open Questions

- [x] Shared `DEFAULT_TEST_SIZE` stays 0.20; HU-08 passes 0.25 explicitly.
- [x] Model selection rule: F1 primary, recall tie-breaker, deterministic fallback to `random_forest`.
- [ ] Whether `modelo.joblib` stores only the classifier (caller must transform first) or a composite preprocessor+classifier object for direct inference — finalize during apply by preferring the smallest option that can produce test predictions consistently with the report. Default recommendation: composite `{preprocessor, classifier}` or an sklearn `Pipeline` wrapping both so loading the artifact is enough to score raw feature rows used by training.
