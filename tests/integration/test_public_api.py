import json
import threading
import urllib.request
import urllib.error
import uuid
from types import SimpleNamespace
from faultline.api import App, make_server
from faultline.ingestion.inspector import Inspector
from faultline.ingestion.commit import ingest
from faultline.learning.runner import DEFAULT_BUDGET


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
        assert request('healthcheck.railway.app')==403
        assert request('faultline.example',origin='https://other.example',body={})==403
        assert request('faultline.example',origin='http://faultline.example',body={})==403
        assert request('faultline.example',origin='https://faultline.example',body={})!=403
    finally:
        server.shutdown();server.server_close()


def test_railway_healthcheck_host_can_only_read_health():
    app=SimpleNamespace(lock=threading.RLock())
    server=make_server(app,port=0,public_origin='https://faultline.example',allow_railway_healthcheck=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    def request(host,path,post=False):
        req=urllib.request.Request(base+path,headers={'Host':host},data=b'{}' if post else None)
        try:
            with urllib.request.urlopen(req) as response:return response.status
        except urllib.error.HTTPError as exc:return exc.code
    try:
        assert request('healthcheck.railway.app','/api/health')==200
        assert request('healthcheck.railway.app','/')==403
        assert request('healthcheck.railway.app','/api/results')==403
        assert request('healthcheck.railway.app','/local/trigger',post=True)==403
        assert request('other.example','/api/health')==403
    finally:
        server.shutdown();server.server_close()


def test_landing_and_live_workspace_routes_are_distinct():
    app=SimpleNamespace(lock=threading.RLock())
    server=make_server(app,port=0)
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        with urllib.request.urlopen(base+'/') as response:
            landing=response.read().decode()
        with urllib.request.urlopen(base+'/workspace') as response:
            workspace=response.read().decode()
        assert 'id="particle-wave"' in landing
        assert 'href="/workspace"' in landing
        assert 'id="trigger"' in workspace
        assert 'id="trigger"' not in landing
        assert 'class="identity" href="/"' in workspace
    finally:
        server.shutdown();server.server_close()


def test_public_demo_session_lifecycle():
    app=SimpleNamespace(lock=threading.RLock())
    server=make_server(app,port=0,public_origin='https://faultline.example')
    thread=threading.Thread(target=server.serve_forever,daemon=True); thread.start()
    base=f'http://127.0.0.1:{server.server_port}'

    def request(path,data=None,cookie=None,origin='https://faultline.example'):
        headers={'Host':'faultline.example','X-Faultline-Local':'sandbox',
                 'Content-Type':'application/json'}
        if origin is not None: headers['Origin']=origin
        if cookie: headers['Cookie']=cookie
        req=urllib.request.Request(base+path,headers=headers,
            data=json.dumps(data).encode() if data is not None else None)
        try:
            with urllib.request.urlopen(req) as response:
                return response.status,json.load(response),response.headers
        except urllib.error.HTTPError as error:
            return error.code,json.load(error),error.headers

    try:
        assert request('/api/demo/session')[1]['signed_in'] is False
        credentials={'email':'judge@faultline.demo','password':'FaultlineDemo2026!'}
        assert request('/api/demo/sign-in',credentials | {'password':'wrong'})[0]==401
        assert request('/api/demo/sign-in',credentials,origin='https://other.example')[0]==403
        status,result,headers=request('/api/demo/sign-in',credentials)
        assert status==200 and result['signed_in'] is True
        cookie=headers['Set-Cookie']
        assert 'HttpOnly' in cookie and 'SameSite=Lax' in cookie and 'Secure' in cookie
        assert request('/api/demo/session',cookie=cookie.split(';',1)[0])[1]['signed_in'] is True
        assert request('/api/demo/sign-out',{},cookie=cookie.split(';',1)[0])[0]==200
        assert request('/api/demo/session',cookie=cookie.split(';',1)[0])[1]['signed_in'] is False
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


def test_public_demo_abstains_when_learned_paths_do_not_distinguish_settings(tmp_path):
    """A shorter graph path alone cannot establish the changed setting's cause."""
    app=App('api-ambiguity-'+uuid.uuid4().hex,tmp_path)
    server=None
    try:
        for round_number,source_id in enumerate(('source:shared','source:checkout'),start=1):
            records=Inspector(app.catalog,DEFAULT_BUDGET,app.graph.version,
                              app.graph.manifest['sources']).inspect(source_id)
            ingest(app.graph,app.catalog,records,round_number)
        app.trigger('demo-currency')
        server=make_server(app,port=0)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        req=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/diagnose',
            headers={'X-Faultline-Local':'sandbox','Content-Type':'application/json'},data=b'{}')
        with urllib.request.urlopen(req,timeout=15) as response:
            answer=json.load(response)
        assert answer['status']=='ambiguous'
        assert answer['selected_origin_id'] is None
        assert {'config:currency','config:inventory'} <= {
            row['entity_id'] for row in answer['ranked_candidates']}
        assert 'shorter' in answer['gap_reason'].lower()
    finally:
        if server:
            server.shutdown();server.server_close()
        app.graph.reset()
