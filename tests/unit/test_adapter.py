import io
import json
import urllib.error
import pytest
from faultline.graph.adapter import HydraAdapter, GraphError, decode_cell


@pytest.mark.parametrize('payload', [
    {}, {'error': {'code': 'timeout'}}, {'columns': [], 'rows': [], 'next_cursor': 'next'},
    {'columns': [], 'rows': [], 'truncated': True},
    {'columns': ['id'], 'rows': [[]]},
    {'columns': ['id'], 'rows': [[{'type': 'vertex_id', 'value': 1}]] * 3},
])
def test_incomplete_or_invalid_response_never_succeeds(monkeypatch, payload):
    monkeypatch.setattr('urllib.request.urlopen', lambda *a, **kw: io.BytesIO(json.dumps(payload).encode()))
    with pytest.raises(GraphError):
        HydraAdapter('http://127.0.0.1:1', 'test', max_rows=2).execute('smoke_read', {'id': 1})


def test_timeout_and_422_are_errors(monkeypatch):
    for error in [TimeoutError(), urllib.error.HTTPError('url', 422, 'bad', {}, None)]:
        def fail(*args, **kwargs):
            raise error
        monkeypatch.setattr('urllib.request.urlopen', fail)
        with pytest.raises(GraphError):
            HydraAdapter('http://127.0.0.1:1', 'test').execute('smoke_read', {'id': 1})


def test_null_and_id_decoding():
    assert decode_cell({'type': 'null'}) is None
    assert decode_cell({'type': 'vertex_id', 'value': 42}) == 42


def test_only_fixed_templates():
    with pytest.raises(GraphError):
        HydraAdapter('http://127.0.0.1:1', 'test').execute('MATCH anything', {})
