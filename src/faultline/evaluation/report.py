"""Private held-out orchestration. Gold labels never enter learner records."""
import copy
import hashlib
import json
import random
import time
import uuid
from pathlib import Path
from faultline.contracts import EvidenceSource, InspectionBudget
from faultline.diagnosis.ranker import diagnose
from faultline.evaluation.baselines import run_round, token_overlap
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.evaluation.scoring import score_predictions
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.sandbox.flows import Sandbox

ROOT=Path(__file__).resolve().parents[3]


def verify_protocol():
    raw=(ROOT/'protocol/v1/protocol.json').read_bytes()
    frozen=json.loads((ROOT/'artifacts/protocol-freeze.json').read_text())
    if hashlib.sha256(raw).hexdigest()!=frozen['sha256']:
        raise RuntimeError('Frozen protocol hash mismatch')
    protocol=json.loads(raw)
    for name, sha in protocol['file_hashes'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=sha:
            raise RuntimeError(f'Frozen input changed: {name}; do not tune on holdout')
    for meta in protocol['catalog']:
        blob=(ROOT/'protocol/v1'/protocol['catalog_files'][meta['source_id']]).read_bytes()
        if hashlib.sha256(blob).hexdigest()!=meta['sha256']:
            raise RuntimeError('Frozen catalog content changed')
    return protocol


def clone_snapshot(snapshot, namespace):
    g=GraphStore(namespace,snapshot['source_version'])
    g.seed()
    for key, c in snapshot['claims'].items():
        if c['source_id']=='source:topology':
            continue
        g.commit_claim(key,c['from_id'],c['kind'],c['to_id'],c['evidence_id'],c['sha256'],c['source_id'],c['round'])
    g.manifest['evidence']=copy.deepcopy(snapshot['evidence'])
    g.manifest['sources']=copy.deepcopy(snapshot['sources'])
    g.manifest['round']=snapshot['round']
    g._save()
    return g


def evaluate():
    protocol=verify_protocol()
    run_id='v1-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex[:6]
    out=ROOT/'artifacts/eval'/run_id
    out.mkdir(parents=True)
    (out/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    (out/'commands.txt').write_text('HYDRADB_TOKEN_FILE=<local ignored auth file> .venv/Scripts/python.exe scripts/evaluate.py\n')
    (out/'environment.json').write_text(json.dumps(dict(runtime='official HydraDB 0.4.0 Docker, local Windows bind store',
        image='sha256:ab71d651fefee13ebb23eb56d72316065bdca563ff7587442e07be663f2bf880',
        query_rows=1000,timeout_ms=5000,source_version=protocol['source_version']),indent=2))
    entries={}
    for data in protocol['catalog']:
        meta=EvidenceSource(**data)
        entries[meta.source_id]=(meta,(ROOT/'protocol/v1'/protocol['catalog_files'][meta.source_id]).read_bytes())
    catalog=Catalog(entries,protocol['source_version'])
    budget=InspectionBudget(**protocol['inspection_budget'])
    s=Sandbox()
    learning=load_scenarios('learning')
    heldout=load_scenarios('heldout')
    predictions=[]; snapshots=[]; inspections=[]
    prediction_file=(out/'predictions.jsonl').open('w',encoding='utf-8')
    inspection_file=(out/'inspections.jsonl').open('w',encoding='utf-8')
    try:
        for seed in protocol['seeds']:
            for method in ['frozen','random','adaptive']:
                rng=random.Random(seed)
                g=GraphStore(f'{run_id}-{seed}-{method}',protocol['source_version'])
                g.seed()
                for round_no in range(7):
                    if round_no:
                        with Controller(s).incident(learning[round_no-1]) as public:
                            trace=run_round(method,g,public,catalog,rng,budget)
                        entry=dict(seed=seed,method=method,round=round_no,budget=trace['budget'],ledger=trace['ledger'],inspection=trace['inspection'])
                        inspections.append(entry); inspection_file.write(json.dumps(entry)+'\n'); inspection_file.flush()
                    snapshot=copy.deepcopy(g.manifest)
                    snapshot_file=f'snapshot-{seed}-{method}-{round_no}.json'
                    (out/snapshot_file).write_text(json.dumps(snapshot,indent=2)+'\n')
                    isolated=clone_snapshot(snapshot,f'{run_id}-{seed}-{method}-eval-{round_no}')
                    manifest_before=isolated.manifest_hash()
                    snapshots.append(dict(seed=seed,method=method,round=round_no,file=snapshot_file,
                        training_hash=g.manifest_hash(),evaluation_hash=manifest_before))
                    for case in heldout:
                        with Controller(s).incident(case) as public:
                            t=time.perf_counter()
                            start_queries=len(isolated.adapter.trace)
                            d=diagnose(isolated,public)
                            row=dict(seed=seed,method=method,round=round_no,case_id=case['case_id'],
                                expected=case['expected_origin_id'],selected=d.selected_origin_id,status=d.status,
                                manifest_hash=d.snapshot_manifest_hash,evidence_ids=d.evidence_ids,
                                elapsed_ms=(time.perf_counter()-t)*1000,query_count=len(isolated.adapter.trace)-start_queries)
                            predictions.append(row); prediction_file.write(json.dumps(row)+'\n'); prediction_file.flush()
                            if method=='adaptive':
                                text_started=time.perf_counter()
                                text=token_overlap(isolated,public)
                                textrow=row | dict(method='same-evidence-token-overlap',selected=text['selected_origin_id'],status=text['status'],query_count=0,
                                    elapsed_ms=(time.perf_counter()-text_started)*1000,evidence_ids=[])
                                predictions.append(textrow); prediction_file.write(json.dumps(textrow)+'\n'); prediction_file.flush()
                        assert manifest_before==isolated.manifest_hash(), 'Held-out diagnosis changed snapshot'
                    snapshots[-1]['evaluation_hash_after']=isolated.manifest_hash()
                    print(f'{seed} {method} round {round_no}: 12 read-only cases completed',flush=True)
                    if method=='adaptive' and round_no==6:
                        ablated=copy.deepcopy(snapshot)
                        ablated['claims']={key:c for key,c in ablated['claims'].items() if not (
                            c['from_id']=='service:pricing' and c['kind']=='READS_CONFIG' and c['to_id']=='config:currency')}
                        ablation=clone_snapshot(ablated,f'{run_id}-{seed}-ablation')
                        ablation_before=ablation.manifest_hash()
                        for case in heldout:
                            with Controller(s).incident(case) as public:
                                d=diagnose(ablation,public)
                                row=dict(seed=seed,method='ablation-no-pricing-currency',round=6,case_id=case['case_id'],
                                    expected=case['expected_origin_id'],selected=d.selected_origin_id,status=d.status,
                                    manifest_hash=d.snapshot_manifest_hash,evidence_ids=d.evidence_ids,elapsed_ms=d.elapsed_ms)
                                predictions.append(row); prediction_file.write(json.dumps(row)+'\n'); prediction_file.flush()
                            assert ablation_before==ablation.manifest_hash()
                        ablation.reset()
                    isolated.reset()
                    isolated.adapter.trace.clear()
                g.reset()
                print(f'{seed} {method} complete',flush=True)
        aggregate=[]
        for method in protocol['methods']+['ablation-no-pricing-currency']:
            for round_no in ([6] if method.startswith('ablation') else range(7)):
                rows=[r for r in predictions if r['method']==method and r['round']==round_no]
                aggregate.append(dict(method=method,round=round_no,**score_predictions(rows)))
        (out/'aggregate.json').write_text(json.dumps(dict(protocol='v1',fixture_label=protocol['fixture_label'],
            seeds=protocol['seeds'],cases_per_seed=12,rows=aggregate,limitations=protocol['limitations']),indent=2)+'\n')
        (out/'snapshots.json').write_text(json.dumps(snapshots,indent=2)+'\n')
        assert len(predictions)==1044, f'Unexpected prediction count: {len(predictions)}'
        verify_protocol()
        (out/'COMPLETE.json').write_text(json.dumps(dict(status='PASS',predictions=len(predictions),snapshots=len(snapshots)),indent=2)+'\n')
        (ROOT/'artifacts/eval/latest.json').write_text(json.dumps(dict(run_id=run_id,directory=str(out.relative_to(ROOT)).replace('\\','/')),indent=2)+'\n')
        print(f'COMPLETE {out}: {len(predictions)} private predictions; no held-out learner writes',flush=True)
    finally:
        prediction_file.close(); inspection_file.close()
    return out
