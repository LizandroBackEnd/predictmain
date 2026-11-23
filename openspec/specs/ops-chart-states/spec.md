# Ops Chart States Specification

## Purpose

Defines shared chart presentation states — loading, empty, and incomplete reading — required by the Kombai chart-states frame and reusable across telemetry and failure-risk charts.

## Requirements

### Requirement: Loading Chart State

Shared chart containers MUST provide a loading state that does not imply successful data.

#### Scenario: Data fetch in progress

- GIVEN a chart region is waiting for series data
- WHEN the loading state is active
- THEN the UI MUST show a loading indicator or skeleton inside the chart region
- AND MUST NOT render stale series as if they were current unless explicitly labeled as cached

### Requirement: Empty Chart State

Shared chart containers MUST provide an empty state when there are zero points to plot.

#### Scenario: Zero points

- GIVEN the resolved dataset for the chart has length zero
- WHEN the chart region renders
- THEN an empty-state message MUST appear in place of axes/series
- AND the surrounding page chrome MUST remain interactive

### Requirement: Incomplete Reading State

Shared chart or reading presentations MUST distinguish incomplete readings (partial sensor payload) from empty and loading states.

#### Scenario: Partial series payload

- GIVEN a telemetry or risk payload is missing required fields for a complete plot
- WHEN the chart/reading region renders
- THEN the UI MUST indicate incomplete reading
- AND MUST NOT silently coerce missing numeric fields to zero without marking incompleteness

#### Scenario: Recovery to complete data

- GIVEN an incomplete state was shown
- WHEN a subsequent complete payload arrives
- THEN the normal chart rendering MUST replace the incomplete state
