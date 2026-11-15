"""Pinned HydraDB repository-engine HTTP boundary with fixed query templates."""
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request


class GraphError(RuntimeError):
    pass


# All interpolated values are parameters; callers cannot supply query text.
QUERIES = {
    'smoke_seed': 'MERGE (a:Smoke {id: $src})-[:SMOKE]->(b:Smoke {id: $dst})',
    'smoke_path': 'MATCH (a:Smoke {id: $src})-[:SMOKE]->(b)-[:SMOKE]->(c) RETURN c.id AS id LIMIT 10',
    'smoke_edges': 'MATCH (a:Smoke {id: $src})-[:SMOKE]->(b) RETURN b.id AS id LIMIT 10',
    'smoke_update': 'MATCH (n:Smoke {id: $id}) SET n.version = $version',
    'smoke_read': 'MATCH (n:Smoke {id: $id}) RETURN n.version AS version LIMIT 10',
    'smoke_delete': 'MATCH (n:Smoke {id: $id}) DETACH DELETE n',
    'smoke_invalid': 'THIS IS NOT CYPHER',
}


def decode_cell(cell):
    if not isinstance(cell, dict) or 'type' not in cell:
        raise GraphError('Malformed typed cell')
    kind = cell['type']
    if kind == 'null':
        return None
    if 'value' not in cell:
        raise GraphError('Missing typed value')
    if kind == 'list':
        return [decode_cell(v) for v in cell['value']]
    types = {'vertex_id': int, 'integer': int, 'string': str, 'boolean': bool, 'float': (int, float)}
    if kind not in types or not isinstance(cell['value'], types[kind]):
        raise GraphError('Unsupported or malformed typed value')
    return cell['value']


class HydraAdapter:
    def __init__(self, endpoint, token, graph='default', cell='cell-0', timeout_ms=5000, max_rows=1000):
        u = urllib.parse.urlsplit(endpoint)
        if u.scheme != 'https' and not (u.scheme == 'http' and u.hostname in ('127.0.0.1', 'localhost')):
            raise ValueError('Plaintext is local-only')
        if u.username or u.password or u.query or u.fragment:
            raise ValueError('Endpoint must not contain credentials or query parameters')
        if not 1 <= timeout_ms <= 60_000 or not 1 <= max_rows <= 1000:
            raise ValueError('Invalid query bounds')
        self.endpoint, self._token, self.graph, self.cell = endpoint.rstrip('/'), token, graph, cell
        self.timeout_ms, self.max_rows = timeout_ms, max_rows
        self.trace = []

    @classmethod
    def from_environment(cls):
        token = os.environ.get('HYDRADB_TOKEN')
        if not token and os.environ.get('HYDRADB_TOKEN_FILE'):
            token = Path(os.environ['HYDRADB_TOKEN_FILE']).read_text().strip()
        if not token:
            raise GraphError('Configure HYDRADB_TOKEN or HYDRADB_TOKEN_FILE locally')
        return cls(os.environ.get('HYDRADB_URL', 'http://127.0.0.1:18443'), token,
                   os.environ.get('HYDRADB_GRAPH', 'default'), os.environ.get('HYDRADB_CELL', 'cell-0'))

    def execute(self, template, parameters):
        if template not in QUERIES:
            raise GraphError('Query template is not allowlisted')
        body = dict(cell_id=self.cell, query=QUERIES[template], parameters=parameters,
                    page_size=self.max_rows + 1, timeout_ms=self.timeout_ms)
        request = urllib.request.Request(
            self.endpoint + '/v1/graphs/' + urllib.parse.quote(self.graph, safe='') + '/query',
            data=json.dumps(body).encode(),
            headers={'Authorization': 'Bearer ' + self._token, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_ms / 1000 + 1) as response:
                raw = response.read(2_000_001)
        except urllib.error.HTTPError as e:
            # Never echo server strings which may contain input values or credentials.
            self.trace.append(dict(template=template, http_status=e.code, status='error'))
            raise GraphError(f'HydraDB HTTP {e.code}') from None
        except (OSError, TimeoutError):
            raise GraphError('HydraDB unavailable or timed out') from None
        if len(raw) > 2_000_000:
            raise GraphError('HydraDB response byte limit exceeded')
        try:
            payload = json.loads(raw)
        except (ValueError, TypeError):
            raise GraphError('Malformed HydraDB JSON') from None
        self.trace.append(dict(template=template, request=body, response=payload))
        if not isinstance(payload, dict) or 'error' in payload or not isinstance(payload.get('rows'), list):
            raise GraphError('HydraDB returned an error or unexpected envelope')
        if payload.get('next_cursor') is not None or payload.get('truncated') or payload.get('partial'):
            raise GraphError('Incomplete HydraDB retrieval')
        rows, columns = payload['rows'], payload.get('columns')
        if not isinstance(columns, list) or len(rows) > self.max_rows:
            raise GraphError('HydraDB result limit or schema violation')
        if any(not isinstance(r, list) or len(r) != len(columns) for r in rows):
            raise GraphError('HydraDB row shape violation')
        return [dict(zip(columns, (decode_cell(c) for c in r))) for r in rows]
