# Eight-minute demonstration

Start the application with `Start-BridgeTwin.cmd`, open http://localhost:5173, and allow the first load to finish. The demo uses a fictional Pune bridge and synthetic history. Reset the simulation before presenting if you have already explored it.

| Step | What to do | What to explain |
|---|---|---|
| 1. Overview | Read current health, priority and component scores | One backend state supplies the dashboard, charts and 3D colors. Scores are condition proxies. |
| 2. Digital Twin | Select Pier 2, then try top, side and reset views | Every geometric member maps to a unique component ID. Orbit and zoom work in both graphics modes. |
| 3. Inspector | Open History, Prediction, Risk Factors and Maintenance | Forecasts and explanations are calculated. Global importance is not a local causal contribution. |
| 4. Simulation Lab | Use Combined stress and Run simulation | The default applies traffic +30%, heavy vehicles +20%, exposure +15%, temperature +3°C and a two-year maintenance delay. Percentages are relative changes. |
| 5. Compare | Switch Baseline / What-if, inspect the two trajectories | The same starting state produces different futures. Running a scenario leaves current condition unchanged. |
| 6. Apply inputs | Apply operating inputs; open Digital Twin; use Play future, then Pause | Inputs change immediately; condition evolves through the clock. This is simulated live state, not physical sensing. |
| 7. Maintenance | Keep ₹25,00,000; Optimize budget; Simulate optimized plan | Binary optimization chooses at most one intervention per component within budget. Compare do-nothing and repair futures. |
| 8. Compare your plan | Select actions manually and Simulate your plan | The same model evaluates your choices. Over-budget plans are blocked. Inspection alone does not physically improve condition. |
| 9. Apply repair | Apply this plan to simulation | Shared component scores, forecasts, history and colors update together. The database preserves the change. |
| 10. Reports | Review scenario history and budget plan; export JSON or Print / Save PDF | Reports include assumptions, provenance and limitations. Historical runs retain their original state revision. |

If a scenario is marked stale, run it again from the current state. If a budget changes, optimize again before simulating the optimized plan. Reset restores the synthetic starting condition and retains imported data and run records.

## Questions to prepare for

- **Is it a real digital twin?** A simulation-driven digital twin prototype that links an asset model, one evolving condition state, predictions and decisions. It is not connected to a physical bridge.
- **Where does the AI come from?** Random Forest and Gradient Boosting are trained on reproducible trajectories. Validation chooses the model; a hybrid of equations and ML supplies forecasts. Isolation Forest identifies unusual inputs.
- **Why is R² high?** Synthetic targets share relationships with the generator and use previous condition. The documented physics and persistence baselines make this visible. High synthetic R² does not establish real bridge accuracy.
- **How does optimization work?** Maximize weighted condition-risk reduction subject to a budget and one intervention per component using SciPy MILP/HiGHS.
- **What is original about the integration?** Select a member, explain its prediction, alter operating assumptions, simulate a budget-constrained repair, and trace the change across the same state and report.
- **What comes next?** Real inspection-data adapters, calibrated deterioration and repair assumptions, independent real holdouts, structural-engineering review and optional observation streaming.
