import pytest
from pydantic import ValidationError
from faultline.contracts import Observation, PublicIncident, EvidenceRecord, DependencyClaim, Diagnosis


def observation(**extra):
    return dict(observation_id='obs:1', observed_at_ms=100, endpoint_id='endpoint:checkout',
                status='failing', symptom_code='unavailable', message='Request failed',
                evidence_id='evidence:1', **extra)


def test_private_fields_rejected_at_every_boundary():
    for name in ['expected_origin_id', 'gold_label', 'private_fault_id', 'anything_else']:
        with pytest.raises(ValidationError):
            Observation(**observation(**{name: 'secret'}))
        with pytest.raises(ValidationError):
            PublicIncident(observations=[observation(**{name: 'secret'})], changes=[])


@pytest.mark.parametrize('field,value', [('endpoint_id', '../private/file'), ('observed_at_ms', -1),
                                       ('observed_at_ms', '100'), ('status', 'gold'), ('message', {'gold': 'x'})])
def test_invalid_data_rejected(field, value):
    data = observation()
    data[field] = value
    with pytest.raises(ValidationError):
        Observation(**data)


def test_immutable_public_roundtrip():
    o = Observation(**observation())
    assert Observation.model_validate_json(o.model_dump_json()) == o
    with pytest.raises(ValidationError):
        o.endpoint_id = 'endpoint:refunds'


def test_evidence_only_accepts_typed_safe_telemetry():
    base = dict(evidence_id='evidence:1', source_id='source:billing', sha256='a'*64,
                source_version='v1', observed_at_ms=100, record_index=0,
                payload=dict(service_id='service:billing', config_key_id='config:billing',
                             operation='read', value='do-not-expose'))
    with pytest.raises(ValidationError):
        EvidenceRecord(**base)
    base['payload'].pop('value')
    base['payload']['gold_label'] = 'hidden'
    with pytest.raises(ValidationError):
        EvidenceRecord(**base)
    base['payload'].pop('gold_label')
    assert 'do-not-expose' not in EvidenceRecord(**base).model_dump_json()


def test_claim_relationship_allowlist_and_diagnosis_consistency():
    with pytest.raises(ValidationError):
        DependencyClaim(claim_id='claim:1', from_id='service:a', to_id='config:b',
                        relationship_type='PROVES_CAUSE', evidence_id='evidence:1',
                        source_version='v1', learned_round=1, state='committed')
    with pytest.raises(ValidationError):
        Diagnosis(investigation_id='investigation:1', snapshot_manifest_hash='a'*64,
                  ranked_candidates=[], selected_origin_id='config:a', status='ambiguous',
                  explanation_paths=[], evidence_ids=[], gap_reason='tie', elapsed_ms=0)
