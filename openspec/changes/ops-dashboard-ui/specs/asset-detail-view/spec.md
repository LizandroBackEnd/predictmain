# Asset Detail View Specification

## Purpose

Defines the machine/asset detail surface for a real AI4I identity: header, latest sensor readings from the processed CSV, status, and navigation into telemetry and failure-risk views.

## Requirements

### Requirement: Asset Identity Header From Processed CSV

The system MUST render an asset detail page keyed by real `Product ID` or `UDI` that exists in the processed CSV.

#### Scenario: Known asset loads

- GIVEN the processed CSV contains `Product ID` `M14860`
- WHEN the operator opens the asset detail route for that id
- THEN the page MUST display that real identity and `Type` when present
- AND MUST display a status indicator derived from real `Machine failure` and/or model risk for that row

#### Scenario: Unknown asset id

- GIVEN the requested id does not exist in the processed CSV
- WHEN the operator opens the asset detail route
- THEN the page MUST show a not-found or unavailable state
- AND MUST NOT render fabricated sensor values

### Requirement: Latest Readings Panel From CSV Columns

The asset detail surface MUST present the latest values for Air Temp, Process Temp, RPM, Torque, and Tool Wear from the selected CSV row.

#### Scenario: Complete latest reading

- GIVEN the selected row has all five sensor columns populated
- WHEN the asset detail page renders
- THEN each sensor MUST show the CSV value with an appropriate unit label

#### Scenario: Incomplete latest reading

- GIVEN one or more sensor fields are missing/null in the selected row
- WHEN the readings panel renders
- THEN the panel MUST mark incomplete fields using the shared incomplete-reading pattern
- AND available fields MUST still render their real values

### Requirement: Deep Links To Telemetry And Risk

The asset detail surface MUST provide navigation to telemetry explorer and failure-risk view for the same real asset id.

#### Scenario: Navigate to telemetry

- GIVEN the operator is on asset detail for a known real machine id
- WHEN the operator activates the telemetry navigation affordance
- THEN the system MUST open the telemetry explorer scoped to that same id

#### Scenario: Navigate to failure risk

- GIVEN the operator is on asset detail for a known real machine id
- WHEN the operator activates the failure-risk navigation affordance
- THEN the system MUST open the failure-risk view for that same id
