# Processed Telemetry Source Specification

## Purpose

Defines the server-side contract for reading real AI4I processed telemetry used by the ops dashboard. Rows MUST originate from the CRISP-DM processed CSV — never from invented fixtures.

## Requirements

### Requirement: Real Processed CSV As Source Of Truth

The ops telemetry/asset/queue data adapter MUST read machine identity and sensor values from the project processed AI4I CSV used by the HU-08 training path (default `data/processed/ai4i2020_outlier_analyzed.csv`) and MUST NOT fabricate rows for the happy path.

#### Scenario: Load known Product ID

- GIVEN the processed CSV contains `Product ID` `M14860` with sensor columns and `Machine failure`
- WHEN the adapter resolves that asset
- THEN it MUST return the CSV values for Air temperature, Process temperature, Rotational speed, Torque, and Tool wear for that row
- AND the identity MUST use real `UDI` and/or `Product ID` from the file

#### Scenario: Missing processed file

- GIVEN the configured processed CSV path is missing
- WHEN any ops query runs
- THEN the adapter MUST fail with a descriptive error naming the path
- AND the UI MUST surface an unavailable/empty state rather than substitute invented machines

### Requirement: No Fabricated Identifiers

Dashboard queries MUST address assets by real dataset identifiers (`UDI` and/or `Product ID`) and MUST NOT use placeholder ids such as `FR-204`.

#### Scenario: Reject invented demo id as source data

- GIVEN a request for an asset id that does not exist in the processed CSV
- WHEN the adapter looks up the asset
- THEN it MUST return not-found / null
- AND MUST NOT synthesize a demo machine record

### Requirement: Ordered Series From Dataset Sequence

Telemetry charts that need an X-axis MUST use the real dataset sequence (`UDI` ascending or stable CSV order) and MUST NOT invent wall-clock timestamps that are not present in the source.

#### Scenario: Series for one product type slice

- GIVEN the operator explores telemetry for a selected asset or filtered slice rooted in the processed CSV
- WHEN series points are built
- THEN each point’s X value MUST derive from `UDI` or row order in the source
- AND sensor Y values MUST equal the CSV numeric fields for that row
