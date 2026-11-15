#!/bin/sh
set -eu
: "${HYDRADB_TOKEN:?Configure the same private token for the bundled graph engine and app}"
: "${FAULTLINE_PUBLIC_ORIGIN:?Configure the exact HTTPS public app origin}"

mkdir -p /data/store /data/cache /data/experiments /app/.runtime
printf '%s' "$HYDRADB_TOKEN" > /data/auth-token
chmod 600 /data/auth-token
ln -sfn /data/experiments /app/.runtime/experiments

export CLOUD_PROVIDER=local LOCAL_PATH=/data/store
export GRAPH_NAMESPACE=default GRAPH_ID=default GRAPH_CELL_ID=cell-0 GRAPH_CELLS=cell-0 GRAPH_NODE_ID=node-0
export GRAPH_BOLT_NODE_ADDRESSES=node-0=127.0.0.1:7687 GRAPH_ADVERTISED_BOLT_ADDR=127.0.0.1:7687
export GRAPH_DATA_CACHE_DIR=/data/cache GRAPH_AUTH_TOKEN_FILE=/data/auth-token GRAPH_ALLOW_PLAINTEXT=true
export RUST_MIN_STACK=33554432 HYDRADB_URL=http://127.0.0.1:8443 FAULTLINE_BIND_HOST=0.0.0.0
# Render expects its web service on PORT=10000 unless the dashboard overrides it.
# Keep the existing 8765 default for local Docker and Railway.
if [ "${RENDER:-}" = true ] && [ -z "${PORT:-}" ]; then export PORT=10000; fi

/usr/local/bin/graph-node >/data/graph.log 2>&1 &
graphpid=$!
trap 'kill -TERM "$graphpid" "${apppid:-$graphpid}" 2>/dev/null || true' TERM INT
ready=0
for attempt in $(seq 1 90); do
    if curl --silent --fail http://127.0.0.1:9090/readyz >/dev/null; then ready=1; break; fi
    if ! kill -0 "$graphpid" 2>/dev/null; then echo 'HydraDB exited before readiness' >&2; exit 1; fi
    sleep 1
done
if [ "$ready" -ne 1 ]; then echo 'HydraDB readiness timed out' >&2; exit 1; fi
echo 'HydraDB ready; starting FAULTLINE public sandbox demo.'
python -u scripts/serve.py &
apppid=$!
wait "$apppid"
status=$?
kill -TERM "$graphpid" 2>/dev/null || true
wait "$graphpid" 2>/dev/null || true
exit "$status"
