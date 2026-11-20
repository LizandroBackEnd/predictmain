# Design: Reconcile Sprint 1 Deliverables

## Technical Approach

Treat The project-level `data/` and `ml_service/` trees as read-only canonical sources and make `entrega_sprint1/` a reproducible submission projection. The implementation will first inventory the requested rubric items, then synchronize only verified source copies, run the corpus/dataset/label validation scripts from documented working directories, capture checksums and execution logs, and update the Markdown documentation that the user will later export to PDF.

The design preserves the current hybrid architecture: the change affects delivery evidence and documentation, not the Next.js application, ML service boundaries, or production RAG behavior. Existing ingestion and pipeline contracts remain authoritative; delivery-specific capabilities add traceability around them.

## Architecture Decisions

### Decision: Canonical source remains outside the delivery folder

**Choice**: Read canonical files from `data/` and `ml_service/`; copy verified versions into `entrega_sprint1/03_dataset/`.
**Alternatives considered**: Make `entrega_sprint1/` the source of truth; maintain two independently editable implementations.
**Rationale**: Independent copies already diverge. One canonical source prevents the submission from documenting or shipping behavior that differs from the project.

### Decision: Preserve immutable inputs

**Choice**: Never transform `data/raw/ai4i2020.csv` or `entrega_sprint1/02_corpus/corpus_original/PredictMain_Corpus_Contenido.pdf` in place.
**Alternatives considered**: Normalize inputs directly; replace originals with processed files.
**Rationale**: Provenance, checksum verification, and auditability require original inputs to remain recoverable and byte-stable.

### Decision: Evidence is generated beside the delivery artifacts

**Choice**: Keep scripts, outputs, reports, logs, comparisons, and validation notes within their existing `entrega_sprint1/02_corpus` through `05_entrenamiento` structure.
**Alternatives considered**: Put all evidence under a new global reports directory; rely only on root project reports.
**Rationale**: The existing folder structure is already aligned with the rubric and is easier to review as a self-contained submission.

### Decision: Documentation is the contract for non-code decisions

**Choice**: Record cleaning, outlier, labeling, source-selection, RAG, and system-prompt rules in Markdown and leave PDF export to the user.
**Alternatives considered**: Generate a PDF during this change; provide only a PDF.
**Rationale**: Markdown is diffable and reproducible, while the user will handle the final presentation export separately.

## Data Flow

```text
Canonical data/ + ml_service/
        │
        ├── hash/schema/row-count verification
        │
        ▼
entrega_sprint1/03_dataset/ synchronized copies
        │
        ├── validation and comparison scripts
        ├── execution logs and reports
        └── documented decisions

Original corpus PDF ──→ extraction ──→ normalization ──→ deduplication
       │                                      │
       └──────── checksum/provenance ────────┴──→ processed corpus + evidence

Labeled data + rules ──→ consistency validation ──→ sample and validation evidence

Vision + corpus + dataset + rules ──→ final Markdown sources ──→ user-managed PDF export
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `entrega_sprint1/01_vision/vision_proyecto.md` | Modify | Align vision, scope, status, and deliverable traceability with the current project. |
| `entrega_sprint1/02_corpus/documentacion/*.md` | Modify | Ensure provenance, structure, and quality criteria are complete and consistent. |
| `entrega_sprint1/02_corpus/scripts/*.py` | Modify | Preserve the existing extraction/cleaning behavior and add concise comments, deterministic checks, and documented execution paths where needed. |
| `entrega_sprint1/02_corpus/evidencias/*` | Regenerate/Modify | Capture reproducible execution, cleaning, deduplication, and quality evidence. |
| `entrega_sprint1/02_corpus/salidas/*` | Regenerate | Rebuild derived corpus outputs from the immutable PDF. |
| `entrega_sprint1/03_dataset/data/*` | Synchronize | Copy verified canonical raw/processed/profiling data and manifest metadata. |
| `entrega_sprint1/03_dataset/ml_service/*` | Synchronize | Copy verified ML source files, requirements, and pipeline artifact metadata. |
| `entrega_sprint1/03_dataset/documentacion/*` | Modify | Document null, duplicate, inconsistency, outlier, normalization, and transformation decisions. |
| `entrega_sprint1/03_dataset/scripts_evidencia/*` | Modify | Validate synchronized data and generate comparisons/evidence. |
| `entrega_sprint1/03_dataset/evidencias/*` | Regenerate/Modify | Record execution, validation, and original-versus-processed comparisons. |
| `entrega_sprint1/04_etiquetado/*` | Modify/Regenerate | Validate catalog, rules, labeled data, samples, and consistency evidence. |
| `entrega_sprint1/05_entrenamiento/*` | Modify | Align model objective, strategy, source criteria, system prompt, and query/response rules. |
| `docs/` | Modify if required | Update supporting source documentation when required by the delivery package. |

## Interfaces / Contracts

### Delivery synchronization contract

The synchronized dataset package MUST preserve:

```text
raw rows = 10,000
raw columns = 14
raw SHA-256 = canonical manifest SHA-256
processed outputs = canonical filenames and schemas
pipeline artifact = loadable by the documented Python environment
```

### Evidence contract

Each processing stage MUST identify:

- input path and immutable-source status;
- command or script used;
- output paths;
- row/column counts and relevant quality metrics;
- validation result and timestamp;
- limitations or unresolved findings.

### Markdown handoff contract

The final delivery MUST keep the vision and requested technical documentation in complete Markdown sources, with headings and source references suitable for the user's later PDF export.

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit | Corpus normalization, deduplication, label consistency, dataset validation | Run the existing Python scripts with controlled fixtures or copied inputs outside canonical paths. |
| Integration | Canonical-to-delivery synchronization | Compare SHA-256, schemas, row counts, manifests, and pipeline loadability. |
| Evidence | Reproducible execution logs and comparisons | Run documented corpus, dataset, and labeling commands from clean temporary working directories and inspect generated reports. |
| Markdown acceptance | Required sections and traceability | Verify the Markdown contains required headings, evidence references, and source traceability. |

## Threat Matrix

N/A — this change does not add or modify routing, shell-command construction, subprocess invocation, VCS/PR automation, executable-file classification, or process-integration boundaries. Existing Python scripts are invoked as documented validation entry points; no new process boundary or command interpolation is introduced.

## Migration / Rollout

No database migration or production rollout is required. Apply in this order: synchronize canonical copies, regenerate evidence, update documentation, validate the Markdown handoff, then review the complete delivery tree. Rollback is limited to the changed delivery files and generated evidence; canonical immutable inputs remain untouched.

## Open Questions

- [x] PDF generation is intentionally deferred to the user; this change produces and validates Markdown sources only.
