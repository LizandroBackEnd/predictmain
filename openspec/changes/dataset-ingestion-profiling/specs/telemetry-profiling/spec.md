# Telemetry Profiling Specification

## Purpose

Defines the requirements for automated statistical profiling, schema validation, cardinality checking, and technical markdown report generation for the historical telemetry dataset.

## Requirements

### Requirement: Statistical and Schema Analysis

The system SHALL read the verified raw dataset and calculate descriptive statistics, data types, null counts, duplicate rows, and class balance.

#### Scenario: Comprehensive statistical profiling
- GIVEN `data/raw/ai4i2020.csv` is validated and readable
- WHEN the profiling use case executes
- THEN the system MUST compute minimum, maximum, mean, median, standard deviation, and unique count for all numerical variables (`Air temperature [K]`, `Process temperature [K]`, `Rotational speed [rpm]`, `Torque [Nm]`, `Tool wear [min]`)
- AND the system MUST evaluate the class distribution of `Machine failure` and specific failure modes (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`).

#### Scenario: Verification against UCI specification
- GIVEN the computed profile metrics
- WHEN comparing against the reference specification
- THEN the system MUST verify that missing value count is exactly 0
- AND the system MUST verify that the categorical variable `Type` strictly contains values `L`, `M`, and `H`.

---

### Requirement: Documentation Report Generation

The system SHALL output a human-readable, auditable Markdown report capturing all profiling findings.

#### Scenario: Markdown report compilation
- GIVEN the profiling analysis has completed successfully
- WHEN the report renderer runs
- THEN the system MUST write `docs/03-analysis/data-profile.md`
- AND the document MUST contain tables for numerical statistics, categorical cardinality, target distributions, and candidate modeling variables with their engineering constraints.
