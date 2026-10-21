import { test } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import vm from 'node:vm';
import { createHash, webcrypto } from 'node:crypto';

const source = await fs.readFile('tools/build/pwa/service-worker.js', 'utf8');
const tick = async () => { for (let i = 0; i < 20; i++) await new Promise(resolve => setImmediate(resolve)); };
async function until(predicate) {
  const deadline = Date.now() + 3000;
  while (!predicate() && Date.now() < deadline) await new Promise(resolve => setTimeout(resolve, 1));
  assert.ok(predicate(), 'download state did not settle');
}
function harness() {
  const files = Array.from({ length: 6 }, (_, i) => ({ path: `part-${i}`, bytes: 4, sha256: createHash('sha256').update('data').digest('hex') }));
  const handlers = new Map(), requests = [], writes = [], stores = new Map();
  const caches = {
    async open(name) {
      if (!stores.has(name)) stores.set(name, new Map());
      const cache = stores.get(name);
      return { match: async key => cache.get(String(key)), put: async (key, value) => { writes.push(String(key)); cache.set(String(key), value); } };
    },
    delete: async name => stores.delete(name), keys: async () => [...stores.keys()],
  };
  const self = { location: { href: 'https://games.test/Rain/service-worker.js' }, clients: { matchAll: async () => [], claim: async () => {} }, addEventListener: (name, callback) => handlers.set(name, callback) };
  const fetch = (request, options) => new Promise((resolve, reject) => requests.push({ request, signal: options?.signal ?? request.signal, resolve, reject }));
  vm.runInNewContext(source.replace('/* BUILD_CONFIG */', JSON.stringify({ revision: 'new', files })), { self, caches, fetch, crypto: webcrypto, Request, Response, URL, AbortController });
  let installation;
  handlers.get('install')({ waitUntil: promise => { installation = promise; } });
  return { requests, writes, stores, installation };
}

test('downloads at most two files together and publishes completeness only after all six verify', async () => {
  const f = harness(); await tick();
  assert.equal(f.requests.length, 2);
  for (let batch = 0; batch < 3; batch++) {
    await until(() => f.requests.length >= (batch + 1) * 2);
    assert.equal(f.requests.length, (batch + 1) * 2);
    assert.ok(!f.writes.some(path => path.endsWith('__rain_complete__')));
    for (const request of f.requests.slice(batch * 2, batch * 2 + 2)) request.resolve(new Response('data'));
  }
  await f.installation;
  assert.equal(f.writes.length, 7);
  assert.ok(f.writes.at(-1).endsWith('__rain_complete__'));
});

test('first failure aborts sibling requests, drains them, and removes only the failed candidate', async () => {
  const f = harness(); let settled = false;
  const result = f.installation.then(() => { throw new Error('installation unexpectedly succeeded'); }, error => { settled = true; return error; });
  await tick(); assert.equal(f.requests.length, 2);
  f.stores.set('rain-pwa:/Rain/:old', new Map()); f.stores.set('rain-pwa:/Other/:old', new Map());
  f.requests[0].reject(new Error('network lost')); await tick();
  assert.equal(f.requests[1].signal.aborted, true);
  assert.equal(settled, false);
  // Simulate a response that arrived just as cancellation happened.
  f.requests[1].resolve(new Response('data'));
  assert.match((await result).message, /network lost/);
  assert.equal(f.requests.length, 2); assert.equal(f.writes.length, 0);
  assert.equal(f.stores.has('rain-pwa:/Rain/:new'), false);
  assert.ok(f.stores.has('rain-pwa:/Rain/:old')); assert.ok(f.stores.has('rain-pwa:/Other/:old'));
});
