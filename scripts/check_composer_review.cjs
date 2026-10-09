#!/usr/bin/env node
/* Review regressions: drawer/player focus, composer history, cancelled/failed MIDI loads,
   mobile player hit targets, and WCAG A/AA. No external audio or soundfont is needed.
   NODE_PATH=/tmp/music-ui-review/node_modules node scripts/check_composer_review.cjs */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const rows = JSON.parse(fs.readFileSync(path.join(root, 'data/library.json')));
const piece = rows.find(r => r.id === 'grieg_peer_gynt_mountain_king');
const other = rows.find(r => r.midi_play_url && r.id !== piece.id);
const server = http.createServer((req, res) => {
  const name = decodeURIComponent(new URL(req.url, 'http://localhost').pathname).replace(/^\//, '') || 'index.html';
  const file = path.resolve(root, name);
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
  res.setHeader('Content-Type', ({ '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.mp3': 'audio/mpeg' })[path.extname(file)] || 'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});
// A controllable synth reproduces delays and failures that a successful live-network check misses.
const fakeSynth = `
window.__synth = { loads: [], starts: [], pending: [], playing: false, failStart: false };
window.Tone = { context: { state: 'running' }, start: async () => {} };
window.core = {
  sequences: { clone: s => structuredClone(s) },
  midiToSequenceProto: bytes => ({ marker: new TextDecoder().decode(bytes), notes: [{startTime:0,endTime:1,pitch:60}], totalTime:60, tempos:[{time:0,qpm:120}] }),
  SoundFontPlayer: class {
    loadSamples(seq) { __synth.loads.push(seq.marker); return new Promise((resolve, reject) => __synth.pending.push({resolve,reject})); }
    isPlaying() { return __synth.playing; }
    stop() { __synth.playing = false; }
    start(seq, tempo, offset) {
      __synth.starts.push({marker:seq.marker, offset});
      if (__synth.failStart) return Promise.reject(new Error('start failed'));
      __synth.playing = true; return new Promise(() => {});
    }
  },
  PianoRollSVGVisualizer: class { redraw() {} }
};`;

(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const base = `http://127.0.0.1:${server.address().port}/`;
  const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
  const failures = [], pageErrors = [];
  const check = async (name, fn) => {
    try { await fn(); console.log('PASS ' + name); }
    catch (e) { failures.push(name + ': ' + e.message); console.error('FAIL ' + name + ': ' + e.message); }
  };
  try {
    const ctx = await browser.newContext();
    const mp3 = fs.readFileSync(path.join(root, piece.preview_url));
    await ctx.route(/upload\.wikimedia\.org|archive\.org\/download|github\.com\/LaDoger\/music-library\/releases\/download/, r => r.fulfill({ contentType: 'audio/mpeg', body: mp3 }));
    await ctx.route('**/files/**/*.mid', r => r.fulfill({ body: r.request().url(), contentType: 'audio/midi' }));
    await ctx.route('**/assets/vendor/midi-player.bundle.js', r => r.fulfill({ body: fakeSynth, contentType: 'text/javascript' }));
    const fresh = async () => {
      const p = await ctx.newPage(); p.on('pageerror', e => pageErrors.push(e.message));
      await p.goto(base + '?id=' + piece.id); await p.waitForSelector('.listen-btn.m-midi'); return p;
    };
    const loaded = async p => {
      await p.locator('.listen-btn.m-midi').click();
      await p.waitForFunction(() => window.__synth?.pending.length === 1);
    };
    const resolveSamples = async p => {
      await p.evaluate(() => __synth.pending.shift().resolve());
      await p.waitForFunction(() => document.querySelector('#pBtn').getAttribute('aria-label') === 'Pause' && !document.querySelector('#player').classList.contains('loading'));
    };

    await check('player Tab cycle and stop focus', async () => {
      const p = await fresh();
      await p.locator('.listen-btn.m-preview').click();
      await p.locator('#pClose').focus(); await p.keyboard.press('Tab');
      assert.equal(await p.evaluate(() => document.activeElement.classList.contains('drawer-close')), true, 'Tab from player close must wrap to details');
      await p.locator('#pBtn').focus(); await p.keyboard.press('Shift+Tab');
      assert.equal(await p.evaluate(() => !!document.activeElement.closest('.drawer-panel')), true, 'Shift+Tab from first player control must reach last detail control');
      await p.locator('#pClose').click();
      assert.equal(await p.evaluate(() => !!document.activeElement.closest('.drawer-panel')), true, 'stopping player must restore visible focus');
      await p.close();
    });
    await check('detail to composer navigation stays closed after reload', async () => {
      const p = await fresh(); await p.locator('.d-composer').click();
      assert.equal(new URL(p.url()).searchParams.has('id'), false, 'composer URL must remove closed detail');
      await p.reload(); await p.waitForSelector('#composerHero:not([hidden])');
      assert.equal(await p.locator('#drawer').getAttribute('aria-hidden'), 'true');
      await p.goBack(); await p.waitForSelector('#drawer.open');
      await p.close();
    });
    await check('cancel library load before switching to recording', async () => {
      const p = await fresh(); let releaseLibrary, arrived;
      const gate = new Promise(r => { releaseLibrary = r; });
      const request = new Promise(r => { arrived = r; });
      const midiRequests = [];
      p.on('request', r => { if (r.url().endsWith('.mid')) midiRequests.push(r.url()); });
      await p.route('**/assets/vendor/midi-player.bundle.js', async r => { arrived(); await gate; await r.fulfill({ body: fakeSynth, contentType: 'text/javascript' }); });
      await p.locator('.listen-btn.m-midi').click(); await request;
      await p.locator('.listen-btn.m-preview').click(); releaseLibrary();
      await p.waitForFunction(() => !!window.__synth); await p.waitForTimeout(100);
      assert.equal(midiRequests.length, 0, 'cancelled MIDI request must not start after library resolves');
      assert.equal(await p.evaluate(() => __synth.loads.length), 0);
      assert.equal(await p.locator('#pMode').textContent(), 'Preview · 15 s');
      await p.close();
    });
    await check('pause during sample loading then resume waits for ready samples', async () => {
      const p = await fresh(); await loaded(p);
      await p.locator('#pBtn').click(); await p.locator('#pBtn').click();
      await p.waitForTimeout(100);
      assert.equal(await p.evaluate(() => __synth.starts.length), 0, 'resume must wait for samples');
      await p.waitForFunction(() => __synth.pending.length === 2);
      await p.evaluate(() => __synth.pending.shift().resolve()); await p.waitForTimeout(100);
      assert.equal(await p.evaluate(() => __synth.starts.length), 0, 'cancelled sample completion must not play');
      await resolveSamples(p);
      assert.equal(await p.evaluate(() => __synth.starts.length), 1);
      await p.close();
    });
    await check('sample failure retries load and start failure clears playing state', async () => {
      const p = await fresh(); await loaded(p);
      await p.evaluate(() => __synth.pending.shift().reject(new Error('sample failed')));
      await p.waitForFunction(() => !document.querySelector('#player').classList.contains('loading'));
      await p.locator('#pBtn').click(); await p.waitForTimeout(100);
      assert.equal(await p.evaluate(() => __synth.starts.length), 0, 'failed load must retry samples');
      await p.waitForFunction(() => __synth.pending.length === 1);
      await p.evaluate(() => { __synth.failStart = true; __synth.pending.shift().resolve(); });
      await p.waitForFunction(() => __synth.starts.length === 1);
      await p.waitForTimeout(100);
      assert.equal(await p.locator('#pBtn').getAttribute('aria-label'), 'Play', 'failed synth start must not show Pause');
      await p.close();
    });
    await check('loading a different piece clears old duration and ignores old completion', async () => {
      const p = await fresh(); await loaded(p); await resolveSamples(p);
      await p.keyboard.press('Escape');
      await p.evaluate(id => { const b = document.createElement('button'); b.dataset.act='open'; b.dataset.id=id; document.body.append(b); b.click(); b.remove(); }, other.id);
      await p.locator('.listen-btn.m-midi').click();
      await p.waitForFunction(() => __synth.pending.length === 1);
      assert.equal(await p.locator('#pTime').textContent(), '0:00 / –:––', 'new loading piece must not inherit previous duration');
      await p.locator('#pModes [data-pmode="preview"]').click();
      await p.evaluate(() => __synth.pending.shift().resolve()); await p.waitForTimeout(100);
      assert.equal(await p.evaluate(() => __synth.playing), false);
      assert.equal(await p.evaluate(() => __synth.starts.length), 1);
      await p.close();
    });
    await check('mobile player seek target and viewport bounds', async () => {
      const p = await fresh(); await p.locator('.listen-btn.m-preview').click();
      for (const width of [320, 390, 560, 720, 1280]) {
        await p.setViewportSize({width, height:844});
        assert.equal(await p.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true, width + 'px page overflow');
        const seek = await p.locator('#pBar').boundingBox();
        assert(seek.height >= 24, 'seek touch target should be at least 24px');
        assert.equal(await p.evaluate(() => [...document.querySelectorAll('#player button, #player input, #pBar')].filter(x => x.getClientRects().length).every(x => {
          const b = x.getBoundingClientRect(); return b.left >= 0 && b.right <= innerWidth && b.bottom <= innerHeight;
        })), true, width + 'px player controls clipped');
      }
      await p.close();
    });
    await check('axe WCAG A/AA and screenshots across composer/works/player views', async () => {
      const p = await ctx.newPage();
      for (const [name, query, width] of [
        ['composers-desktop','',1280], ['composer-mobile','?composer=Johann%20Sebastian%20Bach',390],
        ['works-grid','?view=works',1280], ['works-list','?view=works&layout=list',390],
        ['drawer-player-mobile','?id='+piece.id,320],
      ]) {
        await p.setViewportSize({width, height:900}); await p.goto(base+query); await p.waitForSelector('#resultCount b');
        if (name.startsWith('drawer')) await p.locator('.listen-btn.m-preview').click();
        await p.addScriptTag({path:require.resolve('axe-core/axe.min.js')});
        const result = await p.evaluate(async () => (await axe.run(document, {runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}})).violations.map(x => ({id:x.id, nodes:x.nodes.map(n=>n.target)})));
        assert.deepEqual(result, [], name + ' accessibility violations: ' + JSON.stringify(result));
        await p.screenshot({path:'/tmp/music-review-'+name+'.png',fullPage:false});
      }
      await p.close();
    });
    assert.deepEqual(pageErrors, [], 'browser exceptions');
    assert.deepEqual(failures, [], 'review regressions');
  } finally { await browser.close(); }
})().catch(e => { console.error(e.message); process.exitCode = 1; }).finally(() => server.close());
