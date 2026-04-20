#!/usr/bin/env bash
set -euo pipefail

uvicorn app.index:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}"
