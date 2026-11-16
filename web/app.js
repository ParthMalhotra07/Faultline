const $=id=>document.getElementById(id);
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let replay=false;
document.querySelectorAll('.nav-item').forEach(item=>item.addEventListener('click',()=>{
  document.querySelectorAll('.nav-item').forEach(link=>link.classList.remove('active'));
  item.classList.add('active');
}));
async function api(path,data){const r=await fetch(path,{method:data===undefined?'GET':'POST',headers:{'Content-Type':'application/json','X-Faultline-Local':'sandbox'},body:data===undefined?undefined:JSON.stringify(data)});const value=await r.json();if(!r.ok)throw Error(value.error||value.gap_reason||`Request failed (${r.status})`);return value;}
const demoGate=$('demo-gate');
const demoForm=$('demo-form');
const demoError=$('demo-error');

async function enterWorkspace(){
  demoGate.hidden=true;
  document.querySelector('.shell').inert=false;
  document.body.classList.remove('access-open');
  try{
    await Promise.all([refresh(),loadResults()]);
    notice('Public demo ready. Start with Trigger fault.');
  }catch(error){notice(error.message,true);}
  window.FaultlineTour.maybeStart();
}

demoForm.addEventListener('submit',async event=>{
  event.preventDefault();
  const submit=demoForm.querySelector('button[type="submit"]');
  submit.disabled=true;
  demoError.hidden=true;
  try{
    await api('/api/demo/sign-in',{
      email:$('demo-email').value.trim(),
      password:$('demo-password').value,
    });
    await enterWorkspace();
  }catch(error){
    demoError.textContent=error.message;
    demoError.hidden=false;
  }finally{submit.disabled=false;}
});

$('take-tour').addEventListener('click',()=>window.FaultlineTour.start(true));
$('signout').addEventListener('click',async()=>{
  try{
    await api('/api/demo/sign-out',{});
    window.FaultlineTour.stop(false);
    document.querySelector('.shell').inert=true;
    demoGate.hidden=false;
    document.body.classList.add('access-open');
    $('demo-email').focus();
  }catch(error){notice(error.message,true);}
});

async function bootstrapDemo(){
  try{
    const session=await api('/api/demo/session');
    if(session.signed_in){await enterWorkspace();return;}
    $('demo-email').focus();
  }catch(error){
    demoError.textContent='Demo access is temporarily unavailable: '+error.message;
    demoError.hidden=false;
  }
}
function notice(text,error=false){$('notice').textContent=text;$('notice').className=error?'error':'';}
function health(publicData){const byId=Object.fromEntries(publicData.observations.map(o=>[o.endpoint_id,o]));$('health').innerHTML=['checkout','refunds','renewals'].map(name=>{const o=byId[`endpoint:${name}`];return `<div class="health-card ${esc(o?.status||'unknown')}"><b>${esc(name)}</b><span>${o?(o.status==='healthy'?'● Healthy':'● Acceptance failed'):'○ Not monitored'}</span></div>`;}).join('');}
function diagnosis(d,inspection){$('diagnosis-status').textContent=d.status.replaceAll('_',' ').toUpperCase();const title=d.selected_origin_id||({'ambiguous':'Evidence is tied','insufficient_evidence':'A dependency is missing','error':'Retrieval failed'}[d.status])||'No selection';$('diagnosis').innerHTML=`<div class="diagnosis-body"><p class="eyebrow">${d.selected_origin_id?'SUPPORTED HYPOTHESIS':'INVESTIGATION STATE'}</p><div class="origin">${esc(title)}</div><p>${esc(d.gap_reason||'Supported by the current dependency paths. Graph reachability is a diagnostic heuristic.')}</p>${inspection?`<p>Inspected <b>${esc(inspection.source_id)}</b> · ${inspection.estimated_bytes} bytes</p>`:''}${d.ranked_candidates.slice(0,4).map(c=>`<div class="rank"><b>${esc(c.entity_id)}</b><span>${c.failing_coverage} failing / ${c.healthy_contradictions} healthy</span></div>`).join('')}<p>${d.evidence_ids.length} evidence references · ${Number(d.elapsed_ms).toFixed(1)} ms</p></div>`;}
function graph(data){
  const nodes=data.nodes,edges=data.edges;
  const group=n=>n.kind==='endpoint'?0:n.kind==='config'?3:['service:pricing','service:billing'].includes(n.id)?2:1;
  const names=['ENDPOINTS','FLOW SERVICES','SHARED SERVICES','CONFIG KEYS'];
  const positions={};
  let svg='<svg viewBox="0 0 1000 510" xmlns="http://www.w3.org/2000/svg"><defs><marker id="graph-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M1,1 L7,4 L1,7" fill="none" stroke="#6e707a" stroke-width="1.2"/></marker></defs>';
  for(let col=0;col<4;col++){
    const ns=nodes.filter(n=>group(n)===col),x=38+col*238;
    svg+=`<text class="graph-lane" x="${x}" y="38">${names[col]} <tspan fill="#525560">${ns.length}</tspan></text>`;
    if(col)svg+=`<line class="graph-guide" x1="${x-29}" y1="65" x2="${x-29}" y2="474"/>`;
    ns.forEach((n,i)=>positions[n.id]={x,y:ns.length===1?237:100+i*(320/(ns.length-1))});
  }
  for(const e of edges){
    const a=positions[e.from_id],b=positions[e.to_id];if(!a||!b)continue;
    const ax=a.x+170,ay=a.y+32,bx=b.x,by=b.y+32,mid=(ax+bx)/2;
    svg+=`<path class="edge ${e.relationship_type==='READS_CONFIG'?'learned':''}" d="M${ax},${ay} C${mid},${ay} ${mid},${by} ${bx},${by}" marker-end="url(#graph-arrow)"><title>${esc(e.from_id+' '+e.relationship_type+' '+e.to_id+' · '+e.evidence_id)}</title></path>`;
  }
  for(const n of nodes){
    const p=positions[n.id],kind=n.kind==='config'?'CONFIG KEY':n.kind.toUpperCase();
    svg+=`<g class="node ${esc(n.kind)}" transform="translate(${p.x},${p.y})"><title>${esc(n.id)}</title><rect width="170" height="64" rx="7"/><text class="node-type" x="14" y="22">${kind}</text><text class="node-name" x="14" y="45">${esc(n.id.split(':')[1])}</text></g>`;
  }
  svg+='</svg>';
  $('graph').innerHTML=svg;
  $('graph-count').textContent=`${nodes.length} NODES · ${edges.length} CLAIMS`;
  $('manifest').textContent=`${replay?'Recorded path':'Live snapshot'} ${data.manifest_hash?.slice(0,16)||''}`;
}
async function refresh(){const [observed,g,sources,evidence]=await Promise.all([api('/api/observations'),api('/api/graph'),api('/api/sources'),api('/api/evidence')]);health(observed);graph(g);$('sources').innerHTML=sources.map(s=>`<div class="source ${s.inspected?'done':''}"><b>${esc(s.source_id.replace('source:',''))} ${s.inspected?'✓':''}</b><span>${s.estimated_bytes} bytes</span></div>`).join('');$('evidence').textContent=JSON.stringify(evidence,null,2);}
async function action(label,fn){document.querySelectorAll('button').forEach(b=>b.disabled=true);notice(label+'…');try{replay=false;$('mode').textContent='● LIVE SANDBOX';const message=await fn();await refresh();notice(typeof message==='string'?message:'Complete. App state, graph paths and evidence refreshed from the backend.');}catch(e){notice(e.message,true);}finally{document.querySelectorAll('button').forEach(b=>b.disabled=false);}}
$('trigger').onclick=()=>action('Executing sandbox fault',async()=>{await api('/local/trigger',{scenario:$('scenario').value});$('diagnosis-status').textContent='FAULT ACTIVE';$('diagnosis').innerHTML='<div class="empty"><h3>Behavior changed.</h3><p>Investigate using the current graph. The selected demo control is kept out of investigator inputs.</p></div>';});
$('diagnose').onclick=()=>action('Traversing HydraDB',async()=>diagnosis(await api('/api/diagnose',{})));
$('learn').onclick=()=>action('Inspecting bounded evidence and committing claims',async()=>{const r=await api('/api/learn',{});diagnosis(r.after,r.inspection);if(r.exhausted)return 'No unseen relevant evidence sources remain.';});
$('restore').onclick=()=>action('Restoring sandbox configuration',async()=>{await api('/local/restore',{});$('diagnosis-status').textContent='RESTORED';$('diagnosis').innerHTML='<div class="empty"><h3>Healthy again.</h3><p>Learned relationships remain. Trigger the refunds transfer incident to investigate with the improved map.</p></div>';});
$('reset').onclick=()=>action('Resetting only this demo experiment',async()=>{await api('/local/reset-experiment',{});$('diagnosis-status').textContent='RESET';$('diagnosis').innerHTML='<div class="empty"><h3>Back to the initial map.</h3><p>Known handlers and calls remain. Configuration evidence is uninspected.</p></div>';});
// Results and replay are added from verified artifacts, never placeholder metrics.
const methodStyles={frozen:{label:'Frozen graph',color:'#777b87',dash:'3 5'},random:{label:'Random ingestion',color:'#a8a0c9',dash:'8 4'},adaptive:{label:'Gap-driven ingestion',color:'#e4e2ed',dash:''},'same-evidence-token-overlap':{label:'Same-evidence token overlap',color:'#cdb987',dash:'3 4'}};
async function loadResults(){try{const data=await api('/api/results');const rows=data.rows.filter(r=>!r.method.startsWith('ablation'));$('results-section').hidden=false;$('result-caption').textContent=`Controlled executable commerce fixtures · protocol ${data.protocol} · ${data.cases_per_seed} distinct held-out scenarios × ${data.seeds.length} fixed seeds (${data.seeds.join(', ')}) · counts pooled across seeds. Two telemetry sources; no statistical superiority claim. The live demo additionally abstains when path length alone separates otherwise tied candidates; this guard was not part of frozen protocol v1.`;let svg='<svg viewBox="0 0 1080 280" role="img" aria-label="Actual held-out top-1 accuracy over six learning incidents">';const x=r=>75+r*155,y=v=>220-v*1.75;for(const value of [0,25,50,75,100])svg+=`<line class="gridline" x1="75" x2="1005" y1="${y(value)}" y2="${y(value)}"/><text class="chart-label" x="58" y="${y(value)+4}" text-anchor="end">${value}%</text>`;for(let round=0;round<=6;round++)svg+=`<text class="chart-label" x="${x(round)}" y="243" text-anchor="middle">${round}</text>`;svg+='<text class="chart-label" x="75" y="24">Held-out top-1 accuracy (%)</text><text class="chart-label" x="540" y="270" text-anchor="middle">Learning incidents processed</text>';for(const [method,style]of Object.entries(methodStyles)){const points=rows.filter(r=>r.method===method).sort((a,b)=>a.round-b.round);svg+=`<polyline fill="none" stroke="${style.color}" stroke-width="${method==='random'?4:2}" stroke-dasharray="${style.dash}" points="${points.map(r=>`${x(r.round)},${y(r.accuracy*100)}`).join(' ')}"/>`;for(const r of points)svg+=`<circle cx="${x(r.round)}" cy="${y(r.accuracy*100)}" r="${method==='random'?5:3}" fill="${style.color}" data-method="${method}" data-round="${r.round}" data-correct="${r.correct}" data-total="${r.total}"><title>${esc(style.label)} · round ${r.round}: ${r.correct}/${r.total} correct, ${r.abstentions} abstentions, ${r.errors} errors</title></circle>`;}$('chart').innerHTML=svg+'</svg>';$('result-legend').innerHTML=Object.entries(methodStyles).map(([m,s])=>`<span><i style="background:${s.color}"></i>${esc(s.label)}</span>`).join('');const ablation=data.rows.find(r=>r.method.startsWith('ablation')),adaptive=data.rows.find(r=>r.method==='adaptive'&&r.round===6);$('ablation').textContent=`Structural ablation: removing pricing → currency claims from an isolated final graph changed correct answers from ${adaptive.correct}/${adaptive.total} to ${ablation.correct}/${ablation.total}. This supports a structural effect on these fixtures. Random ingestion also reaches ${adaptive.correct}/${adaptive.total} after both sources are acquired. Token overlap is lexical retrieval, not a semantic/vector baseline.`;const details=document.createElement('details');details.className='result-counts';details.innerHTML='<summary>All observed counts, abstentions and errors</summary><div>'+data.rows.map(r=>`<p>${esc(methodStyles[r.method]?.label||'Ablation: no pricing → currency')} · round ${r.round}: <b>${r.correct}/${r.total}</b> correct · ${r.abstentions} abstentions · ${r.errors} errors</p>`).join('')+'</div>';$('results-section').append(details);}catch(e){notice('Measured results unavailable: '+e.message,true);}}
$('replay').onclick=async()=>{document.querySelectorAll('button').forEach(b=>b.disabled=true);try{const r=await api('/api/replay');replay=true;$('mode').textContent='◷ RECORDED DEVELOPMENT RUN';health(r.public_input);diagnosis(r.after,r.inspection);graph(r.graph);$('evidence').textContent=JSON.stringify({before:r.before,after:r.after,inspection:r.inspection,ledger:r.ledger},null,2);notice('Recorded pilot replay. These are saved HydraDB paths and evidence; no live fault or graph mutation occurred.');$('diagnosis').scrollIntoView({behavior:'smooth',block:'center'});}catch(e){notice(e.message,true);}finally{document.querySelectorAll('button').forEach(b=>b.disabled=false);}};
bootstrapDemo();
