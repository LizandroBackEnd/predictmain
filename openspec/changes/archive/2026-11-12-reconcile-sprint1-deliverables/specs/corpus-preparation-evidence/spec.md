# Corpus Preparation Evidence Specification

## Purpose

Defines the documented and reproducible corpus preparation package for the Sprint 1 submission.

## Requirements

### Requirement: Corpus Provenance and Structure

The corpus package MUST identify the original document's provenance, filename, format, language, size, page count, checksum, logical sections, and intended use.

#### Scenario: Original corpus documentation

- GIVEN `PredictMain_Corpus_Contenido.pdf` is present
- WHEN the corpus documentation is reviewed
- THEN provenance and format MUST be documented
- AND the structure document MUST describe physical and logical characteristics.

#### Scenario: Missing provenance metadata

- GIVEN a provenance field cannot be verified from the source
- WHEN documentation is generated
- THEN it MUST mark the field as unknown or unverified
- AND MUST NOT invent a source value.

### Requirement: Corpus Cleaning and Normalization

The corpus processing script MUST remove or normalize page markers, repeated headers, irrelevant standalone values, control characters, redundant whitespace, and line-break hyphenation while preserving meaningful Spanish text and paragraph order.

#### Scenario: Successful corpus processing

- GIVEN the original PDF is readable
- WHEN the cleaning and normalization script runs
- THEN it MUST generate extracted, structured, and cleaned outputs
- AND MUST write metrics describing the transformations performed.

#### Scenario: Unreadable or missing PDF

- GIVEN the configured PDF does not exist or cannot be read
- WHEN the script runs
- THEN it MUST fail with a descriptive error
- AND MUST NOT claim that a processed corpus was generated.

### Requirement: Corpus Deduplication and Quality Validation

The corpus package MUST remove duplicate paragraphs or repeated content according to documented criteria and MUST produce evidence for character counts, paragraph counts, section detection, prohibited noise, and remaining duplicates.

#### Scenario: Quality validation passes

- GIVEN cleaned corpus output exists
- WHEN deduplication and quality validation run
- THEN the final output MUST contain no prohibited page markers or decorative noise
- AND the evidence MUST record all validation checks and their results.

#### Scenario: Quality validation finds a defect

- GIVEN the final corpus contains duplicate content or prohibited noise
- WHEN validation runs
- THEN the result MUST identify the failed criterion and affected output
- AND MUST return a non-success status.
