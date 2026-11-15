"""Retrospective Qdrant comparator; never changes frozen v1 or learner state."""
from datetime import datetime, timezone
from importlib.metadata import version
import hashlib
import json
from pathlib import Path
import platform
import time
from fastembed import TextEmbedding
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.evaluation.report import verify_protocol
from faultline.evaluation.scoring import score_predictions
from faultline.evaluation.vector_baseline import EmbedCache, SameEvidenceVectorIndex
from faultline.sandbox.flows import Sandbox

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / 'protocol/vector-exploratory-v2.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    rules = json.loads(RULES.read_text(encoding='utf-8'))
    assert rules['status'] == 'FROZEN_EXPLORATORY'
    assert sha(ROOT / 'src/faultline/evaluation/vector_baseline.py') == rules['baseline_sha256']
    assert sha(ROOT / 'scripts/evaluate_vector_exploratory.py') == rules['runner_sha256']
    assert sha(ROOT / 'protocol/v1/protocol.json') == rules['v1_protocol_sha256']
    latest_path = ROOT / 'artifacts/eval/latest.json'
    latest_before = sha(latest_path)
    source = json.loads(latest_path.read_text())
    assert source['directory'] == rules['source_run_directory']
    source_dir = ROOT / source['directory']
    assert sha(source_dir / 'snapshots.json') == rules['v1_snapshots_index_sha256']
    verify_protocol()

    model_file = (ROOT / '.runtime/vector-models/models--Qdrant--bge-small-en-v1.5-onnx-Q'
                  / 'snapshots' / rules['model_revision'] / 'model_optimized.onnx')
    assert sha(model_file) == rules['model_onnx_sha256'], 'Embedding model file changed'
    for package, expected in rules['package_versions'].items():
        assert version(package) == expected, f'{package} version changed'
    snapshot_index = json.loads((source_dir / 'snapshots.json').read_text())
    expected_snapshots = {(seed, round_no): f'snapshot-{seed}-adaptive-{round_no}.json'
                          for seed in rules['seeds'] for round_no in range(rules['rounds'])}
    indexed_snapshots = {(s['seed'], s['round']): s['file'] for s in snapshot_index
                         if s['method'] == 'adaptive'}
    assert indexed_snapshots == expected_snapshots, 'Source snapshot index changed'

    model = TextEmbedding(model_name=rules['model_name'],
                          cache_dir=str(ROOT / '.runtime/vector-models'), threads=2)
    embed = EmbedCache(model)
    sandbox = Sandbox()
    heldout = load_scenarios('heldout')
    assert len(heldout) == rules['cases_per_seed']
    v1 = json.loads((source_dir / 'aggregate.json').read_text())
    adaptive = {r['round']: r for r in v1['rows'] if r['method'] == 'adaptive'}
    assert len(adaptive) == rules['rounds']

    run_id = 'vector-exploratory-' + time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())
    out = ROOT / 'artifacts/eval/vector-exploratory' / run_id
    out.mkdir(parents=True)
    (out / 'protocol.json').write_text(json.dumps(rules, indent=2) + '\n')
    rows, snapshots = [], []
    with (out / 'predictions.jsonl').open('w', encoding='utf-8') as raw:
        for seed in rules['seeds']:
            for round_no in range(rules['rounds']):
                path = source_dir / f'snapshot-{seed}-adaptive-{round_no}.json'
                before = sha(path)
                snapshot = json.loads(path.read_text())
                # The manifest round advances only when new evidence is acquired.
                assert 0 <= snapshot['round'] <= round_no
                index = SameEvidenceVectorIndex(snapshot['evidence'], embed)
                snapshots.append(dict(seed=seed, round=round_no,
                                      acquisition_round=snapshot['round'],
                                      source_snapshot_sha256=before,
                                      acquired_records=len(index.records)))
                for case in heldout:
                    with Controller(sandbox).incident(case) as public:
                        start = time.perf_counter()
                        prediction = index.predict(public)
                        elapsed_ms = (time.perf_counter() - start) * 1000
                    # Private expected label is used only by the outer evaluator.
                    row = dict(seed=seed, round=round_no, case_id=case['case_id'],
                               expected=case['expected_origin_id'],
                               selected=prediction['selected_origin_id'],
                               status=prediction['status'],
                               query_count=prediction['query_count'],
                               elapsed_ms=elapsed_ms, source_snapshot_sha256=before)
                    rows.append(row)
                    raw.write(json.dumps(row) + '\n')
                assert sha(path) == before, 'Vector comparison mutated a v1 snapshot'
                print(f'seed {seed} round {round_no}: {len(heldout)} cases, {len(index.records)} acquired records', flush=True)

    aggregate = []
    for round_no in range(rules['rounds']):
        selected = [row for row in rows if row['round'] == round_no]
        vector = score_predictions(selected)
        graph = adaptive[round_no]
        assert vector['total'] == graph['total'] == len(rules['seeds']) * len(heldout)
        aggregate.append(dict(round=round_no, vector=vector,
                              adaptive_graph=dict(correct=graph['correct'], total=graph['total']),
                              acquired_records=sorted({s['acquired_records'] for s in snapshots if s['round'] == round_no})))
    result = dict(label='RETROSPECTIVE EXPLORATORY; existing controlled heldout reused',
                  source_run=source['run_id'], model=rules['model_name'],
                  vector_store='QdrantClient(:memory:) local vector collection',
                  rows=aggregate, limitations=rules['limitations'])
    (out / 'aggregate.json').write_text(json.dumps(result, indent=2) + '\n')
    (out / 'snapshots.json').write_text(json.dumps(snapshots, indent=2) + '\n')
    (out / 'environment.json').write_text(json.dumps(dict(
        python=platform.python_version(), qdrant_client=version('qdrant-client'),
        fastembed=version('fastembed'), onnxruntime=version('onnxruntime'),
        model_revision=rules['model_revision'], model_onnx_sha256=rules['model_onnx_sha256']), indent=2) + '\n')
    assert len(rows) == len(rules['seeds']) * rules['rounds'] * len(heldout)
    assert sha(latest_path) == latest_before
    assert sha(source_dir / 'snapshots.json') == rules['v1_snapshots_index_sha256']
    (out / 'COMPLETE.json').write_text(json.dumps(dict(status='PASS', predictions=len(rows),
        snapshots=len(snapshots), completed_at=datetime.now(timezone.utc).isoformat()), indent=2) + '\n')
    pointer = ROOT / 'artifacts/eval/vector-exploratory/latest.json'
    pointer.write_text(json.dumps(dict(directory=str(out.relative_to(ROOT)).replace('\\', '/')), indent=2) + '\n')
    print(f'COMPLETE: {len(rows)} vector predictions, {len(aggregate)} rounds; v1 unchanged; {out}', flush=True)


if __name__ == '__main__':
    run()
