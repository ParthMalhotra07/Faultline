"""Freeze experiment rules BEFORE any held-out diagnosis. Refuses overwrite."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from faultline.sandbox.flows import Sandbox
from faultline.ingestion.catalog import Catalog
from faultline.learning.runner import DEFAULT_BUDGET

root=Path(__file__).resolve().parents[1]
directory=root/'protocol/v1'
if directory.exists():
    raise SystemExit('Protocol v1 already exists; no silent re-freeze')
directory.mkdir()
s=Sandbox(); s.observe(100)
catalog=Catalog.from_telemetry(s.config.telemetry(),s.source_version)
for meta in catalog.metadata():
    _,blob=catalog.read(meta.source_id)
    (directory/(meta.source_id.split(':')[1]+'.json')).write_bytes(blob)
files=sorted([str(p.relative_to(root)).replace('\\','/') for p in (root/'src').rglob('*.py')]
    + [f'fixtures/private/{x}.json' for x in ['development','learning','heldout']]
    + ['fixtures/public/topology.json','pyproject.toml','requirements.lock'])
protocol=dict(version='v1',status='FROZEN',frozen_at=datetime.now(timezone.utc).isoformat(),
    source_version=s.source_version, fixture_label='controlled synthetic executable commerce sandbox',
    splits={x:[c['case_id'] for c in json.loads((root/f'fixtures/private/{x}.json').read_text())]
            for x in ['development','learning','heldout']},
    seeds=[17,29,43],learning_order='listed order, same for every method and seed',
    learning_incidents=6,snapshot_points=7,inspection_budget=DEFAULT_BUDGET.model_dump(),
    inspection_budget_calibration='Development pilot consumed one source; caps chosen above actual complete source sizes, no held-out tuning.',
    catalog=[m.model_dump() for m in catalog.metadata()],
    catalog_files={m.source_id:m.source_id.split(':')[1]+'.json' for m in catalog.metadata()},
    initial_policy='Known handler/call topology only; config access sources initially uninspected',
    methods=['frozen','random','adaptive','same-evidence-token-overlap'],
    lexical_baseline='Exact acquired typed config-access evidence; set token overlap, no vectors or graph traversal',
    ranking='Distinct failing coverage desc, healthy contradictions asc, shortest path asc; equal evidence abstains',
    recent_change_window_ms=60000,graph_depth_domain_edges=3,max_query_rows=1000,query_timeout_ms=5000,
    holdout_inspections=False,metrics='Correct supported selected origin / ALL 12 attempted cases; errors and abstentions count non-correct',
    ablation='Disable pricing READS_CONFIG currency learned claims in isolated copy of final adaptive snapshot; score all heldout cases',
    llm=None,load=dict(clients=[1,5,10],requests_per_level=500,warmup_per_level=10),
    file_hashes={f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files},
    limitations=['Small controlled topology; two evidence sources; no statistical superiority claim.',
                'Holdout differs in values/workloads/change ordering, not app topology; symptom vocabulary is intentionally generic.',
                'Remaining time and organizer cutoff are unconfirmed.'])
raw=json.dumps(protocol,indent=2,sort_keys=True)+'\n'
(directory/'protocol.json').write_text(raw)
record=dict(frozen_at=protocol['frozen_at'],protocol='protocol/v1/protocol.json',sha256=hashlib.sha256((directory/'protocol.json').read_bytes()).hexdigest())
(root/'artifacts/protocol-freeze.json').write_text(json.dumps(record,indent=2)+'\n')
print('FROZEN v1: 6 learning incidents, 7 snapshots, 12 held-out cases, seeds 17/29/43; no held-out diagnosis has run.')
