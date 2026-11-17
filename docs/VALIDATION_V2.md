# Version 2 validation

16 November 2026, Linux, Python 3.12, Node.js 24.

- 33 backend tests passed; one non-failing upstream Starlette/httpx deprecation warning.
- Vite production build passed.
- Retraining completed: 15,360 synthetic records; Random Forest candidate; zero ML blend weight. Held-out selected MAE 0.1021454 versus original mixture 0.1144448. Component-row residual coverage 0.8936632.
- All 15 planning cases stayed within budget. Small horizon-aware MILP matched exhaustive enumeration. Solver relative gap is zero.
- Browser: overview loaded and reset; ten-year INR 2,500,000 plan optimized at INR 2,440,000 and simulated. Ten-year scores were 35.8 untreated and 63.5 repaired. Prediction page showed BT-2.0, 100% equations, comparisons, and uncertainty caveats. Desktop visual check completed.
- Compatibility rendering used; hardware WebGL and Windows execution not tested. Import/download were API-tested. OS printing and cloud deployment not tested. No field validation.

Original VALIDATION.md describes an earlier release. Its numerical walkthrough must not be presented as version 2 results.
