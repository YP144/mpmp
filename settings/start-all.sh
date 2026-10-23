#!/bin/bash
# Run FastAPI + Next.js in one container. If either dies, the container exits
# (so the orchestrator restarts it). SIGTERM is forwarded to both.
set -u
cd /usr/src/app

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

echo "[start-all] starting backend on 127.0.0.1:${BACKEND_PORT}"
fastapi run backend/main.py --host 127.0.0.1 --port "${BACKEND_PORT}" &
BE_PID=$!

echo "[start-all] starting frontend on 0.0.0.0:${FRONTEND_PORT}"
node node_modules/next/dist/bin/next start -H 0.0.0.0 -p "${FRONTEND_PORT}" &
FE_PID=$!

shutdown() {
  echo "[start-all] stopping..."
  kill -TERM "$BE_PID" "$FE_PID" 2>/dev/null
  wait "$BE_PID" "$FE_PID" 2>/dev/null
  exit 0
}
trap shutdown SIGTERM SIGINT

wait -n "$BE_PID" "$FE_PID"
CODE=$?
echo "[start-all] a process exited (code ${CODE}); stopping the other"
kill -TERM "$BE_PID" "$FE_PID" 2>/dev/null
wait 2>/dev/null
exit "$CODE"
