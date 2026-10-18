// Real Chromium input against the production client; the native bridge is simulated.
// This deliberately does not claim WASM, native-menu or voice execution.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {chromium} from 'playwright';

const launch = {headless:true, args:['--no-sandbox']};
if (process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE) launch.executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE;
const browser = await chromium.launch(launch);
const checks = [];
try {
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.setContent(`<span id="offlineProgress"></span><button id="retryOffline" hidden></button><span id="offlineStatus"></span><button id="installPwa" hidden></button>
        <form id="historySearchControls" hidden><input id="historyQuery" type="search" maxlength="80" aria-label="搜索已读文字">
        <button id="historyQueryClear" type="button">清除关键词</button><span id="historySearchStatus"></span></form>`);
    await page.evaluate(() => {
        window.nativePanel = {open:true, token:'panel-1', query:''};
        // Match SDL's document-level keypress default prevention. The official
        // Ren'Py HTML input isolates this event as well as keydown/keyup.
        window.engineKeypresses = 0;
        document.addEventListener('keypress', event => { engineKeypresses++; event.preventDefault(); });
        window.renpy_get = async () => [nativePanel.open, nativePanel.token, nativePanel.query];
        window.renpy_exec = async command => {
            const args = command.match(/^result = rain_set_history_query\((.*), (".*")\)$/);
            const value = JSON.parse(args[1]), token = JSON.parse(args[2]);
            if (nativePanel.delay) await new Promise(resolve => { window.releaseQuery = resolve; });
            if (!nativePanel.open || token !== nativePanel.token) return false;
            nativePanel.query = value; return true;
        };
    });
    await page.addScriptTag({path:path.resolve('tools/build/pwa/client.js')});
    const input = page.getByRole('searchbox', {name:'搜索已读文字'});
    await input.waitFor({state:'visible'});
    await input.fill('XYZ'); await input.pressSequentially('ahls');
    assert.equal(await input.inputValue(), 'XYZahls', 'SDL must not suppress the browser input default');
    assert.equal(await page.evaluate(() => engineKeypresses), 0, 'Input keypress must not reach the game');
    await page.waitForFunction(() => nativePanel.query === 'XYZahls');
    await input.press('Backspace'); await input.press('Enter');
    await page.waitForFunction(() => nativePanel.query === 'XYZahl');
    assert.equal(await page.evaluate(() => nativePanel.open), true);
    checks.push('real Latin keys, Backspace and Enter preserve the open panel');
    await page.getByRole('button', {name:'清除关键词'}).click();
    await page.waitForFunction(() => nativePanel.query === '');
    const ime = await page.context().newCDPSession(page);
    await ime.send('Input.imeSetComposition', {text:'出门', selectionStart:2, selectionEnd:2});
    await page.waitForTimeout(700);
    assert.equal(await input.inputValue(), '出门');
    assert.equal(await page.evaluate(() => nativePanel.query), '');
    checks.push('Chinese preedit survives two native-state polls without writing a query');
    await ime.send('Input.insertText', {text:'出门'});
    await page.waitForFunction(() => nativePanel.query === '出门');
    await ime.detach();
    checks.push('actual CDP Chinese IME commit reaches the query bridge');
    await page.evaluate(() => { nativePanel.open = false; }); await input.waitFor({state:'hidden'});
    await page.evaluate(() => { window.nativePanel = {open:true, token:'panel-2', query:''}; });
    await input.waitFor({state:'visible'}); assert.equal(await input.inputValue(), '');
    await input.fill('重开'); await page.waitForFunction(() => nativePanel.query === '重开');
    checks.push('controls hide on close, reset on a new token and accept a reopened query');
    await page.evaluate(() => { nativePanel.delay = true; });
    await input.fill('迟到'); await page.waitForFunction(() => typeof releaseQuery === 'function');
    await page.evaluate(() => { nativePanel.open = false; }); await input.waitFor({state:'hidden'});
    await page.evaluate(() => { window.nativePanel = {open:true, token:'panel-3', query:''}; });
    await input.waitFor({state:'visible'}); await input.fill('新查询');
    await page.evaluate(() => releaseQuery());
    await page.waitForFunction(() => nativePanel.query === '新查询');
    checks.push('a delayed old-panel command cannot overwrite or block new-panel input');
    assert.deepEqual(errors, []);
    const report = {status:'passed', browser:browser.version(), checks, errors,
        scope:'Actual production client.js and real Chromium events with a simulated native bridge; not a WASM or Windows game execution.'};
    await fs.mkdir('reports', {recursive:true});
    await fs.writeFile('reports/history-input-browser.json', JSON.stringify(report, null, 2)+'\n');
    console.log(JSON.stringify(report, null, 2));
} finally { await browser.close(); }
