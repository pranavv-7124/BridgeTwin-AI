# Validation record

Validated on 21 September 2026 in Linux with Python 3.12, Node.js 24 and a desktop Chromium browser. This validates application behavior, not real-world structural accuracy.

## Automated checks

`python -m pytest -q` from `backend`: **27 passed**. A non-failing upstream Starlette warning concerns the future of its httpx test-client integration.

Coverage includes the condition thresholds; increasing deterioration with loading and delayed maintenance; the protective effect of repairs; monthly aging and state immutability; seeded synthetic generation; disjoint bridge groups across training and holdout splits; synchronized component API values; bounded forecasts; isolated and stale scenario handling; valid and invalid CSV ingestion; imported-data isolation; budget and duplicate-action validation; optimization compared with an exhaustive reference; and repair persistence.

`npm run build` from `frontend`: **passed**, producing the bundled `frontend/dist` assets. JavaScript launcher syntax and Linux shell syntax were checked.

Additional integration checks verified that FastAPI serves the production frontend, favicon and API from one origin. With the trained bundle disabled in an isolated test process, the API explicitly returns MODEL NOT TRAINED and physics-only forecasts, empty model explanations, and no invented model metrics.

## Browser walkthrough

| Journey | Observed result |
|---|---|
| Overview | Loaded current condition, eight mapped components, forecasts and priority members from the API |
| Interactive 3D | Compatibility renderer displayed the geometric bridge; side view worked; directly clicking Pier 3 selected PIER_03 and updated its inspector |
| Explanation | Why this prediction displayed calculated reference sensitivities and global importance |
| Clock step and playback | January advanced to February 2026; scene labels, component selectors and inspector scores changed together. Play future advanced the date automatically; Pause and Reset worked. |
| Scenario | Combined stress produced a five-year baseline of 52.8 and scenario of 49.1 from the tested February state |
| Scenario comparison/apply | Baseline switch changed the displayed future; applying inputs retained current condition and invalidated stale reapplication |
| Maintenance optimization | ₹25,00,000 produced an optimal ₹24,40,000 plan treating six components, with ₹60,000 remaining |
| Maintenance counterfactual | Five-year estimates were 49.1 without additional repair and 73.7 with the selected plan |
| Apply repairs | Current modeled bridge score rose to 84.22; the report reflected revision 4 and the changed component forecasts |
| JSON export | Downloaded file was parsed and checked for the displayed revision, eight components and condition score |
| CSV import | Eight-row sample imported under SYNTHETIC with 20 columns; it remained separately labeled |
| Predictions/analytics | Model metrics, trajectories and chart data rendered from the active state |

These numerical observations describe one documented walkthrough, not permanent UI fixtures. Resetting, applying different inputs or advancing time changes the results.

## Validation limits

- WebGL was disabled in the test browser. The interactive Three.js SVG compatibility renderer was exercised; hardware shadows and animated vehicles were not visually validated here.
- The Windows PowerShell/CMD launchers were inspected, but no Windows execution environment was available. First-time dependency installation on the user's machine still requires internet and the stated Python/Node prerequisites.
- Browser JSON export was verified. The operating system's Print / Save PDF dialog and a generated PDF were not tested; the report includes print CSS.
- No cloud deployment, container launch, PostgreSQL migration or real-bridge validation was performed. Deployment preparation and local production serving are provided.
- Browser checks used a desktop viewport. Responsive CSS is included; exhaustive device and accessibility certification are outside this validation.

The ZIP excludes development environments, dependency folders, test databases, uploaded test files and transient logs. A fresh startup creates the deterministic initial bridge state. It includes the trained model, model card, synthetic dataset, import sample, production frontend build, source, tests and documentation.
