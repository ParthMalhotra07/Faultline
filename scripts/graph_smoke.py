"""Live smoke only: no dictionary graph or alternate backend can pass."""
import json
from pathlib import Path
from faultline.graph.adapter import HydraAdapter, GraphError

ROOT = Path(__file__).resolve().parents[1]
g = HydraAdapter.from_environment()
ids = [900000001, 900000002, 900000003]
try:
    for i in ids:
        g.execute('smoke_delete', {'id': i})
    for _ in range(2):
        for a, b in zip(ids, ids[1:]):
            g.execute('smoke_seed', {'src': a, 'dst': b})
    assert g.execute('smoke_edges', {'src': ids[0]}) == [{'id': ids[1]}], 'Duplicate logical edges'
    assert g.execute('smoke_path', {'src': ids[0]}) == [{'id': ids[2]}], 'Two-hop traversal failed'
    g.execute('smoke_update', {'id': ids[2], 'version': 'after-update'})
    assert g.execute('smoke_read', {'id': ids[2]}) == [{'version': 'after-update'}]
    assert g.execute('smoke_read', {'id': 900000099}) == [], 'Existence needs label anchor'
    try:
        g.execute('smoke_invalid', {})
    except GraphError:
        pass
    else:
        raise AssertionError('Invalid query succeeded')
    print('PASS: repeat seed, two-hop traversal, update visibility, label-anchored existence, error decoding')
finally:
    for i in ids:
        g.execute('smoke_delete', {'id': i})
    (ROOT / 'artifacts/hydra-smoke/responses.json').write_text(json.dumps(g.trace, indent=2) + '\n')
