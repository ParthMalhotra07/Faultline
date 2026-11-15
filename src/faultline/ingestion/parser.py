import hashlib
import json
from faultline.graph.store import ENTITIES


def validate_records(catalog, records, version):
    if not records:
        raise ValueError('Empty inspection is not ingestion evidence')
    validated = []
    seen = set()
    for r in records:
        meta, blob = catalog.read(r.source_id)
        if r.source_version != version or meta.source_version != version:
            raise ValueError('Stale evidence version')
        if r.sha256 != hashlib.sha256(blob).hexdigest() or r.sha256 != meta.sha256:
            raise ValueError('Evidence hash mismatch')
        rows = json.loads(blob)
        if not 0 <= r.record_index < len(rows):
            raise ValueError('Invalid evidence locator')
        actual = rows[r.record_index]
        if (actual != dict(observed_at_ms=r.observed_at_ms, payload=r.payload.model_dump()) or
                r.evidence_id != f'evidence:{r.sha256}:{r.record_index}'):
            raise ValueError('Evidence differs from actual source')
        a, b = r.payload.service_id, r.payload.config_key_id
        if a not in ENTITIES or b not in ENTITIES or not a.startswith('service:') or not b.startswith('config:'):
            raise ValueError('Unknown dependency identity')
        signature = (r.sha256, a, b)
        if signature not in seen:
            seen.add(signature)
            key = 'claim:learned:' + hashlib.sha256(json.dumps(signature).encode()).hexdigest()[:24]
            validated.append((key, a, b, r))
    # Only whole-source inspection results may be committed.
    for source in {r.source_id for r in records}:
        _, blob = catalog.read(source)
        if {r.record_index for r in records if r.source_id == source} != set(range(len(json.loads(blob)))):
            raise ValueError('Incomplete source inspection')
    return validated
