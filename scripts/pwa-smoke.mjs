import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {get, waitNative, clickId, startNarrative, verifyReadHistorySearch, verifyReadBookmarks, verifyPlayerHelp, visibleNarration} from './pwa-native-browser.mjs';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const root = path.resolve('dist/web');
const reports = path.resolve('reports/pwa');
const expectedVersion = (await fs.readFile('VERSION', 'utf8')).trim();
const buildMetadata = JSON.parse(await fs.readFile('reports/web-build.json', 'utf8'));
assert.equal(buildMetadata.version, expectedVersion);
// v1.6.0 used 99,243,438 bytes; the two original OGG loops add 3,057,195.
// Keep a bounded 105 MB delivery budget without reducing the music quality.
const offlineByteBudget = 105_000_000;
assert.ok(Number.isSafeInteger(buildMetadata.offline_bytes) && buildMetadata.offline_bytes > 0);
assert.ok(buildMetadata.offline_bytes < offlineByteBudget,
    `Offline payload ${buildMetadata.offline_bytes} exceeds ${offlineByteBudget} bytes`);
await fs.mkdir(reports, {recursive:true});
// Refuse a truncated or stale expanded build before asking the WASM engine to boot.
const workerText = await fs.readFile(path.join(root, 'service-worker.js'), 'utf8');
const deliveredCatalog = JSON.parse(workerText.match(/^const BUILD = (.*);$/m)[1]);
assert.equal(deliveredCatalog.version, expectedVersion);
for (const file of deliveredCatalog.files) {
    const raw = await fs.readFile(path.join(root, file.path));
    assert.equal(raw.length, file.bytes, `Expanded build length changed: ${file.path}`);
    assert.equal(crypto.createHash('sha256').update(raw).digest('hex'), file.sha256, `Expanded build bytes changed: ${file.path}`);
}

const mime = {'.html':'text/html', '.js':'text/javascript', '.json':'application/json', '.wasm':'application/wasm', '.png':'image/png', '.jpg':'image/jpeg'};
const requests = [];
let failFile = null;
let upgradeWorker = false;
const server = http.createServer(async (request, response) => {
    const pathname = decodeURIComponent(new URL(request.url, 'http://local').pathname);
    requests.push(pathname);
    if (pathname === '/foreign-worker.js') {
        response.writeHead(200, {'Content-Type':'text/javascript', 'Cache-Control':'no-cache'});
        response.end('self.addEventListener("activate",e=>e.waitUntil(self.clients.claim()));self.addEventListener("message",e=>e.ports[0]?.postMessage({ready:true,revision:"foreign-app"}));'); return;
    }
    if (pathname === '/foreign-fixture.html') {
        response.writeHead(200, {'Content-Type':'text/html'});
        response.end('<script>navigator.serviceWorker.register("/foreign-worker.js",{scope:"/"})</script>'); return;
    }
    if (!pathname.startsWith('/Rain/') && !pathname.startsWith('/nested/Rain/')) { response.writeHead(404); response.end(); return; }
    const relative = pathname.replace(/^\/(nested\/)?Rain\//, '') || 'index.html';
    const file = path.resolve(root, relative);
    if (!file.startsWith(root + path.sep) || relative === failFile) { response.writeHead(503); response.end('Unavailable'); return; }
    try {
        let data = await fs.readFile(file);
        if (upgradeWorker && relative === 'service-worker.js')
            data = Buffer.from(data.toString().replace(/"revision":\s*"[^"]+"/, '"revision":"test-complete-update"'));
        response.writeHead(200, {'Content-Type':mime[path.extname(file)] || 'application/octet-stream', 'Cache-Control':'no-cache'});
        response.end(data);
    } catch { response.writeHead(404); response.end(); }
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const launch = {headless:true, args:process.env.PLAYWRIGHT_CHROMIUM_ARGS ? JSON.parse(process.env.PLAYWRIGHT_CHROMIUM_ARGS) : ['--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader']};
if (process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE) launch.executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE;
const browser = await chromium.launch(launch);
const errors = [];
const runtimeConsole = [];
const samples = [];
const checks = [];
async function boot(page, base) {
    const start = performance.now();
    await page.goto(origin + base, {waitUntil:'domcontentloaded'});
    try { await page.waitForFunction(() => !document.getElementById('presplash'), null, {timeout:120000}); }
    catch(error) {
        await page.screenshot({path:path.join(reports,'boot-failure.png')});
        await fs.writeFile(path.join(reports,'boot-failure.json'),JSON.stringify({console:runtimeConsole.slice(-100),body:await page.locator('body').innerText(),errors},null,2));
        throw error;
    }
    await page.waitForFunction(() => window.rainOfflineReady === true, null, {timeout:120000});
    await waitNative(page,'bool(renpy.get_screen("main_menu"))');
    await waitNative(page,'not any(renpy.get_ongoing_transition(layer) for layer in (None, "master", "screens"))');
    assert.equal(await get(page, 'config.version'), expectedVersion);
    assert.equal(await get(page, 'bool(renpy.get_screen("main_menu"))'), true);
    const sizes=await page.locator('#offlineProgress').evaluate(node=>[Number(node.dataset.verifiedBytes),Number(node.dataset.totalBytes)]);
    assert.deepEqual(sizes,[buildMetadata.offline_bytes,buildMetadata.offline_bytes]);
    return Math.round(performance.now() - start);
}
const hash = data => crypto.createHash('sha256').update(data).digest('hex');
const shot = async (page, name) => {
    const file = path.join(reports, name + '.png');
    await page.screenshot({path:file});
    return {name,sha256:hash(await fs.readFile(file))};
};
const screenshots = [];
try {
    const context = await browser.newContext({viewport:{width:1440,height:900}, acceptDownloads:true});
    const page = await context.newPage();
    page.on('pageerror',error => errors.push(error.message));
    page.on('console',message => runtimeConsole.push(message.text()));
    for (let iteration=0;iteration<3;iteration++) {
        samples.push({mode:iteration ? 'cached_reopen':'first_install',milliseconds:await boot(page, '/Rain/')});
        console.log('Native PWA boot',iteration,samples.at(-1).milliseconds);
    }
    screenshots.push(await shot(page,'desktop-main-menu'));
    const manifest = await page.evaluate(async () => (await fetch('manifest.json')).json());
    assert.equal(manifest.scope, './'); assert.equal(manifest.start_url, './index.html'); assert.equal(manifest.id, './');
    const installability = await context.newCDPSession(page);
    await installability.send('Page.enable');
    const manifestResult = await installability.send('Page.getAppManifest');
    assert.equal(manifestResult.errors.length, 0);
    checks.push('manifest parsed and app-scoped start URL; complete offline marker');
    await verifyPlayerHelp(page, path.join(reports, 'desktop-title-help.png'));
    await startNarrative(page);
    await verifyPlayerHelp(page, path.join(reports, 'desktop-reading-help.png'));
    checks.push('desktop help opens from title and reading menus and preserves native reading state');
    await verifyReadHistorySearch(page, path.join(reports, 'desktop-history-search.png'));
    checks.push('actual native history search, Chinese input, empty/reset states and preserved read position');
    const bookmarked = await verifyReadBookmarks(page, path.join(reports, 'desktop-bookmarks.png'));
    checks.push('actual read bookmark, chapter filter, removal/re-add and unchanged native state');
    assert.equal(await get(page,'current_scene'),'p00_entry');
    assert.equal(await get(page,'bool(renpy.get_screen("say"))'),true);
    screenshots.push(await shot(page,'desktop-story'));
    checks.push('actual Start click and native narration');
    await clickId(page,'quick_menu','save_open');
    await clickId(page,'save','slot_1');
    await waitNative(page,'renpy.can_load("1-1")');
    await clickId(page,'save','game_return');
    const savedScene = await get(page,'current_scene');
    const savedText = await get(page,visibleNarration);
    checks.push('actual native Save screen writes slot 1');
    // Export uses Ren'Py's official save archive API, including persistent data.
    await page.locator('#ContextButton').click();
    const downloadPromise = page.waitForEvent('download');
    await page.getByText('导出存档',{exact:true}).click();
    const download = await downloadPromise;
    await download.saveAs(path.join(reports,'native-web-saves.zip'));
    const exported = await fs.readFile(path.join(reports,'native-web-saves.zip'));
    assert.equal(exported.readUInt32LE(0),0x04034b50);
    checks.push('native export save ZIP produced by actual browser control');
    await page.locator('#ContextButton').click();
    await context.setOffline(true);
    assert.ok(await boot(page,'/Rain/') < 120000);
    assert.equal(await get(page,'config.version'),expectedVersion);
    assert.equal(await get(page,`rain_is_bookmarked(${JSON.stringify(bookmarked)})`),true);
    assert.equal(await get(page,'renpy.can_load("1-1")'),true);
    await startNarrative(page);
    assert.equal(await get(page,'current_scene'),'p00_entry');
    screenshots.push(await shot(page,'offline-story'));
    await verifyReadHistorySearch(page, path.join(reports, 'offline-history-search.png'));
    checks.push('native history search remains usable during a real offline session');
    checks.push('offline reload boots complete native WASM and starts narrative');
    await context.setOffline(false);
    for (const size of [{width:412,height:915},{width:568,height:320},{width:844,height:390}]) {
        await page.setViewportSize(size);
        await page.reload({waitUntil:'domcontentloaded'});
        await page.waitForFunction(()=>!document.getElementById('presplash'),null,{timeout:120000});
        assert.equal(await get(page,'config.version'),expectedVersion);
        assert.equal(await page.locator('#orientationHint').isVisible(),size.height>size.width);
        screenshots.push(await shot(page,`${size.width}x${size.height}`));
    }
    checks.push('412x915, 568x320 and 844x390 native display boots');
    await page.setViewportSize({width:1440,height:900});
    await boot(page,'/Rain/');
    await startNarrative(page);
    const oldRevision = await page.evaluate(()=>window.rainOfflineRevision);
    const oldScene = await get(page,'current_scene');
    const oldText = await get(page,visibleNarration);
    await page.evaluate(async()=>{
        await (await caches.open('foreign-app-survives')).put('/foreign-fixture.html',new Response('foreign data'));
        await (await caches.open('rain-pwa:/Other/:retained')).put('/Other/fixture',new Response('other scope data'));
    });
    upgradeWorker = true;
    await page.evaluate(async()=>{const registration=await navigator.serviceWorker.getRegistration();await registration.update();});
    await page.waitForFunction(async()=>Boolean((await navigator.serviceWorker.getRegistration())?.waiting),null,{timeout:120000});
    assert.equal(await page.evaluate(()=>window.rainOfflineRevision),oldRevision);
    assert.equal(await get(page,'current_scene'),oldScene);
    assert.equal(await get(page,visibleNarration),oldText);
    await page.waitForFunction(()=>document.getElementById('offlineStatus').textContent.includes('新版已准备'),null,{timeout:10000});
    assert.match(await page.locator('#offlineStatus').textContent(),/新版已准备/);
    checks.push('complete update waits while old WASM narrative keeps its original controller and state');
    await page.close();
    const upgradedPage=await context.newPage(); await boot(upgradedPage,'/Rain/');
    assert.equal(await upgradedPage.evaluate(()=>window.rainOfflineRevision),'test-complete-update');
    const scopedKeys=await upgradedPage.evaluate(()=>caches.keys());
    assert.ok(!scopedKeys.some(key=>key===`rain-pwa:/Rain/:${oldRevision}`));
    assert.ok(scopedKeys.includes('foreign-app-survives'));
    assert.ok(scopedKeys.includes('rain-pwa:/Other/:retained'));
    checks.push('closing old windows activates complete update; prior own cache removed and unrelated/other-scope caches retained');
    await context.close();
    upgradeWorker = false;
    const imported = await browser.newContext({viewport:{width:1440,height:900}});
    const importedPage = await imported.newPage(); await boot(importedPage,'/Rain/');
    assert.equal(await get(importedPage,'renpy.can_load("1-1")'),false);
    await importedPage.locator('#ID_SavegamesImport').setInputFiles(path.join(reports,'native-web-saves.zip'));
    await waitNative(importedPage,'renpy.can_load("1-1")');
    await clickId(importedPage,'main_menu','load_open');
    await clickId(importedPage,'load','slot_1');
    if(await get(importedPage,'bool(renpy.get_screen("confirm"))')) await clickId(importedPage,'confirm','confirm_yes');
    await waitNative(importedPage,`current_scene == ${JSON.stringify(savedScene)}`);
    await waitNative(importedPage,`${visibleNarration} == ${JSON.stringify(savedText)}`);
    assert.equal(await get(importedPage,`rain_is_bookmarked(${JSON.stringify(bookmarked)})`),true);
    screenshots.push(await shot(importedPage,'imported-native-save'));
    checks.push('real export ZIP imported into fresh browser context and actual Load restores saved scene');
    await imported.close();
    const parentScope = await browser.newContext();
    const parentPage = await parentScope.newPage();
    await parentPage.goto(origin+'/foreign-fixture.html');
    await parentPage.waitForFunction(()=>Boolean(navigator.serviceWorker.controller),null,{timeout:30000});
    await boot(parentPage,'/Rain/');
    assert.notEqual(await parentPage.evaluate(()=>window.rainOfflineRevision),'foreign-app');
    assert.equal(await parentPage.evaluate(()=>navigator.serviceWorker.controller.scriptURL),origin+'/Rain/service-worker.js');
    checks.push('unrelated parent-scope worker cannot announce this application offline-ready');
    await parentScope.close();
    const nested = await browser.newContext({viewport:{width:844,height:390}});
    const nestedPage = await nested.newPage();
    await boot(nestedPage,'/nested/Rain/');
    await nested.setOffline(true); await boot(nestedPage,'/nested/Rain/');
    checks.push('nested subpath fresh install and complete offline reopen');
    await nested.close();
    const mobile = await browser.newContext({viewport:{width:412,height:915},isMobile:true,hasTouch:true,
        userAgent:'Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36'});
    const mobilePage = await mobile.newPage();
    for (const size of [{width:412,height:915},{width:568,height:320},{width:844,height:390}]) {
        await mobilePage.setViewportSize(size);
        await boot(mobilePage,'/Rain/');
        assert.equal(await get(mobilePage,'renpy.variant("touch")'),true);
        await verifyPlayerHelp(mobilePage,path.join(reports,`touch-${size.width}x${size.height}-title-help.png`));
        await startNarrative(mobilePage);
        await verifyPlayerHelp(mobilePage,path.join(reports,`touch-${size.width}x${size.height}-reading-help.png`));
    }
    checks.push('touch help at 412x915, 568x320 and 844x390 opens from title and reading menus without advancing');
    await mobile.close();
    const failed = await browser.newContext(); const failedPage = await failed.newPage();
    failFile = 'renpy.wasm';
    await failedPage.goto(origin + '/Rain/');
    await failedPage.waitForTimeout(5000);
    const partial = await failedPage.evaluate(async () => {
        for (const name of await caches.keys()) {
            const cache = await caches.open(name);
            if ((await cache.keys()).some(key => key.url.endsWith('__rain_complete__'))) return true;
        }
        return false;
    });
    assert.equal(partial,false);
    checks.push('missing engine resource cannot produce an offline-ready marker');
    await failedPage.getByRole('button',{name:'重试下载',exact:true}).waitFor({state:'visible'});
    failFile = null;
    await failedPage.getByRole('button',{name:'重试下载',exact:true}).click();
    await failedPage.waitForFunction(()=>window.rainOfflineReady === true,null,{timeout:120000});
    await boot(failedPage,'/Rain/');
    checks.push('failed engine download retries to a verified complete cache and boots the native menu after reopening');
    await failed.close();
    assert.equal(errors.length,0);
    const offlineBytes = buildMetadata.offline_bytes;
    assert.ok(samples.every(sample=>sample.milliseconds<120000));
    const report={status:'passed',engine:'RenPy 8.5.3 official WASM',version:expectedVersion,checks,samples,
        first_baseline:true,budgets:{offline_bytes:offlineByteBudget,boot_milliseconds:120000},offline_bytes:offlineBytes,
        screenshots,errors,requests_outside_application:requests.filter(request=>!request.startsWith('/Rain/')&&!request.startsWith('/nested/Rain/')&&!request.startsWith('/foreign-')),
        limits:['Physical device installation and human listening remain separate acceptance.','Smoke exercises beginning and native save export; all 16 full state routes are checked by native Windows suite.']};
    await fs.writeFile(path.join(reports,'acceptance.json'),JSON.stringify(report,null,2)+'\n');
    console.log(JSON.stringify(report,null,2));
} finally {
    await browser.close(); await new Promise(resolve => server.close(resolve));
}
