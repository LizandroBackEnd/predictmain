# Failure Risk View Specification

## Purpose

Defines the failure-risk screen for a real AI4I asset: score/confidence from FastAPI inference on `modelo.joblib`, trend visualization when historical scores can be derived from real rows, and a recommended-action strip that does not invent maintenance steps or open RAG.

## Requirements

### Requirement: Risk Score From Model Inference

The failure-risk view MUST display a failure-risk probability obtained from FastAPI `POST /predict` using the selected row’s real sensor features from the processed CSV.

#### Scenario: Score available

- GIVEN FastAPI is healthy and `modelo.joblib` loads
- AND the selected asset exists in the processed CSV
- WHEN the failure-risk page renders
- THEN the page MUST show the probability returned by `/predict` for that row’s features
- AND severity styling MUST reflect that real score band
- AND the page MUST NOT display a hard-coded demo score

#### Scenario: Inference unavailable

- GIVEN FastAPI is down or the model artifact is missing
- WHEN the failure-risk page renders
- THEN the page MUST show an unavailable state
- AND MUST NOT invent a confidence or probability

### Requirement: Risk Trend From Real Rows

When the view shows a trend chart, points MUST be derived from real processed rows (and/or repeated inference on those rows). Empty history MUST use the shared empty chart state.

#### Scenario: Trend with real points

- GIVEN multiple real rows are available for the selected context
- WHEN the risk chart renders with computed scores
- THEN each point MUST correspond to a real source row identity/order
- AND MUST NOT use fabricated timestamps or scores

#### Scenario: Trend empty

- GIVEN no scorable history is available
- WHEN the risk chart region renders
- THEN the shared empty chart state MUST be shown

### Requirement: Recommended Action Strip Without Invention

The failure-risk view MAY present guidance only when grounded in real model/label state templates; it MUST NOT deep-link into the RAG assistant in this change and MUST NOT fabricate free-form maintenance narratives.

#### Scenario: Actions from severity template

- GIVEN a real risk severity band is known
- WHEN the action strip renders
- THEN it MAY show a fixed, documented template for that band
- AND MUST NOT open or link to a RAG assistant route

#### Scenario: No actions

- GIVEN no grounded action template applies
- WHEN the action strip region renders
- THEN it MUST show a neutral empty guidance state
