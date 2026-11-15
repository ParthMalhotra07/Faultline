import pytest
from faultline.sandbox.flows import Sandbox


def test_healthy_and_reset_are_real():
    s = Sandbox()
    assert all(x.status == 'healthy' for x in s.observe(100))
    s.config.set('config:currency', 0)
    broken = {o.endpoint_id: o.status for o in s.observe(200)}
    assert broken == {'endpoint:checkout': 'failing', 'endpoint:refunds': 'failing', 'endpoint:renewals': 'healthy'}
    s.reset()
    assert all(x.status == 'healthy' for x in s.observe(300))


@pytest.mark.parametrize('key,value,failed', [
    ('config:billing', False, {'endpoint:checkout', 'endpoint:refunds', 'endpoint:renewals'}),
    ('config:inventory', False, {'endpoint:checkout'}),
])
def test_real_dependencies_and_safe_telemetry(key, value, failed):
    s = Sandbox()
    s.config.set(key, value)
    assert {o.endpoint_id for o in s.observe(100) if o.status == 'failing'} == failed
    records = s.config.telemetry()
    assert records
    assert all(set(r) == {'service_id', 'config_key_id', 'operation', 'observed_at_ms', 'source_version'} for r in records)
    assert all(r['source_version'] == s.source_version for r in records)


def test_amounts_are_computed_not_canned_health():
    s = Sandbox()
    assert s.checkout(100, 100) == 100
    s.config.set('config:currency', 2)
    assert s.checkout(100, 100) == 200


def test_telemetry_overflow_is_explicit():
    s = Sandbox(telemetry_limit=1)
    s.observe(100)
    with pytest.raises(RuntimeError, match='incomplete'):
        s.config.telemetry()
