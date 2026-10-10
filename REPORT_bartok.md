# REPORT: Bartók US-PD-only import (CP-BARTOK1)

Brief: `BRIEF_bartok.md`. Worktree `/workspace/music/wt_bartok`, branch `bartok`. Nothing pushed.

## Approval and checklist

- `scripts/bulk/pdmx_composers_manual.json`: Béla Bartók added to `approved_us_pd_only` (prefix `bartok`, d. 1945).
- `scripts/bulk/catalogue_data.py`: `BARTOK` checklist (12 rows) and `COMPOSERS["bartok"]`.
- `scripts/bulk/import_depth_us_pd.py`: `bartok` name rule. Also `ORIGINAL_EASY`, so that "Ten Easy Pieces" is not dropped by the `\beasy\b` arrangement filter.
- `scripts/bulk/schema.py` already had Bartók in its tier table (tier 4, d. 1945). No change needed.

## First-publication years (checked 2026-10-11)

| Work | Pub. year, publisher | Source | Scope |
|---|---|---|---|
| 14 Bagatelles Op.6 (Sz.38) | 1909, Rozsnyai | IMSLP `14_Bagatelles,_Op.6` | in |
| Ten Easy Pieces Sz.39 | 1909, Rozsnyai | IMSLP `10_Easy_Pieces,_Sz.39` | in |
| For Children Sz.42 (original) | 1909–11, Rozsnyai | IMSLP `For_Children,_Sz.42` | in (1945 revision out) |
| Three Burlesques Sz.47 | 1912, Rózsavölgyi | IMSLP `Burlesques,_Sz.47` | in |
| Allegro barbaro Sz.49 | 1918, UE | IMSLP | in |
| Romanian Folk Dances Sz.56 | 1918, UE | IMSLP | in |
| Suite Op.14 Sz.62 | 1918, UE | IMSLP `Suite_for_Piano,_Op.14` | in |
| Sonatina Sz.55 | 1919, UE | IMSLP | in |
| 15 Hungarian Peasant Songs Sz.71 | 1920, UE | IMSLP | in |
| Piano Sonata Sz.80 | 1927, UE | IMSLP | in |
| Out of Doors Sz.81 | 1927, UE | IMSLP | in |
| Three Rondos on Slovak Folk Tunes Sz.84 | 1930, UE | IMSLP + Wikipedia ("later in 1930") | in (cut-off 1930) |

The brief's "1930?" for Sz.84 is confirmed as 1930, so it is in scope. All 12 are in scope. The IMSLP page for the Bagatelles was not reachable under the brief's title format; the `14_Bagatelles,_Op.6` page gave 1909. The Wikipedia pages gave no publication years.

## Import (`import_depth_us_pd.py --composer bartok`)

Harvest: 3 matches kept, 35 skipped as arranged, 37 unmatched. Sources: PDMX `no_license_conflict` (PD/CC0). No Mutopia or OpenScore Bartók rows.

**Imported (2 live rows, US-PD-only, `licence_status: flagged`)**

| id | Work | Notes |
|---|---|---|
| `bartok_sz_39_ten_easy_pieces` | Ten Easy Pieces, "An Evening at the Village" | One movement, 100 s, 1 track, PDMX 10 Easy Pieces Sz.39, PD. Title edited to say it is one movement. |
| `bartok_sz_56_romanian_folk_dances_piano` | Romanian Folk Dances, one dance | 29 s, 1 track, CC0. Title edited to say "one dance; set not complete". |

Score files: `files/scores/bartok_sz_39_ten_easy_pieces.mid` and `files/scores/bartok_sz_56_romanian_folk_dances_piano.mid`.

**Skipped**

- For Children (PDMX "For Children vol. 1 - no 3", 47 s, 10 tracks, CC0). The file was imported and then dropped. Its version cannot be told apart from the 1945 Boosey & Hawkes revision (not US-PD). The other For Children PDMX files are labelled "Revised and Arranged by the Composer, January 1945" and were skipped by the arrangement filter.
- 14 Bagatelles: 4 PDMX files, all `license_conflict = True`. None usable.
- Romanian Folk Dances "Bela Bártok-Stick Game" (PD, one dance): composer field `NA`, so the importer's composer check did not claim it. It is not imported. It could be added by hand after a human check.
- A "Round Dance" (CC0, title "17. ROUND DANCE B. Bartok") is ambiguous (For Children, unknown version). Not imported.
- Mikrokosmos Sz.107, 2 Romanian Dances Op.8a, and Hungarian Pictures Sz.97 are not in the brief's 12 works. Not imported.

## Checks

- `licence_audit.py`: 0 violations after the run. 142 bulk rows had no score file in this worktree. They exist in `/workspace/music/library/files/scores`, so I copied them in as untracked files (not committed). Before the copy, the audit reported 142 violations, all "score file missing", and the same 142 at HEAD.
- `build_catalog.py --check`: passes (9,787 items, matching HEAD data).
- `sync_site_data.py`: **not kept.** Run in this checkout, it rewrote 2,500 tracked data files, dropped `other_editions` from many items, and modified `library_other_editions.json`. Those changes are unrelated, so `data/` was reverted. The two new rows appear on the site only after a sync from a clean main checkout (`python3 scripts/sync_site_data.py`).
- `library_bulk.csv`: a full `build_bulk_layer.py` rebuild in this checkout also rewrote 188 unrelated rows (Schumann, Ravel, Handel). That was reverted with `git checkout`. The two Bartók rows were appended by hand (35 fields, header-checked).
- `catalogue_report.py`: `docs/catalogues/bartok.csv` written. Coverage 2 of 12 in-scope works = 16.7%. The other five catalogue CSVs were regenerated with unrelated changes and reverted.

## WANTED

`/workspace/music/library/files/imslp_incoming/bartok/WANTED.md` (the path named in the brief; it is outside this worktree). It lists each work with its Sz./Op., first publication and publisher, US status, and IMSLP URL. All 12 URLs returned HTTP 200 (checked with `curl -sI`). It says to take only editions published before 1931.

Still missing:

- Ten Easy Pieces: 9 of 10 movements.
- Romanian Folk Dances: the full set.
- For Children: the original 1909–11 edition.
- 14 Bagatelles: no clean file.
- Three Burlesques, Allegro barbaro, Sonatina, Suite Op.14, Out of Doors, Piano Sonata, 15 Hungarian Peasant Songs, Three Rondos: no clean PD/CC0/CC BY file in PDMX, Mutopia or OpenScore.

## Caveats and decisions for LaDoger

1. The For Children PDMX file was dropped. If LaDoger knows it is the original 1909–11 print, it can be restored.
2. The two imported rows are partial (one movement, one dance). The titles say so. They are auditions for a full pick, not complete pieces.
3. The data layer needs a sync on a clean main checkout before the two rows appear on the site.
4. Files written outside this worktree: `WANTED.md` (in `/workspace/music/library/files/imslp_incoming/bartok/`, as the brief asked) and 142 copied score files in this worktree (not committed).
