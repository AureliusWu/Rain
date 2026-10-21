// Actual Chromium service-worker delivery fixture; this does not boot Ren'Py/WASM.
import http from 'node:http';
import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { chromium } from 'playwright';

const template = await fs.readFile('tools/build/pwa/service-worker.js', 'utf8');
const payloads = new Map(Array.from({ length: 6 }, (_, index) => [`part-${index}`, `verified payload ${index}`]));
const files = [...payloads].map(([path, body]) => ({ path, bytes: Buffer.byteLength(body), sha256: createHash('sha256').update(body).digest('hex') }));
let revision = 'fixture-old', active = 0, peak = 0;
const server = http.createServer((request, response) => {
  const name = new URL(request.url, 'http://fixture').pathname.replace('/Rain/', '');
  response.setHeader('Cache-Control', 'no-store');
  if (name === 'service-worker.js') {
    response.setHeader('Content-Type', 'text/javascript');
    response.end(template.replace('/* BUILD_CONFIG */', JSON.stringify({ revision, files }))); return;
  }
  if (payloads.has(name)) {
    active++; peak = Math.max(peak, active);
    response.once('close', () => active--);
    const body = revision === 'fixture-bad' && name === 'part-0' ? 'corrupt' : payloads.get(name);
    setTimeout(() => response.end(body), name === 'part-0' ? 30 : 100); return;
  }
  response.setHeader('Content-Type', 'text/html');
  response.end('<!doctype html><title>Worker delivery fixture</title><script>window.progress=[];navigator.serviceWorker.addEventListener("message",e=>progress.push(e.data));navigator.serviceWorker.register("./service-worker.js",{scope:"./",updateViaCache:"none"}).then(r=>window.owner=r);</script>');
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const browser = await chromium.launch({ headless: true, ...(process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE ? { executablePath: process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE } : {}) });
const context = await browser.newContext();
const page = await context.newPage(), errors = [], checks = [];
page.on('pageerror', error => errors.push(error.message));
const origin = `http://127.0.0.1:${server.address().port}`, prefix = 'rain-pwa:/Rain/:';
try {
  await page.goto(origin + '/Rain/');
  await page.waitForFunction(() => window.owner?.active?.state === 'activated');
  assert.equal(peak, 2); checks.push('actual install runs at most two downloads together');
  assert.deepEqual(await page.evaluate(() => progress.map(row => row.completedFiles)), [0, 1, 2, 3, 4, 5, 6]);
  checks.push('real progress messages count each verified file in completion order');
  await page.evaluate(async () => { const sibling = await caches.open('rain-pwa:/Other/:keep'); await sibling.put('/Other/sentinel', new Response('keep')); });
  revision = 'fixture-bad';
  await page.evaluate(() => owner.update());
  await page.waitForFunction(() => progress.some(row => row.revision === 'fixture-bad' && row.failed));
  await page.waitForFunction(async () => !(await caches.keys()).includes('rain-pwa:/Rain/:fixture-bad'));
  assert.equal(await page.evaluate(() => owner.active.state), 'activated');
  assert.ok((await page.evaluate(() => caches.keys())).includes(prefix + 'fixture-old'));
  checks.push('corrupt parallel update cleans its candidate and keeps the active complete build');
  revision = 'fixture-new';
  await page.evaluate(() => owner.update());
  await page.waitForFunction(() => owner.waiting?.state === 'installed');
  assert.ok((await page.evaluate(() => caches.keys())).includes(prefix + 'fixture-old'));
  checks.push('successful retry waits for old reading windows to close');
  await page.close();
  const reopened = await context.newPage();
  await reopened.goto(origin + '/Rain/');
  await reopened.waitForFunction(async () => {
    const names = await caches.keys();
    return names.includes('rain-pwa:/Rain/:fixture-new') && !names.includes('rain-pwa:/Rain/:fixture-old');
  });
  assert.ok((await reopened.evaluate(() => caches.keys())).includes('rain-pwa:/Other/:keep'));
  checks.push('activation removes only the old cache in this exact application scope');
  assert.deepEqual(errors, []);
  await fs.mkdir('reports/pwa-downloads', { recursive: true });
  const report = { status: 'passed', scope: 'actual Chromium worker fixture; no RenPy/WASM execution', checks, errors, peakDownloads: peak };
  await fs.writeFile('reports/pwa-downloads/browser.json', JSON.stringify(report, null, 2) + '\n');
  console.log(JSON.stringify(report, null, 2));
} finally { await browser.close(); await new Promise(resolve => server.close(resolve)); }
