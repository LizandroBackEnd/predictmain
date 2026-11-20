# Tasks: Reconcile Sprint 1 Deliverables

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 500–900 authored lines, excluding generated CSV artifacts |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Optional review slices remain phases 1–2, 3, and 4–6, but the user approved one implementation change on the current branch |
| Delivery strategy | exception-ok |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: size-exception
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Delivery slice | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Align vision and produce corpus preparation evidence | Single change | `python entrega_sprint1/02_corpus/scripts/limpieza_normalizacion.py` and `python entrega_sprint1/02_corpus/scripts/depuracion_calidad.py` | Run both scripts from the documented delivery root against a copied fixture; verify generated reports and immutable PDF hash | `entrega_sprint1/01_vision/` and `entrega_sprint1/02_corpus/` only |
| 2 | Synchronize dataset/ML copies and validate processing evidence | Single change | `python -m src.cli ingest` plus delivery validation scripts | Run reconciliation from a clean temporary working directory and load `pipeline.joblib` | `entrega_sprint1/03_dataset/` only |
| 3 | Validate labels, training rules, and final package | Single change | `python entrega_sprint1/04_etiquetado/scripts/validar_etiquetas.py` | Run label validation and inspect required Markdown headings | `entrega_sprint1/04_etiquetado/` and `entrega_sprint1/05_entrenamiento/` only |

## Phase 1: Baseline and Immutable Source Verification

- [x] 1.1 Record baseline SHA-256, schemas, row counts, and file inventory for `data/` (read-only) and `ml_service/` (read-only) without editing canonical files.
- [x] 1.2 Verify the original PDF checksum and metadata in `entrega_sprint1/02_corpus/corpus_original/` (read-only), then record any provenance failure in `entrega_sprint1/02_corpus/evidencias/`.
- [x] 1.3 Create a rubric traceability matrix in `entrega_sprint1/01_vision/` mapping each requested deliverable to its file, script, output, evidence, and status.

## Phase 2: Corpus and Vision Deliverables

- [x] 2.1 Update `entrega_sprint1/01_vision/vision_proyecto.md` to reflect the current repository architecture, Sprint 1 state, and traceability matrix.
- [x] 2.2 Review and correct `entrega_sprint1/02_corpus/documentacion/corpus_original.md`, `entrega_sprint1/02_corpus/documentacion/estructura_corpus.md`, and `entrega_sprint1/02_corpus/documentacion/criterios_calidad.md` so provenance, format, structure, quality criteria, and limitations agree with generated evidence.
- [x] 2.3 Add concise comments and explicit input/output validation to `entrega_sprint1/02_corpus/scripts/limpieza_normalizacion.py` without changing the immutable PDF or the intended normalization rules.
- [x] 2.4 Add concise comments and deterministic duplicate/quality checks to `entrega_sprint1/02_corpus/scripts/depuracion_calidad.py`.
- [x] 2.5 Run both corpus scripts and regenerate `entrega_sprint1/02_corpus/salidas/` and `entrega_sprint1/02_corpus/evidencias/`, recording command, timestamp, input hash, output paths, and validation status.
- [x] 2.6 Verify corpus scenarios from `corpus-preparation-evidence/spec.md` (read-only): missing/unreadable PDF fails explicitly; valid output contains no prohibited page markers or decorative noise; duplicate and quality metrics are reported.

## Phase 3: Dataset and ML Synchronization

- [x] 3.1 Synchronize canonical raw/processed/profiling files from `data/` (read-only) into `entrega_sprint1/03_dataset/data/`, preserving the canonical raw CSV and manifest metadata.
- [x] 3.2 Synchronize canonical Python sources from `ml_service/src/` (read-only), `ml_service/requirements.txt` (read-only), and the loadable pipeline artifact from `ml_service/artifacts/` (read-only) into `entrega_sprint1/03_dataset/ml_service/`.
- [x] 3.3 Add or update the delivery reconciliation check for `entrega_sprint1/03_dataset/data/raw/manifest.json`, including SHA-256, dimensions, columns, and explicit stale-copy failures.
- [x] 3.4 Update `entrega_sprint1/03_dataset/documentacion/limpieza_transformacion.md` with null, duplicate, inconsistency, outlier, normalization, derived-feature, and target-label decisions plus their justifications.
- [x] 3.5 Update `entrega_sprint1/03_dataset/scripts_evidencia/validar_dataset_procesado.py` to validate schema, row count, categories, target distribution, and generated outputs without silently repairing mismatches.
- [x] 3.6 Update `entrega_sprint1/03_dataset/scripts_evidencia/comparar_datasets.py` to report dimensions, quality differences, changed columns, representative values/distributions, and intentional changes.
- [x] 3.7 Run the documented ML pipeline and evidence scripts from a clean temporary working directory, then regenerate `entrega_sprint1/03_dataset/evidencias/`, `entrega_sprint1/03_dataset/reports/`, and profiling evidence.
- [x] 3.8 Verify scenarios from `dataset-ingestion/spec.md` (read-only), `dataset-preparation-evidence/spec.md` (read-only), and `ml-pipeline/spec.md` (read-only): valid synchronized files pass; missing inputs, stale hashes, schema/row/category mismatches, and pipeline-copy drift fail explicitly; comparison output is reproducible.

## Phase 4: Labeling and Training Rules

- [x] 4.1 Review `entrega_sprint1/04_etiquetado/catalogo_etiquetas.md`, `entrega_sprint1/04_etiquetado/reglas_etiquetado.md`, and `entrega_sprint1/04_etiquetado/validacion_etiquetado.md` for complete taxonomy, criteria, constraints, and consistency rules.
- [x] 4.2 Add concise comments and deterministic selection behavior to `entrega_sprint1/04_etiquetado/scripts/generar_muestra_etiquetada.py`.
- [x] 4.3 Add explicit invalid-label and conflicting-label failures to `entrega_sprint1/04_etiquetado/scripts/validar_etiquetas.py`.
- [x] 4.4 Run label validation and sample generation, then update `entrega_sprint1/04_etiquetado/muestra_etiquetada.md` and `entrega_sprint1/04_etiquetado/evidencias/validacion_etiquetado.log`.
- [x] 4.5 Review `entrega_sprint1/05_entrenamiento/objetivo_modelo.md`, `estrategia_entrenamiento.md`, `config_entrenamiento.json`, `reglas_parametros_entrenamiento.md`, `reglas_consulta_respuesta.md`, `system_prompt.md`, `criterios_fuentes.md`, and `dataset_entrenamiento.md` for consistent objectives, strategy, parameters, source boundaries, citations, abstention, and escalation rules; verify the complete-rules and insufficient-evidence scenarios from `labeling-and-llm-rules-package/spec.md` (read-only).

## Phase 5: Final Evidence and Markdown Acceptance

- [x] 5.1 Build a final cross-package checklist covering every requested corpus, dataset, labeling, training, evidence, and documentation item.
- [x] 5.2 Verify the final Markdown sources contain the required vision and technical documentation sections and identify their evidence sources.
- [x] 5.3 Confirm the Markdown package is ready for the user's later PDF export without generated PDF files in this change.
- [x] 5.4 Run final hash/schema/row-count checks and confirm canonical raw inputs and original corpus PDF are unchanged.
- [x] 5.5 Record final pass, fail, skipped, and deferred checks in the delivery evidence and update this task file with observed completion evidence.

## Phase 6: Review and Cleanup

- [x] 6.1 Remove only temporary caches or scratch outputs created inside authorized delivery directories; retain reproducibility logs and final evidence.
- [x] 6.2 Run `bun run lint` and `bunx tsc --noEmit` to confirm the unrelated web application remains unaffected.
- [x] 6.3 Review the final diff for accidental edits outside `entrega_sprint1/`, permitted documentation, and OpenSpec artifacts.

## Completion Evidence

Recorded in `entrega_sprint1/01_vision/evidencias/verificacion_final_entrega.md` (2026-11-13 UTC).

- Corpus: 11/11 quality checks; missing and unreadable PDF fail with the file path; a defective corpus exits 1 naming the failed criteria.
- Dataset: new `scripts_evidencia/reconciliar_entrega.py` passes 36/36 and fails on manifest-field, stale-hash, missing-file, stale-source, and corrupt-artifact cases; validation 36/36; comparison reproducible across runs.
- Pipeline: five CLI stages rerun in a clean temporary copy with exit 0; CSVs, manifest, and `pipeline.joblib` byte-identical to the delivery copy.
- Labeling: 23/23 checks; out-of-catalog, conflicting, and untraceable sample records fail with `UDI`, column, and value; no coercion.
- Hash conflicts resolved: delivery CSV `dc6630cd...` and config corpus hash `9CD37B95...` were CRLF variants of the LF canonical files.
- Canonical `data/`, `ml_service/`, and the original PDF unchanged versus HEAD; no PDFs generated.
- `bun run lint` (0 errors) and `bunx tsc --noEmit` pass.
- Not run: `ml_service/tests/` (pytest is not in the requirements; the canonical code was not modified).
