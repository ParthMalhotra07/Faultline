"""Record an actually executed check and refresh the compact handoff."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('task')
p.add_argument('status', choices=['IN_PROGRESS', 'DONE', 'BLOCKED'])
p.add_argument('--command', default='')
p.add_argument('--exit-code', type=int)
p.add_argument('--output')
p.add_argument('--files', nargs='*', default=[])
p.add_argument('--limitations', nargs='*', default=[])
p.add_argument('--next', required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]
s = json.loads((root / 'STATE.json').read_text(encoding='utf-8'))
t = next(t for t in s['tasks'] if t['id'] == a.task)
if a.status in ('DONE', 'IN_PROGRESS'):
    assert all(next(x for x in s['tasks'] if x['id'] == d)['status'] == 'DONE' for d in t['depends_on'])
    assert not any(x['status'] == 'IN_PROGRESS' and x['id'] != a.task for x in s['tasks'])
if a.status == 'DONE':
    assert a.exit_code == 0 and a.output and (root / a.output).is_file()
    assert all(any(root.glob(x)) if any(c in x for c in '*?[') else (root / x).exists()
               for x in t['expected_outputs'])
t.update(status=a.status, next_action=a.next, limitations=a.limitations,
         blocker='; '.join(a.limitations) if a.status == 'BLOCKED' else None)
t['changed_files'] = sorted(set(t['changed_files'] + a.files + ['STATE.json', 'HANDOFF.md']))
if a.command:
    t['checks'].append(dict(command=a.command, working_directory=str(root), exit_code=a.exit_code,
                            status='PASS' if a.exit_code == 0 else 'FAIL', output_path=a.output))
if a.output:
    t['evidence_paths'] = sorted(set(t['evidence_paths'] + [a.output]))
if a.exit_code == 0 and a.output and a.files:
    # A current task may legitimately replace files verified by an earlier task.
    # Record the new exact hash only alongside an actual passing check.
    t['artifact_sha256'] = t.get('artifact_sha256', {}) | {
        x: hashlib.sha256((root / x).read_bytes()).hexdigest()
        for x in a.files if (root / x).is_file()}
if a.status == 'DONE':
    s['last_verified_implementation_task'] = a.task
for g in s['gates']:
    if g['task'] == a.task:
        if a.status == 'DONE': g['status'] = 'PASS'
        elif a.status == 'BLOCKED': g['status'] = 'BLOCKED'
s['blockers'] = [dict(task=x['id'], prerequisite=x['blocker']) for x in s['tasks'] if x['status'] == 'BLOCKED']
s['current_task_id'] = a.task
s['next_action'] = a.next
s['current_phase'] = t['phase']
s['implementation_started'] = any(x['status'] == 'DONE' and x['id'] != 'T00' for x in s['tasks'])
s['delivery_kind'] = 'implementation_in_progress'
s['session_log'].append(dict(at=datetime.now(timezone.utc).isoformat(), task=a.task, status=a.status,
                             command=a.command, output=a.output))
(root / 'STATE.json').write_text(json.dumps(s, indent=2) + '\n', encoding='utf-8')
done = ', '.join(x['id'] for x in s['tasks'] if x['status'] == 'DONE') or 'none'
blocked = '\n'.join('- ' + x['id'] + ': ' + x['blocker'] for x in s['tasks'] if x['status'] == 'BLOCKED') or 'None.'
(root / 'HANDOFF.md').write_text(f'''# Current handoff

Verified tasks: {done}. Current task: {a.task} ({a.status}).
Consult STATE.json for exact checks, artifact hashes, changed files, and limitations.
Failed checks remain preserved in artifacts and the task ledger.

## Next executable step

{a.next}

## Blockers

{blocked}

## Boundaries

No UI before T12 passes. No final held-out evaluation before protocol freeze.
Real HydraDB traversal required; mocks cannot pass graph gates.
Commits/pushes to the user-specified private GitHub repo are authorized from November 15; public visibility still needs confirmation.
No secret values in artifacts or chat. The host requires a live app link, public GitHub repo and Loom; exact cutoff remains unknown.
''', encoding='utf-8')
print(f'{a.task}: {a.status}')
