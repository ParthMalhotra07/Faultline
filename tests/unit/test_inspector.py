import pytest
from faultline.contracts import InspectionBudget
from faultline.ingestion.catalog import Catalog
from faultline.ingestion.inspector import Inspector, InspectionError
from faultline.sandbox.flows import Sandbox


def catalog():
    s = Sandbox()
    s.observe(100)
    return Catalog.from_telemetry(s.config.telemetry(), s.source_version)


def test_catalog_exposes_only_safe_metadata_and_rejects_paths():
    c = catalog()
    allowed = {'source_id','owner_service_ids','kind','source_version','sha256','estimated_bytes','inspected'}
    assert all(set(x.model_dump()) == allowed for x in c.metadata())
    i = Inspector(c, InspectionBudget(max_sources=2,max_bytes=10000,max_records=20,timeout_ms=1000))
    with pytest.raises(InspectionError):
        i.inspect('../fixtures/private/heldout.json')
    assert len(i.ledger) == 1


def test_hash_version_budget_and_duplicate_handling():
    c = catalog()
    source = c.metadata()[0]
    i = Inspector(c, InspectionBudget(max_sources=1,max_bytes=10000,max_records=20,timeout_ms=1000))
    result = i.inspect(source.source_id)
    assert result and result[0].sha256 == source.sha256
    assert i.inspect(source.source_id) == []
    assert len(i.ledger) == 1  # Same hash is not recharged.
    with pytest.raises(InspectionError):
        i.inspect(c.metadata()[1].source_id)
    assert len(i.ledger) == 2 and i.ledger[-1]['status'] == 'rejected'


def test_oversize_and_stale_fail_explicitly():
    c = catalog()
    i = Inspector(c, InspectionBudget(max_sources=2,max_bytes=1,max_records=1,timeout_ms=1000))
    with pytest.raises(InspectionError, match='budget'):
        i.inspect(c.metadata()[0].source_id)
    assert not i.inspected_hashes
    with pytest.raises(InspectionError, match='version'):
        Inspector(c, InspectionBudget(max_sources=2,max_bytes=10000,max_records=20,timeout_ms=1000), 'different').inspect(c.metadata()[0].source_id)
