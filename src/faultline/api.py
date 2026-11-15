"""Loopback-only demo HTTP API, no arbitrary queries/files or private DTOs."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import CookieError, SimpleCookie
import hmac
import json
from pathlib import Path
import secrets
import threading
import time
from urllib.parse import urlsplit
from faultline.contracts import PublicIncident
from faultline.diagnosis.ranker import diagnose
from faultline.evaluation.controller import Controller, load_scenarios
from faultline.graph.adapter import GraphError
from faultline.graph.store import GraphStore
from faultline.ingestion.catalog import Catalog
from faultline.learning.runner import learn_round
from faultline.sandbox.flows import Sandbox

ROOT=Path(__file__).resolve().parents[2]
PUBLIC_DEMO_EMAIL='judge@faultline.demo'
PUBLIC_DEMO_PASSWORD='FaultlineDemo2026!'  # Published test value, never a private credential.
DEMO_SESSION_SECONDS=8 * 60 * 60


class App:
    def __init__(self,namespace='demo-web',directory=None):
        self.sandbox=Sandbox()
        self.sandbox.observe(100)
        self.catalog=Catalog.from_telemetry(self.sandbox.config.telemetry(),self.sandbox.source_version)
        self.graph=GraphStore(namespace,self.sandbox.source_version,directory)
        if not self.graph.manifest['claims']: self.graph.seed()
        self.lock=threading.RLock()
        self.context=None
        self.public=PublicIncident(observations=self.sandbox.observe(100000),changes=[])
        self.last=None

    def restore(self):
        if self.context:
            self.context.__exit__(None,None,None); self.context=None
        self.sandbox.reset()
        self.public=PublicIncident(observations=self.sandbox.observe(100000),changes=[])
        self.last=None
        return self.public.model_dump()

    def trigger(self,name):
        cases={'demo-currency':load_scenarios('development')[0],
               'demo-transfer':load_scenarios('development')[1],
               'demo-billing':load_scenarios('learning')[1],
               'demo-inventory':load_scenarios('learning')[2]}
        if name not in cases: raise ValueError('Unknown demo scenario')
        self.restore()
        self.context=Controller(self.sandbox).incident(cases[name])
        self.public=self.context.__enter__()
        return self.public.model_dump()

    def graph_view(self):
        nodes=set(); edges={}
        for endpoint in ('endpoint:checkout','endpoint:refunds','endpoint:renewals'):
            for p in self.graph.paths(endpoint):
                nodes.update(p['entity_ids'])
                for a,b,c,e in zip(p['entity_ids'],p['entity_ids'][1:],p['claim_ids'],p['evidence_ids']):
                    claim=self.graph.manifest['claims'][c]
                    edges[c]=dict(id=c,from_id=a,to_id=b,relationship_type=claim['kind'],evidence_id=e)
        return dict(nodes=[dict(id=n,kind=n.split(':')[0]) for n in sorted(nodes)],
                    edges=list(edges.values()),manifest_hash=self.graph.manifest_hash(),source='live HydraDB traversal')


def make_server(app,port=8765,public_origin=None,bind_host='127.0.0.1',allow_railway_healthcheck=False):
    public_host=None
    if public_origin is not None:
        parsed=urlsplit(public_origin)
        if (parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password
                or parsed.path or parsed.query or parsed.fragment or public_origin.rstrip('/')!=public_origin):
            raise ValueError('Public origin must be an exact HTTPS origin')
        public_host=parsed.netloc
    demo_sessions={}
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass  # Do not log arbitrary request payloads/paths.

        def send(self,status,value,extra_headers=()):
            raw=json.dumps(value).encode()
            self.send_response(status); self.send_header('Content-Type','application/json')
            self.send_header('Cache-Control','no-store'); self.send_header('X-Content-Type-Options','nosniff')
            for name,header_value in extra_headers:
                self.send_header(name,header_value)
            self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)

        def demo_token(self):
            cookie=SimpleCookie()
            try: cookie.load(self.headers.get('Cookie',''))
            except CookieError: return None
            morsel=cookie.get('faultline_demo')
            token=morsel.value if morsel else None
            if not token: return None
            expires=demo_sessions.get(token,0)
            if expires<=time.monotonic():
                demo_sessions.pop(token,None)
                return None
            return token

        def demo_cookie(self,token,remote_host,max_age=DEMO_SESSION_SECONDS):
            value=token or ''
            secure='; Secure' if remote_host else ''
            return f'faultline_demo={value}; Path=/; Max-Age={max_age}; HttpOnly; SameSite=Lax{secure}'

        def do_GET(self): self.dispatch('GET')
        def do_POST(self): self.dispatch('POST')

        def dispatch(self,method):
            raw_host=self.headers.get('Host','')
            path=urlsplit(self.path).path
            try: host=urlsplit('http://'+raw_host).hostname
            except ValueError: host=None
            local_host=host in ('localhost','127.0.0.1')
            remote_host=bool(public_host and raw_host==public_host)
            railway_health=bool(allow_railway_healthcheck and raw_host=='healthcheck.railway.app'
                                and method=='GET' and path=='/api/health')
            if not (local_host or remote_host or railway_health):
                return self.send(403,dict(error='Configured demo Host required'))
            if method=='POST':
                if path not in ('/local/trigger','/local/restore','/local/reset-experiment',
                                '/api/diagnose','/api/learn','/api/demo/sign-in','/api/demo/sign-out'):
                    return self.send(404,dict(error='Route not found'))
                origin=self.headers.get('Origin')
                expected_origin=public_origin if remote_host else 'http://'+raw_host
                if (self.headers.get('X-Faultline-Local')!='sandbox'
                        or (remote_host and origin!=expected_origin)
                        or (local_host and origin and origin!=expected_origin)):
                    return self.send(403,dict(error='Same-origin sandbox control required'))
                try:
                    length=int(self.headers.get('Content-Length',0))
                    if not 0<=length<=2048: raise ValueError()
                    data=json.loads(self.rfile.read(length) or b'{}')
                    if not isinstance(data,dict): raise ValueError()
                    allowed={'scenario'} if path=='/local/trigger' else (
                        {'email','password'} if path=='/api/demo/sign-in' else set())
                    if set(data)-allowed: raise ValueError()
                except (ValueError,TypeError):
                    return self.send(400,dict(error='Invalid or extra request fields'))
            try:
                with app.lock:
                    if method=='GET':
                        if path=='/api/health': return self.send(200,dict(status='ok',database='HydraDB',scope='railway healthcheck' if railway_health else 'public sandbox demo' if remote_host else 'local sandbox'))
                        if path=='/api/demo/session':
                            token=self.demo_token()
                            return self.send(200,dict(signed_in=bool(token),
                                email=PUBLIC_DEMO_EMAIL if token else None,
                                scope='public_demo'))
                        if path=='/api/observations': return self.send(200,app.public.model_dump())
                        if path=='/api/graph': return self.send(200,app.graph_view())
                        if path=='/api/sources': return self.send(200,[m.model_dump() | dict(inspected=m.sha256 in app.graph.manifest['sources']) for m in app.catalog.metadata()])
                        if path=='/api/evidence': return self.send(200,app.graph.manifest['evidence'])
                        if path=='/api/results':
                            latest=json.loads((ROOT/'artifacts/eval/latest.json').read_text())
                            return self.send(200,json.loads((ROOT/latest['directory']/'aggregate.json').read_text()))
                        if path=='/api/replay':
                            r=json.loads((ROOT/'artifacts/pilot-transfer/result.json').read_text())
                            trace=r['learning']; nodes=set(); edges={}
                            for p in trace['after']['explanation_paths']:
                                nodes.update(p['entity_ids'])
                                for start,end,key,evidence in zip(p['entity_ids'],p['entity_ids'][1:],p['claim_ids'],p['evidence_ids']):
                                    claim=trace['snapshot']['claims'][key]
                                    edges[key]=dict(id=key,from_id=start,to_id=end,relationship_type=claim['kind'],evidence_id=evidence)
                            recorded_graph=dict(nodes=[dict(id=n,kind=n.split(':')[0]) for n in sorted(nodes)],
                                edges=list(edges.values()),manifest_hash=trace['after']['snapshot_manifest_hash'],source='recorded HydraDB explanation paths')
                            return self.send(200,dict(recorded=True,before=trace['before'],after=trace['after'],graph=recorded_graph,
                                public_input=trace['public_input'],inspection=trace['inspection'],ledger=trace['ledger']))
                        static_files={'/':'landing.html','/workspace':'index.html','/workspace/':'index.html',
                                      '/landing.css':'landing.css','/landing.js':'landing.js',
                                      '/app.js':'app.js','/style.css':'style.css',
                                      '/onboarding.js':'onboarding.js',
                                      '/faultline-logo.png':'faultline-logo.png'}
                        if path in static_files:
                            name=static_files[path]
                            file=ROOT/'web'/name
                            if file.exists():
                                raw=file.read_bytes(); self.send_response(200)
                                self.send_header('Content-Type','text/html; charset=utf-8' if name.endswith('.html') else
                                                 'text/javascript; charset=utf-8' if name.endswith('.js') else
                                                 'image/png' if name.endswith('.png') else 'text/css; charset=utf-8')
                                self.send_header('X-Content-Type-Options','nosniff')
                                self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw); return
                    if method=='POST':
                        if path=='/api/demo/sign-in':
                            email=data.get('email'); password=data.get('password')
                            if (not isinstance(email,str) or not isinstance(password,str)
                                    or len(email)>254 or len(password)>128):
                                return self.send(400,dict(error='Invalid demo sign-in fields'))
                            if (not hmac.compare_digest(email.casefold(),PUBLIC_DEMO_EMAIL)
                                    or not hmac.compare_digest(password,PUBLIC_DEMO_PASSWORD)):
                                return self.send(401,dict(error='Invalid public demo credentials'))
                            now=time.monotonic()
                            for token,expires in tuple(demo_sessions.items()):
                                if expires<=now: demo_sessions.pop(token,None)
                            if len(demo_sessions)>=256:
                                demo_sessions.pop(next(iter(demo_sessions)))
                            token=secrets.token_urlsafe(32)
                            demo_sessions[token]=now+DEMO_SESSION_SECONDS
                            return self.send(200,dict(signed_in=True,email=PUBLIC_DEMO_EMAIL,scope='public_demo'),
                                [('Set-Cookie',self.demo_cookie(token,remote_host))])
                        if path=='/api/demo/sign-out':
                            token=self.demo_token()
                            if token: demo_sessions.pop(token,None)
                            return self.send(200,dict(signed_in=False,scope='public_demo'),
                                [('Set-Cookie',self.demo_cookie(None,remote_host,0))])
                        if path=='/local/trigger': return self.send(200,app.trigger(data.get('scenario')))
                        if path=='/local/restore': return self.send(200,app.restore())
                        if path=='/local/reset-experiment':
                            app.restore(); app.graph.reset(); app.graph.seed()
                            return self.send(200,dict(manifest_hash=app.graph.manifest_hash()))
                        if path=='/api/diagnose':
                            app.last=diagnose(app.graph,app.public).model_dump()
                            return self.send(503 if app.last['status']=='error' else 200,app.last)
                        if path=='/api/learn':
                            trace=learn_round(app.graph,app.public,app.catalog)
                            app.last=trace['after']
                            return self.send(200,{k:trace[k] for k in ['before','after','inspection','ledger','budget','exhausted']})
                    return self.send(404,dict(error='Route not found'))
            except (ValueError,KeyError): return self.send(400,dict(error='Invalid sandbox operation'))
            except (GraphError,RuntimeError): return self.send(503,dict(error='Graph operation failed or retrieval incomplete'))
            except FileNotFoundError: return self.send(503,dict(error='Verified artifact not available'))
    return ThreadingHTTPServer((bind_host,port),Handler)
