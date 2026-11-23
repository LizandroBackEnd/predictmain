# Verify Report: train-baseline-model

**Change**: `train-baseline-model` (HU-08)
**Date**: 2026-11-23
**Mode**: Standard (`strict_tdd: false`)
**Artifact store**: openspec
**Scope inspected**: `openspec/changes/train-baseline-model/` artifacts, `ml_service/` HU-08 implementation, generated `modelo.joblib` / `model_baseline.md`

## Observed Progress

| Item | Observation |
|------|-------------|
| Tasks (`tasks.md`) | **18/18** checked `[x]`; **0** unfinished |
| Apply progress | Reports 18/18 complete; focused suite 15 OK; runtime train exit 0 |
| Proposal / design / specs | Present (`proposal.md`, `design.md`, delta specs for `baseline-model-training` and `ml-pipeline`) |
| Main specs | `openspec/specs/ml-pipeline/spec.md` exists; `openspec/specs/baseline-model-training/` not yet created (expected until archive sync) |

Task checkboxes were **not** rewritten during verify.

## Checks Executed

| Check | Command / action | Exit / result |
|-------|------------------|---------------|
| Focused unit suite | `cd ml_service && .venv/bin/python -m unittest tests.test_baseline_training tests.test_cli_train tests.test_dataset_split -v` | **0** — 15 tests, OK (~2.05s) |
| Artifact presence | `ls` on `ml_service/artifacts/modelo.joblib` and `reports/model_baseline.md` | Both present (mtime 2026-11-22 / UTC 2026-11-23 01:04:20) |
| Report content (static) | Read `reports/model_baseline.md` | Contains Accuracy/Precision/Recall/F1/ROC-AUC for both models; seed 42; 75%/25% stratified; 7500/2500; selected `random_forest` |
| Model load | `joblib.load(artifacts/modelo.joblib)` with `PYTHONPATH=ml_service` | sklearn `Pipeline` with steps `preprocess`, `classifier`; has `predict` / `predict_proba` |
| Split default intact | Grep/read `DEFAULT_TEST_SIZE` in `dataset_split.py` | Remains **0.2**; HU-08 uses explicit `HU08_TEST_SIZE` / seed in `baseline_training.py` |
| Pipeline artifact | `sha256sum` on `pipeline.joblib` | Present; not removed by training (hash recorded: `14bc2c78…084820c1`) |

## Checks Skipped / Unavailable

| Check | Reason |
|-------|--------|
| `bun run build` (`openspec/config.yaml` `rules.verify.build_command`) | Skipped — change is Python/`ml_service` only; Next.js build is out of HU-08 verification scope |
| Full CLI retrain (`python -m src.cli train`) | Not re-executed this verify; relied on existing artifacts + unit/CLI tests. User stated all tasks were already proven |
| Engram mirror of verify-report | Engram MCP namespace still loading / unavailable this session |
| `gentle-ai sdd-status` | CLI present (v4.3.1) but `sdd-status` command unknown — structured status taken from openspec filesystem |

## Spec / Design Alignment (Runtime + Static)

| Requirement area | Verdict | Evidence |
|------------------|---------|----------|
| Stratified 75/25, seed 42 | Met (tests + report) | Unit tests for reproducibility/stratification; report shows 7500/2500 stratified, `random_state` 42 |
| Non-stratified fallback | Met (tests) | `test_single_class_falls_back_without_stratification` |
| Fit transform on train only | Met (tests) | `test_pipeline_fitted_only_on_train` |
| Missing/empty CSV fails without model | Met (tests) | Service + CLI tests exit/fail without writing success artifact |
| LR + RF with required hyperparams | Met (static + tests) | `baseline_training.py`: balanced LR `max_iter=1000`; RF `n_estimators=300`, `random_state=42` |
| F1 then recall selection | Met (tests + report) | Selection test + report selected `random_forest` (higher F1) |
| `modelo.joblib` loadable | Met (runtime load) | Composite Pipeline load succeeded |
| `model_baseline.md` metrics + provenance | Met (static read) | Required columns and provenance fields present |
| Use case under `application/`, I/O in infrastructure, thin CLI | Met (static) | `BaselineTrainingService`, `build_model_baseline_report`, `run_train_cmd` / entrypoint `train` |
| `DEFAULT_TEST_SIZE` unchanged at 0.20 | Met | Value still `0.2` |

## Findings

1. **No blocking requirement gaps observed** against available HU-08 specs for the checks that ran.
2. **Informational**: `all` CLI orchestration still stops at `validate` and does not invoke `train`. Specs for HU-08 define the `train` use case / command; they do not require folding `train` into `all`. Documented pipeline behavior matches implementation.
3. **Informational**: Main-spec sync for new domain `baseline-model-training` and delta updates to `ml-pipeline` remain for **archive**.

## Historical Context

- Prior `apply-progress.md` (apply-time): 18/18 tasks, 15 tests OK, train exit 0, selected `random_forest`.
- This verify re-ran the focused suite (still 15 OK) and re-inspected artifacts; did not contradict apply-time completion claims.

## Summary

- **Verified**: Focused HU-08/HU-06-split unit suites pass; baseline artifacts exist and match report provenance; model artifact loads; split default 0.20 preserved.
- **Not certified by this run**: Next.js production build; a fresh end-to-end `cli train` against the full CSV.
- **Recommended next**: `sdd-archive` (sync delta specs → main specs, move change to `openspec/changes/archive/YYYY-MM-DD-train-baseline-model/`).

## Verdict

Diagnostic status: **success** (implementation complete per tasks; practical checks that ran passed; skipped checks disclosed). Verification is optional and does not certify archive by itself.
