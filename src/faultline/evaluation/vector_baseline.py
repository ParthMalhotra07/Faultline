"""Exploratory same-evidence vector retrieval; no graph claims or labels enter it."""
from qdrant_client import QdrantClient, models
from faultline.diagnosis.ranker import RECENT_WINDOW_MS


def plain_id(value):
    return value.split(':', 1)[-1].replace('_', ' ').replace('-', ' ')


def evidence_text(record):
    payload = record['payload']
    return (f"passage: service {plain_id(payload['service_id'])} "
            f"{payload['operation']}s configuration {plain_id(payload['config_key_id'])}")


def incident_text(public):
    failing = sorted((o for o in public.observations if o.status == 'failing'),
                     key=lambda o: o.endpoint_id)
    return 'query: ' + '; '.join(
        f"failing endpoint {plain_id(o.endpoint_id)} {o.symptom_code} {o.message}"
        for o in failing)


class EmbedCache:
    def __init__(self, model):
        self.model, self.cache = model, {}

    def vector(self, text):
        if text not in self.cache:
            self.cache[text] = list(self.model.embed([text]))[0].tolist()
        return self.cache[text]


class SameEvidenceVectorIndex:
    """Qdrant local collection of only acquired, source-backed telemetry records."""
    def __init__(self, evidence, embed):
        self.records = sorted((item['record'] for item in evidence.values() if 'record' in item),
                              key=lambda record: record['evidence_id'])
        self.embed = embed
        self.client = None
        if not self.records:
            return
        self.client = QdrantClient(':memory:')
        vectors = [embed.vector(evidence_text(record)) for record in self.records]
        self.client.create_collection('evidence', vectors_config=models.VectorParams(
            size=len(vectors[0]), distance=models.Distance.COSINE))
        self.client.upsert('evidence', points=[models.PointStruct(
            id=i + 1, vector=vector,
            payload={'config_key_id': record['payload']['config_key_id'],
                     'evidence_id': record['evidence_id']})
            for i, (record, vector) in enumerate(zip(self.records, vectors))])

    def predict(self, public):
        failing = [o for o in public.observations if o.status == 'failing']
        at = max((o.observed_at_ms for o in public.observations), default=0)
        candidates = {c.target_entity_id for c in public.changes
                      if 0 <= at - c.changed_at_ms <= RECENT_WINDOW_MS}
        if not failing or not candidates or not self.client:
            return dict(status='insufficient_evidence', selected_origin_id=None, query_count=0)
        results = self.client.query_points('evidence', query=self.embed.vector(incident_text(public)),
                                           limit=min(100, len(self.records)), with_payload=True).points
        best = {}
        for result in results:
            candidate = result.payload['config_key_id']
            if candidate in candidates:
                best[candidate] = max(best.get(candidate, float('-inf')), result.score)
        ranked = sorted(best, key=lambda candidate: (-best[candidate], candidate))
        if not ranked:
            return dict(status='insufficient_evidence', selected_origin_id=None, query_count=1)
        if len(ranked) > 1 and abs(best[ranked[0]] - best[ranked[1]]) <= 1e-6:
            return dict(status='ambiguous', selected_origin_id=None, query_count=1)
        return dict(status='supported', selected_origin_id=ranked[0], query_count=1)
