/* Watch player: engraved score (OpenSheetMusicDisplay) synced to live audio rendered in the
   browser from the score itself (unrolled MusicXML; the MIDI for MIDI-only rows). Lazy-loaded by app.js on ?watch=<id>; adds no media files.
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
  const GLEITZ = "https://gleitz.github.io/midi-js-soundfonts/FluidR3_GM/";
  const SOUNDS = [
    { id: "auto", label: "Auto (best for this piece)" },
    { id: "salamander", label: "Grand piano (Salamander)", credit: 'Salamander Grand Piano by Alexander Holm, <a href="https://creativecommons.org/licenses/by/3.0/" target="_blank" rel="noopener">CC BY 3.0</a>' },
    { id: "harpsichord", label: "Harpsichord", gm: "harpsichord" },
    { id: "rhodes", label: "Rhodes / electric piano", gm: "electric_piano_1" },
    { id: "celesta", label: "Celesta", gm: "celesta" },
    { id: "musicbox", label: "Music box", gm: "music_box" },
    { id: "organ", label: "Church organ", gm: "church_organ" },
    { id: "gm", label: "Orchestral set (SGM+, multi-instrument)", credit: "SGM+ soundfont via Magenta (Apache-2.0 player)" },
  ];
  const GM_CREDIT = 'FluidR3_GM by Frank Wen, pre-rendered by gleitz/midi-js-soundfonts, <a href="https://creativecommons.org/licenses/by/3.0/" target="_blank" rel="noopener">CC BY 3.0</a>';
  const soundDef = (id) => SOUNDS.find((x) => x.id === id) || SOUNDS[0];
  const soundName = (id) => soundDef(id).label.replace(/ \(.*/, "").toLowerCase();
  async function gmUrls(name) {
    const r = await fetch(GLEITZ + name + "-mp3.js");
    if (!r.ok) throw new Error("soundfont " + r.status);
    const t = await r.text();
    const all = JSON.parse(t.slice(t.indexOf("{", t.indexOf("MIDI.Soundfont." + name)), t.lastIndexOf("}") + 1).replace(/,\s*}$/, "}"));
    const urls = {}; Object.keys(all).forEach((k, i) => { if (i % 2 === 0) urls[k] = all[k]; });   // every 2nd key; the sampler repitches
    return urls;
  }
  function makeEngine(kind, sound) {
    const core = window.core, Tone = window.Tone;
    const e = { kind, sound, ready: false, playing: false, pos: 0, base: 0, started: 0, seq: null, gen: 0, onend: null };
    if (kind === "piano") {
      e.load = async (seq) => {
        e.seq = seq;
        e.notes = seq.notes.filter((n) => !n.isDrum).sort((a, b) => a.startTime - b.startTime);
        if (!e.sampler) {
          const def = soundDef(e.sound);
          const cfg = def.gm ? { urls: await gmUrls(def.gm), release: def.id === "organ" ? 0.3 : 1 } : { urls: pianoUrls(), release: 1.2, baseUrl: SALAMANDER };
          e.sampler = await new Promise((res, rej) => {
            const s = new Tone.Sampler({ ...cfg, onload: () => res(s), onerror: rej }).toDestination();
            setTimeout(() => rej(new Error("samples timed out")), 40000);
          });
        }
        e.ready = true;
      };
      e.now = () => Tone.context.rawContext.currentTime;
      e.position = () => (e.playing ? Math.min(e.pos + (e.now() - e.started), e.seq.totalTime) : e.pos);
      e.start = (offset) => {
        e.gen++; const gen = e.gen;
        try { e.sampler.releaseAll(); } catch { /* ok */ }
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

  /* ---------- score timeline: MusicXML -> unrolled measures, tempo map, notes ----------
     Audio and cursor share one clock: the score is unrolled in playback order (repeats, voltas,
     D.C./D.S./Fine/To Coda; repeats are not replayed after a jump, the last volta is taken),
     tempo comes from <sound tempo> / metronome marks, and the notes of the unrolled score become
     the NoteSequence the audio engines play. Positions are in quarter notes ("u" = unrolled). */
  async function unzipXml(buf) {
    const b = new Uint8Array(buf), dv = new DataView(buf);
    let eocd = -1;
    for (let i = b.length - 22; i >= Math.max(0, b.length - 65557); i--) if (dv.getUint32(i, true) === 0x06054b50) { eocd = i; break; }
    if (eocd < 0) throw new Error("not a zip");
    const files = new Map();
    for (let p = dv.getUint32(eocd + 16, true), n = dv.getUint16(eocd + 10, true); n-- > 0;) {
      const method = dv.getUint16(p + 10, true), size = dv.getUint32(p + 20, true), nl = dv.getUint16(p + 28, true);
      const xl = dv.getUint16(p + 30, true), cl = dv.getUint16(p + 32, true), lh = dv.getUint32(p + 42, true);
      files.set(new TextDecoder().decode(b.subarray(p + 46, p + 46 + nl)), { method, size, lh });
      p += 46 + nl + xl + cl;
    }
    const read = async (name) => {
      const f = files.get(name); if (!f) return null;
      const start = f.lh + 30 + dv.getUint16(f.lh + 26, true) + dv.getUint16(f.lh + 28, true), raw = b.subarray(start, start + f.size);
      if (f.method === 0) return raw;
      if (f.method !== 8 || typeof DecompressionStream === "undefined") throw new Error("unsupported zip");
      return new Uint8Array(await new Response(new Blob([raw]).stream().pipeThrough(new DecompressionStream("deflate-raw"))).arrayBuffer());
    };
    const cont = await read("META-INF/container.xml");
    const m = cont && new TextDecoder().decode(cont).match(/full-path="([^"]+)"/);
    const name = m ? m[1] : [...files.keys()].find((k) => !k.startsWith("META-INF") && /\.(xml|musicxml)$/i.test(k));
    return read(name);
  }
  const decodeXml = (u) => new TextDecoder(u[0] === 0xff && u[1] === 0xfe ? "utf-16le" : u[0] === 0xfe && u[1] === 0xff ? "utf-16be" : "utf-8").decode(u);
  // Returns { text } (MusicXML) or { raw } (binary string for OSMD) when the browser cannot unzip.
  async function fetchScore(file) {
    const res = await fetch(file);
    if (!res.ok) throw new Error("score " + res.status);
    const buf = await res.arrayBuffer();
    if (!/\.mxl$/i.test(file)) return { text: decodeXml(new Uint8Array(buf)) };
    try { return { text: decodeXml(await unzipXml(buf)) }; } catch (err) { console.warn("mxl unzip failed", err); return { raw: toBinary(buf) }; }
  }

  const STEP = { C: 0, D: 2, E: 4, F: 5, G: 7, A: 9, B: 11 };
  const DYN = { pppp: 10, ppp: 23, pp: 36, p: 49, mp: 64, mf: 80, f: 96, ff: 112, fff: 120, ffff: 127, sf: 112, sfz: 112, fz: 112, sfp: 96, rfz: 112 };
  const kid = (el, name) => { for (const c of el.children) if (c.localName === name) return c; return null; };
  const kids = (el, name) => [...el.children].filter((c) => c.localName === name);
  const txt = (el, name, d) => { const c = el && kid(el, name); return c ? c.textContent.trim() : d; };
  function parseMusicXML(text) {
    const doc = new DOMParser().parseFromString(text, "application/xml");
    const root = doc.documentElement;
    if (!root || root.localName !== "score-partwise") throw new Error("not score-partwise MusicXML");
    const instr = new Map();   // score-part id -> Map(instrument id -> {prog, drum, unpitched})
    for (const sp of root.querySelectorAll("part-list > score-part")) {
      const m = new Map();
      for (const mi of kids(sp, "midi-instrument")) {
        const ch = +txt(mi, "midi-channel", 1), prog = Math.max(0, +txt(mi, "midi-program", 1) - 1), up = txt(mi, "midi-unpitched", "");
        m.set(mi.getAttribute("id"), { prog, drum: ch === 10, unpitched: up ? +up - 1 : -1 });
      }
      instr.set(sp.getAttribute("id"), m);
    }
    const parts = kids(root, "part");
    const n = kids(parts[0], "measure").length;
    const meas = Array.from({ length: n }, () => ({ len: 0, fwd: false, bwd: 0, ending: null, endStop: false, segno: false, coda: false, dc: false, ds: false, fine: false, tocoda: false }));
    const notes = [], tempos = [];
    let soundJumps = false;
    const words = [];
    parts.forEach((part, pi) => {
      const ins = instr.get(part.getAttribute("id")) || new Map();
      const insDef = ins.values().next().value || { prog: 0, drum: false, unpitched: -1 };
      let div = 1, ts = 4, vel = 80, trans = 0;
      kids(part, "measure").forEach((mEl, mi) => {
        if (mi >= n) return;
        const M = meas[mi];
        if (M.num === undefined) M.num = mEl.getAttribute("number") || "";
        let pos = 0, mx = 0, last = 0;
        const sound = (s, at) => {
          if (s.hasAttribute("tempo") && +s.getAttribute("tempo") > 0) tempos.push({ m: mi, off: at, qpm: +s.getAttribute("tempo") });
          if (s.hasAttribute("dynamics")) vel = Math.max(1, Math.min(127, Math.round(+s.getAttribute("dynamics") * 0.9)));
          for (const [a, k] of [["segno", "segno"], ["coda", "coda"], ["dalsegno", "ds"], ["tocoda", "tocoda"]]) if (s.hasAttribute(a)) { M[k] = true; soundJumps = true; }
          if (s.getAttribute("dacapo") === "yes") { M.dc = true; soundJumps = true; }
          if (s.hasAttribute("fine")) { M.fine = true; soundJumps = true; }
        };
        for (const el of mEl.children) {
          const t = el.localName;
          if (t === "attributes") {
            const d = txt(el, "divisions", ""); if (d) div = +d || 1;
            const tm = kid(el, "time");
            if (tm && txt(tm, "beats", "")) ts = txt(tm, "beats", "4").split("+").reduce((a, x) => a + (+x || 0), 0) * 4 / (+txt(tm, "beat-type", 4) || 4);
            const tr = kid(el, "transpose");
            if (tr) trans = (+txt(tr, "chromatic", 0) || 0) + 12 * (+txt(tr, "octave-change", 0) || 0);
          } else if (t === "note") {
            if (kid(el, "grace")) continue;
            const dur = (+txt(el, "duration", 0) || 0) / div;
            let start;
            if (kid(el, "chord")) start = last; else { start = pos; last = pos; pos += dur; }
            mx = Math.max(mx, pos);
            if (kid(el, "rest") || kid(el, "cue")) continue;
            const iid = kid(el, "instrument") && kid(el, "instrument").getAttribute("id");
            const def = (iid && ins.get(iid)) || insDef;
            let pitch = -1, drum = def.drum;
            const p = kid(el, "pitch"), up = kid(el, "unpitched");
            if (p) pitch = 12 * (+txt(p, "octave", 4) + 1) + STEP[txt(p, "step", "C")] + Math.round(+txt(p, "alter", 0) || 0) + (drum ? 0 : trans);
            else if (up) { pitch = def.unpitched; drum = true; }
            if (pitch < 0 || pitch > 127) continue;
            const ties = kids(el, "tie").map((x) => x.getAttribute("type"));
            const nv = el.hasAttribute("dynamics") ? Math.max(1, Math.min(127, Math.round(+el.getAttribute("dynamics") * 0.9))) : vel;
            notes.push({ m: mi, off: start, dur, pitch, part: pi, prog: def.prog, drum, vel: nv, tieStop: ties.includes("stop"), tieStart: ties.includes("start") });
          } else if (t === "backup") pos -= (+txt(el, "duration", 0) || 0) / div;
          else if (t === "forward") { pos += (+txt(el, "duration", 0) || 0) / div; mx = Math.max(mx, pos); }
          else if (t === "barline") {
            const r = kid(el, "repeat");
            if (r) { if (r.getAttribute("direction") === "forward") M.fwd = true; else M.bwd = Math.max(M.bwd, +r.getAttribute("times") || 1); }   // 1 = times not given
            const e = kid(el, "ending");
            if (e) { if (e.getAttribute("type") === "start") M.ending = (e.getAttribute("number") || "1").match(/\d+/g)?.map(Number) || [1]; else M.endStop = true; }
            for (const s of kids(el, "sound")) sound(s, pos);
            if (kid(el, "segno")) M.segno = true;
            if (kid(el, "coda")) M.coda = true;
          } else if (t === "sound") sound(el, pos);
          else if (t === "direction") {
            const at = pos + (+txt(el, "offset", 0) || 0) / div;
            const ss = kids(el, "sound");
            for (const s of ss) sound(s, at);
            for (const dt of kids(el, "direction-type")) {
              if (kid(dt, "segno")) M.segno = true;
              if (kid(dt, "coda")) M.coda = true;
              const mm = kid(dt, "metronome");
              if (mm && !ss.some((s) => s.hasAttribute("tempo")) && txt(mm, "per-minute", "")) {
                const unit = { whole: 4, half: 2, quarter: 1, eighth: 0.5, "16th": 0.25 }[txt(mm, "beat-unit", "quarter")] || 1;
                const qpm = parseFloat(txt(mm, "per-minute", "")) * unit * (kids(mm, "beat-unit-dot").length ? 1.5 : 1);
                if (qpm > 0) tempos.push({ m: mi, off: at, qpm });
              }
              const dy = kid(dt, "dynamics");
              if (dy && !ss.some((s) => s.hasAttribute("dynamics")) && dy.children[0] && DYN[dy.children[0].localName]) vel = DYN[dy.children[0].localName];
              for (const wd of kids(dt, "words")) words.push({ M, s: wd.textContent.trim() });
            }
          }
        }
        // notated durations can be rounded (tuplets): snap to the time signature when within 3 %
        M.len = Math.max(M.len, Math.abs(mx - ts) <= ts * 0.03 ? ts : mx);
      });
    });
    // Scores without <sound> jump attributes: read the usual words instead.
    if (!soundJumps) for (const { M, s } of words) {
      if (/^D\.\s*C\./i.test(s) || /^da capo/i.test(s)) M.dc = true;
      else if (/^D\.\s*S\./i.test(s) || /^dal segno/i.test(s)) M.ds = true;
      else if (/^fine\.?$/i.test(s)) M.fine = true;
      else if (/^to coda/i.test(s)) M.tocoda = true;
    }
    let cur = null;   // an ending without a stop closes at a backward repeat or before a forward repeat
    for (const M of meas) { if (M.fwd && !M.ending) cur = null; if (M.ending) cur = M.ending; M.endnums = cur; if (M.endStop || M.bwd) cur = null; }
    // repeat without times= inside a volta group: as many passes as the highest ending number
    meas.forEach((M, i) => {
      if (M.bwd !== 1) return;
      let lo = i, hi = i, mx = 2;
      if (M.endnums) { while (lo > 0 && meas[lo - 1].endnums) lo--; while (hi + 1 < meas.length && meas[hi + 1].endnums) hi++; for (let k = lo; k <= hi; k++) mx = Math.max(mx, ...meas[k].endnums); }
      M.bwd = mx;
    });
    return { meas, notes, tempos };
  }
  // Per movement (numbering restarts at 1, or 0 for a pickup): D.C./segno/coda stay inside it and
  // Fine ends only that movement.
  function unrollOrder(meas) {
    const n = meas.length, out = [];
    const lastEnding = (i) => { let k = i; while (k + 1 < n && meas[k + 1].endnums) k++; return meas[k].endnums; };
    const st = [0];
    for (let i = 1; i < n; i++) if (meas[i].num === "0" || (meas[i].num === "1" && meas[i - 1].num !== "0")) st.push(i);
    st.push(n);
    for (let s = 0; s + 1 < st.length; s++) {
      const s0 = st[s], s1 = st[s + 1];
      let i = s0, start = s0, pass = 1, jumped = false, guard = 0;
      while (i < s1 && guard++ < 20 * n) {
        const M = meas[i];
        if (M.fwd && start !== i) { start = i; pass = 1; }
        if (M.endnums && !(jumped ? M.endnums === lastEnding(i) : M.endnums.includes(pass))) { i++; continue; }
        out.push(i);
        if (jumped && M.fine) break;
        if (jumped && M.tocoda) { let c = i + 1; while (c < s1 && !meas[c].coda) c++; if (c < s1) { i = c; continue; } }
        if (M.bwd && !jumped && pass < M.bwd) { pass++; i = start; continue; }
        if (M.bwd) { pass = 1; start = i + 1; }
        if ((M.dc || M.ds) && !jumped) {
          jumped = true; pass = 1;
          if (M.dc) i = s0; else { i = s0; for (let k = s0; k < s1; k++) if (meas[k].segno) { i = k; break; } }
          start = i;
          continue;
        }
        i++;
      }
    }
    return out;
  }
  // Piecewise-linear lookups over sorted [x, y] anchors (clamped extrapolation at the ends).
  function pwl(xs, ys) {
    const f = (a, b) => (v) => {
      let lo = 0, hi = a.length - 1;
      if (v <= a[0]) return b[0] + (v - a[0]) * (a.length > 1 ? (b[1] - b[0]) / (a[1] - a[0] || 1) : 1);
      while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (a[mid] <= v) lo = mid; else hi = mid - 1; }
      if (lo >= a.length - 1) { const k = a.length - 1; return b[k] + (v - a[k]) * (k > 0 ? (b[k] - b[k - 1]) / (a[k] - a[k - 1] || 1) : 1); }
      return b[lo] + (v - a[lo]) * (b[lo + 1] - b[lo]) / (a[lo + 1] - a[lo] || 1);
    };
    return { yOf: f(xs, ys), xOf: f(ys, xs) };
  }
  // uTempos: [[u, qpm]] to use instead of the score's marks (scores without any tempo mark).
  function scoreTimeline(score, uTempos) {
    const { meas, notes, tempos } = score;
    const order = unrollOrder(meas);
    if (!order.length) throw new Error("empty score");
    tempos.sort((a, b) => a.m - b.m || a.off - b.off);
    const startQpm = []; let q = 120, ti = 0;   // MuseScore default before the first mark
    for (let m = 0; m < meas.length; m++) { while (ti < tempos.length && (tempos[ti].m < m || (tempos[ti].m === m && tempos[ti].off < 1e-6))) q = tempos[ti++].qpm; startQpm[m] = q; }
    const byM = new Map(); for (const nt of notes) { if (!byM.has(nt.m)) byM.set(nt.m, []); byM.get(nt.m).push(nt); }
    for (const l of byM.values()) l.sort((a, b) => a.off - b.off || b.tieStop - a.tieStop);   // time order, so a tie is closed before a later re-strike
    const tByM = new Map(); for (const t of tempos) if (t.off >= 1e-6) { if (!tByM.has(t.m)) tByM.set(t.m, []); tByM.get(t.m).push(t); }
    const entries = [], ev = []; let u = 0;
    for (const m of order) {
      entries.push({ m, u0: u, len: meas[m].len });
      ev.push([u, startQpm[m]]);
      for (const t of tByM.get(m) || []) if (t.off < meas[m].len) ev.push([u + t.off, t.qpm]);
      u += meas[m].len;
    }
    if (uTempos && uTempos.length) { ev.length = 0; ev.push(...uTempos); }
    // tempo segments -> anchors (u, seconds)
    const us = [0], ts = [0]; let cq = ev[0][1];
    for (const [eu, qpm] of ev) {
      if (eu > us[us.length - 1] + 1e-9) { ts.push(ts[ts.length - 1] + (eu - us[us.length - 1]) * 60 / cq); us.push(eu); }
      cq = qpm;
    }
    ts.push(ts[ts.length - 1] + (u - us[us.length - 1]) * 60 / cq); us.push(u);
    const map = pwl(ts, us);   // yOf: seconds -> u, xOf: u -> seconds
    const sec = (x) => map.xOf(x);
    // notes in playback order; ties extend the sounding note
    const out = [], onsets = [], open = new Map();
    for (const e of entries) {
      for (const nt of byM.get(e.m) || []) {
        const su = e.u0 + nt.off, eu = su + nt.dur, key = nt.part + ":" + nt.pitch;
        const prev = open.get(key);
        if (nt.tieStop && prev && Math.abs(prev.eu - su) < 1e-3) { prev.eu = eu; if (!nt.tieStart) open.delete(key); continue; }
        const o = { su, eu, pitch: nt.pitch, velocity: nt.vel, program: nt.prog, isDrum: nt.drum, instrument: nt.part };
        out.push(o); if (!nt.drum) onsets.push([su, nt.pitch]);
        if (nt.tieStart) open.set(key, o); else open.delete(key);
      }
    }
    out.sort((a, b) => a.su - b.su);
    onsets.sort((a, b) => a[0] - b[0]);
    const total = sec(u);
    const seqObj = {
      ticksPerQuarter: 220, totalTime: total,
      tempos: ev.map(([eu, qpm]) => ({ time: sec(eu), qpm })).filter((t, i, a) => i === 0 || t.qpm !== a[i - 1].qpm),
      notes: out.map((o) => ({ pitch: o.pitch, velocity: o.velocity, startTime: sec(o.su), endTime: Math.max(sec(o.su) + 0.03, sec(o.eu) - 0.005), program: o.program, isDrum: o.isDrum, instrument: o.instrument })),
    };
    const NS = window.core && window.core.NoteSequence;
    const seq = NS && NS.fromObject ? NS.fromObject(seqObj) : seqObj;
    return { entries, measures: meas.length, U: u, onsets, seq, total, uOf: map.yOf, tOf: map.xOf, score, marked: tempos.length > 0 };
  }

  // Score shown, audio from a separate MIDI: align MIDI onsets to the unrolled score onsets with a
  // banded DTW (cost = 1 - Jaccard of the pitch sets) and map MIDI seconds -> score position.
  function alignMidi(tl, seq) {
    const S = []; for (const [x, p] of tl.onsets) { const l = S[S.length - 1]; if (l && x - l.x < 1e-6) l.p.add(p); else S.push({ x, p: new Set([p]) }); }
    const mid = [...seq.notes].filter((nt) => !nt.isDrum).sort((a, b) => a.startTime - b.startTime);
    const A = []; for (const nt of mid) { const l = A[A.length - 1]; if (l && nt.startTime - l.x < 0.03) l.p.add(nt.pitch); else A.push({ x: nt.startTime, p: new Set([nt.pitch]) }); }
    const N = A.length, M = S.length;
    if (N < 2 || M < 2) return null;
    const W = Math.max(150, Math.ceil(0.15 * Math.max(N, M))), Wd = 2 * W + 1;
    const center = (i) => Math.round(i * (M - 1) / (N - 1));
    const D = new Float32Array(N * Wd).fill(Infinity), B = new Uint8Array(N * Wd);
    const at = (i, j) => { const k = j - center(i) + W; return k >= 0 && k < Wd ? i * Wd + k : -1; };
    const jac = (a, b) => { let c = 0; for (const x of a) if (b.has(x)) c++; return c / (a.size + b.size - c || 1); };
    for (let i = 0; i < N; i++) {
      const c0 = center(i);
      for (let j = Math.max(0, c0 - W); j <= Math.min(M - 1, c0 + W); j++) {
        const c = 1 - jac(A[i].p, S[j].p), k = at(i, j);
        if (i === 0 && j === 0) { D[k] = c; continue; }
        let best = Infinity, dir = 0, x;
        if (i > 0 && j > 0 && (x = at(i - 1, j - 1)) >= 0 && D[x] < best) { best = D[x]; dir = 1; }
        if (i > 0 && (x = at(i - 1, j)) >= 0 && D[x] + 0.3 < best) { best = D[x] + 0.3; dir = 2; }
        if (j > 0 && (x = at(i, j - 1)) >= 0 && D[x] + 0.3 < best) { best = D[x] + 0.3; dir = 3; }
        D[k] = c + best; B[k] = dir;
      }
    }
    if (at(N - 1, M - 1) < 0 || !isFinite(D[at(N - 1, M - 1)])) return null;
    const xs = [], ys = [];
    for (let i = N - 1, j = M - 1; i >= 0 && j >= 0;) {
      const k = at(i, j), d = B[k];
      if (d === 1 || (i === 0 && j === 0)) { if (jac(A[i].p, S[j].p) >= 0.5) { xs.push(A[i].x); ys.push(S[j].x); } }
      if (d === 1) { i--; j--; } else if (d === 2) i--; else if (d === 3) j--; else break;
    }
    xs.reverse(); ys.reverse();
    const fx = [], fy = [];   // strictly increasing in both
    for (let k = 0; k < xs.length; k++) if (!fx.length || (xs[k] > fx[fx.length - 1] + 1e-4 && ys[k] > fy[fy.length - 1] + 1e-6)) { fx.push(xs[k]); fy.push(ys[k]); }
    if (fx.length < 2) return null;
    if (seq.totalTime > fx[fx.length - 1] && tl.U > fy[fy.length - 1]) { fx.push(seq.totalTime); fy.push(tl.U); }
    const map = pwl(fx, fy);
    return { uOf: (t) => Math.max(0, Math.min(tl.U, map.yOf(t))), anchors: fx.length };
  }

  /* ---------- score (OSMD) ---------- */
  const toBinary = (buf) => { const u = new Uint8Array(buf); let s = ""; for (let i = 0; i < u.length; i += 8192) s += String.fromCharCode.apply(null, u.subarray(i, i + 8192)); return s; };
  async function loadScore(w, data) {
    await loadOSMD();
    const o = new window.opensheetmusicdisplay.OpenSheetMusicDisplay(w.osmdEl, {
      backend: "svg", autoResize: false, drawTitle: false, drawSubtitle: false, drawComposer: false, drawLyricist: false,
      drawCredits: false, drawPartNames: true, followCursor: false, drawingParameters: "default", pageFormat: "Endless",
    });
    await o.load(data);
    w.osmd = o;
    layoutScore(w);
    // Cursor step table (score order, no repeats): measure index + quarter offset in the measure for
    // every note onset; per measure the first step index and an iterator clone to jump to it.
    o.cursor.show();
    cursorA11y(w);
    const it = o.cursor.Iterator; w.steps = []; w.mFirst = []; w.mClone = []; w.mStart = [];
    while (!it.EndReached) {
      const m = it.CurrentMeasureIndex;
      if (w.mFirst[m] === undefined) { w.mFirst[m] = w.steps.length; w.mClone[m] = it.clone(); }
      w.steps.push({ m, o: (it.currentTimeStamp.RealValue - it.CurrentMeasure.AbsoluteTimestamp.RealValue) * 4 });
      o.cursor.next();
    }
    o.Sheet.SourceMeasures.forEach((sm, i) => { w.mStart[i] = sm.AbsoluteTimestamp.RealValue * 4; });
    o.cursor.reset(); w.stepIdx = 0;
  }
  // No usable MusicXML timeline (e.g. the browser cannot unzip): score order, MIDI tempo map,
  // linear stretch if the MIDI is longer (repeats expanded). Last resort only.
  function linearClock(w, seq) {
    const sm = w.osmd.Sheet.SourceMeasures, tm = tempoMap(seq);
    const entries = sm.map((x, i) => ({ m: i, u0: w.mStart[i], len: x.Duration.RealValue * 4 }));
    const U = entries.length ? entries[entries.length - 1].u0 + entries[entries.length - 1].len : 1;
    let scale = tm.qOf(seq.totalTime) / U; if (Math.abs(scale - 1) < 0.03) scale = 1;
    return { entries, uOf: (t) => tm.qOf(t) / scale };
  }
  function cursorA11y(w) {
    const el = w.osmd && w.osmd.cursor.cursorElement;
    if (el) { el.alt = ""; el.setAttribute("role", "presentation"); }
  }
  function layoutScore(w) {
    const o = w.osmd;
    const width = Math.max(240, Math.min(w.slide.clientWidth, 1500));
    w.osmdEl.style.width = width + "px";
    o.zoom = (width < 600 ? 0.7 : width > 1200 ? 1.1 : 1) * w.zoom;
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
          <div class="w-heading"><div class="w-comp" id="wComp"></div><h2 class="w-title" id="wTitle" tabindex="-1"></h2><div class="w-cat" id="wCat"></div></div>
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
            <span class="w-zoom" role="group" aria-label="Score zoom"><button class="w-chip" type="button" data-w="zout" aria-label="Zoom out">−</button><output id="wZoom" aria-live="polite">100%</output><button class="w-chip" type="button" data-w="zin" aria-label="Zoom in">+</button><button class="w-chip" type="button" data-w="zfit">Fit</button></span>
            <label class="w-sound"><span>Sound</span><select id="wSound" disabled>${SOUNDS.map((x) => `<option value="${x.id}">${esc(x.label)}</option>`).join("")}</select></label>
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
    fillHeading(w, r);
    document.title = `${r.title} · ${r.composer} — Watch · Music Library`;
    $("#wTitle", root).focus({ preventScroll: true });
    const z = parseFloat(ctx.zoom ? ctx.zoom() : "");
    w.zoom = z >= 0.5 && z <= 2.5 ? Math.round(z * 10) / 10 : 1;
    window.scrollTo(0, 0);
    bindUI(w);
    renderNext(w);
    exposeState(w);
    try {
      const full = await ctx.loadFull(r);
      if (W !== w) return;
      renderCredits(w, full);
      fillHeading(w, full);
      const xml = (full.score_files || []).find((f) => XML_RE.test(f));
      w.hasXml = !!xml;
      w.view = xml ? (prefs.view || "score") : "roll";
      for (const b of root.querySelectorAll('.w-seg [data-view="score"], .w-seg [data-view="both"]')) b.disabled = !xml;
      setView(w, w.view, true);
      await loadBundle();
      // Audio source: the unrolled MusicXML (one clock for audio and cursor); the MIDI only for
      // MIDI-only rows, when the score cannot be turned into notes, or with &audio=midi.
      const forceMidi = (ctx.audio ? ctx.audio() : "") === "midi";
      let tl = null;
      if (xml) {
        setStatus("Engraving the score…");
        await new Promise((res2) => setTimeout(res2, 30));
        try {
          const src = await fetchScore(xml);
          if (W !== w) return;
          if (src.text) { try { tl = scoreTimeline(parseMusicXML(src.text)); } catch (err) { console.warn("score timeline failed", err); } }
          await loadScore(w, src.text || src.raw); w.hasScore = true;
          if (tl && tl.measures !== w.osmd.Sheet.SourceMeasures.length) { console.warn("measure count differs from OSMD; using the MIDI"); tl = null; }
        } catch (err) { console.warn("score failed", err); w.hasScore = false; if (w.view !== "roll") setView(w, "roll", true); root.querySelectorAll('.w-seg [data-view="score"], .w-seg [data-view="both"]').forEach((b) => { b.disabled = true; }); setStatus("Score could not be drawn; showing the piano roll."); }
        if (W !== w) return;
      }
      let base, midi = null;
      const loadMidi = async () => {
        const res = await fetch(full.midi_play_url);
        if (!res.ok) throw new Error("MIDI " + res.status);
        return window.core.midiToSequenceProto(new Uint8Array(await res.arrayBuffer()));
      };
      if (tl && !tl.marked && !forceMidi) {
        // No tempo mark in the score: borrow the MIDI's tempo map when it has the same length in quarters.
        try {
          midi = await loadMidi();
          const tm = tempoMap(midi), mq = tm.qOf(midi.totalTime);
          if (Math.abs(mq - tl.U) <= 0.03 * tl.U && midi.tempos && midi.tempos.length) tl = scoreTimeline(tl.score, midi.tempos.map((t) => [tm.qOf(t.time), t.qpm]).sort((a, b) => a[0] - b[0]));
        } catch (err) { console.warn("MIDI tempo unavailable", err); }
        if (W !== w) return;
      }
      if (tl && tl.seq.notes.length && !forceMidi) { base = tl.seq; w.audioSrc = "score"; w.clock = tl; }
      else {
        base = midi || await loadMidi();
        if (W !== w) return;
        w.audioSrc = "midi";
        if (w.hasScore) {
          const al = tl && alignMidi(tl, base);
          w.clock = al ? { entries: tl.entries, uOf: al.uOf } : linearClock(w, base);
          w.audioSrc = al ? "midi-aligned" : "midi-linear";
        }
      }
      w.base = base; w.total = base.totalTime;
      w.sound = resolveSound(base);
      w.kind = w.sound === "gm" ? "sf" : "piano";
      w.rollNotes = base.notes.filter((n) => !n.isDrum);
      await prepareAudio(w);
      if (W !== w) return;
      w.ready = true;
      w.full = full; w.soundChoice = prefSound(); w.q("#wSound").value = SOUNDS.some((x) => x.id === w.soundChoice) ? w.soundChoice : "auto";
      renderCredits(w, full);
      setStatus(w.kind === "piano" ? "" : "");
      w.q("#wPlay").disabled = false; w.q("#wSound").disabled = false;
      w.q("#wPlay").focus({ preventScroll: true });
      sync(w, true);
      loop(w);
    } catch (err) {
      if (W !== w) return;
      console.warn(err);
      setStatus("Could not load this piece: " + err.message);
    }
  }

  const prefSound = () => ctx.sound() || localStorage.getItem("watchSound") || "auto";
  const autoSound = (base) => (isPianoSeq(base) ? "salamander" : "gm");
  function resolveSound(base) {
    const c = prefSound();
    return SOUNDS.some((x) => x.id === c) && c !== "auto" ? c : autoSound(base);
  }
  async function setSound(w, id) {
    const choice = SOUNDS.some((x) => x.id === id) ? id : "auto";
    if (!w.ready || w.switching) return;
    const next = choice === "auto" ? autoSound(w.base) : choice;
    const commit = () => { w.soundChoice = choice; localStorage.setItem("watchSound", choice); ctx.setSound(choice === "auto" ? "" : choice); };
    if (next === w.sound) return commit();
    const old = w.engine, t = basePos(w), was = old.playing, sel = w.q("#wSound"), prev = w.sound;
    const lock = (on) => { w.switching = on; for (const x of [sel, w.q("#wTempo"), w.q("#wPlay")]) x.disabled = on; };
    lock(true); w.setStatus("Loading " + soundName(next) + "…");
    if (was) old.pause();
    const eng = makeEngine(next === "gm" ? "sf" : "piano", next);
    try { await eng.load(w.scaled); }
    catch (err) {
      console.warn("sound failed", err);
      if (W !== w) return;
      lock(false); w.setStatus("Could not load that sound. Keeping " + soundName(prev) + ".");
      if (was) old.start(old.pos);
      sel.value = w.soundChoice; return;
    }
    if (W !== w) return;
    commit();
    old.gen++; old.onend = null;
    eng.onend = () => onEnded(w);
    try { if (old.sampler) old.sampler.dispose(); if (old.sfp && old.sfp.isPlaying()) old.sfp.stop(); } catch { /* ok */ }
    w.engine = eng; w.sound = next; w.kind = eng.kind;
    eng.pos = t / w.tempo;
    if (was) eng.start(eng.pos);
    lock(false); w.setStatus(""); renderCredits(w, w.full); setPlayUI(w); sync(w, true);
  }
  async function prepareAudio(w) {
    const f = prefs.tempo;
    w.q("#wTempo").value = f; w.q("#wTempoOut").textContent = Math.round(f * 100) + "%";
    w.scaled = scaleSeq(w.base, f);
    w.setStatus("Loading " + soundName(w.sound) + " samples…");
    let eng = makeEngine(w.kind, w.sound);
    try { await eng.load(w.scaled); }
    catch (err) {
      if (w.kind !== "piano") throw err;
      console.warn("samples failed, falling back to SGM+", err);
      w.sound = "gm"; w.kind = "sf"; eng = makeEngine("sf", "gm"); await eng.load(w.scaled);
    }
    eng.onend = () => onEnded(w);
    w.engine = eng; w.tempo = f;
  }

  /* ---------- sync / animation ---------- */
  const basePos = (w) => (w.engine ? w.engine.position() * w.tempo : 0);   // base seconds
  // base seconds -> { m: measure (score index), step: cursor step index } via the unrolled timeline
  function posAt(w, t) {
    const E = w.clock.entries, u = w.clock.uOf(t);
    let lo = 0, hi = E.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (E[mid].u0 <= u + 1e-6) lo = mid; else hi = mid - 1; }
    const e = E[lo], off = u - e.u0;
    let step = w.mFirst[e.m];
    if (step === undefined) {   // measure without cursor steps: stay on the last step before it
      step = 0; for (let m = e.m - 1; m >= 0; m--) if (w.mFirst[m] !== undefined) { step = w.mFirst[m]; while (step + 1 < w.steps.length && w.steps[step + 1].m === m) step++; break; }
    } else while (step + 1 < w.steps.length && w.steps[step + 1].m === e.m && w.steps[step + 1].o <= off + 1e-6) step++;
    return { m: e.m, step, u };
  }
  function moveCursor(w, idx) {
    const c = w.osmd.cursor;
    if (idx === w.stepIdx + 1) c.next();
    else if (idx !== w.stepIdx) {
      const m = w.steps[idx].m;
      c.iterator = w.mClone[m].clone();
      for (let i = w.mFirst[m]; i < idx; i++) c.next();
    }
    c.update();
    w.stepIdx = idx;
  }
  function sync(w, force) {
    if (!w.engine) return;
    const t = basePos(w), total = w.total;
    w.q("#wProg").style.width = (total ? Math.min(100, t / total * 100) : 0) + "%";
    const seek = w.q("#wSeek");
    seek.setAttribute("aria-valuenow", String(Math.round(t / total * 100)));
    seek.setAttribute("aria-valuetext", `${fmt(t / w.tempo)} of ${fmt(total / w.tempo)}`);
    w.q("#wTime").textContent = `${fmt(t / w.tempo)} / ${fmt(total / w.tempo)}`;
    if (w.hasScore && w.steps.length && w.clock) {
      const p = posAt(w, t);
      w.u = p.u;
      if (p.step !== w.stepIdx || force) moveCursor(w, p.step);
      if (p.m !== w.curMeasure || force) highlight(w, p.m, force);
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
    const live = w.engine && w.engine.playing;
    if (w.engine && (live || w.dirty)) sync(w);
    if (w.view !== "score" && (live || w.dirty)) drawRoll(w);
    w.dirty = false;
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
  function setView(w, v, forced) {
    w.view = v; if (!forced) prefs.view = v;
    w.dirty = true;
    w.stage.dataset.vmode = v;
    w.root.querySelectorAll(".w-seg [data-view]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === v)));
    if (w.hasScore) requestAnimationFrame(() => { w.dirty = true; });
  }
  function setPaper(w, p) {
    prefs.paper = p; localStorage.setItem("watchPaper", p);
    w.root.className = w.root.className.replace(/paper-\w+/, "paper-" + p); w.dirty = true;
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
        case "zin": return setZoom(w, w.zoom + 0.1);
        case "zout": return setZoom(w, w.zoom - 0.1);
        case "zfit": return setZoom(w, 1);
        case "prev": { const { set } = upNext(w.r); const i = set.findIndex((x) => x.id === w.r.id); if (basePos(w) > 3 || i <= 0) return seek(w, 0); return go(set[i - 1].id, false); }
        case "next": { const { next } = upNext(w.r); if (next.length) go(next[0].id, false); return; }
      }
    };
    w.q("#wSound").onchange = (e) => setSound(w, e.target.value);
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
      w.dirty = true;
      clearTimeout(rt);
      rt = setTimeout(() => {
        if (!w.hasScore || !w.paper.clientWidth || Math.abs(w.paper.clientWidth - w.lastW) < 4) return;
        w.lastW = w.paper.clientWidth; relayout(w);
      }, 250);
    });
    w.lastW = 0;
    w.ro.observe(w.paper);
    zoomUI(w); fitStage(w);
    w.ro2 = new ResizeObserver(() => fitStage(w));
    w.ro2.observe(w.q(".w-bar")); w.ro2.observe(w.q(".w-controls"));
    w.onFs = () => { w.q('[data-w="full"]').setAttribute("aria-pressed", String(!!document.fullscreenElement)); };
    document.addEventListener("fullscreenchange", w.onFs);
  }
  function setZoom(w, z) {
    z = Math.round(Math.max(0.5, Math.min(2.5, z)) * 10) / 10;
    if (z === w.zoom) return;
    w.zoom = z;
    if (ctx.setZoom) ctx.setZoom(z === 1 ? "" : String(z));
    zoomUI(w);
    if (w.hasScore) relayout(w);
  }
  function zoomUI(w) {
    w.q("#wZoom").textContent = Math.round(w.zoom * 100) + "%";
    w.q('[data-w="zout"]').disabled = w.zoom <= 0.5; w.q('[data-w="zin"]').disabled = w.zoom >= 2.5;
  }
  // Stage height = viewport minus header bar and controls, so bar + stage + controls fit on screen.
  function fitStage(w) {
    const h = (w.q(".w-bar").offsetHeight || 0) + (w.q(".w-controls").offsetHeight || 0);
    w.root.style.setProperty("--w-bars", h + "px");
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
      <span class="wc-sound">${w.sound ? "Sound credits: " + (soundDef(w.sound).gm ? GM_CREDIT : soundDef(w.sound).credit) + ". " : ""}Audio rendered live in your browser; engraving by OpenSheetMusicDisplay. <a href="https://github.com/LaDoger/music-library/blob/main/docs/WATCH_PLAYER.md" target="_blank" rel="noopener">Licences</a></span>
      <a href="?id=${encodeURIComponent(f.id)}" data-w-detail>Details</a>`;
  }
  // Static heading above the stage (never over the score): composer, work title, catalogue line.
  function fillHeading(w, f) {
    w.q("#wTitle").textContent = f.title + (f.movement && !f.title.includes(f.movement) ? " · " + f.movement : "");
    w.q("#wCat").textContent = f.catalog || "";
    w.q("#wCat").hidden = !f.catalog;
  }

  function exposeState(w) {
    const e = w.engine;
    window.__watch = {
      id: w.id, ready: !!w.ready, playing: !!(e && e.playing), kind: w.kind || "", sound: w.sound || "", view: w.view,
      ctxState: window.Tone ? window.Tone.context.state : "none",
      audioTime: e ? e.position() : 0, baseTime: w.engine ? basePos(w) : 0, total: w.total || 0,
      measure: w.curMeasure, measures: w.meas ? w.meas.length : 0, system: w.curSys, systems: w.sys ? w.sys.length : 0,
      turns: w.turns, hasScore: !!w.hasScore, tempo: w.tempo || 1, steps: w.steps ? w.steps.length : 0,
      cursor: w.steps && w.steps[w.stepIdx] ? { m: w.steps[w.stepIdx].m, off: w.steps[w.stepIdx].o } : null, u: w.u || 0, audioSrc: w.audioSrc || "",
      seek: (t) => seek(w, t), play: () => play(w),
    };
  }

  function teardown() {
    const w = W; if (!w) return;
    W = null;
    cancelAnimationFrame(w.raf);
    document.removeEventListener("keydown", w.keys); document.removeEventListener("keydown", w.trap);
    document.removeEventListener("fullscreenchange", w.onFs);
    w.ro && w.ro.disconnect(); w.ro2 && w.ro2.disconnect();
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

  window.MusicWatch = { open, close, _score: { fetchScore, parseMusicXML, unrollOrder, scoreTimeline, alignMidi } };   // _score: tests only
})();
