"""Prepare local source/evidence package; never publishes or submits."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
out=root/'artifacts/submission';out.mkdir(parents=True,exist_ok=True)
internal={'docs/BUILD_PLAN.md','docs/WORK_LOG.md',
          'scripts/audit_handoff.py','scripts/record_task.py'}
paths=[]
for folder in ['src','web','scripts','fixtures','protocol','docs']:
    paths += [p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts
              and p.relative_to(root).as_posix() not in internal]
for name in ['README.md','LICENSE','pyproject.toml',
             'requirements.lock','requirements-repro.txt','requirements-ui.txt',
             'requirements-vector.txt','.gitignore','.gitattributes',
             '.dockerignore','Dockerfile.demo']:
    paths.append(root/name)
paths += [p for p in (root/'tests').rglob('*.py')]
latest=json.loads((root/'artifacts/eval/latest.json').read_text())
paths += [p for p in (root/latest['directory']).iterdir() if p.is_file()]
# Keep the original completed run alongside the selected exact-protocol rerun.
# README links to its raw evidence and explains the metadata-only correction.
paths += [p for p in (root/'artifacts/eval/v1-20261114T060320Z-2f47a2').iterdir() if p.is_file()]
paths += [p for p in (root/'artifacts/eval/vector-exploratory').rglob('*') if p.is_file()]
load=json.loads((root/'artifacts/load/latest.json').read_text())
paths += [p for p in (root/load['directory']).iterdir() if p.is_file()]
ui=json.loads((root/'artifacts/ui/latest-attempt.json').read_text())
paths += [p for p in (root/ui['directory']).iterdir() if p.is_file() and p.suffix in ('.json','.png')]
landing=json.loads((root/'artifacts/ui/latest-landing.json').read_text())
paths += [p for p in (root/landing['directory']).iterdir() if p.is_file() and p.suffix in ('.json','.png')]
paths += [p for p in (root/'artifacts/pilot-transfer').glob('*.json')]
paths += [root/'artifacts/protocol-freeze.json',root/'artifacts/eval/latest.json',root/'artifacts/load/latest.json',root/'artifacts/ui/latest-attempt.json',root/'artifacts/ui/latest-landing.json']
paths += [root/'artifacts/T30-browser-report.json']
onboarding=json.loads((root/'artifacts/T30-browser-report.json').read_text())
paths += [p for p in (root/onboarding['directory']).iterdir()
          if p.is_file() and p.suffix in ('.json','.png')]
paths += [p for p in (root/'artifacts').glob('T*.log') if 'handoff-audit' not in p.name]
paths += [p for p in (root/'artifacts/hydra-smoke').iterdir() if p.is_file()]
paths=sorted(set(paths))
archive=out/'FAULTLINE-source-and-evidence.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
    for path in paths:
        relative=path.relative_to(root)
        assert not any(part in {'.runtime','.venv','.codex','.aws','.git','__pycache__'} for part in relative.parts)
        assert not path.name.startswith('.env') and path.name!='auth-token'
        z.write(path,relative.as_posix())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    assert all(p in z.namelist() for p in ['README.md','src/faultline/graph/adapter.py','web/index.html','protocol/v1/protocol.json'])
manifest=dict(prepared_at=datetime.now(timezone.utc).isoformat(),archive=archive.name,
    sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),files=len(paths),bytes=archive.stat().st_size,
    deadline_date='2026-11-16',timezone='Asia/Calcutta',exact_cutoff='09:00',
    organizer_format=['usable live app link','open-source GitHub repo','Loom walkthrough'],
    submitted=False,published=False,
    privacy='Whitelist package excludes local agent workspace, runtime credentials, environment files, virtualenvs, user/browser profiles and config backups',
    private_evaluator='Gold fixtures/raw predictions included for reproducibility; public API and learner do not serve/read these files',
    fallback_video='fallback-demo.webm',rehearsal='rehearsal.json',
    remaining=['Confirm whether the organizer submission-form cutoff differs from the event end','Resolve or disclose free Render instance storage limits',
        'Make and verify the existing GitHub repo public','Record and verify narrated Loom',
        'Publish truthful social posts with verified HydraDB handle','Submit and record actual confirmation'])
(out/'package-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(status='PASS',archive=str(archive.relative_to(root)),files=len(paths),bytes=archive.stat().st_size,sha256=manifest['sha256'],submitted=False),indent=2))
