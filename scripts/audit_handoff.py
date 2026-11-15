"""Audit completion records against disk and latest recorded file ownership."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
s=json.loads((root/'STATE.json').read_text())
tasks={t['id']:t for t in s['tasks']}
assert sum(t['status']=='IN_PROGRESS' for t in tasks.values())<=1
latest={}
current_verified={}
for t in tasks.values():
    if t['status']=='DONE':
        assert all(tasks[d]['status']=='DONE' for d in t['depends_on']),t['id']
        assert all(any(root.glob(p)) if any(c in p for c in '*?[') else (root/p).exists() for p in t['expected_outputs']),t['id']
        assert any(c['exit_code']==0 and c.get('output_path') and (root/c['output_path']).exists() for c in t['checks']),t['id']
        for name,sha in t.get('artifact_sha256',{}).items():latest[name]=(t['id'],sha)
    if t['status'] in ('IN_PROGRESS','BLOCKED') and any(c['exit_code']==0 and c.get('output_path') and
            (root/c['output_path']).exists() for c in t['checks']):
        for name,sha in t.get('artifact_sha256',{}).items():
            assert name in t['changed_files'],(t['id'],name)
            current_verified[name]=(t['id'],sha)
    if t['status']=='SKIPPED':
        assert not t['required'] and t['limitations'],t['id']
changes=[]
for name,(owner,sha) in latest.items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=sha:
        # A later active task may legitimately change an earlier verified file,
        # but only when it records a passing check and the exact current hash.
        if name not in current_verified or hashlib.sha256((root/name).read_bytes()).hexdigest()!=current_verified[name][1]:
            changes.append(dict(file=name,last_verified_owner=owner,reason='Changed after recorded verification; inspect latest task evidence'))
for name,(owner,sha) in current_verified.items():
    if hashlib.sha256((root/name).read_bytes()).hexdigest()!=sha:
        changes.append(dict(file=name,last_verified_owner=owner,reason='Active-task artifact changed after its recorded check'))
report=dict(done=sum(t['status']=='DONE' for t in tasks.values()),
    blocked=[t['id'] for t in tasks.values() if t['status']=='BLOCKED'],
    active=[t['id'] for t in tasks.values() if t['status']=='IN_PROGRESS'],
    optional_skipped=[t['id'] for t in tasks.values() if t['status']=='SKIPPED'],
    current_task_verified_files=len(current_verified),artifact_changes=changes)
(root/'artifacts/handoff-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
assert not changes,'Artifact hash discrepancies require review before final handoff'
