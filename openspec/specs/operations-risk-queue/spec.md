# Operations Risk Queue Specification

## Purpose

Defines the Operations home surface (“cola de riesgo”) where operators see risk summary for real AI4I processed machines, severity filtering, KPIs, and a primary risk visualization. Data MUST come from the processed CSV + model scores — not invented fixtures.

## Requirements

### Requirement: Risk Queue Overview From Real Rows

The system MUST provide an Operations risk-queue page populated from real processed AI4I identities (`UDI` / `Product ID`) and risk signals derived from `Machine failure` labels and/or FastAPI model probabilities for those rows.

#### Scenario: Operator views the risk queue with data

- GIVEN the processed CSV is available and contains both failure and non-failure rows
- WHEN the operator opens the Operations risk-queue route
- THEN the page MUST list queue items using real `Product ID` (and/or `UDI`) values from the CSV
- AND each item’s sensor-derived context MUST match the CSV row
- AND risk presentation MUST use real label and/or model probability — not hard-coded demo scores

#### Scenario: Operator opens the queue when source is empty or unavailable

- GIVEN the processed CSV is missing or yields zero readable rows
- WHEN the operator opens the Operations risk-queue route
- THEN the page MUST show an empty or unavailable state
- AND MUST NOT inject invented machines

### Requirement: Severity Filtering

The system MUST allow the operator to filter the risk queue by severity (critical, warning, and ok classes aligned to canvas tokens), where severity is derived from real risk signals.

#### Scenario: Filter to critical only

- GIVEN the queue contains critical and non-critical items derived from real data
- WHEN the operator selects the critical severity filter
- THEN only critical items MUST remain visible
- AND clearing the filter MUST restore the unfiltered real list

#### Scenario: Filter yields no matches

- GIVEN an active severity filter that matches zero items
- WHEN the filtered list renders
- THEN the list region MUST show a no-matches state
- AND MUST NOT present filtered-empty as fabricated data

### Requirement: Navigation To Asset Context

Each risk-queue item MUST navigate to the asset detail route for that row’s real identifier.

#### Scenario: Open asset from queue row

- GIVEN a queue item for a real `Product ID` such as `M14860`
- WHEN the operator activates the item’s primary navigation affordance
- THEN the system MUST navigate to the asset detail route for that same identifier
