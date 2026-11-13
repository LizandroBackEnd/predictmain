# Proposal: Reconcile Sprint 1 Deliverables

## Intent

Align `entrega_sprint1/` with the current PredictMain source of truth and the Sprint 1 evaluation requirements. The delivery folder already contains most requested artifacts, but its duplicated dataset, ML service code, serialized pipeline, manifests, and profiling outputs diverge from the project-level versions. The change will make the submission reproducible, traceable, and complete without altering the immutable original sources.

## Scope

### In Scope

- Update the Sprint 1 project vision document so it accurately reflects the current repository architecture, data pipeline state, and explicitly requested deliverables.
- Reconcile the corpus deliverables: preserve the original PDF, document provenance and structure, retain cleaned/processed outputs, improve Python scripts with clear comments and reproducible execution, and consolidate quality-validation evidence.
- Reconcile the dataset deliverables: copy the canonical raw/processed data and ML pipeline sources into the expected delivery folders, document nulls, duplicates, inconsistencies, outliers, normalization, and validation decisions, and provide comparative and execution evidence.
- Complete the labeling package with catalog, assignment rules, labeled samples/data, consistency validation, and commented reproducible scripts.
- Validate and align the training/rules package, including objective, strategy, system prompt, query/response rules, source criteria, and corpus/dataset usage boundaries.
- Produce or update the requested Markdown documentation, leaving the later PDF export to the user.

### Out of Scope

- Implementing the production RAG assistant, embeddings, vector database integration, or final LLM fine-tuning.
- Training or deploying a new production predictive model beyond the reproducible Sprint 1 preparation and documented training configuration.
- Changing the canonical raw AI4I dataset or the original corpus PDF.
- Refactoring unrelated Next.js application features or changing public application APIs.

## Capabilities

### New Capabilities

- `sprint1-deliverable-reconciliation`: A reproducible and traceable Sprint 1 submission package containing synchronized corpus, dataset, labeling, and training artifacts.
- `corpus-preparation-evidence`: Documented corpus provenance, structure, cleaning/normalization, deduplication, quality criteria, processed output, and execution evidence.
- `dataset-preparation-evidence`: Documented dataset cleaning, transformation, outlier/null/duplicate handling, validation, comparison, and reproducible execution evidence.
- `labeling-and-llm-rules-package`: A validated labeling package and a documented set of model-training, RAG, system-prompt, and query/response rules.

### Modified Capabilities

- `dataset-ingestion`: The delivery package must expose the same immutable raw dataset, manifest, and integrity metadata as the canonical project pipeline.
- `ml-pipeline`: The delivery package must contain the current reproducible Python pipeline sources and artifacts, with documentation and evidence matching the implemented behavior.

## Approach

Use the project-level `data/` and `ml_service/` implementations as the canonical source, compare them against the copies under `entrega_sprint1/03_dataset/`, and synchronize only the delivery copies after validating hashes, schemas, row counts, and generated outputs. Review each requested rubric item against the existing Sprint 1 folders, add missing documentation or evidence, and update Python scripts with concise English comments only where the processing logic is non-obvious. Keep the original corpus and raw dataset immutable, record provenance and checksums, and leave the final PDF export to the user after validating the Markdown sources.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `entrega_sprint1/01_vision/vision_proyecto.md` | Modified | Update project vision, scope, status, and traceability to the current implementation. |
| `entrega_sprint1/02_corpus/` | Modified | Align source metadata, processing scripts, outputs, validation criteria, evidence, and Markdown documentation. |
| `entrega_sprint1/03_dataset/` | Modified | Synchronize canonical data and ML pipeline copies; complete processing documentation, comparisons, logs, and reports. |
| `entrega_sprint1/04_etiquetado/` | Modified | Validate labeled data, catalog, rules, sample, and commented scripts. |
| `entrega_sprint1/05_entrenamiento/` | Modified | Align training configuration, RAG strategy, source criteria, system prompt, and response rules. |
| `data/` | Read-only source | Provide canonical dataset and profiling inputs; raw data remains immutable. |
| `ml_service/` | Read-only source | Provide canonical Python pipeline implementation and serialized artifact metadata. |
| `docs/` | Modified if required | Supply or update supporting documentation for the Markdown delivery package. |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Delivery copies remain inconsistent with canonical data or code | Medium | Add checksum/schema/row-count checks and compare generated outputs before finalizing. |
| Evidence claims results that are not reproducible from the included scripts | Medium | Re-run the documented commands from a clean working directory and retain logs with timestamps and inputs. |
| Markdown package is incomplete for later PDF export | Low | Validate required headings, evidence references, and source traceability before handoff. |
| A synchronization step accidentally modifies an immutable raw source | Low | Treat canonical raw files and the original corpus PDF as read-only and verify their hashes before and after processing. |

## Rollback Plan

Revert the proposal's implementation commit(s) to restore the previous `entrega_sprint1/` contents. If generated evidence or PDFs need to be discarded independently, remove only the newly generated files from their explicitly documented delivery paths. Restore any synchronized delivery copy from its prior Git version; never restore by modifying `data/raw/ai4i2020.csv` or the original corpus PDF.

## Dependencies

- Canonical project files in `data/` and `ml_service/`.
- Python dependencies declared by `entrega_sprint1/02_corpus/requirements.txt` and `ml_service/requirements.txt`.
- No PDF generation dependency; the user will export the validated Markdown package later.
- Existing OpenSpec capabilities for dataset ingestion and ML pipeline behavior.

## Success Criteria

- [ ] Every requested Sprint 1 rubric item is mapped to a file, script, output, evidence record, or documented justified omission.
- [ ] Delivery copies of the raw dataset, processed datasets, manifests, ML source files, and serialized pipeline are synchronized with the canonical project sources and verified by hashes or structural checks.
- [ ] Corpus and dataset scripts execute successfully from the documented location and produce the included outputs and evidence without modifying immutable originals.
- [ ] The final package includes documented provenance, structure, quality criteria, cleaning decisions, transformations, labeling rules, training strategy, system prompt, and source-use rules.
- [ ] The Markdown package contains the final vision and required technical documentation and can be traced back to its evidence sources.
