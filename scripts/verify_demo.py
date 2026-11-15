"""Clean-environment verification in a fresh, disposable application scope."""
import json
import platform
import tempfile
import uuid
from faultline.sandbox.flows import Sandbox
from faultline.evaluation.controller import Controller,load_scenarios
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.learning.runner import learn_round
from faultline.diagnosis.ranker import diagnose
from faultline.evaluation.report import verify_protocol

verify_protocol()
s=Sandbox(); assert all(o.status=='healthy' for o in s.observe(100))
catalog=Catalog.from_telemetry(s.config.telemetry(),s.source_version)
with tempfile.TemporaryDirectory(prefix='faultline-clean-demo-') as directory:
    g=GraphStore('clean-'+uuid.uuid4().hex,s.source_version,directory)
    try:
        g.seed()
        a,b=load_scenarios('development')
        with Controller(s).incident(a) as public:
            assert diagnose(g,public).status=='insufficient_evidence'
            trace=learn_round(g,public,catalog)
            assert trace['after']['selected_origin_id']=='config:currency'
        assert all(o.status=='healthy' for o in s.observe(100))
        restored=GraphStore(g.namespace,s.source_version,directory)
        snapshot=restored.manifest_hash()
        with Controller(s).incident(b) as public:
            d=diagnose(restored,public)
            assert d.selected_origin_id=='config:currency'
        assert snapshot==restored.manifest_hash()
        print(json.dumps(dict(status='PASS',python=platform.python_version(),initial='insufficient_evidence',
            learned=trace['after']['selected_origin_id'],transfer=d.selected_origin_id,
            committed_claims=len(restored.manifest['claims']),source_version=s.source_version,
            reset_restored_health=True,restart_retained_learning=True,heldout_run=False),indent=2))
    finally:
        g.reset()
