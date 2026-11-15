"""Verify prepared local submission artifacts without claiming public delivery."""
import hashlib
import json
from pathlib import Path
import zipfile

root=Path(__file__).resolve().parents[1]
out=root/'artifacts/submission'
rehearsal=json.loads((out/'rehearsal.json').read_text())
assert rehearsal['status']=='PASS' and rehearsal['storyboard_elapsed_seconds']>=180
assert not rehearsal['console_errors'] and not rehearsal['page_errors']
assert len(rehearsal['stages'])>=8
video=out/'fallback-demo.webm'
assert video.is_file() and video.stat().st_size>1_000_000
assert all((out/name).is_file() for name in ('landing.png','healthy.png','learning.png','comparison.png'))

manifest=json.loads((out/'package-manifest.json').read_text())
archive=out/manifest['archive']
assert archive.is_file() and hashlib.sha256(archive.read_bytes()).hexdigest()==manifest['sha256']
assert manifest['submitted'] is False and manifest['published'] is False
assert manifest['organizer_format']==['usable live app link','open-source GitHub repo','Loom walkthrough']
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    names=set(z.namelist())
    assert len(names)==manifest['files']
    assert {'README.md','STATE.json','HANDOFF.md','Dockerfile.demo','docs/SUBMISSION.md',
        'docs/HOSTING.md','protocol/v1/protocol.json','src/faultline/graph/store.py'}<=names
    vector_latest=json.loads(z.read('artifacts/eval/vector-exploratory/latest.json'))
    assert {'requirements-vector.txt','protocol/vector-exploratory-v2.json',
        'src/faultline/evaluation/vector_baseline.py',
        'scripts/evaluate_vector_exploratory.py',
        'scripts/verify_vector_exploratory.py',
        f"{vector_latest['directory']}/aggregate.json",
        f"{vector_latest['directory']}/predictions.jsonl"}<=names
    assert not any(part in {'.runtime','.venv','.git','.aws','.codex','__pycache__'}
        for name in names for part in Path(name).parts)
    assert not any(Path(name).name in {'auth-token','.env'} or Path(name).name.startswith('.env.') for name in names)
    latest=json.loads(z.read('artifacts/eval/latest.json'))
    assert f"{latest['directory']}/aggregate.json" in names

ui=json.loads((root/'artifacts/ui/latest-attempt.json').read_text())
report=json.loads((root/ui['directory']/'report.json').read_text())
assert report['status']=='PASS'
landing=json.loads((root/'artifacts/ui/latest-landing.json').read_text())
landing_report=json.loads((root/landing['directory']/'report.json').read_text())
assert landing_report['status']=='PASS' and len(landing_report['checks'])>=8
assert any(name.endswith('00-hero-desktop.png') for name in landing_report['screenshots'])
print(f"PASS: 180-second silent rehearsal, browser reports, and {len(names)}-file source/evidence archive verified; no public repo, Loom or submission inferred.")
