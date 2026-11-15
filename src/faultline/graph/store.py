"""Authoritative reified claims traversed in HydraDB, with isolated ID manifests."""
import hashlib
import json
from pathlib import Path
import re
from faultline.graph.adapter import HydraAdapter, QUERIES, GraphError

QUERIES.update({
    'nodes': 'UNWIND $rows AS row MERGE (n {id: row.id}) SET n:Entity, n.key = row.key, n.version = row.version',
    'evidence_node': 'UNWIND $rows AS row MERGE (n {id: row.id}) SET n:Evidence, n.key = row.key, n.version = row.version, n.sha256 = row.sha256',
    'claim_node': 'UNWIND $rows AS row MERGE (n {id: row.id}) SET n:Claim, n.key = row.key, n.version = row.version, n.kind = row.kind, n.state = row.state',
    'claim_from': 'MERGE (a:Claim {id: $claim})-[:FROM_ENTITY]->(b:Entity {id: $entity})',
    'claim_to': 'MERGE (a:Claim {id: $claim})-[:TO_ENTITY]->(b:Entity {id: $entity})',
    'claim_support': 'MERGE (a:Claim {id: $claim})-[:SUPPORTED_BY]->(b:Evidence {id: $evidence})',
    'claim_commit': 'MATCH (c:Claim {id: $id}) SET c.state = $state',
    'owned_delete': 'MATCH (n {id: $id}) DETACH DELETE n',
})
# Fixed maximum three domain edges = six relationship hops plus evidence joins.
for depth in (1, 2, 3):
    pattern = '(n0:Entity {id: $src})'
    for i in range(1, depth + 1):
        pattern += f'<-[:FROM_ENTITY]-(c{i}:Claim)-[:TO_ENTITY]->(n{i}:Entity)'
    support = ', '.join(f'(c{i})-[:SUPPORTED_BY]->(e{i}:Evidence)' for i in range(1, depth + 1))
    where = ' AND '.join(f"c{i}.state = 'committed' AND c{i}.version = $version AND e{i}.version = $version" for i in range(1, depth + 1))
    columns = [f'n{i}.key AS n{i}' for i in range(depth + 1)]
    columns += [f'c{i}.key AS c{i}' for i in range(1, depth + 1)]
    columns += [f'e{i}.key AS e{i}' for i in range(1, depth + 1)]
    QUERIES[f'paths_{depth}'] = f'MATCH {pattern}, {support} WHERE {where} RETURN ' + ', '.join(columns) + ' LIMIT 1001'

ENTITIES = [f'endpoint:{x}' for x in ('checkout', 'refunds', 'renewals')] + [
    f'service:{x}' for x in ('checkout', 'refunds', 'renewals', 'pricing', 'billing')] + [
    f'config:{x}' for x in ('currency', 'billing', 'inventory')]
TOPOLOGY = [(f'endpoint:{x}', 'HANDLED_BY', f'service:{x}') for x in ('checkout', 'refunds', 'renewals')] + [
    ('service:checkout', 'CALLS', 'service:pricing'), ('service:checkout', 'CALLS', 'service:billing'),
    ('service:refunds', 'CALLS', 'service:pricing'), ('service:refunds', 'CALLS', 'service:billing'),
    ('service:renewals', 'CALLS', 'service:billing')]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class GraphStore:
    def __init__(self, namespace, version, directory=None, adapter=None):
        if not re.fullmatch(r'[a-zA-Z0-9_-]{1,80}', namespace):
            raise ValueError('Invalid experiment namespace')
        self.namespace, self.version = namespace, version
        directory = Path(directory or '.runtime/experiments')
        directory.mkdir(parents=True, exist_ok=True)
        self.path = directory / (namespace + '.json')
        self.adapter = adapter or HydraAdapter.from_environment()
        self.manifest = json.loads(self.path.read_text()) if self.path.exists() else dict(
            namespace=namespace, source_version=version, owned_ids={}, claims={}, evidence={}, sources={}, round=0)
        if self.manifest['source_version'] != version:
            raise GraphError('Stored experiment source version differs; use a new experiment')

    def _save(self):
        temp = self.path.with_suffix('.tmp')
        temp.write_text(json.dumps(self.manifest, sort_keys=True, indent=2) + '\n')
        temp.replace(self.path)

    def vid(self, key):
        value = int.from_bytes(hashlib.sha256((self.namespace + ':' + key).encode()).digest()[:6], 'big')
        for oldkey, oldid in self.manifest['owned_ids'].items():
            if oldid == value and oldkey != key:
                raise GraphError('ID collision')
        self.manifest['owned_ids'][key] = value
        self._save()  # Persist ownership before attempting any write, including interrupted writes.
        return value

    def seed(self):
        rows = [dict(id=self.vid(x), key=x, version=self.version) for x in ENTITIES]
        self.adapter.execute('nodes', {'rows': rows})
        seed_hash = digest(TOPOLOGY)
        for a, kind, b in TOPOLOGY:
            claim = 'claim:seed:' + digest([a, kind, b])[:20]
            evidence = 'evidence:seed:' + digest([a, kind, b])[:20]
            self.commit_claim(claim, a, kind, b, evidence, seed_hash, 'source:topology', 0)

    def commit_claim(self, key, a, kind, b, evidence, sha256, source_id, round_number):
        if a not in ENTITIES or b not in ENTITIES or kind not in ('HANDLED_BY', 'CALLS', 'READS_CONFIG'):
            raise GraphError('Unknown identity or relationship')
        content = dict(from_id=a, to_id=b, kind=kind, evidence_id=evidence,
                       sha256=sha256, source_id=source_id, source_version=self.version, round=round_number)
        if key in self.manifest['claims']:
            if self.manifest['claims'][key] != content:
                raise GraphError('Claim identity reused with different content')
            return
        cid, aid, bid, eid = [self.vid(x) for x in (key, a, b, evidence)]
        self.adapter.execute('evidence_node', {'rows': [dict(id=eid, key=evidence, version=self.version, sha256=sha256)]})
        self.adapter.execute('claim_node', {'rows': [dict(id=cid, key=key, version=self.version, kind=kind, state='pending')]})
        self.adapter.execute('claim_from', {'claim': cid, 'entity': aid})
        self.adapter.execute('claim_to', {'claim': cid, 'entity': bid})
        self.adapter.execute('claim_support', {'claim': cid, 'evidence': eid})
        self.adapter.execute('claim_commit', {'id': cid, 'state': 'committed'})
        self.manifest['claims'][key] = content
        self.manifest['evidence'][evidence] = dict(source_id=source_id, sha256=sha256, source_version=self.version)
        self._save()

    def paths(self, endpoint):
        if endpoint not in ENTITIES or not endpoint.startswith('endpoint:'):
            raise GraphError('Unknown endpoint')
        src = self.vid(endpoint)
        paths = []
        for depth in (1, 2, 3):
            rows = self.adapter.execute(f'paths_{depth}', {'src': src, 'version': self.version})
            for r in rows:
                claims = [r[f'c{i}'] for i in range(1, depth + 1)]
                # Manifest acts as committed-snapshot gate after an interrupted final write.
                if not all(c in self.manifest['claims'] for c in claims):
                    continue
                if any(self.manifest['claims'][c]['source_id'] != 'source:topology' and
                       self.manifest['claims'][c]['sha256'] not in self.manifest['sources'] for c in claims):
                    continue
                paths.append(dict(entity_ids=[r[f'n{i}'] for i in range(depth + 1)], claim_ids=claims,
                                  evidence_ids=[r[f'e{i}'] for i in range(1, depth + 1)]))
        return sorted(paths, key=lambda p: (p['entity_ids'], p['claim_ids']))

    def manifest_hash(self):
        return digest(self.manifest)

    def reset(self):
        for i in list(self.manifest['owned_ids'].values()):
            self.adapter.execute('owned_delete', {'id': i})
        self.manifest.update(owned_ids={}, claims={}, evidence={}, sources={}, round=0)
        self._save()
