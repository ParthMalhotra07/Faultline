"""Fair acquisition baselines and a precisely labeled lexical evidence baseline."""
import re
from faultline.diagnosis.ranker import diagnose, RECENT_WINDOW_MS
from faultline.learning.runner import learn_round, DEFAULT_BUDGET


def run_round(method, store, public, catalog, rng, budget=DEFAULT_BUDGET):
    if method == 'frozen':
        d = diagnose(store, public).model_dump()
        return dict(before=d, after=d, budget=budget.model_dump(), ledger=[], inspection=None)
    return learn_round(store, public, catalog, budget, method, rng)


def token_overlap(store, public):
    """No vectors, graph traversal, or hidden labels. Exact acquired evidence as plain text."""
    def tokens(text):
        return set(re.findall(r'[a-z0-9]+', text.lower()))
    query = tokens(' '.join(o.endpoint_id + ' ' + o.message for o in public.observations if o.status == 'failing'))
    at = max((o.observed_at_ms for o in public.observations), default=0)
    candidates = sorted({c.target_entity_id for c in public.changes if 0 <= at - c.changed_at_ms <= RECENT_WINDOW_MS})
    evidence = list(store.manifest['evidence'].values())
    scores = {}
    for candidate in candidates:
        scores[candidate] = max((len(query & tokens(r['record']['payload']['service_id'] + ' ' +
            r['record']['payload']['config_key_id'])) for r in evidence
            if 'record' in r and r['record']['payload']['config_key_id'] == candidate), default=0)
    ranked = sorted(scores, key=lambda c: (-scores[c], c))
    if not ranked or scores[ranked[0]] == 0:
        return dict(status='insufficient_evidence', selected_origin_id=None)
    if len(ranked) > 1 and scores[ranked[0]] == scores[ranked[1]]:
        return dict(status='ambiguous', selected_origin_id=None)
    return dict(status='supported', selected_origin_id=ranked[0])
