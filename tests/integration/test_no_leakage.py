import ast
import json
from pathlib import Path
import uuid
from faultline.contracts import PublicIncident
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.sandbox.flows import Sandbox
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.learning.runner import learn_round


def test_runtime_captured_learner_input_is_public_only(tmp_path):
    s=Sandbox(); s.observe(100)
    catalog=Catalog.from_telemetry(s.config.telemetry(),s.source_version)
    g=GraphStore('leak-'+uuid.uuid4().hex,s.source_version,tmp_path)
    try:
        g.seed()
        with Controller(s).incident(load_scenarios('development')[0]) as public:
            trace=learn_round(g,public,catalog)
        assert PublicIncident.model_validate(trace['public_input']).model_dump()==trace['public_input']
        text=json.dumps(trace)
        assert not any(x in text for x in ['expected_origin_id','fault_value','private_fault_id','fixtures/private','development-01','gold_label'])
        assert all(set(s.model_dump())=={'source_id','owner_service_ids','kind','source_version','sha256','estimated_bytes','inspected'} for s in catalog.metadata())
    finally:
        g.reset()


def test_learner_modules_have_no_private_imports_or_shell_tools():
    for folder in ['learning','diagnosis','ingestion']:
        for path in Path('src/faultline',folder).glob('*.py'):
            text=path.read_text()
            ast.parse(text)
            assert not any(x in text for x in ['faultline.evaluation','subprocess','os.system','fixtures/private'])
