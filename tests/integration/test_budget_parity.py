import random
import uuid
from faultline.evaluation.baselines import run_round
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.sandbox.flows import Sandbox


def test_frozen_and_random_budget_parity_and_reproducibility(tmp_path):
    s = Sandbox(); s.observe(100)
    catalog = Catalog.from_telemetry(s.config.telemetry(), s.source_version)
    stores = [GraphStore('budget-'+uuid.uuid4().hex, s.source_version, tmp_path) for _ in range(3)]
    try:
        for g in stores:
            g.seed()
        with Controller(s).incident(load_scenarios('development')[0]) as public:
            before = stores[0].manifest_hash()
            frozen = run_round('frozen', stores[0], public, catalog, random.Random(17))
            assert stores[0].manifest_hash() == before and frozen['ledger'] == []
            a = run_round('random', stores[1], public, catalog, random.Random(17))
            b = run_round('random', stores[2], public, catalog, random.Random(17))
            assert a['inspection'] == b['inspection']
            assert a['budget'] == b['budget'] == frozen['budget']
            assert a['ledger'] == b['ledger']
            assert len(a['ledger']) <= a['budget']['max_sources']
    finally:
        for g in stores:
            g.reset()
