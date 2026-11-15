import argparse
import json
from pathlib import Path
from faultline.sandbox.flows import Sandbox
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.diagnosis.ranker import diagnose
from faultline.learning.runner import learn_round


def main():
    p = argparse.ArgumentParser(prog='faultline')
    p.add_argument('--experiment', default='demo')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor')
    reset = sub.add_parser('reset')
    reset.add_argument('--scope', choices=['sandbox','experiment'], required=True)
    for command in ['diagnose','learn']:
        q = sub.add_parser(command)
        q.add_argument('--case', required=True, choices=[c['case_id'] for split in ['development','learning'] for c in load_scenarios(split)])
    a = p.parse_args()
    s = Sandbox()
    if a.command == 'doctor' or a.command == 'reset' and a.scope == 'sandbox':
        s.reset()
        print(json.dumps({'scope': 'sandbox', 'observations': [o.model_dump() for o in s.observe(0)]}))
        return
    g = GraphStore(a.experiment, s.source_version)
    if a.command == 'reset':
        g.reset(); g.seed()
        print(json.dumps({'scope':'experiment','manifest_hash':g.manifest_hash()}))
        return
    if not g.manifest['claims']:
        g.seed()
    s.observe(100)
    catalog = Catalog.from_telemetry(s.config.telemetry(), s.source_version)
    cases = [c for split in ['development','learning'] for c in load_scenarios(split)]
    case = next(c for c in cases if c['case_id'] == a.case)
    with Controller(s).incident(case) as public:
        result = learn_round(g, public, catalog) if a.command == 'learn' else diagnose(g, public).model_dump()
    if a.command == 'learn':
        directory = Path('artifacts/rounds'); directory.mkdir(parents=True,exist_ok=True)
        (directory / f'{a.experiment}-{g.manifest["round"]}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
