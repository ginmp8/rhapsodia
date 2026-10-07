/* Reader-controlled finite walkthrough. Presentation state never enters GraphView. */
(() => {
  'use strict';
  const $=id=>document.getElementById(id),NS='http://www.w3.org/2000/svg';
  const svg=(tag,attrs)=>{const e=document.createElementNS(NS,tag);for(const [k,v] of Object.entries(attrs||{}))e.setAttribute(k,String(v));return e;};
  const ordered=xs=>[...xs].sort((a,b)=>a<b?-1:a>b?1:0);
  function create(host){
    let scope={nodes:[],edges:[]},scopeKey=null,overview=null,plan=null,step=0,status='idle',timer=null,epoch=0,miniFrame=null;
    const media=matchMedia('(prefers-reduced-motion: reduce)');
    const label=id=>scope.nodes.find(n=>n.id===id)?.label||id;
    const state=()=>({status,step,steps:plan?.steps.length||0,mode:plan?.mode||null,start:plan?.start||null,target:plan?.target||null,
      starts:plan?.starts||overview?.starts||[],ends:plan?.ends||overview?.ends||[],cycles:plan?.cycles||overview?.cycles||[]});
    function cancel(){clearTimeout(timer);timer=null;epoch++;}
    function pause(reason='Paused'){
      if(status!=='playing')return;
      cancel();status='paused';update(reason);
    }
    function reset(reason='Choose a direction and prepare a structural walkthrough.'){
      cancel();plan=null;step=0;status='idle';update(reason);
    }
    function setScope(nodes,edges){
      const key=JSON.stringify([host.identity(),nodes.map(n=>n.id),edges.map(e=>[e.id,e.source,e.target,e.directed!==false])]);
      const changed=scopeKey!==null&&scopeKey!==key;
      scope={nodes,edges};
      if(scopeKey!==key){
        scopeKey=key;
        overview=LocalGraphTraversal.build(nodes,edges);
        for(const id of ['walk-from','walk-to']){
          const select=$(id),old=select.value;select.replaceChildren(new Option(id==='walk-from'?'All displayed entry groups':'Choose endpoint',''));
          for(const n of nodes)select.add(new Option(n.label,n.id));
          select.value=nodes.some(n=>n.id===old)?old:'';
        }
        if(changed)reset('Projection changed. Prepare the walkthrough again.');
      }
      $('walk-summary').textContent=`Displayed projection: ${overview.starts.length} entry members / ${overview.ends.length} end members / ${overview.cycles.length} cycle groups. ${overview.undirected_excluded} undirected relationships excluded from ordering.`;
      update();
    }
    function prepare(){
      reset('Preparing structural walkthrough.');
      try{
        const options={mode:$('walk-mode').value,start:$('walk-from').value||null,target:$('walk-to').value||null};
        const next=LocalGraphTraversal.build(scope.nodes,scope.edges,options);
        if(!next.steps.length)throw Error('No displayed nodes to walk through.');
        host.prepare();plan=next;step=0;status='paused';
        update('Prepared. Playback is optional; the graph remains movable.');
        host.inspect(plan.steps[0].nodes[0]);
      }catch(error){reset('No walkthrough prepared.');host.message(error.message);}
    }
    function follow(){
      if(!plan||!$('walk-follow').checked||host.dragging())return;
      const points=plan.steps[step].nodes.map(id=>host.positions().get(id)).filter(Boolean);
      if(points.length)host.panTo(points.reduce((n,p)=>n+p.x,0)/points.length,points.reduce((n,p)=>n+p.y,0)/points.length);
    }
    function seek(index,user=true){
      if(!plan)return;
      if(user){cancel();status='paused';}
      step=Math.max(0,Math.min(plan.steps.length-1,Math.trunc(index)));
      if(status==='playing'&&step===plan.steps.length-1){cancel();status='ended';}
      host.inspect(plan.steps[step].nodes[0]);update();follow();
    }
    function schedule(){
      const activeEpoch=epoch;
      timer=setTimeout(()=>{
        if(activeEpoch!==epoch||status!=='playing')return;
        if(document.hidden||!host.isGraph()){pause('Paused while the graph is not visible.');return;}
        seek(step+1,false);
        if(status==='playing')schedule();
      },1000/Number($('walk-speed').value));
    }
    function play(){
      if(status==='playing'){pause();return;}
      if(!plan||plan.steps.length<2)return;
      if(media.matches){update('Reduced motion: use Previous, Next or the step slider.');return;}
      if(document.hidden||!host.isGraph())return;
      cancel();if(step===plan.steps.length-1)step=0;status='playing';update();follow();schedule();
    }
    function decorate(){
      const current=new Set(plan?.steps[step]?.nodes||[]),activeEdges=new Set(plan?.steps[step]?.edges||[]);
      const visited=new Set(plan?plan.steps.slice(0,step).flatMap(s=>s.nodes):[]),visitedEdges=new Set(plan?plan.steps.slice(0,step).flatMap(s=>s.edges):[]);
      const boundary=plan||overview,starts=new Set(boundary?.starts||[]),ends=new Set(boundary?.ends||[]),cycles=new Set((boundary?.cycles||[]).flat());
      for(const [id,node] of host.nodeElements()){
        node.querySelectorAll('[data-journey-overlay]').forEach(e=>e.remove());
        for(const a of ['data-walk-state','data-boundary','data-cycle'])node.removeAttribute(a);
        if(plan)node.dataset.walkState=current.has(id)?'current':visited.has(id)?'visited':'future';
        const role=cycles.has(id)?'cycle':starts.has(id)&&ends.has(id)?'isolated':starts.has(id)?'entry':ends.has(id)?'end':null;
        if(role){
          node.dataset.boundary=role;
          const badge=svg('g',{'data-journey-overlay':'boundary','aria-hidden':'true'});
          const mark=role==='entry'?'IN':role==='end'?'END':role==='cycle'?'CYCLE':'IN / END';
          const t=svg('text',{x:70,y:-30,'text-anchor':'end','font-size':9,'font-weight':700,fill:'var(--accent)'});t.textContent=mark;badge.append(t);node.append(badge);
        }
      }
      for(const r of host.edgeRecords()){
        r.line.removeAttribute('data-walk-edge');
        if(plan)r.line.dataset.walkEdge=activeEdges.has(r.edge.id)?'active':visitedEdges.has(r.edge.id)?'visited':'future';
      }
    }
    function update(reason){
      if(!$('walk-prepare'))return;
      $('walk-prev').disabled=!plan||step===0;$('walk-next').disabled=!plan||step>=plan.steps.length-1;
      $('walk-play').disabled=!plan||plan.steps.length<2||media.matches;
      $('walk-play').textContent=status==='playing'?'Pause':status==='ended'?'Replay':'Play';
      $('walk-play').setAttribute('aria-pressed',String(status==='playing'));
      $('walk-progress').disabled=!plan;$('walk-progress').max=Math.max(0,(plan?.steps.length||1)-1);$('walk-progress').value=step;
      $('walk-progress').setAttribute('aria-valuetext',plan?`Step ${step+1} of ${plan.steps.length}`:'Not prepared');
      $('walk-count').textContent=plan?`${step+1} / ${plan.steps.length}`:'0 / 0';
      if(reason)$('walk-status').textContent=reason;
      else if(plan)$('walk-status').textContent=(status==='playing'?'Playing':status==='ended'?'Finished':'Paused')+' - structural walkthrough, not a live execution.';
      if(media.matches)$('walk-status').textContent='Reduced motion: manual steps only. No autoplay.';
      const rail=$('walk-rail');rail.replaceChildren();
      if(plan){
        const current=plan.steps[step];
        const edgeIds=new Set(current.edges),facts=scope.edges.filter(e=>edgeIds.has(e.id));
        const relationships=facts.slice(0,3).map(e=>`${label(e.source)} --${e.relation}--> ${label(e.target)}`).join('; ');
        $('walk-detail').textContent=(plan.mode==='path'?'Directed path':'Dependency layer')+` ${step+1}: `+current.nodes.map(label).join(' / ')+'. '+
          (current.cycles.length?'Cycle group: no internal start or end is implied. ':'')+
          (current.nodes.length>1?'Same structural level, not runtime parallelism. ':'')+
          (plan.excluded_nodes?`${plan.excluded_nodes} displayed nodes are outside this walkthrough. `:'')+
          'Visited means read, not executed.'+(relationships?' Relationships (original direction): '+relationships+'. ':'')+(facts.length>3?`${facts.length-3} further relationships: inspect the graph.`:'');
        // Bounded chapter window instead of hundreds of DOM buttons.
        const first=Math.max(0,Math.min(step-3,plan.steps.length-7));
        for(let i=first;i<Math.min(plan.steps.length,first+7);i++){
          const b=document.createElement('button');b.textContent=String(i+1);b.title=plan.steps[i].nodes.map(label).join(' / ');b.setAttribute('aria-label',`Go to step ${i+1}`);b.setAttribute('aria-current',String(i===step));b.onclick=()=>seek(i);rail.append(b);
        }
      }else $('walk-detail').textContent='Entry and end markers are relative to displayed directed relationships. Cycles are grouped, not flattened into a false sequence.';
      decorate();drawMiniMap();
    }
    function drawMiniMap(){
      const mini=$('walk-minimap');if(!mini)return;mini.replaceChildren();
      const points=scope.nodes.map(n=>host.positions().get(n.id)).filter(Boolean);if(!points.length)return;
      const minX=Math.min(...points.map(p=>p.x))-100,maxX=Math.max(...points.map(p=>p.x))+100,minY=Math.min(...points.map(p=>p.y))-65,maxY=Math.max(...points.map(p=>p.y))+65;
      mini.setAttribute('viewBox',`${minX} ${minY} ${Math.max(200,maxX-minX)} ${Math.max(130,maxY-minY)}`);
      for(const e of scope.edges){const a=host.positions().get(e.source),b=host.positions().get(e.target);if(a&&b)mini.append(svg('line',{x1:a.x,y1:a.y,x2:b.x,y2:b.y,stroke:'var(--edge)','stroke-width':4}));}
      const active=new Set(plan?.steps[step]?.nodes||[]);
      for(const n of scope.nodes){const p=host.positions().get(n.id);if(p)mini.append(svg('rect',{x:p.x-50,y:p.y-16,width:100,height:32,rx:5,fill:active.has(n.id)?'var(--accent)':'var(--muted)'}));}
      const v=host.viewport(),r=host.rect();
      mini.append(svg('rect',{x:-v.x/v.k,y:-v.y/v.k,width:r.width/v.k,height:r.height/v.k,fill:'none',stroke:'var(--accent)','stroke-width':5,'vector-effect':'non-scaling-stroke','stroke-opacity':.6}));
    }
    function scheduleMiniMap(){
      if(miniFrame!==null)return;
      miniFrame=requestAnimationFrame(()=>{miniFrame=null;drawMiniMap();});
    }
    function manualGesture(){if($('walk-follow').checked){$('walk-follow').checked=false;$('walk-status').textContent='Follow camera released. You control the viewport; playback is unchanged.';}}
    $('walk-prepare').onclick=prepare;$('walk-play').onclick=play;
    $('walk-prev').onclick=()=>seek(step-1);$('walk-next').onclick=()=>seek(step+1);$('walk-reset').onclick=()=>reset();
    $('walk-progress').oninput=()=>seek(Number($('walk-progress').value));
    $('walk-mode').onchange=()=>{$('walk-to').disabled=$('walk-mode').value!=='path';reset('Direction changed. Prepare a new walkthrough.');};
    for(const id of ['walk-from','walk-to'])$(id).onchange=()=>reset('Endpoint changed. Prepare a new walkthrough.');
    $('walk-speed').onchange=()=>{if(status==='playing'){cancel();schedule();}};
    $('walk-follow').onchange=()=>{if($('walk-follow').checked)follow();};
    $('walk-minimap').addEventListener('click',event=>{
      const matrix=$('walk-minimap').getScreenCTM();if(!matrix)return;manualGesture();
      const point=new DOMPoint(event.clientX,event.clientY).matrixTransform(matrix.inverse());host.panTo(point.x,point.y);
    });
    $('walk-minimap').addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();manualGesture();host.fit();}});
    document.addEventListener('visibilitychange',()=>{if(document.hidden)pause('Paused because the page is hidden.');});
    window.addEventListener('blur',()=>pause('Paused because the window lost focus.'));
    media.addEventListener('change',()=>{if(media.matches)pause();update();});
    update();
    return {setScope,reset,pause,getState:()=>JSON.parse(JSON.stringify(state())),isActive:()=>!!plan,
      positionsChanged:scheduleMiniMap,cameraChanged:scheduleMiniMap,manualGesture,
      viewChanged:view=>{if(view!=='graph')pause('Paused while another data view is open.');}};
  }
  window.LocalGraphJourney=Object.freeze({create});
})();
