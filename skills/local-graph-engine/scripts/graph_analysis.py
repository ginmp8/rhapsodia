"""Deterministic graph analytics with optional explicitly selected NetworkX."""
from __future__ import annotations
import json
from collections import defaultdict,deque
from pathlib import Path
import graph_engine as ge
from graph_common import canonical,digest
from graph_query import adjacency,filtered_graph,validate_request
from graph_store import readonly,ensure_extensions,logical_hash


def components(nodes,adj):
    seen=set();result=[]
    for node in sorted(nodes):
        if node in seen:continue
        q=deque([node]);seen.add(node);members=[]
        while q:
            current=q.popleft();members.append(current)
            for other,_ in adj.get(current,[]):
                if other not in seen:seen.add(other);q.append(other)
        result.append(sorted(members))
    return sorted(result)

def scc(nodes,rows):
    out=adjacency(rows,'outgoing');inc=adjacency(rows,'incoming');seen=set();order=[]
    for start in sorted(nodes):
        if start in seen:continue
        stack=[(start,False)]
        while stack:
            node,done=stack.pop()
            if done:order.append(node);continue
            if node in seen:continue
            seen.add(node);stack.append((node,True))
            for other,_ in reversed(out.get(node,[])):
                if other not in seen:stack.append((other,False))
    seen=set();groups=[]
    for start in reversed(order):
        if start in seen:continue
        group=[];stack=[start];seen.add(start)
        while stack:
            node=stack.pop();group.append(node)
            for other,_ in inc.get(node,[]):
                if other not in seen:seen.add(other);stack.append(other)
        groups.append(sorted(group))
    return sorted(groups)

def pagerank(nodes,rows,alpha=.85,tolerance=1e-10,max_iterations=300):
    ids=sorted(nodes);n=len(ids)
    if not n:return {},0
    out=adjacency(rows,'outgoing');rank={node:1/n for node in ids}
    for iteration in range(max_iterations):
        dangling=sum(rank[v] for v in ids if not out.get(v))
        new={v:(1-alpha)/n+alpha*dangling/n for v in ids}
        for node in ids:
            neighbors=out.get(node,[])
            if neighbors:
                share=alpha*rank[node]/len(neighbors)
                for target,_ in neighbors:new[target]+=share
        delta=sum(abs(rank[v]-new[v]) for v in ids);rank=new
        if delta<tolerance:return rank,iteration+1
    raise ValueError('PageRank did not converge within the iteration budget')

def analyze(db:Path,algorithm='components',backend='stdlib',seed=0)->dict:
    allowed={'components','scc','cycles','degree','pagerank','betweenness','closeness','communities','leiden','louvain'}
    if algorithm not in allowed:raise ValueError('unknown algorithm')
    if backend not in ('stdlib','networkx'):raise ValueError('unknown backend')
    con=readonly(db)
    try:
        con.execute('BEGIN')
        request=validate_request({'operation':'subgraph'})
        nodes,rows=filtered_graph(con,request)
        if len(nodes)>20000 or len(rows)>100000:raise ValueError('analytics budget exceeded; work with a bounded partition')
        source_hash=logical_hash(con)
    finally:con.close()
    groups=[];metrics={};extra={};version='builtin-2.0.0'
    if algorithm=='components':groups=components(nodes,adjacency(rows,'both'))
    elif algorithm in ('scc','cycles'):
        groups=scc(nodes,rows)
        if algorithm=='cycles':
            loops={r['source_node_id'] for r in rows if r['source_node_id']==r['target_node_id']}
            groups=[g for g in groups if len(g)>1 or any(n in loops for n in g)]
            extra['interpretation']='strongly connected cyclic regions; not enumeration of all simple cycles'
    elif algorithm=='degree':
        out=adjacency(rows,'outgoing');inc=adjacency(rows,'incoming')
        metrics={'in_degree':{n:len(inc.get(n,[])) for n in nodes},'out_degree':{n:len(out.get(n,[])) for n in nodes}}
    elif algorithm=='pagerank':
        scores,iterations=pagerank(nodes,rows);metrics={'pagerank':scores};extra['iterations']=iterations
    else:
        if backend!='networkx':raise ValueError('this algorithm requires --backend networkx explicitly')
        try:import networkx as nx
        except ImportError as exc:raise RuntimeError('optional NetworkX library is not installed') from exc
        version=nx.__version__
        # Every input relation is retained in the store. Analytics projects parallel
        # relations as weighted simple arcs, recording that projection explicitly.
        directed=nx.DiGraph();directed.add_nodes_from(sorted(nodes))
        for source,targets in sorted(adjacency(rows,'outgoing').items()):
            for target,_ in targets:
                weight=directed.get_edge_data(source,target,{}).get('weight',0)+1
                directed.add_edge(source,target,weight=weight)
        undirected=nx.Graph();undirected.add_nodes_from(sorted(nodes))
        for r in rows:
            a,b=r['source_node_id'],r['target_node_id']
            undirected.add_edge(a,b,weight=undirected.get_edge_data(a,b,{}).get('weight',0)+1)
        extra['projection']='parallel relations aggregated as arc/edge multiplicity'
        if algorithm in ('betweenness','closeness'):
            if len(nodes)>2000:raise ValueError('exact centrality budget is 2000 nodes')
            scores=nx.betweenness_centrality(directed,normalized=True,weight=None) if algorithm=='betweenness' else nx.closeness_centrality(directed)
            metrics={algorithm:scores}
        elif not undirected.number_of_edges():groups=[[n] for n in sorted(nodes)]
        elif algorithm=='communities':groups=nx.community.greedy_modularity_communities(undirected,weight='weight')
        elif algorithm=='louvain':groups=nx.community.louvain_communities(undirected,weight='weight',seed=seed)
        elif algorithm=='leiden':
            fn=getattr(nx.community,'leiden_communities',None)
            if fn is None:raise RuntimeError('installed NetworkX does not provide Leiden; no silent algorithm substitution')
            groups=fn(undirected,weight='weight',seed=seed)
        groups=sorted(sorted(g) for g in groups)
    params={'algorithm':algorithm,'backend':backend,'seed':seed,'evidence_statuses':['accepted']}
    run_id='run:'+digest([source_hash,params,version])[:32]
    con=ge.connect(db)
    try:
        con.execute('BEGIN IMMEDIATE');ensure_extensions(con)
        if logical_hash(con)!=source_hash:raise ValueError('graph changed during analysis; rerun on the new snapshot')
        con.execute('DELETE FROM analysis_runs WHERE id=?',(run_id,))
        con.execute('INSERT INTO analysis_runs VALUES(?,?,?,?,?,?)',(run_id,algorithm,version,canonical(params),source_hash,'pass'))
        for metric,scores in sorted(metrics.items()):
            con.executemany('INSERT INTO node_metrics VALUES(?,?,?,?)',[(run_id,n,metric,float(scores[n])) for n in sorted(scores)])
        for members in groups:
            cid='community:'+digest(members)[:24]
            con.execute('INSERT INTO communities VALUES(?,?,?,?)',(run_id,cid,algorithm+' '+str(len(members)),canonical({'algorithm':algorithm})))
            con.executemany('INSERT INTO community_members VALUES(?,?,?)',[(run_id,cid,n) for n in members])
        if groups and algorithm not in ('cycles',):con.execute("INSERT INTO graph_meta VALUES('current_analysis',?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",(run_id,))
        con.commit()
    except Exception:con.rollback();raise
    finally:con.close()
    return {'status':'pass','run_id':run_id,'algorithm':algorithm,'backend':backend,'backend_version':version,'graph_hash':source_hash,'groups':groups,'metrics':{k:dict(sorted(v.items())) for k,v in metrics.items()},**extra}
