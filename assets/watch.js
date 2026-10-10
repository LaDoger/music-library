/* Watch player: engraved score (OpenSheetMusicDisplay) synced to live audio rendered in the
   browser from the score MIDI. Lazy-loaded by app.js on ?watch=<id>; adds no media files.
   Libraries: OSMD (BSD-3, jsDelivr, loaded here), Tone.js + Magenta core (vendor bundle, shared with
   the detail-page synth), Salamander Grand Piano samples (CC BY 3.0, tonejs.github.io). See docs/WATCH_PLAYER.md. */
(() => {
  "use strict";
  const OSMD_URL = "https://cdn.jsdelivr.net/npm/opensheetmusicdisplay@1.9.0/build/opensheetmusicdisplay.min.js";
  const BUNDLE_URL = "assets/vendor/midi-player.bundle.js";
  const SOUNDFONT = "https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus";
  const SALAMANDER = "https://tonejs.github.io/audio/salamander/";
  const XML_RE = /\.(mxl|musicxml|xml)$/i;

  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fmt = (s) => { s = Math.max(0, Math.round(s || 0)); return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`; };
  const loadScript = (src) => new Promise((res, rej) => {
    const s = document.createElement("script");
    s.src = src; s.onload = res; s.onerror = () => rej(new Error("could not load " + src));
    document.head.appendChild(s);
  });
  const libs = {};
  const lib = (k, fn) => (libs[k] ||= fn().catch((e) => { delete libs[k]; throw e; }));
  const loadBundle = () => lib("bundle", async () => { if (!window.core) await loadScript(BUNDLE_URL); if (!window.core || !window.Tone) throw new Error("synth library missing"); });
  const loadOSMD = () => lib("osmd", async () => { if (!window.opensheetmusicdisplay) await loadScript(OSMD_URL); });

  let ctx = null;       // app context from app.js
  let W = null;         // current session
  const prefs = { paper: localStorage.getItem("watchPaper") || "dark", view: "", tempo: 1 };

  /* ---------- helpers: item / sets ---------- */
  const natKey = (r) => (String(r.movement || r.title).match(/\d+/g) || []).map(Number);
  function setKey(r) {
    const t = r.title.includes(":") ? r.title.split(":")[0].trim() : "";
    return r.composer + "|" + (t || r.catalog || "");
  }
  function siblings(r) {
    const k = setKey(r);
    if (k.endsWith("|")) return [r];
    const byTitle = new Map();   // duplicate editions share a title: keep one (the open item wins)
    for (const x of ctx.rows) if (x.midi_play_url && setKey(x) === k && (!byTitle.has(x.title) || x.id === r.id)) byTitle.set(x.title, x);
    const list = [...byTitle.values()];
    list.sort((a, b) => { const A = natKey(a), B = natKey(b); for (let i = 0; i < Math.max(A.length, B.length); i++) { if ((A[i] ?? -1) !== (B[i] ?? -1)) return (A[i] ?? -1) - (B[i] ?? -1); } return a.id < b.id ? -1 : 1; });
    return list.length ? list : [r];
  }
  function upNext(r) {
    const set = siblings(r);
    const idx = set.findIndex((x) => x.id === r.id);
    const out = set.length > 1 ? set.slice(idx + 1) : [];
    const seen = new Set([r.id, ...out.map((x) => x.id)]);
    const same = ctx.rows.filter((x) => x.midi_play_url && x.composer === r.composer && !seen.has(x.id) && setKey(x) !== setKey(r));
    same.sort((a, b) => (b.has_editable_score - a.has_editable_score) || ((a.featured_rank || 9) - (b.featured_rank || 9)) || ((b.editors_pick_rank > 0) - (a.editors_pick_rank > 0)) || (a.title < b.title ? -1 : 1));
    return { set, next: out, more: same.slice(0, 12) };
  }

  /* ---------- tempo map (base seconds <-> quarter notes) ---------- */
  function tempoMap(seq) {
    const tpq = seq.ticksPerQuarter || 220;
    const ts = (seq.tempos && seq.tempos.length ? seq.tempos.slice() : [{ time: 0, qpm: 120 }]).sort((a, b) => a.time - b.time);
    const segs = []; let q = 0;
    for (let i = 0; i < ts.length; i++) {
      const t0 = i === 0 ? 0 : ts[i].time, qpm = ts[i].qpm || 120;
      if (i > 0) q += (t0 - segs[i - 1].t) * segs[i - 1].qpm / 60;
      segs.push({ t: t0, q, qpm });
    }
    return {
      tpq,
      qOf: (t) => { let s = segs[0]; for (const x of segs) { if (x.t <= t) s = x; else break; } return s.q + (t - s.t) * s.qpm / 60; },
      tOf: (q) => { let s = segs[0]; for (const x of segs) { if (x.q <= q) s = x; else break; } return s.t + (q - s.q) * 60 / s.qpm; },
    };
  }

  /* ---------- audio engines ---------- */
  // Piano-led (solo piano, or piano plus a sung line): use the Salamander grand for everything.
  const isPianoSeq = (seq) => { const ns = seq.notes.filter((n) => !n.isDrum); return ns.length > 0 && new Set(ns.map((n) => n.instrument || 0)).size <= 3 && ns.filter((n) => (n.program || 0) < 8).length >= 0.65 * ns.length && ns.every((n) => (n.program || 0) < 24 || (n.program || 0) >= 64 && (n.program || 0) < 80); };
  function pianoUrls() {
    const urls = {};
    for (let o = 0; o <= 8; o++) for (const [n, f] of [["C", "C"], ["D#", "Ds"], ["F#", "Fs"], ["A", "A"]]) {
      if ((o === 0 && n !== "A") || (o === 8 && n !== "C")) continue;
      urls[n + o] = f + o + ".mp3";
    }
    return urls;
  }
  function makeEngine(kind) {
    const core = window.core, Tone = window.Tone;
    const e = { kind, ready: false, playing: false, pos: 0, base: 0, started: 0, seq: null, gen: 0, onend: null };
    if (kind === "piano") {
      e.load = async (seq) => {
        e.seq = seq;
        e.notes = seq.notes.filter((n) => !n.isDrum).sort((a, b) => a.startTime - b.startTime);
        if (!e.sampler) {
          e.sampler = await new Promise((res, rej) => {
            const s = new Tone.Sampler({ urls: pianoUrls(), release: 1.2, baseUrl: SALAMANDER, onload: () => res(s), onerror: rej }).toDestination();
            setTimeout(() => rej(new Error("piano samples timed out")), 25000);
          });
        }
        e.ready = true;
      };
      e.now = () => Tone.context.rawContext.currentTime;
      e.position = () => (e.playing ? Math.min(e.pos + (e.now() - e.started), e.seq.totalTime) : e.pos);
      e.start = (offset) => {
        e.gen++; const gen = e.gen;
        e.pos = offset; e.started = e.now() + 0.08; e.playing = true;
        e.idx = e.notes.findIndex((n) => n.endTime > offset);
        if (e.idx < 0) e.idx = e.notes.length;
        clearInterval(e.timer);
        const pump = () => {
          if (gen !== e.gen) return;
          const p = e.position(), horizon = p + 0.35;
          while (e.idx < e.notes.length && e.notes[e.idx].startTime < horizon) {
            const n = e.notes[e.idx++];
            const at = e.started + (n.startTime - e.pos);
            const dur = Math.max(0.05, n.endTime - n.startTime);
            try { e.sampler.triggerAttackRelease(Tone.Frequency(n.pitch, "midi").toFrequency(), dur, Math.max(at, e.now()), (n.velocity || 80) / 127); } catch { /* sample not ready */ }
          }
          if (p >= e.seq.totalTime - 0.01) { e.playing = false; e.pos = e.seq.totalTime; clearInterval(e.timer); e.onend && e.onend(); }
        };
        e.timer = setInterval(pump, 60); pump();
      };
      e.pause = () => { e.pos = e.position(); e.playing = false; e.gen++; clearInterval(e.timer); try { e.sampler.releaseAll(); } catch { /* ok */ } };
    } else {
      e.load = async (seq) => {
        e.seq = seq;
        if (!e.sfp) e.sfp = new core.SoundFontPlayer(SOUNDFONT, undefined, undefined, undefined, { run: () => {}, stop: () => {} });
        await e.sfp.loadSamples(seq);
        e.ready = true;
      };
      e.position = () => (e.playing ? Math.min(e.pos + (performance.now() - e.started) / 1000, e.seq.totalTime) : e.pos);
      e.start = (offset) => {
        const gen = ++e.gen;
        e.pos = offset; e.started = performance.now(); e.playing = true;
        if (e.sfp.isPlaying()) e.sfp.stop();
        Promise.resolve().then(() => (gen === e.gen ? e.sfp.start(e.seq, undefined, offset) : null)).then(() => {
          if (gen === e.gen && e.playing) { e.playing = false; e.pos = e.seq.totalTime; e.onend && e.onend(); }
        }).catch(() => { if (gen === e.gen) { e.playing = false; W && W.toast("Audio unavailable. Press play to retry."); } });
      };
      e.pause = () => { e.pos = e.position(); e.playing = false; e.gen++; if (e.sfp && e.sfp.isPlaying()) e.sfp.stop(); };
    }
    return e;
  }
  function scaleSeq(seq, f) {
    const s = window.core.sequences.clone(seq);
    for (const n of s.notes) { n.startTime /= f; n.endTime /= f; }
    for (const c of s.controlChanges || []) c.time /= f;
    for (const p of s.pitchBends || []) p.time /= f;
    for (const t of s.tempos || []) { t.time /= f; t.qpm *= f; }
    s.totalTime /= f;
    return s;
  }

  /* ---------- score (OSMD) ---------- */
  const toBinary = (buf) => { const u = new Uint8Array(buf); let s = ""; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return s; };
  async function loadScore(w, file) {
    await loadOSMD();
    const res = await fetch(file);
    if (!res.ok) throw new Error("score " + res.status);
    const isZip = /\.mxl$/i.test(file);
    const data = isZip ? toBinary(await res.arrayBuffer()) : await res.text();
    const o = new window.opensheetmusicdisplay.OpenSheetMusicDisplay(w.osmdEl, {
      backend: "svg", autoResize: false, drawTitle: false, drawSubtitle: false, drawComposer: false, drawLyricist: false,
      drawCredits: false, drawPartNames: true, followCursor: false, drawingParameters: "default", pageFormat: "Endless",
    });
    await o.load(data);
    w.osmd = o;
    layoutScore(w);
    // Cursor step table: whole-note timestamps and measure index per step.
    o.cursor.show();
    cursorA11y(w);
    const it = o.cursor.Iterator; w.steps = [];
    while (!it.EndReached) { w.steps.push({ q: it.currentTimeStamp.RealValue * 4, m: it.CurrentMeasureIndex }); o.cursor.next(); }
    o.cursor.reset(); w.stepIdx = 0;
    const last = w.steps[w.steps.length - 1];
    w.scoreQ = last ? last.q + 1 : 1;
  }
  function cursorA11y(w) {
    const el = w.osmd && w.osmd.cursor.cursorElement;
    if (el) { el.alt = ""; el.setAttribute("role", "presentation"); }
  }
  function layoutScore(w) {
    const o = w.osmd, box = w.paper;
    const width = Math.max(280, Math.min(box.clientWidth, 1500));
    w.osmdEl.style.width = width + "px";
    o.zoom = width < 600 ? 0.7 : width > 1200 ? 1.1 : 1;
    o.render();
    const unit = 10 * o.zoom;
    const sysMap = new Map(); w.sys = []; w.meas = [];
    o.GraphicSheet.MeasureList.forEach((staves, mi) => {
      let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity, sysObj = null;
      for (const g of staves) {
        if (!g) continue;
        const ps = g.PositionAndShape, ap = ps.AbsolutePosition;
        x0 = Math.min(x0, ap.x + ps.BorderLeft); x1 = Math.max(x1, ap.x + ps.BorderRight);
        y0 = Math.min(y0, ap.y + ps.BorderTop); y1 = Math.max(y1, ap.y + ps.BorderBottom);
        sysObj = sysObj || (g.ParentStaffLine && g.ParentStaffLine.ParentMusicSystem);
      }
      if (!isFinite(x0)) { w.meas[mi] = null; return; }
      if (!sysMap.has(sysObj)) { sysMap.set(sysObj, w.sys.length); w.sys.push({ top: Infinity, bottom: -Infinity, measures: [] }); }
      const si = sysMap.get(sysObj), s = w.sys[si];
      s.top = Math.min(s.top, y0 * unit); s.bottom = Math.max(s.bottom, y1 * unit); s.measures.push(mi);
      w.meas[mi] = { x: x0 * unit, y: y0 * unit, w: (x1 - x0) * unit, h: (y1 - y0) * unit, sys: si };
    });
    w.svgW = width;
  }

  /* ---------- session ---------- */
  function shell() {
    const root = $("#watch");
    root.hidden = false;
    root.className = "watch paper-" + prefs.paper;
    root.innerHTML = `
      <div class="w-main">
        <header class="w-bar">
          <button class="w-icon" type="button" data-w="close" aria-label="Close player">←</button>
          <div class="w-heading"><div class="w-comp" id="wComp"></div><h2 class="w-title" id="wTitle" tabindex="-1"></h2></div>
          <div class="w-opts">
            <div class="w-seg" role="group" aria-label="View">
              <button type="button" data-view="score" aria-pressed="false">Score</button>
              <button type="button" data-view="roll" aria-pressed="false">Piano roll</button>
              <button type="button" data-view="both" aria-pressed="false">Both</button>
            </div>
            <button class="w-chip" type="button" data-w="paper" aria-pressed="false"></button>
            <button class="w-icon" type="button" data-w="full" aria-label="Fullscreen" title="Fullscreen (F)">⛶</button>
          </div>
        </header>
        <div class="w-stage" id="wStage" data-vmode="score">
          <div class="w-paper" id="wPaper" role="region" aria-label="Sheet music" tabindex="-1">
            <div class="w-slide" id="wSlide">
              <div class="w-osmd" id="wOsmd"></div>
              <div class="w-sysband" id="wBand" hidden></div>
              <div class="w-measure" id="wMeasure" hidden></div>
            </div>
            <div class="w-fade-top"></div><div class="w-fade-bot"></div>
            <div class="w-page" id="wPage"></div>
          </div>
          <canvas class="w-roll" id="wRoll" aria-label="Piano roll"></canvas>
          <div class="w-card" id="wCard" aria-hidden="true"><div class="wc-comp"></div><div class="wc-title"></div><div class="wc-cat"></div></div>
          <div class="w-status" id="wStatus" role="status" aria-live="polite">Loading…</div>
        </div>
        <div class="w-controls">
          <div class="w-seek" id="wSeek" role="slider" tabindex="0" aria-label="Position" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><span id="wProg"></span></div>
          <div class="w-row">
            <button class="w-icon" type="button" data-w="prev" aria-label="Previous movement" disabled>⏮</button>
            <button class="w-play" id="wPlay" type="button" data-w="play" aria-label="Play" disabled>▶</button>
            <button class="w-icon" type="button" data-w="next" aria-label="Next movement" disabled>⏭</button>
            <span class="w-time" id="wTime">0:00 / 0:00</span>
            <span class="w-meas" id="wMeas"></span>
            <label class="w-tempo"><span>Tempo</span><input type="range" id="wTempo" min="0.5" max="1.5" step="0.05" value="1"><output id="wTempoOut">100%</output></label>
          </div>
        </div>
        <footer class="w-credits" id="wCredits"></footer>
      </div>
      <aside class="w-side" aria-label="Up next"><h3>Up next</h3><div id="wNext"></div></aside>`;
    return root;
  }

  async function open(id, context) {
    ctx = context;
    if (W) teardown();
    const r = ctx.byId.get(id);
    const root = shell();
    const w = W = {
      id, r, root, gen: Math.random(), toast: (m) => setStatus(m), q: (s) => $(s, root),
      stage: $("#wStage", root), paper: $("#wPaper", root), slide: $("#wSlide", root), osmdEl: $("#wOsmd", root),
      curSys: -1, curMeasure: -1, turns: 0, playing: false, hasScore: false, ended: false,
    };
    w.view = prefs.view;
    const setStatus = (m) => { const s = w.q("#wStatus"); if (!s) return; s.textContent = m || ""; s.hidden = !m; };
    w.setStatus = setStatus;
    $("#wComp", root).textContent = r.composer;
    $("#wTitle", root).textContent = r.title + (r.movement && !r.title.includes(r.movement) ? " · " + r.movement : "");
    document.title = `${r.title} · ${r.composer} — Watch · Music Library`;
    $("#wTitle", root).focus({ preventScroll: true });
    bindUI(w);
    renderNext(w);
    exposeState(w);
    try {
      const full = await ctx.loadFull(r);
      if (W !== w) return;
      renderCredits(w, full);
      fillCard(w, full);
      const xml = (full.score_files || []).find((f) => XML_RE.test(f));
      w.hasXml = !!xml;
      if (!w.view) w.view = xml ? "score" : "roll";
      setView(w, w.view);
      await loadBundle();
      const res = await fetch(full.midi_play_url);
      if (!res.ok) throw new Error("MIDI " + res.status);
      const base = window.core.midiToSequenceProto(new Uint8Array(await res.arrayBuffer()));
      if (W !== w) return;
      w.base = base; w.tm = tempoMap(base); w.total = base.totalTime;
      w.kind = isPianoSeq(base) ? "piano" : "sf";
      if (xml) {
        setStatus("Engraving the score…");
        await new Promise((res2) => setTimeout(res2, 30));
        try { await loadScore(w, xml); w.hasScore = true; } catch (err) { console.warn("score failed", err); w.hasScore = false; if (w.view !== "roll") setView(w, "roll"); setStatus("Score could not be drawn; showing the piano roll."); }
        if (W !== w) return;
      }
      if (w.hasScore) { w.scale = w.scoreQ > 0 ? w.tm.qOf(w.total) / w.scoreQ : 1; if (Math.abs(w.scale - 1) < 0.03) w.scale = 1; }
      w.rollNotes = base.notes.filter((n) => !n.isDrum);
      await prepareAudio(w);
      if (W !== w) return;
      w.ready = true;
      renderCredits(w, full);
      setStatus(w.kind === "piano" ? "" : "");
      w.q("#wPlay").disabled = false;
      w.q("#wPlay").focus({ preventScroll: true });
      showCard(w);
      sync(w, true);
      loop(w);
    } catch (err) {
      if (W !== w) return;
      console.warn(err);
      setStatus("Could not load this piece: " + err.message);
    }
  }

  async function prepareAudio(w) {
    const f = prefs.tempo;
    w.q("#wTempo").value = f; w.q("#wTempoOut").textContent = Math.round(f * 100) + "%";
    w.scaled = scaleSeq(w.base, f);
    w.setStatus(w.kind === "piano" ? "Loading piano samples…" : "Loading orchestral samples…");
    let eng = makeEngine(w.kind);
    try { await eng.load(w.scaled); }
    catch (err) {
      if (w.kind !== "piano") throw err;
      console.warn("piano samples failed, falling back to SGM+", err);
      w.kind = "sf"; eng = makeEngine("sf"); await eng.load(w.scaled);
    }
    eng.onend = () => onEnded(w);
    w.engine = eng; w.tempo = f;
  }

  /* ---------- sync / animation ---------- */
  const basePos = (w) => (w.engine ? w.engine.position() * w.tempo : 0);   // base seconds
  function stepAt(w, t) {
    let q = w.tm.qOf(t);
    if (w.scale !== 1) q /= w.scale;
    const s = w.steps; let lo = 0, hi = s.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (s[mid].q <= q + 1e-6) lo = mid; else hi = mid - 1; }
    return lo;
  }
  function sync(w, force) {
    if (!w.engine) return;
    const t = basePos(w), total = w.total;
    w.q("#wProg").style.width = (total ? Math.min(100, t / total * 100) : 0) + "%";
    const seek = w.q("#wSeek");
    seek.setAttribute("aria-valuenow", String(Math.round(t / total * 100)));
    seek.setAttribute("aria-valuetext", `${fmt(t / w.tempo)} of ${fmt(total / w.tempo)}`);
    w.q("#wTime").textContent = `${fmt(t / w.tempo)} / ${fmt(total / w.tempo)}`;
    if (w.hasScore && w.steps.length) {
      const idx = stepAt(w, t);
      if (idx !== w.stepIdx || force) {
        const c = w.osmd.cursor;
        if (idx === w.stepIdx + 1) c.next();
        else if (idx !== w.stepIdx) { c.reset(); for (let i = 0; i < idx; i++) c.next(); }
        c.update();
        w.stepIdx = idx;
        highlight(w, w.steps[idx].m, force);
      } else if (force) highlight(w, w.steps[idx].m, true);
    }
    exposeState(w);
  }
  function highlight(w, mi, force) {
    const m = w.meas[mi]; if (!m) return;
    const box = w.q("#wMeasure"), band = w.q("#wBand");
    if (mi !== w.curMeasure || force) {
      w.curMeasure = mi;
      const pad = 6;
      box.hidden = false; box.style.cssText = `left:${m.x - pad}px;top:${m.y - pad}px;width:${m.w + 2 * pad}px;height:${m.h + 2 * pad}px`;
      w.q("#wMeas").textContent = `Measure ${mi + 1}${w.meas.length ? " / " + w.meas.length : ""}`;
    }
    if (m.sys !== w.curSys || force) {
      const first = w.curSys < 0 || force;
      const changed = m.sys !== w.curSys;
      w.curSys = m.sys;
      const s = w.sys[m.sys];
      band.hidden = false; band.style.cssText = `top:${s.top - 14}px;height:${s.bottom - s.top + 28}px;width:${w.svgW}px`;
      const stageH = w.paper.clientHeight;
      const target = Math.max(0, s.top - Math.min(60, stageH * 0.08));
      w.slide.classList.toggle("no-anim", !!first && !w.playing);
      w.slide.style.transform = `translate3d(0,${-target}px,0)`;
      if (changed && !first) w.turns++;
      w.q("#wPage").textContent = `System ${m.sys + 1} / ${w.sys.length}`;
    }
  }
  function loop(w) {
    if (W !== w) return;
    if (w.engine && (w.engine.playing || w.dirty)) { sync(w); w.dirty = false; }
    if (w.view !== "score") drawRoll(w);
    w.raf = requestAnimationFrame(() => loop(w));
  }
  function drawRoll(w) {
    const cv = w.q("#wRoll"); if (!cv || cv.offsetParent === null) return;
    const dpr = window.devicePixelRatio || 1, cw = cv.clientWidth, ch = cv.clientHeight;
    if (cv.width !== Math.round(cw * dpr) || cv.height !== Math.round(ch * dpr)) { cv.width = Math.round(cw * dpr); cv.height = Math.round(ch * dpr); }
    const g = cv.getContext("2d"); g.setTransform(dpr, 0, 0, dpr, 0, 0);
    const light = prefs.paper === "light";
    g.fillStyle = light ? "#f4ecd8" : "#0e0f13"; g.fillRect(0, 0, cw, ch);
    const t = basePos(w), win = 8 / 1, headX = cw * 0.22, pps = cw * 0.78 / win;   // 8 base-seconds visible ahead
    const lo = 21, hi = 108, nh = Math.max(2, ch / (hi - lo + 1));
    g.fillStyle = light ? "rgba(0,0,0,.05)" : "rgba(255,255,255,.04)";
    for (let p = lo; p <= hi; p++) if ([1, 3, 6, 8, 10].includes(p % 12)) g.fillRect(0, ch - (p - lo + 1) * nh, cw, nh);
    const cols = ["#d8c49a", "#8fb8de", "#c98fae", "#9ccf9a", "#e0a064", "#a99be0"];
    for (const n of w.rollNotes) {
      const x = headX + (n.startTime - t) * pps, x2 = headX + (n.endTime - t) * pps;
      if (x2 < 0 || x > cw) continue;
      const on = n.startTime <= t && n.endTime > t;
      g.globalAlpha = on ? 1 : 0.62;
      g.fillStyle = on ? (light ? "#8a5a00" : "#fff1c4") : cols[(n.instrument || 0) % cols.length];
      g.fillRect(x, ch - (n.pitch - lo + 1) * nh, Math.max(2, x2 - x - 1), Math.max(1.5, nh - 0.5));
    }
    g.globalAlpha = 1;
    g.fillStyle = "#e2c48c"; g.fillRect(headX - 1, 0, 2, ch);
  }

  /* ---------- transport ---------- */
  async function play(w) {
    if (!w.ready) return;
    try { if (window.Tone.context.state !== "running") await window.Tone.start(); } catch { /* retried on next click */ }
    hideCard(w);
    const e = w.engine;
    const from = e.pos >= w.scaled.totalTime - 0.05 ? 0 : e.pos;
    w.playing = true; e.start(from); setPlayUI(w);
  }
  function pause(w) { if (!w.engine) return; w.engine.pause(); w.playing = false; setPlayUI(w); sync(w); }
  function setPlayUI(w) {
    const b = w.q("#wPlay"); const on = w.engine && w.engine.playing;
    b.textContent = on ? "❚❚" : "▶"; b.setAttribute("aria-label", on ? "Pause" : "Play");
    w.root.classList.toggle("is-playing", !!on);
  }
  function seek(w, baseT) {
    if (!w.ready) return;
    const e = w.engine, t = Math.max(0, Math.min(w.total - 0.01, baseT)) / w.tempo;
    if (e.playing) e.start(t); else e.pos = t;
    sync(w, true);
  }
  function setTempo(w, f) {
    f = Math.max(0.5, Math.min(1.5, f || 1));
    prefs.tempo = f;
    w.q("#wTempoOut").textContent = Math.round(f * 100) + "%";
    if (!w.ready || f === w.tempo) return;
    const e = w.engine, t = basePos(w), was = e.playing;
    if (was) e.pause();
    const scaled = scaleSeq(w.base, f);
    w.scaled = scaled; e.seq = scaled;
    if (e.kind === "piano") e.notes = scaled.notes.filter((n) => !n.isDrum).sort((a, b) => a.startTime - b.startTime);
    w.tempo = f; e.pos = t / f;
    // Soundfont players keep per-sequence sample state, so reload cheaply (cached by URL).
    const go = () => { if (was) e.start(e.pos); sync(w, true); setPlayUI(w); };
    if (e.kind === "sf") e.sfp.loadSamples(scaled).then(go); else go();
  }
  function onEnded(w) {
    if (W !== w) return;
    w.ended = true; setPlayUI(w); sync(w);
    const { set } = upNext(w.r);
    const idx = set.findIndex((x) => x.id === w.r.id);
    if (set.length > 1 && idx >= 0 && idx < set.length - 1) go(set[idx + 1].id, true);
  }
  function go(id, autoplay) {
    if (!ctx.byId.get(id)) return;
    ctx.navigate(id, false);
    const keep = autoplay;
    open(id, ctx).then(() => { if (keep && W && W.id === id) autoplayWhenReady(W); });
  }
  function autoplayWhenReady(w) {
    if (!w.ready) return;
    play(w);
  }

  /* ---------- UI ---------- */
  function setView(w, v) {
    if (v !== "score" && !w.rollNotes && !w.hasXml) { /* roll data arrives after MIDI loads */ }
    w.view = v; prefs.view = v;
    w.stage.dataset.vmode = v;
    w.root.querySelectorAll(".w-seg [data-view]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === v)));
    if (w.hasScore) requestAnimationFrame(() => { w.dirty = true; });
  }
  function setPaper(w, p) {
    prefs.paper = p; localStorage.setItem("watchPaper", p);
    w.root.className = w.root.className.replace(/paper-\w+/, "paper-" + p) + "";
    const b = w.q('[data-w="paper"]'); b.textContent = p === "dark" ? "Dark paper" : "Light paper"; b.setAttribute("aria-pressed", String(p === "light"));
  }
  function bindUI(w) {
    const root = w.root;
    setPaper(w, prefs.paper);
    root.onclick = (e) => {
      const b = e.target.closest("[data-w],[data-view],[data-next]"); if (!b) return;
      if (b.dataset.view) return setView(w, b.dataset.view);
      if (b.dataset.next) { e.preventDefault(); return go(b.dataset.next, false); }
      switch (b.dataset.w) {
        case "close": return ctx.close();
        case "play": return w.engine && w.engine.playing ? pause(w) : play(w);
        case "paper": return setPaper(w, prefs.paper === "dark" ? "light" : "dark");
        case "full": return toggleFull(w);
        case "prev": { const { set } = upNext(w.r); const i = set.findIndex((x) => x.id === w.r.id); if (basePos(w) > 3 || i <= 0) return seek(w, 0); return go(set[i - 1].id, false); }
        case "next": { const { next } = upNext(w.r); if (next.length) go(next[0].id, false); return; }
      }
    };
    w.q("#wTempo").oninput = (e) => setTempo(w, +e.target.value);
    const bar = w.q("#wSeek");
    const frac = (e) => { const b = bar.getBoundingClientRect(); return Math.max(0, Math.min(1, (e.clientX - b.left) / b.width)); };
    let drag = false;
    bar.onpointerdown = (e) => { drag = true; bar.setPointerCapture(e.pointerId); seek(w, frac(e) * w.total); };
    bar.onpointermove = (e) => { if (drag) seek(w, frac(e) * w.total); };
    bar.onpointerup = bar.onpointercancel = () => { drag = false; };
    bar.onkeydown = (e) => {
      const step = { ArrowLeft: -5, ArrowRight: 5, ArrowDown: -5, ArrowUp: 5, PageDown: -30, PageUp: 30 }[e.key];
      if (e.key === "Home") seek(w, 0); else if (e.key === "End") seek(w, w.total - 0.5);
      else if (step) seek(w, basePos(w) + step * w.tempo); else return;
      e.preventDefault();
    };
    w.keys = (e) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const t = e.target;
      if (e.key === "Escape") { if (document.fullscreenElement) return; e.preventDefault(); return ctx.close(); }
      if (t.matches && t.matches("input[type=range], [role=slider]")) { if (e.key !== " ") return; }
      if (e.key === " " || e.code === "Space") { if (t.matches && t.matches("button, a")) return; e.preventDefault(); w.q("#wPlay").click(); }
      else if (e.key === "f" || e.key === "F") toggleFull(w);
    };
    document.addEventListener("keydown", w.keys);
    w.trap = (e) => {
      if (e.key !== "Tab") return;
      const f = [...root.querySelectorAll("button, a[href], input, [tabindex='0']")].filter((x) => !x.disabled && x.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && (document.activeElement === first || !root.contains(document.activeElement))) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && (document.activeElement === last || !root.contains(document.activeElement))) { e.preventDefault(); first.focus(); }
    };
    document.addEventListener("keydown", w.trap);
    let rt = 0;
    w.ro = new ResizeObserver(() => {
      clearTimeout(rt);
      rt = setTimeout(() => {
        if (!w.hasScore || !w.paper.clientWidth || Math.abs(w.paper.clientWidth - w.lastW) < 4) return;
        w.lastW = w.paper.clientWidth; relayout(w);
      }, 250);
    });
    w.lastW = 0;
    w.ro.observe(w.paper);
    w.onFs = () => { w.q('[data-w="full"]').setAttribute("aria-pressed", String(!!document.fullscreenElement)); };
    document.addEventListener("fullscreenchange", w.onFs);
  }
  function relayout(w) {
    layoutScore(w);
    w.osmd.cursor.show(); cursorA11y(w); w.osmd.cursor.reset(); w.stepIdx = 0; w.curSys = -1; w.curMeasure = -1;
    sync(w, true);
  }
  function toggleFull(w) {
    if (document.fullscreenElement) document.exitFullscreen(); else if (w.root.requestFullscreen) w.root.requestFullscreen().catch(() => {});
  }

  function renderNext(w) {
    const { set, next, more } = upNext(w.r);
    const item = (x, tag) => `<a class="wn" href="?watch=${encodeURIComponent(x.id)}" data-next="${esc(x.id)}"><span class="wn-t">${esc(x.title.includes(":") && set.length > 1 ? (x.movement || x.title) : x.title)}</span><span class="wn-s">${esc(tag || x.composer)}${x.catalog ? " · " + esc(x.catalog) : ""}</span></a>`;
    w.q("#wNext").innerHTML = (next.length ? `<h4>Next in this work</h4>${next.map((x) => item(x, x.movement)).join("")}` : "")
      + (more.length ? `<h4>More by ${esc(w.r.composer)}</h4>${more.map((x) => item(x)).join("")}` : "")
      + (!next.length && !more.length ? "<p class='wn-empty'>Nothing else queued.</p>" : "");
    const idx = set.findIndex((x) => x.id === w.r.id);
    w.q('[data-w="prev"]').disabled = false;
    w.q('[data-w="next"]').disabled = !next.length;
    if (set.length > 1) w.q("#wComp").textContent = `${w.r.composer} · ${idx + 1} of ${set.length}`;
  }
  function renderCredits(w, f) {
    const lic = { clean: "Public domain / CC0 score", attribution: "Credit required (CC BY)", sharealike: "ShareAlike", flagged: "Flagged: read the legal notes", unverified: "Unverified: not cleared for publishing" }[f.licence_status] || f.licence_status;
    w.q("#wCredits").innerHTML = `<span class="wc-lic ${esc(f.score_status === "clean" ? "" : "warn")}">Score: ${esc(f.score_status || "?")} · ${esc(lic)}</span>
      <span>${esc(f.credit_text || "")}</span>
      <span>Audio rendered live in your browser${w.kind === "piano" ? " with the Salamander Grand Piano (Alexander Holm, CC BY 3.0)" : " with the SGM+ soundfont"}; engraving by OpenSheetMusicDisplay. <a href="https://github.com/LaDoger/music-library/blob/main/docs/WATCH_PLAYER.md" target="_blank" rel="noopener">Licences</a></span>
      <a href="?id=${encodeURIComponent(f.id)}" data-w-detail>Details</a>`;
  }
  function fillCard(w, f) {
    const c = w.q("#wCard");
    c.querySelector(".wc-comp").textContent = f.composer;
    c.querySelector(".wc-title").textContent = f.title.includes(":") ? f.title.split(":").slice(1).join(":").trim() || f.title : f.title;
    c.querySelector(".wc-cat").textContent = [...new Set([f.title.includes(":") ? f.title.split(":")[0].trim() : "", f.catalog, f.movement].filter(Boolean))].join(" · ");
  }
  function showCard(w) {
    const c = w.q("#wCard"); c.classList.remove("show"); void c.offsetWidth; c.classList.add("show");
    clearTimeout(w.cardT); w.cardT = setTimeout(() => hideCard(w), 3400);
  }
  function hideCard(w) { w.q("#wCard")?.classList.remove("show"); }

  function exposeState(w) {
    const e = w.engine;
    window.__watch = {
      id: w.id, ready: !!w.ready, playing: !!(e && e.playing), kind: w.kind || "", view: w.view,
      ctxState: window.Tone ? window.Tone.context.state : "none",
      audioTime: e ? e.position() : 0, baseTime: w.engine ? basePos(w) : 0, total: w.total || 0,
      measure: w.curMeasure, measures: w.meas ? w.meas.length : 0, system: w.curSys, systems: w.sys ? w.sys.length : 0,
      turns: w.turns, hasScore: !!w.hasScore, tempo: w.tempo || 1, steps: w.steps ? w.steps.length : 0,
      seek: (t) => seek(w, t), play: () => play(w),
    };
  }

  function teardown() {
    const w = W; if (!w) return;
    W = null;
    cancelAnimationFrame(w.raf); clearTimeout(w.cardT);
    document.removeEventListener("keydown", w.keys); document.removeEventListener("keydown", w.trap);
    document.removeEventListener("fullscreenchange", w.onFs);
    w.ro && w.ro.disconnect();
    if (w.engine) { try { w.engine.pause(); w.engine.sampler && w.engine.sampler.dispose(); } catch { /* ok */ } }
    if (w.osmd) { try { w.osmd.clear(); } catch { /* ok */ } }
  }
  function close() {
    teardown();
    const root = $("#watch");
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    root.hidden = true; root.innerHTML = ""; root.onclick = null;
    document.title = "Music Library — public-domain classical music, scores & full recordings";
  }

  window.MusicWatch = { open, close };
})();
