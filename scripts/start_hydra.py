"""Start isolated local HydraDB, pinned by immutable official image digest."""
from pathlib import Path
import secrets
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'ghcr.io/hydra-db/hydradb@sha256:ab71d651fefee13ebb23eb56d72316065bdca563ff7587442e07be663f2bf880'
local = ROOT / '.runtime/hydra'
local.mkdir(parents=True, exist_ok=True)
for name in ('store', 'cache'):
    (local / name).mkdir(exist_ok=True)
token = local / 'auth-token'
if not token.exists():
    token.write_text(secrets.token_urlsafe(48), encoding='utf-8')
env = dict(CLOUD_PROVIDER='local', LOCAL_PATH='/data/store', GRAPH_NAMESPACE='default',
           GRAPH_ID='default', GRAPH_CELL_ID='cell-0', GRAPH_CELLS='cell-0', GRAPH_NODE_ID='node-0',
           GRAPH_BOLT_NODE_ADDRESSES='node-0=127.0.0.1:7687', GRAPH_ADVERTISED_BOLT_ADDR='127.0.0.1:7687',
           GRAPH_DATA_CACHE_DIR='/data/cache', GRAPH_AUTH_TOKEN_FILE='/data/auth-token',
           GRAPH_ALLOW_PLAINTEXT='true', RUST_MIN_STACK='33554432')
probe = subprocess.run(['docker', 'container', 'inspect', 'faultline-hydra', '--format', '{{.State.Running}}'],
                       capture_output=True, text=True)
if probe.returncode == 0:
    if probe.stdout.strip() != 'true':
        subprocess.run(['docker', 'start', 'faultline-hydra'], check=True)
else:
    args = ['docker', 'run', '-d', '--name', 'faultline-hydra', '--cpus', '4', '--memory', '4g',
            '-p', '127.0.0.1:18443:8443', '-p', '127.0.0.1:19090:9090',
            '--mount', f'type=bind,source={local},target=/data']
    for k, v in env.items():
        args += ['-e', f'{k}={v}']
    subprocess.run(args + [IMAGE], check=True)
for _ in range(30):
    try:
        with urllib.request.urlopen('http://127.0.0.1:19090/readyz', timeout=1) as r:
            if r.status == 200:
                print('HydraDB ready; auth file configured locally, never printed.')
                break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit('HydraDB readiness failed; inspect container runtime logs.')
