# Satie: Three Sarabandes — 2026-10-26

Follow-up to the 2026-10-25 lead. Result: still no cleared complete editable set, zero imports.

- [free-scores item 52977](https://www.free-scores.com/download-sheet-music.php?pdf=52977): the page answered HTTP 200 but served an anti-bot verification interstitial ("Verifying you are human") instead of the score. The challenge was not bypassed and no PDF was downloaded. Nothing was saved, so there is no file hash and no page count.
- IMSLP (complete original piano score, 1911, public domain, no editable file) is unchanged from 2026-10-25.
- Still needed: a complete piano scan obtained by a normal route (a manual download or a different source), then conversion of all three pieces and an all-PASS comparison before any import.

# Debussy Épigraphes (rank-1 OMR lead), read-only

- The latest correction log for this job was last written 2026-10-23. It keeps piece 5 at FAIL (bar 26). Pieces 1–4 and 6 PASS in the earlier records. The job folder holds completion markers only; the REPORT and VERDICTS files it cites are not present.
- Gate unchanged: not all six pieces PASS, so nothing was launched or imported.
- The active correction job for another Debussy set was not touched.

# Validation (isolated worktree, 2026-10-26)

- Bulk gate: `build_bulk_layer.py --check` used a temporary snapshot of the committed bulk CSV (5,590 rows, 0 duplicates dropped). Full write run: same counts. `library_bulk.csv` unchanged.
- Sync and catalogue: `sync_site_data.py` and `build_catalog.py --check` pass (5,925 items).
- Licence audit: 5,590 bulk rows audited, 0 violations.
- Pages UI check: pass (11,850-row fixture).
- Player check: pass, including live MIDI.
- New public documents: brand and secret scans pass. Existing composer names and technical documentation were left unchanged.

# Next steps

1. Obtain a complete public-domain Sarabandes piano scan through a normal route (manual download or a different source) and record its URL, hash and page count.
2. Epigraphes: resolve piece 5 (bar 26) and obtain an all-PASS verdict for all six pieces before any import.
3. Import each set only after its own source, licence and complete-set quality gates pass.
