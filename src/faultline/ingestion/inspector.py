import hashlib
import json
import time
from faultline.contracts import ConfigAccess, EvidenceRecord


class InspectionError(RuntimeError):
    pass


class Inspector:
    def __init__(self, catalog, budget, version=None, inspected_hashes=()):
        self.catalog, self.budget = catalog, budget
        self.version = version or catalog.version
        self.inspected_hashes = set(inspected_hashes)
        self.ledger = []

    def inspect(self, source_id):
        started = time.monotonic()
        try:
            meta, blob = self.catalog.read(source_id)
        except KeyError:
            self.ledger.append(dict(source_id='source:rejected', status='rejected', bytes=0, records=0))
            raise InspectionError('Source is not allowlisted') from None
        if meta.sha256 in self.inspected_hashes:
            return []
        prior = len(self.ledger)
        entry = dict(source_id=source_id, sha256=meta.sha256, status='rejected', bytes=0, records=0)
        self.ledger.append(entry)
        if prior >= self.budget.max_sources:
            raise InspectionError('Source attempt budget exhausted')
        if meta.source_version != self.version:
            raise InspectionError('Unsupported source version')
        entry['bytes'] = len(blob)
        if sum(r['bytes'] for r in self.ledger) > self.budget.max_bytes:
            raise InspectionError('Byte budget exhausted')
        if hashlib.sha256(blob).hexdigest() != meta.sha256:
            raise InspectionError('Source hash mismatch')
        rows = json.loads(blob)
        entry['records'] = len(rows)
        if sum(r['records'] for r in self.ledger) > self.budget.max_records:
            raise InspectionError('Record budget exhausted')
        output = []
        for i, r in enumerate(rows):
            if set(r) != {'observed_at_ms', 'payload'}:
                raise InspectionError('Unsupported record schema')
            output.append(EvidenceRecord(evidence_id=f'evidence:{meta.sha256}:{i}', source_id=source_id,
                sha256=meta.sha256, source_version=meta.source_version, observed_at_ms=r['observed_at_ms'],
                record_index=i, payload=ConfigAccess.model_validate(r['payload'])))
        if (time.monotonic() - started) * 1000 > self.budget.timeout_ms:
            raise InspectionError('Inspection timeout')
        entry['status'] = 'complete'
        self.inspected_hashes.add(meta.sha256)
        return output
