/* Origyn-inspired landing motion, adapted to FAULTLINE's live public API. */
const byId=id=>document.getElementById(id);
const reducedMotion=window.matchMedia('(prefers-reduced-motion: reduce)');

function revealSections(){
  const elements=[...document.querySelectorAll('.reveal')];
  if(reducedMotion.matches||!('IntersectionObserver' in window)){
    elements.forEach(el=>el.classList.add('reveal-visible'));
    return;
  }
  elements.forEach(el=>el.classList.add('reveal-ready'));
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
    if(!entry.isIntersecting)return;
    requestAnimationFrame(()=>entry.target.classList.add('reveal-visible'));
    observer.unobserve(entry.target);
  }),{threshold:.08,rootMargin:'0px 0px -10% 0px'});
  elements.forEach(el=>observer.observe(el));
}

function particleWave(){
  const canvas=byId('particle-wave'),ctx=canvas.getContext('2d',{alpha:true});
  if(!ctx)return;
  const stages=['.hero','#intake','#planning','#automation','#build','#closing'];
  let width=0,height=0,dpr=1,cols=0,rows=0,targetStage=0,stage=0,mouseX=0,mouseY=0,targetMouseX=0,targetMouseY=0,frame=0;
  const hash=(x,y)=>{let n=Math.sin(x*127.1+y*311.7)*43758.5453;return n-Math.floor(n)};
  function resize(){
    width=innerWidth;height=innerHeight;dpr=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);
    ctx.setTransform(dpr,0,0,dpr,0,0);
    cols=width<700?67:width<1100?89:123;
    rows=width<700?22:34;
    stageAtScroll();
    if(reducedMotion.matches)draw(0);
  }
  function stageAtScroll(){
    const point=scrollY+innerHeight*.55;
    const anchors=stages.map((selector,index)=>({index,top:document.querySelector(selector)?.getBoundingClientRect().top+scrollY||0}));
    if(point<=anchors[0].top){targetStage=0;return}
    if(point>=anchors.at(-1).top){targetStage=5;return}
    for(let i=0;i<anchors.length-1;i++)if(point>=anchors[i].top&&point<=anchors[i+1].top){
      const distance=Math.max(1,anchors[i+1].top-anchors[i].top),t=(point-anchors[i].top)/distance;
      targetStage=i+t*t*(3-2*t);return;
    }
  }
  function waveShape(u,v,t,s){
    const broad=Math.sin(u*7.3-t*.35+v*1.4)*.11+Math.sin(u*15+t*.22)*.035;
    const valley=-.14*Math.exp(-Math.pow((u-.52)*4,2));
    const arch=.16*Math.sin(Math.PI*u);
    const braid=Math.sin(u*12+v*5+t*.5)*.09;
    const shape=[broad,broad*.45+valley,arch+Math.sin(u*9+t*.25)*.04,braid,Math.sin(u*20-t*.6)*.025,arch*.4+Math.sin(u*6+t*.2)*.08];
    const index=Math.max(0,Math.min(4,Math.floor(s))),blend=s-index;
    return shape[index]*(1-blend)+shape[index+1]*blend;
  }
  function draw(time){
    ctx.clearRect(0,0,width,height);
    const t=time*.001;
    const drift=reducedMotion.matches?0:t;
    const yBase=height*(width<700?.28:.32),fieldHeight=height*(width<700?.65:.73);
    for(let x=0;x<cols;x++){
      const u=x/(cols-1);
      for(let y=0;y<rows;y++){
        const v=y/(rows-1),rnd=hash(x,y);
        const xPos=u*width+(rnd-.5)*5+mouseX*(1-v)*8;
        const swell=waveShape(u,v,drift,stage);
        const yPos=yBase+v*fieldHeight+swell*height*(.5+.4*v)+mouseY*(u-.5)*12;
        if(yPos<0||yPos>height)continue;
        const edgeFade=Math.min(1,u*7,(1-u)*7,v*5,(1-v)*5);
        const center=1-Math.abs(v-.52)*1.25;
        const twinkle=reducedMotion.matches?1:.82+.18*Math.sin(drift*1.2+rnd*15);
        const alpha=Math.max(0,Math.min(.69,(.10+.47*center)*edgeFade*twinkle));
        const lavender=(stage>1.5&&stage<4.4)&&rnd>.81;
        ctx.fillStyle=lavender?`rgba(173,160,217,${alpha*.85})`:`rgba(222,223,231,${alpha})`;
        const size=rnd>.97?1.6:1.05;
        ctx.fillRect(xPos,yPos,size,size);
      }
    }
  }
  function animate(time){
    stage+=(targetStage-stage)*.035;mouseX+=(targetMouseX-mouseX)*.055;mouseY+=(targetMouseY-mouseY)*.055;
    draw(time);frame=requestAnimationFrame(animate);
  }
  addEventListener('resize',resize,{passive:true});
  addEventListener('scroll',stageAtScroll,{passive:true});
  addEventListener('pointermove',event=>{targetMouseX=event.clientX/Math.max(1,width)*2-1;targetMouseY=event.clientY/Math.max(1,height)*2-1},{passive:true});
  reducedMotion.addEventListener('change',()=>{cancelAnimationFrame(frame);resize();if(!reducedMotion.matches)frame=requestAnimationFrame(animate)});
  resize();
  if(!reducedMotion.matches)frame=requestAnimationFrame(animate);
  canvas.dataset.motion=reducedMotion.matches?'reduced':'active';
}

async function api(path){
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
  try{
    const response=await fetch(path,{signal:controller.signal,cache:'no-store'});
    if(!response.ok)throw Error(`HTTP ${response.status}`);
    return await response.json();
  }finally{clearTimeout(timer)}
}
function message(id,text){byId(id).textContent=text}
function node(tag,className,text){const el=document.createElement(tag);if(className)el.className=className;el.textContent=text;return el}
function displayName(id){return String(id||'').replace(/^(endpoint|service|config|source):/,'')}

function showHealth(data){
  const observations=Object.fromEntries((data.observations||[]).map(item=>[item.endpoint_id,item]));
  const preview=byId('preview-health'),feature=byId('feature-health');preview.replaceChildren();feature.replaceChildren();
  const names=['checkout','refunds','renewals'];
  for(const name of names){
    const status=observations[`endpoint:${name}`]?.status||'unknown';
    const label=status==='healthy'?'Healthy':status==='failing'?'Acceptance failed':'Not monitored';
    const row=node('div','', '');row.append(node('b','',name),node('span',status,label));preview.append(row);
    const card=node('div',status,'');card.append(node('b','',name),node('span','',label));feature.append(card);
  }
  message('preview-flow-count',`${(data.observations||[]).length} observed`);
  message('feature-observed-at','CURRENT SANDBOX');
}

function pathFromGraph(graph){
  const adjacency=new Map();for(const edge of graph.edges||[]){
    if(!adjacency.has(edge.from_id))adjacency.set(edge.from_id,[]);
    adjacency.get(edge.from_id).push(edge.to_id);
  }
  for(const start of ['endpoint:refunds','endpoint:checkout','endpoint:renewals']){
    const queue=[[start]];
    while(queue.length){
      const path=queue.shift(),last=path.at(-1);
      if(last.startsWith('config:'))return path;
      if(path.length>=5)continue;
      for(const next of adjacency.get(last)||[])if(!path.includes(next))queue.push([...path,next]);
    }
  }
  return null;
}
function showGraph(graph){
  const nodes=graph.nodes||[],edges=graph.edges||[],learned=edges.filter(edge=>edge.relationship_type==='READS_CONFIG');
  message('preview-graph-count',`${nodes.length} nodes · ${edges.length} claims`);
  message('preview-sidebar-state',`${learned.length} learned config edges`);
  message('preview-source',`${graph.source||'Graph unavailable'} · snapshot ${String(graph.manifest_hash||'').slice(0,12)}`);
  message('feature-node-count',String(nodes.length));message('feature-edge-count',String(edges.length));message('feature-learned-count',String(learned.length));
  const pathArea=byId('preview-path');pathArea.replaceChildren();
  const path=pathFromGraph(graph);
  if(path){path.forEach((id,index)=>{if(index)pathArea.append(node('span','path-arrow','→'));pathArea.append(node('span',id.startsWith('config:')?'path-node learned':'path-node',displayName(id)))});}
  else pathArea.append(node('p','', 'No verified configuration path yet. Open the workspace to inspect a gap.'));
  const edgeArea=byId('feature-edges');edgeArea.replaceChildren();
  if(learned.length){for(const [index,edge] of learned.slice(0,2).entries()){
    if(index)edgeArea.append(node('i','','·'));
    edgeArea.append(node('span','',displayName(edge.from_id)));
    edgeArea.append(node('i','','→'));
    edgeArea.append(node('span','learned',displayName(edge.to_id)));
  }}else edgeArea.append(node('p','', 'Configuration edges have not been learned in this sandbox snapshot.'));
}

function showSources(sources){
  const host=byId('feature-sources');host.replaceChildren();
  for(const source of sources){
    const row=node('div','source-row','');
    row.append(node('b','',displayName(source.source_id)),node('small','',`${source.estimated_bytes} bytes`),node('em',source.inspected?'done':'',source.inspected?'Inspected':'Available'));
    host.append(row);
  }
  if(!sources.length)host.append(node('p','', 'No public evidence sources are available.'));
}

function showResults(data){
  const rows=(data.rows||[]).filter(row=>['frozen','random','adaptive'].includes(row.method));
  const methods=[['frozen','#797c87','Frozen graph'],['random','#aba1cc','Random ingestion'],['adaptive','#e8e6ee','Gap-driven ingestion']];
  const chart=byId('feature-chart');chart.replaceChildren();
  if(!rows.length){chart.append(node('p','', 'Measured aggregates are unavailable.'));return}
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');svg.setAttribute('viewBox','0 0 720 220');
  const add=(tag,attrs,text)=>{const el=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const [key,value] of Object.entries(attrs))el.setAttribute(key,String(value));if(text!==undefined)el.textContent=text;svg.append(el)};
  const x=round=>55+round*104,y=accuracy=>178-accuracy*1.45;
  for(const value of [0,50,100]){add('line',{class:'grid',x1:55,x2:682,y1:y(value),y2:y(value)});add('text',{x:45,y:y(value)+4,'text-anchor':'end'},`${value}%`)}
  for(let round=0;round<=6;round++)add('text',{x:x(round),y:202,'text-anchor':'middle'},String(round));
  for(const [method,color] of methods){
    const points=rows.filter(row=>row.method===method).sort((a,b)=>a.round-b.round);
    add('polyline',{points:points.map(row=>`${x(row.round)},${y(row.accuracy*100)}`).join(' '),fill:'none',stroke:color,'stroke-width':method==='random'?3:2,'stroke-dasharray':method==='frozen'?'3 5':method==='random'?'7 4':''});
    for(const row of points)add('circle',{cx:x(row.round),cy:y(row.accuracy*100),r:method==='random'?4:3,fill:color,'data-method':method,'data-round':row.round,'data-correct':row.correct,'data-total':row.total});
  }
  chart.append(svg);
  const legend=byId('feature-legend');legend.replaceChildren();for(const [,color,label] of methods){const item=node('span','','');const swatch=node('i','','');swatch.style.background=color;item.append(swatch,document.createTextNode(label));legend.append(item)}
  const final=rows.find(row=>row.method==='adaptive'&&row.round===6);
  message('feature-protocol',`PROTOCOL ${String(data.protocol||'').toUpperCase()} / ${data.seeds?.length||0} SEEDS`);
  message('feature-result-note',final?`Final gap-driven result: ${final.correct}/${final.total} correct. Random ingestion reaches the same final count after both sources are acquired.`:'All plotted values are from the recorded held-out evaluation.');
}

async function loadLivePreview(){
  const targets=[['/api/observations',showHealth,['preview-health','feature-health']],['/api/graph',showGraph,['preview-path','feature-edges']],['/api/sources',showSources,['feature-sources']],['/api/results',showResults,['feature-chart']]];
  await Promise.all(targets.map(async([path,render,ids])=>{
    try{render(await api(path))}catch(error){for(const id of ids)message(id,`Live data unavailable: ${error.message}`)}
  }));
  document.documentElement.dataset.previewLoaded='true';
}

revealSections();particleWave();loadLivePreview();
