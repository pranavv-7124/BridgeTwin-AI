# Data guide

The bundled training file is `backend/data/synthetic/bridge_trajectories.csv`. All 15,360 rows are synthetic. `backend/data/sample-observations.csv` is a small synthetic CSV for demonstrating import. Choose **SYNTHETIC** when importing it.

## Import observations

Open Data Explorer, choose REAL or SYNTHETIC according to the actual provenance, select a UTF-8 `.csv`, then import. Accepted files contain 1–50,000 rows and at most 10 MiB. Required values must be present; numeric values must be finite and within the documented bounds. The source selector is a declaration by the uploader, not an independent provenance check.

| Column | Meaning | Required for import | Accepted range |
|---|---|---|---|
| bridge_id | Stable asset identifier | Yes | Up to 100 characters |
| component_id | Stable component identifier | Yes | Up to 100 characters |
| timestamp | Observation date, preferably ISO 8601 | Yes | Valid date |
| health_score | Condition score under a documented transform | Yes | 0–100 |
| age | Component age in years | Training | 0–150 |
| traffic_load | Normalized traffic utilization, percent | Training | 0–100 |
| heavy_vehicle_percentage | Heavy vehicle share, percent | Training | 0–100 |
| temperature | Temperature, °C | Training | −60 to 70 |
| rainfall | Annual rainfall proxy, mm/year | Training | 0–15,000 |
| environmental_exposure | Normalized environmental severity | Training | 0–1 |
| cumulative_load | Normalized exposure-years proxy | Training | 0–1,000 |
| last_maintenance_years | Years since maintenance | Training | 0–150 |
| maintenance_delay | Additional deferred-maintenance years | Training | 0–100 |
| previous_health | Condition at the prediction origin | Training | 0–100 |
| material_factor | Calibrated susceptibility factor | Training | 0.1–5 |
| protection | Remaining intervention protection | Training | 0–1 |
| type_code | Deck 0, pier 1, bearing 2, joint 3 | Training | Integer 0–3 |
| target_health_1y | Observed condition one year later | Training target | 0–100 |
| data_source | Provenance, if included | No | Must match selected source |

Imports register dataset metadata and preserve normalized observations in SQLite. Missing optional features remain missing. Imports neither overwrite the active fictional bridge nor silently retrain the model. The preview shows the first 20 rows. A successful import marked ineligible for training can still serve as an observation archive.

## Prepare real training data

1. Document the original source, license, asset/component identifiers and health-score conversion. Do not rename a real condition rating to 0–100 without a defensible transformation.
2. Align each feature row at time t with the same component's observation at t + 1 year. Do not use future measurements as input features. The software checks schema, not whether this alignment is scientifically valid.
3. Supply all 13 model features plus `target_health_1y`, `bridge_id`, and source labels. Do not fabricate missing operational measurements merely to satisfy the schema.
4. Use at least 20 independent real bridge IDs. Training reserves real bridge groups for validation, calibration and final testing; synthetic observations augment training only.
5. From `backend`, run `.\.venv\Scripts\python.exe scripts/train_models.py --real-csv "C:\data\normalized-real-bridges.csv"`, then restart the backend.

The 20-bridge minimum is an implementation guard, not proof of statistical adequacy. Assess geographic, temporal and asset-type generalization separately. Maintain a truly unseen real test set and document uncertainty before operational use.

## Source categories

REAL and SYNTHETIC label imported or generated observations. SIMULATION labels calculated evolving state and interventions. PREDICTION labels future estimates. The forecast's horizon-zero anchor is labeled CURRENT because it refers to the existing state; use the state's provenance to interpret it. An anomaly means an unusual feature distribution, not detected structural damage.
