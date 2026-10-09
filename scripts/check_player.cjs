#!/usr/bin/env node
/* Player check: preview / full recording (stream -> Release -> "open recording" fallback) /
   live in-browser MIDI synth with tempo (no pre-rendered synth audio); one source at a time.
   NODE_PATH=/tmp/music-ui-review/node_modules node scripts/check_player.cjs
   External audio URLs are routed to local files, so the audio part is offline. The live MIDI
   part loads the Magenta SGM+ soundfont from storage.googleapis.com; SKIP_NET=1 skips it. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const rows = JSON.parse(fs.readFileSync(path.join(root, 'data/library.json')));
const server = http.createServer((req, res) => {
  const name = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\//, '') || 'index.html';
  const file = path.resolve(root, name);
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
  const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.mp3': 'audio/mpeg', '.mid': 'audio/midi' };
  res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
  const errors = [];
  try {
    const ctx = await browser.newContext();
    await ctx.addInitScript(() => {
      const Native = window.Audio;
      window.Audio = function (...a) { const x = new Native(...a); (window.__audios ||= []).push(x); return x; };
    });
    const mp3 = fs.readFileSync(path.join(root, 'previews/grieg_peer_gynt_mountain_king.mp3'));
    const hits = [];
    // Commons/Archive/Release audio: fail or serve a local MP3, per test.
    let failStreams = false, failRelease = false;
    await ctx.route(/upload\.wikimedia\.org|archive\.org\/download|github\.com\/LaDoger\/music-library\/releases\/download/, route => {
      const u = route.request().url();
      hits.push(u);
      const isRelease = u.includes('/releases/download/');
      if ((isRelease && failRelease) || (!isRelease && failStreams)) return route.fulfill({ status: 404, body: 'nope' });
      // Answer Range requests like Commons / GitHub do, so seeking works.
      const m = /bytes=(\d+)-(\d*)/.exec(route.request().headers().range || '');
      if (!m) return route.fulfill({ status: 200, contentType: 'audio/mpeg', headers: { 'Accept-Ranges': 'bytes' }, body: mp3 });
      const start = +m[1], end = m[2] ? Math.min(+m[2], mp3.length - 1) : mp3.length - 1;
      return route.fulfill({ status: 206, contentType: 'audio/mpeg', body: mp3.subarray(start, end + 1),
        headers: { 'Accept-Ranges': 'bytes', 'Content-Range': `bytes ${start}-${end}/${mp3.length}` } });
    });
    const page = await ctx.newPage();
    page.on('pageerror', e => errors.push(e.message));
    const audioState = () => page.evaluate(() => ({ n: window.__audios.length, src: window.__audios[0].src, paused: window.__audios[0].paused }));
    const r = rows.find(x => x.id === 'grieg_peer_gynt_mountain_king');
    assert(r.stream_audio_url && r.release_audio_url && r.midi_play_url && !('stream_synth_url' in r), 'test row has every source');

    await page.goto(base + '?id=' + r.id);
    await page.waitForSelector('#drawer.open .listen-btn');
    assert.deepEqual(await page.locator('.listen-btn').evaluateAll(b => b.map(x => x.dataset.mode)), ['preview', 'full', 'midi']);
    assert.deepEqual(await page.locator('.listen-btn .kind').allTextContents(), ['Preview', 'Recording', 'Synth']);

    // Full recording from the direct stream.
    await page.locator('.listen-btn.m-full').click();
    await page.waitForFunction(() => !window.__audios[0].paused);
    let a = await audioState();
    assert.equal(a.src, r.stream_audio_url);
    assert.equal(await page.locator('#pMode').textContent(), 'Recording');
    assert.equal(await page.locator('#pModes [aria-pressed="true"]').textContent(), 'Full');
    await page.waitForFunction(() => /\/ \d+:\d\d$/.test(document.querySelector('#pTime').textContent));
    // Seek via the bar.
    const box = await page.locator('#pBar').boundingBox();
    await page.mouse.click(box.x + box.width * 0.5, box.y + box.height / 2);
    assert(+(await page.locator('#pBar').getAttribute('aria-valuenow')) > 0, 'seek moved');

    // Switching piece/source stops the previous one: still a single Audio element.
    await page.locator('.listen-btn.m-preview').click();
    await page.waitForFunction(src => window.__audios[0].src.endsWith(src) && !window.__audios[0].paused, r.preview_url);
    assert.equal(await page.locator('#pMode').textContent(), 'Preview · 15 s');

    // Stream fails -> Release asset.
    failStreams = true;
    await page.locator('.listen-btn.m-full').click();
    await page.waitForFunction(u => window.__audios[0].src === u && !window.__audios[0].paused, r.release_audio_url);
    // Both fail -> "Download / open recording" shown, no exception.
    failRelease = true;
    await page.locator('.listen-btn.m-preview').click();
    await page.locator('.listen-btn.m-full').click();
    await page.waitForSelector('#pOpen:not([hidden])');
    assert.equal(await page.locator('#pOpen').getAttribute('href'), r.release_audio_url);
    failStreams = failRelease = false;

    // No pre-rendered synth audio (removed 2026-10-09): no synth MP3 button, single Audio element.
    assert.equal(await page.locator('.listen-btn.m-synth').count(), 0);
    assert.equal(await page.evaluate(() => window.__audios.length), 1);

    if (!process.env.SKIP_NET) {
      // Live MIDI: audio element released, synth plays, tempo rescales duration.
      await page.locator('.listen-btn.m-midi').click();
      await page.waitForFunction(() => document.querySelector('#pMode').textContent === 'Synth · in-browser MIDI' && !document.querySelector('#player').classList.contains('loading') && /^0:0[1-9]/.test(document.querySelector('#pTime').textContent), null, { timeout: 60000 });
      assert.match(await page.locator('#pSub').textContent(), /score licence/);
      a = await audioState();
      assert.equal(a.paused, true); assert.equal(a.src, '', 'audio element released while MIDI plays');
      assert.equal(await page.locator('#pTempoWrap').isVisible(), true);
      assert.equal(await page.locator('#rollWrap').isVisible(), true, 'piano roll');
      const dur = s => { const [m, ss] = s.split(' / ')[1].split(':'); return +m * 60 + +ss; };
      const d1 = dur(await page.locator('#pTime').textContent());
      await page.locator('#dTempo').fill('1.5');
      await page.waitForTimeout(400);
      const d2 = dur(await page.locator('#pTime').textContent());
      assert(Math.abs(d2 - d1 / 1.5) <= 2, `tempo 150% shortens ${d1}s -> ${d2}s`);
      assert.equal(await page.locator('#pTempoOut').textContent(), '150%');
      await page.locator('#pBtn').click(); // pause
      await page.waitForFunction(() => document.querySelector('#pBtn').textContent === '▶');
      const t1 = await page.locator('#pTime').textContent(); await page.waitForTimeout(600);
      assert.equal(await page.locator('#pTime').textContent(), t1, 'paused MIDI does not advance');
      // Seek and resume, then switch to audio in this same document (no reload hiding overlap).
      await page.locator('#pBar').focus(); await page.keyboard.press('ArrowRight');
      assert(+(await page.locator('#pBar').getAttribute('aria-valuenow')) >= 5, 'paused MIDI seek moved');
      await page.locator('#pBtn').click();
      await page.waitForFunction(() => document.querySelector('#pBtn').getAttribute('aria-label') === 'Pause');
      await page.locator('.listen-btn.m-preview').click();
      await page.waitForFunction(() => !window.__audios[0].paused);
      assert.equal(await page.locator('#pMode').textContent(), 'Preview · 15 s');
      assert.equal(await page.locator('#pTempoWrap').isVisible(), false);
      assert.equal(await page.locator('#rollWrap').isVisible(), false);
    }
    // Score-only piece: no Full button, synth modes offered.
    const scoreOnly = rows.find(x => !x.has_recording && x.midi_play_url);
    await page.goto(base + '?id=' + scoreOnly.id);
    await page.waitForSelector('#drawer.open .listen-btn');
    assert.equal(await page.locator('.listen-btn.m-full').count(), 0);
    assert.equal(await page.locator('.listen-btn.m-midi').count(), 1);
    assert.equal(await page.locator('.listen-btn.m-preview').count(), 0, 'score-only row has no (synth) preview');
    await page.keyboard.press('Escape'); // stop
    assert.equal(errors.length, 0, errors.join('\n'));
    console.log(`PASS player: modes + badges; full stream, seek, Release fallback, open-recording fallback; no synth MP3; ${process.env.SKIP_NET ? '(live MIDI skipped)' : 'live MIDI + tempo + piano roll + pause'}; one source at a time; score-only row.`);
  } finally {
    await browser.close();
  }
})().catch(e => { console.error(e.stack); process.exitCode = 1; }).finally(() => server.close());
