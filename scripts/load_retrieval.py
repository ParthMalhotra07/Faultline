"""Labeled generated-graph load, separate from incident accuracy and LLM work."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import threading
import time
import uuid
from faultline.graph.adapter import HydraAdapter,QUERIES

ROOT=Path(__file__).resolve().parents[1]
started_at=datetime.now(timezone.utc).isoformat()
out=ROOT/'artifacts/load'/time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
out.mkdir(parents=True)
scope='load-'+uuid.uuid4().hex
QUERIES.update({
    'load_nodes':'UNWIND $rows AS row MERGE (n {id: row.id}) SET n:Load, n.scope = row.scope, n.version = row.version',
    'load_edges':'UNWIND $rows AS row CREATE (a {id: row.src})-[:LOAD_LINK]->(b {id: row.dst})',
    'load_path':'MATCH (a:Load {id: $src})-[:LOAD_LINK]->(b)-[:LOAD_LINK]->(c) RETURN c.id AS id LIMIT 101',
    'load_node_count':'MATCH (n:Load) WHERE n.scope = $scope RETURN count(*) AS total',
    'load_edge_count':'MATCH (a:Load)-[:LOAD_LINK]->(b) WHERE a.scope = $scope RETURN count(*) AS total',
    'load_update':'MATCH (n:Load {id: $id}) SET n.version = $version',
    'load_read':'MATCH (n:Load {id: $id}) RETURN n.version AS version LIMIT 2',
    'load_delete':'MATCH (n {id: $id}) DETACH DELETE n',
})
def vid(i):return int.from_bytes(hashlib.sha256(f'{scope}:{i}'.encode()).digest()[:6],'big')
ids=[vid(i) for i in range(300)]
assert len(set(ids))==300
g=HydraAdapter.from_environment()
local=threading.local()
def request(i):
    if not hasattr(local,'graph'):local.graph=HydraAdapter.from_environment()
    graph=local.graph
    src=i%100*3
    started=time.perf_counter()
    try:
        rows=graph.execute('load_path',{'src':ids[src]})
        if rows!=[{'id':ids[src+2]}]:raise RuntimeError('Incomplete or wrong traversal')
        return dict(request=i,elapsed_ms=(time.perf_counter()-started)*1000,status='ok')
    except Exception as e:
        return dict(request=i,elapsed_ms=(time.perf_counter()-started)*1000,status='error',error=type(e).__name__)
    finally:graph.trace.clear()

try:
    g.execute('load_nodes',{'rows':[dict(id=i,scope=scope,version='before') for i in ids]})
    edges=[dict(src=ids[i+j],dst=ids[i+j+1]) for i in range(0,300,3) for j in (0,1)]
    g.execute('load_edges',{'rows':edges})
    node_count=g.execute('load_node_count',{'scope':scope})[0]['total']
    edge_count=g.execute('load_edge_count',{'scope':scope})[0]['total']
    assert (node_count,edge_count)==(300,200)
    g.execute('load_update',{'id':ids[0],'version':'after'})
    assert g.execute('load_read',{'id':ids[0]})==[{'version':'after'}]
    summary=[]
    for clients in (1,5,10):
        with ThreadPoolExecutor(max_workers=clients) as pool:
            warmup=list(pool.map(request,range(10)))
            started=time.perf_counter()
            rows=list(pool.map(request,range(500)))
            elapsed=time.perf_counter()-started
        durations=sorted(r['elapsed_ms'] for r in rows)
        successes=sum(r['status']=='ok' for r in rows)
        (out/f'clients-{clients}.json').write_text(json.dumps(rows,indent=2)+'\n')
        summary.append(dict(clients=clients,requests=500,successes=successes,errors=500-successes,
            warmup_requests=10,warmup_errors=sum(r['status']!='ok' for r in warmup),
            elapsed_seconds=elapsed,successful_requests_per_second=successes/elapsed,
            p50_ms=statistics.median(durations),p95_ms=durations[int(.95*(len(durations)-1))],cache='warm after 10 warmup requests; no cold-cache claim'))
        print(f'{clients} clients: {successes}/500 successful, p95={summary[-1]["p95_ms"]:.2f}ms',flush=True)
    raw=subprocess.run(['docker','inspect','faultline-hydra','--format','{{.HostConfig.NanoCpus}} {{.HostConfig.Memory}}'],capture_output=True,text=True,check=True).stdout.strip()
    report=dict(label='Generated isolated 100 chains; NOT real incident diversity',
        nodes=node_count,edges=edge_count,scope=scope,started_at=started_at,completed_at=datetime.now(timezone.utc).isoformat(),
        host=platform.platform(),cpu=platform.processor(),logical_cpus=os.cpu_count(),docker_cpu_memory_limits=raw,
        database='Official HydraDB 0.4.0 Docker on local Windows host',
        bounds=dict(hops=2,query_limit=101,page_rows=1001,timeout_ms=5000,requests_per_level=500),
        write_visible_read=True,levels=summary)
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'artifacts/load/latest.json').write_text(json.dumps(dict(directory=str(out.relative_to(ROOT)).replace('\\','/')),indent=2)+'\n')
    assert all(r['errors']==0 and r['warmup_errors']==0 for r in summary)
finally:
    for i in ids:g.execute('load_delete',{'id':i})
