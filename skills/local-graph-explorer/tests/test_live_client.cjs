/* Execute the exact production live-action block with fake transport and DOM.
 * This tests client options/control flow, not browser origin policy or a server.
 */
'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync(process.argv[2],'utf8');
const start=source.indexOf("  const profile=VIEWER_CONFIG.security_profile||'offline';");
const end=source.indexOf('  if(window.LocalGraphJourney',start);
assert.ok(start>=0&&end>start,'live action boundary must exist');
const code=source.slice(start,end);
let count=0;
function response(chunks, status='pass'){
  let i=0,canceled=false;
  const values=chunks||[new TextEncoder().encode(JSON.stringify({status,nodes:3}))];
  return {ok:true,body:{getReader(){return {async read(){return i<values.length?{done:false,value:values[i++]}:{done:true};},async cancel(){canceled=true;}};}},canceled:()=>canceled};
}
function setup({profile='local-live',origin='http://127.0.0.1:8765',fetchImpl}={}){
  const elements={};
  const el=id=>elements[id]||(elements[id]={textContent:'',value:'',hidden:true,disabled:false});
  el('local-graph-session').textContent=JSON.stringify({token:'x'.repeat(43)});
  const calls=[],timers=new Map(),events={},messages=[],loads=[];
  const location=new URL(origin);
  const context={VIEWER_CONFIG:{security_profile:profile},$:el,location,URL,TextEncoder,TextDecoder,AbortController,
    setTimeout(fn){timers.set(1,fn);return 1;},clearTimeout(id){timers.delete(id);},addEventListener(name,fn){events[name]=fn;},
    message:value=>messages.push(value),load:value=>loads.push(value),
    fetch:async(url,options)=>{calls.push({url,options});return fetchImpl?fetchImpl(url,options,{timers,events}):response();}};
  vm.runInNewContext(code,context,{timeout:1000});
  return {elements,el,calls,timers,events,messages,loads,click:()=>el('live-button').onclick?.()};
}
async function test(name,fn){await fn();count++;console.log('PASS '+name);}
(async()=>{
  await test('explicit profile and loopback origin required',async()=>{
    for(const options of [{profile:'offline'},{profile:'extended'},{origin:'https://example.invalid'},{origin:'http://localhost:8765'},{origin:'https://127.0.0.1:8765'}]){
      const x=setup(options);await x.click();assert.equal(x.calls.length,0);assert.equal(x.el('live-panel').hidden,true);
    }
  });
  await test('origin-based URL, no redirects/cookies/referrer and explicit POST',async()=>{
    const x=setup();x.el('live-query').value=JSON.stringify({operation:'stats',baseURI:'https://example.invalid'});await x.click();
    assert.equal(x.calls.length,1);const {url,options}=x.calls[0];assert.equal(url,'http://127.0.0.1:8765/api/query');
    for(const [key,value] of Object.entries({method:'POST',mode:'same-origin',credentials:'omit',redirect:'error',referrerPolicy:'no-referrer',cache:'no-store'}))assert.equal(options[key],value);
    assert.equal(options.headers['X-Local-Graph-Token'],'x'.repeat(43));assert.ok(options.signal);assert.equal(x.el('local-graph-session').textContent,'{}');assert.equal(x.timers.size,0);
  });
  await test('oversized request never reaches transport',async()=>{const x=setup();x.el('live-query').value=JSON.stringify({operation:'search',term:'a'.repeat(65536)});await x.click();assert.equal(x.calls.length,0);assert.match(x.messages.at(-1),/request budget/);});
  await test('invalid JSON never reaches transport',async()=>{const x=setup();x.el('live-query').value='{';await x.click();assert.equal(x.calls.length,0);assert.equal(x.el('live-button').disabled,false);});
  await test('oversized response cancels stream without loading data',async()=>{const r=response([new Uint8Array(8*1024*1024+1)]);const x=setup({fetchImpl:()=>r});await x.click();assert.ok(r.canceled());assert.equal(x.loads.length,0);assert.match(x.messages.at(-1),/response exceeds/);});
  await test('transport failures leave no token in UI message',async()=>{const x=setup({fetchImpl:()=>{throw new TypeError('Fetch refused');}});await x.click();assert.deepEqual(x.messages,['Fetch refused']);assert.equal(x.el('live-button').disabled,false);});
  await test('timeout abort signal and cleanup',async()=>{let signal;const x=setup({fetchImpl:(_url,options,{timers})=>{signal=options.signal;timers.get(1)();throw Object.assign(new Error('aborted'),{name:'AbortError'});}});await x.click();assert.ok(signal.aborted);assert.match(x.messages.at(-1),/timed out/);assert.equal(x.timers.size,0);});
  await test('page hide cancels active request',async()=>{let signal;const x=setup({fetchImpl:(_url,options,{events})=>{signal=options.signal;events.pagehide();throw Object.assign(new Error('aborted'),{name:'AbortError'});}});await x.click();assert.ok(signal.aborted);assert.match(x.messages.at(-1),/canceled/);});
  await test('only one in-flight query',async()=>{let release;const x=setup({fetchImpl:()=>new Promise(resolve=>{release=resolve;})});const first=x.click();await x.click();assert.equal(x.calls.length,1);release(response());await first;assert.equal(x.el('live-button').disabled,false);});
  console.log(JSON.stringify({status:'pass',cases:count,scope:'mocked transport, production client block'}));
})().catch(error=>{console.error(error);process.exitCode=1;});
