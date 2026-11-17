#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [ ! -x backend/.venv/bin/python ]; then python3 -m venv backend/.venv; fi
if [ ! -f backend/.venv/.bridgetwin-installed ]; then
  backend/.venv/bin/python -m pip install -r backend/requirements.txt
  touch backend/.venv/.bridgetwin-installed
fi
if [ ! -f frontend/node_modules/.package-lock.json ]; then npm --prefix frontend ci; fi
node scripts/dev.mjs
