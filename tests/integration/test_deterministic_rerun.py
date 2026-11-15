import uuid
from faultline.diagnosis.ranker import diagnose
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.learning.runner import learn_round
from faultline.sandbox.flows import Sandbox


def test_development_structural_rerun_is_identical(tmp_path):
    s=Sandbox(); s.observe(100)
    catalog=Catalog.from_telemetry(s.config.telemetry(),s.source_version)
    g=GraphStore('determinism-'+uuid.uuid4().hex,s.source_version,tmp_path)
    try:
        g.seed()
        a,b=load_scenarios('development')
        with Controller(s).incident(a) as public:
            learn_round(g,public,catalog)
        results=[]
        for _ in range(2):
            with Controller(s).incident(b) as public:
                results.append(diagnose(g,public).model_dump(exclude={'elapsed_ms'}))
        assert results[0]==results[1]
    finally:
        g.reset()
