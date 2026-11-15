"""Allowlisted immutable public DTOs. No arbitrary dictionaries cross this boundary."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Id = Annotated[str, Field(pattern=r'^[a-z][a-z0-9_-]*:[a-zA-Z0-9_.:-]{1,100}$')]
Hash = Annotated[str, Field(pattern=r'^[0-9a-f]{64}$')]
Millis = Annotated[int, Field(ge=0)]
Text = Annotated[str, Field(min_length=1, max_length=512)]
Relationship = Literal['HANDLED_BY', 'CALLS', 'READS_CONFIG', 'MODIFIES', 'OBSERVED_AT']


class PublicRecord(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, frozen=True, hide_input_in_errors=True)


class Observation(PublicRecord):
    observation_id: Id
    observed_at_ms: Millis
    endpoint_id: Id
    status: Literal['healthy', 'failing', 'unknown']
    symptom_code: Text
    message: Text
    evidence_id: Id


class ChangeRecord(PublicRecord):
    change_id: Id
    changed_at_ms: Millis
    target_entity_id: Id
    public_summary: Text
    evidence_id: Id


class EvidenceSource(PublicRecord):
    source_id: Id
    owner_service_ids: list[Id] = Field(max_length=32)
    kind: Literal['config_access']
    source_version: Text
    sha256: Hash
    estimated_bytes: int = Field(ge=0)
    inspected: bool = False


class ConfigAccess(PublicRecord):
    service_id: Id
    config_key_id: Id
    operation: Literal['read']


class EvidenceRecord(PublicRecord):
    evidence_id: Id
    source_id: Id
    sha256: Hash
    source_version: Text
    observed_at_ms: Millis
    record_index: int = Field(ge=0)
    payload: ConfigAccess


class DependencyClaim(PublicRecord):
    claim_id: Id
    from_id: Id
    relationship_type: Relationship
    to_id: Id
    evidence_id: Id
    source_version: Text
    learned_round: int = Field(ge=0)
    state: Literal['pending', 'committed', 'stale']


class Candidate(PublicRecord):
    entity_id: Id
    failing_coverage: int = Field(ge=0)
    healthy_contradictions: int = Field(ge=0)
    shortest_path: int = Field(ge=0)


class ExplanationPath(PublicRecord):
    endpoint_id: Id
    candidate_id: Id
    entity_ids: list[Id] = Field(min_length=2, max_length=8)
    claim_ids: list[Id] = Field(min_length=1, max_length=7)
    evidence_ids: list[Id] = Field(min_length=1, max_length=7)


class Diagnosis(PublicRecord):
    investigation_id: Id
    snapshot_manifest_hash: Hash
    ranked_candidates: list[Candidate] = Field(max_length=100)
    selected_origin_id: Id | None
    status: Literal['supported', 'ambiguous', 'insufficient_evidence', 'error']
    explanation_paths: list[ExplanationPath] = Field(max_length=1000)
    evidence_ids: list[Id] = Field(max_length=1000)
    gap_reason: Text | None
    elapsed_ms: float = Field(ge=0)

    @model_validator(mode='after')
    def consistent_selection(self):
        if self.status == 'supported':
            if not self.ranked_candidates or self.selected_origin_id != self.ranked_candidates[0].entity_id:
                raise ValueError('Supported diagnosis must select the actual first candidate')
        elif self.selected_origin_id is not None:
            raise ValueError('Only supported diagnoses select an origin')
        return self


class InspectionBudget(PublicRecord):
    max_sources: int = Field(gt=0, le=100)
    max_bytes: int = Field(gt=0, le=10_000_000)
    max_records: int = Field(gt=0, le=100_000)
    timeout_ms: int = Field(gt=0, le=60_000)


class PublicIncident(PublicRecord):
    observations: list[Observation] = Field(max_length=100)
    changes: list[ChangeRecord] = Field(max_length=100)
