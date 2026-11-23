# ML Inference API Specification

## Purpose

Defines the minimal FastAPI inference surface that serves HU-08 `modelo.joblib` to the Next.js ops dashboard over HTTP. Next.js MUST NOT execute Python or load joblib directly.

## Requirements

### Requirement: Predict Endpoint Over Baseline Artifact

The ML service MUST expose `POST /predict` that loads `ml_service/artifacts/modelo.joblib` and returns a failure-risk probability for one sensor feature payload.

#### Scenario: Successful prediction

- GIVEN `modelo.joblib` exists and is a loadable sklearn Pipeline
- AND the request body includes the five operating features required by the HU-06/HU-08 pipeline
- WHEN `POST /predict` is called
- THEN the response MUST include a numeric failure-risk probability in `[0, 1]`
- AND the service MUST NOT retrain or overwrite the artifact during inference

#### Scenario: Missing model artifact

- GIVEN `modelo.joblib` is missing
- WHEN `POST /predict` is called
- THEN the service MUST return a non-success HTTP error
- AND MUST NOT invent a probability

### Requirement: Health Endpoint

The ML service MUST expose `GET /health` for readiness checks used by the web adapter.

#### Scenario: Healthy service

- GIVEN the FastAPI process is running and the model file is present
- WHEN `GET /health` is called
- THEN the response MUST indicate readiness suitable for the web layer to attempt predictions

### Requirement: Next.js Consumes Predictions Only Via HTTP Adapter

The Next.js application MUST call the ML service through an HTTP port/adapter (`FastApiMlAdapter`) and MUST NOT import Python, joblib, or sklearn in the web runtime.

#### Scenario: Dashboard risk panel

- GIVEN the failure-risk view needs a score for a real processed CSV row
- WHEN the web use case requests a prediction
- THEN it MUST send the row’s real sensor features to FastAPI via the adapter
- AND display the returned probability (mapped to UI severity) without hard-coded scores
