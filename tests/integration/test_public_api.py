import json
import threading
import urllib.request
import urllib.error
import uuid
from types import SimpleNamespace
from faultline.api import App, make_server


def test_explicit_public_origin_allows_only_that_host_and_same_origin_writes():
    def rejected_scenario(_): raise ValueError('Unknown demo scenario')
    app=SimpleNamespace(lock=threading.RLock(),trigger=rejected_scenario)
    server=make_server(app,port=0,public_origin='https://faultline.example')
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    def request(host,origin=None,body=None):
        headers={'Host':host,'X-Faultline-Local':'sandbox','Content-Type':'application/json'}
        if origin: headers['Origin']=origin
        req=urllib.request.Request(base+('/api/health' if body is None else '/local/trigger'),
            headers=headers,data=None if body is None else b'{}')
        try:
            with urllib.request.urlopen(req) as response: return response.status
        except urllib.error.HTTPError as exc: return exc.code
    try:
        assert request('faultline.example')==200
        assert request('other.example')==403
        assert request('faultline.example',origin='https://other.example',body={})==403
        assert request('faultline.example',origin='http://faultline.example',body={})==403
        assert request('faultline.example',origin='https://faultline.example',body={})!=403
    finally:
        server.shutdown();server.server_close()


def test_real_http_workflow_and_private_boundary(tmp_path):
    app=App('api-'+uuid.uuid4().hex,tmp_path)
    server=make_server(app,port=0,public_origin='https://faultline.example')
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    def request(path,data=None,local=True,remote=False):
        headers={'Content-Type':'application/json'}
        if local: headers['X-Faultline-Local']='sandbox'
        if remote:
            headers['Host']='faultline.example'
            if data is not None: headers['Origin']='https://faultline.example'
        req=urllib.request.Request(base+path,headers=headers,data=json.dumps(data).encode() if data is not None else None)
        try:
            with urllib.request.urlopen(req) as r:return r.status,json.load(r)
        except urllib.error.HTTPError as e:return e.code,json.load(e)
    try:
        assert request('/api/health')[0]==200
        assert request('/local/trigger',{'scenario':'demo-currency'},False)[0]==403
        assert request('/local/trigger',{'scenario':'demo-currency','expected_origin_id':'bad'})[0]==400
        assert request('/local/trigger',{'scenario':'demo-currency'},remote=True)[0]==200
        before=request('/api/diagnose',{},remote=True)[1]
        assert before['status']=='insufficient_evidence'
        learned=request('/api/learn',{},remote=True)[1]
        assert learned['after']['selected_origin_id']=='config:currency'
        assert request('/api/graph')[1]['edges']
        text=json.dumps([request('/api/observations')[1],learned,request('/api/evidence')[1]])
        assert not any(k in text for k in ['expected_origin_id','fault_value','fixtures/private','private_fault_id'])
        assert request('/fixtures/private/heldout.json')[0]==404
        assert request('/api/query',{'query':'MATCH (n)'})[0]==404
        assert request('/local/restore',{})[0]==200
        assert all(o['status']=='healthy' for o in request('/api/observations')[1]['observations'])
    finally:
        server.shutdown(); server.server_close(); app.graph.reset()
