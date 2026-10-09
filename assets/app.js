/* Music Library UI — vanilla JS, no build step. Data: data/library.json (built by scripts/sync_site_data.py).
   Scales by filtering a precomputed in-memory index and rendering one page (24 rows) at a time. */
(() => {
  "use strict";

  const PAGE_SIZE = 24;
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

  // Filter keys <-> URL params. Facet filters are single-value selects.
  const FACETS = ["genre", "composer", "mood", "era", "energy", "licence", "rec", "verified"];
  const PARAMS = ["q", ...FACETS, "score", "picks", "sort", "view", "page", "id"];

  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const fold = (s) => String(s || "").normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const squash = (s) => s.replace(/[\s.,;:/()\-–'"]+/g, "");
  const safeUrl = (u) => (/^(https?:\/\/|previews\/|files\/|data\/)/i.test(u || "") ? u : "");
  const surname = (name) => { const p = String(name).split(" "); return p[p.length - 1]; };

  let ROWS = [];
  let BY_ID = new Map();
  const state = {};
  const audio = new Audio();
  audio.preload = "none";
  let currentId = null;
  let lastFocus = null;
  let browseTab = "genre";
  let qTimer;

  /* ---------- data ---------- */
  function prepare(rows) {
    return rows.map((r) => {
      const text = fold(r.search_text || [r.title, r.composer, r.catalog, r.mood_tags].join(" "));
      return Object.assign(r, {
        _text: text,
        _squash: squash(text),
        _title: fold(r.title),
        _composer: fold(r.composer),
        _catalog: squash(fold(r.catalog)),
        genre: r.genre || "other",
        mood_tags_list: r.mood_tags_list || String(r.mood_tags || "").split(";").map((s) => s.trim()).filter(Boolean),
      });
    });
  }

  /* ---------- state <-> URL ---------- */
  function readState() {
    const p = new URLSearchParams(location.search);
    for (const k of PARAMS) state[k] = p.get(k) || "";
    state.page = Math.max(1, parseInt(state.page, 10) || 1);
    state.view = state.view === "list" ? "list" : "grid";
    for (const k of ["score", "picks"]) state[k] = state[k] === "1" ? "1" : "";
    const allowed = {
      genre: GENRES.map(([v]) => v), energy: ENERGY.map(([v]) => v), licence: LICENCE_ORDER,
      rec: ["0", "1"], verified: ["yes", "unverified"], sort: ["score", "title", "composer", "year", "energy"],
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
      if (v && !(k === "page" && v === 1) && !(k === "view" && v === "grid")) p.set(k, v);
    }
    const qs = p.toString();
    const url = location.pathname + (qs ? "?" + qs : "") + location.hash;
    if (url !== location.pathname + location.search + location.hash) history[push ? "pushState" : "replaceState"](null, "", url);
  }

  /* ---------- filtering ---------- */
  function tokens() {
    return fold(state.q).split(/\s+/).filter(Boolean);
  }
  function facetValue(r, k) {
    switch (k) {
      case "licence": return r.licence_status;
      case "rec": return r.has_recording ? "1" : "0";
      case "verified": return r.verified === "yes" ? "yes" : "unverified";
      default: return r[k];
    }
  }
  function matches(r, toks, except) {
    if (state.score && !r.has_editable_score) return false;
    if (state.picks && !r.top_pick_rank) return false;
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
    if (r.top_pick_rank) s += 3 + (16 - r.top_pick_rank) / 16;
    if (r.has_editable_score) s += 1;
    return s;
  }
  function compute() {
    const toks = tokens();
    const res = ROWS.filter((r) => matches(r, toks, null));
    const by = {
      title: (a, b) => a.title.localeCompare(b.title),
      composer: (a, b) => surname(a.composer).localeCompare(surname(b.composer)) || a.title.localeCompare(b.title),
      year: (a, b) => (+a.death_year || 9999) - (+b.death_year || 9999) || a.title.localeCompare(b.title),
      energy: (a, b) => (ENERGY_RANK[b.energy] || 0) - (ENERGY_RANK[a.energy] || 0) || a.title.localeCompare(b.title),
      score: (a, b) => (b.has_editable_score - a.has_editable_score) || surname(a.composer).localeCompare(surname(b.composer)) || a.title.localeCompare(b.title),
    }[state.sort];
    if (by) res.sort(by);
    else if (state.picks) res.sort((a, b) => a.top_pick_rank - b.top_pick_rank);
    else {
      const rel = new Map(res.map((r) => [r, relevance(r, toks)]));
      res.sort((a, b) => rel.get(b) - rel.get(a) || a.title.localeCompare(b.title));
    }
    return res;
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
  const subStatus = (r) => {
    const parts = [];
    if (r.recording_status) parts.push(`rec <b>${esc(LICENCE[r.recording_status][0])}</b>`);
    if (r.score_status) parts.push(`score <b>${esc(LICENCE[r.score_status][0])}</b>`);
    return parts.length > 1 || (parts.length && r.licence_status !== (r.recording_status || r.score_status))
      ? `<span class="sub-status">${parts.join(" · ")}</span>` : "";
  };
  const playIcon = (id) => (id === currentId && !audio.paused ? "❚❚" : "▶");
  const playBtn = (r, cls = "") =>
    r.preview_url
      ? `<button class="play-btn ${cls}" type="button" data-act="play" data-id="${esc(r.id)}" aria-label="Play 15 s preview of ${esc(r.title)}">${playIcon(r.id)}</button>`
      : `<button class="play-btn ${cls}" type="button" disabled aria-label="No preview">▶</button>`;

  function cardHTML(r) {
    const cat = r.catalog ? `<span class="cat">${esc(r.catalog)}</span>` : "";
    const moods = r.mood_tags_list.slice(0, 4).map((m) => `<button type="button" class="tag mood" data-act="mood" data-mood="${esc(m)}">${esc(m)}</button>`).join("");
    const score = r.has_editable_score
      ? `<span class="tag score" title="${esc(r.editable_format || "Editable score")}">✎ Score</span>`
      : `<span class="tag noscore" title="No editable score yet">no score</span>`;
    const rec = r.has_recording ? `<span class="tag" title="Full recording on GitHub Release">♫ Recording</span>` : "";
    return `<article class="card${r.id === currentId ? " playing" : ""}" data-id="${esc(r.id)}">
      <div class="card-head">
        ${playBtn(r)}
        <div class="card-title">
          <h3><button type="button" data-act="open" data-id="${esc(r.id)}">${esc(r.title)}</button></h3>
          <div class="composer">${esc(r.composer)} ${cat}</div>
        </div>
      </div>
      <div class="meta">${score}${rec}<span class="tag" title="${esc(r.tempo_energy)}">⚡ ${esc(ENERGY_LABEL[r.energy] || r.energy || "?")}</span>${moods}</div>
      ${r.video_use_ideas ? `<p class="excerpt">${esc(r.video_use_ideas)}</p>` : ""}
      <div class="badges">${badge(r.licence_status)}${subStatus(r)}${r.top_pick_rank ? `<span class="tag" title="Top pick">★ #${r.top_pick_rank}</span>` : ""}</div>
    </article>`;
  }

  function renderResults(res) {
    const pages = Math.max(1, Math.ceil(res.length / PAGE_SIZE));
    if (state.page > pages) state.page = pages;
    writeState();
    const slice = res.slice((state.page - 1) * PAGE_SIZE, state.page * PAGE_SIZE);
    const box = $("#results");
    box.className = "results " + state.view;
    if (!slice.length) {
      const g = state.genre && GENRE_LABEL[state.genre];
      box.innerHTML = `<div class="empty-state"><p><b>No matches.</b> ${g && !ROWS.some((r) => r.genre === state.genre)
        ? `No ${esc(g)} pieces yet — they arrive in later batches (only legally clean material, no filler).`
        : "Try fewer filters or a different spelling (catalogue numbers work with or without spaces: BWV565, Op 27)."}</p>
        <button class="btn" type="button" data-act="clear">Clear all filters</button></div>`;
    } else {
      box.innerHTML = slice.map(cardHTML).join("");
    }
    const from = res.length ? (state.page - 1) * PAGE_SIZE + 1 : 0;
    const to = Math.min(res.length, state.page * PAGE_SIZE);
    $("#resultCount").innerHTML = `<b>${res.length}</b> of ${ROWS.length} pieces${res.length > PAGE_SIZE ? ` · showing ${from}–${to}` : ""}`;
    renderPager(pages);
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

  function renderFilters() {
    fillSelect("#f_genre", "genre", GENRES, "All genres");
    const composers = uniq("composer").sort((a, b) => surname(a).localeCompare(surname(b)));
    fillSelect("#f_composer", "composer", composers.map((c) => [c, c]), "All composers");
    const moodCounts = facetCounts("mood");
    const moods = [...new Set(ROWS.flatMap((r) => r.mood_tags_list))].sort((a, b) => (moodCounts.get(b) || 0) - (moodCounts.get(a) || 0) || a.localeCompare(b));
    fillSelect("#f_mood", "mood", moods.map((m) => [m, m]), "Any mood");
    const eras = uniq("era").sort((a, b) => eraYear(a) - eraYear(b));
    fillSelect("#f_era", "era", eras.map((e) => [e, e]), "All eras");
    fillSelect("#f_energy", "energy", ENERGY, "Any energy");
    fillSelect("#f_licence", "licence", LICENCE_ORDER.map((k) => [k, LICENCE[k][0]]), "Any licence");
    $("#f_rec").value = state.rec; $("#f_rec").classList.toggle("active", !!state.rec);
    $("#f_verified").value = state.verified; $("#f_verified").classList.toggle("active", !!state.verified);
    $("#f_sort").value = state.sort; $("#f_sort").classList.toggle("active", !!state.sort);
    $("#f_score").checked = !!state.score;
    if (document.activeElement !== $("#q")) $("#q").value = state.q;
    const active = FACETS.filter((k) => state[k]).length + (state.score ? 1 : 0) + (state.q ? 1 : 0) + (state.picks ? 1 : 0);
    $("#filterCount").hidden = !active;
    $("#filterCount").textContent = active;
    $("#clearAll").hidden = !active;
    $$(".view-toggle button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.view === state.view)));
  }

  function eraYear(e) {
    const order = ["Medieval", "Renaissance", "Baroque", "Classical", "Romantic", "Late Romantic", "Modern"];
    const i = order.findIndex((o) => e.startsWith(o));
    return i < 0 ? 99 : i;
  }

  function renderGenreStrip() {
    const counts = new Map();
    for (const r of ROWS) counts.set(r.genre, (counts.get(r.genre) || 0) + 1);
    const btn = (v, label, n) =>
      `<button type="button" data-genre="${esc(v)}" aria-pressed="${state.genre === v}" class="${n === 0 ? "empty" : ""}" title="${n === 0 ? "Coming in later batches" : ""}">${esc(label)}<small>${n}</small></button>`;
    $("#genreStrip").innerHTML = btn("", "All", ROWS.length) + GENRES.map(([v, l]) => btn(v, l, counts.get(v) || 0)).join("");
  }

  function renderBrowse() {
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
    else if (browseTab === "composer") items = uniq("composer").sort((a, b) => (counts.get(b) || 0) - (counts.get(a) || 0) || surname(a).localeCompare(surname(b))).map((c) => [c, surname(c)]);
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
    const genres = new Set(ROWS.map((r) => r.genre)).size;
    const composers = new Set(ROWS.map((r) => r.composer)).size;
    $("#stats").innerHTML = [[n, "pieces"], [scores, "editable scores"], [recs, "recordings"], [clean, "clean"], [composers, "composers"], [genres, genres === 1 ? "genre live" : "genres"]]
      .map(([v, l]) => `<div class="stat"><b>${v}</b><span>${l}</span></div>`).join("");
  }

  function renderPicks() {
    const picks = ROWS.filter((r) => r.top_pick_rank).sort((a, b) => a.top_pick_rank - b.top_pick_rank);
    $(".picks").hidden = !picks.length;
    $("#picks").innerHTML = picks.map((r) => `<div class="pick" data-id="${esc(r.id)}">
      <span class="rank">${r.top_pick_rank}</span>
      <div style="min-width:0">
        <button class="pt" type="button" data-act="open" data-id="${esc(r.id)}">${esc(r.title)}</button>
        <div class="pc">${esc(surname(r.composer))}${r.catalog ? " · " + esc(r.catalog) : ""}</div>
        <div class="why">${esc(r.top_pick_why)}</div>
        <div style="margin-top:6px">${badge(r.licence_status)}</div>
      </div>
      ${playBtn(r)}
    </div>`).join("");
  }

  function render() {
    clearTimeout(qTimer);
    renderFilters();
    renderGenreStrip();
    renderBrowse();
    renderResults(compute());
    syncPlayButtons();
  }

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
      flagged: "Flagged: there is a known caveat (territory, arrangement or dedication). Read the notes before commercial use.",
      unverified: "Unverified: rights could not be confirmed from the source page. Do not use commercially until checked.",
    }[r.licence_status] || "";

    $("#detail").innerHTML = `
      <div class="d-kicker">${esc(r.catalog || r.id)}${r.top_pick_rank ? ` · ★ Top pick #${r.top_pick_rank}` : ""}</div>
      <h2 class="d-title" id="dTitle">${esc(r.title)}</h2>
      <p class="d-composer">${esc(r.composer)}${r.death_year ? ` <span style="color:var(--dim)">(d. ${esc(r.death_year)})</span>` : ""}</p>
      <div class="badges">${badge(r.licence_status)}${subStatus(r)}
        ${r.has_editable_score ? '<span class="tag score">✎ Editable score</span>' : '<span class="tag noscore">No editable score yet</span>'}</div>
      <div class="d-actions">
        ${playBtn(r, "big")}<span style="color:var(--muted);font-size:13px">15 s preview</span>
        <button class="small-btn" type="button" data-act="copy" data-id="${esc(r.id)}">Copy licence + credit</button>
        <button class="small-btn" type="button" data-act="link" data-id="${esc(r.id)}">Copy link</button>
      </div>
      ${r.top_pick_why ? `<div class="callout">${esc(r.top_pick_why)}</div>` : ""}
      <div class="d-section"><h4>Strong excerpt</h4><p>${esc(r.notable_excerpt || "—")}</p></div>
      <div class="d-section"><h4>Video ideas</h4><p>${esc(r.video_use_ideas || "—")}</p>
        <div class="meta" style="margin-top:6px">${r.mood_tags_list.map((m) => `<button type="button" class="tag mood" data-act="mood" data-mood="${esc(m)}">${esc(m)}</button>`).join("")}</div></div>
      <div class="d-section"><h4>Licence &amp; legal</h4>
        <div class="callout muted" style="margin-bottom:8px">${esc(statusNote)}</div>
        ${flags ? `<div class="flags" style="margin-bottom:8px">${flags}</div>` : ""}
        <p class="legal">${esc(r.legal_notes || "No notes.")}</p>
        <h4 style="margin-top:10px">Credit block</h4>
        <div class="credit-box" id="creditBox" tabindex="0" role="region" aria-label="Licence and credit text">${esc(creditText(r))}</div>
      </div>
      <div class="d-section"><h4>Files &amp; links</h4><div class="links">
        ${linkRow(r.preview_url, "15 s preview MP3", "MP3")}
        ${linkRow(r.release_audio_url, "Full recording (Release audio-v1)", fmtBytes(r.release_audio_bytes))}
        ${scoreLinks || ""}
        ${linkRow(r.recording_source_url, "Recording source page", "source")}
        ${linkRow(r.editable_source_url, "Score source page", "source")}
        ${linkRow(r.musescore_url, "MuseScore page", "check licence")}
      </div></div>
      <div class="d-section"><h4>Details</h4><dl class="kv">${kv}</dl></div>`;
  }
  function openDetail(id, push = true) {
    const r = BY_ID.get(id);
    if (!r) return;
    if (!$("#drawer").classList.contains("open")) lastFocus = document.activeElement;
    renderDetail(r);
    const d = $("#drawer");
    d.inert = false;
    d.classList.add("open");
    d.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    $$(".skip, header.top, main, #player").forEach((el) => { el.inert = true; });
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
    $$(".skip, header.top, main, #player").forEach((el) => { el.inert = false; });
    if (updateUrl && state.id) { state.id = ""; writeState(false); }
    if (lastFocus && document.contains(lastFocus) && lastFocus !== document.body && !lastFocus.closest("[hidden]")) lastFocus.focus();
    else $("#results").focus({ preventScroll: true });
  }

  /* ---------- player (one at a time) ---------- */
  function play(id) {
    const r = BY_ID.get(id);
    if (!r || !r.preview_url) return;
    if (currentId === id) {
      if (audio.paused) audio.play().catch(onPlayError); else audio.pause();
      return;
    }
    currentId = id;
    audio.src = r.preview_url;
    audio.currentTime = 0;
    updateProgress();
    audio.play().catch(onPlayError);
    $("#player").hidden = false;
    $("#pTitle").textContent = r.title;
    $("#pSub").textContent = `${r.composer}${r.catalog ? " · " + r.catalog : ""} · ${LICENCE[r.licence_status]?.[0] || ""}`;
    syncPlayButtons();
  }
  function onPlayError(e) {
    if (e && e.name === "AbortError") return;
    toast("Could not play preview");
    syncPlayButtons();
  }
  function stop() {
    audio.pause();
    audio.removeAttribute("src");
    audio.load();
    currentId = null;
    $("#player").hidden = true;
    syncPlayButtons();
  }
  function syncPlayButtons() {
    const playing = !audio.paused && !!currentId;
    $$('[data-act="play"]').forEach((b) => {
      const on = b.dataset.id === currentId;
      b.textContent = on && playing ? "❚❚" : "▶";
      b.setAttribute("aria-pressed", String(on && playing));
      b.setAttribute("aria-label", `${on && playing ? "Pause" : "Play"} 15 s preview of ${BY_ID.get(b.dataset.id)?.title || "music"}`);
    });
    $$(".card").forEach((c) => c.classList.toggle("playing", c.dataset.id === currentId));
    $("#pBtn").textContent = playing ? "❚❚" : "▶";
    $("#pBtn").setAttribute("aria-label", playing ? "Pause" : "Play");
  }
  const fmtTime = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`;
  audio.addEventListener("play", syncPlayButtons);
  audio.addEventListener("pause", syncPlayButtons);
  audio.addEventListener("ended", () => { audio.currentTime = 0; updateProgress(); syncPlayButtons(); });
  function updateProgress() {
    const d = Number.isFinite(audio.duration) ? audio.duration : 15;
    $("#pProg").style.width = `${Math.min(100, (audio.currentTime / d) * 100)}%`;
    $("#pTime").textContent = fmtTime(audio.currentTime);
    $("#pBar").setAttribute("aria-valuemax", String(d));
    $("#pBar").setAttribute("aria-valuenow", String(audio.currentTime));
    $("#pBar").setAttribute("aria-valuetext", `${fmtTime(audio.currentTime)} of ${fmtTime(d)}`);
  }
  audio.addEventListener("timeupdate", updateProgress);
  audio.addEventListener("loadedmetadata", updateProgress);

  /* ---------- misc ---------- */
  let toastTimer;
  function toast(msg) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove("show"), 1800);
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
    state[key] = state[key] === value ? "" : value;
    state.page = 1;
    writeState();
    render();
  }
  function clearAll() {
    for (const k of [...FACETS, "q", "score", "picks", "sort"]) state[k] = "";
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

  /* ---------- events ---------- */
  function bind() {
    $("#q").addEventListener("input", (e) => {
      clearTimeout(qTimer);
      state.q = e.target.value.trim(); state.page = 1;
      qTimer = setTimeout(() => { writeState(); render(); }, 120);
    });
    const selMap = { f_genre: "genre", f_composer: "composer", f_mood: "mood", f_era: "era", f_energy: "energy", f_licence: "licence", f_rec: "rec", f_verified: "verified", f_sort: "sort" };
    for (const [id, key] of Object.entries(selMap)) {
      $("#" + id).addEventListener("change", (e) => { state[key] = e.target.value; state.page = 1; writeState(); render(); });
    }
    $("#f_score").addEventListener("change", (e) => { state.score = e.target.checked ? "1" : ""; state.page = 1; writeState(); render(); });
    $("#filtersBtn").addEventListener("click", (e) => {
      const open = $("#filters").classList.toggle("open");
      e.currentTarget.setAttribute("aria-expanded", String(open));
    });
    $("#clearAll").addEventListener("click", clearAll);
    $("#showPicks").addEventListener("click", () => {
      clearAll();
      state.picks = "1"; state.view = "list"; writeState(); render(); scrollToResults();
    });
    $$(".view-toggle button").forEach((b) => b.addEventListener("click", () => { state.view = b.dataset.view; writeState(); render(); }));
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

    // Delegated actions on cards, picks and the drawer.
    document.addEventListener("click", (e) => {
      const el = e.target.closest("[data-act], [data-close]");
      if (!el) return;
      if (el.hasAttribute("data-close")) return closeDetail();
      const id = el.dataset.id;
      switch (el.dataset.act) {
        case "play": return play(id);
        case "open": return openDetail(id);
        case "mood": closeDetail(); return setFilter("mood", el.dataset.mood);
        case "clear": return clearAll();
        case "copy": return copy(creditText(BY_ID.get(id)), "Licence + credit copied");
        case "link": {
          const u = new URL(location.href); u.search = ""; u.searchParams.set("id", id);
          return copy(u.toString(), "Link copied");
        }
      }
    });
    $("#pBtn").addEventListener("click", () => currentId && play(currentId));
    $("#pClose").addEventListener("click", stop);
    $("#pTitle").addEventListener("click", () => currentId && openDetail(currentId));
    $("#pBar").addEventListener("click", (e) => {
      if (!audio.duration) return;
      const rect = e.currentTarget.getBoundingClientRect();
      audio.currentTime = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width)) * audio.duration;
      updateProgress();
    });
    $("#pBar").addEventListener("keydown", (e) => {
      if (!Number.isFinite(audio.duration)) return;
      const steps = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1, PageDown: -5, PageUp: 5 };
      if (!(e.key in steps) && e.key !== "Home" && e.key !== "End") return;
      e.preventDefault();
      audio.currentTime = e.key === "Home" ? 0 : e.key === "End" ? audio.duration : Math.max(0, Math.min(audio.duration, audio.currentTime + steps[e.key]));
      updateProgress();
    });

    document.addEventListener("keydown", (e) => {
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const t = e.target;
      const typing = t.matches && t.matches("input, textarea, select, [contenteditable]");
      if (e.key === "Escape") {
        if (typing && t.id === "q" && t.value) return; // let the browser clear the search box
        if ($("#drawer").classList.contains("open")) { e.preventDefault(); closeDetail(); }
        else if (currentId) { e.preventDefault(); stop(); }
        else if (typing) t.blur();
        return;
      }
      if (typing) return;
      if (e.key === " " || e.code === "Space") {
        if (t.matches && t.matches("button, a, [role=button]")) return; // native activation
        e.preventDefault();
        if (currentId) play(currentId);
        else {
          const first = compute().find((r) => r.preview_url);
          if (first) play(first.id);
        }
      } else if (e.key === "/" && !$("#drawer").classList.contains("open")) {
        e.preventDefault();
        $("#q").focus();
      }
    });

    // Keep focus inside the open drawer.
    $("#drawer").addEventListener("keydown", (e) => {
      if (e.key !== "Tab") return;
      const f = $$("button, a[href], [tabindex]:not([tabindex='-1'])", $(".drawer-panel")).filter((x) => !x.disabled);
      if (!f.length) return;
      const first = f[0], last = f[f.length - 1];
      if (e.shiftKey && (document.activeElement === first || document.activeElement === $(".drawer-panel"))) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });

    window.addEventListener("popstate", () => {
      readState();
      $("#q").value = state.q;
      render();
      if (state.id) openDetail(state.id, false); else closeDetail(false);
    });
  }

  /* ---------- boot ---------- */
  async function boot() {
    readState();
    bind();
    try {
      const res = await fetch("data/library.json", { cache: "no-cache" });
      if (!res.ok) throw new Error(res.status);
      ROWS = prepare(await res.json());
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
