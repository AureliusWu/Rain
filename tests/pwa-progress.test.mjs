import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import { webcrypto, createHash } from 'node:crypto';
const source=await fs.readFile('tools/build/pwa/service-worker.js','utf8');
async function fixture(corrupt=false){
 const payloads=new Map([['index.html','real index'],['renpy.wasm','real wasm']]);
 const build={revision:'candidate',files:[...payloads].map(([path,raw])=>({path,bytes:Buffer.byteLength(raw),sha256:createHash('sha256').update(raw).digest('hex')}))};
 const stores=new Map([['rain-pwa:/Rain/:old',new Map([['old',new Response('complete old')]])],['rain-pwa:/Other/:keep',new Map()]]);
 const events=new Map(),messages=[];const cache={open:async name=>{if(!stores.has(name))stores.set(name,new Map());const data=stores.get(name);return{match:async key=>data.get(String(key)),put:async(key,value)=>{data.set(String(key),value);}};},delete:async name=>stores.delete(name),keys:async()=>[...stores.keys()]};
 const clients=[{url:'https://games.test/Rain/',postMessage:message=>messages.push(structuredClone(message))},{url:'https://games.test/Other/',postMessage:()=>assert.fail('cross-scope progress leak')}];
 const self={location:{href:'https://games.test/Rain/service-worker.js'},clients:{matchAll:async()=>clients,claim:async()=>{}},addEventListener:(name,fn)=>events.set(name,fn)};
 vm.runInNewContext(source.replace('/* BUILD_CONFIG */',JSON.stringify(build)),{self,caches:cache,crypto:webcrypto,URL,Request,Response,fetch:async request=>{const path=new URL(request.url).pathname.split('/').at(-1);return new Response(corrupt&&path==='renpy.wasm'?'wrong wasm':payloads.get(path));},Uint8Array,Map});
 const fire=async(name,data={})=>{let promise;events.get(name)({...data,waitUntil:p=>{promise=p;}});await promise;};
 return{fire,stores,messages,build};
}
test('counts bytes only after verifying hashes and committing each file to its own cache',async()=>{
 const f=await fixture();await f.fire('install');
 assert.deepEqual(f.messages.map(x=>x.completedFiles),[0,1,2]);
 assert.deepEqual(f.messages.map(x=>x.verifiedBytes),[0,10,19]);
 assert.ok(f.messages.every(x=>x.totalBytes===19&&x.totalFiles===2&&!x.failed));
 assert.ok(f.stores.get('rain-pwa:/Rain/:candidate').has('https://games.test/Rain/__rain_complete__'));
 let status;await f.fire('message',{data:{type:'RAIN_OFFLINE_STATUS'},ports:[{postMessage:value=>{status=value;}}]});
 assert.equal(status.ready,true);assert.equal(status.verifiedBytes,19);
 assert.ok(f.stores.has('rain-pwa:/Rain/:old'));await f.fire('activate');
 assert.equal(f.stores.has('rain-pwa:/Rain/:old'),false);assert.ok(f.stores.has('rain-pwa:/Other/:keep'));
});
test('a corrupt file reports failure, never counts its bytes and preserves the complete old build',async()=>{
 const f=await fixture(true);await assert.rejects(()=>f.fire('install'),/Build changed/);
 assert.equal(f.messages.at(-1).failed,true);assert.equal(f.messages.at(-1).completedFiles,1);assert.equal(f.messages.at(-1).verifiedBytes,10);
 assert.equal(f.stores.has('rain-pwa:/Rain/:candidate'),false);assert.ok(f.stores.has('rain-pwa:/Rain/:old'));
});
