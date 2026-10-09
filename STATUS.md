# Music library — STATUS

Updated: 2026-10-09 17:30 Europe/Warsaw (CEST)

## State
**PAGES LIVE — UI REVIEW COMPLETE; FIXES READY TO COMMIT/PUSH.** Repo `LaDoger/music-library` on main (75 pieces). Release `audio-v1` contains all 64 referenced recordings (65 assets total). Data model now multi-genre. Expansion batch 1 (Bach/Wagner/Mahler/Bruckner + niches) waits until first deploy.

## Checkpoint log
| # | Time | What | Quota |
|---|---|---|---|
| CP-WM6 | 2026-10-09 18:00 | Final biography check corrected Heintz (1911) and Winkler (1886) dates in three Wagner legal notes; classification unchanged. Source citations added to manifest/report; regenerated data in scoped HEAD snapshot. Next: push correction, verify live legal notes, then close batch. Concurrent 66-row niche expansion and UI edits preserved. | Codex 47% → continue |
| CP-WM5 | 2026-10-09 17:57 | Scoped Wagner/Mahler expansion committed and pushed: 5a768be (23 clean rows, 60 score files, 23 previews, licence evidence/reports). Concurrent UI/research CSV/data edits left in working tree. Pages deployed: 268 entries; 106/106 new item, score and preview URLs HTTP 200. | Codex 47% → continue |
| CP-WM4 | 2026-10-09 17:53 | Wagner/Mahler slice integrated: 23 new clean rows (13 Wagner/10 Mahler), 60 score files, 23 15s MP3 previews (−16.5 to −16.0 LUFS). All slice metadata/hash/preview/CLI checks passed; sampled cross-audit of 170 Bach rows passed (10 source pages). Summary/research/evidence saved. Shared master now 268 rows with concurrent Bach work preserved. Next: scoped commit/push, then Pages smoke checks; no new Release audio. | quota check follows |
| CP-R1 | 2026-10-09 17:10 | Agent-library research brief written; launching Grok Build | continue |
| CP5 | 16:58 | Repo pushed; release created | continue |
| CP6 | 17:02 | Genre field + multi-genre UI brief; upload script; expand-batch1 brief (Bach/Wagner/Mahler/Bruckner first) | continue |
| CP7 | 17:10 | `scripts/sync_site_data.py` (CSV→JSON, idempotent; licence/era/energy/flags/top picks). Next: index.html + assets at repo root | continue |
| CP9 | 17:19 | First deploy LIVE: https://ladoger.github.io/music-library/ (index/js/css/json/previews/scores 200). Release audio-v1 has 65 assets. Agent-first + Codex review running. | Codex 44% OK; Claude no rate-limit → continue |
| CP8 | 17:35 | Site at repo root (index.html, assets/, .nojekyll); local http.server test via headless Chrome: search incl. catalogue nos, all filters + URL params, score toggle, chips, card/list, pagination, one-at-a-time player, Space/Esc, drawer + copy, mobile 390px; 1,200-row synthetic test ~6 ms render. README, SCHEMA, parts/UI_NOTES.md updated | continue |
| CP-UI1 | 2026-10-09 17:18 | Pages review started: briefs/protocol read; no AGENTS.md present. Inspecting keyboard/modal, ranked picks, URL state, clipboard and local/Release/source links. Next: reproduce and apply must-fixes; write parts/UI_REVIEW.md | Codex 45% primary; continue |
| CP-AF1 | 2026-10-09 17:30 | Agent-first surface DONE, commit-ready (Claude): AGENTS.md, llms.txt, docs/MCP_PLAN.md; `scripts/build_catalog.py` → data/catalog.json + 75 data/items/*.json (run automatically by sync_site_data.py, idempotent); `src/musiclib` CLI + pyproject (search/get/credit/download/render/trim/arrange hook, stdlib only). Tested: pip install -e in venv, render from .mid and zip member, −15.9 LUFS, remote/Pages mode via local server, UI still renders 24 cards. Footer + noscript links added to index.html; README CLI/soundfont section; SCHEMA agent-files note | Claude no rate-limit; Codex 45% → continue |
| CP-UI2 | 2026-10-09 17:24 | Must-fixes applied for ranked picks, modal focus/inert state, URL validation/clamping, search debounce/history, clipboard feedback, keyboard tabs/seek and pagination focus. Links: 125 local files present, 86/86 sources HTTP 200, 64/64 recording assets present on Release. Next: browser regression/accessibility/scale checks and UI_REVIEW.md; review newly-created AGENTS.md | Codex below 85%; continue |
| CP-UI3 | 2026-10-09 17:30 | Review complete: parts/UI_REVIEW.md; browser regression scripts/check_pages_ui.cjs passes (search/facets/reload, ranked picks, modal/history/focus, copy denial, real audio/seek, responsive 320–1280px); axe main/modal zero WCAG A/AA violations; 1200-row test capped at 24 cards (median 7.4ms, one 152.8ms sample); licence/data checks pass. AGENTS.md/llms.txt claims corrected; UI_NOTES/README updated. Next: commit/push review + agent-first changes; verify deployed site | Codex 45% primary; continue |

## Resume steps
0. **Agent-first files (uncommitted, separate from the Codex UI-review edits to assets/ + index.html body):** `git add AGENTS.md llms.txt docs/MCP_PLAN.md pyproject.toml src/musiclib scripts/build_catalog.py scripts/sync_site_data.py data/catalog.json data/items .gitignore README.md SCHEMA.md` (+ index.html footer line once the UI review is merged), commit, push. Then check https://ladoger.github.io/music-library/llms.txt and /data/catalog.json return 200. After any CSV change run `python3 scripts/sync_site_data.py` (rebuilds catalog + items too).
1. Review `git status`; include the UI review changes: index.html, assets/app.js, assets/styles.css, scripts/check_pages_ui.cjs, parts/UI_REVIEW.md, parts/UI_NOTES.md, README.md, AGENTS.md, llms.txt and STATUS.md. Preserve concurrent agent-first changes listed above. **Never** add files/audio/.
2. Commit/push the reviewed changes, then verify the live Pages URL, ranked picks (`?picks=1`), detail keyboard focus and agent links. Pages is already enabled (CP9).
3. Release inventory is complete, including `grieg_peer_gynt_morning_mood.flac`; no re-upload is required.
4. UI review is in parts/UI_REVIEW.md. Re-run locally with `NODE_PATH=/tmp/music-ui-review/node_modules node scripts/check_pages_ui.cjs` (install Playwright there if absent), `python3 scripts/sync_site_data.py --check`, `python3 scripts/build_catalog.py --check`, and `git diff --check`. After deployed smoke checks, continue briefs/BRIEF_expand_batch1.md.

## Scope (standing)
Any legally usable good music, any genre. Editable scores first. Verify licences per item. Quality bar: no filler.

## Codex Wagner/Mahler batch 1 resume

The verified 23-row slice is committed/pushed in 5a768be: 13 Wagner + 10 Mahler, 60 score files and 23 validated 15s auditions. Report: parts/BATCH1_codex_SUMMARY.md. Deployment checks: 268 live catalogue entries, 106/106 new URLs HTTP 200. Final arranger-date correction is prepared as a separate scoped commit; push and verify the three updated live legal notes. Unverified Mahler symphony candidates remain research-only in parts/BATCH1_codex_RESEARCH.md. Preserve concurrent work; after later CSV changes run python3 scripts/sync_site_data.py and python3 scripts/build_catalog.py --check. No audio-v1 upload is needed.
