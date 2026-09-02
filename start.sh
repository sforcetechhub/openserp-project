#!/bin/sh
set -eu

OPENSERP_PORT="${OPENSERP_SERVER_PORT:-7000}"
API_PORT="${PORT:-8000}"

echo "starting OpenSERP on 127.0.0.1:${OPENSERP_PORT}"
/usr/local/bin/openserp serve -a 127.0.0.1 -p "${OPENSERP_PORT}" &
OPENSERP_PID=$!

i=0
while [ "${i}" -lt 30 ]; do
  if wget --quiet --tries=1 --spider "http://127.0.0.1:${OPENSERP_PORT}/health"; then
    echo "OpenSERP is ready"
    break
  fi
  if ! kill -0 "${OPENSERP_PID}" 2>/dev/null; then
    echo "OpenSERP exited during startup" >&2
    exit 1
  fi
  i=$((i + 1))
  sleep 2
done

echo "starting API on 0.0.0.0:${API_PORT}"
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port "${API_PORT}"
