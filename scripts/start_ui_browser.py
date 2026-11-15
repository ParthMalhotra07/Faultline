"""Start local headless QA service, bound to loopback and resource limited."""
from pathlib import Path
import subprocess
import time
import urllib.request

root=Path(__file__).resolve().parents[1]
deps=root/'.runtime/ui-playwright-python'; deps.mkdir(parents=True,exist_ok=True)
image='mcr.microsoft.com/playwright/python@sha256:38dd67fc654b56b3cba611e4c8eb71cd33750e1cd29eea2a5dc00b484817a75f'
probe=subprocess.run(['docker','inspect','faultline-ui-browser','--format','{{.State.Running}}'],capture_output=True,text=True)
if probe.returncode or probe.stdout.strip()!='true':
    subprocess.run(['docker','run','--rm','-d','--init','--name','faultline-ui-browser',
        '--cpus','2','--memory','2g','--shm-size','1g','-p','127.0.0.1:13000:3000',
        '--mount',f'type=bind,source={root/"scripts"},target=/qa,readonly',
        '--mount',f'type=bind,source={deps},target=/deps','-e','PYTHONPATH=/deps',
        image,'python','/qa/playwright_server.py'],check=True)
for _ in range(180):
    try:
        urllib.request.urlopen('http://127.0.0.1:13000',timeout=1)
        break
    except urllib.error.HTTPError:
        break  # WebSocket endpoint is alive even if plain HTTP returns an error.
    except OSError:
        time.sleep(.5)
else:
    raise SystemExit('Playwright service startup failed; inspect its logs')
print('Headless QA service ready at ws://127.0.0.1:13000/ (separate container, no desktop input)')
