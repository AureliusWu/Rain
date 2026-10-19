// Read native state and perform real browser input; no injected game actions.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

const story=JSON.parse(await fs.readFile(new URL('../game/data/story.json',import.meta.url),'utf8'));
const firstLine=story.nodes.find(node=>node.id==='p00_entry').lines[0].text;
export const visibleNarration='renpy.get_screen("say") and renpy.get_screen("say").scope.get("what")';

export const get = async (page, expression) => Promise.race([
    // The official command bridge uses btoa; Python string escapes keep
    // authored Chinese text exact while sending ASCII source commands.
    page.evaluate(expression => window.renpy_get(expression), expression.replace(/[^\x00-\x7f]/g,character=>'\\u'+character.charCodeAt(0).toString(16).padStart(4,'0'))),
    new Promise((_,reject) => setTimeout(() => reject(new Error(`Ren'Py read timed out: ${expression}`)), 5000))]);
export async function waitNative(page, expression) {
    const deadline=Date.now()+60000;
    while (Date.now()<deadline) {
        if (await get(page,expression)) return;
        await page.waitForTimeout(100);
    }
    throw new Error(`Native condition timed out: ${expression}`);
}
export async function clickVirtual(page, x, y) {
    const box = await page.locator('#canvas').boundingBox();
    const scale = Math.min(box.width/1920, box.height/1080);
    await page.mouse.click(box.x+(box.width-1920*scale)/2+x*scale, box.y+(box.height-1080*scale)/2+y*scale);
}
export async function clickId(page, screen, id) {
    await waitNative(page,`bool(renpy.get_displayable(${JSON.stringify(screen)},${JSON.stringify(id)}))`);
    await waitNative(page,'not any(renpy.get_ongoing_transition(layer) for layer in (None, "master", "screens"))');
    // Read the same render-tree geometry used by official Ren'Py testfocus.
    // This command only observes displayables; the following real mouse click
    // performs the action (no injected Start, Save, Load or state mutation).
    const position=await page.evaluate(async({screen,id})=>window.renpy_exec(`
d = renpy.get_displayable(${JSON.stringify(screen)}, ${JSON.stringify(id)})
stack = [(renpy.display.render.screen_render, 0, 0)]
result = None
while stack:
    r, x, y = stack.pop()
    if not isinstance(r, renpy.display.render.Render):
        continue
    if d in r.render_of:
        result = [x + r.width / 2, y + r.height / 2]
        break
    for c in r.children:
        stack.append((c[0], x + c[1], y + c[2]))
`),{screen,id});
    assert.ok(position,`Rendered focus target ${screen}:${id}`);
    await clickVirtual(page,...position);
}
export async function startNarrative(page) {
    await clickId(page,'main_menu','menu_start');
    for(let attempt=0;attempt<10;attempt++) {
        await page.waitForTimeout(200);
        if (await get(page,`${visibleNarration} == ${JSON.stringify(firstLine)}`)) {
            await waitNative(page,'not any(renpy.get_ongoing_transition(layer) for layer in (None, "master", "screens"))');
            return;
        }
        await page.keyboard.press('Space');
    }
    throw new Error('Actual Start did not reach native narration');
}

export async function verifyReadHistorySearch(page, screenshotPath) {
    // Build history using genuine input, rather than injecting unread records.
    for (let attempt = 0; attempt < 8 && !(await get(page, 'bool(_history_list)')); attempt++) {
        await page.keyboard.press('Space');
        await page.waitForTimeout(200);
    }
    assert.ok(await get(page, 'bool(_history_list)'), 'A real read record is available');
    const state = '[current_scene, current_chapter, affection, trust, truth_known, list(visited_scenes), len(_history_list), _last_say_what]';
    const before = await get(page, state);
    const keyword = (await get(page, 'renpy.filter_text_tags(_history_list[0].what, allow=set())')).slice(0, 4);
    await clickId(page, 'quick_menu', 'history_open');
    const panelToken = await get(page, 'renpy.get_screen("history").scope["history_session"]');
    const input = page.getByRole('searchbox', { name: '搜索已读文字', exact: true });
    await input.waitFor({ state: 'visible' });
    await input.fill('XYZ');
    await input.pressSequentially('ahls');
    await waitNative(page, 'renpy.get_screen("history").scope["history_query"] == "XYZahls"');
    assert.equal(await get(page, 'len(renpy.get_screen("history").scope["history_rows"])'), 0);
    await input.press('Backspace');
    await waitNative(page, 'renpy.get_screen("history").scope["history_query"] == "XYZahl"');
    await input.press('Enter');
    assert.equal(await get(page, 'bool(renpy.get_screen("history"))'), true, 'Enter keeps history open');
    await clickId(page, 'history', 'history_clear');
    assert.equal(await get(page, 'bool(renpy.get_screen("history"))'), true, 'Clear must not end the menu interaction');
    assert.equal(await get(page, 'renpy.get_screen("history").scope["history_session"]'), panelToken);
    await page.waitForFunction(() => document.getElementById('historyQuery').value === '');
    // Actual Chromium IME preedit stays local across native polling until commit.
    await input.focus();
    const ime = await page.context().newCDPSession(page);
    await ime.send('Input.imeSetComposition', {text:keyword, selectionStart:keyword.length, selectionEnd:keyword.length});
    await page.waitForTimeout(350);
    assert.equal(await input.inputValue(), keyword);
    assert.equal(await get(page, 'renpy.get_screen("history").scope["history_query"]'), '');
    await ime.send('Input.insertText', {text:keyword});
    await ime.detach();
    await waitNative(page, `renpy.get_screen("history").scope["history_query"] == ${JSON.stringify(keyword)}`);
    assert.equal(await page.evaluate(async () => {
        await document.fonts.load('16px RainInterface'); return document.fonts.check('16px RainInterface');
    }), true, 'The browser-control font is self-hosted and loaded');
    const indices = await get(page, '[i for i, h in renpy.get_screen("history").scope["history_rows"]]');
    assert.ok(indices.includes(0), 'Chinese keyword matches the original first read entry');
    if (screenshotPath) await page.screenshot({ path: screenshotPath });
    await clickId(page, 'history', 'history_clear');
    assert.equal(await get(page, 'renpy.get_screen("history").scope["history_session"]'), panelToken);
    assert.equal(await get(page, 'len(renpy.get_screen("history").scope["history_rows"])'), before[6]);
    await clickId(page, 'history', 'game_return');
    await input.waitFor({state:'hidden'});
    assert.deepEqual(await get(page, state), before);
    await clickId(page, 'quick_menu', 'history_open');
    await input.waitFor({state:'visible'});
    assert.notEqual(await get(page, 'renpy.get_screen("history").scope["history_session"]'), panelToken);
    assert.equal(await get(page, 'renpy.get_screen("history").scope["history_query"]'), '');
    assert.equal(await get(page, 'renpy.get_screen("history").scope["history_speaker"]'), '');
    await clickId(page, 'history', 'game_return');
    await input.waitFor({state:'hidden'});
    return { read_records: before[6], matched_original_indices: indices, state_preserved: true };
}

export async function verifyReadBookmarks(page, screenshotPath) {
    // Chapter cards also enter native history. Find an actual authored record;
    // never assume history[0] is a line from the story catalog.
    for (let step=0;step<12;step++) {
        if (await get(page,'any(rain_history_identity(h) for h in _history_list)')) break;
        await page.keyboard.press('Space');
        await page.waitForTimeout(150);
    }
    const read = await get(page,'next(((i, rain_history_identity(h)) for i, h in enumerate(_history_list) if rain_history_identity(h)), None)');
    assert.ok(read, 'An actual read record is required for a bookmark');
    const [index, identity] = read;
    const state='[current_scene, current_chapter, visited_scenes, last_ending, renpy.random.getstate(), len(_history_list)]';
    const before=await get(page,state);
    await clickId(page,'quick_menu','history_open');
    await clickId(page,'history',`history_bookmark_${index}`);
    assert.equal(await get(page,`rain_is_bookmarked(${JSON.stringify(identity)})`),true);
    await clickId(page,'history','history_bookmarks');
    await waitNative(page,'bool(renpy.get_screen("rain_bookmarks"))');
    assert.ok((await get(page,'[row["id"] for row in rain_bookmark_rows()]')).includes(identity));
    await clickId(page,'rain_bookmarks','bookmark_chapter_ch05');
    assert.equal(await get(page,'len(rain_bookmark_rows(renpy.get_screen("rain_bookmarks").scope["bookmark_chapter"]))'),0);
    await clickId(page,'rain_bookmarks','bookmark_chapter_all');
    const input = page.getByRole('searchbox', { name: '搜索已读文字', exact: true });
    await input.waitFor({state:'visible'});
    await input.fill('没有收藏的文字XYZ');
    await waitNative(page, 'renpy.get_screen("rain_bookmarks").scope["history_query"] == "没有收藏的文字XYZ"');
    assert.equal(await get(page, 'len(renpy.get_screen("rain_bookmarks").scope["bookmark_rows"])'), 0);
    await clickId(page,'rain_bookmarks','bookmark_clear');
    await page.waitForFunction(() => document.getElementById('historyQuery').value === '');
    const text = await get(page, `RAIN_READING_CATALOG[${JSON.stringify(identity)}]["text"]`);
    await input.fill(text.slice(0, 4));
    await waitNative(page, 'len(renpy.get_screen("rain_bookmarks").scope["bookmark_rows"]) > 0');
    assert.ok((await get(page,'[row["id"] for row in renpy.get_screen("rain_bookmarks").scope["bookmark_rows"]]')).includes(identity));
    if(screenshotPath) await page.screenshot({path:screenshotPath});
    await clickId(page,'rain_bookmarks',`bookmark_remove_${identity}`);
    assert.equal(await get(page,`rain_is_bookmarked(${JSON.stringify(identity)})`),false);
    await clickId(page,'rain_bookmarks','game_return');
    await clickId(page,'quick_menu','history_open');
    await clickId(page,'history',`history_bookmark_${index}`);
    await clickId(page,'history','game_return');
    assert.equal(await get(page,`rain_is_bookmarked(${JSON.stringify(identity)})`),true);
    assert.deepEqual(await get(page,state),before);
    return identity;
}
