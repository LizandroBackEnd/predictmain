# Tasks: Industrial Ops Dashboard UI — Real Pipeline Data

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1100–1800 authored lines (UI + CSV adapter + FastAPI predict + web ML adapter + tests) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Single PR under size:exception (user-approved 2026-11-22) |
| Delivery strategy | ask-on-risk → size:exception accepted |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: size-exception
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Full ops UI + real CSV source + FastAPI `/predict` + adapters | Single PR (size:exception) | `bun run lint && bunx tsc --noEmit && bun run build` + `cd ml_service && .venv/bin/python -m pytest` (predict tests) | `uvicorn` + `bun run dev`; walk screens with `Product ID=M14860` | `(dashboard)/`, `src/components/**`, telemetry/predictive modules, `ml_service/main.py` — never delete `data/` or `modelo.joblib` |

## Phase 1: Foundation (Shell, Theme, Shadcn, Tabler)

- [x] 1.1 Initialize Shadcn for Tailwind 4 (`components.json`) and add required primitives under `src/components/ui/`.
- [x] 1.2 Add `@tabler/icons-react` and `recharts`; add Shadcn `src/components/ui/chart.tsx`.
- [x] 1.3 Replace starter tokens in `src/app/globals.css` with canvas-aligned light/dark CSS variables.
- [x] 1.4 Update `src/app/layout.tsx` for PredictMain metadata + theme class support.
- [x] 1.5 Create `src/app/(dashboard)/layout.tsx` with Tabler nav (Operations, Assets, Telemetry, Predictions) — **no RAG item** — plus theme toggle.
- [x] 1.6 Redirect `src/app/page.tsx` to `/operations`.

## Phase 2: Real Processed Telemetry Source

- [x] 2.1 Create `TelemetryQueryPort` + `ProcessedCsvTelemetryAdapter` under `src/modules/telemetry-ingestion/` reading `data/processed/ai4i2020_outlier_analyzed.csv` (read-only).
- [x] 2.2 Implement `getByProductId`, `listSlice`, and UDI-window series helpers; unknown ids return null (no invented rows).
- [x] 2.3 Add Bun tests proving `M14860` sensors match the CSV and unknown ids return null.

## Phase 3: FastAPI Inference Over `modelo.joblib`

- [x] 3.1 Add FastAPI app entry (`ml_service/main.py` or equivalent) with `GET /health` and `POST /predict` loading `artifacts/modelo.joblib`.
- [x] 3.2 Define Pydantic request/response matching the fitted Pipeline feature contract (inspect artifact during implement).
- [x] 3.3 Add pytest coverage: happy-path probability in `[0,1]`; missing model → error.
- [x] 3.4 Ensure `fastapi`/`uvicorn` are listed in `ml_service/requirements.txt`.

## Phase 4: Web ML Adapter

- [x] 4.1 Create `FailureRiskPort` + `fastapi-ml.adapter.ts` under `src/modules/predictive-analytics/`.
- [x] 4.2 Add `src/app/api/predictions/route.ts` proxy (or server-only adapter calls) so Client Components never talk to Python directly without a boundary.
- [x] 4.3 Map adapter network/health failures to UI unavailable states (no hard-coded scores).

## Phase 5: Shared Chart States

- [x] 5.1 Implement `src/components/telemetry/OpsChartState.tsx` for loading/empty/incomplete.
- [x] 5.2 Wire chart status mapping used by telemetry and predictions.

## Phase 6: Operations Risk Queue

- [x] 6.1 Create `src/app/(dashboard)/operations/page.tsx` listing real CSV identities via `TelemetryQueryPort`.
- [x] 6.2 Add severity filters + KPI/chart composition in `operations/_components/` using real label/model-derived severity (no fake `FR-204`).
- [x] 6.3 Navigate rows to `/assets/[productId]` for real ids (smoke with `M14860`).

## Phase 7: Asset Detail

- [x] 7.1 Create `src/app/(dashboard)/assets/[id]/page.tsx` using `getByProductId`; not-found when null.
- [x] 7.2 Readings panel binds the five real sensor columns; incomplete marking when nulls exist.
- [x] 7.3 Deep links to `/telemetry?assetId=` and `/predictions?assetId=` with the same real id.

## Phase 8: Telemetry Explorer

- [x] 8.1 Create `src/app/(dashboard)/telemetry/page.tsx` with UDI-window presets (not fake clock ranges).
- [x] 8.2 Multi-series Shadcn/Recharts chart from real sensor columns.
- [x] 8.3 Integrate `OpsChartState`; thresholds only if documented — never invent undocumented lines.

## Phase 9: Failure Risk View

- [x] 9.1 Create `src/app/(dashboard)/predictions/page.tsx` loading CSV features then `FailureRiskPort.predict`.
- [x] 9.2 Show returned probability + severity; unavailable state when FastAPI/model is down.
- [x] 9.3 Optional UDI-history chart only from real rows; action strip templates only — **no RAG**.

## Phase 10: Verification And Cleanup

- [x] 10.1 Run `bun run lint`, `bunx tsc --noEmit`, `bun run build`.
- [x] 10.2 Run ML predict tests; manually verify uvicorn + dashboard with `M14860`.
- [x] 10.3 Grep to ensure no `FR-204`, no `lucide-react` in ops UI, and no assistant/RAG routes.
- [x] 10.4 Confirm `data/processed/` and `modelo.joblib` were not overwritten except by explicit train if regenerating was required (prefer reuse).
