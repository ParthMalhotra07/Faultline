"""Learner accepts public records and allowlisted sources only."""
import copy
from faultline.contracts import InspectionBudget
from faultline.diagnosis.ranker import diagnose
from faultline.diagnosis.gaps import unresolved_services
from faultline.learning.selector import select_source
from faultline.ingestion.inspector import Inspector
from faultline.ingestion.commit import ingest

DEFAULT_BUDGET = InspectionBudget(max_sources=1, max_bytes=10000, max_records=100, timeout_ms=1000)


def learn_round(store, public, catalog, budget=DEFAULT_BUDGET, policy='adaptive', rng=None):
    before = diagnose(store, public)
    if before.status == 'error':
        raise RuntimeError('Cannot learn after incomplete graph retrieval')
    endpoint_paths = {o.endpoint_id: store.paths(o.endpoint_id) for o in public.observations if o.status == 'failing'}
    unresolved = unresolved_services(public, endpoint_paths)
    inspected = set(store.manifest['sources'])
    if policy == 'adaptive':
        source = select_source(catalog.metadata(), unresolved, inspected)
    elif policy == 'random' and rng is not None:
        unseen = sorted((s for s in catalog.metadata() if s.sha256 not in inspected), key=lambda s:s.source_id)
        source = rng.choice(unseen) if unseen else None
    else:
        raise ValueError('Unsupported ingestion policy')
    inspector = Inspector(catalog, budget, store.version, inspected)
    if source is not None:
        records = inspector.inspect(source.source_id)
        ingest(store, catalog, records, store.manifest['round'] + 1)
    after = diagnose(store, public)
    return dict(public_input=public.model_dump(), before=before.model_dump(), after=after.model_dump(),
                unresolved_services=sorted(unresolved),
                inspection=source.model_dump() if source else None,
                ledger=inspector.ledger, budget=budget.model_dump(),
                snapshot=copy.deepcopy(store.manifest), exhausted=source is None)
