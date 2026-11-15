import time
from faultline.contracts import Candidate, Diagnosis
from faultline.diagnosis.paths import explanation
from faultline.graph.adapter import GraphError

RECENT_WINDOW_MS = 60_000


def diagnose(store, public):
    started = time.monotonic()
    manifest = store.manifest_hash()
    base = dict(investigation_id='investigation:structural', snapshot_manifest_hash=manifest,
                ranked_candidates=[], selected_origin_id=None, explanation_paths=[], evidence_ids=[])
    try:
        at = max((o.observed_at_ms for o in public.observations), default=0)
        candidates = {c.target_entity_id for c in public.changes if 0 <= at - c.changed_at_ms <= RECENT_WINDOW_MS}
        endpoints = {o.endpoint_id: o.status for o in public.observations}
        paths = {endpoint: store.paths(endpoint) for endpoint in endpoints}
        if not candidates:
            candidates = {p['entity_ids'][1] for endpoint, ps in paths.items() for p in ps
                          if endpoints[endpoint] == 'failing' and len(p['entity_ids']) == 2}
        ranked, explanations = [], []
        for candidate in sorted(candidates):
            failing, healthy, lengths = set(), set(), []
            for endpoint, ps in paths.items():
                for path in ps:
                    if path['entity_ids'][-1] != candidate:
                        continue
                    explanations.append(explanation(endpoint, candidate, path))
                    if endpoints[endpoint] == 'failing':
                        failing.add(endpoint)
                        lengths.append(len(path['claim_ids']))
                    if endpoints[endpoint] == 'healthy':
                        healthy.add(endpoint)
            ranked.append(Candidate(entity_id=candidate, failing_coverage=len(failing),
                                    healthy_contradictions=len(healthy), shortest_path=min(lengths, default=999)))
        def score(c):
            return (-c.failing_coverage, c.healthy_contradictions, c.shortest_path)
        ranked.sort(key=lambda c: (score(c), c.entity_id))
        if not ranked or not ranked[0].failing_coverage:
            status, reason, selected = 'insufficient_evidence', 'No candidate has a complete supporting path', None
        elif len(ranked) > 1 and score(ranked[0]) == score(ranked[1]):
            status, reason, selected = 'ambiguous', 'Best candidates have equal structural evidence', None
        else:
            status, reason, selected = 'supported', None, ranked[0].entity_id
        return Diagnosis(**(base | dict(ranked_candidates=ranked, selected_origin_id=selected,
            status=status, gap_reason=reason, explanation_paths=explanations,
            evidence_ids=sorted({e for p in explanations for e in p.evidence_ids}),
            elapsed_ms=(time.monotonic()-started)*1000)))
    except GraphError:
        return Diagnosis(**base, status='error', gap_reason='HydraDB retrieval failed or was incomplete',
                         elapsed_ms=(time.monotonic()-started)*1000)
