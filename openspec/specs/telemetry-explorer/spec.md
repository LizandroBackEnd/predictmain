# Telemetry Explorer Specification

## Purpose

Defines the sensor explorer surface backed by real processed AI4I sensor columns and Shadcn Charts (Recharts). The X-axis uses dataset sequence (`UDI`/order), not invented timestamps.

## Requirements

### Requirement: Multi-Series Telemetry Chart From Real Sensors

The telemetry explorer MUST render a multi-series chart for Air Temp, Process Temp, RPM, Torque, and Tool Wear using values from the processed CSV via the telemetry source adapter.

#### Scenario: Chart renders with series data

- GIVEN readable processed rows for the selected asset context or slice
- WHEN the explorer page renders
- THEN the chart MUST plot the five sensor series from those real values
- AND series colors MUST follow ops canvas series tokens (or theme-mapped equivalents)
- AND a legend or labeled affordance MUST identify each series

#### Scenario: Series can be toggled when UI provides toggles

- GIVEN the explorer exposes series visibility controls
- WHEN the operator hides one series
- THEN that series MUST no longer render on the chart
- AND remaining series MUST stay visible with their real values

### Requirement: Range Controls Over Dataset Sequence

The explorer MUST provide range presets that slice the real `UDI`/row sequence (for example first N cycles / recent window over UDI order). Presets MUST NOT invent wall-clock times absent from the source.

#### Scenario: Switch sequence window

- GIVEN the explorer is showing a default UDI window
- WHEN the operator selects another preset window
- THEN the chart MUST bind to the corresponding real CSV slice
- AND the active preset MUST be visually indicated

### Requirement: Threshold Markers From Documented Limits

The explorer MAY display threshold markers only when limits come from documented domain rules or source metadata — not arbitrary invented numbers without provenance.

#### Scenario: Documented thresholds present

- GIVEN documented threshold values exist for at least one sensor
- WHEN the chart renders
- THEN threshold markers or bands MUST be visible and labeled as such

#### Scenario: Thresholds absent

- GIVEN no documented threshold metadata is available
- WHEN the chart renders
- THEN the series chart MUST still render without inventing threshold lines
