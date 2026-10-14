/* Installation status belongs to the browser; gameplay remains in Ren'Py. */
(() => {
    const status = document.getElementById('offlineStatus');
    const install = document.getElementById('installPwa');
    let installPrompt;
    let owner;
    let preparedUpdate;
    // A browser input supplies IME/Chinese text; Ren'Py still owns the history,
    // result list, speaker selection and voice replay. No story/save writes.
    const searchControls = document.getElementById('historySearchControls');
    const queryInput = document.getElementById('historyQuery');
    const searchStatus = document.getElementById('historySearchStatus');
    let queryRevision = 0, latestQuery = '', lastSent = '', writing = false, composing = false;
    const pythonString = value => JSON.stringify(value).replace(/[^\x00-\x7f]/g,
        character => '\\u' + character.charCodeAt(0).toString(16).padStart(4, '0'));
    async function sendQuery() {
        if (writing || composing || searchControls.hidden || typeof window.renpy_exec !== 'function') return;
        writing = true;
        try {
            while (lastSent !== latestQuery && !searchControls.hidden) {
                const value = latestQuery;
                await window.renpy_exec('if renpy.get_screen("history") is not None:\n' +
                    '    renpy.set_screen_variable("history_query", ' + pythonString(value) + ', screen="history")\n' +
                    '    renpy.restart_interaction()');
                lastSent = value;
            }
            searchStatus.textContent = '';
        } catch {
            searchStatus.textContent = '暂时无法检索，请重新打开回看。';
        } finally { writing = false; }
    }
    function changedQuery() {
        queryRevision++; latestQuery = queryInput.value.slice(0, 80);
        void sendQuery();
    }
    queryInput.addEventListener('input', changedQuery);
    queryInput.addEventListener('compositionstart', () => { composing = true; });
    queryInput.addEventListener('compositionend', () => { composing = false; changedQuery(); });
    queryInput.addEventListener('keydown', event => event.stopPropagation());
    queryInput.addEventListener('keyup', event => event.stopPropagation());
    searchControls.addEventListener('submit', event => event.preventDefault());
    document.getElementById('historyQueryClear').addEventListener('click', () => {
        queryInput.value = ''; changedQuery(); queryInput.focus();
    });
    async function syncSearch() {
        try {
            if (!document.hidden && !document.getElementById('presplash') && typeof window.renpy_get === 'function') {
                const revision = queryRevision;
                const info = await window.renpy_get('[bool(renpy.get_screen("history")), renpy.get_screen("history").scope.get("history_query", "") if renpy.get_screen("history") else ""]');
                searchControls.hidden = !info?.[0];
                if (!searchControls.hidden && !writing && !composing && revision === queryRevision && lastSent === latestQuery) {
                    queryInput.value = info[1]; latestQuery = lastSent = info[1];
                }
            }
        } catch { searchControls.hidden = true; }
        window.setTimeout(syncSearch, 300);
    }
    void syncSearch();
    window.addEventListener('beforeinstallprompt', event => {
        event.preventDefault(); installPrompt = event; install.hidden = false;
    });
    install.addEventListener('click', async () => {
        if (!installPrompt) return;
        await installPrompt.prompt(); await installPrompt.userChoice;
        installPrompt = null; install.hidden = true;
    });
    window.addEventListener('appinstalled', () => { install.hidden = true; });
    async function check() {
        if (!owner?.active) return;
        const expected = new URL('./service-worker.js', location.href).href;
        if (owner.scope !== new URL('./', location.href).href || owner.active.scriptURL !== expected) return;
        const channel = new MessageChannel();
        channel.port1.onmessage = event => {
            window.rainOfflineReady = event.data.ready;
            window.rainOfflineRevision = event.data.revision;
            status.textContent = owner.waiting || preparedUpdate?.state === 'installed' ? '新版已准备，请关闭此应用的所有窗口后重开' :
                event.data.ready ? '完整内容已保存，可离线重开' : '正在保存离线内容…';
            status.dataset.ready = String(event.data.ready);
            channel.port1.close();
        };
        owner.active.postMessage({type: 'RAIN_OFFLINE_STATUS'}, [channel.port2]);
    }
    function watchWorker(worker) {
        if (!worker) return;
        const changed = () => {
            // At the installed event the registration's waiting property may
            // update on the next task. An installed replacement already has
            // the same verified complete cache and must wait for old clients.
            if (worker.state === 'installed' && owner.active && owner.active !== worker) preparedUpdate = worker;
            if (worker.state === 'activated' || worker.state === 'redundant') {
                if (preparedUpdate === worker) preparedUpdate = null;
            }
            if (worker.state === 'redundant') status.textContent = '离线保存未完成；联网后重新打开可重试';
            if (worker.state === 'installed' || worker.state === 'activated') check();
        };
        worker.addEventListener('statechange', changed);
        changed();
    }
    if (!('serviceWorker' in navigator)) {
        status.textContent = '此浏览器不支持离线安装，建议使用最新版浏览器'; return;
    }
    navigator.serviceWorker.addEventListener('controllerchange', check);
    navigator.serviceWorker.register('./service-worker.js', {scope: './', updateViaCache: 'none'})
        .then(registration => {
            owner = registration;
            registration.addEventListener('updatefound', () => watchWorker(registration.installing));
            // Registration can finish after updatefound has already fired.
            watchWorker(registration.installing);
            watchWorker(registration.waiting);
            check();
        }).catch(() => { status.textContent = '离线保存未完成；联网后重新打开可重试'; });
})();
