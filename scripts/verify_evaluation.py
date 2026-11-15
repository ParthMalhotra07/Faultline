"""Verify complete raw counts and immutable evaluation snapshots; no tuning."""
import json
from pathlib import Path
from faultline.evaluation.report import verify_protocol
from faultline.evaluation.scoring import score_predictions

root=Path(__file__).resolve().parents[1]
verify_protocol()
latest=json.loads((root/'artifacts/eval/latest.json').read_text())
directory=root/latest['directory']
complete=json.loads((directory/'COMPLETE.json').read_text())
rows=[json.loads(line) for line in (directory/'predictions.jsonl').read_text().splitlines()]
assert len(rows)==complete['predictions']==1044
snapshots=json.loads((directory/'snapshots.json').read_text())
assert len(snapshots)==63
assert all(s['evaluation_hash']==s['evaluation_hash_after'] for s in snapshots)
aggregate=json.loads((directory/'aggregate.json').read_text())
assert len(aggregate['rows'])==29
for group in aggregate['rows']:
    selected=[r for r in rows if r['method']==group['method'] and r['round']==group['round']]
    assert len(selected)==36
    assert all(group[k]==v for k,v in score_predictions(selected).items())
    assert len({(r['seed'],r['case_id']) for r in selected})==36
print(f'PASS: {len(rows)} raw predictions reproduce 29 aggregate points; all 63 held-out snapshot hashes unchanged.')
print(f'Artifacts: {directory}')
