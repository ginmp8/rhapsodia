/* Local Graph Explorer. No network calls except the explicit same-origin query
 * action when a local Engine server supplied an in-memory session capability. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const NS = 'http://www.w3.org/2000/svg';
  const palette = ['#2462aa','#198277','#966223','#8056aa','#b24963','#557b2b','#466c80','#936846'];
  const sort = values => [...values].sort((a,b) => a < b ? -1 : a > b ? 1 : 0);
  const text = value => value === null ? 'null' : typeof value === 'object' ? JSON.stringify(value,null,2) : String(value);
  const element = (tag, content, cls) => { const e=document.createElement(tag);if(content!==undefined)e.textContent=content;if(cls)e.className=cls;return e; };
  const svgElement = (tag,attrs={}) => {const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));return e;};
  const message = value => { $('message').textContent=value; };
  let graph, byId, selected=null, focus=null, highlighted=new Set(), page=0, currentView='graph', g6=null, renderRevision=0;
  let positions=new Map(), graphSelection=null, viewport={x:0,y:0,k:1}, drag=null;
  // Presentation only: never put these coordinates into graph nodes/properties.
  let manualPositions=new Map(), graphLayoutKey=null, suppressedClick=null;
  const nodeElements=new Map(), incidentEdges=new Map();
  const DRAG_THRESHOLD=4, MAX_POSITION=1000000;
  const validPosition=p=>p!==null && typeof p==='object' && !Array.isArray(p) &&
    ['x','y'].every(key=>Number.isFinite(p[key]) && Math.abs(p[key])<=MAX_POSITION);
  let kinds=new Set(), relations=new Set(), statuses=new Set(['accepted','ambiguous','stale','rejected','unknown']);
  const allStatuses=['accepted','ambiguous','stale','rejected','unknown'];
  let currentVisible={nodes:[],edges:[]},journey=null;
  function validate(data){
    if(!data||data.schema_version!=='graph-view-v1'||!Array.isArray(data.nodes)||!Array.isArray(data.edges))throw Error('Expected graph-view-v1 with node and edge arrays.');
    if(data.nodes.length>10000||data.edges.length>50000)throw Error('View exceeds the 10,000 node / 50,000 edge loading budget. Export a focused view.');
    const inspect=(value,depth=0)=>{if(depth>64)throw Error('Data nesting exceeds 64 levels.');if(typeof value==='number'&&!Number.isFinite(value))throw Error('Non-finite number.');if(value&&typeof value==='object')for(const child of Object.values(value))inspect(child,depth+1);};inspect(data);
    const ids=new Set(),edges=new Set();
    const object=value=>value!==null&&typeof value==='object'&&!Array.isArray(value);
    const optionalFields=record=>{
      for(const key of ['properties','metrics','evidence_summary'])if(record[key]!=null&&!object(record[key]))throw Error('Invalid '+key+' object.');
      for(const key of ['evidence','claims'])if(record[key]!=null&&!Array.isArray(record[key]))throw Error('Invalid '+key+' array.');
      if(record.evidence!=null&&record.evidence.some(ev=>!object(ev)))throw Error('Evidence must contain objects.');
    };
    for(const n of data.nodes){
      if(!n||!['id','kind','label'].every(k=>typeof n[k]==='string'&&n[k].trim())||ids.has(n.id))throw Error('Invalid or duplicate node.');
      ids.add(n.id);optionalFields(n);
      if(n.aliases!==undefined&&(!Array.isArray(n.aliases)||n.aliases.some(x=>typeof x!=='string'||!x.trim())))throw Error('Invalid aliases.');
    }
    for(const e of data.edges){
      if(!e||!['id','source','target','relation'].every(k=>typeof e[k]==='string'&&e[k].trim())||edges.has(e.id)||!ids.has(e.source)||!ids.has(e.target))throw Error('Invalid edge, duplicate ID, or missing endpoint.');
      if(e.directed!==undefined&&typeof e.directed!=='boolean')throw Error('Invalid edge direction.');edges.add(e.id);optionalFields(e);
    }
    for(const key of ['graph','metadata','query'])if(data[key]!=null&&!object(data[key]))throw Error('Invalid '+key+' object.');
    if(data.communities!=null&&!Array.isArray(data.communities))throw Error('Invalid communities array.');
    return data;
  }
  function identity(){
    const material=JSON.stringify([graph.nodes,graph.edges]);let hash=2166136261;
    for(let i=0;i<material.length;i++)hash=Math.imul(hash^material.charCodeAt(i),16777619);
    return (graph.metadata?.source_graph_sha256 || VIEWER_CONFIG.source_sha256 || 'local')+':'+(hash>>>0).toString(16);
  }
  function color(kind){const keys=sort(new Set(graph.nodes.map(n=>n.kind)));return palette[keys.indexOf(kind)%palette.length];}
  function evidenceMatches(record){
    const ev=Array.isArray(record.evidence)?record.evidence:[];
    const min=Math.max(0,Math.min(1,Number($('confidence').value)||0));
    if(ev.length)return ev.some(e=>statuses.has(e.status||'unknown')&&(typeof e.confidence==='number'?e.confidence:0)>=min);
    const summary=record.evidence_summary||{};
    const keys=Object.keys(summary.statuses||{});
    const confidence=summary.max_confidence??summary.confidence??0;
    return (keys.length?keys.some(k=>statuses.has(k)):statuses.has('unknown'))&&confidence>=min;
  }
  function adjacent(edges,direction='both'){
    const map=new Map();const add=(a,b,id)=>{if(!map.has(a))map.set(a,[]);map.get(a).push([b,id]);};
    for(const e of edges){if(direction!=='incoming'||e.directed===false)add(e.source,e.target,e.id);if(direction!=='outgoing'||e.directed===false)add(e.target,e.source,e.id);}
    for(const a of map.values())a.sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:a[1]<b[1]?-1:1);
    return map;
  }
  function visible(){
    const search=$('search').value.toLowerCase(),source=$('source-filter').value.toLowerCase(),property=$('property-key').value,value=$('property-value').value.toLowerCase();
    let nodes=graph.nodes.filter(n=>kinds.has(n.kind)&&evidenceMatches(n));
    nodes=nodes.filter(n=>(!search||[n.label,n.id,...(n.aliases||[]),JSON.stringify(n.properties||{})].join(' ').toLowerCase().includes(search))&&(!source||(n.evidence||[]).some(e=>String(e.source_uri||'').toLowerCase().includes(source)))&&(!property||(Object.prototype.hasOwnProperty.call(n.properties||{},property)&&(!value||text(n.properties[property]).toLowerCase().includes(value)))));
    let ids=new Set(nodes.map(n=>n.id));let edges=graph.edges.filter(e=>ids.has(e.source)&&ids.has(e.target)&&relations.has(e.relation)&&evidenceMatches(e));
    if(focus){
      const adj=adjacent(edges,$('direction').value),depth=Math.max(0,Math.min(10,Number($('depth').value)||0)),seen=new Set([focus]),queue=[[focus,0]];
      for(let i=0;i<queue.length;i++){const [node,d]=queue[i];if(d>=depth)continue;for(const [n] of adj.get(node)||[])if(!seen.has(n)){seen.add(n);queue.push([n,d+1]);}}
      nodes=nodes.filter(n=>seen.has(n.id));ids=new Set(nodes.map(n=>n.id));edges=edges.filter(e=>ids.has(e.source)&&ids.has(e.target));
    }
    return {nodes:nodes.slice().sort((a,b)=>a.id<b.id?-1:1),edges:edges.slice().sort((a,b)=>a.id<b.id?-1:1)};
  }
  function checkList(id,values,set,onChange){
    const list=$(id);list.replaceChildren();
    for(const [value,count] of [...values.entries()].sort((a,b)=>a[0]<b[0]?-1:1)){
      const row=element('label',undefined,'check-row'),box=element('input');box.type='checkbox';box.checked=set.has(value);box.dataset.value=value;
      box.addEventListener('change',()=>{box.checked?set.add(value):set.delete(value);onChange();});row.append(box);
      if(id==='kind-filters'){const dot=element('span',undefined,'swatch');dot.style.background=color(value);row.append(dot);}
      row.append(element('span',value),element('span',String(count),'count'));list.append(row);
    }
  }
  function counts(values){const map=new Map();for(const v of values)map.set(v,(map.get(v)||0)+1);return map;}
  function controls(){
    checkList('kind-filters',counts(graph.nodes.map(n=>n.kind)),kinds,refresh);
    checkList('relation-filters',counts(graph.edges.map(e=>e.relation)),relations,refresh);
    const sc=new Map(allStatuses.map(x=>[x,graph.nodes.filter(n=>(n.evidence||[]).some(e=>e.status===x)).length]));checkList('status-filters',sc,statuses,refresh);
    for(const id of ['path-from','path-to']){const s=$(id);s.replaceChildren(new Option('Choose entity',''));for(const n of graph.nodes.slice().sort((a,b)=>a.label<b.label?-1:1)){s.add(new Option(n.label+' ['+n.kind+']',n.id));}}
    const keys=sort(new Set(graph.nodes.flatMap(n=>Object.keys(n.properties||{}))));
    $('time-property').replaceChildren();for(const key of keys)$('time-property').add(new Option(key,key));
    if(keys.includes('timestamp'))$('time-property').value='timestamp';
    $('numeric-property').replaceChildren(new Option('Entity count',''));
    for(const key of keys)if(graph.nodes.some(n=>typeof n.properties?.[key]==='number'))$('numeric-property').add(new Option(key,key));
  }
  function load(data){
    validate(data);journey?.reset();finishDrag(null,true);destroyG6();
    graph=data;byId=new Map(data.nodes.map(n=>[n.id,n]));selected=null;focus=null;highlighted.clear();page=0;positions.clear();
    manualPositions.clear();graphLayoutKey=null;suppressedClick=null;
    kinds=new Set(data.nodes.map(n=>n.kind));relations=new Set(data.edges.map(e=>e.relation));statuses=new Set(allStatuses);
    for(const id of ['search','source-filter','property-key','property-value'])$(id).value='';$('confidence').value='0';
    controls();$('dataset-label').textContent=graph.graph?.label||'Data-led exploration / '+data.nodes.length.toLocaleString('en-US')+' loaded entities';
    const scoped=graph.metadata?.truncated||graph.metadata?.complete_database===false||graph.query?.seed;
    $('projection-label').textContent=scoped?'Scoped projection: not the entire database':'Snapshot: coverage is defined by the producer';
    $('identity').textContent='snapshot '+String(identity()||'unidentified').slice(0,12);refresh();
  }
  function switchView(view){
    if(!['graph','table','timeline','matrix','summary'].includes(view))return;
    journey?.viewChanged(view);currentView=view;for(const tab of document.querySelectorAll('.tab')){const active=tab.dataset.view===view;tab.classList.toggle('active',active);tab.setAttribute('aria-pressed',String(active));}
    for(const pane of document.querySelectorAll('.view'))pane.classList.toggle('active',pane.id===view+'-view');refresh(false);
  }
  function refresh(resetPage=true){
    if(resetPage)page=0;currentVisible=visible();const {nodes,edges}=currentVisible;
    $('counts').textContent=nodes.length.toLocaleString('en-US')+' / '+graph.nodes.length.toLocaleString('en-US')+' entities · '+edges.length.toLocaleString('en-US')+' / '+graph.edges.length.toLocaleString('en-US')+' relationships';
    $('selection-status').textContent=selected?(byId.get(selected)?.label||selected)+(focus?' · focused':''):'Nothing selected';
    if(currentView==='graph')drawGraph();else if(currentView==='table')drawTable();else if(currentView==='timeline')drawTimeline();else if(currentView==='matrix')drawMatrix();else drawSummary();
    inspect();
  }
  function isDAG(nodes,edges){
    if(edges.some(e=>e.directed===false))return false;
    const degree=new Map(nodes.map(n=>[n.id,0])),out=adjacent(edges,'outgoing');for(const e of edges)degree.set(e.target,degree.get(e.target)+1);
    const q=sort([...degree].filter(x=>x[1]===0).map(x=>x[0]));let count=0;
    while(q.length){const id=q.shift();count++;for(const [next] of out.get(id)||[]){degree.set(next,degree.get(next)-1);if(degree.get(next)===0){q.push(next);q.sort();}}}
    return count===nodes.length;
  }
  function layoutName(nodes,edges){
    const choice=$('layout').value;
    if(choice!=='auto')return choice;
    const hint=graph.metadata?.layout_hint;if(['dagre','radial','circular','grid','community','force'].includes(hint))return hint;
    if(focus||graph.query?.seed)return 'radial';return isDAG(nodes,edges)?'dagre':'circular';
  }
  function layoutPositions(nodes,edges,layout){
    const result=new Map(),n=nodes.length;
    if(!n)return result;
    if(layout==='grid'){
      const cols=Math.ceil(Math.sqrt(n));nodes.forEach((node,i)=>result.set(node.id,{x:(i%cols)*185,y:Math.floor(i/cols)*95}));
    } else if(layout==='dagre'){
      const levels=new Map(nodes.map(n=>[n.id,0])),degree=new Map(nodes.map(n=>[n.id,0])),out=adjacent(edges,'outgoing');for(const e of edges)degree.set(e.target,degree.get(e.target)+1);
      const ready=sort(nodes.filter(n=>degree.get(n.id)===0).map(n=>n.id));let processed=0;
      while(ready.length){const id=ready.shift();processed++;for(const [next] of out.get(id)||[]){levels.set(next,Math.max(levels.get(next),levels.get(id)+1));degree.set(next,degree.get(next)-1);if(degree.get(next)===0){ready.push(next);ready.sort();}}}
      if(processed!==n){message('Layered layout requires a DAG. Cyclic nodes use the stable grid layout.');return layoutPositions(nodes,edges,'grid');}
      const groups=new Map();for(const node of nodes){const l=levels.get(node.id);if(!groups.has(l))groups.set(l,[]);groups.get(l).push(node.id);}
      for(const [l,ids] of groups)ids.forEach((id,i)=>result.set(id,{x:l*190,y:(i-(ids.length-1)/2)*100}));
    } else if(layout==='radial'){
      const seed=nodes.some(n=>n.id===(focus||graph.query?.seed))?(focus||graph.query.seed):nodes[0].id,adj=adjacent(edges),distance=new Map([[seed,0]]),q=[seed];
      for(let i=0;i<q.length;i++)for(const [id] of adj.get(q[i])||[])if(!distance.has(id)){distance.set(id,distance.get(q[i])+1);q.push(id);}
      const outer=Math.max(...distance.values())+1,groups=new Map();for(const node of nodes){const d=distance.get(node.id)??outer;if(!groups.has(d))groups.set(d,[]);groups.get(d).push(node.id);}
      for(const [d,ids] of groups)ids.forEach((id,i)=>{const angle=2*Math.PI*i/ids.length;const radius=d?Math.max(d*200,ids.length*31):0;result.set(id,{x:radius*Math.cos(angle),y:radius*Math.sin(angle)});});
    } else if(layout==='community'){
      const groups=new Map();for(const node of nodes){const key=node.community||node.kind;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(node);}
      let offset=0;for(const key of sort(groups.keys())){const members=groups.get(key),cols=Math.ceil(Math.sqrt(members.length));members.forEach((node,i)=>result.set(node.id,{x:offset+(i%cols)*175,y:Math.floor(i/cols)*90}));offset+=cols*175+150;}
    } else {
      const radius=Math.max(160,n*29);nodes.forEach((node,i)=>result.set(node.id,{x:radius*Math.cos(i*2*Math.PI/n),y:radius*Math.sin(i*2*Math.PI/n)}));
      if(layout==='force'){
        if(n>200){message('Force layout is capped at 200 entities. Showing stable circular positions instead.');return result;}
        // Fixed initial positions, ordering and iteration count. No random/time-dependent loop.
        for(let step=0;step<90;step++){
          const delta=new Map(nodes.map(n=>[n.id,{x:0,y:0}]));
          for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){
            const a=result.get(nodes[i].id),b=result.get(nodes[j].id),dx=a.x-b.x,dy=a.y-b.y,d2=Math.max(100,dx*dx+dy*dy),f=3200/d2;
            delta.get(nodes[i].id).x+=dx*f;delta.get(nodes[i].id).y+=dy*f;delta.get(nodes[j].id).x-=dx*f;delta.get(nodes[j].id).y-=dy*f;
          }
          for(const e of edges){if(e.source===e.target)continue;const a=result.get(e.source),b=result.get(e.target),dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)||1,f=(d-210)*.007;delta.get(e.source).x+=dx/d*f;delta.get(e.source).y+=dy/d*f;delta.get(e.target).x-=dx/d*f;delta.get(e.target).y-=dy/d*f;}
          const cooling=(1-step/90)*.6;for(const node of nodes){const p=result.get(node.id),d=delta.get(node.id);p.x+=Math.max(-12,Math.min(12,d.x))*cooling;p.y+=Math.max(-12,Math.min(12,d.y))*cooling;}
        }
      }
    }
    for(const p of result.values()){p.x=Math.round(p.x*100)/100;p.y=Math.round(p.y*100)/100;}return result;
  }
  function getStyle(key){return getComputedStyle(document.documentElement).getPropertyValue(key).trim();}
  function destroyG6(){if(g6){try{g6.destroy();}catch{}g6=null;}$('g6-canvas').replaceChildren();$('g6-canvas').hidden=true;}
  function drawGraph(){
    finishDrag(null,true);syncG6Positions();
    const revision=++renderRevision;destroyG6();
    const all=currentVisible,nodes=all.nodes.slice(0,500),ids=new Set(nodes.map(n=>n.id)),edges=all.edges.filter(e=>ids.has(e.source)&&ids.has(e.target)).slice(0,4000);
    $('graph-limit').textContent=nodes.length<all.nodes.length||edges.length<all.edges.length?'Canvas budget: '+nodes.length+' entities and '+edges.length+' relationships shown. Filter/focus to narrow the canvas; other views retain the loaded selection.':'';
    const name=layoutName(nodes,edges),key=JSON.stringify([name,nodes.map(n=>n.id),edges.map(e=>e.id)]);
    const needsFit=graphLayoutKey!==key;graphLayoutKey=key;
    positions=layoutPositions(nodes,edges,name);
    for(const node of nodes)if(manualPositions.has(node.id))positions.set(node.id,{...manualPositions.get(node.id)});
    graphSelection={nodes,edges};drawSVG(nodes,edges);updateLayoutLabel();
    if(needsFit)fit();else updateTransform();
    journey?.setScope(nodes,edges);
    if(VIEWER_CONFIG.backend!=='builtin'&&window.G6?.Graph&&!journey?.isActive()){
      $('g6-canvas').hidden=false;
      try{
        g6=new window.G6.Graph({container:$('g6-canvas'),data:{nodes:nodes.map(n=>({id:n.id,data:{label:n.label},style:{...positions.get(n.id),labelText:n.label,size:24,fill:color(n.kind)}})),edges:edges.map(e=>({id:e.id,source:e.source,target:e.target,style:{endArrow:e.directed!==false,stroke:getStyle('--edge')}}))},node:{type:'circle'},edge:{type:'line'},behaviors:['drag-canvas','zoom-canvas','click-select',{type:'drag-element',trigger:[],animation:false,dropEffect:'none',hideEdge:'none'}],animation:false,autoFit:'view'});
        g6.on('node:click',event=>{const id=event.target?.id||event.item?.id;if(byId.has(id)){selected=id;inspect();$('selection-status').textContent=byId.get(id).label;}});
        g6.on('node:dragend',()=>{requestAnimationFrame(()=>{if(revision===renderRevision)syncG6Positions();});});
        Promise.resolve(g6.render()).catch(error=>{if(revision===renderRevision){destroyG6();message('Optional G6 did not render; the offline SVG view remains available. '+String(error.message||error));}});
      }catch(error){destroyG6();message('Optional G6 failed; using the offline SVG renderer. '+String(error.message||error));}
    }
  }
  function drawSVG(nodes,edges){
    const svg=$('graph-svg');svg.replaceChildren();nodeElements.clear();incidentEdges.clear();
    const defs=svgElement('defs');
    for(const [name,c] of [['normal',getStyle('--edge')],['path',getStyle('--accent')],['incoming',getStyle('--in')],['outgoing',getStyle('--out')]]){
      const marker=svgElement('marker',{id:'arrow-'+name,viewBox:'0 0 10 10',refX:9,refY:5,markerWidth:6,markerHeight:6,orient:'auto-start-reverse'});marker.append(svgElement('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:c}));defs.append(marker);
    }
    svg.append(defs);const world=svgElement('g',{id:'graph-world'});svg.append(world);
    const pairCounts=new Map(),pairSeen=new Map();for(const e of edges){const key=JSON.stringify(sort([e.source,e.target]));pairCounts.set(key,(pairCounts.get(key)||0)+1);}
    for(const e of edges){
      const key=JSON.stringify(sort([e.source,e.target])),index=pairSeen.get(key)||0;pairSeen.set(key,index+1);
      const count=pairCounts.get(key),d=edgePath(e,index,count);
      const path=highlighted.has(e.id),direction=e.target===selected?'incoming':e.source===selected?'outgoing':'normal',style=path?'path':direction;
      const line=svgElement('path',{d,fill:'none',stroke:getStyle(style==='path'?'--accent':style==='normal'?'--edge':style==='incoming'?'--in':'--out'),'stroke-width':path?3:direction!=='normal'?2:1.2,opacity:highlighted.size && !path ? .18 : 1,'stroke-dasharray':(e.evidence||[]).some(v=>v.provenance==='INFERRED')?'5 4':'none'});
      if(e.directed!==false)line.setAttribute('marker-end','url(#arrow-'+style+')');const title=svgElement('title');title.textContent=(byId.get(e.source)?.label||e.source)+' '+e.relation+' '+(byId.get(e.target)?.label||e.target);line.append(title);world.append(line);
      const hit=svgElement('path',{d,fill:'none',stroke:'transparent','stroke-width':12,class:'edge-hit'});hit.addEventListener('click',()=>inspectEdge(e));world.append(hit);
      const record={edge:e,index,count,line,hit};
      for(const id of new Set([e.source,e.target])){if(!incidentEdges.has(id))incidentEdges.set(id,[]);incidentEdges.get(id).push(record);}
    }
    const pathNodes=new Set(edges.filter(e=>highlighted.has(e.id)).flatMap(e=>[e.source,e.target]));
    for(const n of nodes){
      const p=positions.get(n.id),group=svgElement('g',{transform:`translate(${p.x},${p.y})`,class:'node',tabindex:0,role:'button','aria-label':n.label+', '+n.kind,'aria-describedby':'graph-help','data-node':n.id,opacity:highlighted.size && !pathNodes.has(n.id) ? .25 : 1});
      group.append(svgElement('rect',{x:-77,y:-24,width:154,height:48,rx:5,fill:getStyle('--panel'),stroke:n.id===selected?getStyle('--accent'):getStyle('--line'),'stroke-width':n.id===selected?2:1}));
      group.append(svgElement('rect',{x:-77,y:-24,width:4,height:48,rx:1,fill:color(n.kind)}));
      const name=svgElement('text',{x:-64,y:-2,fill:getStyle('--ink'),'font-family':'system-ui,sans-serif','font-size':13,'font-weight':600});name.textContent=n.label.length>19?n.label.slice(0,18)+'…':n.label;group.append(name);
      const kind=svgElement('text',{x:-64,y:14,fill:getStyle('--muted'),'font-family':'system-ui,sans-serif','font-size':9});kind.textContent=n.kind.length>25?n.kind.slice(0,24)+'…':n.kind;group.append(kind);
      group.addEventListener('click',event=>{
        event.stopPropagation();
        if(suppressedClick===n.id && event.detail!==0){suppressedClick=null;return;}
        selected=n.id;refresh(false);nodeElements.get(n.id)?.focus({preventScroll:true});
      });
      group.addEventListener('keydown',event=>{
        if(event.key==='Enter'||event.key===' '){event.preventDefault();selected=n.id;inspect();$('selection-status').textContent=n.label;return;}
        const delta={ArrowLeft:[-1,0],ArrowRight:[1,0],ArrowUp:[0,-1],ArrowDown:[0,1]}[event.key];
        if(delta && !event.ctrlKey && !event.metaKey && !event.altKey && !drag){
          event.preventDefault();const step=event.shiftKey?50:10,p=positions.get(n.id);
          moveNode(n.id,{x:p.x+delta[0]*step,y:p.y+delta[1]*step});
          $('move-status').textContent=n.label+' moved to '+positions.get(n.id).x+', '+positions.get(n.id).y+'.';
        }
      });
      nodeElements.set(n.id,group);
      const title=svgElement('title');title.textContent=n.label+'\n'+n.id;group.append(title);world.append(group);
    }
    if(!nodes.length){const label=svgElement('text',{x:30,y:90,fill:getStyle('--muted'),'font-size':14});label.textContent='No entities match the current filters.';svg.append(label);}
  }
  function edgePath(edge,index,count){
    const a=positions.get(edge.source),b=positions.get(edge.target);
    if(edge.source===edge.target)return `M ${a.x+50} ${a.y-12} C ${a.x+155} ${a.y-115},${a.x-30} ${a.y-115},${a.x-15} ${a.y-24}`;
    const dx=b.x-a.x,dy=b.y-a.y,length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length;
    const off=(index-(count-1)/2)*36,trim=Math.min(82,length*.22);
    return `M ${a.x+ux*trim} ${a.y+uy*trim*.45} Q ${(a.x+b.x)/2-uy*off} ${(a.y+b.y)/2+ux*off} ${b.x-ux*trim} ${b.y-uy*trim*.45}`;
  }
  function updateLayoutLabel(){
    if(!graphSelection)return;
    const name=layoutName(graphSelection.nodes,graphSelection.edges);
    const count=graphSelection.nodes.filter(n=>manualPositions.has(n.id)).length;
    $('layout-label').textContent=(name==='dagre'?'Layered (built-in)':name[0].toUpperCase()+name.slice(1))+
      (count?' \u00b7 '+count+' manually positioned':' \u00b7 stable positions');
  }
  function updateNodeGeometry(id){
    const p=positions.get(id);nodeElements.get(id)?.setAttribute('transform',`translate(${p.x},${p.y})`);
    for(const r of incidentEdges.get(id)||[]){const d=edgePath(r.edge,r.index,r.count);r.line.setAttribute('d',d);r.hit.setAttribute('d',d);}
  }
  function moveNode(id,point){
    if(!positions.has(id)||!Number.isFinite(point.x)||!Number.isFinite(point.y))return;
    const normalize=v=>Math.round(Math.max(-MAX_POSITION,Math.min(MAX_POSITION,v))*100)/100;
    const p={x:normalize(point.x),y:normalize(point.y)};
    positions.set(id,p);manualPositions.set(id,{...p});updateNodeGeometry(id);updateLayoutLabel();
      journey?.positionsChanged();
  }
  function syncG6Positions(){
    if(!g6?.getNodeData)return;
    // G6 owns its canvas, but exported SVG/state must mirror user node movement.
    try{for(const node of g6.getNodeData()){
      const p=node.style,old=positions.get(node.id);
      if(old&&validPosition(p)&&(Math.abs(p.x-old.x)>.005||Math.abs(p.y-old.y)>.005))moveNode(node.id,p);
    }}catch(error){message('Could not synchronize optional G6 positions: '+String(error.message||error));}
  }
  function screenPoint(event,inverse){
    const p=$('graph-svg').createSVGPoint();p.x=event.clientX;p.y=event.clientY;return p.matrixTransform(inverse);
  }
  function startDrag(event){
    if(event.button===0)journey?.manualGesture();
    if(drag||event.button!==0||event.isPrimary===false)return;
    const node=event.target.closest('.node'),svg=$('graph-svg');
    if(!node&&event.target.closest('.edge-hit'))return;
    const matrix=(node?$('graph-world'):svg)?.getScreenCTM();if(!matrix)return;
    let inverse;try{inverse=matrix.inverse();}catch{return;}
    const start=screenPoint(event,inverse);if(!Number.isFinite(start.x)||!Number.isFinite(start.y))return;
    suppressedClick=null;
    drag={kind:node?'node':'canvas',id:node?.dataset.node,pointerId:event.pointerId,
      target:node||svg,clientX:event.clientX,clientY:event.clientY,inverse,start,moved:false,v:{...viewport}};
    if(node){drag.original={...positions.get(drag.id)};drag.previous=manualPositions.get(drag.id);node.focus({preventScroll:true});}
    try{drag.target.setPointerCapture(event.pointerId);}catch{drag=null;return;}
    event.preventDefault();
  }
  function moveDrag(event){
    if(!drag||event.pointerId!==drag.pointerId)return;
    if(!drag.moved&&Math.hypot(event.clientX-drag.clientX,event.clientY-drag.clientY)<DRAG_THRESHOLD)return;
    drag.moved=true;$('graph-svg').classList.add('is-dragging');event.preventDefault();
    const p=screenPoint(event,drag.inverse);
    if(drag.kind==='node')moveNode(drag.id,{x:drag.original.x+p.x-drag.start.x,y:drag.original.y+p.y-drag.start.y});
    else {viewport.x=drag.v.x+p.x-drag.start.x;viewport.y=drag.v.y+p.y-drag.start.y;updateTransform();}
  }
  function finishDrag(event,cancel=false){
    if(!drag||(event&&event.pointerId!==drag.pointerId))return;
    const active=drag;drag=null;$('graph-svg').classList.remove('is-dragging');
    if(active.kind==='node'&&active.moved){
      suppressedClick=active.id;
      if(cancel){positions.set(active.id,active.original);if(active.previous)manualPositions.set(active.id,active.previous);else manualPositions.delete(active.id);updateNodeGeometry(active.id);updateLayoutLabel();}
      $('move-status').textContent=cancel?'Node move cancelled.':byId.get(active.id).label+' repositioned. Save View state to keep manual positions.';
    }else if(cancel&&active.kind==='canvas'){viewport=active.v;updateTransform();}
    if(active.target.hasPointerCapture(active.pointerId))active.target.releasePointerCapture(active.pointerId);
  }
  function updateTransform(){const world=$('graph-world');if(world)world.setAttribute('transform',`translate(${viewport.x},${viewport.y}) scale(${viewport.k})`);journey?.cameraChanged();}
  function fit(){
    if(!positions.size)return;const rect=$('graph-svg').getBoundingClientRect(),xs=[...positions.values()].map(p=>p.x),ys=[...positions.values()].map(p=>p.y),minx=Math.min(...xs)-100,maxx=Math.max(...xs)+100,miny=Math.min(...ys)-100,maxy=Math.max(...ys)+100;
    viewport.k=Math.min(1.25,Math.max(.04,Math.min((rect.width-70)/(maxx-minx),(rect.height-80)/(maxy-miny))));viewport.x=rect.width/2-(minx+maxx)/2*viewport.k;viewport.y=rect.height/2-(miny+maxy)/2*viewport.k;updateTransform();
    if(g6?.fitView)try{g6.fitView();}catch{}
  }
  function zoom(factor,x,y){if(drag)return;const rect=$('graph-svg').getBoundingClientRect();x??=rect.width/2;y??=rect.height/2;const next=Math.max(.025,Math.min(6,viewport.k*factor)),ratio=next/viewport.k;viewport.x=x-(x-viewport.x)*ratio;viewport.y=y-(y-viewport.y)*ratio;viewport.k=next;updateTransform();}
  function inspect(){
    const box=$('inspector-content');box.replaceChildren();const node=byId?.get(selected);
    if(!node){const empty=element('div',undefined,'empty');empty.append(element('strong','Select an entity'),element('p','Inspect its properties, sources and relationships. View changes never modify the graph database.'));box.append(empty);return;}
    box.append(element('span',node.kind,'inspector-kind'),element('h3',node.label,'inspector-title'),element('p',node.id,'small-code'));
    const props=element('section',undefined,'inspector-section');props.append(element('h3','Properties'));const dl=element('dl');
    for(const key of sort(Object.keys(node.properties||{}))){const entry=element('div',undefined,'property');entry.append(element('dt',key),element('dd',text(node.properties[key])));dl.append(entry);}props.append(dl);if(!dl.children.length)props.append(element('p','No recorded properties.','hint'));box.append(props);
    const r=element('section',undefined,'inspector-section');r.append(element('h3','Loaded relationships'));
    for(const edge of graph.edges.filter(e=>e.source===node.id||e.target===node.id).slice(0,150)){
      const incoming=edge.target===node.id,other=byId.get(incoming?edge.source:edge.target),row=element('div',undefined,'relation-row');row.append(element('span',(edge.directed===false?'Undirected':incoming?'Incoming':'Outgoing')+' / '+edge.relation));const button=element('button',other?.label||'Unknown endpoint');button.addEventListener('click',()=>{selected=other.id;refresh(false);});row.append(button);r.append(row);
    }
    if(graph.edges.filter(e=>e.source===node.id||e.target===node.id).length>150)r.append(element('p','Inspector shows the first 150 loaded relationships. Use focused queries for the remainder.','hint'));box.append(r);appendEvidence(box,node);
  }
  function appendEvidence(box,record){
    const section=element('section',undefined,'inspector-section');section.append(element('h3','Evidence and origin'));
    if((record.claims||[]).length>1){const claims=element('details');claims.append(element('summary','Compare source assertions ('+record.claims.length+')'));for(const claim of record.claims){claims.append(element('p',claim.source_uri,'hint'),element('pre',text({label:claim.assertion?.label,kind:claim.assertion?.kind,properties:claim.assertion?.properties}),'small-code'));}section.append(claims);}
    for(const e of record.evidence||[]){const item=element('div',undefined,'evidence');item.append(element('span',(e.provenance||'unknown')+' / '+(e.status||'unknown')+' / '+(e.confidence??'unscored'),'badge'),element('p',e.source_uri||e.source_id||'Source not included','source'),element('p',e.locator||'No locator'));if(e.details&&Object.keys(e.details).length)item.append(element('pre',text(e.details)));section.append(item);}
    if(!(record.evidence||[]).length){section.append(element('p','This projection contains an evidence summary only. Query the Engine for source-level details.','hint'));if(record.evidence_summary)section.append(element('pre',text(record.evidence_summary),'small-code'));}
    if(record.evidence_truncated)section.append(element('p','Evidence list is bounded; request source details from the Engine.','hint'));box.append(section);
  }
  function inspectEdge(edge){
    const box=$('inspector-content');box.replaceChildren(element('span','Relationship','inspector-kind'),element('h3',edge.relation,'inspector-title'),element('p',(byId.get(edge.source)?.label||edge.source)+(edge.directed===false?' — ':' → ')+(byId.get(edge.target)?.label||edge.target)));
    const pre=element('pre',text(edge.properties||{}),'small-code');box.append(pre);appendEvidence(box,edge);
  }
  function selectButton(node){const b=element('button',node.label,'link');b.addEventListener('click',()=>{selected=node.id;inspect();$('selection-status').textContent=node.label;});return b;}
  function drawTable(){
    const box=$('table-content');box.replaceChildren();let rows=currentVisible.nodes.slice();const degree=counts(currentVisible.edges.flatMap(e=>[e.source,e.target]));
    const key=$('table-sort').value;rows.sort((a,b)=>key==='degree'?(degree.get(b.id)||0)-(degree.get(a.id)||0)||a.id.localeCompare(b.id):text(a[key]).localeCompare(text(b[key]))||a.id.localeCompare(b.id));
    const pages=Math.max(1,Math.ceil(rows.length/100));page=Math.min(page,pages-1);const table=element('table'),head=element('thead'),tr=element('tr');for(const x of ['Entity','Kind','Connections','Identifier'])tr.append(element('th',x));head.append(tr);table.append(head);const body=element('tbody');
    for(const n of rows.slice(page*100,(page+1)*100)){const row=element('tr'),name=element('td');name.append(selectButton(n));row.append(name,element('td',n.kind),element('td',String(degree.get(n.id)||0)),element('td',n.id,'small-code'));body.append(row);}table.append(body);box.append(table);
    if(!rows.length)box.append(element('p','No matching entities.','empty'));$('page-label').textContent=`Page ${page+1} of ${pages} / ${rows.length} entities`;$('page-prev').disabled=page===0;$('page-next').disabled=page>=pages-1;
  }
  function validTime(v){return typeof v==='string'&&/^\d{4}-\d{2}-\d{2}T.*(?:Z|[+-]\d{2}:\d{2})$/.test(v)&&Number.isFinite(Date.parse(v));}
  function drawTimeline(){
    const box=$('timeline-content');box.replaceChildren();const property=$('time-property').value;
    const rows=currentVisible.nodes.filter(n=>validTime(n.properties?.[property])).sort((a,b)=>Date.parse(a.properties[property])-Date.parse(b.properties[property])||a.id.localeCompare(b.id));
    box.append(element('p',`${rows.length} dated entities; ${currentVisible.nodes.length-rows.length} excluded because this property is missing or ambiguous. Display cap: 400.`,'summary-note'));
    for(const n of rows.slice(0,400)){const row=element('div',undefined,'timeline-item'),time=element('time',n.properties[property]);time.dateTime=n.properties[property];const body=element('div');body.append(selectButton(n),element('p',n.kind,'hint'));row.append(time,body);box.append(row);}
    if(!rows.length)box.append(element('div','No timezone-qualified timestamps in the selected property. Choose another property or preserve timestamps during ingestion.','empty'));
  }
  function drawMatrix(){
    const box=$('matrix-content');box.replaceChildren();const nodes=currentVisible.nodes.slice(0,60),matrix=new Map();
    for(const e of currentVisible.edges){const key=JSON.stringify([e.source,e.target]);matrix.set(key,(matrix.get(key)||0)+1);if(e.directed===false&&e.source!==e.target){const reverse=JSON.stringify([e.target,e.source]);matrix.set(reverse,(matrix.get(reverse)||0)+1);}}
    box.append(element('p',`${nodes.length} / ${currentVisible.nodes.length} entities shown. The matrix is capped at 60; narrow filters for a more readable selection.`,'summary-note'));const table=element('table',undefined,'matrix-table'),header=element('tr');header.append(element('th','From / to'));nodes.forEach((n,i)=>{const th=element('th',String(i+1));th.title=n.label;header.append(th);});table.append(header);
    nodes.forEach((n,i)=>{const row=element('tr');row.append(element('th',(i+1)+'. '+n.label));for(const other of nodes){const td=element('td'),count=matrix.get(JSON.stringify([n.id,other.id]))||0;if(count){const b=element('button',String(count));b.setAttribute('aria-label',n.label+' to '+other.label+': '+count+' relationships');b.addEventListener('click',()=>{selected=n.id;inspect();message(n.label+' → '+other.label+': '+count+' loaded relationships.');});td.append(b);}else td.textContent='·';row.append(td);}table.append(row);});box.append(table);
  }
  function drawSummary(){
    const box=$('summary-content');box.replaceChildren();const {nodes,edges}=currentVisible,degree=counts(edges.flatMap(e=>[e.source,e.target])),metrics=element('div',undefined,'metrics');
    for(const [label,value] of [['Entities',nodes.length],['Relationships',edges.length],['Kinds',new Set(nodes.map(n=>n.kind)).size],['Isolated',nodes.filter(n=>!degree.has(n.id)).length]]){const m=element('div',undefined,'metric');m.append(element('strong',String(value)),element('span',label));metrics.append(m);}box.append(metrics);
    const property=$('numeric-property').value,groups=new Map();let skipped=0;
    for(const n of nodes){const value=property?n.properties?.[property]:1;if(typeof value!=='number'||!Number.isFinite(value)){skipped++;continue;}groups.set(n.kind,(groups.get(n.kind)||0)+value);}
    box.append(element('h3',property?'Sum of '+property+' by kind':'Entities by kind'));const bars=element('div',undefined,'bars'),max=Math.max(1,...[...groups.values()].map(Math.abs));
    for(const [kind,v] of [...groups].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))){const row=element('div',undefined,'bar-row'),track=element('div',undefined,'bar-track'),bar=element('div',undefined,'bar');bar.style.width=(Math.abs(v)/max*100)+'%';bar.style.background=color(kind);track.append(bar);row.append(element('span',kind),track,element('span',v.toLocaleString('en-US',{maximumFractionDigits:3}),'bar-value'));bars.append(row);}box.append(bars);
    if(property)box.append(element('p',`${skipped} records excluded for missing/non-numeric values. Bar length shows absolute magnitude; the label preserves the sign. Confirm units and comparability before using this sum.`,'summary-note'));
    box.append(element('p','All counts refer to the loaded, filtered selection. Communities are annotations from the producer; proximity on a layout is not evidence of a relationship.','summary-note'));
    const inferred=edges.filter(e=>(e.evidence||[]).some(x=>x.provenance==='INFERRED')).length;box.append(element('p',`${inferred} displayed relationships include an inferred observation. Source facts and model interpretations remain distinct.`,'summary-note'));
  }
  function path(){
    const start=$('path-from').value,goal=$('path-to').value;if(!start||!goal){message('Choose both path endpoints.');return;}
    const ids=new Set(currentVisible.nodes.map(n=>n.id));if(!ids.has(start)||!ids.has(goal)){message('An endpoint is outside the current filters.');return;}
    const adj=adjacent(currentVisible.edges,'outgoing'),seen=new Set([start]),prev=new Map(),q=[start];
    for(let i=0;i<q.length&&!seen.has(goal);i++)for(const [next,id] of adj.get(q[i])||[])if(!seen.has(next)){seen.add(next);prev.set(next,[q[i],id]);q.push(next);}
    highlighted.clear();if(!seen.has(goal)){message('No directed path found in the loaded, filtered projection.');refresh(false);return;}
    let current=goal;while(current!==start){const [parent,id]=prev.get(current);highlighted.add(id);current=parent;}selected=start;message('Directed shortest path: '+highlighted.size+' relationships in this projection.');switchView('graph');
  }
  function snapshot(){return {...graph,graph:{...(graph.graph||{}),node_count:currentVisible.nodes.length,edge_count:currentVisible.edges.length},nodes:currentVisible.nodes,edges:currentVisible.edges,query:{...(graph.query||{}),viewer_filter:$('search').value},metadata:{...(graph.metadata||{}),complete_database:false,viewer_projection:true,truncated:!!graph.metadata?.truncated||currentVisible.nodes.length!==graph.nodes.length}};}
  function download(name,data,type){const blob=data instanceof Blob?data:new Blob([data],{type});const url=URL.createObjectURL(blob),a=element('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function savedState(){
    syncG6Positions();
    return {schema_version:'graph-explorer-state-v1',graph_identity:identity(),view:currentView,layout:$('layout').value,theme:$('theme').value,search:$('search').value,kinds:sort(kinds),relations:sort(relations),statuses:sort(statuses),selected,focus,depth:Number($('depth').value),direction:$('direction').value,confidence:Number($('confidence').value),source:$('source-filter').value,property:$('property-key').value,value:$('property-value').value,viewport:{...viewport},node_positions:Object.fromEntries(sort(manualPositions.keys()).map(id=>[id,{...manualPositions.get(id)}]))};
  }
  function restoreState(s){
    if(!s||s.schema_version!=='graph-explorer-state-v1'||s.graph_identity!==identity())throw Error('State belongs to a different graph snapshot.');
    if(!['graph','table','timeline','matrix','summary'].includes(s.view)||!['auto','dagre','radial','circular','grid','community','force'].includes(s.layout))throw Error('Invalid state view/layout.');
    for(const [key,allowed] of [['kinds',new Set(graph.nodes.map(n=>n.kind))],['relations',new Set(graph.edges.map(e=>e.relation))],['statuses',new Set(allStatuses)]])if(!Array.isArray(s[key])||s[key].some(x=>!allowed.has(x)))throw Error('State filter is invalid.');
    if(s.selected!==null&&!byId.has(s.selected)||s.focus!==null&&!byId.has(s.focus))throw Error('State references an unknown entity.');
    if(!Number.isInteger(s.depth)||s.depth<0||s.depth>10||!Number.isFinite(s.confidence)||s.confidence<0||s.confidence>1)throw Error('State exceeds bounds.');
    if(!['both','incoming','outgoing'].includes(s.direction)||!['system','light','dark'].includes(s.theme))throw Error('Invalid state preference.');
    for(const key of ['search','source','property','value'])if(typeof s[key]!=='string'||s[key].length>2048)throw Error('State text is invalid.');
    if(!s.viewport||!['x','y','k'].every(k=>Number.isFinite(s.viewport[k]))||s.viewport.k<.025||s.viewport.k>6)throw Error('Invalid viewport.');
    // Optional additive field: legacy v1 states without coordinates still load.
    const points=s.node_positions===undefined?{}:s.node_positions;
    if(points===null||typeof points!=='object'||Array.isArray(points)||Object.keys(points).length>graph.nodes.length)throw Error('Invalid node positions.');
    for(const [id,p] of Object.entries(points))if(!byId.has(id)||!validPosition(p))throw Error('Invalid node position or unknown entity.');
    journey?.reset();finishDrag(null,true);destroyG6();manualPositions=new Map(Object.entries(points).map(([id,p])=>[id,{x:p.x,y:p.y}]));graphLayoutKey=null;
    kinds=new Set(s.kinds);relations=new Set(s.relations);statuses=new Set(s.statuses);selected=s.selected;focus=s.focus;$('layout').value=s.layout;$('theme').value=s.theme;$('search').value=s.search;$('depth').value=s.depth;$('direction').value=s.direction;$('confidence').value=s.confidence;$('source-filter').value=s.source;$('property-key').value=s.property;$('property-value').value=s.value;controls();applyTheme();switchView(s.view);viewport={...s.viewport};updateTransform();
  }
  function svgText(){
    if(!graphSelection)drawGraph();syncG6Positions();const copy=$('graph-svg').cloneNode(true),rect=$('graph-svg').getBoundingClientRect();copy.setAttribute('xmlns',NS);copy.setAttribute('width',Math.round(rect.width)||1000);copy.setAttribute('height',Math.round(rect.height)||700);copy.querySelectorAll('[data-journey-overlay]').forEach(e=>e.remove());for(const el of copy.querySelectorAll('[data-walk-state],[data-walk-edge],[data-boundary],[data-cycle]'))for(const key of ['data-walk-state','data-walk-edge','data-boundary','data-cycle'])el.removeAttribute(key);return new XMLSerializer().serializeToString(copy);
  }
  function exportData(){
    const fmt=$('export-format').value;
    if(fmt==='json')download('graph-view.json',JSON.stringify(snapshot(),null,2),'application/json');
    else if(fmt==='state')download('view-state.json',JSON.stringify(savedState(),null,2),'application/json');
    else if(fmt==='csv'){
      const escape=v=>'"'+(/^[=+\-@\t\r]/.test(String(v))?"'"+v:String(v)).replaceAll('"','""')+'"';
      const rows=[['id','kind','label','properties'],...currentVisible.nodes.map(n=>[n.id,n.kind,n.label,JSON.stringify(n.properties||{})])];download('entities.csv',rows.map(row=>row.map(escape).join(',')).join('\r\n'),'text/csv');
    }else{
      if(currentView!=='graph'){switchView('graph');message('Graph view selected for image export. Click Save again to export.');return;}
      if(fmt==='svg')download('graph.svg',svgText(),'image/svg+xml');
      else {const blob=new Blob([svgText()],{type:'image/svg+xml'}),url=URL.createObjectURL(blob),image=new Image();image.onload=()=>{const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;const ctx=canvas.getContext('2d');ctx.fillStyle=getStyle('--graph');ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(image,0,0);canvas.toBlob(b=>{if(b)download('graph.png',b);else message('PNG export failed. Use SVG.');});URL.revokeObjectURL(url);};image.onerror=()=>{URL.revokeObjectURL(url);message('PNG export was blocked. SVG remains available.');};image.src=url;}
    }
  }
  function applyTheme(){const selectedTheme=$('theme').value;document.documentElement.dataset.theme=selectedTheme==='system'?(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light'):selectedTheme;}
  async function importFile(input,mode){
    const file=input.files[0];if(!file)return;
    try{if(file.size>32*1024*1024)throw Error('File exceeds 32 MB input limit.');const data=JSON.parse(await file.text());if(mode==='state')restoreState(data);else load(data);message(mode==='state'?'View state restored.':'Local GraphView loaded. No data was uploaded.');}catch(e){message(e.message);}finally{input.value='';}
  }
  $('import-button').onclick=()=>$('import-file').click();$('import-file').onchange=()=>importFile($('import-file'),'graph');$('state-button').onclick=()=>$('state-file').click();$('state-file').onchange=()=>importFile($('state-file'),'state');
  $('export-button').onclick=exportData;$('theme').onchange=()=>{applyTheme();refresh(false);};$('layout').onchange=()=>{finishDrag(null,true);destroyG6();manualPositions.clear();graphLayoutKey=null;refresh(false);};
  document.querySelectorAll('.tab').forEach(b=>b.onclick=()=>switchView(b.dataset.view));
  let timer;for(const id of ['search','source-filter','property-key','property-value'])$(id).addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(refresh,120);});
  for(const id of ['confidence','direction','depth','table-sort','time-property','numeric-property'])$(id).addEventListener('change',()=>refresh());
  $('clear-filters').onclick=()=>{kinds=new Set(graph.nodes.map(n=>n.kind));relations=new Set(graph.edges.map(e=>e.relation));statuses=new Set(allStatuses);for(const id of ['search','source-filter','property-key','property-value'])$(id).value='';$('confidence').value='0';focus=null;controls();refresh();};
  $('reset-button').onclick=()=>{load(graph);message('View reset. Source data unchanged.');};$('fit-button').onclick=fit;
  $('focus-button').onclick=()=>{if(!selected){message('Select an entity first.');return;}focus=selected;refresh();};$('unfocus-button').onclick=()=>{focus=null;highlighted.clear();refresh();};
  $('path-button').onclick=path;$('clear-selection').onclick=()=>{selected=null;highlighted.clear();refresh(false);};
  $('page-prev').onclick=()=>{page=Math.max(0,page-1);drawTable();};$('page-next').onclick=()=>{page++;drawTable();};
  $('zoom-in').onclick=()=>{journey?.manualGesture();zoom(1.25);};$('zoom-out').onclick=()=>{journey?.manualGesture();zoom(.8);};
  $('graph-svg').addEventListener('wheel',event=>{event.preventDefault();journey?.manualGesture();const r=$('graph-svg').getBoundingClientRect();zoom(event.deltaY<0?1.12:1/1.12,event.clientX-r.left,event.clientY-r.top);},{passive:false});
  $('graph-svg').addEventListener('pointerdown',startDrag);
  $('graph-svg').addEventListener('pointermove',moveDrag);
  $('graph-svg').addEventListener('pointerup',event=>finishDrag(event));
  $('graph-svg').addEventListener('pointercancel',event=>finishDrag(event,true));
  $('graph-svg').addEventListener('lostpointercapture',event=>finishDrag(event,true));
  addEventListener('blur',()=>finishDrag(null,true));
  addEventListener('keydown',event=>{if(event.key==='Escape'&&drag){event.preventDefault();finishDrag(null,true);}});
  addEventListener('resize',()=>{if(currentView==='graph')fit();});
  matchMedia('(prefers-color-scheme:dark)').addEventListener('change',()=>{if($('theme').value==='system'){applyTheme();refresh(false);}});
  const profile=VIEWER_CONFIG.security_profile||'offline';
  $('offline-badge').textContent=profile==='extended'?'Custom code / unverified':profile==='local-live'?'Local query profile':'Offline snapshot';
  // The session slot is data, not a dynamically authorized inline program.
  // Remove the token from the DOM after reading; exports never include it.
  const sessionSlot=$('local-graph-session');
  let session=null;
  try{session=JSON.parse(sessionSlot?.textContent||'{}');}catch{/* Invalid session means no live authority. */}
  if(sessionSlot)sessionSlot.textContent='{}';
  const localOrigin=location.protocol==='http:'&&location.hostname==='127.0.0.1';
  if(profile==='local-live'&&localOrigin&&typeof session?.token==='string'&&/^[A-Za-z0-9_-]{43}$/.test(session.token)){
    const token=session.token;session=null;let pending=null;
    $('live-panel').hidden=false;$('offline-badge').textContent='Local, read-only';$('live-query').value=JSON.stringify({operation:'subgraph',max_nodes:500},null,2);
    addEventListener('pagehide',()=>pending?.abort());
    $('live-button').onclick=async()=>{
      if(pending)return;
      const controller=new AbortController();pending=controller;
      const timer=setTimeout(()=>controller.abort(),10000);
      try{
        // Resolve against the origin, never document.baseURI or a data-provided URL.
        const endpoint=new URL('/api/query',location.origin);
        if(location.protocol!=='http:'||endpoint.hostname!=='127.0.0.1'||endpoint.origin!==location.origin)throw Error('Live access requires the same local Engine origin.');
        const request=JSON.parse($('live-query').value),body=JSON.stringify(request);
        if(new TextEncoder().encode(body).length>65536)throw Error('Local query exceeds the 64 KiB request budget.');
        $('live-button').disabled=true;
        const response=await fetch(endpoint.href,{method:'POST',mode:'same-origin',credentials:'omit',redirect:'error',referrerPolicy:'no-referrer',cache:'no-store',signal:controller.signal,headers:{'Content-Type':'application/json','X-Local-Graph-Token':token},body});
        const reader=response.body?.getReader();if(!reader)throw Error('Streaming response support is required for bounded local queries.');
        const decoder=new TextDecoder('utf-8',{fatal:true});let total=0,content='';
        while(true){const {done,value}=await reader.read();if(done)break;total+=value.byteLength;if(total>8*1024*1024){await reader.cancel();throw Error('Local response exceeds the 8 MiB budget.');}content+=decoder.decode(value,{stream:true});}
        content+=decoder.decode();const result=JSON.parse(content);
        if(!response.ok||result.status!=='pass')throw Error(result.error||'Local query failed.');
        if(result.view)load(result.view);
        $('live-result').textContent=JSON.stringify(result.view?{status:result.status,nodes:result.view.nodes.length,edges:result.view.edges.length}:result,null,2);message('Local read-only query complete.');
      }catch(error){message(error.name==='AbortError'?'Local query canceled or timed out.':error.message);}
      finally{clearTimeout(timer);pending=null;$('live-button').disabled=false;}
    };
  }
  session=null;
  if(window.LocalGraphJourney&&$('walk-prepare'))journey=LocalGraphJourney.create({
    identity,positions:()=>positions,nodeElements:()=>nodeElements,
    edgeRecords:()=>[...new Map([...incidentEdges.values()].flat().map(r=>[r.edge.id,r])).values()],
    viewport:()=>viewport,rect:()=>$('graph-svg').getBoundingClientRect(),dragging:()=>!!drag,isGraph:()=>currentView==='graph',
    prepare:()=>{if(g6){destroyG6();message('Guided walkthrough uses the bundled SVG renderer.');}},
    inspect:id=>{if(byId?.has(id)){selected=id;inspect();$('selection-status').textContent=byId.get(id).label;}},
    panTo:(x,y)=>{const r=$('graph-svg').getBoundingClientRect();viewport.x=r.width/2-x*viewport.k;viewport.y=r.height/2-y*viewport.k;updateTransform();},
    fit,message
  });
  // A small read-only testing/debug surface; it cannot mutate the SQLite database.
  window.LocalGraphView={getSnapshot:()=>JSON.parse(JSON.stringify(snapshot())),getState:savedState,restoreState,validate,getPositions:()=>Object.fromEntries(positions),getWalkthrough:()=>journey?.getState()||{status:'unavailable'}};
  try{applyTheme();load(INITIAL_GRAPH);}catch(error){message('Could not load GraphView: '+error.message);}
})();
