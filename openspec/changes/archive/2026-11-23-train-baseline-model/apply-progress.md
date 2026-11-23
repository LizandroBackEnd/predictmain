# Apply Progress: train-baseline-model

**Mode**: Standard (`strict_tdd: false`)
**Workload**: size:exception (user-approved 2026-11-22)
**Status**: 18/18 tasks complete

## Work Unit Evidence

| Evidence | Result |
|---|---|
| Focused test command | `cd ml_service && .venv/bin/python -m unittest tests.test_baseline_training tests.test_cli_train tests.test_dataset_split -v` → 15 tests, OK |
| Runtime harness | `cd ml_service && .venv/bin/python -m src.cli train --csv ../data/processed/ai4i2020_outlier_analyzed.csv --model artifacts/modelo.joblib --report ../reports/model_baseline.md` → exit 0; selected `random_forest`; 7500/2500 stratified split |
| Rollback boundary | HU-08 code under `ml_service/src/` + tests; generated `ml_service/artifacts/modelo.joblib` and `reports/model_baseline.md`; delivery status updates under `entrega_sprint1/05_entrenamiento/` |

## Completed Tasks

All Phase 1–5 tasks marked `[x]` in `tasks.md`.

## Notes

- `DEFAULT_TEST_SIZE` remains `0.2`; HU-08 passes `test_size=0.25` explicitly.
- HU-06 `artifacts/pipeline.joblib` SHA-256 unchanged after training.
- `modelo.joblib` stores a composite sklearn `Pipeline` (`preprocess` + selected classifier).
