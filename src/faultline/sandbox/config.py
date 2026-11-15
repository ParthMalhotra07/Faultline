from collections import deque

HEALTHY = {'config:currency': 1, 'config:billing': True, 'config:inventory': True}


class Config:
    def __init__(self, source_version, limit=1000):
        self.source_version = source_version
        self._records = deque(maxlen=limit)
        self.reset()

    def reset(self):
        self._values = dict(HEALTHY)
        self.clear_telemetry()

    def clear_telemetry(self):
        self._records.clear()
        self._overflow = False

    def set(self, key, value):
        if key not in HEALTHY:
            raise ValueError('Unknown sandbox config key')
        self._values[key] = value

    def read(self, service, key, observed_at_ms):
        if len(self._records) == self._records.maxlen:
            self._overflow = True
        self._records.append(dict(service_id=service, config_key_id=key, operation='read',
                                  observed_at_ms=observed_at_ms, source_version=self.source_version))
        return self._values[key]

    def telemetry(self):
        if self._overflow:
            raise RuntimeError('Telemetry incomplete: record capacity exceeded')
        return [dict(r) for r in self._records]
