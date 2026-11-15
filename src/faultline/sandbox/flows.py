"""Three real functions, with shared dependencies and a healthy counterexample."""
import hashlib
from pathlib import Path
from faultline.contracts import Observation
from faultline.sandbox.config import Config


def source_version():
    return hashlib.sha256(Path(__file__).read_bytes() + Path(__file__).with_name('config.py').read_bytes()).hexdigest()


class FlowUnavailable(Exception):
    pass


class Sandbox:
    def __init__(self, telemetry_limit=1000):
        self.source_version = source_version()
        self.config = Config(self.source_version, telemetry_limit)

    def reset(self):
        self.config.reset()

    def price(self, amount, at):
        rate = self.config.read('service:pricing', 'config:currency', at)
        if type(rate) not in (int, float) or not 0 < rate <= 100:
            raise FlowUnavailable()
        return amount * rate

    def bill(self, amount, at):
        active = self.config.read('service:billing', 'config:billing', at)
        if active is not True:
            raise FlowUnavailable()
        return amount

    def checkout(self, amount, at):
        available = self.config.read('service:checkout', 'config:inventory', at)
        priced = self.price(amount, at)
        charged = self.bill(priced, at)
        if available is not True:
            raise FlowUnavailable()
        return charged

    def refunds(self, amount, at):
        return -self.bill(self.price(amount, at), at)

    def renewals(self, amount, at):
        return self.bill(amount, at)

    def observe(self, at, amount=100):
        self.config.clear_telemetry()
        observations = []
        for name in ('checkout', 'refunds', 'renewals'):
            try:
                result = getattr(self, name)(amount, at)
                expected = -amount if name == 'refunds' else amount
                healthy = result == expected
            except FlowUnavailable:
                healthy = False
            observations.append(Observation(
                observation_id=f'obs:{name}:{at}', observed_at_ms=at, endpoint_id=f'endpoint:{name}',
                status='healthy' if healthy else 'failing', symptom_code='ok' if healthy else 'acceptance_failed',
                message='Acceptance check passed' if healthy else 'Acceptance check failed',
                evidence_id=f'evidence:acceptance:{name}:{at}'))
        return observations
