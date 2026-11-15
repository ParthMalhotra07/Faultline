"""Preserve and correct inherited metadata in the initial running evaluator only.

No selected answer, status, case, seed, aggregate count, or scoring rule changes.
The original rows remain available; copied graph timings are not text timings.
"""
import json
from pathlib import Path
import shutil

root=Path(__file__).resolve().parents[1]
latest=json.loads((root/'artifacts/eval/latest.json').read_text())
directory=root/latest['directory']
source=directory/'predictions.jsonl'
backup=directory/'predictions-original-metadata.jsonl'
if backup.exists():
    raise SystemExit('Correction already applied; do not overwrite preserved raw rows')
shutil.copyfile(source,backup)
rows=[json.loads(x) for x in source.read_text().splitlines()]
for row in rows:
    if row['method']=='same-evidence-token-overlap':
        row['elapsed_ms']=None
        row['evidence_ids']=[]
        row['metadata_note']='Initial text timing was not independently measured; no per-document citations emitted.'
source.write_text(''.join(json.dumps(row)+'\n' for row in rows))
(directory/'metadata-correction.json').write_text(json.dumps(dict(
    changed='Text-baseline timing marked unmeasured and inherited graph citations removed',
    original=backup.name,prediction_fields_changed=False,scoring_changed=False),indent=2)+'\n')
print('Corrected text-only metadata; all predictions/statuses/counts unchanged; original rows preserved.')
