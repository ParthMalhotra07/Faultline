from faultline.contracts import EvidenceSource
from faultline.learning.selector import select_source


def source(id, owners, size, hash):
    return EvidenceSource(source_id=id,owner_service_ids=owners,kind='config_access',
                          source_version='v1',sha256=hash*64,estimated_bytes=size)


def test_selection_only_uses_public_coverage_size_id_and_seen_hash():
    a = source('source:a',['service:a'],100,'a')
    b = source('source:b',['service:a','service:b'],200,'b')
    c = source('source:c',['service:a'],50,'c')
    unresolved = {'service:a','service:b'}
    assert select_source([a,b,c],unresolved,set()) == b
    assert select_source([b,a,c],unresolved,{'b'*64}) == c
    assert select_source([a],unresolved,{'a'*64}) is None
    assert select_source([a],{'service:other'},set()) is None


def test_stable_id_orders_equal_metadata():
    a = source('source:a',['service:a'],100,'a')
    b = source('source:b',['service:a'],100,'b')
    assert select_source([b,a],{'service:a'},set()) == a
