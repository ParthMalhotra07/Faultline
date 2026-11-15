import uuid
import pytest
from faultline.contracts import InspectionBudget
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.ingestion.inspector import Inspector
from faultline.ingestion.commit import ingest
from faultline.sandbox.flows import Sandbox


def test_evidence_validation_recovery_and_idempotence(tmp_path, monkeypatch):
    s = Sandbox(); s.observe(100)
    c = Catalog.from_telemetry(s.config.telemetry(), s.source_version)
    records = Inspector(c, InspectionBudget(max_sources=1,max_bytes=10000,max_records=100,timeout_ms=1000)).inspect('source:shared')
    g = GraphStore('ingest-' + uuid.uuid4().hex, s.source_version, tmp_path)
    try:
        g.seed()
        tampered = records[0].model_copy(update={'observed_at_ms': 999})
        with pytest.raises(ValueError):
            ingest(g, c, [tampered], 1)
        original = g.adapter.execute
        def fail(template, params):
            if template == 'claim_support':
                raise RuntimeError('simulated interrupted write')
            return original(template, params)
        monkeypatch.setattr(g.adapter, 'execute', fail)
        with pytest.raises(RuntimeError):
            ingest(g, c, records, 1)
        monkeypatch.setattr(g.adapter, 'execute', original)
        assert not any(p['entity_ids'][-1].startswith('config:') for p in g.paths('endpoint:checkout'))
        ingest(g, c, records, 1)
        assert any(p['entity_ids'][-1] == 'config:currency' for p in g.paths('endpoint:checkout'))
        before = g.manifest_hash()
        ingest(g, c, records, 1)
        assert g.manifest_hash() == before
    finally:
        g.reset()
