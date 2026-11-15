import uuid
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.learning.runner import learn_round
from faultline.diagnosis.ranker import diagnose
from faultline.sandbox.flows import Sandbox


def test_live_learning_restart_and_reset_scopes(tmp_path):
    s = Sandbox(); s.observe(100)
    catalog = Catalog.from_telemetry(s.config.telemetry(), s.source_version)
    g = GraphStore('round-' + uuid.uuid4().hex, s.source_version, tmp_path)
    try:
        g.seed()
        with Controller(s).incident(load_scenarios('development')[0]) as public:
            trace = learn_round(g, public, catalog)
            assert trace['before']['status'] == 'insufficient_evidence'
            assert trace['after']['selected_origin_id'] == 'config:currency'
            assert trace['inspection']['source_id'] == 'source:shared'
            assert len(trace['ledger']) == 1
            snapshot = g.manifest_hash()
            s.reset()  # Runtime reset preserves the separate graph manifest.
            assert g.manifest_hash() == snapshot
        restored = GraphStore(g.namespace, s.source_version, tmp_path)
        with Controller(s).incident(load_scenarios('development')[1]) as public:
            assert diagnose(restored, public).selected_origin_id == 'config:currency'
        assert restored.manifest_hash() == snapshot
        restored.reset(); restored.seed()  # Explicit experiment reset removes learned edges.
        assert not restored.manifest['sources']
    finally:
        g = GraphStore(g.namespace, s.source_version, tmp_path)
        g.reset()
