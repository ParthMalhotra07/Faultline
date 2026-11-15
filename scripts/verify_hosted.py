"""Exercise the bundled HydraDB+app image through a configured HTTPS Host."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit
import urllib.error
import urllib.request

p=argparse.ArgumentParser()
p.add_argument('--base',default='http://127.0.0.1:18765')
p.add_argument('--origin',default='https://faultline.example')
p.add_argument('--phase',choices=['first','after'],required=True)
p.add_argument('--state',default='.runtime/host-smoke/manifest.json')
p.add_argument('--railway-healthcheck',action='store_true',help='Also probe Railway healthcheck Host isolation')
a=p.parse_args()
host=urlsplit(a.origin).netloc

def request(path, body=None, origin=a.origin, host_override=None):
    headers={'Host':host_override or host,'Content-Type':'application/json'}
    if body is not None:
        headers['X-Faultline-Local']='sandbox'
        if origin: headers['Origin']=origin
    req=urllib.request.Request(a.base+path,headers=headers,
        data=None if body is None else json.dumps(body).encode())
    try:
        with urllib.request.urlopen(req,timeout=30) as response:
            return response.status,json.load(response)
    except urllib.error.HTTPError as exc:
        return exc.code,json.load(exc)

assert request('/api/health')[0]==200
assert request('/api/results')[1]['rows'] and len(request('/api/results')[1]['rows'])==29
assert request('/api/replay')[1]['recorded'] is True
assert request('/fixtures/private/heldout.json')[0]==404
assert request('/local/trigger',{'scenario':'demo-currency'},origin='https://other.example')[0]==403
if a.railway_healthcheck:
    health_host='healthcheck.railway.app'
    assert request('/api/health',host_override=health_host)[0]==200
    assert request('/api/results',host_override=health_host)[0]==403
    assert request('/local/trigger',{},host_override=health_host)[0]==403
if a.phase=='first':
    assert request('/local/reset-experiment',{})[0]==200
    assert request('/local/trigger',{'scenario':'demo-currency'})[0]==200
    before=request('/api/diagnose',{})[1]
    assert before['status']=='insufficient_evidence'
    learned=request('/api/learn',{})[1]
    assert learned['after']['selected_origin_id']=='config:currency'
    status,graph=request('/api/graph')
    assert status==200 and graph['source']=='live HydraDB traversal'
    assert any(e['relationship_type']=='READS_CONFIG' for e in graph['edges'])
    Path(a.state).write_text(json.dumps({'manifest_hash':graph['manifest_hash'],
        'edges':len(graph['edges'])})+'\n')
    assert request('/local/restore',{})[0]==200
    print('PASS: bundled image serves results and replay; remote same-origin controls trigger, abstain, learn and traverse actual HydraDB claims.')
else:
    previous=json.loads(Path(a.state).read_text())
    graph=request('/api/graph')[1]
    assert graph['manifest_hash']==previous['manifest_hash'] and len(graph['edges'])==previous['edges']
    assert request('/local/trigger',{'scenario':'demo-transfer'})[0]==200
    answer=request('/api/diagnose',{})[1]
    assert answer['selected_origin_id']=='config:currency' and answer['status']=='supported'
    assert request('/local/restore',{})[0]==200
    print('PASS: bundled image restart retained graph manifest and a different incident transferred without new inspection.')
