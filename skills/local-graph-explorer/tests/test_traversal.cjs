// Frozen deterministic graph semantics tests. Usage: node test_traversal.cjs asset.js
const assert = require('node:assert/strict');
const T = require(process.argv[2]);
const node = id => ({id, kind:'stage', label:id});
const edge = (id,s,t,d=true) => ({id,source:s,target:t,relation:'precedes',directed:d});
const N=['a','b','c','d','x'].map(node), E=[edge('ab','a','b'),edge('ac','a','c'),edge('bd','b','d'),edge('cd','c','d')];
const build=(nodes=N,edges=E,opts={})=>T.build(nodes,edges,opts);
let tests=0;function test(name,f){f();tests++;console.log('PASS '+name);}
test('parallel dependency layers',()=>{const p=build();assert.deepEqual(p.steps.map(s=>s.nodes),[['a','x'],['b','c'],['d']]);assert.deepEqual(p.starts,['a','x']);assert.deepEqual(p.ends,['d','x']);});
test('seed excludes disconnected nodes',()=>{const p=build(N,E,{start:'a'});assert.equal(p.nodes.length,4);assert.equal(p.excluded_nodes,1);});
test('upstream reverses traversal not stored edges',()=>{const p=build(N,E,{start:'d',mode:'upstream'});assert.deepEqual(p.steps.map(s=>s.nodes),[['d'],['b','c'],['a']]);assert.deepEqual(E[0],edge('ab','a','b'));});
test('exact path tie break',()=>{const p=build(N,E,{mode:'path',start:'a',target:'d'});assert.deepEqual(p.steps.map(s=>s.nodes),[['a'],['b'],['d']]);assert.deepEqual(p.steps[2].edges,['bd']);});
test('unreachable path fails closed',()=>{assert.throws(()=>build(N,E,{mode:'path',start:'d',target:'a'}),/path/i);});
test('same start end',()=>{const p=build(N,E,{mode:'path',start:'a',target:'a'});assert.equal(p.steps.length,1);assert.deepEqual(p.steps[0].edges,[]);});
test('cycle becomes explicit component',()=>{const p=build(N,[...E,edge('db','d','b')],{start:'a'});assert.equal(p.cycles.length,1);assert.deepEqual(p.cycles[0],['b','d']);assert.equal(p.steps.length,3);});
test('self loop is cycle',()=>{const p=build([node('a')],[edge('loop','a','a')]);assert.deepEqual(p.cycles,[['a']]);assert.equal(p.steps.length,1);});
test('undirected not fabricated into execution',()=>{const p=build([node('a'),node('b')],[edge('ab','a','b',false)]);assert.equal(p.undirected_excluded,1);assert.equal(p.steps.length,1);});
test('empty graph',()=>{assert.deepEqual(build([],[]).steps,[]);});
test('array order invariant',()=>{assert.deepEqual(build(N.slice().reverse(),E.slice().reverse()),build());});
test('missing endpoint and duplicate reject',()=>{assert.throws(()=>build(N,[edge('bad','a','z')]));assert.throws(()=>build([...N,node('a')],E));assert.throws(()=>build(N,[...E,E[0]]));});
test('limits fail explicitly',()=>{assert.throws(()=>build(Array.from({length:501},(_,i)=>node('n'+i)),[]),/budget|limit/i);});
test('unknown modes and seeds reject',()=>{assert.throws(()=>build(N,E,{mode:'wrong'}));assert.throws(()=>build(N,E,{start:'unknown'}));});
test('all real parallel relationships preserved',()=>{const p=build(N,[...E,edge('ab2','a','b')],{start:'a'});assert.deepEqual(p.steps[1].edges,['ab','ab2','ac']);});
console.log(JSON.stringify({passed:tests,failed:0}));
