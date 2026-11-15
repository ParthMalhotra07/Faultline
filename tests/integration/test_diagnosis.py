import uuid
from faultline.contracts import InspectionBudget, PublicIncident, ChangeRecord
from faultline.diagnosis.ranker import diagnose
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.graph.store import GraphStore
from faultline.graph.adapter import GraphError
from faultline.sandbox.flows import Sandbox
from faultline.ingestion.catalog import Catalog
from faultline.ingestion.inspector import Inspector
from faultline.ingestion.commit import ingest


def test_actual_graph_ranking_abstention_and_ties(tmp_path, monkeypatch):
    s = Sandbox(); s.observe(100)
    catalog = Catalog.from_telemetry(s.config.telemetry(), s.source_version)
    store = GraphStore('rank-' + uuid.uuid4().hex, s.source_version, tmp_path)
    try:
        store.seed()
        with Controller(s).incident(load_scenarios('development')[0]) as public:
            assert diagnose(store, public).status == 'insufficient_evidence'
            records = Inspector(catalog, InspectionBudget(max_sources=1,max_bytes=10000,max_records=100,timeout_ms=1000)).inspect('source:shared')
            ingest(store, catalog, records, 1)
            d = diagnose(store, public)
            assert d.selected_origin_id == 'config:currency'
            assert d.explanation_paths and d.evidence_ids
            changes = [ChangeRecord(change_id=f'change:{i}', changed_at_ms=99900, target_entity_id=k,
                public_summary='Service deployment', evidence_id=f'evidence:change:{i}')
                for i,k in enumerate(['service:pricing','service:billing'])]
            checkout_only = [o for o in public.observations if o.endpoint_id == 'endpoint:checkout']
            tied = diagnose(store, PublicIncident(observations=checkout_only, changes=changes))
            assert tied.status == 'ambiguous' and tied.selected_origin_id is None
            def broken(*args):
                raise GraphError('Incomplete retrieval')
            monkeypatch.setattr(store, 'paths', broken)
            assert diagnose(store, public).status == 'error'
    finally:
        store.reset()
