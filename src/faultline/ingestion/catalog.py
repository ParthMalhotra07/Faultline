import hashlib
import json
from faultline.contracts import EvidenceSource, ConfigAccess


class Catalog:
    def __init__(self, entries, version):
        self._entries, self.version = entries, version

    @classmethod
    def from_telemetry(cls, records, version):
        groups = {'source:shared': [], 'source:checkout': []}
        for r in records:
            if set(r) != {'service_id', 'config_key_id', 'operation', 'observed_at_ms', 'source_version'}:
                raise ValueError('Unsupported telemetry schema')
            if r['source_version'] != version:
                raise ValueError('Unsupported source version')
            payload = ConfigAccess(service_id=r['service_id'], config_key_id=r['config_key_id'], operation=r['operation'])
            key = 'source:checkout' if payload.service_id == 'service:checkout' else 'source:shared'
            groups[key].append(dict(observed_at_ms=r['observed_at_ms'], payload=payload.model_dump()))
        entries = {}
        for source_id, rows in groups.items():
            if not rows:
                continue
            blob = json.dumps(rows, sort_keys=True, separators=(',', ':')).encode()
            meta = EvidenceSource(source_id=source_id,
                owner_service_ids=sorted({r['payload']['service_id'] for r in rows}),
                kind='config_access', source_version=version, sha256=hashlib.sha256(blob).hexdigest(), estimated_bytes=len(blob))
            entries[source_id] = (meta, blob)
        return cls(entries, version)

    def metadata(self):
        return [v[0] for k, v in sorted(self._entries.items())]

    def read(self, source_id):
        if source_id not in self._entries:
            raise KeyError('Unknown allowlisted source')
        return self._entries[source_id]
