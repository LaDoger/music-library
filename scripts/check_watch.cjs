#!/usr/bin/env node
/* Watch player check (?watch=<id>): score + live audio sync, measure highlight, system turns,
   MIDI-only piano roll, orchestral score, multi-movement autoplay, axe.
   NODE_PATH=/tmp/music-ui-review/node_modules node scripts/check_watch.cjs
   Needs network (jsDelivr OSMD, tonejs.github.io Salamander samples, Magenta SGM+ soundfont).
   Screenshots: $SHOTS (default .tmp/watch/shots next to the main checkout). */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const SHOTS = process.env.SHOTS || '/workspace/music/library/.tmp/watch/shots';
fs.mkdirSync(SHOTS, { recursive: true });
const IDS = { piano: 'chopin_op74_no_1_zyczenie', midiOnly: 'bach_bwv1007_prelude', orchestral: 'wagner_wwv70_tannhauser_overture', set: 'mahler_gmw10_gesellen1', setNext: 'mahler_gmw10_gesellen2' };
const server = http.createServer((req, res) => {
  const name = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\//, '') || 'index.html';
  const file = path.resolve(root, name);
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
  const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.mid': 'audio/midi' };
  res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  await new Promise((r) => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
  const errors = [];
  let failed = 0;
  const ok = (m) => console.log('  ok  ' + m);
  try {
    const ctx = await browser.newContext({ viewport: { width: 1360, height: 860 } });
    const page = await ctx.newPage();
    page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
    page.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) errors.push('console: ' + m.text()); });
    const st = () => page.evaluate(() => { const { seek, play, ...s } = window.__watch || {}; return s; });
    const ready = async (id) => {
      await page.waitForFunction((i) => window.__watch && window.__watch.id === i && window.__watch.ready, id, { timeout: 150000 });
    };
    const start = async (id, tempo) => {
      await page.goto(base + '?watch=' + id);
      await page.waitForSelector('#watch:not([hidden]) #wPlay');
      await ready(id);
      if (tempo) await page.evaluate((t) => { const i = document.querySelector('#wTempo'); i.value = t; i.dispatchEvent(new Event('input')); }, tempo);
      await page.click('#wPlay');
      await page.waitForFunction(() => window.__watch.playing);
    };

    /* (a) piano MusicXML */
    console.log('piano MusicXML: ' + IDS.piano);
    await start(IDS.piano, 1.5);
    let s = await st();
    assert.equal(s.kind, 'piano'); assert(s.hasScore, 'score drawn'); assert(s.steps > 20 && s.systems >= 3, 'steps/systems');
    assert.equal(s.ctxState, 'running'); ok('audio context running (Salamander piano)');
    assert.equal(await page.locator('#wCard .wc-comp').textContent(), 'Frédéric Chopin');
    await page.screenshot({ path: path.join(SHOTS, 'watch_piano_titlecard.png') });
    await sleep(3800);
    const t0 = s.baseTime, m0 = s.measure;
    await page.waitForFunction((m) => window.__watch.measure > m + 1, m0, { timeout: 40000 });
    s = await st();
    assert(s.baseTime > t0 + 0.5, 'currentTime advances'); ok(`currentTime advances (${t0.toFixed(2)} -> ${s.baseTime.toFixed(2)}), measure ${m0} -> ${s.measure}`);
    const boxA = await page.locator('#wMeasure').boundingBox();
    await page.waitForFunction((m) => window.__watch.measure > m + 2, s.measure, { timeout: 40000 });
    const boxB = await page.locator('#wMeasure').boundingBox();
    assert(boxA && boxB && (Math.abs(boxA.x - boxB.x) > 5 || Math.abs(boxA.y - boxB.y) > 5), 'measure highlight box moved'); ok('measure highlight box moves');
    const sys0 = (await st()).system;
    await page.waitForFunction((sy) => window.__watch.system > sy || window.__watch.turns > 0, sys0, { timeout: 90000 });
    s = await st(); assert(s.turns >= 1, 'system turn happened during playback'); ok(`system turn during playback (system ${s.system + 1}/${s.systems}, turns ${s.turns})`);
    await page.screenshot({ path: path.join(SHOTS, 'watch_piano_dark.png') });
    await page.click('[data-w="paper"]');
    await sleep(500);
    await page.screenshot({ path: path.join(SHOTS, 'watch_piano_light.png') });
    await page.click('[data-view="both"]'); await sleep(400);
    await page.screenshot({ path: path.join(SHOTS, 'watch_piano_both.png') });
    // seek across systems
    await page.evaluate(() => window.__watch.seek(window.__watch.total * 0.9)); await sleep(1000);
    const late = await st(); assert(late.system >= 2 && late.measure > 10, 'seek jumps to late system'); ok(`seek moves cursor (measure ${late.measure + 1})`);
    await page.click('[data-view="score"]');
    await page.click('#wPlay'); // pause
    await page.waitForFunction(() => !window.__watch.playing);
    // axe
    const axeSrc = fs.readFileSync(require.resolve('axe-core/axe.min.js'), 'utf8');
    await page.evaluate(axeSrc);
    const ax = await page.evaluate(() => axe.run(document.querySelector('#watch'), { rules: { 'color-contrast': { enabled: false } } }));
    const bad = ax.violations.filter((v) => ['serious', 'critical'].includes(v.impact));
    if (bad.length) { failed++; console.log('  FAIL axe: ' + bad.map((v) => v.id + ' x' + v.nodes.length + ' ' + v.nodes.map((n) => n.html.slice(0, 110)).join(' | ')).join('\n   ')); } else ok(`axe: no serious/critical violations (${ax.violations.length} minor)`);

    /* (a2) sound picker: switch each sound live, URL + localStorage persist */
    console.log('sound picker');
    await page.evaluate(() => localStorage.removeItem('watchSound'));
    await start(IDS.piano, 1.5);
    for (const snd of ['harpsichord', 'rhodes', 'celesta', 'musicbox', 'organ', 'gm', 'salamander']) {
      await page.selectOption('#wSound', snd);
      await page.waitForFunction((x) => window.__watch.sound === x && !document.querySelector('#wSound').disabled, snd, { timeout: 90000 });
      const a = (await st()).baseTime; await sleep(1800); s = await st();
      assert(s.playing && s.baseTime > a + 0.5, snd + ' plays and time advances');
      assert.equal(new URL(page.url()).searchParams.get('sound'), snd);
      assert.equal(await page.evaluate(() => localStorage.getItem('watchSound')), snd);
      assert((await page.locator('#wCredits .wc-sound').textContent()).includes('Sound credits'), 'credits shown');
      ok('sound ' + snd + ' loaded and playing');
    }
    await page.goto(base + '?watch=' + IDS.piano + '&sound=harpsichord'); await ready(IDS.piano);
    assert.equal((await st()).sound, 'harpsichord'); assert.equal(await page.inputValue('#wSound'), 'harpsichord'); ok('&sound=harpsichord honoured on load');
    await page.evaluate(() => localStorage.removeItem('watchSound'));

    /* (b) MIDI-only */
    console.log('MIDI-only: ' + IDS.midiOnly);
    await start(IDS.midiOnly, 1.5);
    s = await st();
    assert(!s.hasScore && s.view === 'roll'); assert.equal(s.ctxState, 'running');
    const b0 = s.baseTime; await sleep(2500); s = await st();
    assert(s.baseTime > b0 + 1, 'MIDI-only time advances'); ok(`piano roll playing, time ${b0.toFixed(1)} -> ${s.baseTime.toFixed(1)}`);
    await page.screenshot({ path: path.join(SHOTS, 'watch_midi_only_roll.png') });

    /* (c) orchestral */
    console.log('orchestral MusicXML: ' + IDS.orchestral);
    await start(IDS.orchestral, 1.5);
    s = await st();
    assert(s.hasScore && s.systems >= 2); assert.equal(s.ctxState, 'running');
    await page.waitForFunction(() => window.__watch.measure >= 2, null, { timeout: 60000 });
    s = await st(); ok(`${s.kind} engine, measure ${s.measure + 1}/${s.measures}, system ${s.system + 1}/${s.systems}`);
    await page.screenshot({ path: path.join(SHOTS, 'watch_orchestral.png') });

    /* (d) set autoplay */
    console.log('multi-movement set: ' + IDS.set);
    await start(IDS.set, 1.5);
    await page.evaluate(() => window.__watch.seek(window.__watch.total - 2.5));
    await page.waitForFunction((n) => window.__watch.id === n && window.__watch.ready, IDS.setNext, { timeout: 150000 });
    await page.waitForFunction(() => window.__watch.playing, null, { timeout: 30000 });
    assert.equal(new URL(page.url()).searchParams.get('watch'), IDS.setNext);
    ok('autoplayed next movement ' + IDS.setNext);
    await page.screenshot({ path: path.join(SHOTS, 'watch_set_next.png') });

    /* mobile */
    await page.setViewportSize({ width: 390, height: 780 });
    await page.goto(base + '?watch=' + IDS.piano); await ready(IDS.piano); await sleep(800);
    await page.screenshot({ path: path.join(SHOTS, 'watch_mobile.png') });
    ok('mobile screenshot');
    await page.click('[data-w="close"]');
    await page.waitForSelector('body:not(.watching)'); ok('close returns to library');
  } catch (e) { failed++; console.log('  FAIL ' + (e.stack || e)); }
  if (errors.length) { failed++; console.log('console errors:\n  ' + errors.join('\n  ')); } else ok('no console errors');
  await browser.close(); server.close();
  console.log(failed ? 'FAILED' : 'PASS');
  process.exit(failed ? 1 : 0);
})();
