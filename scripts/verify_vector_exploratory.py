"""Recount exploratory vector results without changing the frozen v1 experiment."""
import hashlib
import json
from pathlib import Path

from faultline.evaluation.report import verify_protocol
from faultline.evaluation.scoring import score_predictions

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    rules = json.loads((ROOT / 'protocol/vector-exploratory-v2.json').read_text())
    source = ROOT / rules['source_run_directory']
    assert sha(ROOT / 'src/faultline/evaluation/vector_baseline.py') == rules['baseline_sha256']
    assert sha(ROOT / 'scripts/evaluate_vector_exploratory.py') == rules['runner_sha256']
    assert sha(ROOT / 'protocol/v1/protocol.json') == rules['v1_protocol_sha256']
    assert sha(source / 'snapshots.json') == rules['v1_snapshots_index_sha256']
    assert json.loads((ROOT / 'artifacts/eval/latest.json').read_text())['directory'] == rules['source_run_directory']
    verify_protocol()

    pointer = json.loads((ROOT / 'artifacts/eval/vector-exploratory/latest.json').read_text())
    out = ROOT / pointer['directory']
    assert json.loads((out / 'COMPLETE.json').read_text())['status'] == 'PASS'
    assert json.loads((out / 'protocol.json').read_text()) == rules
    rows = [json.loads(line) for line in (out / 'predictions.jsonl').read_text().splitlines()]
    snapshots = json.loads((out / 'snapshots.json').read_text())
    aggregate = json.loads((out / 'aggregate.json').read_text())
    graph = json.loads((source / 'aggregate.json').read_text())
    graph_adaptive = {row['round']: row for row in graph['rows'] if row['method'] == 'adaptive'}
    assert len(rows) == 252 and len(snapshots) == 21 and len(aggregate['rows']) == 7
    assert len({(r['seed'], r['round'], r['case_id']) for r in rows}) == 252

    for snapshot in snapshots:
        seed, round_no = snapshot['seed'], snapshot['round']
        source_path = source / f'snapshot-{seed}-adaptive-{round_no}.json'
        source_data = json.loads(source_path.read_text())
        assert sha(source_path) == snapshot['source_snapshot_sha256']
        assert source_data['round'] == snapshot['acquisition_round'] <= round_no
        assert sum('record' in evidence for evidence in source_data['evidence'].values()) == snapshot['acquired_records']
        matching = [r for r in rows if (r['seed'], r['round']) == (seed, round_no)]
        assert len(matching) == 12
        assert all(r['source_snapshot_sha256'] == snapshot['source_snapshot_sha256'] for r in matching)

    for result in aggregate['rows']:
        round_no = result['round']
        selected = [r for r in rows if r['round'] == round_no]
        assert score_predictions(selected) == result['vector']
        assert result['adaptive_graph'] == {key: graph_adaptive[round_no][key] for key in ('correct', 'total')}
        assert len(selected) == 36
        assert result['vector']['correct'] + result['vector']['wrong'] + result['vector']['abstentions'] + result['vector']['errors'] == 36

    failed = ROOT / 'artifacts/eval/vector-exploratory/vector-exploratory-20261115T110711Z'
    assert (failed / 'FAILED.json').is_file() and not (failed / 'COMPLETE.json').exists()
    print(f'PASS: {len(rows)} predictions, {len(snapshots)} unchanged source snapshots, '
          f'{len(aggregate["rows"])} recounted rounds; failed v1 attempt retained')
    print('round | vector correct/36 | graph correct/36')
    for result in aggregate['rows']:
        print(result['round'], result['vector']['correct'], result['adaptive_graph']['correct'], sep=' | ')


if __name__ == '__main__':
    verify()
