"""Development only. Never opens the final holdout manifest."""
import json
from pathlib import Path
import uuid
from faultline.sandbox.flows import Sandbox
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.learning.runner import learn_round
from faultline.diagnosis.ranker import diagnose

s = Sandbox(); s.observe(100)
catalog = Catalog.from_telemetry(s.config.telemetry(), s.source_version)
g = GraphStore('pilot-' + uuid.uuid4().hex, s.source_version)
a, b = load_scenarios('development')
out = Path('artifacts/pilot-transfer')
out.mkdir(parents=True,exist_ok=True)
g.seed()
with Controller(s).incident(b) as public_b:
    before = diagnose(g, public_b)
with Controller(s).incident(a) as public_a:
    learning = learn_round(g, public_a, catalog)
snapshot = g.manifest_hash()
with Controller(s).incident(b) as public_b:
    after = diagnose(g, public_b)
assert snapshot == g.manifest_hash(), 'Read-only B changed learned snapshot'
new = [p.model_dump() for p in after.explanation_paths if p.candidate_id == after.selected_origin_id]
report = dict(status='PASS' if before.selected_origin_id is None and after.selected_origin_id == b['expected_origin_id'] else 'FAIL',
              label='development pilot only; no held-out accuracy measurement',
              monitoring='A monitors checkout+renewals; B monitors refunds+renewals; each executes all real flows',
              before=before.model_dump(), learning=learning, after=after.model_dump(),
              new_supporting_paths=new, snapshot_hash=snapshot)
(out / 'result.json').write_text(json.dumps(report,indent=2)+'\n')
assert report['status'] == 'PASS', 'Development transfer did not pass; preserve report and investigate'
print('PASS: development B changed from insufficient evidence to config:currency after A learned pricing READS_CONFIG currency.')
print('Returned path: endpoint:refunds -> service:refunds -> service:pricing -> config:currency, with claim/evidence IDs in result.json.')
