# Proposal: Industrial Ops Dashboard UI (Light/Dark) — Real Pipeline Data

## Intent

PredictMain already has ML and data-pipeline foundations (through HU-08), but the web surface is still a Next.js starter page. Kombai has produced an industrial operations canvas (`.kombai/canvas/predictmain_ops.canvas`) that defines the visual system and core screens operators need: risk queue, asset detail, telemetry explorer, and failure-risk view — each in dark and light themes, with explicit chart empty/loading/incomplete states.

This change implements that UI in Next.js (App Router) + React + Tailwind + Shadcn UI, with **Tabler Icons** and **Shadcn Charts (Recharts)**, bound to **real AI4I pipeline artifacts** — not invented fixtures. Telemetry/identity MUST come from the processed dataset; failure risk MUST come from `modelo.joblib` via FastAPI `POST /predict` and the Next.js `FastApiMlAdapter`. The RAG technical assistant frames from the canvas remain **explicitly excluded**.

**Requirement change (2026-11-22):** User rejected invented/mock FR-204 fixtures. Dashboard data MUST be sourced from the real CRISP-DM outputs and trained baseline model.

## Scope

### In Scope

- Implement the following canvas screens (dark + light parity):
  - **Operación — cola de riesgo**
  - **Activo — detalle** (real `Product ID` / `UDI` from AI4I, e.g. `M14860` — never a fake `FR-204`)
  - **Telemetría — explorador de sensores**
  - **Riesgo de falla**
  - Shared **chart states**: loading, empty, incomplete reading
- Shared ops shell: sidebar/nav, theme toggle (light/dark), canvas-aligned tokens
- UI stack: Next.js 16, React 19, Tailwind CSS 4, Shadcn UI, Shadcn Charts (Recharts), `@tabler/icons-react`
- **Real telemetry/asset source:** read `data/processed/ai4i2020_outlier_analyzed.csv` (or the current HU-05/HU-06 processed equivalent used by training) via a server-side Next.js adapter — columns `UDI`, `Product ID`, `Type`, five sensors, `Machine failure`
- **Real risk source:** implement minimal FastAPI `POST /predict` (and `/health`) in `ml_service/` loading `artifacts/modelo.joblib`; Next.js consumes it only through `FastApiMlAdapter` + optional `src/app/api/predictions/route.ts` proxy
- Chart X-axis uses real dataset order (`UDI` / cycle index). AI4I is not a wall-clock time series — do **not** invent fake timestamps
- Scope Rule for components under `src/app/(dashboard)/…` and `src/components/`

### Out of Scope

- **Asistente técnico / RAG panel**
- Auth, multi-tenant IAM, billing
- PDF report/work-order UI
- Real-time websocket protocol
- Retraining HU-08 or changing selection metrics
- Invented machines, sensor values, risk scores, or synthetic CSVs for the happy path
- Pixel-perfect HTML port of Kombai static markup

## Capabilities

### New Capabilities

- `ops-ui-shell`: Shared dashboard chrome, navigation, light/dark theme tokens, Tabler icons, Shadcn primitives
- `operations-risk-queue`: Operations risk queue driven by real processed rows + model scores
- `asset-detail-view`: Asset detail for a real AI4I `Product ID` / `UDI`
- `telemetry-explorer`: Sensor explorer charts from real processed sensor columns
- `failure-risk-view`: Failure-risk UI fed by FastAPI inference on `modelo.joblib`
- `ops-chart-states`: Shared loading / empty / incomplete chart states
- `ml-inference-api`: Minimal FastAPI inference surface (`POST /predict`, `/health`) serving the HU-08 artifact
- `processed-telemetry-source`: Server-side adapter that reads the real processed AI4I CSV for ops UI queries (no fabricated rows)

### Modified Capabilities

- None (no existing OpenSpec UI/inference domains to delta yet)

## Approach

1. Canvas remains visual source of truth for layout/theme; Lucide in the canvas maps to **Tabler** in code.
2. Bootstrap Shadcn + Charts + theme tokens.
3. Add `ml_service` FastAPI app exposing `POST /predict` over `modelo.joblib` (composite Pipeline).
4. Next.js: `ProcessedCsvTelemetryAdapter` (or equivalent) for queue/asset/telemetry reads; `FastApiMlAdapter` for risk probabilities.
5. Map routes under `/(dashboard)/operations`, `/assets/[id]`, `/telemetry`, `/predictions`.
6. Omit RAG from nav and routes.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `.kombai/canvas/predictmain_ops.canvas` | Reference (read-only) | Visual source of truth |
| `package.json` / lockfile | Modified | Shadcn, Recharts, Tabler, theme helper |
| `src/app/globals.css`, `layout.tsx`, `page.tsx` | Modified | Tokens, theme, redirect |
| `src/app/(dashboard)/**` | New | Shell + four screens |
| `src/components/ui/**`, `src/components/telemetry/**` | New | Shadcn + shared charts/states |
| `src/modules/telemetry-ingestion/` and/or `ops` adapters | New | Processed CSV reader port/adapter |
| `src/modules/predictive-analytics/` | New | ML port + `FastApiMlAdapter` |
| `src/app/api/predictions/route.ts` | New (optional proxy) | Server proxy to FastAPI |
| `ml_service/main.py` (or `ml_service/src/interfaces/http/`) | New | FastAPI `/predict` + `/health` |
| `ml_service/requirements.txt` | Modify | Ensure FastAPI/uvicorn present |
| `data/processed/*.csv` | Read-only | Real telemetry source |
| `ml_service/artifacts/modelo.joblib` | Read-only | Real model artifact |
| RAG / chat UI | Excluded | Not implemented |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| FastAPI not running → empty risk UI | Med | `/health` check; clear unavailable state; document `uvicorn` start |
| AI4I has no wall-clock time | Med | Chart on `UDI`/cycle index; label axis honestly |
| Large CSV read on every request | Med | Cache/parse once per process or page-load slice; don’t load unnecessary columns |
| Scope creep into full ML platform | Med | Minimal `/predict` contract only; no retraining |
| Canvas Lucide vs Tabler mismatch | Med | Tabler-only rule in review |

## Rollback Plan

- Remove `(dashboard)/` tree, UI components, predictive/telemetry adapters, and predictions API proxy.
- Remove or disable new FastAPI entrypoint files without deleting `modelo.joblib` or processed CSVs.
- Revert package dependency additions.
- No destructive changes to `data/` or training artifacts.

## Dependencies

- `data/processed/ai4i2020_outlier_analyzed.csv` (or documented successor used by HU-08 train)
- `ml_service/artifacts/modelo.joblib` from HU-08
- Bun for Next; `.venv` + uvicorn for FastAPI
- Visual reference: ops canvas (in-scope frames only)

## Success Criteria

- [ ] Four ops screens render in light and dark themes
- [ ] Queue/asset/telemetry values are traceable to real processed CSV rows (`UDI` / `Product ID`)
- [ ] Risk scores come from `modelo.joblib` via FastAPI `/predict` (not hard-coded)
- [ ] No invented machine ids such as `FR-204` in code or docs for this change
- [ ] No RAG assistant routes/nav
- [ ] Icons are Tabler; charts are Shadcn Charts + Recharts
- [ ] Scope Rule respected
