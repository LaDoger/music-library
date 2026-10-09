# Pages UI review

Reviewed: 2026-10-09 17:29 CEST. Scope: `index.html`, `assets/app.js`, `assets/styles.css`, all 75 rows in `data/library.json`, the Pages and agent-first briefs, and the newly created `AGENTS.md` / `llms.txt`. No AGENTS.md existed at the first inspection; it was read once the concurrent agent-first work created it.

**Result: all identified must-fixes applied locally. Ready for commit and deployment review.** No catalogue licence classifications needed changing. This review checks UI/data consistency and link availability; it does not repeat the underlying legal research.

## Must-fixes — applied

| Finding | Fix and evidence |
|---|---|
| “See all ranked” returned all 75 pieces and relevance order could put an editable score ahead of a higher-ranked pick. | Added shareable `picks=1` filter. Only the 15 top picks appear, in exact rank order with default sort; Clear all removes it. Browser checks compare all 15 IDs with the data. |
| Closed drawer controls remained keyboard-accessible; `/` focused search behind an open modal; the player sat above the modal scrim. | Closed drawer is inert; opening it makes the background, skip link and player inert. Initial focus goes to Close, Tab/Shift+Tab wrap within the drawer, and close restores focus or falls back to results. Search shortcut stays within the modal. Player now sits below the modal. Browser tests cover opening, closing, wrapping, Back/Forward and deep links. |
| `?score=0` enabled the score filter; invalid facet values could silently filter everything; `?page=999` showed a clamped page while leaving the wrong URL. | Validate booleans, supported filter/sort values and item IDs. Write the clamped page back to the URL. Browser test confirms `score=0` is off, invalid filters/IDs disappear and page 999 becomes page 4. |
| Delayed search could survive another action; Back/Forward could leave a focused search field showing the previous query. | Update query state immediately, cancel pending debounce when rendering, and explicitly synchronize search on history navigation. Test covers immediate Clear all and history changes while search is focused. |
| Clipboard fallback announced success even if copying failed; its hidden textarea could leave keyboard focus lost. | Check the fallback result, announce failure honestly, place the fallback inside an open drawer and restore focus. Tests cover real clipboard text/link contents and denial of both copy methods. |
| Browse tabs lacked keyboard tab behavior; seek was pointer-only; pagination discarded focus; preview labels always said Play. | Added native top-pick buttons, tab relationships and Arrow/Home/End navigation; a labelled seek slider with keyboard controls; focus on results after pagination; Play/Pause labels and explicit view-button names. Real MP3 playback verifies a single Audio object, switching tracks, seeking and Space/Esc. |
| Small count text had 3.66:1 contrast; the scrollable credit block could not be focused for keyboard scrolling. | Raised the dim text colour and made the labelled credit region focusable. Automated axe WCAG A/AA scans of the main page and open drawer report zero violations after these fixes. |
| Agent guidance claimed every row had a checked licence and all per-item URL fields were absolute, despite four unverified rows and preserved relative fields. | Corrected AGENTS.md and llms.txt introductions to distinguish research rows from cleared material; documented the per-item `*_abs` URL fields explicitly. The agent-first recipes, stable IDs, catalogue/CLI pointers and footer links remain available. |

## Link and licence checks

- **Local assets:** all 125 unique preview/score files referenced by the data exist. This includes 75 preview MP3s and 50 distinct score files. Browser tests serve the actual site under `/music-library/`, so the Pages subpath resolves correctly.
- **Release:** all 64 recording URLs match `https://github.com/LaDoger/music-library/releases/download/audio-v1/<local_audio_basename>`. The public release inventory has 65 assets and contains every referenced filename, including `grieg_peer_gynt_morning_mood.flac`. The old missing-recording note in UI_NOTES.md and STATUS.md was removed. Full recordings were not downloaded or uploaded for this review.
- **Sources:** all 86 unique recording/score/MuseScore source URLs returned HTTP 200 with redirects followed during the review. No broken source link was found.
- **Badges:** all rows match the generator's separate recording/score classes and overall severity/verification rules: **49 Clean, 5 Credit required, 11 ShareAlike, 6 Flagged, 4 Unverified**. CC BY and BY-SA are distinct; unverified rows never become Clean. Score-only renders use the score class. Mixed PD recordings/BY-SA scores retain their separate labels. Legal notes and territorial caveats remain visible in details.
- Generated data checks pass: `python3 scripts/sync_site_data.py --check` and `python3 scripts/build_catalog.py --check`. `data/library.json` was not hand-edited.

## UX, mobile and scale

Search passes for `BWV565`, `bwv 565`, `Op 27`, `K331` and accent-free `dvorak`. All eight facets, the editable-score toggle, reloadable URLs, clear-all, top picks, pagination, card/list view, credit/link copy, detail history, keyboard controls and actual audio playback pass browser regression checks.

Card/list layouts were checked at **320, 390, 560, 561, 720, 999, 1000 and 1280 px**: no document overflow or clipped result cards. Mobile filters collapse below 1000 px, remain open after a desktop/mobile round trip when opened by the user, and can be closed again. The 390 px drawer fits the viewport. Chrome was used; Safari/Firefox and a physical mobile device were not exercised.

The current JSON is 178,240 bytes. A **1,200-row** synthetic catalogue (2.49 MiB compact JSON) rendered **24 result cards**. Five full filter/facet/render samples were **6.9, 9.9, 152.8, 7.4, 5.8 ms**: median **7.4 ms**, maximum **152.8 ms**. Pagination is a suitable DOM bound for 1000+ rows; these desktop timings do not establish a low-end mobile first-load budget. UI_NOTES.md now records the measured range instead of assuming every render takes 6 ms.

## Nice-to-have — follow-up

- Profile download, JSON parsing, search latency and memory on a slower mobile device. Use the new compact agent catalogue as a starting point for a dedicated UI index/detail split when full-record payloads become expensive.
- Precompute invariant facet option lists and cache query/facet counts if profiling shows repeated passes becoming costly; consider an A–Z composer browser for hundreds of composers.
- Add periodic CI link checks for local paths, public Release inventory and source URLs so future batches do not introduce dead links. Keep link availability separate from licence verification.
- Generate a concise credit block for only the parts actually used, with structured edition credits, licence URLs and user-specified changes; keep the complete legal notes available separately. Current copy text contains the original metadata/notes and should be reviewed for the chosen use.
- Consider 44 px touch targets for small chips/pagination and user-agent testing in Safari/Firefox. Add waveform/excerpt markers when structured timestamps become available.

## Reproduce the browser checks

The regression runner starts and stops its own local HTTP server and uses an installed Chrome. Playwright is a development-only dependency and can be installed outside the checkout:

```bash
npm install --prefix /tmp/music-ui-review playwright
NODE_PATH=/tmp/music-ui-review/node_modules node scripts/check_pages_ui.cjs
node --check assets/app.js
python3 scripts/sync_site_data.py --check
python3 scripts/build_catalog.py --check
git diff --check
```

Use `CHROME_BIN` to point to another Chrome executable. The browser runner verifies real MP3 playback, so its static test server supports HTTP byte ranges. Accessibility scans additionally used axe-core installed in the same temporary dependency directory.

## Checkpoints

- **CP-UI1:** read briefs/protocol, established baseline and identified defects; usage script reported Codex primary 45%, below the 85% handoff threshold.
- **CP-UI2:** applied interaction fixes; verified local files, source URLs and Release inventory; updated STATUS.md and ran the usage script.
- **CP-UI3:** completed browser/accessibility/data/scale checks, reviewed the agent-first guidance, wrote this report and refreshed UI_NOTES.md / STATUS.md; usage checked again. No quota handoff required.

No secrets were printed and no files/audio content was changed or committed. Existing concurrent agent-first work was preserved. This task did not commit, push or deploy the review fixes.
