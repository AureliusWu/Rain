/* Installation status belongs to the browser; gameplay remains in Ren'Py. */
(() => {
    const status = document.getElementById('offlineStatus');
    const offlineProgress = document.getElementById('offlineProgress');
    const retryOffline = document.getElementById('retryOffline');
    let checking = false;
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
    let historySession = null;
    const pythonString = value => JSON.stringify(value).replace(/[^\x00-\x7f]/g,
        character => '\\u' + character.charCodeAt(0).toString(16).padStart(4, '0'));
    async function sendQuery() {
        if (writing || composing || searchControls.hidden || !historySession || typeof window.renpy_exec !== 'function') return;
        writing = true;
        let failed = false, attemptedSession = historySession;
        try {
            while (lastSent !== latestQuery && !searchControls.hidden && !composing) {
                const value = latestQuery, session = historySession;
                attemptedSession = session;
                const accepted = await window.renpy_exec('result = rain_set_history_query(' +
                    pythonString(value) + ', ' + pythonString(session) + ')');
                if (!accepted || historySession !== session) { failed = true; break; }
                lastSent = value;
            }
            searchStatus.textContent = '';
        } catch {
            failed = true;
            searchStatus.textContent = '暂时无法检索，请重新打开回看。';
        } finally {
            writing = false;
            // Input may arrive while the previous panel's command completes.
            if ((!failed || attemptedSession !== historySession) && lastSent !== latestQuery && !searchControls.hidden && !composing)
                window.setTimeout(sendQuery, 0);
        }
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
    queryInput.addEventListener('keypress', event => event.stopPropagation());
    searchControls.addEventListener('submit', event => event.preventDefault());
    document.getElementById('historyQueryClear').addEventListener('click', () => {
        queryInput.value = ''; changedQuery(); queryInput.focus();
    });
    async function syncSearch() {
        try {
            if (!document.hidden && !document.getElementById('presplash') && typeof window.renpy_get === 'function') {
                const revision = queryRevision;
                const sentAtRequest = lastSent;
                const idleAtRequest = !writing && !composing && lastSent === latestQuery;
                const info = await window.renpy_get('rain_search_panel_info()');
                searchControls.hidden = !info?.[0];
                if (searchControls.hidden) {
                    historySession = null;
                } else if (historySession !== info[1]) {
                    // A reopen starts a new independent panel. In-flight input
                    // from the old panel is rejected by the native token check.
                    historySession = info[1]; queryRevision++;
                    queryInput.value = info[2]; latestQuery = lastSent = info[2];
                } else if (idleAtRequest && !writing && !composing && revision === queryRevision &&
                           lastSent === sentAtRequest && lastSent === latestQuery) {
                    queryInput.value = info[2]; latestQuery = lastSent = info[2];
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
    function showProgress(data) {
        offlineProgress.textContent = `${data.completedFiles} / ${data.totalFiles} 个文件 · ${(data.verifiedBytes / 1048576).toFixed(1)} / ${(data.totalBytes / 1048576).toFixed(1)} MB`;
        offlineProgress.dataset.verifiedBytes = String(data.verifiedBytes);
        offlineProgress.dataset.totalBytes = String(data.totalBytes);
        retryOffline.hidden = !data.failed;
    }
    navigator.serviceWorker?.addEventListener('message', event => {
        if (event.data?.type !== 'RAIN_OFFLINE_PROGRESS' || !owner || ![owner.active, owner.waiting, owner.installing, preparedUpdate].includes(event.source)) return;
        showProgress(event.data);
        if (event.data.failed) status.textContent = '下载未完成，可重试；已有离线版本仍保留';
    });
    async function check() {
        if (!owner?.active) return;
        const expected = new URL('./service-worker.js', location.href).href;
        if (owner.scope !== new URL('./', location.href).href || owner.active.scriptURL !== expected) return;
        const channel = new MessageChannel();
        channel.port1.onmessage = event => {
            showProgress(event.data);
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
            if (worker.state === 'redundant') { status.textContent = '离线保存未完成；联网后可重试'; retryOffline.hidden = false; }
            if (worker.state === 'installed' || worker.state === 'activated') check();
        };
        worker.addEventListener('statechange', changed);
        changed();
    }
    if (!('serviceWorker' in navigator)) {
        status.textContent = '此浏览器不支持离线安装，建议使用最新版浏览器'; return;
    }
    navigator.serviceWorker.addEventListener('controllerchange', check);
    async function register() {
        if (checking) return;
        checking = true; retryOffline.disabled = true;
        try {
            const registration = await navigator.serviceWorker.register('./service-worker.js', {scope: './', updateViaCache: 'none'});
            owner = registration;
            if (!registration.rainWatching) {
                registration.rainWatching = true;
                registration.addEventListener('updatefound', () => watchWorker(registration.installing));
            }
            watchWorker(registration.installing); watchWorker(registration.waiting);
            await registration.update();
            await check();
        } catch { status.textContent = '离线保存未完成；联网后可重试'; retryOffline.hidden = false; }
        finally { checking = false; retryOffline.disabled = false; }
    }
    retryOffline.addEventListener('click', () => { retryOffline.hidden = true; status.textContent = '正在重新下载离线内容…'; void register(); });
    void register();
})();
