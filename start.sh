#!/usr/bin/env bash
set -euo pipefail

exec gunicorn app:app \
  --bind 0.0.0.0:${PORT:-5000} \
  --workers ${GUNICORN_WORKERS:-2} \
  --threads ${GUNICORN_THREADS:-4} \
  --timeout ${GUNICORN_TIMEOUT:-120}
