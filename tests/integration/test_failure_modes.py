import copy
import uuid
import pytest
from faultline.graph.adapter import GraphError
from faultline.graph.store import GraphStore
from faultline.sandbox.flows import Sandbox
from faultline.ingestion.catalog import Catalog
from faultline.ingestion.inspector import Inspector
from faultline.ingestion.commit import ingest
from faultline.learning.runner import DEFAULT_BUDGET, learn_round
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.diagnosis.ranker import diagnose


def test_partial_source_stale_restart_and_read_only_diagnosis(tmp_path, monkeypatch):
    s=Sandbox(); s.observe(100)
    catalog=Catalog.from_telemetry(s.config.telemetry(),s.source_version)
    records=Inspector(catalog,DEFAULT_BUDGET).inspect('source:shared')
    g=GraphStore('fail-'+uuid.uuid4().hex,s.source_version,tmp_path)
    try:
        g.seed()
        original=g.adapter.execute
        commits=[]
        def fail_second(template, params):
            if template=='claim_commit':
                commits.append(params)
                if len(commits)==2:
                    raise RuntimeError('interrupted second claim')
            return original(template,params)
        monkeypatch.setattr(g.adapter,'execute',fail_second)
        with pytest.raises(RuntimeError):
            ingest(g,catalog,records,1)
        monkeypatch.setattr(g.adapter,'execute',original)
        assert not any(p['entity_ids'][-1].startswith('config:') for p in g.paths('endpoint:checkout'))
        ingest(g,catalog,records,1)
        with pytest.raises(GraphError,match='source version'):
            GraphStore(g.namespace,'stale',tmp_path)
        with Controller(s).incident(load_scenarios('development')[1]) as public:
            before=copy.deepcopy(g.manifest)
            assert diagnose(g,public).status=='supported'
            assert g.manifest==before
        stale=records[0].model_copy(update={'source_version':'stale'})
        with pytest.raises(ValueError,match='Stale'):
            ingest(g,catalog,[stale],1)
    finally:
        g.reset()


def test_round_trace_is_an_immutable_snapshot(tmp_path):
    s=Sandbox(); s.observe(100)
    catalog=Catalog.from_telemetry(s.config.telemetry(),s.source_version)
    g=GraphStore('trace-'+uuid.uuid4().hex,s.source_version,tmp_path)
    try:
        g.seed()
        with Controller(s).incident(load_scenarios('development')[0]) as public:
            trace=learn_round(g,public,catalog)
            saved=copy.deepcopy(trace['snapshot'])
            g.manifest['round']+=1
            assert trace['snapshot']==saved
    finally:
        g.reset()
