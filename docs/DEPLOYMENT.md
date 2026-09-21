# Local production and later deployment

The default package requires no hosting account. Dependencies need internet for first installation; inference, optimization, geometry, fonts and data generation then run locally. Preserve the complete extracted folder.

## One-server local production

The ZIP contains a current `frontend/dist` build. After changing frontend source, rebuild from `frontend` using `npm.cmd run build` (Windows) or `npm run build` (Linux/macOS). Start the backend **after** the build exists:

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

Open http://127.0.0.1:8000. FastAPI serves the UI, assets and API from the same origin. No separate Vite server or Node runtime is needed to serve an existing production build. Python dependencies are still required. API documentation is at `/docs`.

## Separate frontend and backend

Copy `frontend/.env.example` to `frontend/.env` when configuring a different API location. Set `VITE_API_BASE_URL=https://your-api-host.example` before building; this value is compiled into the frontend. The default empty value uses `/api` on the same origin. `API_PROXY_TARGET` configures the development proxy only.

Copy `backend/.env.example` to `backend/.env` for backend configuration. Set `CORS_ORIGINS` to the exact frontend origin(s), comma-separated. The example SQLite URL is relative to the backend working directory; use an absolute URL for production volumes.

## Backend container

From the project root:

```bash
docker build -f backend/Dockerfile -t bridgetwin-api .
docker run --rm -p 127.0.0.1:8000:8000 -v bridgetwin-data:/app/data bridgetwin-api
```

This Dockerfile packages the backend only. Serve the frontend separately or extend the image to include its built assets in the directory expected by `app/main.py`. Container execution has not been validated in this delivery environment; the provided build is deployment preparation, not a deployed service.

## Persistence and access

Use a persistent volume for `backend/data`, and preserve `backend/models_saved` to retain the trained artifact. Back up SQLite with a consistent database backup rather than copying a live database arbitrarily. Uploaded observations and scenario history are persistent.

Run one Uvicorn worker for this shared-workspace prototype. All connected clients operate on the same simulated bridge. Revision checks reject stale scenarios, but this is not a full multi-user product. Before public deployment, add authenticated per-project authorization and a suitable reverse proxy with TLS. `API_WRITE_TOKEN` is an optional shared write gate; `VITE_API_WRITE_TOKEN` is visible in the browser and must not be treated as a secret or user authentication.

The SQLAlchemy repository permits a future PostgreSQL adapter, but its driver, migrations, isolation and concurrency behavior require separate validation. No cloud resources are created by the launchers.

## Troubleshooting

- **Python command missing:** install Python 3.12 with Add to PATH, then open a new terminal.
- **npm script execution blocked in PowerShell:** use `npm.cmd` or the provided `.cmd` launcher. The launcher does not change the machine-wide execution policy.
- **Backend unavailable:** keep its terminal open, check the printed exception and verify http://127.0.0.1:8000/api/health.
- **Port occupied:** stop the previous BridgeTwin instance. The root launcher reuses a healthy existing BridgeTwin API on port 8000.
- **MODEL NOT TRAINED:** run the documented training command and restart the backend. Physics-only estimates remain available when loading fails or auto-training is disabled.
- **Graphics limited:** the app automatically uses an interactive Three.js software projection when WebGL is unavailable. Hardware mode adds shadows and animated vehicles.
- **First install fails offline:** reconnect to install dependencies once; the app itself does not require a cloud API.
