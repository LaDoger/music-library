# Satie Sarabandes, Debussy Images I and Épigraphes: source re-check — 2026-10-27

Read-only follow-up to the 2026-10-22, 2026-10-24, 2026-10-25 and 2026-10-26 leads. Result: no cleared complete editable set, zero imports.

# Épigraphes (rank-1 OMR lead), read-only

- The correction log for this job was last written on 2026-10-23 and has not changed since. Its final verdicts are: pieces 1–4 and 6 PASS (piece 1 has an earlier FAIL that a later PASS line supersedes), **piece 5 FAIL** (bar 26 internal timing uncertain, rhythm estimate 96, pitch estimate 92).
- The job's `corrected/` folder holds only an empty `.finished3` processing marker. Its `REPORT.md`, `VERDICTS.txt` and `RESUME.md` are absent, so the verdicts above exist only in the log.
- Gate unchanged: not all six pieces are PASS. Nothing was launched, converted, imported or changed. Six MusicXML/MIDI pairs surviving on disk do not clear the set.

# Satie: Three Sarabandes (rank-1 complete piano set), normal fetch

- [IMSLP work page](https://imslp.org/wiki/3_Sarabandes_(Satie,_Erik)) fetched once on 2026-10-27 (HTTP 200). Unchanged: complete original piano score #08097, 10 pages, Paris: Rouart, Lerolle & Cie., 1911, tagged Public Domain. Source Files (0), Synthesized/MIDI (0). The arrangement entries cover No. 2 only (a Bagheri brass-quintet arrangement and a Morel album copy), so they do not complete the piano set.
- [Free-scores item 52977](https://www.free-scores.com/download-sheet-music.php?pdf=52977) fetched once on 2026-10-27 (HTTP 200): still an anti-bot "Verifying you are human" interstitial. Not retried, no challenge handled, no PDF downloaded.
- The complete piano PDF is still not obtained through a normal route. No editable source exists on the pages checked.

# Debussy Images I, #11443 (CC BY 3.0 Sibelius engraving), normal fetch

- [IMSLP work page](https://imslp.org/wiki/Images,_1re_s%C3%A9rie,_CD_105_(Debussy,_Claude)) fetched once on 2026-10-27 (HTTP 200). Dtromp's engraving files #11443 (Sibelius, "SIB", 0.73 MB, page count not stated) are tagged **Creative Commons Attribution 3.0**. Dtromp's complete PDF is #357447 (CC BY 3.0, 23 pp) and the Ray Alston complete PDF #512300 is CC0 but PDF only.
- The IMSLP file download is human-gated. No download was attempted, no challenge bypass, and no file was fetched.
- Still needed: a human download of #11443, conversion of all three pieces, and a comparison against the source before any import. Licence not inferred from the composition.

# Validation (isolated worktree, 2026-10-27)

- Bulk gate: `build_bulk_layer.py` and its `--check` mode ran on a temporary snapshot of the committed `library_bulk.csv` (5,590 rows, 0 duplicates dropped). Snapshot removed afterwards. Ignored batch inputs are absent; the generated dedupe files were rewritten by the check run but are ignored and not tracked.
- Final write rebuild used the same snapshot; committed alternate-edition provenance was restored before the final sync.
- Site data: `sync_site_data.py` ran; no tracked file changed. `build_catalog.py --check`: 5,925 items.
- Licence audit: 5,590 bulk rows audited, 0 violations.
- Pages UI check (existing `playwright` reused, no install): pass, 11,850-row fixture.
- Player check: pass, including live MIDI.
- Brand and secret scan of the new documents: pass (no internal names, keys or tokens found).

# Next steps

1. Obtain the complete PD Sarabandes piano scan through a normal route (manual download or a different source); record URL, hash and page count, then convert and verify all three pieces.
2. Épigraphes: resolve piece 5 (bar 26) and obtain an all-PASS verdict for all six pieces, with the REPORT/VERDICTS files restored, before any import.
3. Images I: a human fetch of Sibelius #11443, then conversion and a three-piece review. Import only when each set's licence and complete-set gates pass.
