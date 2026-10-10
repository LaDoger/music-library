#!/usr/bin/env node
/* Watch player sync drift: does the score cursor follow the audio?
   Ground truth is independent of assets/watch.js:
   - scripts/watch_truth.py unrolls the MusicXML (repeats, voltas, D.C./D.S./Fine/Coda) into a
     timeline of measures and note onsets, cross-checked against the piece's MIDI;
   - the notes the audio engine actually triggers (Tone.Sampler calls, audio-clock times) are
     aligned to those score onsets by subsequence DTW; the last sounded onset plus elapsed time
     gives the true unrolled position in quarter notes.
   The cursor's measure + offset is placed on the same unrolled timeline (nearest occurrence of
   that measure); error = distance (quarter-note beats) from the window [last sounded onset, now],
   so a note-level cursor on the note being heard scores 0.
   Standalone: NODE_PATH=/tmp/music-ui-review/node_modules node scripts/watch_drift.cjs [id ...]
   Library: require('./watch_drift.cjs').measureDrift(page, baseUrl, id) */
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const root = process.env.WATCH_ROOT || path.resolve(__dirname, '..');
const DEFAULT_IDS = ['duchambge_ronde_des_pauvres', 'wagner_wwv75_elsa_procession', 'wagner_wwv86d_siegfried_funeral_march'];
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function truthFor(ids) {
  const out = JSON.parse(execFileSync('python3', [path.join(__dirname, 'watch_truth.py'), ...ids], { cwd: root, maxBuffer: 1 << 28 }).toString());
  return Object.fromEntries(out.map((t) => [t.id, t]));
}

// score onset groups [{u, p:Set}]
function groups(onsets) {
  const g = [];
  for (const [u, p] of onsets) {
    const last = g[g.length - 1];
    if (last && Math.abs(last.u - u) < 1e-6) last.p.add(p); else g.push({ u, p: new Set([p]) });
  }
  return g;
}
const jac = (a, b) => { let n = 0; for (const x of a) if (b.has(x)) n++; return n / (a.size + b.size - n || 1); };

// Subsequence DTW of the sounded onset groups A against score groups S. Returns the end index
// candidates (all equally good ends, e.g. identical repeated passages) and the path start.
function locate(A, S) {
  const k = A.length, N = S.length;
  let prev = new Float64Array(N), cur = new Float64Array(N);
  const back = [];
  for (let i = 0; i < k; i++) {
    const bk = new Int32Array(N);   // start index of the best path ending here
    for (let j = 0; j < N; j++) {
      const c = 1 - jac(A[i].p, S[j].p);
      if (i === 0) { cur[j] = c; bk[j] = j; continue; }
      let best = prev[j] + 0.5, from = back[i - 1][j];                       // two audio groups on one score group
      if (j > 0 && prev[j - 1] <= best) { best = prev[j - 1]; from = back[i - 1][j - 1]; }
      if (j > 0 && cur[j - 1] + 0.5 < best) { best = cur[j - 1] + 0.5; from = bk[j - 1]; }   // skipped score group
      cur[j] = c + best; bk[j] = from;
    }
    back.push(bk);
    [prev, cur] = [cur, prev];
  }
  let min = Infinity;
  for (let j = 0; j < N; j++) min = Math.min(min, prev[j]);
  const ends = [];
  for (let j = 0; j < N; j++) if (prev[j] <= min + 1e-9) ends.push({ j, start: back[k - 1][j] });
  return { ends, cost: min / k };
}

async function hook(page) {
  await page.evaluate(() => {
    if (window.__trigHooked) return;
    window.__trigHooked = true; window.__trig = [];
    const S = window.Tone.Sampler.prototype, orig = S.triggerAttackRelease;
    S.triggerAttackRelease = function (f, d, at, v) {
      const freq = typeof f === 'number' ? f : window.Tone.Frequency(f).toFrequency();
      window.__trig.push({ p: Math.round(69 + 12 * Math.log2(freq / 440)), at: at ?? window.Tone.context.rawContext.currentTime });
      return orig.apply(this, arguments);
    };
  });
}

async function sample(page) {
  return page.evaluate(() => ({ now: window.Tone.context.rawContext.currentTime, cursor: window.__watch.cursor, t: window.__watch.baseTime, measure: window.__watch.measure, trig: window.__trig.slice() }));
}

function evaluate(truth, S, smp) {
  const A = [];
  for (const n of smp.trig.filter((x) => x.at <= smp.now).sort((a, b) => a.at - b.at)) {
    const last = A[A.length - 1];
    if (last && n.at - last.at < 0.002) last.p.add(n.p); else A.push({ at: n.at, p: new Set([n.p]) });
  }
  const tail = A.slice(-12);
  if (tail.length < 3 || !smp.cursor) return { ok: false, why: tail.length < 3 ? 'too few sounded onsets' : 'no cursor' };
  const { ends, cost } = locate(tail, S);
  if (process.env.DRIFT_DEBUG) console.log('   tail', tail.map((g) => g.at.toFixed(2) + ':' + [...g.p].join('/')).join(' '), 'now', smp.now.toFixed(2), '\n   ends', ends.map((e) => `${S[e.start].u}->${S[e.j].u} [${[...S[e.j].p].join('/')}]`).join(' '), 'cursor', JSON.stringify(smp.cursor));
  const a0 = tail[0], a1 = tail[tail.length - 1];
  // True position: somewhere between the last sounded onset and "now" (extrapolated at the local
  // rate, never past the next onset). A note-level cursor anywhere in that window is exact.
  const trues = ends.map(({ j, start }) => {
    const rate = a1.at - a0.at > 0.2 && S[j].u > S[start].u ? (S[j].u - S[start].u) / (a1.at - a0.at) : 0;
    const next = j + 1 < S.length ? S[j + 1].u : truth.unrolled_q;
    return [S[j].u, Math.max(S[j].u, Math.min(S[j].u + Math.max(0, smp.now - a1.at) * rate, next - 1e-3))];
  });
  const occ = truth.measures.filter((r) => r.m === smp.cursor.m).map((r) => r.u0 + smp.cursor.off);
  let err = Infinity, best = null;
  for (const [lo, hi] of trues) for (const uc of occ) { const d = uc < lo ? lo - uc : uc > hi ? uc - hi : 0; if (d < err) { err = d; best = { ut: Math.min(hi, Math.max(lo, uc)), uc }; } }
  if (!occ.length) { err = Infinity; best = { ut: trues[0][1], uc: null }; }
  const uMeasure = (u) => { const r = truth.measures.find((x) => u >= x.u0 - 1e-6 && u < x.u0 + x.len - 1e-6) || truth.measures[truth.measures.length - 1]; return r.m; };
  return { ok: cost < 0.6, cost, err, trueMeasure: uMeasure(best.ut) + 1, cursorMeasure: smp.cursor.m + 1, u: best.ut, t: smp.t };
}

/* Plays the piece, samples ~8 positions (start + 7 seeks spread over the piece), returns rows. */
async function measureDrift(page, base, id, truth, opts = {}) {
  truth = truth || truthFor([id])[id];
  const S = groups(truth.onsets);
  const listen = opts.listen || 3200;
  await page.goto(base + '?watch=' + id + '&sound=salamander' + (opts.extra || ''));
  await page.waitForFunction((i) => window.__watch && window.__watch.id === i && window.__watch.ready, id, { timeout: 150000 });
  if (opts.tempo) await page.evaluate((t) => { const i = document.querySelector('#wTempo'); i.value = t; i.dispatchEvent(new Event('input')); }, opts.tempo);
  await hook(page);
  await page.click('#wPlay');
  await page.waitForFunction(() => window.__watch.playing);
  const { total, audioSrc } = await page.evaluate(() => ({ total: window.__watch.total, audioSrc: window.__watch.audioSrc }));
  const rows = [];
  const fracs = [0, 0.12, 0.25, 0.38, 0.5, 0.62, 0.75, 0.87];
  for (const f of fracs) {
    if (f > 0) {
      await page.evaluate((t) => { window.__trig.length = 0; window.__watch.seek(t); }, f * total);
      if (!(await page.evaluate(() => window.__watch.playing))) await page.click('#wPlay');
    }
    await sleep(listen);
    // slow passages: keep listening (up to 10 s) until enough onsets have sounded to locate them
    for (let k = 0; k < 17 && (await page.evaluate(() => new Set(window.__trig.filter((x) => x.at <= window.Tone.context.rawContext.currentTime).map((x) => Math.round(x.at * 30))).size)) < 6; k++) await sleep(400);
    const r = evaluate(truth, S, await sample(page));
    r.frac = f;
    rows.push(r);
  }
  await page.click('#wPlay').catch(() => {});
  const good = rows.filter((r) => r.ok);
  return { id, rows, total, audioSrc, max: good.length ? Math.max(...good.map((r) => r.err)) : NaN, mean: good.length ? good.reduce((a, r) => a + r.err, 0) / good.length : NaN, n: good.length, match: truth.match };
}

module.exports = { measureDrift, truthFor };

if (require.main === module) {
  const fs = require('node:fs');
  const http = require('node:http');
  const { chromium } = require('playwright');
  const ids = process.argv.slice(2).filter((a) => !a.startsWith('--'));
  const extra = (process.argv.find((a) => a.startsWith('--extra=')) || '').slice(8);
  const server = http.createServer((req, res) => {
    const name = decodeURIComponent(new URL(req.url, 'http://x').pathname).replace(/^\//, '') || 'index.html';
    const file = path.resolve(root, name);
    if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
    const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json' };
    res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
    fs.createReadStream(file).pipe(res);
  });
  (async () => {
    await new Promise((r) => server.listen(0, '127.0.0.1', r));
    const base = `http://127.0.0.1:${server.address().port}/`;
    const browser = await chromium.launch({ executablePath: process.env.CHROME_BIN || '/usr/bin/google-chrome', headless: true, args: ['--no-sandbox', '--autoplay-policy=no-user-gesture-required'] });
    const page = await (await browser.newContext({ viewport: { width: 1360, height: 860 } })).newPage();
    page.on('pageerror', (e) => console.log('pageerror: ' + e.message));
    const list = ids.length ? ids : DEFAULT_IDS;
    const truths = truthFor(list);
    const all = [];
    for (const id of list) {
      const r = await measureDrift(page, base, id, truths[id], { extra });
      all.push(r);
      console.log(`${id}  (truth/MIDI match ${(r.match * 100).toFixed(0)}%, ${truths[id].n_measures} measures, ${truths[id].n_unrolled} unrolled)`);
      for (const x of r.rows) console.log(x.ok ? `  ${(x.frac * 100).toFixed(0).padStart(3)}%  t=${x.t.toFixed(1).padStart(6)}s  true m${String(x.trueMeasure).padEnd(4)} cursor m${String(x.cursorMeasure).padEnd(4)} err ${x.err.toFixed(2)} beats  (dtw ${x.cost.toFixed(2)})` : `  ${(x.frac * 100).toFixed(0).padStart(3)}%  unreliable sample: ${x.why || 'dtw cost ' + x.cost.toFixed(2)}`);
      console.log(`  => max ${r.max.toFixed(2)}  mean ${r.mean.toFixed(2)} beats over ${r.n} samples`);
    }
    if (process.env.DRIFT_JSON) fs.writeFileSync(process.env.DRIFT_JSON, JSON.stringify(all, null, 1));
    await browser.close(); server.close();
  })();
}
