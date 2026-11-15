import uuid
from faultline.graph.store import GraphStore
from faultline.sandbox.flows import source_version


def test_live_seed_and_provenance_idempotence(tmp_path):
    store = GraphStore('test-' + uuid.uuid4().hex, source_version(), tmp_path)
    try:
        store.seed()
        before = store.manifest_hash()
        store.seed()
        assert store.manifest_hash() == before
        paths = store.paths('endpoint:checkout')
        assert any(p['entity_ids'] == ['endpoint:checkout', 'service:checkout', 'service:pricing'] for p in paths)
        assert all(p['claim_ids'] and p['evidence_ids'] for p in paths)
        assert not any(p['entity_ids'][-1].startswith('config:') for p in paths)
        restored = GraphStore(store.namespace, source_version(), tmp_path)
        assert restored.manifest_hash() == before
        assert restored.paths('endpoint:checkout') == paths
    finally:
        store.reset()
    assert store.paths('endpoint:checkout') == []
