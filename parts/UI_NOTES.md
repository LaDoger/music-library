# Pages UI — architecture notes (built for 1000+ rows)

Live: https://ladoger.github.io/music-library/ (GitHub Pages, branch `main`, folder `/` root)

## Files
```
index.html            shell: header, top picks, controls, results, drawer, mini player
assets/styles.css     dark theme, amber/orange accent, mobile-first (breakpoints 560 / 720 / 1000 px)
assets/app.js         all logic, vanilla JS, no build step, no external requests except the data file
data/library.json     one array of rows, built by scripts/sync_site_data.py (never hand-edit)
.nojekyll             serve files as-is (no Jekyll pass)
previews/*.mp3        15 s clips (relative URLs from the root page)
files/scores/*        editable scores (relative URLs)
full recordings       GitHub Release audio-v1 (release_audio_url), not in git
```
The site sits at the repo root so `previews/` and `files/scores/` resolve without copies or rewrites.

## Data flow
`library.csv` (+ README top-picks table, files on disk) → `python3 scripts/sync_site_data.py` → `data/library.json` → browser.

The sync script derives every UI field (genre, era, energy, licence classes, legal flags, score file list,
release URL, top pick rank, `search_text`). It is deterministic: re-running without input changes gives a
byte-identical file. `--check` prints the summary and warnings without writing.

Adding a genre batch: add `genre` (and optionally `era`) columns to the CSV rows or rely on the previous JSON;
the UI already lists all 11 schema genres (empty ones are dimmed, "coming in later batches").

## Licence badge logic (never overclaim)
- `recording_status` / `score_status` are classified separately from the licence strings.
- `licence_status` = the most restrictive of the two, order `clean < attribution < flagged < sharealike < unverified`.
- `FLAGGED` in the sync script lists rows with a known caveat (Holst territory, band arrangements, retired CC PD
  dedication). These can never show "Clean".
- `verified != yes` always forces `unverified`.
- Cards show the overall badge plus "rec X · score Y" when the parts differ, so a PD recording with a BY-SA score
  is visibly ShareAlike only on the score side.
- `legal_flags` are informational chips derived from `legal_notes` (US-gov PD territorial, own MIDI render, lo-fi,
  courtesy credit, arrangement risk). They do not change the badge.

## Search / filter performance
- On load each row gets precomputed lowercase, diacritic-folded `_text` plus a squashed copy without spaces/dots,
  so `BWV565`, `bwv 565`, `op.27`, `Dvorak` all match. Query tokens are ANDed.
- Filtering is a single linear pass; facet counts are one extra pass per facet. Measured with 1,200 synthetic rows
  (2.7 MB JSON) in headless Chrome: full filter + facet counts + render of one page ≈ 6 ms.
- Only one page (24 rows) is in the DOM at a time; pagination instead of virtual scroll keeps URLs shareable
  (`?page=3`) and keyboard/screen-reader behaviour simple.
- All filter state is in the URL (`q, genre, composer, mood, era, energy, licence, rec, verified, score, sort, view,
  page, id`). `?id=<row id>` deep-links the detail drawer; Back closes it.

## Scaling thresholds
| rows | JSON (raw / gzip on Pages) | plan |
|---|---|---|
| ≤ 3,000 | ≤ ~7 MB / ~1 MB | current single file is fine |
| 3k–20k | too heavy for mobile first load | split: `data/index.json` (id, title, composer, catalog, genre, era, energy, moods, licence, has_*, top pick, search_text) + `data/detail/<shard>.json` loaded when the drawer opens |
| > 20k | | prebuilt inverted index (e.g. MiniSearch/Lunr JSON) or per-genre shards |
The sync script is the only place that needs to change; `app.js` reads `search_text` and the listed fields only.

## Player
One shared `Audio` element (`preload="none"`), so starting a clip stops the previous one. Mini player bar at the
bottom with seek. Keys: `Space` play/pause (current clip, or the first result), `Esc` closes the drawer then stops
playback, `/` focuses search. Space on a focused button keeps the native click.

## Known gaps / next
- `grieg_peer_gynt_morning_mood.flac` was not on Release `audio-v1` at 2026-10-09 17:30 (upload hit a network
  error); its "Full recording" link 404s until `scripts/upload_release.sh` is re-run.
- No waveform / exact excerpt markers; `notable_excerpt` is free text.
- Composer browse chips list every composer; at 300+ composers switch that tab to an A–Z index.
