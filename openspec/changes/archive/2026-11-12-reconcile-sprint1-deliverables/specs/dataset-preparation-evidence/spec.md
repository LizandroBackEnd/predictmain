# Dataset Preparation Evidence Specification

## Purpose

Defines evidence requirements for cleaning, transforming, validating, and comparing the AI4I 2020 dataset in the Sprint 1 submission.

## Requirements

### Requirement: Dataset Processing Decisions

The dataset package MUST document treatment of null values, duplicate records, inconsistent values, outliers, categorical variables, derived variables, normalization, and target labels, including justification for each decision.

#### Scenario: Processing decision is applied

- GIVEN a cleaning or transformation rule is documented
- WHEN the corresponding pipeline executes
- THEN the output MUST reflect the rule
- AND the evidence MUST report the affected rows, columns, or distributions when measurable.

#### Scenario: No issue is found

- GIVEN a quality check finds no nulls, duplicates, or invalid categories
- WHEN the validation report is generated
- THEN the report MUST state that the check was executed and found zero affected records
- AND MUST distinguish zero findings from a skipped check.

### Requirement: Processed Dataset Validation

The delivery package MUST validate the processed dataset's schema, row count, target distribution, expected categories, and transformation outputs.

#### Scenario: Valid processed dataset

- GIVEN synchronized processed files are available
- WHEN validation runs
- THEN it MUST verify expected schemas and row counts
- AND MUST produce a successful validation record with the input and output paths.

#### Scenario: Validation mismatch

- GIVEN a processed file has an unexpected schema, row count, category, or target distribution
- WHEN validation runs
- THEN it MUST fail explicitly
- AND MUST identify the mismatched property without silently repairing the file.

### Requirement: Original-versus-Processed Comparison

The dataset evidence MUST provide a reproducible comparison between original and processed data, including dimensions, quality findings, changed columns, and representative values or distributions.

#### Scenario: Comparison generated

- GIVEN original and processed datasets are readable
- WHEN the comparison script runs
- THEN it MUST generate a report with measurable differences and processing-stage references
- AND the report MUST identify which changes were intentional.

#### Scenario: Comparison inputs are missing

- GIVEN either comparison input is missing or unreadable
- WHEN the comparison script runs
- THEN it MUST fail with the missing input path
- AND MUST NOT generate an incomplete success report.
