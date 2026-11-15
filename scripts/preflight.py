"""Redacted, repeatable environment inspection; never prints environment values."""
import json
import os
from pathlib import Path
import platform
import subprocess
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
commands = [
    ['python', '--version'], ['node', '--version'], ['git', '--version'],
    ['git', 'rev-parse', '--show-toplevel'], ['git', 'status', '--short'],
    ['wsl.exe', '--list', '--quiet'], ['docker', '--version'],
    ['docker', 'info', '--format', '{{.ServerVersion}}'],
    ['wsl.exe', '-d', 'Ubuntu', '--', 'bash', '-lc',
     'python3 --version; command -v cargo; command -v cc; sudo -n true'],
]
results = []
for command in commands:
    try:
        r = subprocess.run(command, cwd=ROOT, capture_output=True, timeout=20)
        def decode(b):
            return b.decode('utf-16-le' if b'\x00' in b else 'utf-8', errors='replace').strip()
        results.append(dict(command=command, exit_code=r.returncode,
                            stdout=decode(r.stdout), stderr=decode(r.stderr)))
    except (OSError, subprocess.TimeoutExpired) as e:
        results.append(dict(command=command, exit_code=None, error=type(e).__name__))
try:
    with urllib.request.urlopen('https://api.github.com/repos/hydra-db/hydradb/commits/main', timeout=15) as r:
        network = dict(status=r.status, hydradb_commit=json.load(r)['sha'])
except Exception as e:
    network = dict(error=type(e).__name__)
report = dict(checked_at=datetime.now(timezone.utc).isoformat(), workspace=str(ROOT),
              platform=platform.platform(), python=platform.python_version(),
              probes=results, network=network,
              credential_presence={k: bool(v) for k, v in os.environ.items()
                                   if any(s in k.upper() for s in ('HYDRA', 'OPENAI_API', 'ANTHROPIC_API'))},
              confirmed_cutoff=None, remaining_time=None)
out = ROOT / 'artifacts/preflight-retry.json'
out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, indent=2))
