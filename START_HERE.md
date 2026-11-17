# BridgeTwin AI 2.0

This release improves prediction selection, planning horizons, import checks, and state consistency. It retains the React/FastAPI application and interactive bridge. It is a simulation-driven academic prototype with no real sensor connection.

## Windows startup

Install Python 3.12 and Node.js 22 LTS or newer. Extract the ZIP. Double-click Start-BridgeTwin.cmd, or run Start-BridgeTwin.ps1. First launch installs dependencies and needs internet. Open http://localhost:5173 when ready. Keep the terminal open; Ctrl+C stops the app. Windows launchers were inspected but not executed during this Linux revision.

If the launcher is blocked by PowerShell, run these commands from the project root:

```powershell
python -m venv backend/.venv
backend\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
backend\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --port 8000
```

In a second terminal:

```powershell
npm --prefix frontend ci
npm --prefix frontend run dev
```

Linux/macOS: `bash start.sh`.

## Changes

- Validation-only search over 21 blend weights replaces fixed 65/35 blending. The supplied synthetic data selects 100% equations and 0% ML. Both ML candidates remain trained and compared.
- The selected 1–20-year horizon now changes the maintenance objective: integrated weighted condition-deficit reduction. All repairs happen now. This is not multi-period scheduling.
- Applying repairs requires the comparison revision; missing or stale revisions return HTTP 409.
- Imports reject blank IDs, duplicates after date/ID normalization, fractional type codes, and inconsistent current-health features. Imported data receives condition profiles and normalized CSV downloads, and remains separate from the active simulation and training.
- Startup creates necessary folders. Prediction diagnostics disclose blend selection, original baselines, observed residual coverage, and aggregate uncertainty limits. Clock advances clear obsolete scenarios.

## Demo

Reset to January 2026. Select the bearing group in Digital Twin. In Predictions, inspect baseline results and the selected weight; do not call R² percentage accuracy. In Maintenance Planner, compare one-year and ten-year plans with INR 500,000. Simulate before applying. In Data Explorer, import backend/data/sample-observations.csv as SYNTHETIC; view its profile and normalized download. Reports supports JSON export and browser printing; printing depends on browser settings.

## Reproduce

From backend:

```text
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/train_models.py
```

From project root:

```text
npm --prefix frontend ci
npm --prefix frontend run build
python scripts/research_experiment.py
```

Retraining overwrites the model/card; restart the API afterward. research/experiment_results.json records 15 budget/horizon cases and the model card. Timing is environment-dependent.

## Paper and submission

research/BridgeTwin_AI_IEEE_Paper.pdf is an IEEEtran conference-format review draft, with LaTeX source, class file, and figure included. Compile twice in a normal TeX Live or Overleaf environment. It uses seven verified primary/documentation references and measured synthetic results.

The draft is anonymous because uploaded team/guide details conflict. Confirm author order, affiliation, emails, supervisor, and target venue before submission. No similarity or AI-detection service was run; no percentage is guaranteed. The original half-report remains separate and has not been presented as a completed report.

## Limits

The generator and equation baseline share assumptions. No real bridge accuracy, capacity estimate, failure probability, or safety certification is established. Costs and recovery are illustrative. Multi-year/bridge-level bands are not calibrated. Mandatory engineering constraints, inspection information value, crews, repeated repairs, discounting, and live sensors are not implemented.

This package runs locally and has not been cloud-deployed. It excludes dependencies, environments, test uploads, and the old advanced database. Fresh startup creates the baseline. Original documentation is historical; this file describes version 2.
