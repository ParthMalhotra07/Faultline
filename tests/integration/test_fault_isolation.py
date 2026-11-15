import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from faultline.contracts import PublicIncident
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.sandbox.flows import Sandbox


@pytest.mark.parametrize('split', ['development', 'learning'])
def test_cases_change_real_behavior_and_restore(split):
    s = Sandbox()
    c = Controller(s)
    for scenario in load_scenarios(split):
        with c.incident(scenario) as public:
            assert isinstance(public, PublicIncident)
            assert {o.endpoint_id for o in public.observations if o.status == 'failing'} == set(scenario['failing_endpoints'])
            serialized = public.model_dump_json()
            for forbidden in ['expected_origin_id', 'fault_value', 'private_fault_id', scenario['case_id']]:
                assert forbidden not in serialized
            assert len(public.changes) >= 3
        assert all(o.status == 'healthy' for o in s.observe(999))


def test_exception_restores_runtime():
    s = Sandbox()
    with pytest.raises(RuntimeError):
        with Controller(s).incident(load_scenarios('development')[0]):
            raise RuntimeError('simulated investigation crash')
    assert all(o.status == 'healthy' for o in s.observe(100))


def test_splits_disjoint_without_running_holdout():
    splits = [load_scenarios(x) for x in ['development', 'learning', 'heldout']]
    assert list(map(len, splits)) == [2, 6, 12]
    signatures = [(x['fault_key'], json.dumps(x['fault_value']), x['amount'], tuple(x['change_order']))
                  for split in splits for x in split]
    assert len(set(signatures)) == len(signatures)
    ids = [x['case_id'] for split in splits for x in split]
    assert len(set(ids)) == len(ids)


def test_nested_private_fields_cannot_be_forwarded():
    with pytest.raises(ValidationError):
        PublicIncident(observations=[], changes=[{'expected_origin_id': 'config:currency'}])
