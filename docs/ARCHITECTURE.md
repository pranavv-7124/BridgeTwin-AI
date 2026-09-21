# Technical architecture

## One authoritative state

`BridgeService` reads and mutates a versioned JSON snapshot through `Repository`. All mutations use an RLock within the process and compare-and-swap revision checks in the database. Repeated reads are cached per revision. No browser KPI is generated randomly. Zustand holds the latest API view; charts, component lists, the inspector and 3D colors derive from the same component values.

`bridge` describes the demo asset; `components` holds condition and deterioration inputs; `environment_base` stores chosen operating assumptions; `environment` stores the current seasonal realization; `simulation` holds clock and scenario identity; `history` and `maintenance_history` retain provenance; `metadata` holds model/source context. The service adds `summary`, `predictions`, `revision` and recent activities for the API view.

## State-changing journeys

- Clock step: integrate monthly conditions, age, load, protection and environment; append a SIMULATION history point; persist a new revision; recompute forecasts.
- Run scenario: copy the current state, adjust inputs with validated bounds, calculate baseline and altered forecasts, and save an immutable run with source revision. The active bridge stays at the current date.
- Apply scenario: reject a stale source revision; update active operating inputs and scenario name. Health does not instantly deteriorate just because an input changed. Playing the clock evolves condition.
- Optimize: calculate available actions from current component health and solve the budget problem.
- Simulate repair: compare do-nothing and repaired futures from the same state. Applying a plan changes only the simulated component state and appends SIMULATION maintenance history.
- Reset: restore the deterministic 2026 synthetic snapshot. Imported observations and historical scenario records remain separate and intact.

The single workspace is shared by all browser clients connected to this API. The interface is not a multi-user collaboration system. Run one Uvicorn worker for this prototype. A cloud version should introduce authenticated per-project state, database migrations, and broader concurrency tests.

## Persistence

SQLAlchemy tables: `bridges` (active versioned snapshot), `records` (typed dataset and simulation-run records), and `observations` (immutable imported observations). Components, predictions and maintenance history are stored in the versioned snapshot/run payloads rather than redundant normalized copies. Indexes support kind/date and bridge/component/time lookups. This compact repository can later be expanded into normalized entities without changing simulation or ML interfaces.

The default SQLite file is `backend/data/bridgetwin.db`. Original CSV bytes are represented by a validated normalized CSV stored under a UUID filename in `data/raw`; source, missingness, preview, date range and eligibility metadata are retained. No CSV is executed. Files must be UTF-8 CSV, ≤10 MiB, ≤50,000 rows, with finite validated numerics and unique observation keys.

## API map

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | API and model availability |
| GET | `/api/bridge` | Complete consistent bridge view |
| GET | `/api/components` | All component states |
| GET | `/api/components/{id}` | One mapped component |
| GET | `/api/history/{id}` | Source-tagged condition history |
| GET | `/api/predictions/{id}` | Forecast horizons |
| GET | `/api/explanations/{id}` | Global importance and reference sensitivities |
| GET | `/api/analytics` | Chart-ready view |
| GET | `/api/model-info` | Actual model card and metrics |
| GET | `/api/datasets` | Provenance and row previews |
| GET | `/api/data/template` | CSV column template |
| GET | `/api/simulation-runs` | Stored calculations |
| GET | `/api/maintenance/actions` | Current intervention catalog |
| GET | `/api/report` | Structured assessment |
| POST | `/api/simulate` | Calculate isolated scenario |
| POST | `/api/simulate/future` | Advance the live simulation clock |
| POST | `/api/simulate/apply` | Apply a scenario's operating inputs |
| POST | `/api/simulate/reset` | Restore the synthetic baseline |
| POST | `/api/maintenance/optimize` | Solve the budget problem |
| POST | `/api/maintenance/simulate` | Evaluate or apply selected repairs |
| POST | `/api/data/upload` | Validate and register a CSV |

FastAPI's `/docs` and `/openapi.json` expose input schemas. Unknown components return 404, invalid inputs 422, stale state 409, missing write tokens 401, and database failures 503. The UI shows actionable errors and preserves already-loaded data. No model means explicitly labeled physics-only forecasts, not fake model metrics.

## 3D and interface

Eight IDs map directly to 3D members. A camera rig implements framing commands. Canvas WebGL is preferred; the CPU/SVG Three.js renderer provides interactive geometric projection and raycast selection when hardware rendering is unavailable. A keyboard-accessible component selector gives the same inspection capability. Heavy routes and 3D/chart dependencies are split into lazy-loaded chunks. Fonts and geometry are local. The app does not poll when paused.

Optional WebMCP inspection tools are feature-detected; unsupported browsers ignore registration. They share the same Zustand state and do not invent a parallel model.

## Future observation boundary

Ingestion is deliberately separate from active demo state. A future adapter should map validated real asset IDs and component identities, define measured-to-condition transforms, enforce timestamp ordering, and explicitly create a real asset workspace. An MQTT/HTTP sensor adapter can feed the same observation store, but no current function claims physical streaming or automatic real-asset calibration.
