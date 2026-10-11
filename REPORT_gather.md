# Gather reports (US-PD-only composers, LaDoger priority list)

## CP-GATHER-falla: Manuel de Falla (d. 1946), 2026-10-11

- **Approved:** `manuel de falla` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". Scope: works published 1930 or earlier only.
- **Checklist:** `FALLA` in `scripts/bulk/catalogue_data.py`, 18 rows. First-publication years from IMSLP work pages (Wikipedia / a Greek archive where IMSLP had no page).
  - In scope (≤1930, 13): Noches en los jardines de España (1922), El amor brujo (1921), El sombrero de tres picos ballet (1921) and Suites No.1 (1921) and No.2 (1921), La vida breve (1913), Siete canciones (1922), Fantasía bética (1922), El retablo de maese Pedro (1924), Harpsichord Concerto (1928), Cuatro piezas españolas (1909), Psyché (1927), 3 Mélodies (1910), Serenata andaluza (ca.1902), Nocturno (ca.1902).
  - Excluded post-1930 (4): Soneto a Córdoba (1932 or 1956), Balada de Mallorca (1975), Homenaje / Le tombeau de Paul Dukas (1935), Atlántida (1962).
  - Unverified, not imported (2): Fanfare pour une fête, El gran teatro del mundo.
  - Note: the in-scope Serenata andaluza and Nocturno carry "ca.1902" dates; both are before 1931 under any source.
- **Imported (5 PDMX rows, all cc-zero, no_license_conflict, US-PD-only):**
  - `falla_siete_canciones_polo_manuel_de_falla` (1922)
  - `falla_siete_canciones_jota_manuel_de_falla` (1922)
  - `falla_siete_canciones_nana_berceuse_de_manuel_de_falla` (1922)
  - `falla_siete_canciones_seguidilla_murciana_manuel_de_fa` (1922)
  - `falla_3_melodies_2_chinoiserie_de_falla` (1910; "Chinoiserie" confirmed as song 2 of 3 Mélodies on IMSLP)
- **Skipped:** 13 in-scope works with no clean PD/CC0 file in PDMX, Mutopia or OpenScore. Arrangements 0. Mutopia and OpenScore had no Falla rows.
- **Importer:** `scripts/bulk/import_depth_us_pd.py` gained the `falla` name rule (`\bfalla\b`), and the Siete canciones / Cuatro piezas / 3 Melodies checklist rows are treated as multi-piece sets. Output now merges into `parts/BULK_batchP7_rows.csv` instead of overwriting other composers' rows.
- **Checks:** `licence_audit.py`: 0 violations (9460 bulk rows). `build_catalog.py --check`: pass.
- **Data layer:** `sync_site_data.py` rewrote 2,356 unrelated tracked data files in this checkout, so `data/` was restored; the 5 rows reach the site after a sync in a clean main checkout.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/falla/WANTED.md`, 18 entries (3 Siete songs, 2 Mélodies, 13 works without a clean file). IMSLP URLs checked with curl (HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-granados: Enrique Granados (d. 1916), 2026-10-11

- **Scope:** fully PD (died 1916), so there is no US-PD-only approval and no publication-year gate. `licence_class` clean, no `licence_scope`. Publication years are kept in `publication_year` for the record.
- **Checklist:** `GRANADOS` in `scripts/bulk/catalogue_data.py`, 28 rows (LaDoger priority first: Goyescas, 12 Danzas, Escenas romanticas, Valses poeticos).
  - In scope with IMSLP years (22): Goyescas (1912), 12 Danzas (1892), Valses poeticos (1900), Escenas romanticas Op.10 (ca.1906), Escenas poeticas (1912), Allegro de concierto Op.46 (ca.1905), Capricho espanol Op.39 (ca.1915), Valse de concert Op.35 (1914), Paisaje Op.35 (ca.1913), Carezza Op.38 (ca.1891), A la cubana Op.36 (1914), Dante Op.21 (1915), Piano Quintet Op.49 (1973 first publication), Madrigal (1945?), 12 Tonadillas (ca.1915), Canciones amatorias (1915-16), Bocetos (1918), El jardi d'Elisenda (1913), Paises sonados (1918), Elegia eterna (1916), Cuentos de la juventud Op.1 (1910), 6 Pieces on Spanish Folksongs (ca.1900).
  - Unverified, not imported (6): Moresque y cancion arabe, Playera, Rapsodia aragonesa, El pelele, Marchas militares / Marche militaire Op.38, Maria del Carmen (zarzuela).
  - Not in the checklist: the opera Goyescas (Schirmer 1915 vocal score) and the 2 Danzas Op.37 as a separate item (covered by the 12 Danzas row).
- **Imported (2 PDMX rows, CC0, no_license_conflict, pub 1900):** `granados_valses_8_poetic_waltzes_coda`, `granados_valses_8_poetic_waltzes_7`.
- **Skipped:**
  - `8 Poetic Waltzes 5`: already live as `granados_s5_8_poetic_waltzes_5`.
  - PDMX "Spanish dance no 2 oriental": classical-guitar transcription (tag `classicalguitar`), counted as an arrangement.
  - Mutopia "Danzas Espanolas No. 2, Oriental": CC BY-SA, not usable.
  - The other 20 in-scope works: no clean PD/CC0 file in PDMX, Mutopia or OpenScore. Arrangements 0 otherwise.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):**
  - `granados` name rule (`enrique granados` / `granados enrique`; `J.A. Granados`, `Sean Granados` and `Lizbeth Granados-Aparicio` do not match).
  - Fully PD composers (death <= 1929) pass the gate and get `licence_class clean` and no `licence_scope`.
  - Sets: Goyescas, Danzas, Valses.
  - PDMX rows with the `classicalguitar` tag are skipped as arrangements.
  - Rows already live (same composer and normalised title) are skipped, because catalogue labels differ between sources.
- **Live rows that need a decision (found while gathering, not changed here):** in `library_bulk.csv` from an earlier batch, all credited to "Enrique Granados":
  - `granados_composition_1` and `granados_composition_1_finishedb51`: PDMX composer is Lizbeth Granados-Aparicio, so the attribution is wrong.
  - `granados_heart_and_soul_remix`: PDMX credits Sean Granados (arranger), so the attribution is wrong.
  - `granados_himno_atletico_de_madrid`: by J.A. Granados & A. Currás, so the attribution is wrong.
  - `granados_granados_enrique_spanish_dan`: a classical-guitar transcription (arrangement) under the composer's name.
  - Suggested: remove or re-attribute these four or five rows. This needs LaDoger's decision, because the rows are in another agent's batch.
- **Checks:** `licence_audit.py`: 0 violations (9462 bulk rows). `build_catalog.py --check`: pass.
- **Data layer:** not regenerated in this checkout (as for falla); the 2 rows reach the site after a sync in a clean main checkout.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/granados/WANTED.md`. 21 checklist works still wanted (Valses counted as covered), plus the 6 unverified rows and the 2 Danzas Op.37 entries listed for completeness. IMSLP URLs checked with curl (HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-prokofiev: Sergei Prokofiev (d. 1953), 2026-10-11

- **Approved:** `sergei prokofiev` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". Scope: works first published 1930 or earlier only.
- **Exclusion lifted for this composer only** (it was excluded in four places; the other excluded composers are unchanged):
  - `scripts/bulk/schema.py`: removed from `EXCLUDED_CANONS`; `_RAW` tier 9 -> 4 (as Bartók).
  - `scripts/bulk/build_bulk_layer.py`: removed from `EXCLUDED`.
  - `scripts/bulk/licence_audit.py`: removed from the excluded-composer set (the checklist-match check still applies).
  - `AGENTS.md` and `SCHEMA.md`: the excluded list now says Prokofiev is excluded except the approved pre-1931 works.
- **Checklist:** `PROKOFIEV` in `scripts/bulk/catalogue_data.py`, 50 rows: 24 in scope (IMSLP "First Publication" field, 1930 or earlier), 4 unverified, 22 excluded (1931 or later). Piano Sonatas 6-8, Peter and the Wolf, Lieutenant Kijé, Romeo and Juliet, Cinderella, Symphonies 3 and 5 and the post-1930 concertos are excluded.
- **Imported (3 PDMX rows, CC0, `no_license_conflict`, `licence_scope` US-PD-only, `licence_class` flagged):**
  - `prokofiev_op_22_ridicolosamente`: Visions fugitives Op.22, first published 1917.
  - `prokofiev_op_33_march_from_the_love_of_three_oranges`: Love for Three Oranges, first published 1922.
  - `prokofiev_op_25_gavotta`: Symphony No. 1 Op.25 (Classical), III. Gavotta only, first published 1921 (piano reduction; full score 1925). The importer first gave it the symphony's title and id; I renamed it by hand to the movement title and id (the file is only the movement).
- **Skipped:**
  - 4 arrangements (`arr.` in the PDMX name or title; the importer counted 4): among them Lieutenant Kijé III (arr. Lai), Dance of the Knight (arr. Schonauer), Peter and the Wolf mixed quintet.
  - Post-1930 matches (excluded): Romeo and Juliet ("Montagues", "Dance of the Knights, suite 2 version"), Piano Sonata No. 7 (WIP movement), Lieutenant Kijé snare excerpt.
  - Unmatched: "Mnogaia leta" (not on the checklist).
  - PDMX rows with `license_conflict` (e.g. Troika, Tarentelle, a second Gavotta) were not used.
  - Mutopia and OpenScore: no Prokofiev rows in `parts/bulk_raw/`.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `prokofiev` name rule (`prokof`); Visions fugitives and Love for Three Oranges added to `SETS` (keep file titles). `SETS` is a global list keyed by catalogue label, so the new labels `Op.2`, `Op.17`, `Op.22`, `Op.31`, `Op.35` and `Op.33 / Op.33bis` also apply to any other composer with that label (title selection only, no matching change).
- **library_bulk.csv:** 3 rows appended by column name. I did **not** use `build_bulk_layer.py` to write it: in this worktree the batch files other than `BULK_batchP7_rows.csv` are absent, so the rebuild wrote 11 rows and dropped 9,489 (restored with `git checkout`). The built header also lacks the tracked `score_method` column, so the rows were written by name. Maintainers with the full batch set should rebuild and confirm the result.
- **Checks:** `licence_audit.py`: 0 violations (9465 bulk rows). `build_catalog.py --check`: passes (9799 items). `sync_site_data.py` rewrote 2,356 tracked data files again (as in the Falla run): restored with `git checkout -- data/`. The three new `data/items/prokofiev_*.json` files are untracked, like the other gather rows.
- **Decisions for LaDoger:**
  - Divertissement Op.43 (first published 1930) is in scope under the brief's "1930 or earlier" rule. It is at the cut-off.
  - Symphony No. 1 has a "?" in IMSLP's first-publication field (piano reduction, 1921-22 or later). It is in scope on the 1925 full score at the latest.
  - Piano Sonata No. 5 (1923 / 1952-53), Symphony No. 4 (1930 / 1947), Seven They Are Seven (1922 / 1933) and Chout (no publication date found) are unverified and not imported.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/prokofiev/WANTED.md`. 22 in-scope works in the table (Symphony No. 1 partly imported), plus the rest of Visions fugitives and the Love for Three Oranges suite; 4 unverified; 23 post-1930 excluded (22 in the checklist plus Sinfonietta Op.5/48, not in the checklist). All 46 IMSLP work-page URLs checked with curl (HTTP 200).
- **Models:** Haiku 5.5.

## Carl Nielsen (CP-GATHER-nielsen, 2026-10-11)

- **Approval (US-PD-only, not fully PD).** The brief said "PD everywhere", but Nielsen died 3 Oct 1931. Works published 1931 or later are still in copyright in the US, so the composer is approved as US-PD-only, the same as Prokofiev and Falla. Only works first published 1930 or earlier are in scope. Added to `approved_us_pd_only` with the note "LaDoger priority list 2026-10-11". EU / life+70 PD is not the test here. **Please confirm this reading with LaDoger.**
- **Checklist:** `NIELSEN` in `scripts/bulk/catalogue_data.py`, 22 rows. In scope with an IMSLP / Wikipedia year: Symphonies 1-5, Helios, Maskarade overture, Pan og Syrinx, Violin Concerto, Chaconne, Wind Quintet, String Quartet No. 1, Fantasy Pieces Op. 2. Unverified: Op. 40, 45, 59, 39, 35, 42, 34 (no first-publication year found). Excluded: Clarinet Concerto (1931), Flute Concerto CNW 42 (1952), Commotio (composed 1930-31), Symphony No. 6 (unpublished).
- **Imported (3 rows, licence_scope US-PD-only, licence_class flagged):**
  - `nielsen_op_13_string_quartet_no_1_op_13`: OpenScore StringQuartets, CC0; pub. 1902 (IMSLP). Other sources give 1900, still in scope.
  - `nielsen_op_43_wind_quintet`: PDMX, CC0, `no_license_conflict`; the full quintet from the PDMX row credited to "Karl Nielsen" (the importer now also matches that spelling). Pub. 1923 (Wikipedia; the premiere was 1922, so in scope either way).
  - `nielsen_op_2_two_fantasy_pieces_for_oboe_and_piano_roman`: PDMX, CC0; the Romance only (the second of the two pieces). Pub. 1891. Retitled by hand to "Fantasy Pieces for Oboe and Piano (Romance)".
- **Skipped:**
  - PDMX `Allegretto ben marcato from Nielsen's Wind Quintet` (a movement excerpt of the same work): dropped in favour of the full quintet (the import left only one row per checklist entry).
  - PDMX hymn settings (titles credited "Carl Nielsen (FS83/n)", e.g. "Der er en Vej", "Dig vil jeg elske"): not on the checklist. These are hymn and song settings, not video cues, and their publication dates were not checked.
  - PDMX `license_conflict` rows (several FS 83 hymns and "Canto Serioso" CC0): not used.
  - "Jeg ved en lærkerede" and "Af Flamme blev du avlet" (Karl/Carl Nielsen, CC0 hymns): not on the checklist.
  - Mutopia: no Nielsen rows in `parts/bulk_raw/`.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `nielsen` name rule `\bcarl nielsen\b|\bnielsen carl\b|\bkarl nielsen\b`.
- **Checks:** `licence_audit.py` 0 violations; `build_catalog.py --check` passes. `sync_site_data.py` rewrote tracked data files (the uncommitted `library_other_editions.json` feeds into them); restored with `git checkout -- data/`. The three `data/items/nielsen_*.json` are untracked, like the other gather rows.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/nielsen/WANTED.md`: 10 in-scope works (Symphonies 1-5, Helios, Maskarade overture, Pan og Syrinx, Violin Concerto, Chaconne), 9 unverified, 4 excluded. All IMSLP URLs curl-checked (HTTP 200).
- **Models:** Haiku 5.5.
