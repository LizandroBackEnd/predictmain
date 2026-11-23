# Design: Industrial Ops Dashboard UI — Real Pipeline Data

## Technical Approach

Build the Kombai ops screens under `src/app/(dashboard)/` with Shadcn + Tabler + light/dark tokens, bound to **real** CRISP-DM outputs:

1. **Telemetry / assets / queue** ← server-side adapter reading `data/processed/ai4i2020_outlier_analyzed.csv` (read-only).
2. **Failure risk** ← `modelo.joblib` served by a new minimal FastAPI app, consumed only via `FastApiMlAdapter` (Next never loads joblib).

No invented `FR-204` fixtures. Demo identity in docs/tests MUST be a real row such as `Product ID=M14860` (`UDI=1`).

AI4I is cycle-indexed, not wall-clock time: charts use `UDI`/row order on the X-axis.

## Architecture Decisions

### Decision: Processed CSV adapter in Next server layer

**Choice**: `ProcessedCsvTelemetryAdapter` implements a port that parses the processed CSV on the server (RSC / route handlers). Cache parsed rows in module scope for the Node/Bun process.
**Alternatives considered**: Invented fixtures; copy CSV into Postgres first; call Python for every telemetry read.
**Rationale**: CSV already exists from HU-04/05; Prisma schema is not present; keeps reads simple while remaining honest to source data.

### Decision: Minimal FastAPI inference now (was pending in README)

**Choice**: Add `ml_service/main.py` (or `src/interfaces/http/app.py` imported by main) with `GET /health` and `POST /predict` loading `artifacts/modelo.joblib`.
**Alternatives considered**: Defer risk UI; spawn Python from Next; read joblib in Bun.
**Rationale**: Architecture Law 1 requires HTTP to Python; README already documents FastAPI as pending — this change closes the gap needed for non-invented risk scores.

### Decision: Hexagonal ports on the web side

**Choice**:
- `TelemetryQueryPort` → CSV adapter
- `FailureRiskPort` → `FastApiMlAdapter`
**Alternatives considered**: Pages reading `fs` and `fetch` inline.
**Rationale**: Matches Screaming Architecture modules (`telemetry-ingestion`, `predictive-analytics`) and keeps UI swappable later to Prisma without rewriting pages.

### Decision: UDI-based chart axis

**Choice**: Label charts as cycle/`UDI` sequence windows (presets = last N / first N / full slice caps), not fake ISO timestamps.
**Alternatives considered**: Synthesize timestamps; hide charts until IoT stream exists.
**Rationale**: Invented time would violate the “no invented data” rule.

### Decision: Exclude RAG; Tabler-only icons; Shadcn Charts

**Choice**: Unchanged from prior design — no assistant routes; `@tabler/icons-react`; Shadcn Charts over Recharts.
**Rationale**: Explicit product constraints.

## Data Flow

```text
 data/processed/ai4i2020_outlier_analyzed.csv
        │ (read-only)
        ▼
 TelemetryQueryPort / ProcessedCsvTelemetryAdapter
        │
        ├── operations queue (real Product ID + label/severity)
        ├── assets/[id] latest sensors
        └── telemetry series (UDI → sensors)

 ml_service/artifacts/modelo.joblib
        │
        ▼
 FastAPI POST /predict  ◄── FastApiMlAdapter ◄── failure-risk / queue scoring
        │
        ▼
 UI severity + score (probability in [0,1])
```

Sequence (risk page):

```text
Operator → /predictions?assetId=M14860
  → RSC loads CSV row for M14860
  → FailureRiskPort.predict(features)
  → HTTP POST /predict
  → modelo.joblib predict_proba
  → render score | unavailable state
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `ml_service/main.py` | Create | FastAPI app: `/health`, `/predict` |
| `ml_service/requirements.txt` | Modify | Ensure fastapi/uvicorn |
| `src/modules/telemetry-ingestion/**` | Create | Port + CSV adapter + view models |
| `src/modules/predictive-analytics/**` | Create | Port + `fastapi-ml.adapter.ts` |
| `src/app/api/predictions/route.ts` | Create | Optional BFF proxy to FastAPI |
| `src/app/(dashboard)/**` | Create | Shell + 4 screens |
| `src/components/ui/**`, `src/components/telemetry/**` | Create | Shadcn + chart states |
| `src/app/globals.css`, `layout.tsx`, `page.tsx` | Modify | Theme + redirect |
| `package.json` | Modify | UI deps |
| `data/processed/*.csv`, `modelo.joblib` | Read-only | Real sources |
| Fixture/`FR-204` modules | None | Explicitly not created |

## Interfaces / Contracts

```ts
// Web ports (TypeScript)

export interface TelemetryRow {
  udi: number;
  productId: string; // e.g. "M14860"
  type: "L" | "M" | "H" | string;
  airTemp: number;
  processTemp: number;
  rpm: number;
  torque: number;
  toolWear: number;
  machineFailure: 0 | 1;
}

export interface TelemetryQueryPort {
  getByProductId(productId: string): Promise<TelemetryRow | null>;
  listSlice(opts: { offset: number; limit: number }): Promise<TelemetryRow[]>;
  seriesForProductId(
    productId: string,
    window: { startUdi?: number; endUdi?: number; limit: number },
  ): Promise<TelemetryRow[]>;
}

export interface PredictFeatures {
  airTemp: number;
  processTemp: number;
  rpm: number;
  torque: number;
  toolWear: number;
  // plus any Type encoding the Pipeline expects — must match training columns
}

export interface FailureRiskPort {
  predict(features: PredictFeatures): Promise<{ probability: number }>;
  health(): Promise<boolean>;
}
```

```python
# FastAPI predict body (sketch) — must match modelo.joblib feature contract
class PredictRequest(BaseModel):
    # raw sensor fields accepted; server applies the serialized Pipeline
    air_temperature_k: float
    process_temperature_k: float
    rotational_speed_rpm: float
    torque_nm: float
    tool_wear_min: float
    product_type: Literal["L", "M", "H"]

class PredictResponse(BaseModel):
    failure_probability: float  # [0, 1]
```

## Testing Strategy

| Layer | What to Test | Approach |
|-------|-------------|----------|
| Unit (TS) | CSV adapter returns `M14860` sensors matching file; unknown id → null | Bun test against real CSV (read-only) |
| Unit (Py) | `/predict` with known vector returns probability in [0,1]; missing model → error | pytest + TestClient |
| Integration | Dashboard risk page shows adapter probability when uvicorn up | Manual + `bun run build` |
| Negative | FastAPI down → unavailable UI state | Manual / adapter mock of network error |

## Threat Matrix

N/A — no shell/VCS/PR automation boundary. FastAPI is an HTTP service boundary already required by architecture; standard input validation via Pydantic applies, but the design does not add git/shell execution surfaces.

## Migration / Rollout

1. Ensure `modelo.joblib` exists (`python -m src.cli train` if needed — read-only reuse if already trained).
2. Start uvicorn for `ml_service.main:app`.
3. Run Next dashboard against real CSV + `/predict`.
4. Later swap CSV adapter for Prisma without changing view models.

No DB migration in this change.

## Open Questions

- [x] Invented fixtures? **No** — user decision 2026-11-22; real CSV + model only
- [ ] Predict request feature encoding details (exact column names / Type one-hot) — resolve during apply by inspecting the fitted Pipeline in `modelo.joblib`
- [ ] Whether queue scores every visible row via `/predict` or shows label-first with on-demand predict — default: label for coarse queue severity + live `/predict` on detail/risk pages to avoid N+1 latency
