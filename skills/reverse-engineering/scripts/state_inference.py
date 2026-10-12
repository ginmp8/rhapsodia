#!/usr/bin/env python3
"""Evidence-bounded state transition inference, with opt-in trusted active queries.

Does not assert equivalence to a minimal DFA/Mealy machine. Missing state
observations are represented by distinct prefix nodes (never silently merged).
"""
from __future__ import annotations
import argparse
from collections import defaultdict, deque
import hashlib
import itertools
import json
from pathlib import Path
import sys
from typing import Any
from behavior_lab import DataError, load_corpus, strict_json
from json_writer import write_exclusive
from oracle_runner import check_command, run_one


def canon(v: Any) -> str:
    return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',', ':'),allow_nan=False)


def identity(v: Any) -> str:
    return hashlib.sha256(canon(v).encode('utf-8')).hexdigest()[:18]


def action_id(a: Any) -> str:
    if isinstance(a,dict):
        key=a.get('action',a.get('method',a.get('name')))
        if isinstance(key,str) and 0<len(key)<=128:
            # All arguments are part of label to avoid merging distinct commands.
            return key+'@'+identity(a)
    return 'action@'+identity(a)


def infer(rows: dict, alphabet: list | None = None, max_states: int = 5000) -> dict:
    nodes: dict[str,dict]={}
    transitions: dict[tuple[str,str],set[tuple[str,str]]]=defaultdict(set)
    paths: dict[str,list]= {'initial':[]}
    examples=[];skipped=[]
    nodes['initial']={'id':'initial','evidence':'initial-state-assumed-reset','paths':1}
    for cid, case in sorted(rows.items()):
        if case.get('runner_status','ok')!='ok':
            skipped.append({'id':cid,'reason':'unverified runner status'})
            continue
        data=case['input']; obs=case['observation']
        actions=data.get('actions') if isinstance(data,dict) else None
        steps=obs.get('steps') if isinstance(obs,dict) else None
        if not isinstance(actions,list) or not isinstance(steps,list) or len(actions)!=len(steps):
            skipped.append({'id':cid,'reason':'no aligned input.actions/observation.steps'})
            continue
        prior='initial'
        prefix=[]
        for idx, (act, step) in enumerate(zip(actions,steps)):
            prefix.append(act)
            # Explicit state is the only observable state-equality basis.
            if 'state' in step:
                nxt='observed:'+identity(step['state'])
                status='observed-state-value'
            else:
                nxt='prefix:'+identity(prefix)
                status='unknown-state-prefix'
            if nxt not in nodes and len(nodes)>=max_states:
                skipped.append({'id':cid,'reason':'state budget exceeded'});break
            nodes.setdefault(nxt,{'id':nxt,'evidence':status,'paths':0})
            nodes[nxt]['paths']+=1
            paths.setdefault(nxt,list(prefix))
            # Preserve a hashed observable signature, not secrets in output values.
            observed = {k:step[k] for k in ('output','error','status','events','effects') if k in step}
            aid=action_id(act)
            transitions[(prior,aid)].add((nxt,identity(observed)))
            examples.append({'source':cid,'action_index':idx,'from':prior,'action':aid,
                             'to':nxt,'observation_sha256':identity(observed)})
            prior=nxt
    output=[];conflicts=[]
    for (source, aid), outcomes in sorted(transitions.items()):
        for target,obsid in sorted(outcomes):
            output.append({'from':source,'action':aid,'to':target,'observation_hash':obsid})
        if len(outcomes)>1:
            conflicts.append({'state':source,'action':aid,'observed_outcomes':len(outcomes),
                              'reason':'nondeterminism, missing reset, or abstracted state alias'})
    suggestions=[]
    if alphabet:
        for state_id,path in sorted(paths.items(),key=lambda p:(len(p[1]),p[0])):
            for act in alphabet:
                aid=action_id(act)
                if (state_id,aid) not in transitions:
                    suggestions.append({'input':{'actions':path+[act]},'from':state_id,
                                        'missing_action':aid,'status':'hypothesis-not-observed'})
                if len(suggestions)>=200:break
            if len(suggestions)>=200:break
    return {'schema_version':'1.0','mode':'observed-state-inference',
            'states':sorted(nodes.values(),key=lambda x:x['id']),
            'transitions':output,'conflicts':conflicts,'skipped':skipped[:200],
            'missing_transition_probes':suggestions,
            'cases_with_steps':len(set(e['source'] for e in examples)),
            'completeness':'finite observed transitions only; no complete automaton or state-minimality proof',
            'limitations':['reset and external effects not authenticated',
                           'state equality relies on supplied explicit state; others are prefix nodes',
                           'different outputs from same abstract state are not averaged']}


def active_capture(alphabet: list, command_file: Path, cwd: Path, *, depth:int=2,
                   max_queries:int=100, execute_authorized:bool=False, reset_confirmed:bool=False) -> list:
    if not execute_authorized or not reset_confirmed:
        raise DataError('active queries require explicit authorization and a confirmed resettable TRUSTED oracle')
    if cwd.is_symlink() or not cwd.is_dir():
        raise DataError('cwd must be nonsymlink directory')
    if not 1<=depth<=5 or not 1<=max_queries<=200 or not 1<=len(alphabet)<=12:
        raise DataError('active query budget exceeded')
    if any(not isinstance(a,dict) for a in alphabet):
        raise DataError('alphabet entries must be action objects')
    command=check_command(command_file)
    rows=[]
    for n in range(1,depth+1):
        for actions in itertools.product(alphabet,repeat=n):
            stimulus={'actions':list(actions)}
            status,observed=run_one(command,stimulus,cwd,3.0,256*1024,512)
            if status=='ok' and (not isinstance(observed.get('steps'),list) or
                                 len(observed['steps'])!=len(stimulus['actions'])):
                status='invalid-output'
                observed={'error':{'kind':'missing_aligned_steps'}}
            rows.append({'id':f'active-{len(rows):04}', 'schema_version':'2.0',
                         'kind':'trusted-active-query','input':stimulus,
                         'observation':observed,'runner_status':status})
            if len(rows)>=max_queries:
                return rows
    return rows



def aalpy_learn(alphabet:list, command_file:Path, cwd:Path, *, authorized:bool=False,
                reset_confirmed:bool=False, max_queries:int=100, seed:int=0)->dict:
    """Optional active L* Mealy inference. Requires AALpy installed by operator.

    Each SUL.step replays a full prefix in a fresh TRUSTED process. Reset must
    be deterministic; otherwise stateful membership answers are incomparable.
    """
    if not authorized or not reset_confirmed:
        raise DataError('AALpy mode requires authorized trusted executable and confirmed reset')
    if not 1<=len(alphabet)<=12 or not 1<=max_queries<=500 or any(not isinstance(x,dict) for x in alphabet):
        raise DataError('invalid alphabet/query budget')
    if cwd.is_symlink() or not cwd.is_dir():raise DataError('nonsymlink cwd required')
    try:
        from aalpy.base import SUL
        from aalpy.oracles import RandomWalkEqOracle
        from aalpy.learning_algs import run_Lstar
    except ImportError as exc:
        raise DataError('AALpy is optional and unavailable; use offline/active stdlib modes') from exc
    import random
    command=check_command(command_file)
    input_alphabet=list(range(len(alphabet)))
    class ReferenceSUL(SUL):
        def __init__(self):
            super().__init__()
            self.prefix=[]
            self.queries=0
        def pre(self):self.prefix=[]
        def post(self):pass
        def step(self,letter):
            if self.queries>=max_queries:
                raise DataError('bounded membership-query budget reached')
            self.prefix.append(alphabet[letter]);self.queries+=1
            status,obs=run_one(command,{'actions':self.prefix},cwd,3.0,256*1024,512)
            if status!='ok' or not isinstance(obs.get('steps'),list) or len(obs['steps'])!=len(self.prefix):
                raise DataError('trusted oracle must return aligned V2 steps for each prefix')
            step=obs['steps'][-1]
            observed={k:step[k] for k in ('output','error','status','events','effects') if k in step}
            return identity(observed)
    state=random.getstate()
    sul=ReferenceSUL()
    try:
        random.seed(seed)
        eq=RandomWalkEqOracle(input_alphabet,sul,num_steps=min(max_queries,50),
                              reset_prob=0.3,reset_after_cex=True)
        model=run_Lstar(input_alphabet,sul,eq,automaton_type='mealy',
                        cache_and_non_det_check=True,print_level=0)
    finally:
        random.setstate(state)
    observed=[]
    for machine_state in model.states:
        trans=getattr(machine_state,'transitions',{})
        fun=getattr(machine_state,'output_fun',{})
        for key,destination in sorted(trans.items(),key=lambda x:x[0]):
            observed.append({'from':str(machine_state.state_id),'action':action_id(alphabet[key]),
                             'to':str(destination.state_id),'output_fingerprint':str(fun.get(key,''))})
    return {'schema_version':'1.0','mode':'aalpy-Lstar-trusted','transitions':observed,
            'learned_states':len(model.states),'membership_queries':sul.queries,'seed':seed,
            'source_command_sha256':hashlib.sha256(command_file.read_bytes()).hexdigest(),
            'completeness':'active inferred hypothesis only; finite membership and random-walk equivalence queries cannot prove full parity',
            'warning':'AALpy runtime/external trusted oracle required, no filesystem/network sandbox in the adapter'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['offline','active','aalpy'])
    p.add_argument('--corpus',type=Path)
    p.add_argument('--alphabet',type=Path)
    p.add_argument('--argv-file',type=Path)
    p.add_argument('--cwd',type=Path)
    p.add_argument('--depth',type=int,default=2)
    p.add_argument('--seed',type=int,default=0)
    p.add_argument('--max-queries',type=int,default=100)
    p.add_argument('--execute-authorized',action='store_true')
    p.add_argument('--reset-confirmed',action='store_true')
    p.add_argument('--capture-corpus',type=Path)
    p.add_argument('-o','--output',required=True,type=Path)
    a=p.parse_args(argv)
    try:
        alphabet=None
        if a.alphabet:
            alphabet=strict_json(a.alphabet.read_text('utf-8'))
            if not isinstance(alphabet,list):raise DataError('alphabet must be JSON array')
        if a.mode=='aalpy':
            if not (a.argv_file and a.cwd and alphabet):raise DataError('AALpy needs --alphabet, --argv-file, --cwd')
            result=aalpy_learn(alphabet,a.argv_file,a.cwd,authorized=a.execute_authorized,
                               reset_confirmed=a.reset_confirmed,max_queries=a.max_queries,seed=a.seed)
            write_exclusive(a.output,json.dumps(result,ensure_ascii=False,indent=2)+'\n',[a.alphabet,a.argv_file])
            return 0
        if a.mode=='offline':
            if not a.corpus:raise DataError('--corpus required')
            rows=load_corpus(a.corpus)
        else:
            if not (a.argv_file and a.cwd and alphabet):
                raise DataError('--argv-file, --cwd and --alphabet required for active mode')
            captured=active_capture(alphabet,a.argv_file,a.cwd,depth=a.depth,max_queries=a.max_queries,
                                    execute_authorized=a.execute_authorized,reset_confirmed=a.reset_confirmed)
            if not a.capture_corpus:raise DataError('--capture-corpus required for active mode')
            input_paths=[v for v in (a.corpus,a.alphabet,a.argv_file) if v]
            if any(a.output.resolve()==v.resolve() or a.capture_corpus.resolve()==v.resolve() for v in input_paths) or a.output.resolve()==a.capture_corpus.resolve():
                raise DataError('output aliases input or corpus')
            write_exclusive(a.capture_corpus, ''.join(canon(r)+'\n' for r in captured),input_paths)
            rows={row['id']:row for row in captured if row['runner_status']=='ok' and 'steps' in row['observation']}
        result=infer(rows,alphabet)
        result['evidence']={'input_corpus_sha256':hashlib.sha256(a.corpus.read_bytes()).hexdigest() if a.corpus else None,
                            'capture_corpus':str(a.capture_corpus) if a.mode=='active' else None,
                            'runtime_authorized_trusted':a.mode=='active'}
        excluded=[v for v in (a.corpus,a.alphabet,a.argv_file,a.capture_corpus) if v]
        if any(a.output.resolve()==v.resolve() for v in excluded):raise DataError('output aliases input')
        write_exclusive(a.output,json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',excluded)
        return 0 if not result['conflicts'] and not result['skipped'] else 3
    except (DataError,ValueError,OSError) as exc:
        print(json.dumps({'error':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
