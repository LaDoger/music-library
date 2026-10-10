#!/usr/bin/env node
/* Browser regression check. Install Playwright outside the repo if desired:
   npm install --prefix /tmp/music-ui-review playwright
   NODE_PATH=/tmp/music-ui-review/node_modules node scripts/check_pages_ui.cjs
   Uses installed Chrome (CHROME_BIN can override); serves a Pages-style subpath locally. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const rows = JSON.parse(fs.readFileSync(path.join(root, 'data/library.json')));
const server = http.createServer((req, res) => {
  const url = new URL(req.url, 'http://localhost');
  const name = decodeURIComponent(url.pathname).replace(/^\/music-library\//, '') || 'index.html';
  const file = path.resolve(root, name);
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
    res.writeHead(404); res.end(); return;
  }
  const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.mp3': 'audio/mpeg', '.mid': 'audio/midi' };
  res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
  const size = fs.statSync(file).size;
  const range = /bytes=(\d+)-(\d*)/.exec(req.headers.range || '');
  const start = range ? Number(range[1]) : 0;
  const end = range && range[2] ? Math.min(Number(range[2]), size - 1) : size - 1;
  res.setHeader('Accept-Ranges', 'bytes');
  res.setHeader('Content-Length', end - start + 1);
  if (range) res.writeHead(206, { 'Content-Range': `bytes ${start}-${end}/${size}` });
  fs.createReadStream(file, { start, end }).pipe(res);
});

(async () => {
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/music-library/`;
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox'] });
  try {
    const context = await browser.newContext({ permissions: ['clipboard-read', 'clipboard-write'] });
    await context.addInitScript(() => {
      const NativeAudio = window.Audio;
      window.Audio = function (...args) {
        const audio = new NativeAudio(...args);
        (window.__reviewAudios ||= []).push(audio);
        return audio;
      };
    });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    async function load(query = '?view=works') {
      await page.goto(base + query);
      await page.waitForFunction(() => document.querySelector('#resultCount b'));
    }
    const coll = new Intl.Collator('en', { numeric: true, sensitivity: 'base' });
    const fold = s => String(s || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    const composers = [...new Set(rows.map(r => r.composer))];
    const bach = rows.filter(r => r.composer === 'Johann Sebastian Bach');

    // Composer-first: default view is the A–Z composer index.
    await load('');
    assert.equal(await page.locator('.composer-card').count(), composers.length);
    assert.equal(await page.locator('.card').count(), 0);
    assert.equal(await page.locator('#composerHero').isHidden(), true);
    const featNames = [...new Set(rows.filter(r => r.featured_rank >= 1 && r.featured_rank <= 2).map(r => r.composer))];
    assert.equal(await page.locator('#featuredStrip .fchip').count(), featNames.length, 'featured composer chips');
    assert.equal(await page.locator('#featuredStrip').isVisible(), true);
    assert.equal(await page.locator('.pick').count(), 15);
    assert.match(await page.locator('#picksTitle').textContent(), /Editor.s picks for video/);
    const sortNames = await page.locator('.composer-card .cc-name').allInnerTexts();
    const bySort = [...composers].sort((a, b) => coll.compare(fold(rows.find(r => r.composer === a).composer_sort), fold(rows.find(r => r.composer === b).composer_sort)));
    assert.deepEqual(sortNames, bySort, 'composer index A–Z by sort name');
    await page.locator('.composer-card', { hasText: 'Johann Sebastian Bach' }).click();
    await page.waitForSelector('#composerHero:not([hidden])');
    assert.equal(new URL(page.url()).searchParams.get('composer'), 'Johann Sebastian Bach');
    await count(bach.length);
    assert.match(await page.locator('#composerHero').innerText(), /1685–1750/);
    const cats = await page.locator('.card').evaluateAll(cards => cards.map(c => c.dataset.id));
    const expectedCats = [...bach].sort((a, b) => (!a.catalog - !b.catalog) || coll.compare(a.catalog || '', b.catalog || '') || (!a.preview_url - !b.preview_url) || coll.compare(a.title, b.title)).slice(0, 48).map(r => r.id);
    assert.deepEqual(cats, expectedCats, 'composer page sorted by catalogue number');
    await page.goBack(); await page.waitForSelector('.composer-card');
    await load('?composer=Johann%20Sebastian%20Bach&score=1'); await count(bach.filter(r => r.has_editable_score).length);
    await page.locator('#composerHero .back').click(); await page.waitForSelector('.composer-card');
    assert.equal(new URL(page.url()).searchParams.has('composer'), false);
    // Works view: default sort is featured composers first (rank 1-4, depth run 1), then composer, catalogue, title.
    await load();
    const firstIds = await page.locator('.card').evaluateAll(cards => cards.map(c => c.dataset.id));
    const expectedFirst = [...rows].sort((a, b) => ((a.featured_rank || 9) - (b.featured_rank || 9)) || coll.compare(a.composer_sort, b.composer_sort) || (!a.catalog - !b.catalog) || coll.compare(a.catalog || '', b.catalog || '') || (!a.preview_url - !b.preview_url) || coll.compare(a.title, b.title)).slice(0, 48).map(r => r.id);
    assert.deepEqual(firstIds, expectedFirst, 'default works sort');
    assert.equal(await page.locator('.card .c-composer').count(), 48, 'composer name on every card');
    async function count(n) {
      await page.waitForFunction(expected => +document.querySelector('#resultCount b')?.textContent === expected, n);
    }
    async function insideDrawer() {
      assert(await page.evaluate(() => !!document.activeElement.closest('#drawer')), 'Focus must stay inside dialog');
    }

    await load();
    assert.equal(await page.locator('.card').count(), 48);
    assert.equal(await page.locator('.pick').count(), 15);
    for (const q of ['BWV565', 'bwv 565', 'dvorak', 'Op 27', 'K331']) {
      await page.locator('#q').fill(q);
      await page.waitForTimeout(180);
      assert((await page.locator('.card').count()) > 0, `Search ${q}`);
      assert.equal(new URL(page.url()).searchParams.get('q'), q);
    }
    await page.locator('#clearAll').click(); await count(rows.length);
    // Clear before the search debounce expires: the old query must not return.
    await page.evaluate(() => {
      const q = document.querySelector('#q'); q.value = 'Bach'; q.dispatchEvent(new Event('input', { bubbles: true }));
      document.querySelector('#clearAll').click();
    });
    await page.waitForTimeout(180); await count(rows.length);
    assert.equal(await page.locator('#q').inputValue(), '');
    await page.locator('#f_score').check(); await count(rows.filter(r => r.has_editable_score).length);
    await page.locator('#clearAll').click();
    // Featured composers (featured_rank 1-2): filter checkbox + URL param.
    const isFeat = r => r.featured_rank >= 1 && r.featured_rank <= 2;
    assert(rows.some(isFeat), 'featured_rank present in data');
    await page.locator('#f_featured').check(); await count(rows.filter(isFeat).length);
    assert.equal(new URL(page.url()).searchParams.get('featured'), '1');
    await page.reload(); await count(rows.filter(isFeat).length);
    await page.locator('#clearAll').click(); await count(rows.length);
    assert.equal(await page.locator('#f_featured').isChecked(), false);
    await page.setViewportSize({ width: 1280, height: 900 });
    const filters = {
      genre: ['classical', r => r.genre === 'classical'],
      mood: ['epic', r => r.mood_tags_list.includes('epic')],
      era: ['Baroque', r => r.era === 'Baroque'],
      energy: ['high', r => r.energy === 'high'],
      licence: ['sharealike', r => r.licence_status === 'sharealike'],
      rec: ['0', r => !r.has_recording],
      verified: ['unverified', r => r.verified !== 'yes'],
    };
    for (const [key, [value, predicate]] of Object.entries(filters)) {
      await page.locator('#f_' + key).selectOption(value); await count(rows.filter(predicate).length);
      assert.equal(new URL(page.url()).searchParams.get(key), value);
      await page.reload(); await count(rows.filter(predicate).length);
      await page.locator('#clearAll').click(); await count(rows.length);
    }
    await page.locator('#showPicks').click(); await count(15);
    const expectedPicks = rows.filter(r => r.editors_pick_rank).sort((a, b) => a.editors_pick_rank - b.editors_pick_rank).map(r => r.id);
    assert.deepEqual(await page.locator('.card').evaluateAll(cards => cards.map(c => c.dataset.id)), expectedPicks);
    assert.equal(new URL(page.url()).searchParams.get('picks'), '1');
    await page.locator('#clearAll').click();
    await page.locator('#pager button[data-page="2"]').first().click();
    assert.equal(await page.evaluate(() => document.activeElement.id), 'results');
    assert.equal(new URL(page.url()).searchParams.get('page'), '2');
    await load('?view=works&page=999&score=0&rec=no&licence=unknown&id=missing');
    assert.equal(await page.locator('#f_score').isChecked(), false);
    assert.equal(new URL(page.url()).searchParams.get('page'), String(Math.ceil(rows.length / 48)));
    for (const k of ['score', 'rec', 'licence', 'id']) assert.equal(new URL(page.url()).searchParams.has(k), false);
    await load('?q=BWV565');
    const opener = page.locator('.card h3 button').first(); await opener.click();
    assert.equal(await page.locator('main').evaluate(el => el.inert), true);
    assert.equal(await page.locator('#drawer').evaluate(el => el.inert), false);
    assert.equal(await page.evaluate(() => document.activeElement.className), 'icon-btn drawer-close');
    await page.keyboard.press('Shift+Tab'); await insideDrawer();
    await page.keyboard.press('Tab'); await insideDrawer();
    await page.keyboard.press('/'); await insideDrawer();
    for (let i = 0; i < 25; i++) { await page.keyboard.press('Tab'); await insideDrawer(); }
    await page.locator('[data-act="copy"]').click();
    assert.match(await page.evaluate(() => navigator.clipboard.readText()), /Norbert Schenk/);
    await page.locator('[data-act="link"]').click();
    assert.equal(new URL(await page.evaluate(() => navigator.clipboard.readText())).searchParams.get('id'), 'bach_bwv565_toccata');
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#drawer').evaluate(el => el.inert), true);
    assert.equal(await page.locator('main').evaluate(el => el.inert), false);
    assert.equal(await page.evaluate(() => document.activeElement.dataset.act), 'open');
    await opener.click(); await page.goBack();
    assert.equal(await page.locator('#drawer').getAttribute('aria-hidden'), 'true');
    await page.goForward();
    assert.equal(await page.locator('#drawer').getAttribute('aria-hidden'), 'false');
    await page.keyboard.press('Escape');
    // Back/Forward while the search field is focused must update its visible value.
    await page.evaluate(() => { history.pushState(null, '', '?q=Bach'); history.pushState(null, '', '?q=Chopin'); document.querySelector('#q').focus(); });
    await page.goBack(); assert.equal(await page.locator('#q').inputValue(), 'Bach');
    await load();
    await page.locator('#browse-era').focus(); await page.keyboard.press('ArrowRight');
    assert.equal(await page.evaluate(() => document.activeElement.id), 'browse-composer');
    assert.equal(await page.locator('#browseChips').getAttribute('aria-labelledby'), 'browse-composer');
    await page.keyboard.press('End'); assert.equal(await page.evaluate(() => document.activeElement.id), 'browse-genre');
    await page.keyboard.press('Home'); assert.equal(await page.evaluate(() => document.activeElement.id), 'browse-era');

    // Real MP3 playback, one Audio object, native button Space, global Space/Esc and seek.
    await load('?view=works&picks=1'); // bulk rows have no MP3 preview; picks all do
    await page.locator('.card [data-act="play"][data-mode="preview"]').first().click();
    await page.waitForFunction(() => !window.__reviewAudios[0].paused && Number.isFinite(window.__reviewAudios[0].duration));
    assert.equal(await page.evaluate(() => window.__reviewAudios.length), 1);
    const firstSrc = await page.evaluate(() => window.__reviewAudios[0].src);
    await page.locator('.card [data-act="play"][data-mode="preview"]').nth(1).click();
    await page.waitForFunction(src => window.__reviewAudios[0].src !== src && !window.__reviewAudios[0].paused && Number.isFinite(window.__reviewAudios[0].duration), firstSrc);
    assert.equal(await page.locator('.card.playing').count(), 1);
    await page.locator('.card.playing h3 button').click();
    assert.equal(await page.locator('#detail [data-act="mode"][data-mode="preview"]').getAttribute('aria-pressed'), 'true');
    await page.keyboard.press('Escape');
    await page.locator('#pBtn').focus(); await page.keyboard.press('Space');
    await page.waitForFunction(() => window.__reviewAudios[0].paused);
    await page.locator('#pBar').focus(); await page.keyboard.press('ArrowRight');
    assert((await page.locator('#pBar').getAttribute('aria-valuenow')) > 0);
    await page.keyboard.press('Home'); assert.equal(await page.locator('#pBar').getAttribute('aria-valuenow'), '0');
    await page.locator('#results').focus(); await page.keyboard.press('Space');
    await page.waitForFunction(() => !window.__reviewAudios[0].paused);
    await page.keyboard.press('Escape'); assert.equal(await page.locator('#player').isVisible(), false);
    await page.keyboard.press('/'); assert.equal(await page.evaluate(() => document.activeElement.id), 'q');

    for (const width of [320, 390, 560, 561, 720, 999, 1000, 1280]) {
      await page.setViewportSize({ width, height: 844 });
      for (const view of ['grid', 'list']) {
        await page.locator(`[data-layout="${view}"]`).click();
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `${width}px ${view} overflow`);
        assert(await page.evaluate(() => [...document.querySelectorAll('.card')].every(c => c.scrollWidth <= c.clientWidth + 1)), `${width}px ${view} card clipping`);
      }
      assert.equal(await page.locator('#filters').isVisible(), width >= 1000);
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.locator('#filtersBtn').click(); assert.equal(await page.locator('#filters').isVisible(), true);
    await page.setViewportSize({ width: 1280, height: 844 });
    await page.setViewportSize({ width: 390, height: 844 });
    assert.equal(await page.locator('#filters').isVisible(), true);
    await page.locator('#filtersBtn').click(); assert.equal(await page.locator('#filters').isVisible(), false);
    await page.locator('.card h3 button').first().click();
    assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), 'Mobile drawer overflow');
    // Force both clipboard methods to fail; never claim that the copy succeeded.
    await page.evaluate(() => {
      Object.defineProperty(navigator, 'clipboard', { value: { writeText: async () => { throw new Error('denied'); } } });
      document.execCommand = () => false;
    });
    await page.locator('[data-act="copy"]').click();
    assert.match(await page.locator('#toast').innerText(), /Could not copy/);
    await insideDrawer();
    assert.equal(await page.locator('textarea').count(), 0);
    await page.keyboard.press('Escape');

    // Synthetic expansion preserves unique IDs and uses the actual UI render/filter path.
    const synthetic = Array.from({ length: Math.max(2, Math.ceil(10000 / rows.length)) }, (_, batch) => rows.map(r => ({ ...r, id: r.id + '_' + batch, editors_pick_rank: batch ? 0 : r.editors_pick_rank }))).flat();
    const scalePage = await context.newPage();
    await scalePage.route('**/data/index/manifest.json', route => route.fulfill({ status: 404, body: '' })); // force the library.json fallback
    await scalePage.route('**/data/library.json', route => route.fulfill({ json: synthetic }));
    await scalePage.goto(base + '?view=works'); await scalePage.waitForSelector('.card');
    assert.equal(await scalePage.locator('.card').count(), 48);
    assert.equal(await scalePage.locator('#resultCount b').innerText(), String(synthetic.length));
    const timings = [];
    for (let i = 0; i < 5; i++) {
      timings.push(await scalePage.evaluate(() => {
        const start = performance.now();
        const toggle = document.querySelector('#f_score'); toggle.checked = !toggle.checked;
        toggle.dispatchEvent(new Event('change', { bubbles: true }));
        return performance.now() - start;
      }));
    }
    assert.equal(await scalePage.locator('.card').count(), 48);
    await scalePage.goto(base); await scalePage.waitForSelector('.composer-card');
    assert.equal(await scalePage.locator('.composer-card').count(), composers.length);
    assert.equal(errors.length, 0, errors.join('\n'));
    console.log(`PASS: composer index/page/sort; search; all facets + reload; clear debounce; editor's picks; pagination/URL normalization; modal focus/history; copy success/failure; tabs; real single-player audio/seek/Space/Esc; mobile/resize; ${synthetic.length} rows.`);
    console.log(`${synthetic.length}-row filter/facet/render samples (ms): ${timings.map(t => t.toFixed(1)).join(', ')}; raw JSON ${(Buffer.byteLength(JSON.stringify(synthetic)) / 1024 / 1024).toFixed(2)} MiB; 48 result cards.`);
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e.stack); process.exitCode = 1; }).finally(() => server.close());
