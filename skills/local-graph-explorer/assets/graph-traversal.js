/* Deterministic structural walkthroughs. Standalone, original implementation.
 * A layer is a topological level, never evidence of temporal concurrency.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.LocalGraphTraversal=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const sorted=xs=>[...xs].sort((a,b)=>a<b?-1:a>b?1:0);
  function build(inputNodes,inputEdges,options={}){
    if(!Array.isArray(inputNodes)||!Array.isArray(inputEdges))throw Error('Expected graph arrays.');
    if(inputNodes.length>500||inputEdges.length>4000)throw Error('Walkthrough budget: at most 500 nodes and 4000 edges.');
    const ids=new Set(),edgeIds=new Set();
    for(const n of inputNodes){if(!n||typeof n.id!=='string'||!n.id||ids.has(n.id))throw Error('Invalid or duplicate node.');ids.add(n.id);}
    for(const e of inputEdges){
      if(!e||typeof e.id!=='string'||!e.id||edgeIds.has(e.id)||!ids.has(e.source)||!ids.has(e.target))throw Error('Invalid edge or missing endpoint.');
      if(e.directed!==undefined&&typeof e.directed!=='boolean')throw Error('Invalid direction.');edgeIds.add(e.id);
    }
    const mode=options.mode||'downstream',start=options.start||null,target=options.target||null;
    if(!['downstream','upstream','path'].includes(mode))throw Error('Invalid walkthrough mode.');
    if(start!==null&&!ids.has(start)||target!==null&&!ids.has(target))throw Error('Endpoint is outside this projection.');
    if(mode==='path'&&(!start||!target))throw Error('A directed path needs both endpoints.');
    const edges=inputEdges.filter(e=>e.directed!==false).slice().sort((a,b)=>a.id<b.id?-1:1);
    const oriented=edges.map(e=>({id:e.id,source:mode==='upstream'?e.target:e.source,target:mode==='upstream'?e.source:e.target}));
    const adj=new Map(sorted(ids).map(id=>[id,[]]));
    for(const e of oriented)adj.get(e.source).push([e.target,e.id]);
    for(const values of adj.values())values.sort((a,b)=>a[0]<b[0]?-1:a[0]>b[0]?1:a[1]<b[1]?-1:1);
    const base={mode,start,target,undirected_excluded:inputEdges.length-edges.length};
    if(mode==='path'){
      const queue=[start],seen=new Set([start]),previous=new Map();
      for(let i=0;i<queue.length&&!seen.has(target);i++)for(const [next,eid] of adj.get(queue[i])){
        if(seen.has(next))continue;seen.add(next);previous.set(next,[queue[i],eid]);queue.push(next);
      }
      if(!seen.has(target))throw Error('No directed path in the displayed, filtered projection.');
      const route=[target],routeEdges=[];let current=target;
      while(current!==start){const [parent,eid]=previous.get(current);route.unshift(parent);routeEdges.unshift(eid);current=parent;}
      return {...base,nodes:sorted(route),starts:[start],ends:[target],cycles:[],excluded_nodes:ids.size-route.length,
        steps:route.map((id,index)=>({index,nodes:[id],edges:index?[routeEdges[index-1]]:[],cycles:[]}))};
    }
    let chosen=ids;
    if(start){
      chosen=new Set([start]);const queue=[start];
      for(let i=0;i<queue.length;i++)for(const [next] of adj.get(queue[i]))if(!chosen.has(next)){chosen.add(next);queue.push(next);}
    }
    const nodes=sorted(chosen),scoped=oriented.filter(e=>chosen.has(e.source)&&chosen.has(e.target));
    const forward=new Map(nodes.map(id=>[id,[]])),reverse=new Map(nodes.map(id=>[id,[]]));
    for(const e of scoped){forward.get(e.source).push(e.target);reverse.get(e.target).push(e.source);}
    for(const map of [forward,reverse])for(const [id,values] of map)map.set(id,sorted(new Set(values)));
    // Iterative Kosaraju: cycles are explicit groups; no recursion depth hazard.
    const seen=new Set(),finish=[];
    for(const root of nodes){
      if(seen.has(root))continue;seen.add(root);const stack=[[root,0]];
      while(stack.length){const frame=stack[stack.length-1],next=forward.get(frame[0]);
        if(frame[1]<next.length){const id=next[frame[1]++];if(!seen.has(id)){seen.add(id);stack.push([id,0]);}}
        else {finish.push(frame[0]);stack.pop();}
      }
    }
    seen.clear();const components=[];
    for(const root of finish.reverse()){
      if(seen.has(root))continue;const members=[],stack=[root];seen.add(root);
      while(stack.length){const id=stack.pop();members.push(id);for(const next of reverse.get(id))if(!seen.has(next)){seen.add(next);stack.push(next);}}
      components.push(sorted(members));
    }
    components.sort((a,b)=>a[0]<b[0]?-1:1);
    const componentOf=new Map();components.forEach((group,i)=>group.forEach(id=>componentOf.set(id,i)));
    const ins=components.map(()=>new Set()),outs=components.map(()=>new Set());
    for(const e of scoped){const a=componentOf.get(e.source),b=componentOf.get(e.target);if(a!==b){outs[a].add(b);ins[b].add(a);}}
    const selfLoops=new Set(scoped.filter(e=>e.source===e.target).map(e=>e.source));
    const cyclic=components.map(c=>c.length>1||selfLoops.has(c[0]));
    const cycles=components.filter((_,i)=>cyclic[i]);
    const starts=sorted(components.flatMap((c,i)=>ins[i].size?[]:c)),ends=sorted(components.flatMap((c,i)=>outs[i].size?[]:c));
    const degree=ins.map(v=>v.size),steps=[];let ready=degree.map((d,i)=>d===0?i:-1).filter(i=>i>=0);
    while(ready.length){
      ready.sort((a,b)=>a-b);const wave=new Set(ready),waveNodes=sorted(ready.flatMap(i=>components[i]));
      steps.push({index:steps.length,nodes:waveNodes,edges:scoped.filter(e=>wave.has(componentOf.get(e.target))).map(e=>e.id).sort(),cycles:ready.filter(i=>cyclic[i]).map(i=>components[i])});
      const next=[];for(const i of ready)for(const n of outs[i])if(--degree[n]===0)next.push(n);ready=next;
    }
    if(steps.reduce((n,s)=>n+s.nodes.length,0)!==nodes.length)throw Error('Invalid condensed graph.');
    return {...base,nodes,starts,ends,cycles,excluded_nodes:ids.size-chosen.size,steps};
  }
  return Object.freeze({build});
});
