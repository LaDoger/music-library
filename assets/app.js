/* Music Library UI — vanilla JS, no build step.
   Data: data/index/manifest.json + data/index/part-*.json (slim columnar index, built by
   scripts/build_catalog.py) + data/composers.json; data/items/<id>.json is fetched when a
   piece is opened. Falls back to data/library.json if the index is missing.
   Views: composer index (default) → composer page (?composer=) → works (?view=works).
   One global player: 15 s preview / full recording (real recordings only) or the score MIDI
   synthesised live in the browser (html-midi-player). No pre-rendered synth audio. */
(() => {
  "use strict";

  const PAGE_SIZE = 48;
  const SOUNDFONT = "https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus";
  const MIDI_LIB = "assets/vendor/midi-player.bundle.js";
  const GENRES = [
    ["classical", "Classical"], ["jazz", "Jazz"], ["ragtime", "Ragtime"], ["blues", "Blues"], ["folk", "Folk"],
    ["world", "World"], ["marches", "Marches"], ["early_popular", "Early popular"], ["film_silent", "Silent / film"],
    ["modern_cc", "Modern CC0 / CC BY"], ["other", "Other"],
  ];
  const GENRE_LABEL = Object.fromEntries(GENRES);
  const LICENCE = {
    clean: ["Clean", "PD / CC0 — commercial use, no credit required"],
    attribution: ["Credit required", "CC BY — put the credit in the post or description"],
    sharealike: ["ShareAlike", "BY-SA / OAL — remixes may have to carry the same licence"],
    flagged: ["Flagged", "Known caveat (territory, arrangement or dedication) — read the notes"],
    unverified: ["Unverified", "Rights not confirmed from the source page — do not treat as cleared"],
  };
  const LICENCE_ORDER = ["clean", "attribution", "flagged", "sharealike", "unverified"];
  const ENERGY = [["very_high", "Very high"], ["high", "High"], ["moderate", "Moderate"], ["low", "Low"]];
  const ENERGY_LABEL = Object.fromEntries(ENERGY);
  const ENERGY_RANK = { very_high: 4, high: 3, moderate: 2, low: 1 };
  const SORTS = ["featured", "composer", "catalog", "title", "relevance", "year", "energy", "score"];
  const MODES = {
    preview: { label: "Preview", short: "15 s", badge: "Preview · 15 s" },
    full: { label: "Full recording", short: "Full", badge: "Recording" },
    midi: { label: "Synth (in-browser MIDI)", short: "Synth", badge: "Synth · in-browser MIDI" },
  };

  // Filter keys <-> URL params. Facet filters are single-value selects.
  const FACETS = ["genre", "composer", "mood", "era", "energy", "licence", "scope", "rec", "verified"];
  const PARAMS = ["q", ...FACETS, "score", "featured", "picks", "sort", "view", "layout", "page", "id"];

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fold = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const squash = (s) => s.replace(/[\s.,;:/()\-–'"]+/g, "");
  const safeUrl = (u) => (/^(https?:\/\/|previews\/|files\/|data\/)/i.test(u || "") ? u : "");
  const coll = new Intl.Collator("en", { numeric: true, sensitivity: "base" });
  const fmtTime = (s) => {
    s = Math.max(0, Math.floor(s || 0));
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = String(s % 60).padStart(2, "0");
    return h ? `${h}:${String(m).padStart(2, "0")}:${ss}` : `${m}:${ss}`;
  };

  let ROWS = [];
  let BY_ID = new Map();
  let COMPOSERS = new Map(); // name -> composers.json entry
  const state = {};
  let lastFocus = null;
  let browseTab = "era";
  let qTimer;

  /* ---------- data ---------- */
  function shortName(name) {
    const p = String(name).split(" ");
    return /^(I|II|III|IV)$/.test(p[p.length - 1]) && p.length > 2 ? p.slice(-2).join(" ") : p[p.length - 1];
  }
  function prepare(rows) {
    return rows.map((r) => {
      const c = COMPOSERS.get(r.composer) || {};
      const text = fold(r.search_text || [r.title, r.composer, c.sort_name, r.catalog, r.catalog_variants, r.movement, r.mood_tags, r.genre, r.era, r.id.replace(/_/g, " ")].join(" "));
      return Object.assign(r, {
        _text: text,
        // Squash each field on its own: "BWV 56" + variants "56 56" must not squash to "bwv565656".
        _squash: [r.title, r.catalog, r.movement, r.composer].map((v) => squash(fold(v || ""))).join("|"),
        _title: fold(r.title),
        _composer: fold(r.composer),
        _catalog: squash(fold(r.catalog)),
        composer_sort: r.composer_sort || c.sort_name || r.composer,
        composer_short: r.composer_short || c.short_name || shortName(r.composer),
        genre: r.genre || "other",
        featured_rank: +r.featured_rank || 0,
        mood_tags_list: r.mood_tags_list || String(r.mood_tags || "").split(";").map((s) => s.trim()).filter(Boolean),
      });
    });
  }
  function composerInfo(name) {
    const c = COMPOSERS.get(name);
    if (c) return c;
    const r = ROWS.find((x) => x.composer === name) || {};
    return { name, short_name: r.composer_short || shortName(name), sort_name: r.composer_sort || name,
      birth_year: +r.birth_year || null, death_year: +r.death_year || null, era: r.era || "", genres: [r.genre].filter(Boolean) };
  }
  const lifeDates = (c) => (c.birth_year || c.death_year ? `${c.birth_year || "?"}–${c.death_year || ""}` : "");
  function monogram(c) {
    const given = String(c.sort_name || "").split(", ")[1] || "";
    const g = given.split(/\s+/).find((w) => w && w[0] === w[0].toUpperCase()) || "";
    return (g ? g[0] : "") + String(c.short_name || c.name)[0];
  }
  const composerHref = (name) => "?composer=" + encodeURIComponent(name);

  /* ---------- state <-> URL ---------- */
  function readState() {
    const p = new URLSearchParams(location.search);
    for (const k of PARAMS) state[k] = p.get(k) || "";
    state.page = Math.max(1, parseInt(state.page, 10) || 1);
    // Legacy ?view=list|grid (v1 URLs) -> works view with that layout.
    if (state.view === "list" || state.view === "grid") { state.layout = state.layout || state.view; state.view = "works"; }
    if (!["composers", "works"].includes(state.view)) state.view = "";
    state.layout = state.layout === "list" ? "list" : "grid";
    for (const k of ["score", "featured", "picks"]) state[k] = state[k] === "1" ? "1" : "";
    const allowed = {
      genre: GENRES.map(([v]) => v), energy: ENERGY.map(([v]) => v), licence: LICENCE_ORDER,
      rec: ["0", "1"], verified: ["yes", "unverified"], sort: SORTS,
    };
    if (ROWS.length) {
      for (const k of ["composer", "era"]) allowed[k] = uniq(k);
      allowed.mood = [...new Set(ROWS.flatMap((r) => r.mood_tags_list))];
      if (state.id && !BY_ID.has(state.id)) state.id = "";
    }
    for (const [k, values] of Object.entries(allowed)) if (state[k] && !values.includes(state[k])) state[k] = "";
  }
  function writeState(push = false) {
    const p = new URLSearchParams();
    for (const k of PARAMS) {
      const v = state[k];
      if (v && !(k === "page" && v === 1) && !(k === "layout" && v === "grid")) p.set(k, v);
    }
    const qs = p.toString();
    const url = location.pathname + (qs ? "?" + qs : "") + location.hash;
    if (url !== location.pathname + location.search + location.hash) history[push ? "pushState" : "replaceState"](null, "", url);
  }
  /** composers (A–Z index) | composer (one composer's works) | works (all works). */
  function mode() {
    if (state.composer) return "composer";
    if (state.view === "works" || state.q || state.picks) return "works";
    return "composers";
  }
  function activeFilterCount() {
    return FACETS.filter((k) => k !== "composer" && state[k]).length + (state.score ? 1 : 0) + (state.featured ? 1 : 0) + (state.q ? 1 : 0) + (state.picks ? 1 : 0);
  }

  /* ---------- filtering ---------- */
  function tokens() {
    return fold(state.q).split(/\s+/).filter(Boolean);
  }
  function facetValue(r, k) {
    switch (k) {
      case "licence": return r.licence_status;
      case "scope": return (r.licence_scope === "US-PD-only") ? "us_pd_only" : "worldwide";
      case "rec": return r.has_recording ? "1" : "0";
      case "verified": return r.verified === "yes" ? "yes" : "unverified";
      default: return r[k];
    }
  }
  function matches(r, toks, except) {
    if (state.score && !r.has_editable_score) return false;
    if (state.featured && !(r.featured_rank >= 1 && r.featured_rank <= 2)) return false;
    if (state.picks && !r.editors_pick_rank) return false;
    for (const k of FACETS) {
      if (k === except || !state[k]) continue;
      if (k === "mood") { if (!r.mood_tags_list.includes(state.mood)) return false; }
      else if (facetValue(r, k) !== state[k]) return false;
    }
    for (const t of toks) {
      if (!r._text.includes(t) && !r._squash.includes(squash(t))) return false;
    }
    return true;
  }
  function relevance(r, toks) {
    let s = 0;
    const q = squash(fold(state.q));
    if (q && r._catalog && r._catalog.startsWith(q)) s += 50;
    for (const t of toks) {
      if (r._title.includes(t)) s += 6;
      if (r._composer.includes(t)) s += 4;
      if (r._catalog.includes(squash(t))) s += 8;
    }
    if (r.editors_pick_rank) s += 3 + (16 - r.editors_pick_rank) / 16;
    if (r.has_editable_score) s += 1;
    return s;
  }
  // Same catalogue number: the curated row (it has a preview) before bulk imports.
  const byCatalog = (a, b) => (!a.catalog - !b.catalog) || coll.compare(a.catalog || "", b.catalog || "") || (!a.preview_url - !b.preview_url) || coll.compare(a.title, b.title);
  const byComposer = (a, b) => coll.compare(a.composer_sort, b.composer_sort) || byCatalog(a, b);
  // Featured composers first (rank 1 top cinematic group, 2 next tier, 3 tier A/B, 4 other majors), then A–Z.
  const rankOf = (r) => r.featured_rank || 9;
  const byFeatured = (a, b) => rankOf(a) - rankOf(b) || byComposer(a, b);
  function effectiveSort() {
    if (state.sort) return state.sort;
    if (state.picks) return "picks";
    return mode() === "composer" ? "catalog" : "featured";
  }
  function compute() {
    const toks = tokens();
    const res = ROWS.filter((r) => matches(r, toks, null));
    const sort = effectiveSort();
    if (sort === "relevance") {
      const rel = new Map(res.map((r) => [r, relevance(r, toks)]));
      return res.sort((a, b) => rel.get(b) - rel.get(a) || byComposer(a, b));
    }
    const by = {
      picks: (a, b) => a.editors_pick_rank - b.editors_pick_rank,
      featured: byFeatured,
      composer: byComposer,
      catalog: (a, b) => byCatalog(a, b) || byComposer(a, b),
      title: (a, b) => coll.compare(a.title, b.title) || byComposer(a, b),
      year: (a, b) => (+a.death_year || 9999) - (+b.death_year || 9999) || byComposer(a, b),
      energy: (a, b) => (ENERGY_RANK[b.energy] || 0) - (ENERGY_RANK[a.energy] || 0) || byComposer(a, b),
      score: (a, b) => (b.has_editable_score - a.has_editable_score) || byComposer(a, b),
    }[sort];
    return res.sort(by);
  }
  function facetCounts(key) {
    const toks = tokens();
    const counts = new Map();
    for (const r of ROWS) {
      if (!matches(r, toks, key)) continue;
      const vals = key === "mood" ? r.mood_tags_list : [facetValue(r, key)];
      for (const v of vals) if (v) counts.set(v, (counts.get(v) || 0) + 1);
    }
    return counts;
  }

  /* ---------- rendering helpers ---------- */
  const badge = (st) => {
    const [label, tip] = LICENCE[st] || LICENCE.unverified;
    return `<span class="badge b-${esc(st || "unverified")}" title="${esc(tip)}">${esc(label)}</span>`;
  };
  const scopeBadge = (r) => {
    if (r.licence_scope !== "US-PD-only") return "";
    const tip = "US public domain only — may be copyrighted elsewhere, including EU/Poland. Composer died 1930–1955; work published before 1931.";
    return `<span class="badge b-us-pd" title="${esc(tip)}">US public domain only</span>`;
  };
  const subStatus = (r) => {
    const parts = [];
    if (r.recording_status) parts.push(`rec <b>${esc(LICENCE[r.recording_status][0])}</b>`);
    if (r.score_status) parts.push(`score <b>${esc(LICENCE[r.score_status][0])}</b>`);
    return parts.length > 1 || (parts.length && r.licence_status !== (r.recording_status || r.score_status))
      ? `<span class="sub-status">${parts.join(" · ")}</span>` : "";
  };
  const cardMode = (r) => (r.preview_url ? "preview" : availableModes(r)[0] || "");
  const playBtn = (r, cls = "") => {
    const m = cardMode(r);
    return m
      ? `<button class="play-btn ${cls}" type="button" data-act="play" data-mode="${m}" data-id="${esc(r.id)}" aria-label="Play ${esc(MODES[m].label.toLowerCase())} of ${esc(r.title)}">▶</button>`
      : `<button class="play-btn ${cls}" type="button" disabled aria-label="Nothing to play">▶</button>`;
  };
  const movementSuffix = (r) => (r.movement && !fold(r.title).includes(fold(r.movement)) ? ` · ${esc(r.movement)}` : "");

  function cardHTML(r, inComposer) {
    const moods = r.mood_tags_list.slice(0, 3).map((m) => `<button type="button" class="tag mood" data-act="mood" data-mood="${esc(m)}">${esc(m)}</button>`).join("");
    const score = r.has_editable_score
      ? `<span class="tag score" title="${esc(r.editable_format || "Editable score")}">✎ Score</span>`
      : `<span class="tag noscore" title="No editable score yet">no score</span>`;
    const rec = r.has_recording ? `<span class="tag rec" title="Full recording: play it in full from the player">♫ Recording</span>` : "";
    const synth = r.midi_play_url ? `<span class="tag synth" title="Plays the score MIDI in the browser">◍ Synth</span>` : "";
    const composer = inComposer ? "" : `<a class="c-composer" href="${esc(composerHref(r.composer))}" data-act="composer" data-composer="${esc(r.composer)}">${esc(r.composer)}</a>`;
    return `<article class="card${inComposer ? " in-composer" : ""}${r.id === player.id ? " playing" : ""}" data-id="${esc(r.id)}">
      <div class="card-head">
        ${playBtn(r)}
        <div class="card-title">
          ${composer}
          <h3><button type="button" data-act="open" data-id="${esc(r.id)}">${esc(r.title)}</button></h3>
          <div class="c-cat">${r.catalog ? `<span class="cat">${esc(r.catalog)}</span>` : ""}${movementSuffix(r)}</div>
        </div>
      </div>
      <div class="meta">${score}${rec}${synth}<span class="tag" title="${esc(r.tempo_energy)}">⚡ ${esc(ENERGY_LABEL[r.energy] || r.energy || "?")}</span>${moods}</div>
      ${r.video_use_ideas ? `<p class="excerpt">${esc(r.video_use_ideas)}</p>` : ""}
      <div class="badges">${badge(r.licence_status)}${scopeBadge(r)}${subStatus(r)}${r.editors_pick_rank ? `<span class="tag pick-tag" title="Editor's pick">★ Pick #${r.editors_pick_rank}</span>` : ""}</div>
    </article>`;
  }

  function renderWorks(res) {
    const pages = Math.max(1, Math.ceil(res.length / PAGE_SIZE));
    if (state.page > pages) state.page = pages;
    writeState();
    const slice = res.slice((state.page - 1) * PAGE_SIZE, state.page * PAGE_SIZE);
    const box = $("#results");
    box.className = "results " + state.layout;
    if (!slice.length) {
      const g = state.genre && GENRE_LABEL[state.genre];
      box.innerHTML = `<div class="empty-state"><p><b>No matches.</b> ${g && !ROWS.some((r) => r.genre === state.genre)
        ? `No ${esc(g)} pieces yet — they arrive in later batches (only legally clean material, no filler).`
        : "Try fewer filters or a different spelling (catalogue numbers work with or without spaces: BWV565, Op 27)."}</p>
        <button class="btn" type="button" data-act="clear">Clear all filters</button></div>`;
    } else {
      const inComposer = mode() === "composer";
      box.innerHTML = slice.map((r) => cardHTML(r, inComposer)).join("");
    }
    const from = res.length ? (state.page - 1) * PAGE_SIZE + 1 : 0;
    const to = Math.min(res.length, state.page * PAGE_SIZE);
    const scope = mode() === "composer" ? `works by ${esc(composerInfo(state.composer).short_name)}` : `of ${ROWS.length} works`;
    $("#resultCount").innerHTML = `<b>${res.length}</b> ${scope}${res.length > PAGE_SIZE ? ` · showing ${from}–${to}` : ""}`;
    renderPager(pages);
  }

  function composerGroups() {
    const toks = tokens();
    const groups = new Map();
    for (const r of ROWS) {
      if (!matches(r, toks, "composer")) continue;
      const g = groups.get(r.composer) || { n: 0, scores: 0, recs: 0 };
      g.n++; g.scores += r.has_editable_score ? 1 : 0; g.recs += r.has_recording ? 1 : 0;
      groups.set(r.composer, g);
    }
    return [...groups.entries()].map(([name, g]) => ({ ...composerInfo(name), name, ...g }))
      .sort((a, b) => coll.compare(fold(a.sort_name), fold(b.sort_name)));
  }
  function portraitHTML(c, cls) {
    return c.portrait_url
      ? `<img class="${cls}" src="${esc(c.portrait_url)}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer">`
      : `<span class="${cls} monogram" aria-hidden="true">${esc(monogram(c))}</span>`;
  }
  function renderComposers() {
    writeState();
    const list = composerGroups();
    const box = $("#results");
    box.className = "results composers";
    const letters = new Map();
    for (const c of list) {
      const L = fold(c.sort_name)[0].toUpperCase();
      if (!letters.has(L)) letters.set(L, []);
      letters.get(L).push(c);
    }
    const az = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("").map((L) => letters.has(L)
      ? `<a href="#letter-${L}" data-act="letter" data-letter="${L}">${L}</a>` : `<span aria-hidden="true">${L}</span>`).join("");
    box.innerHTML = !list.length
      ? `<div class="empty-state"><p><b>No composers match these filters.</b></p><button class="btn" type="button" data-act="clear">Clear all filters</button></div>`
      : `<nav class="az" aria-label="Composers by letter">${az}</nav>` + [...letters.entries()].map(([L, cs]) => `
        <section class="letter-group" id="letter-${L}" aria-labelledby="lh-${L}">
          <h3 class="letter" id="lh-${L}">${L}</h3>
          <div class="composer-grid">${cs.map((c) => `
            <a class="composer-card" href="${esc(composerHref(c.name))}" data-act="composer" data-composer="${esc(c.name)}">
              ${portraitHTML(c, "cc-portrait")}
              <span class="cc-body">
                <span class="cc-name">${esc(c.name)}</span>
                <span class="cc-dates">${esc(lifeDates(c))}${c.era ? ` · ${esc(c.era)}` : ""}</span>
                <span class="cc-count"><b>${c.n}</b> ${c.n === 1 ? "work" : "works"}${c.scores ? ` · ${c.scores} ${c.scores === 1 ? "score" : "scores"}` : ""}${c.recs ? ` · ${c.recs} ${c.recs === 1 ? "recording" : "recordings"}` : ""}</span>
              </span>
            </a>`).join("")}</div>
        </section>`).join("");
    const works = list.reduce((s, c) => s + c.n, 0);
    $("#resultCount").innerHTML = `<b>${list.length}</b> composers · ${works} works`;
    $("#pager").innerHTML = "";
  }

  /** Featured composers (featured_rank 1-2 in data/composers.json): a chip strip above the A-Z index. */
  function renderFeatured() {
    const strip = $("#featuredStrip");
    const names = new Map();
    for (const r of ROWS) if (r.featured_rank >= 1 && r.featured_rank <= 2 && !names.has(r.composer)) names.set(r.composer, { rank: r.featured_rank, n: 0 });
    for (const r of ROWS) if (names.has(r.composer)) names.get(r.composer).n++;
    const list = [...names.entries()].sort((a, b) => a[1].rank - b[1].rank || coll.compare(fold(composerInfo(a[0]).sort_name), fold(composerInfo(b[0]).sort_name)));
    strip.hidden = !(mode() === "composers" && !activeFilterCount() && list.length);
    if (strip.hidden) return;
    $("#fchips").innerHTML = list.map(([name, v]) => `<a class="fchip r${v.rank}" href="${esc(composerHref(name))}" data-act="composer" data-composer="${esc(name)}">${esc(composerInfo(name).short_name)} <span>${v.n}</span></a>`).join("");
  }

  function renderComposerHero() {
    const hero = $("#composerHero");
    if (mode() !== "composer") { hero.hidden = true; hero.innerHTML = ""; return; }
    const c = composerInfo(state.composer);
    const all = ROWS.filter((r) => r.composer === state.composer);
    const scores = all.filter((r) => r.has_editable_score).length;
    const recs = all.filter((r) => r.has_recording).length;
    const genres = (c.genres || []).filter((g) => g !== "classical" || c.genres.length > 1).map((g) => GENRE_LABEL[g] || g).join(", ");
    hero.hidden = false;
    hero.innerHTML = `
      <a class="back" href="./" data-act="composers">← All composers</a>
      <div class="hero-inner">
        ${portraitHTML(c, "hero-portrait")}
        <div>
          <p class="hero-kicker">${esc(c.era || "")}${genres ? ` · ${esc(genres)}` : ""}</p>
          <h2 class="hero-name" id="heroName">${esc(c.name)}</h2>
          <p class="hero-dates">${esc(lifeDates(c))}</p>
          <p class="hero-stats"><b>${all.length}</b> ${all.length === 1 ? "work" : "works"} · <b>${scores}</b> editable ${scores === 1 ? "score" : "scores"} · <b>${recs}</b> ${recs === 1 ? "recording" : "recordings"}</p>
          ${c.portrait_url ? `<p class="hero-credit">Portrait: <a href="${esc(safeUrl(c.portrait_source))}" target="_blank" rel="noopener">Wikimedia Commons</a> · ${esc(c.portrait_licence || "")}</p>` : ""}
        </div>
      </div>`;
    document.title = `${c.name} — Music Library`;
  }

  function renderPager(pages) {
    const nav = $("#pager");
    if (pages <= 1) { nav.innerHTML = ""; return; }
    const cur = state.page;
    const want = new Set([1, pages, cur - 1, cur, cur + 1, cur - 2, cur + 2].filter((n) => n >= 1 && n <= pages));
    const nums = [...want].sort((a, b) => a - b);
    let html = `<button type="button" data-page="${cur - 1}" ${cur === 1 ? "disabled" : ""} aria-label="Previous page">‹</button>`;
    let prev = 0;
    for (const n of nums) {
      if (n - prev > 1) html += `<span class="gap">…</span>`;
      html += `<button type="button" data-page="${n}" ${n === cur ? 'aria-current="page"' : ""}>${n}</button>`;
      prev = n;
    }
    html += `<button type="button" data-page="${cur + 1}" ${cur === pages ? "disabled" : ""} aria-label="Next page">›</button>`;
    nav.innerHTML = html;
  }

  function fillSelect(id, key, options, allLabel) {
    const sel = $(id);
    const counts = facetCounts(key);
    const html = [`<option value="">${esc(allLabel)}</option>`];
    for (const [v, label] of options) {
      const n = counts.get(v) || 0;
      if (!n && state[key] !== v && key !== "genre") continue;
      html.push(`<option value="${esc(v)}">${esc(label)} (${n})</option>`);
    }
    sel.innerHTML = html.join("");
    sel.value = state[key];
    sel.classList.toggle("active", !!state[key]);
  }

  function uniq(key) {
    return [...new Set(ROWS.map((r) => r[key]).filter(Boolean))];
  }
  function composersSorted() {
    return uniq("composer").sort((a, b) => coll.compare(fold(composerInfo(a).sort_name), fold(composerInfo(b).sort_name)));
  }

  function renderFilters() {
    fillSelect("#f_genre", "genre", GENRES, "All genres");
    fillSelect("#f_composer", "composer", composersSorted().map((c) => [c, composerInfo(c).sort_name]), "All composers");
    const moodCounts = facetCounts("mood");
    const moods = [...new Set(ROWS.flatMap((r) => r.mood_tags_list))].sort((a, b) => (moodCounts.get(b) || 0) - (moodCounts.get(a) || 0) || a.localeCompare(b));
    fillSelect("#f_mood", "mood", moods.map((m) => [m, m]), "Any mood");
    const eras = uniq("era").sort((a, b) => eraYear(a) - eraYear(b));
    fillSelect("#f_era", "era", eras.map((e) => [e, e]), "All eras");
    fillSelect("#f_energy", "energy", ENERGY, "Any energy");
    fillSelect("#f_licence", "licence", LICENCE_ORDER.map((k) => [k, LICENCE[k][0]]), "Any licence");
    fillSelect("#f_scope", "scope", [["worldwide", "Worldwide / life+70 PD"], ["us_pd_only", "US public domain only"]], "Any territory");
    $("#f_rec").value = state.rec; $("#f_rec").classList.toggle("active", !!state.rec);
    $("#f_verified").value = state.verified; $("#f_verified").classList.toggle("active", !!state.verified);
    $("#f_sort").value = state.sort; $("#f_sort").classList.toggle("active", !!state.sort);
    $("#f_score").checked = !!state.score;
    $("#f_featured").checked = !!state.featured;
    if (document.activeElement !== $("#q")) $("#q").value = state.q;
    const active = activeFilterCount();
    $("#filterCount").hidden = !active;
    $("#filterCount").textContent = active;
    $("#clearAll").hidden = !active;
    $$(".view-toggle button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.layout === state.layout)));
    $(".view-toggle").hidden = mode() === "composers";
    $(".sort-field").hidden = mode() === "composers";
  }

  function eraYear(e) {
    const order = ["Medieval", "Renaissance", "Baroque", "Classical", "Romantic", "Late Romantic", "Modern"];
    const i = order.findIndex((o) => e.startsWith(o));
    return i < 0 ? 99 : i;
  }

  function renderNav() {
    const m = mode();
    const cur = state.picks ? "picks" : m === "works" ? "works" : "composers";
    $$(".modes [data-nav]").forEach((b) => {
      if (b.dataset.nav === cur) b.setAttribute("aria-current", "page"); else b.removeAttribute("aria-current");
    });
  }

  function renderGenreStrip() {
    const counts = new Map();
    for (const r of ROWS) counts.set(r.genre, (counts.get(r.genre) || 0) + 1);
    const btn = (v, label, n) =>
      `<button type="button" data-genre="${esc(v)}" aria-pressed="${state.genre === v}" class="${n === 0 ? "empty" : ""}" title="${n === 0 ? "Coming in later batches" : ""}">${esc(label)}<small>${n}</small></button>`;
    $("#genreStrip").innerHTML = btn("", "All genres", ROWS.length) + GENRES.map(([v, l]) => btn(v, l, counts.get(v) || 0)).join("");
  }

  function renderBrowse() {
    $(".browse").hidden = mode() === "composers";
    $$(".browse-tabs button").forEach((b) => {
      const selected = b.dataset.browse === browseTab;
      b.setAttribute("aria-selected", String(selected));
      b.tabIndex = selected ? 0 : -1;
    });
    $("#browseChips").setAttribute("aria-labelledby", "browse-" + browseTab);
    const counts = facetCounts(browseTab);
    let items;
    if (browseTab === "genre") items = GENRES.map(([v, l]) => [v, l]);
    else if (browseTab === "era") items = uniq("era").sort((a, b) => eraYear(a) - eraYear(b)).map((e) => [e, e]);
    else if (browseTab === "composer") items = composersSorted().map((c) => [c, composerInfo(c).short_name]);
    else items = [...counts.keys()].sort((a, b) => counts.get(b) - counts.get(a) || a.localeCompare(b)).slice(0, 60).map((m) => [m, m]);
    $("#browseChips").innerHTML = items.map(([v, l]) => {
      const n = counts.get(v) || 0;
      const on = state[browseTab] === v;
      return `<button type="button" class="chip" data-facet="${browseTab}" data-value="${esc(v)}" aria-pressed="${on}" ${!n && !on ? "disabled" : ""} title="${esc(v)}">${esc(l)}<small>${n}</small></button>`;
    }).join("");
  }

  function renderStats() {
    const n = ROWS.length;
    const scores = ROWS.filter((r) => r.has_editable_score).length;
    const recs = ROWS.filter((r) => r.has_recording).length;
    const clean = ROWS.filter((r) => r.licence_status === "clean").length;
    const composers = new Set(ROWS.map((r) => r.composer)).size;
    $("#stats").innerHTML = [[composers, "composers"], [n, "works"], [scores, "editable scores"], [recs, "recordings"], [clean, "clean"]]
      .map(([v, l]) => `<div class="stat"><b>${v}</b><span>${l}</span></div>`).join("");
  }

  function renderPicks() {
    const picks = ROWS.filter((r) => r.editors_pick_rank).sort((a, b) => a.editors_pick_rank - b.editors_pick_rank);
    $("#picks").innerHTML = picks.map((r) => `<div class="pick" data-id="${esc(r.id)}">
      <span class="rank">${r.editors_pick_rank}</span>
      <div class="pick-body">
        <a class="pc" href="${esc(composerHref(r.composer))}" data-act="composer" data-composer="${esc(r.composer)}">${esc(r.composer_short)}</a>
        <button class="pt" type="button" data-act="open" data-id="${esc(r.id)}">${esc(r.title)}</button>
        <div class="pcat">${esc(r.catalog || "")}</div>
        <div class="why">${esc(r.editors_pick_why)}</div>
        <div class="pick-badges">${badge(r.licence_status)}${scopeBadge(r)}</div>
      </div>
      ${playBtn(r)}
    </div>`).join("");
    return picks.length;
  }

  function render() {
    clearTimeout(qTimer);
    const m = mode();
    renderNav();
    renderFilters();
    renderGenreStrip();
    renderBrowse();
    renderComposerHero();
    renderFeatured();
    if (m !== "composer") document.title = "Music Library — public-domain classical music, scores & full recordings";
    $(".picks").hidden = !(m !== "composer" && !state.q && !state.picks && !activeFilterCount()) || !$("#picks").children.length;
    if (m === "composers") renderComposers(); else renderWorks(compute());
    syncPlayButtons();
  }

  /* ---------- navigation ---------- */
  function go(changes, { push = true, scroll = true } = {}) {
    closeDetail(false);
    Object.assign(state, { page: 1, id: "" }, changes);
    writeState(push);
    render();
    if (scroll) window.scrollTo({ top: 0, behavior: "smooth" });
  }
  const openComposer = (name) => { go({ composer: name, view: "", sort: "", picks: "" }); $("#composerHero .back")?.focus({ preventScroll: true }); };
  const showComposers = () => go({ composer: "", view: "", q: "", picks: "", sort: "" });
  const showWorks = () => go({ composer: "", view: "works", picks: "" });
  const showPicks = () => go({ ...Object.fromEntries(FACETS.map((k) => [k, ""])), q: "", score: "", sort: "", view: "works", picks: "1", layout: "list" });

  /* ---------- detail drawer ---------- */
  function fmtBytes(b) {
    if (!b) return "";
    return b > 1e6 ? (b / 1e6).toFixed(1) + " MB" : Math.round(b / 1e3) + " kB";
  }
  function creditText(r) {
    const lines = [`"${r.title}"${r.catalog ? " (" + r.catalog + ")" : ""} — ${r.composer}${r.death_year ? " (d. " + r.death_year + ")" : ""}`];
    if (r.has_recording) {
      lines.push(`Recording: ${r.recording_performer || "performer not stated"} — ${r.recording_license || "licence not stated"}`);
      if (r.recording_source_url) lines.push(`  Source: ${r.recording_source_url}`);
    }
    if (r.has_editable_score) {
      lines.push(`Score: ${r.editable_format || "editable file"} — ${r.editable_license || "licence not stated"}`);
      if (r.editable_source_url) lines.push(`  Source: ${r.editable_source_url}`);
    }
    lines.push(`Licence status: ${LICENCE[r.licence_status]?.[0] || "Unverified"}${r.verified === "yes" ? "" : " (unverified)"}`);
    if (r.legal_notes) lines.push(`Notes: ${r.legal_notes}`);
    return lines.join("\n");
  }
  function linkRow(href, label, note) {
    const u = safeUrl(href);
    if (!u) return "";
    const ext = /^https?:/.test(u) ? ' target="_blank" rel="noopener"' : "";
    return `<a href="${esc(u)}"${ext}><span>${esc(label)}</span>${note ? `<small>${esc(note)}</small>` : ""}</a>`;
  }
  function listenHTML(r) {
    const modes = availableModes(r);
    const dur = (s) => (s ? fmtTime(s) : "");
    const scoreLic = r.score_status ? LICENCE[r.score_status][0] : "score licence";
    const note = {
      preview: "15 s audition",
      full: [r.stream_audio_url ? (/archive\.org/.test(r.stream_audio_url) ? "Internet Archive stream" : "Wikimedia stream") : "GitHub Release file", dur(r.duration_s)].filter(Boolean).join(" · "),
      midi: `in-browser, adjustable tempo · licence: ${scoreLic}`,
    };
    const kind = { preview: "Preview", full: "Recording", midi: "Synth" };
    const btns = modes.map((m) => `<button type="button" class="listen-btn m-${m}" data-act="mode" data-mode="${m}" data-id="${esc(r.id)}" aria-pressed="false">
        <span class="lb-icon" aria-hidden="true">▶</span>
        <span class="lb-text"><span class="lb-label">${esc(MODES[m].label)}</span><small>${esc(note[m])}</small></span>
        <span class="kind k-${m}">${kind[m]}</span>
      </button>`).join("");
    const fallback = !r.has_recording ? "" : `<p class="listen-note">Full recording won't play here? ${[
      linkRow(r.release_audio_url, "Download from the Release", fmtBytes(r.release_audio_bytes)),
      linkRow(r.recording_source_url, "open the source page", ""),
    ].filter(Boolean).join(" or ")}</p>`;
    return `<div class="d-section d-listen"><h4>Listen</h4>
      ${btns ? `<div class="listen-grid">${btns}</div>` : "<p>No audio for this piece yet.</p>"}
      ${r.midi_play_url ? `<div class="tempo-row"><label for="dTempo">Tempo</label><input type="range" id="dTempo" class="tempo" min="0.5" max="1.5" step="0.05" value="${player.tempo}"><output id="dTempoOut">${Math.round(player.tempo * 100)}%</output><small>live MIDI only</small></div>
        <div class="roll-wrap" id="rollWrap" hidden><svg id="roll" aria-label="Piano roll"></svg></div>` : ""}
      ${fallback}
    </div>`;
  }
  function renderDetail(r) {
    const flags = (r.legal_flags || []).map((f) => {
      const soft = /render|lo-fi|courtesy|US-gov/i.test(f);
      return `<span class="flag${soft ? " soft" : ""}">${esc(f)}</span>`;
    }).join("");
    const scoreLinks = (r.score_files || []).map((p) => linkRow(p, p.split("/").pop(), p.split(".").pop().toUpperCase())).join("");
    const kv = [
      ["Catalogue", r.catalog], ["Movement", r.movement], ["Genre", GENRE_LABEL[r.genre] || r.genre], ["Era", r.era],
      ["Tempo / energy", r.tempo_energy], ["Performer", r.recording_performer], ["Quality", r.recording_quality],
      ["Recording licence", r.recording_license], ["Score format", r.editable_format], ["Score licence", r.editable_license],
      ["Verified", r.verified], ["Added by", r.added_by],
    ].filter(([, v]) => v).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("");
    const statusNote = {
      clean: "Composition and the parts we ship are PD / CC0 as far as the source pages show. Courtesy credits are still listed where the source asks.",
      attribution: "Credit is required — copy the block below into the post or video description.",
      sharealike: "ShareAlike: a remix or render of the BY-SA part may have to be released under the same licence. Do not treat as clean.",
      flagged: "Flagged: there is a known caveat (territory, US-PD-only scope, arrangement or dedication). Read the notes before commercial use.",
      unverified: "Unverified: rights could not be confirmed from the source page. Do not use commercially until checked.",
    }[r.licence_status] || "";
    const c = composerInfo(r.composer);

    $("#detail").innerHTML = `
      <a class="d-composer" href="${esc(composerHref(r.composer))}" data-act="composer" data-composer="${esc(r.composer)}">${esc(r.composer)}<span>${esc(lifeDates(c))}</span></a>
      <h2 class="d-title" id="dTitle">${esc(r.title)}</h2>
      <div class="d-kicker">${esc(r.catalog || "")}${movementSuffix(r)}${r.editors_pick_rank ? ` · ★ Editor's pick #${r.editors_pick_rank}` : ""}</div>
      <div class="badges">${badge(r.licence_status)}${scopeBadge(r)}${subStatus(r)}
        ${r.has_editable_score ? '<span class="tag score">✎ Editable score</span>' : '<span class="tag noscore">No editable score yet</span>'}</div>
      ${listenHTML(r)}
      <div class="d-actions">
        <button class="small-btn" type="button" data-act="copy" data-id="${esc(r.id)}">Copy licence + credit</button>
        <button class="small-btn" type="button" data-act="link" data-id="${esc(r.id)}">Copy link</button>
      </div>
      ${r.editors_pick_why ? `<div class="callout">${esc(r.editors_pick_why)}</div>` : ""}
      <div class="d-section"><h4>Strong excerpt</h4><p>${esc(r.notable_excerpt || "—")}</p></div>
      <div class="d-section"><h4>Video ideas</h4><p>${esc(r.video_use_ideas || "—")}</p>
        <div class="meta" style="margin-top:6px">${r.mood_tags_list.map((m) => `<button type="button" class="tag mood" data-act="mood" data-mood="${esc(m)}">${esc(m)}</button>`).join("")}</div></div>
      <div class="d-section"><h4>Licence &amp; legal</h4>
        <div class="callout muted" style="margin-bottom:8px">${esc(statusNote)}${r.midi_play_url ? " Synth renders are made from the score, so they carry the score licence." : ""}</div>
        ${flags ? `<div class="flags" style="margin-bottom:8px">${flags}</div>` : ""}
        <p class="legal">${esc(r.legal_notes || "No notes.")}</p>
        <h4 style="margin-top:10px">Credit block</h4>
        <div class="credit-box" id="creditBox" tabindex="0" role="region" aria-label="Licence and credit text">${esc(creditText(r))}</div>
      </div>
      <div class="d-section"><h4>Files &amp; links</h4><div class="links">
        ${linkRow(r.preview_url, "15 s preview MP3", "MP3")}
        ${linkRow(r.release_audio_url, "Full recording (Release audio-v1)", fmtBytes(r.release_audio_bytes))}
        ${linkRow(r.stream_audio_url, "Full recording stream", (r.stream_audio_mime || "").replace("audio/", "").toUpperCase())}
        ${scoreLinks || ""}
        ${r.midi_play_url && !(r.score_files || []).includes(r.midi_play_url) ? linkRow(r.midi_play_url, "Playable MIDI (extracted)", "MID") : ""}
        ${linkRow(r.recording_source_url, "Recording source page", "source")}
        ${linkRow(r.editable_source_url, "Score source page", "source")}
        ${linkRow(r.musescore_url, "MuseScore page", "check licence")}
      </div></div>
      ${(r.other_editions || []).length ? `<div class="d-section"><h4>Other editions (duplicates merged into this card)</h4><div class="links">
        ${r.other_editions.map((e) => linkRow(e.url, `${e.title || e.id} · ${e.source}`, e.licence)).join("")}
      </div></div>` : ""}
      <div class="d-section"><h4>Details</h4><dl class="kv">${kv}</dl></div>`;
    $("#dTempo")?.addEventListener("input", (e) => setTempo(+e.target.value));
    if (player.mode === "midi" && player.id === r.id) attachRoll();
  }
  // Index rows are slim; the full record (legal notes, sources, score files) loads on open.
  async function loadFull(r) {
    if (r._full) return r;
    const res = await fetch(`data/items/${encodeURIComponent(r.id)}.json`);
    if (!res.ok) throw new Error(res.status);
    const full = await res.json();
    delete full.mood_tags_list;
    for (const k of ["preview_url", "midi_play_url", "score_url"]) if (full[k] === undefined) delete full[k];
    return Object.assign(r, full, { _full: true });
  }
  function openDetail(id, push = true) {
    const r = BY_ID.get(id);
    if (!r) return;
    if (!r._full) {
      // Open at once from the index row, then fill in the full record.
      loadFull(r).then(() => {
        if (state.id === id && $("#drawer").classList.contains("open")) { renderDetail(r); syncPlayButtons(); }
      }).catch((err) => toast(`Could not load the full record (${err.message})`));
    }
    if (!$("#drawer").classList.contains("open")) lastFocus = document.activeElement;
    renderDetail(r);
    syncPlayButtons();
    const d = $("#drawer");
    d.inert = false;
    d.classList.add("open");
    d.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    $$(".skip, header.top, main").forEach((el) => { el.inert = true; });
    $(".drawer-panel").scrollTop = 0;
    $(".drawer-close").focus();
    if (state.id !== id) { state.id = id; writeState(push); }
  }
  function closeDetail(updateUrl = true) {
    const d = $("#drawer");
    if (!d.classList.contains("open")) return;
    d.classList.remove("open");
    d.setAttribute("aria-hidden", "true");
    d.inert = true;
    document.body.style.overflow = "";
    $$(".skip, header.top, main").forEach((el) => { el.inert = false; });
    if (updateUrl && state.id) { state.id = ""; writeState(false); }
    if (lastFocus && document.contains(lastFocus) && lastFocus !== document.body && !lastFocus.closest("[hidden]")) lastFocus.focus();
    else $("#results").focus({ preventScroll: true });
  }

  /* ---------- player: one source at a time ---------- */
  const audio = new Audio();
  audio.preload = "metadata";
  const player = { id: null, mode: null, sources: [], srcIdx: 0, tempo: 1, failed: false };
  const midi = { id: null, base: null, seq: null, sfp: null, ready: false, pos: 0, startedAt: 0, playing: false, loading: false, gen: 0, vis: null, tick: null };
  let midiLib = null;

  function availableModes(r) {
    const m = [];
    if (r.preview_url) m.push("preview");
    if (r.stream_audio_url || r.release_audio_url) m.push("full");
    if (r.midi_play_url) m.push("midi");
    return m;
  }
  function sourcesFor(r, m) {
    if (m === "preview") return [r.preview_url];
    if (m === "full") return [...new Set([r.stream_audio_url, r.release_audio_url].filter(Boolean))];
    return [];
  }
  const isPlaying = () => (player.mode === "midi" ? midi.playing || midi.loading : !!player.id && !audio.paused);

  function playItem(id, m) {
    const r = BY_ID.get(id);
    if (!r) return;
    m = m || cardMode(r);
    if (!availableModes(r).includes(m)) return;
    if (player.id === id && player.mode === m) return togglePlay();
    haltAll();
    Object.assign(player, { id, mode: m, failed: false, srcIdx: 0, sources: sourcesFor(r, m) });
    showPlayer(r);
    if (m === "midi") midiStart(r, 0);
    else loadSource(0);
    syncPlayButtons();
  }
  function loadSource(i) {
    player.srcIdx = i;
    const src = player.sources[i];
    audio.src = src;
    audio.currentTime = 0;
    updateProgress();
    const started = audio.src;
    audio.play().catch((e) => onAudioFail(started, e));
  }
  function onAudioFail(src, e) {
    if (e && e.name === "AbortError") return;
    if (e && e.name === "NotAllowedError") { toast("Press play to start"); syncPlayButtons(); return; }
    if (!player.id || player.mode === "midi" || src !== audio.src) return;
    if (player.srcIdx + 1 < player.sources.length) { loadSource(player.srcIdx + 1); return; }
    player.failed = true;
    toast(player.mode === "full" ? "This browser can't stream the recording — use Download / open recording" : "Could not play this audio");
    showPlayer(BY_ID.get(player.id));
    syncPlayButtons();
  }
  audio.addEventListener("error", () => { if (audio.getAttribute("src")) onAudioFail(audio.src); });
  function togglePlay() {
    if (!player.id) return;
    if (player.mode === "midi") return midi.playing || midi.loading ? midiPause() : midiResume();
    if (player.failed) { player.failed = false; return loadSource(0); }
    if (audio.paused) {
      const src = audio.src;
      audio.play().catch((e) => onAudioFail(src, e));
    } else audio.pause();
  }
  function haltAll() {
    if (audio.getAttribute("src")) { audio.pause(); audio.removeAttribute("src"); audio.load(); }
    midiHalt();
  }
  function stop() {
    const restoreFocus = $("#player").contains(document.activeElement);
    haltAll();
    player.id = player.mode = null;
    $("#player").hidden = true;
    document.body.classList.remove("has-player");
    syncPlayButtons();
    if (restoreFocus) ($("#drawer").classList.contains("open") ? $(".drawer-close") : $("#results")).focus({ preventScroll: true });
  }
  function position() { return player.mode === "midi" ? midiPos() : audio.currentTime || 0; }
  function duration() {
    if (player.mode === "midi") return midi.seq ? midi.seq.totalTime : 0;
    if (Number.isFinite(audio.duration) && audio.duration > 0) return audio.duration;
    const r = BY_ID.get(player.id) || {};
    return player.mode === "preview" ? 15 : r.duration_s || 0;
  }
  function seek(t) {
    const d = duration();
    if (!d) return;
    t = Math.max(0, Math.min(d, t));
    if (player.mode === "midi") midiSeek(t); else audio.currentTime = t;
    updateProgress();
  }

  function showPlayer(r) {
    const focusedMode = document.activeElement?.dataset.pmode;
    const modes = availableModes(r);
    $("#player").hidden = false;
    document.body.classList.add("has-player");
    $("#pTitle").textContent = r.title;
    $("#pComposer").textContent = r.composer;
    $("#pSub").textContent = `${r.catalog ? r.catalog + " · " : ""}${LICENCE[r.licence_status]?.[0] || ""}${player.mode === "midi" ? " · score licence: " + (LICENCE[r.score_status]?.[0] || "?") : ""}`;
    $("#pMode").textContent = MODES[player.mode].badge;
    $("#pMode").className = "p-mode k-" + player.mode;
    $("#pModes").innerHTML = ["preview", "full", "midi"].filter((m) => modes.includes(m)).map((m) =>
      `<button type="button" data-pmode="${m}" aria-pressed="${m === player.mode}" title="${esc(MODES[m].label)}">${esc(MODES[m].short)}</button>`).join("");
    if (!modes.includes("full") && r.has_editable_score) $("#pModes").insertAdjacentHTML("beforeend", `<span class="p-nofull" title="No recording yet: Synth plays the full score MIDI in the browser">no recording</span>`);
    $("#pTempoWrap").hidden = player.mode !== "midi";
    $("#pTempo").value = player.tempo;
    $("#pTempoOut").textContent = Math.round(player.tempo * 100) + "%";
    const open = player.failed && player.mode === "full" ? safeUrl(r.release_audio_url || r.recording_source_url) : "";
    $("#pOpen").hidden = !open;
    if (open) $("#pOpen").href = open;
    $("#pBar").setAttribute("aria-label", `${MODES[player.mode].label} position`);
    updateProgress();
    if (focusedMode) $("#pModes [data-pmode='" + focusedMode + "']")?.focus({ preventScroll: true });
  }
  function syncPlayButtons() {
    const playing = isPlaying();
    $$('[data-act="play"]').forEach((b) => {
      const on = b.dataset.id === player.id && b.dataset.mode === player.mode;
      b.textContent = on && playing ? "❚❚" : "▶";
      b.setAttribute("aria-pressed", String(on && playing));
      const m = MODES[b.dataset.mode] || MODES.preview;
      b.setAttribute("aria-label", `${on && playing ? "Pause" : "Play"} ${m.label.toLowerCase()} of ${BY_ID.get(b.dataset.id)?.title || "music"}`);
    });
    $$('[data-act="mode"]').forEach((b) => {
      const on = b.dataset.id === player.id && b.dataset.mode === player.mode;
      b.setAttribute("aria-pressed", String(on && playing));
      b.classList.toggle("current", on);
      $(".lb-icon", b).textContent = on && playing ? "❚❚" : "▶";
    });
    $$("#pModes [data-pmode]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.pmode === player.mode)));
    $$(".card, .pick").forEach((c) => c.classList.toggle("playing", c.dataset.id === player.id));
    $("#pBtn").textContent = playing ? "❚❚" : "▶";
    $("#pBtn").setAttribute("aria-label", playing ? "Pause" : "Play");
    $("#player").classList.toggle("loading", midi.loading && player.mode === "midi");
  }
  function updateProgress() {
    const d = duration();
    const t = Math.min(position(), d || Infinity);
    $("#pProg").style.width = d ? `${Math.min(100, (t / d) * 100)}%` : "0";
    $("#pTime").textContent = `${fmtTime(t)} / ${d ? fmtTime(d) : "–:––"}`;
    const bar = $("#pBar");
    bar.setAttribute("aria-valuemax", String(Math.round(d)));
    bar.setAttribute("aria-valuenow", String(Math.round(t)));
    bar.setAttribute("aria-valuetext", `${fmtTime(t)} of ${fmtTime(d)}`);
  }
  audio.addEventListener("play", syncPlayButtons);
  audio.addEventListener("pause", syncPlayButtons);
  audio.addEventListener("ended", () => { audio.currentTime = 0; updateProgress(); syncPlayButtons(); });
  audio.addEventListener("timeupdate", updateProgress);
  audio.addEventListener("loadedmetadata", updateProgress);
  audio.addEventListener("durationchange", updateProgress);

  /* ---------- live MIDI synth (Magenta SoundFontPlayer, loaded on first use) ---------- */
  function loadMidiLib() {
    if (!midiLib) {
      midiLib = new Promise((resolve, reject) => {
        const s = document.createElement("script");
        s.src = MIDI_LIB;
        s.onload = () => (window.core ? resolve(window.core) : reject(new Error("synth library missing")));
        s.onerror = () => { midiLib = null; reject(new Error("could not load the synth library")); };
        document.head.appendChild(s);
      });
    }
    return midiLib;
  }
  function scaleSeq(core, seq, f) {
    const s = core.sequences.clone(seq);
    for (const n of s.notes) { n.startTime /= f; n.endTime /= f; }
    for (const c of s.controlChanges || []) c.time /= f;
    for (const p of s.pitchBends || []) p.time /= f;
    for (const t of s.tempos || []) { t.time /= f; t.qpm *= f; }
    s.totalTime /= f;
    return s;
  }
  function midiPos() {
    if (!midi.seq) return 0;
    const p = midi.playing ? midi.pos + (performance.now() - midi.startedAt) / 1000 : midi.pos;
    return Math.min(p, midi.seq.totalTime);
  }
  async function midiStart(r, offset) {
    const gen = ++midi.gen;
    midi.ready = false;
    if (midi.id !== r.id) midi.seq = null;
    midi.loading = true; midi.playing = false; midi.pos = offset;
    updateProgress();
    syncPlayButtons();
    try {
      const core = await loadMidiLib();
      if (gen !== midi.gen) return;
      if (window.Tone && Tone.context.state !== "running") await Tone.start().catch(() => {});
      if (gen !== midi.gen) return;
      if (midi.id !== r.id) {
        const res = await fetch(r.midi_play_url);
        if (gen !== midi.gen) return;
        if (!res.ok) throw new Error("MIDI " + res.status);
        const base = core.midiToSequenceProto(new Uint8Array(await res.arrayBuffer()));
        if (gen !== midi.gen) return;
        Object.assign(midi, { id: r.id, base, seq: null });
      }
      midi.seq = scaleSeq(core, midi.base, player.tempo);
      if (!midi.sfp) {
        midi.sfp = new core.SoundFontPlayer(SOUNDFONT, undefined, undefined, undefined, {
          run: (n) => { try { midi.vis && midi.vis.redraw(n, true); } catch { /* visual only */ } },
          stop: () => {},
        });
      }
      await midi.sfp.loadSamples(midi.seq);
      if (gen !== midi.gen) return;
      midi.loading = false;
      midi.ready = true;
      // Tempo may have changed while samples were downloading.
      midi.seq = scaleSeq(core, midi.base, player.tempo);
      if (window.Tone && Tone.context.state !== "running") {
        syncPlayButtons(); toast("Press play to start the synth"); return;
      }
      midiRun(midi.pos);
      attachRoll();
    } catch (err) {
      if (gen !== midi.gen) return;
      midi.loading = false;
      toast("Synth unavailable: " + err.message);
      syncPlayButtons();
    }
  }
  function midiRun(offset) {
    const gen = ++midi.gen;
    midi.pos = offset; midi.startedAt = performance.now(); midi.playing = true;
    if (midi.sfp.isPlaying()) midi.sfp.stop();
    Promise.resolve().then(() => {
      if (gen !== midi.gen) return;
      return midi.sfp.start(midi.seq, undefined, offset);
    }).then(() => {
      if (gen === midi.gen && midi.playing) { clearInterval(midi.tick); midi.playing = false; midi.pos = 0; updateProgress(); syncPlayButtons(); }
    }).catch(() => {
      if (gen !== midi.gen) return;
      clearInterval(midi.tick);
      midi.playing = false;
      toast("Synth unavailable. Press play to retry.");
      updateProgress();
      syncPlayButtons();
    });
    clearInterval(midi.tick);
    midi.tick = setInterval(() => { if (player.mode === "midi") updateProgress(); }, 250);
    syncPlayButtons();
  }
  function midiPause() {
    if (midi.loading) { midi.gen++; midi.loading = false; syncPlayButtons(); return; }
    midi.pos = midiPos(); midi.playing = false; midi.gen++;
    if (midi.sfp && midi.sfp.isPlaying()) midi.sfp.stop();
    clearInterval(midi.tick);
    syncPlayButtons();
  }
  function midiResume() {
    const r = BY_ID.get(player.id);
    if (!midi.ready || !midi.seq || midi.id !== player.id) return midiStart(r, midi.pos || 0);
    if (window.Tone && Tone.context.state !== "running") Tone.start().catch(() => {});
    midiRun(midi.pos >= midi.seq.totalTime - 0.05 ? 0 : midi.pos);
  }
  function midiSeek(t) {
    if (midi.playing) midiRun(t); else midi.pos = t;
  }
  function midiHalt() {
    midi.gen++;
    midi.loading = false;
    if (midi.sfp && midi.sfp.isPlaying()) midi.sfp.stop();
    midi.playing = false; midi.pos = 0;
    clearInterval(midi.tick);
    detachRoll();
  }
  function setTempo(f) {
    f = Math.max(0.5, Math.min(1.5, f || 1));
    const was = player.tempo;
    player.tempo = f;
    for (const el of ["#pTempo", "#dTempo"]) if ($(el) && +$(el).value !== f) $(el).value = f;
    for (const el of ["#pTempoOut", "#dTempoOut"]) if ($(el)) $(el).textContent = Math.round(f * 100) + "%";
    if (player.mode !== "midi" || midi.id !== player.id || !midi.base || !window.core) return;
    const scorePos = midiPos() * was;
    midi.seq = scaleSeq(window.core, midi.base, f);
    const t = scorePos / f;
    if (midi.playing) midiRun(t); else midi.pos = t;
    if (!midi.loading) attachRoll();
    updateProgress();
  }
  function attachRoll() {
    const svg = $("#roll");
    if (!svg || !window.core || !midi.seq || player.mode !== "midi" || state.id !== player.id) return;
    try {
      svg.innerHTML = "";
      midi.vis = new window.core.PianoRollSVGVisualizer(midi.seq, svg, {
        noteHeight: 2, pixelsPerTimeStep: 40, noteRGB: "200, 200, 210", activeNoteRGB: "226, 196, 140", minPitch: 21, maxPitch: 108,
      });
      $("#rollWrap").hidden = false;
    } catch { midi.vis = null; }
  }
  function detachRoll() {
    midi.vis = null;
    if ($("#rollWrap")) $("#rollWrap").hidden = true;
  }

  /* ---------- misc ---------- */
  let toastTimer;
  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove("show"), 2600);
  }
  async function copy(text, msg) {
    const focus = document.activeElement;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      ($("#drawer").classList.contains("open") ? $(".drawer-panel") : document.body).appendChild(ta);
      ta.select();
      let copied = false;
      try { copied = document.execCommand("copy"); } catch { /* handled below */ }
      ta.remove();
      if (focus && document.contains(focus)) focus.focus();
      if (!copied) { toast("Could not copy. Select and copy the text manually."); return; }
    }
    toast(msg);
  }
  function setFilter(key, value) {
    if (key === "composer") return state.composer === value ? showComposers() : openComposer(value);
    state[key] = state[key] === value ? "" : value;
    state.page = 1;
    writeState();
    render();
  }
  function clearAll() {
    for (const k of [...FACETS.filter((f) => f !== "composer"), "q", "score", "featured", "picks", "sort"]) state[k] = "";
    state.page = 1;
    $("#q").value = "";
    writeState();
    render();
  }
  function scrollToResults() {
    const controls = $(".controls");
    const offset = getComputedStyle(controls).position === "sticky" ? controls.offsetHeight : 0;
    const top = $("#results").getBoundingClientRect().top + window.scrollY - offset - 10;
    window.scrollTo({ top: Math.max(0, top), behavior: "smooth" });
  }
  const plainClick = (e) => !(e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button > 0);

  /* ---------- events ---------- */
  function bind() {
    $("#q").addEventListener("input", (e) => {
      clearTimeout(qTimer);
      state.q = e.target.value.trim(); state.page = 1;
      if (state.q && mode() === "composers") state.view = "works";
      qTimer = setTimeout(() => { writeState(); render(); }, 120);
    });
    const selMap = { f_genre: "genre", f_mood: "mood", f_era: "era", f_energy: "energy", f_licence: "licence", f_rec: "rec", f_verified: "verified", f_sort: "sort" };
    for (const [id, key] of Object.entries(selMap)) {
      $("#" + id).addEventListener("change", (e) => { state[key] = e.target.value; state.page = 1; writeState(); render(); });
    }
    $("#f_composer").addEventListener("change", (e) => (e.target.value ? openComposer(e.target.value) : showComposers()));
    $("#f_score").addEventListener("change", (e) => { state.score = e.target.checked ? "1" : ""; state.page = 1; writeState(); render(); });
    $("#f_featured").addEventListener("change", (e) => { state.featured = e.target.checked ? "1" : ""; state.page = 1; writeState(); render(); });
    $("#showFeatured").addEventListener("click", () => { state.featured = "1"; state.page = 1; writeState(); render(); });
    $("#filtersBtn").addEventListener("click", (e) => {
      const open = $("#filters").classList.toggle("open");
      e.currentTarget.setAttribute("aria-expanded", String(open));
    });
    $("#clearAll").addEventListener("click", clearAll);
    $("#showPicks").addEventListener("click", () => { showPicks(); scrollToResults(); });
    $(".modes").addEventListener("click", (e) => {
      const b = e.target.closest("[data-nav]");
      if (!b || !plainClick(e)) return;
      e.preventDefault();
      ({ composers: showComposers, works: showWorks, picks: showPicks })[b.dataset.nav]();
    });
    $$(".view-toggle button").forEach((b) => b.addEventListener("click", () => { state.layout = b.dataset.layout; writeState(); render(); }));
    $$(".browse-tabs button").forEach((b) => b.addEventListener("click", () => { browseTab = b.dataset.browse; renderBrowse(); }));
    $(".browse-tabs").addEventListener("keydown", (e) => {
      const tabs = $$(".browse-tabs button");
      const i = tabs.indexOf(e.target);
      if (i < 0 || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) return;
      e.preventDefault();
      const next = e.key === "Home" ? 0 : e.key === "End" ? tabs.length - 1 : (i + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length;
      tabs[next].click(); tabs[next].focus();
    });
    $("#browseChips").addEventListener("click", (e) => {
      const c = e.target.closest(".chip");
      if (c) setFilter(c.dataset.facet, c.dataset.value);
    });
    $("#genreStrip").addEventListener("click", (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      state.genre = b.dataset.genre; state.page = 1; writeState(); render();
    });
    $("#pager").addEventListener("click", (e) => {
      const b = e.target.closest("button[data-page]");
      if (!b || b.disabled) return;
      state.page = +b.dataset.page; writeState(); render(); $("#results").focus({ preventScroll: true }); scrollToResults();
    });

    // Delegated actions on cards, composer cards, picks and the drawer.
    document.addEventListener("click", (e) => {
      const el = e.target.closest("[data-act], [data-close]");
      if (!el) return;
      if (el.hasAttribute("data-close")) return closeDetail();
      const id = el.dataset.id;
      switch (el.dataset.act) {
        case "play": return playItem(id, el.dataset.mode);
        case "mode": return playItem(id, el.dataset.mode);
        case "open": return openDetail(id);
        case "composer": if (!plainClick(e)) return; e.preventDefault(); return openComposer(el.dataset.composer);
        case "composers": if (!plainClick(e)) return; e.preventDefault(); return showComposers();
        case "letter": {
          e.preventDefault();
          const target = $("#letter-" + el.dataset.letter);
          if (!target) return;
          const controls = $(".controls");
          const offset = getComputedStyle(controls).position === "sticky" ? controls.offsetHeight : 0;
          window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - offset - 8, behavior: "smooth" });
          return $(".composer-card", target)?.focus({ preventScroll: true });
        }
        case "mood": closeDetail(); return setFilter("mood", el.dataset.mood);
        case "clear": return clearAll();
        case "copy": return loadFull(BY_ID.get(id)).then((r) => copy(creditText(r), "Licence + credit copied"));
        case "link": {
          const u = new URL(location.href); u.search = ""; u.searchParams.set("id", id);
          return copy(u.toString(), "Link copied");
        }
      }
    });
    $("#pBtn").addEventListener("click", togglePlay);
    $("#pClose").addEventListener("click", stop);
    $("#pTitle").addEventListener("click", () => player.id && openDetail(player.id));
    $("#pModes").addEventListener("click", (e) => {
      const b = e.target.closest("[data-pmode]");
      if (b && player.id) playItem(player.id, b.dataset.pmode);
    });
    $("#pTempo").addEventListener("input", (e) => setTempo(+e.target.value));
    $("#pBar").addEventListener("click", (e) => {
      const rect = e.currentTarget.getBoundingClientRect();
      seek(Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width)) * duration());
    });
    $("#pBar").addEventListener("keydown", (e) => {
      const d = duration();
      if (!d) return;
      const big = Math.max(5, d / 20);
      const steps = { ArrowLeft: -5, ArrowDown: -5, ArrowRight: 5, ArrowUp: 5, PageDown: -big, PageUp: big };
      if (!(e.key in steps) && e.key !== "Home" && e.key !== "End") return;
      e.preventDefault();
      seek(e.key === "Home" ? 0 : e.key === "End" ? d - 0.5 : position() + steps[e.key]);
    });

    document.addEventListener("keydown", (e) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const t = e.target;
      const typing = t.matches && t.matches("input:not([type=range]), textarea, select, [contenteditable]");
      if (e.key === "Escape") {
        if (typing && t.id === "q" && t.value) return; // let the browser clear the search box
        if ($("#drawer").classList.contains("open")) { e.preventDefault(); closeDetail(); }
        else if (player.id) { e.preventDefault(); stop(); }
        else if (typing) t.blur();
        return;
      }
      if (typing) return;
      if (e.key === " " || e.code === "Space") {
        if (t.matches && t.matches("button, a, [role=button], input")) return; // native activation
        e.preventDefault();
        if (player.id) togglePlay();
        else if (mode() !== "composers") {
          const first = compute().find((r) => cardMode(r));
          if (first) playItem(first.id);
        }
      } else if (e.key === "/" && !$("#drawer").classList.contains("open")) {
        e.preventDefault();
        $("#q").focus();
      }
    });

    // Keep focus inside the open drawer.
    document.addEventListener("keydown", (e) => {
      if (e.key !== "Tab" || !$("#drawer").classList.contains("open")) return;
      // The player sits above the drawer and stays operable, so it is part of the Tab cycle.
      const sel = "button, a[href], input, [tabindex]:not([tabindex='-1'])";
      const f = [...$$(sel, $(".drawer-panel")), ...($("#player").hidden ? [] : $$(sel, $("#player")))]
        .filter((x) => !x.disabled && x.offsetParent !== null);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      const outside = !f.includes(document.activeElement);
      if (e.shiftKey && (document.activeElement === first || outside)) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && (document.activeElement === last || outside)) { e.preventDefault(); first.focus(); }
    });

    window.addEventListener("popstate", () => {
      readState();
      $("#q").value = state.q;
      render();
      if (state.id) openDetail(state.id, false); else closeDetail(false);
    });
  }

  /* ---------- boot ---------- */
  const getJSON = (url) => fetch(url, { cache: "no-cache" }).then((res) => { if (!res.ok) throw new Error(res.status); return res.json(); });
  function unpack(part) {
    const f = part.fields;
    return part.rows.map((row) => {
      const r = {};
      f.forEach((k, i) => { r[k] = row[i]; });
      r.has_editable_score = !!r.has_editable_score;
      r.has_recording = !!r.has_recording;
      r.verified = r.verified ? "yes" : "no";
      r.editors_pick_rank = +r.editors_pick_rank || 0;
      return r;
    });
  }
  async function loadIndex() {
    let manifest;
    try { manifest = await getJSON("data/index/manifest.json"); } catch { return getJSON("data/library.json"); }
    const parts = await Promise.all(manifest.parts.map((p) => getJSON("data/index/" + p.file)));
    return parts.flatMap(unpack);
  }
  async function boot() {
    readState();
    bind();
    try {
      const [lib, comps] = await Promise.all([
        loadIndex(),
        fetch("data/composers.json", { cache: "no-cache" }).then((res) => (res.ok ? res.json() : [])).catch(() => []),
      ]);
      COMPOSERS = new Map(comps.map((c) => [c.name, c]));
      ROWS = prepare(lib);
    } catch (err) {
      $("#results").innerHTML = `<div class="empty-state">Could not load <code>data/library.json</code> (${esc(err.message)}). If you opened this file from disk, run <code>python3 -m http.server</code> in the repo root and open <code>http://localhost:8000/</code>.</div>`;
      return;
    }
    BY_ID = new Map(ROWS.map((r) => [r.id, r]));
    readState();
    renderStats();
    renderPicks();
    render();
    if (state.id) openDetail(state.id, false);
  }
  boot();
})();
