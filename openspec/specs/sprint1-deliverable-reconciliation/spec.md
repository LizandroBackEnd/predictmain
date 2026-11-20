# Sprint 1 Deliverable Reconciliation Specification

## Purpose

Defines the behavior required for a self-contained, traceable, and reproducible Sprint 1 submission package.

## Requirements

### Requirement: Rubric Traceability

The delivery package MUST map every requested corpus, dataset, labeling, training, evidence, and documentation item to a concrete file, generated output, execution record, or justified documented omission.

#### Scenario: Complete rubric mapping

- GIVEN the Sprint 1 delivery folder is reviewed
- WHEN the traceability review is executed
- THEN every requested item SHALL have one identifiable location and an associated validation status
- AND missing or deferred items MUST include a written reason and owner of the next action.

#### Scenario: Duplicate or conflicting artifact

- GIVEN two delivery artifacts claim to represent the same source or processing stage
- WHEN their metadata or content differs
- THEN the package MUST identify the canonical artifact
- AND MUST record the conflict and resolution in the relevant evidence document.

### Requirement: Immutable Source Preservation

The delivery process MUST preserve the original AI4I CSV and original corpus PDF byte-for-byte.

#### Scenario: Processing derived outputs

- GIVEN an immutable raw dataset or original PDF
- WHEN corpus or dataset processing runs
- THEN processing MUST write derived outputs elsewhere
- AND the original file hash MUST remain unchanged.

#### Scenario: Integrity check failure

- GIVEN an original source hash differs from its recorded provenance
- WHEN packaging validation runs
- THEN validation MUST fail with an explicit integrity error
- AND MUST NOT overwrite the source or produce a success-shaped evidence report.
