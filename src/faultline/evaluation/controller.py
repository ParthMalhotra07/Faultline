"""Private local-only mutations; public view contains no case label or manifest."""
from contextlib import contextmanager
import json
from pathlib import Path
from faultline.contracts import ChangeRecord, PublicIncident

ROOT = Path(__file__).resolve().parents[3]


def load_scenarios(split):
    if split not in ('development', 'learning', 'heldout'):
        raise ValueError('Unknown private split')
    return json.loads((ROOT / 'fixtures/private' / (split + '.json')).read_text())


class Controller:
    def __init__(self, sandbox):
        self.sandbox = sandbox

    @contextmanager
    def incident(self, scenario):
        self.sandbox.reset()
        try:
            self.sandbox.config.set(scenario['fault_key'], scenario['fault_value'])
            at = scenario['observed_at_ms']
            changes = [ChangeRecord(change_id=f'change:{i}:{at}', changed_at_ms=at - 100 - i,
                                    target_entity_id=target, public_summary='Configuration deployment observed',
                                    evidence_id=f'evidence:change:{i}:{at}')
                       for i, target in enumerate(scenario['change_order'])]
            # Construct narrowly; never dump/copy a private manifest into a public record.
            observations = self.sandbox.observe(at, scenario['amount'])
            if 'monitored_endpoints' in scenario:
                observations = [o for o in observations if o.endpoint_id in scenario['monitored_endpoints']]
            yield PublicIncident(observations=observations, changes=changes)
        finally:
            self.sandbox.reset()
