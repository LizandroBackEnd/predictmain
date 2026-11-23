# Baseline Model Training Specification

## Purpose

Defines the requirements for HU-08: preparing a stratified train/test split, training baseline failure-risk classifiers with the HU-06 transformation pipeline, producing test-set predictions, serializing the selected model, and recording a comparative metrics report.

## Requirements

### Requirement: Stratified Train-Test Preparation

The training flow MUST partition the labeled dataset into 75% training and 25% test rows, MUST use a documented random seed, and MUST stratify on the binary target when class imbalance allows a valid stratified split.

#### Scenario: Successful stratified 75/25 split

- GIVEN a labeled dataset with both failure and non-failure classes and enough samples per class for stratification
- WHEN the training preparation split runs with `test_size=0.25` and a fixed random seed
- THEN approximately 75% of rows MUST be assigned to training and 25% to test
- AND the split MUST be stratified on `Machine failure`
- AND repeating the split with the same seed MUST produce identical partitions

#### Scenario: Stratification is not feasible

- GIVEN a dataset where the target has a single class or fewer than two samples in a class
- WHEN the training preparation split runs
- THEN the system MUST fall back to a non-stratified random split with the same seed and proportions
- AND MUST record that stratification was not applied

### Requirement: Baseline Classifier Training With HU-06 Pipeline

The system MUST train at least two baseline classifiers (logistic regression and random forest) using features produced by the HU-06 transformation pipeline, and MUST fit that transformation pipeline only on the training partition before transforming the test partition.

#### Scenario: Leakage-free training run

- GIVEN a stratified train/test split of the processed labeled dataset
- WHEN baseline training runs
- THEN the HU-06 transformation pipeline MUST be fitted only on the training partition
- AND the test partition MUST be transformed without refitting the pipeline
- AND both classifiers MUST be fitted only on the transformed training features and training labels

#### Scenario: Missing training input

- GIVEN the configured training CSV is missing or empty
- WHEN baseline training runs
- THEN the system MUST abort with a descriptive error naming the missing or empty path
- AND MUST NOT write `modelo.joblib` or claim a successful training run

### Requirement: Test Predictions And Model Serialization

The system MUST generate initial predictions on the test set for each trained baseline and MUST persist the selected classifier to `ml_service/artifacts/modelo.joblib`.

#### Scenario: Selected model is serialized

- GIVEN both baselines have test predictions and metrics
- WHEN model selection completes using primary metric F1 and recall as the tie-breaker
- THEN the selected estimator MUST be written to `ml_service/artifacts/modelo.joblib`
- AND the artifact MUST be loadable afterward
- AND the report MUST identify which model was selected

#### Scenario: Training fails before serialization

- GIVEN an error occurs while fitting a classifier or evaluating metrics
- WHEN the training flow terminates
- THEN it MUST return a non-zero exit status
- AND MUST NOT leave a success-shaped `modelo.joblib` for the failed run

### Requirement: Comparative Baseline Metrics Report

The system MUST write `reports/model_baseline.md` containing a comparative table of accuracy, precision, recall, F1, and ROC-AUC for both baseline models, plus enough provenance to reproduce the run.

#### Scenario: Metrics report is generated

- GIVEN both baselines were evaluated on the same test set
- WHEN the metrics report is written
- THEN the report MUST include accuracy, precision, recall, F1, and ROC-AUC for each model
- AND MUST record seed, split proportions, stratification status, selected model, and artifact path
- AND the training command MUST exit with code 0 on the happy path

#### Scenario: Incomplete metrics are rejected

- GIVEN evaluation cannot compute a required metric for a model
- WHEN the report is assembled
- THEN the system MUST fail explicitly
- AND MUST NOT write a success report that omits a required metric column
