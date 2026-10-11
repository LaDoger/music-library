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

## Leoš Janáček (d. 1928) — gather, 2026-10-11 (CP-GATHER-janacek)

- **Rights:** died 1928, so PD in life+70 countries. Janáček is not on `approved_us_pd_only` and needs no approval. The brief said "PD everywhere", but US copyright still runs on works first published 1931 or later, so those are excluded from the checklist (see below). 1930 publications are PD in the US from 2026.
- **Checklist:** `JANACEK` in `scripts/bulk/catalogue_data.py` (21 rows: 16 in scope, 2 unverified, 4 excluded post-1930). Publication years from IMSLP work categories and "First edition" fields, fetched 2026-10-11. Importer: `import_depth_us_pd.py` `janacek` name rule (`\bjana\w{0,3}ek\b|\bleos janacek\b`, which also matches the mojibake credits in the live rows).
- **Imported:** none. The PDMX/OpenScore pool holds 3 candidates, and all are already live:
  - String Quartet No. 1 "Kreutzer Sonata" (OpenScore, CC0): `janacek_string_quartet_no_1_kreutzer`, already live.
  - Sinfonietta Fanfare (PDMX, CC0, two files `mid/12/49/QmUVZ…` and `mid/13/7/QmV8y…`): both already in `library_bulk.csv`.
- **Skipped / flagged:**
  - `janacek_string_quartet_no_2_intimate` (live, OpenScore CC0): IMSLP work category **1938** (composed 1928). US copyright still runs on it. It is clean in the EU and most life+70 countries, but this row is not PD in the US. **Not changed here; LaDoger to decide** (keep with a US note, or drop).
  - Duplicate live rows: `janacek_fanfare_from_janaaek_s_sinfo` and `janacek_janaaek_fanfare_from_sinfoni` are the same PDMX Fanfare (both titles carry mojibake, "JanáÄek"). Left as they are; one should be removed in a library data pass.
  - Post-1930 excluded: Capriccio (1953), Romance for violin (1938), Presto for cello (1970).
  - Unverified: *Zápisník zmizelého* (IMSLP category 1921, only print Hudební Matice 1945) and *Po zarostlém chodníčku* (category 1911, only print Hudební Matice 1942). Their first publication is not confirmed, so they are not imported.
- **Checks:** `licence_audit.py`: 0 violations (9468 bulk rows). `build_catalog.py --check`: passes (9787 items). `sync_site_data.py` not run, because no library rows changed.
- **Coverage:** `docs/catalogues/janacek.csv`: 2 of 16 in-scope entries covered (12.5%).
- **WANTED:** `/workspace/music/library/files/imslp_incoming/janacek/WANTED.md`: 15 in-scope works still wanted, 2 unverified, 4 excluded. All IMSLP URLs curl-checked (HTTP 200).
- **Models:** Haiku 5.5.

## Igor Stravinsky (CP-GATHER-stravinsky, 2026-10-11)

- **Approval (US-PD-only, not fully PD).** Stravinsky died 1971, so the composer is approved as US-PD-only, the same as Prokofiev and Nielsen. Only works first published 1930 or earlier are in scope. Added to `approved_us_pd_only` with the note "LaDoger priority list 2026-10-11". AGENTS.md and SCHEMA.md now say Stravinsky is excluded except for those works.
- **Death ceiling.** The US-PD-only window was 1930-1955 in four places (`schema.py` loader and composition status, `build_bulk_layer.py`, `licence_audit.py`). A 1971 death fell outside it, so `schema.py` now has `US_PD_ONLY_MAX_DEATH = {"igor stravinsky": 1971}`, with the default 1955 for everyone else. No other composer's gate changed.
- **Checklist:** `STRAVINSKY` in `scripts/bulk/catalogue_data.py`, 52 rows: 29 in scope (IMSLP "first published" year, all verified from the work pages), 4 unverified (Suite No. 2, Four Études for Orchestra, Three Pieces for String Quartet: no year on IMSLP; plus the Firebird 1919 suite, a later revision, kept as a row so title matches do not fall through to the 1910 ballet), 19 post-1930 excluded (for example Symphony of Psalms and Violin Concerto, both 1931). The brief asked for about 15-25 works; the list is longer because the post-1930 rows let the audit flag a match. Checklist size is the only deviation.
- **Revisions excluded by rule:** Firebird 1919 and 1945 suites, Petrushka 1947, Symphonies of Wind Instruments 1947. The importer matches by title, so a PDMX file titled only "Firebird Suite" would land on the 1910/1911 row. Check the publication before using any such file.
- **Imported: 0 rows.** PDMX has no Stravinsky `composer_name` (0 hits, any licence). Mutopia and OpenScore raw CSVs have no Stravinsky rows. `import_depth_us_pd.py --dry-run --composer stravinsky` harvested 0 candidates.
- **Checks:** `licence_audit.py`: 0 violations (9468 bulk rows). `docs/catalogues/stravinsky.csv` written (0 of 29 covered). `catalogue_report.py` also rewrote five other composers' CSVs without content changes from this gather; restored with `git checkout`.
- **Not done:** `sync_site_data.py` and `build_catalog.py --check` were not run, because no library rows changed. `library_other_editions.json` was already modified in the worktree before this run and is not part of this commit.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/stravinsky/WANTED.md`: 29 in-scope works, 3 unverified, 20 excluded listed for reference. IMSLP URLs curl-checked (HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-lyadov: Anatoly Lyadov (d. 1914), 2026-10-11

- **Scope:** fully PD (died 1914), so there is no US-PD-only approval and no publication-year gate. `licence_class` clean, no `licence_scope`. Publication years are kept in `publication_year` for the record. `AGENTS.md` and `pdmx_composers_manual.json` do not list Lyadov as excluded, so nothing changed there.
- **Checklist:** `LYADOV` in `scripts/bulk/catalogue_data.py`, 18 rows (LaDoger priority first: Musical Snuffbox Op.32, Biryulki Op.2, Barcarolle Op.44, the Preludes, then Baba Yaga, Kikimora, The Enchanted Lake).
  - In scope (7): Musical Snuffbox Op.32 (1897 earliest edition found, composed 1893; first printing not confirmed), Biryulki Op.2 (1876), Barcarolle Op.44 (1898 earliest edition found), Etude et 3 Preludes Op.40 (1897), 8 Russian Folksongs Op.58 (1906), The Enchanted Lake Op.62 (1909), Die Braut von Messina Op.28 (1891, Wikipedia only).
  - Unverified, not imported (11): 3 Morceaux Op.11 (composed 1885), Three Preludes Op.57, Baba Yaga Op.56, Kikimora Op.63, Mazurka Op.42, Variations Op.51, Polonaise Op.49, Village Scene Op.19, Dance of the Amazon Op.65, From the Apocalypse Op.66, Nénie Op.67.
  - Caveat: the Op.32, Op.44 and Op.40 years are the earliest dated editions found, not confirmed first printings. This does not block import (fully PD), but the years should be corrected if IMSLP shows otherwise.
- **Imported:** 0 new rows. PDMX has only two Lyadov files, both already live: `lyadov_op11no1_prelude_op_11_no_1_anatoly_l` and `lyadov_op40no3_anatoliy_lyadov_prelude_op_4` (both cc-zero, no_license_conflict).
- **Skipped:** nothing else. Mutopia and OpenScore raw pools have no Lyadov match.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `lyadov` name rule (`lyadov` / `liadov`); Op.40 and Op.58 added to `SETS` so each movement keeps its own title.
- **Checks:** `licence_audit.py`: 0 violations (9468 bulk rows). `build_catalog.py --check`: pass.
- **Not done:** `sync_site_data.py` not run (no rows added).
- **WANTED:** `/workspace/music/library/files/imslp_incoming/lyadov/WANTED.md`: 7 in-scope works still wanted, 11 unverified. The Braut von Messina IMSLP page was not found, and neither were the Op.42, Op.51, Op.57 and Op.66 pages.
- **Models:** Haiku 5.5.

## CP-GATHER-lyapunov: Sergei Lyapunov (d. 1924), 2026-10-11

- **Scope:** fully PD (died 1924), so there is no US-PD-only approval and no publication-year gate. `licence_class` clean, no `licence_scope`. `AGENTS.md` and `pdmx_composers_manual.json` do not list Lyapunov as excluded, so nothing changed there.
- **Checklist:** `LYAPUNOV` in `scripts/bulk/catalogue_data.py`, 22 rows (LaDoger priority first: Op.11 Etudes, Op.6 Preludes, then the Piano Sonata, then orchestral).
  - In scope (18): Op.11 (ca. 1906), Op.26 Chant d'automne (1906), Op.6 Preludes (1896), Op.27 Piano Sonata (1908), Op.40 (1910), Op.46 Barcarolle (1911), Op.23 (ca. 1905, uncertain), Op.58 (1914), Op.65 (1922), Op.49 (ca. 1912), Op.53 (1914), Op.63 (n.d. 1924, uncertain), Op.12 Symphony 1 (1902), Op.66 Symphony 2 (1958 Muzgiz edition), Op.4 Concerto 1 (1892), Op.38 Concerto 2 (1910), Op.28 Rhapsody (1908), Op.16 Polonaise (Wikipedia only).
  - Unverified, not imported (4): Op.57 (composed 1913, no first-publication year), Op.61 Violin Concerto (IMSLP lists only Muzgiz 1964), Op.7 (Wikipedia 1886 only), Op.2 Ballade (composed 1883 only).
  - Not on the checklist: Op.8 Nocturne (in PDMX, cc-zero, no year found), folksong sets (Op.10, Op.13), songs, organ.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `lyapunov` name rule widened to the PDMX spellings (`Liapounow`, `LiapounowOp.8`, which have no word boundary after the name); `Op.6` added to `SETS` so each prelude keeps its own title.
- **Imported: 5 new rows** (PDMX, cc-zero, no_license_conflict): `lyapunov_op_11_12_transcendental_etudes_op_11` (Berceuse), `lyapunov_op_6_prelude_s_liapounow_op_6_no_1`, `..._op_6_no_6`, `lyapunov_op_26_chant_d_automne_op_26`, `lyapunov_op_27_piano_sonata_in_f_minor_op_27`. Score MIDIs in `files/scores/`.
- **Appended to `library_bulk.csv`** by column name (5 lines; the batch file's extra columns left blank). `score_method` is the only column not in the batch file.
- **Did not use `build_bulk_layer.py` to write `library_bulk.csv`.** I ran it once; it rebuilt the file from `parts/BULK_batchP7_rows.csv` alone and dropped the other 9,474 rows. I restored `library_bulk.csv` from HEAD with `git checkout` before doing anything else, then appended the 5 rows directly. This worktree does not have the other batch files, so the script is unsafe to run here. Run it only in a checkout that has all `parts/BULK_batch*_rows.csv`.
- **Checks:** `licence_audit.py`: 0 violations (9473 bulk rows). `build_catalog.py --check`: pass (9787 items).
- **Sync:** `sync_site_data.py` ran, and the tracked `data/` files were restored with `git checkout -- data/`, as in the Nielsen run. The new `data/items/lyapunov_*.json` files are untracked and not committed.
- **Shared file:** `parts/BULK_batchP7_rows.csv` is shared by all composers in this worktree. My run kept the existing rows and added only Lyapunov rows.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/lyapunov/WANTED.md`: 14 in-scope works still wanted, plus the other 5 Op.6 Preludes and 11 Op.11 Etudes; 4 unverified. IMSLP URLs curl-checked (21 of 21 HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-arensky: Anton Arensky (d. 1906), 2026-10-11

- **Scope:** fully PD (died 1906), so there is no US-PD-only approval and no publication-year gate. `licence_class` would be `clean`, with no `licence_scope`. `AGENTS.md` and `pdmx_composers_manual.json` do not exclude Arensky, so nothing changed there. `schema.py` already lists him (tier 4, canon `anton arensky`).
- **Checklist:** `ARENSKY` in `scripts/bulk/catalogue_data.py`, 25 works, all in scope. LaDoger priority first: 24 Characteristic Pieces Op.36, Essais Op.28, the two-piano Suites Op.15, Op.23, Op.33 and Op.62, then Piano Trio No.1 Op.32 and Variations on a Theme of Tchaikovsky Op.35a, then the other piano sets, chamber, orchestral and concerto works. Years are from IMSLP "First Publication" / "n.d. [year]" fields; the Suite Op.15, Op.35a, Op.73, Op.7 and Op.2 years are marked uncertain.
- **Not on the checklist:** Op.4 Symphony No.1, Op.65 Children's Suite and Op.66 (four hands), Op.13, Op.8, Op.50a, songs and choral works.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `arensky` name rule (`\barensk`, which covers Arenskij and Arenski). Op.52 and Op.74 added to `SETS` (unique to Arensky). I did not add the piano-set catalogue numbers (Op.25, Op.28, Op.41, Op.43, Op.63, Op.67) because they are shared with other composers and `SETS` is global; a future import from those sets would get the set title, not its own movement title.
- **Imported: 0 rows.** The PDMX pool has 2 Arensky hits: the Lullaby, already live as `arensky_3_4_n_n_1_2_n_lullaby_n_1_2n`, and "Otche nash" Op.40 No.3, which has a licence conflict. Mutopia and OpenScore raw pools have no Arensky rows. The dry run harvested 0 rows.
- **Checks:** `licence_audit.py`: 0 violations (9473 bulk rows). `build_catalog.py --check`: pass (9787 items). `docs/catalogues/arensky.csv` written; the other composers' CSVs regenerated by `catalogue_report.py` were restored with `git checkout`.
- **Not run:** `sync_site_data.py` (no library rows changed); `library_bulk.csv` untouched.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/arensky/WANTED.md`: 25 in-scope works, all still wanted. IMSLP URLs curl-checked (25/25 HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-kalinnikov: Vasily Kalinnikov (d. 1901), 2026-10-11

- **Scope:** fully PD (died 1901), so there is no US-PD-only approval and no publication-year gate. `licence_class` would be `clean`, with no `licence_scope`. `AGENTS.md` and `pdmx_composers_manual.json` do not list Kalinnikov as excluded, so nothing changed there.
- **Checklist:** `KALINNIKOV` in `scripts/bulk/catalogue_data.py`, 17 rows plus the `kalinnikov` entry in `COMPOSERS` (the Tsar Boris regex covers "Zaar Boris"). Piano first (LaDoger priority), then Symphonies 1-2, then orchestral.
  - In scope (11; Symphony No.2 is covered by its four live movement rows, so 10 are still wanted): Chanson triste (1901), Nocturne in F sharp minor (1901), Elegie in B flat minor (1901), Symphony No.1 (1900), Symphony No.2 (1901), Suite for Orchestra (n.d. 1902), The Cedar and the Palm (n.d. 1901), Intermezzo No.1 (n.d. 1902), Intermezzo No.2 (n.d. 1902), Tsar Boris incidental music (n.d. 1902), In 1812 (1901, incomplete opera). Years are from IMSLP "First Publication" and "n.d. [year]" fields (Jurgenson plates).
  - Unverified, not imported (6): Russian Intermezzo (IMSLP shows only Muzgiz 1950 and Sobranie 1980), Waltz in A major (Sovyetsky Kompozitor 1960), Moderato in E flat minor (Muzgiz n.d. 1950; the IMSLP composition year 1980 is a typo), Serenade for Strings ("1950?" Muzgiz), Bylina (no IMSLP page found), Polonaise on a theme from Symphony No.1 for piano four hands (no IMSLP page found).
  - Not on the checklist: songs, the Romances collection, choral works, the Minuet in E major, the Overture in D minor, Nymphs, the Viktor Kalinnikov mixed choruses.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `kalinnikov` name rule (`kalinnikov`, `kalinnikoff`, `kalinnikow`, `kalinnikof`). No `SETS` change.
- **Imported: 0 new rows.** The PDMX pool has 8 Kalinnikov rows. The Symphony No.2 1st-movement candidate is byte-identical to the live `kalinnikov_vasili_kalinnikov_sinfonia_s` (same MIDI, md5 checked), so it was not imported; the other three movements are already live. Chanson triste and the three Tsar Boris rows have `no_license_conflict` False, so they fail the gate. The dry run harvested 1 row, and that row is the duplicate. No Mutopia or OpenScore rows.
- **Skipped (duplicate):** Symphony No.2 (1st mvt), already live as `kalinnikov_vasili_kalinnikov_sinfonia_s`.
- **Checks:** `licence_audit.py`: 0 violations (9473 bulk rows). `build_catalog.py --check`: pass (9787 items).
- **Not run:** `sync_site_data.py` (no library rows changed); `library_bulk.csv` and `data/` untouched; `build_bulk_layer.py` not run (it wipes `library_bulk.csv` in a worktree that lacks the other batch files). `docs/catalogues/kalinnikov.csv` not generated.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/kalinnikov/WANTED.md`: 10 in-scope works still wanted, plus 6 unverified. IMSLP URLs curl-checked (14 of 14 HTTP 200 after following redirects; Bylina and the Polonaise have no IMSLP page).
- **Models:** Haiku 5.5.

## CP-GATHER-taneyev: Sergei Taneyev (d. 1915), 2026-10-11

- **Scope:** fully PD (died 1915): no US-PD-only gate; `clean` if imported. LaDoger priority list 2026-10-11: Prelude and Fugue Op.29 for piano first, then the piano trio and quintet, the string quartets, then the Symphony No.4 and the Concert Suite Op.28.
- **Checklist:** `TANEYEV` in `scripts/bulk/catalogue_data.py`: 24 rows, 14 in scope (IMSLP first-publication years: Op.29 1914, Op.30 1911, Op.22 1908, Op.20 1904, Op.4 1892, Op.5 1896, Op.7 1898, Op.11 1900, Op.13 1903, Op.19 1906, Op.12 1901, Op.28 1910, Op.6 Oresteia vocal score 1900, Op.1 John of Damascus 1886), 10 unverified (Op.14, Op.16, Op.26, Symphony No.1 with IMSLP pages but no year; Op.31, Op.36, Op.27, Symphony No.3, Overture, Scherzo with no IMSLP page found).
- **Importer:** `import_depth_us_pd.py`: `taneyev` name rule (Latin PDMX spellings).
- **Imported:** 0 rows.
- **Skipped:** PDMX name hits. Two are Op.1 cantata movements (`publicdomain`, no_license_conflict True), but PDMX stores the composer as mojibake (`Ð. Ð. ÐÐÐ½ÐµÐµÐ²`), so the name rule does not match them. Fix: add a mojibake alternative to the name rule, then re-run the dry-run. One is a cc-zero anthology of four improvisations (Arensky, Rachmaninoff, Glazunov, Taneyev), not a Taneyev work. Mutopia and OpenScore have no Taneyev rows.
- **Checks:** dry-run harvests 0 (`--composer taneyev`). `library_bulk.csv`, `library.csv` and `data/` untouched; `sync_site_data.py` not run (no rows changed).
- **WANTED:** `/workspace/music/library/files/imslp_incoming/taneyev/WANTED.md`: 14 in-scope works still wanted, 10 unverified. IMSLP URLs curl-checked (HTTP 200 after redirects).
- **Models:** Haiku 5.5.

## CP-GATHER-blumenfeld: Felix Blumenfeld (d. 1931), 2026-10-11

- **Scope:** died 21 January 1931, so he falls in the 1930–1955 band and is US-PD-only, not fully PD. The brief said "PD everywhere". That holds for life+70 countries (PD since 2002) but not for the US. Works first published 1930 or earlier only.
- **Approved:** `felix blumenfeld` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". AGENTS.md is unchanged (it does not list Falla or Taneyev either).
- **Checklist:** `BLUMENFELD` in `scripts/bulk/catalogue_data.py`, 27 rows, plus the `blumenfeld` entry in `COMPOSERS`. The Op.36 Etude for the left hand and the Op.17 24 Preludes come first (LaDoger priority).
  - In scope (20, first-publication years from IMSLP "First Publication" fields): Op.36 (1905), Op.17 (1892–94), Op.24 (1897), Op.25 (1898), Op.29 (1898), Op.48 (1916), Op.20 (1895), Op.21 (1895), Op.40 (1909), Op.41 (1910), Op.34 (1903), Op.8 (1888), Op.39 Symphony (1909), Op.32 (1902), Op.31 No.2 (1901), Op.26 String Quartet (1898), Op.52 (1926), Op.33 (1902), Op.38 (1906), Op.22 (1896).
  - Unverified, not imported (7): Op.12, Op.3, Op.44, Op.54, Op.7, Op.23, Op.46. IMSLP work pages have a composition year but no First Publication field.
  - Not on the checklist: songs, choral works, Op.19 cello pieces and the rest of the opus list.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `blumenfeld` name rule only. Op.25, Op.29, Op.21, Op.38, Op.40, Op.32 and Op.33 are not in `SETS`: those cat numbers are shared with other composers, and `SETS` is global. Multi-piece sets (Op.17, Op.25, Op.29) therefore get the checklist title rather than each file's own title, with the per-entry cap of 4 applied. Revisit if a set import needs movement titles.
- **Imported: 0 rows.** PDMX has 4 Blumenfeld hits: cc-zero, `no_license_conflict` True, all movements of the Suite Polonaise No.1 Op.23 (Berceuse, Mazurka, Krakowiak). Op.23 has no first-publication year, so the US gate cannot be checked and they are skipped. Mutopia and OpenScore have no Blumenfeld rows. The dry run harvested 0 (`--composer blumenfeld`: 1 arranged, 3 excluded-or-unverified).
- **Checks:** `licence_audit.py`: 0 violations (9473 bulk rows). `build_catalog.py --check`: pass (9787 items). `docs/catalogues/blumenfeld.csv` generated; the other composers' CSVs regenerated by `catalogue_report.py` were restored with `git checkout`.
- **Not run:** `sync_site_data.py` (no library rows changed); `library_bulk.csv` untouched.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/blumenfeld/WANTED.md`: 20 in-scope works still wanted (all "only editions published before 1931"), 7 unverified. 20 IMSLP URLs checked (HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-glazunov: Alexander Glazunov (d. 1936), 2026-10-11

- **Scope:** died 21 March 1936, so US-PD-only (1930–1955 band). Works first published 1930 or earlier only, US use only of editions published before 1931. PD in the EU since 2007, but not in the US for later publications. Brief said "PD in EU; US pre-1931 only": that is what this implements.
- **Approved:** `alexander glazunov` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". AGENTS.md is unchanged.
- **Checklist:** `GLAZUNOV` in `scripts/bulk/catalogue_data.py`, 32 rows, plus the `glazunov` entry in `COMPOSERS`. Years are IMSLP first-publication fields or "Works first published in" categories (checked 2026-10-11). Piano first (Op.101 1925, Op.62 1899, Op.93 1913, Op.98 1916, Op.85 1911, Op.25 1890, Op.31 1892, Op.72 1901, Op.74 1901, Op.75 1902, Op.37, Op.36, Op.42, Op.49, Op.54, Op.15), then The Seasons Op.67 (1901), Raymonda Op.57 (1898) and Suite Op.57a (1898), Violin Concerto Op.82 (1905), then Piano Concerto No.1 Op.92 (1912), Symphonies 1, 5, 6, 7, 8 (Op.5, 55, 58, 77, 83) and String Quartets 1, 4, 5 (Op.1 1887, Op.64 1899, Op.70 1900).
  - Unverified, not imported (2): Piano Concerto No.2 Op.100 (IMSLP shows 1922 with a query mark) and Theme and Variations for String Orchestra Op.97 (no First Publication field; composition year 1895 only).
  - Excluded post-1930 (2): String Quartet No.7 Op.107 (1931), Saxophone Concerto Op.109 (1936).
  - Not on the checklist: the rest of the opus list (songs, cantatas, Op.9, the concert waltzes, Op.106 quartet whose year is unclear, etc.).
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `glazunov` name rule (`\bglazun`, `\bglasun` and spellings; PDMX also credits "A. Glazunov"). `SETS` gains Op.101, Op.85, Op.49, Op.54 and Op.15 (multi-piece opus numbers, so each file keeps its own title). Op.25 is not added, since it is also Blumenfeld's multi-piece number.
- **Imported: 1 row.** OpenScore `openscore-quartets` (CC0): `glazunov_op_1_string_quartet_no_1_op_1` (String Quartet No.1 Op.1, 1887). It is `flagged` with scope `US-PD-only`. PDMX has one live Glazunov hit (Op.97, unverified, see above) plus a cc-zero anthology of four improvisations (Arensky, Rachmaninoff, Glazunov, Taneyev), which is not a Glazunov work. The import wrote `files/scores/glazunov_op_1_string_quartet_no_1_op_1.{mid,mxl}` (untracked, as for the other imports).
- **Not synced (important):** `build_bulk_layer.py` was run once in this worktree and it rebuilt `library_bulk.csv` from the P7 batch file alone (21 rows instead of about 9,500) and emptied `library_other_editions.json`. Both were restored to HEAD straight away; the row was then appended to `library_bulk.csv` by hand (one line, 35 columns, `score_method` blank). Do not run `build_bulk_layer.py` from a worktree that lacks the other batch files. `library_other_editions.json`: the session-start uncommitted edit in this worktree (title changes, "arr.") is gone and cannot be recovered from git; the main checkout `/workspace/music/library/library_other_editions.json` still carries a similar uncommitted version, so compare there if it matters. `sync_site_data.py` was run here to check the output, then `data/` was restored to its pre-run state. Running it from a worktree with HEAD inputs changes Elgar, Holst, Mahler, Satie and Wagner items, which is why it was not committed. The glazunov item it generates is `licence_status` `flagged`, `verified` `yes`, `licence_scope` `US-PD-only`, `publication_year` `1887`. A maintainer should run `sync_site_data.py` on a clean checkout to publish it.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items). `docs/catalogues/glazunov.csv` generated; the other composers' CSVs regenerated by `catalogue_report.py` restored with `git checkout`.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/glazunov/WANTED.md`: 28 in-scope works still wanted, 2 unverified; 30 IMSLP URLs curl-checked (HTTP 200 after redirects).
- **Models:** Haiku 5.5.

## CP-GATHER-medtner: Nikolai Medtner (d. 1951), 2026-10-11

- **Scope:** died 13 November 1951, so US-PD-only (1930–1955 band). Works first published 1930 or earlier only, and US use only of editions published before 1931. PD in the EU since 2022.
- **Approved:** `nikolai medtner` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". AGENTS.md does not list Medtner, so it is unchanged.
- **Exclusion change (needed for the approval to work):** Medtner was blocked by a named exclusion in code, not by AGENTS.md. `schema.py` `EXCLUDED_CANONS` and the tier-9 check in `composition_status` excluded him, and `build_bulk_layer.py` `EXCLUDED` dropped any row whose composer contains "medtner". I removed the name from both lists and lowered his tier from 9 to 6 (the tier generated composers get). The post-1930 gate still applies through `_us_pd_only_ok`. A maintainer should check that this is the intended reading of the earlier batch exclusion (STATUS CP-G1 said "Medtner excluded").
- **Checklist:** `MEDTNER` in `scripts/bulk/catalogue_data.py`, 28 rows. Years are IMSLP "First Publication" fields checked 2026-10-11, except where noted in the row. Piano first (Forgotten Melodies Op.38, 39, 40 (all 1922), Skazki Op.20 (1910), Op.26 (1913), Op.51 (1928), Op.42 (1924), Op.48 (1927 or earlier), Op.49 (1929), Sonata No.1 Op.5 (1904), Sonata-Skazka Op.25/1 (1911?), Night Wind Op.25/2 (1912), Sonata No.5 Op.22 (1911?), Sonata-Ballade Op.27 (1913), Sonata No.9 Op.30 (1917), Canzonas Op.43 (1924)), then Piano Concerto No.1 Op.33 (1921) and No.2 Op.50 (1928), then Nocturnes Op.16 (1910), Violin Sonata No.1 Op.21 (1911), Violin Sonata No.2 Op.44 (1928).
  - Unverified, not imported (1): Sonata-Triad Op.11 (no IMSLP page at the URLs tried, 404).
  - Excluded post-1930 (6): Sonata romantica Op.53 No.1 (1932), Sonata minacciosa Op.53 No.2 (1933), Sonata-Idyll Op.56 (composed 1935–37), Violin Sonata No.3 Op.57 (1939/40), Piano Concerto No.3 Op.60 (1951), Piano Quintet (completed 1949).
  - Not on the checklist: Op.34 and Op.35 (4 Tales each, composed 1916–17; no publication year checked), the songs.
  - Two dates are uncertain: Op.39 (IMSLP 1922, Wikipedia 1923; both in scope) and Op.22 and Op.25/1 (IMSLP "1911?"; both in scope).
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `medtner` name rule (PDMX "Medtner"). `SETS` gains Op.38, 40, 20, 26, 51. Op.25 is split into "Op.25 No.1" and "Op.25 No.2" (separate sonatas, not in SETS).
- **Imported: 0 rows.** The `--dry-run --composer medtner` harvest is 0 matches. The one PDMX hit is `Medtner Piano Concerto No. 1 (Excerpt) arr. for 2 pianos` (cc-zero, `no_license_conflict` True), skipped as an arrangement. Mutopia and OpenScore have no Medtner rows.
- **Not synced:** no rows changed, so `sync_site_data.py` was not run and `library_bulk.csv` and `data/` are untouched.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items). `docs/catalogues/medtner.csv` generated; the other composers' CSVs were regenerated by `catalogue_report.py`, the tracked ones restored with `git checkout`, and the untracked ones were rewritten from unchanged inputs.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/medtner/WANTED.md`: 21 in-scope works still wanted; 23 IMSLP URLs curl-checked (HTTP 200; Op.11 404s marked).
- **Models:** Haiku 5.5.

## CP-GATHER-rebikov: Vladimir Rebikov (d. 1920), 2026-10-11

- **Scope:** died 1 October 1920, so fully PD (no US-PD-only gate; `licence_status` `clean` if imported). Not in `approved_us_pd_only`, not excluded in AGENTS.md, and no name exclusion in code; `pdmx_composers_manual.json` and `schema.py` are unchanged.
- **Checklist:** `REBIKOV` in `scripts/bulk/catalogue_data.py`, 25 rows. In scope (14): Les Rêves Op.15 (IMSLP FP 1900, Jurgenson), Autumn Dreams Op.8 (1900, Grüninger, from the IMSLP list; the work page has no FP field), The Christmas Tree Op.21 (vocal opera score, [1902] bracketed on IMSLP), Op.2 (1896), Op.5 (1899), Op.7 for violin and piano (1899), Op.9 (1898), Op.10 (1898, Simrock), Op.11 (1898), Op.14 (1899), Op.24 (ca.1900), Op.48 (1913), Fleurs d'automne (1910), Children's Rest (1901). Unverified, not imported (11): Op.21a (orchestra), Op.13, 22, 23, 27, 28, 31 (Gos. 1929 edition only), 37, 38, 47, 49.
- **Sources:** IMSLP work pages and the IMSLP list of works by Rebikov (all 25 URLs curl-checked, HTTP 200). The en Wikipedia article carries an "LLM-generated text" notice, so its dates and opus numbers were not used on their own.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `rebikov` name rule (Rebikov, Rebikoff, Rebikow, Rebikof, Rebicov). `SETS` gains Op.15, 8, 2, 5, 7, 9, 10, 11, 14, 24, 48 and the two no-opus albums ("Fleurs", "Children's Rest").
- **Imported: 0 rows.** `--dry-run --composer rebikov` harvests 0. The PDMX CSV has no Rebikov name, Rebikoff/Rebikow spelling, Cyrillic form, or mojibake form; Mutopia and OpenScore have no Rebikov rows.
- **Not synced:** no rows changed, so `sync_site_data.py` was not run and `library_bulk.csv`, `library.csv` and `data/` are untouched.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items). `docs/catalogues/rebikov.csv` generated; the tracked CSVs regenerated by `catalogue_report.py` restored with `git checkout`.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/rebikov/WANTED.md`: 14 in-scope works still wanted, 11 unverified.
- **Models:** Haiku 5.5.

## CP-GATHER-grechaninov: Alexander Grechaninov (d. 1956), 2026-10-11

- **Approved:** `alexander grechaninov` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". Scope: works first published 1930 or earlier only.
- **Death-year ceiling:** he died 1956, one year past the default 1955 ceiling, so `US_PD_ONLY_MAX_DEATH` in `scripts/bulk/schema.py` now lists `"alexander grechaninov": 1956` (same mechanism as Stravinsky). Other 1930–1955 composers are unchanged. AGENTS.md's "Approved today" list was not edited, as for Glazunov, Medtner and Rebikov.
- **Checklist:** `GRECHANINOV` in `scripts/bulk/catalogue_data.py`, 40 rows. First-publication years from IMSLP work pages (`First Publication` field), checked 2026-10-11.
  - In scope (≤1930, 23): Livre d'enfants Op.98 (1924), Glass Beads Op.123 (1930), On the Green Meadow Op.99 (1926), The Day of the Child Op.109 (1927), 2 Sonatinas Op.110 (1927), Grandfather's Album Op.119 (1929), Historiettes Op.118 (1930), 5 Pastels Op.3 (1894), Pastelle No.2 Op.61 (1913 ca.), 4 Mazurkas Op.53 (1911), Pensées fugitives Op.115 (1928), 3 Pieces Op.116 (1928), 2 Pieces Op.37 (1905), String Quartet No.1 Op.2 (1894), No.2 Op.70 (1915), Piano Trio No.1 Op.38 (1907), Violin Sonata No.1 Op.87 (1923), In aller Frühe Op.126 (1921), Wish Op.9 (1895), Symphony No.1 Op.6 (1905 or earlier), Symphony No.2 Op.27 (1910), In modo antico Op.81 (1920), Liturgy No.1 Op.13 (1898).
  - Excluded post-1930 (8): Piano Sonata No.1 Op.129 (1931), Piano Sonata No.2 Op.174 (1947), Russian Folk Dances Op.130 (1931), Piano Trio No.2 Op.128 (composed 1931), Violin Sonata No.2 Op.137 (composed 1933), Clarinet Sonata No.2 Op.172 (1949), Symphony No.5 Op.153 (composed 1936), Violin Concerto Op.132 (composed 1932).
  - Unverified, not imported (9): Bagatelles Op.112 ("1928 ?" on IMSLP), Dobrynya Nikitich Op.22 (no First Publication field), String Quartets No.3 Op.75 and No.4 Op.124, Cello Sonata Op.113, Symphonies No.3 Op.100 and No.4 Op.102, Cello Concerto Op.8, All-Night Vigil Op.59. The last seven have no IMSLP work page at the obvious URL (404), so they were not confirmed.
  - Not in the checklist: the songs and most choral works (Op.13 is the only liturgy), Liturgia domestica Op.79 (IMSLP shows a US copyright-restoration notice, so it was left out), Passion Week Op.58 (IMSLP "1912 ?"), Liturgy No.2 Op.29 and The Seasons Op.46 (no First Publication field).
- **Imported:** none. The PDMX pool has two Grechaninov hits, "Promenade" (a saxophone-quartet arrangement) and "Nunc Dimittis Op. 34 No. 1" (not in the checklist, no verified year). Mutopia and OpenScore have no Grechaninov rows. `--dry-run --composer grechaninov` harvests 0.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: pass (9787 items).
- **Data layer:** nothing changed in `library.csv`, `library_bulk.csv` or `data/`, so `sync_site_data.py` was not run. The tracked CSVs (`elgar`, `holst`, `rachmaninoff`, `ravel`, `strauss_r`) regenerated by `catalogue_report.py` were restored with `git checkout`.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/grechaninov/WANTED.md`: 23 in-scope works still wanted, IMSLP URLs curl-checked (HTTP 200 for the 23 in scope plus Op.112 and Op.22; 404 for the other 7 unverified).
- **Models:** Haiku 5.5.

## Alexander Borodin (d. 1887), fully PD, 2026-10-11 (CP-GATHER-borodin)

- **Rights:** fully PD (died 1887). No US-PD-only approval needed and no gate; publication years are kept for the record. `borodin` is already in `schema.py` (tier 4) and was not excluded anywhere.
- **Checklist:** `BORODIN` in `scripts/bulk/catalogue_data.py`: 17 rows. 7 in scope (Petite Suite 1885, Scherzo in A-flat 1885, Symphony No.2 1878, Symphony No.1 1875, In the Steppes 1882, String Quartet No.1 1884, String Quartet No.2 1888). 9 unverified (no confirmed first-publication year). 1 excluded: the lost flute concerto.
- **Years:** from IMSLP "First Publication" fields (Petite Suite, Scherzo, Symphonies 1-2, String Quartets 1-2) and the Wikipedia work list (In the Steppes: composed 1880, published 1882; IMSLP field not read). Prince Igor and Polovtsian Dances: no first-publication year confirmed.
- **Importer:** `import_depth_us_pd.py` gets a `borodin` name rule (`\bborodin`). No SETS change: In the Steppes is a single work, so its title stays the checklist title and deduplicates against the live row.
- **Imported: 0 rows.** `--dry-run --composer borodin` harvests 3 matches, none new:
  - In the Steppes (PDMX cc-zero, clean): same work as live `borodin_steppes`, skipped as a duplicate.
  - String Quartet No.1 and No.2 (OpenScore): already live.
  - The PDMX Petite Suite 'Reverie' has `no_license_conflict` False: not clean, skipped.
  - The PDMX Notturno (sax quartet) and Blumenfeld's Polovtsian Dances: arrangements, skipped.
  - Mutopia has no Borodin rows.
- **Skipped (no clean file):** Petite Suite (other than the conflicted Reverie) and Scherzo in A-flat have no clean PD/CC0 file in any pool.
- **Checks:** `licence_audit.py` 0 violations (9474 bulk rows). `docs/catalogues/borodin.csv` generated; `catalogue_report.py` also rewrote five tracked CSVs (elgar, holst, rachmaninoff, ravel, strauss_r), restored with `git checkout`.
- **Data layer:** `library.csv`, `library_bulk.csv` and `data/` untouched; `sync_site_data.py` not run (no rows changed).
- **WANTED:** `files/imslp_incoming/borodin/WANTED.md`: 4 in-scope works still wanted (Petite Suite, Scherzo in A-flat, Symphonies 1-2), 9 unverified; 16 IMSLP URLs curl-checked (all HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-szymanowski: Karol Szymanowski (d. 1937), 2026-10-11

- **Approved:** `karol szymanowski` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". Scope: works first published 1930 or earlier only. Death year 1937 is inside the default band, so `US_PD_ONLY_MAX_DEATH` is unchanged.
- **Checklist:** `SZYMANOWSKI` in `scripts/bulk/catalogue_data.py`, 28 rows. First-publication years from IMSLP "First Publication" fields, checked 2026-10-11.
  - In scope (≤1930, 18): 9 Preludes Op.1 (1906), 4 Etudes Op.4 (1906), Piano Sonata No.1 Op.8 (1910), Variations Op.10 (1906 ca.), Fantasy Op.14 (1911), Piano Sonata No.2 Op.21 (1912), Nocturne and Tarantella Op.28 (1921), Metopes Op.29 (1922), Mythes Op.30 (1921), 12 Etudes Op.33 (1922), Masques Op.34 (1919), Piano Sonata No.3 Op.36 (1919), Violin Sonata Op.9 (1911), Violin Concerto No.1 Op.35 (1921/1923), String Quartet No.1 Op.37 (1925), Symphony No.3 Op.27 (1925), King Roger Op.46 (1925), Stabat Mater Op.53 (1928).
  - Unverified, not imported (4): Mazurkas Op.50 (IMSLP "1926–31", not a single year), Romance Op.23, Hagith Op.25 (no First Publication field), String Quartet No.2 Op.56.
  - Excluded post-1930 or unpublished (6): Symphony No.2 Op.19 (published 1954), Concert Overture Op.12 (1937), Symphony No.4 Op.60 (composed 1932), Harnasie Op.55 (1932 arrangement), Penthesilea Op.18 (published 1977), Piano Trio Op.16 (withdrawn).
  - Not in the checklist: the songs (Op.2/5/11/13/17/20/26/31/32/41/42/54/58), the Kurpian songs, the Violin Concerto No.2 Op.61, the Caprices Op.40 and the Mazurkas Op.62.
- **Imported:** none. The PDMX CSV has no Szymanowski rows (checked under Szymanowski, Szymanowsky and Szimanowski); Mutopia and OpenScore raw pools have none. `--dry-run --composer szymanowski` harvests 0.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items).
- **Data layer:** nothing changed in `library.csv`, `library_bulk.csv` or `data/`, so `sync_site_data.py` was not run. The tracked CSVs (`elgar`, `holst`, `rachmaninoff`, `ravel`, `strauss_r`) regenerated by `catalogue_report.py` were restored with `git checkout`.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/szymanowski/WANTED.md`: 18 in-scope works still wanted; 28 IMSLP URLs curl-checked (27 HTTP 200; Piano Trio Op.16 has no work page because it was withdrawn).
- **Models:** Haiku 5.5.

## CP-GATHER-busoni: Ferruccio Busoni (d. 1924), 2026-10-11

- **Scope:** fully PD (died 1924). No US-PD-only approval and no publication-year gate; `busoni` is not added to `approved_us_pd_only`. Any new rows would be `licence_class clean` with no `licence_scope`.
- **Checklist:** `BUSONI` in `scripts/bulk/catalogue_data.py`, 27 rows. Years from IMSLP work pages ("First Publication" field or the publisher line), checked 2026-10-11.
  - In scope (24): piano: Toccata BV 287 (1922), Fantasia contrappuntistica BV 256 (1912, "1912 and later"), Sonatina No.1 BV 257 (1910), Sonatina seconda BV 259 (1912), Sonatina ad usum infantis BV 268 (1916), Sonatina in diem nativitatis BV 274 (1918), Sonatina brevis BV 280 (1919), Sonatina No.6 Carmen BV 284 (1920), Indianisches Tagebuch I BV 267 (1916), Elegien BV 249 (1908-09), Fantasia nach J.S. Bach BV 253 (1909), Nuit de Noel BV 251 (1909), Prelude et etude en arpeges BV 297 (1923). Orchestral: Piano Concerto Op.39 BV 247 (1906), Violin Concerto Op.35a BV 243 (1899), Turandot Suite Op.41 BV 248 (1906), Berceuse elegiaque Op.42 BV 252a (1910), Lustspielouverture Op.38 BV 245 (1904), Rondo arlecchinesco Op.46 BV 266 (1917). Opera: Arlecchino Op.50 BV 270 (1917), Doktor Faust BV 303 (1926). Chamber: String Quartet No.1 Op.19 BV 208 (1886, uncertain), String Quartet No.2 Op.26 BV 225 (1889), Violin Sonata No.2 Op.36a BV 244 (1901).
  - Unverified, not imported (3): 24 Preludes Op.37 BV 181 (only a Ricordi n.d.(1927) scan; no First Publication year), Kleine Suite Op.23 BV 215 (n.d.), Turandot opera BV 273 (no First Publication field).
  - Not on the checklist (real works, left for LaDoger to decide): Die Brautwahl BV 258, Tanzwalzer Op.53, Sarabande und Cortege Op.51, Indianische Fantasie Op.44, Indianisches Tagebuch II Op.47, Nocturne symphonique Op.43, Concertino Op.48, Divertimento Op.52. Busoni's Bach transcriptions are arrangements and are not wanted.
- **Imported:** none. The PDMX CSV has one Busoni row (Schlechter Trost, cc-zero, no_license_conflict); it is already live as `busoni_schlechter_trost_f_busoni` and is not on the checklist. OpenScore String Quartets have the Nos.1 and 2 (CC0); both are already live as `busoni_op19_string_quartet_no_1_op_19_bv` and `busoni_op26_string_quartet_no_2_op_26_bv`. Mutopia has none. `--dry-run --composer busoni` harvests 2, both already live, so 0 new rows.
- **Skipped:** PDMX Schlechter Trost (not on the checklist; already live). The two OpenScore quartets (already live).
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items). `docs/catalogues/busoni.csv` generated (coverage 2 of 24 in scope, 8.3%).
- **Data layer:** `library.csv`, `library_bulk.csv` and `data/` untouched; `sync_site_data.py` not run (no rows changed).
- **Flagged, not changed:** `scripts/bulk/schema.py` line 86 has the canon key `feruccio busoni` (typo for Ferruccio), so the Busoni tier entry never matches `Ferruccio Busoni`. Fixing it changes tiers for existing Busoni rows, so it is left for a maintainer.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/busoni/WANTED.md`: 22 in-scope works still wanted, 3 unverified; 25 IMSLP URLs fetched (all HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-roussel: Albert Roussel (d. 1937), 2026-10-11

- **Approved:** `albert roussel` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". Scope: works first published 1930 or earlier only. Death year 1937 is inside the default band, so `US_PD_ONLY_MAX_DEATH` is unchanged. Roussel was not listed as excluded or flagged anywhere in the repo.
- **Checklist:** `ROUSSEL` in `scripts/bulk/catalogue_data.py`, 32 rows. First-publication years from IMSLP "First Publication" fields, checked 2026-10-11.
  - In scope (24): piano: Rustiques Op.5 (1906), Sonatine Op.16 (1912), Suite Op.14 (1910), Impromptu Op.21 (1919), Prelude et fughetta Op.41 (1930); chamber: Piano Trio Op.2 (1904), Violin Sonatas No.1 Op.11 (1909) and No.2 Op.28 (1925), Trio for flute, viola and cello Op.40 (1930), Serenade Op.30 (1926), Segovia Op.29 (1925), Divertissement Op.6 (1911), Flammes Op.10 (1910), Evocations Op.15 (1912); stage and orchestral: Le festin de l'araignee Op.17 (1913), Symphony No.1 Op.7 (1909), Symphony No.2 Op.23 (1923), Padmavati Op.18 (1919/1924), Pour une fete de printemps Op.22 (1921), Joueurs de flute Op.27 (1925), Suite in F Op.33 (1927), Concert pour petit orchestre Op.34 (1927), Piano Concerto Op.36 (1928), Petite suite Op.39 (1929).
  - Excluded, first published 1931–1935 (8): Symphony No.3 Op.42 (1931), Bacchus et Ariane Op.43 (1931), String Quartet Op.45 (1932), Prelude et fugue Op.46 (1932), 3 Pieces Op.49 (1934), Andante et scherzo Op.51 (1934), Sinfonietta Op.52 (1934), Symphony No.4 Op.53 (1935).
  - Not on the checklist: the songs (Op.1/3/8/19/20/26/50/55), the cantatas and operas beyond Padmavati, Aeneas Op.54, Elpenor Op.59, Rapsodie flamande Op.56, Cello Concertino Op.57, String Trio Op.58 and the Vocalise (all mid-1930s or later, not checked), and Le Marchand de sable Op.13 and Resurrection Op.4 (not checked).
- **Imported:** none. `--dry-run --composer roussel` harvests 0. The PDMX CSV has no Roussel rows: the 15 'rouss' hits are Rousseau, Carousel, Rousset and similar. Mutopia and OpenScore raw pools have none.
- **Importer:** `import_depth_us_pd.py` gained a `roussel` name rule (`\brouss[ea]l|\brousel`). Op.5 and Op.14 went into `SETS`. Note: the `SETS` block in HEAD has a misplaced comment (the Szymanowski note is attached to the Busoni line); left as it was.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items). `docs/catalogues/roussel.csv` generated (coverage 0 of 24 in scope). The six tracked CSVs regenerated by `catalogue_report.py` (busoni, elgar, holst, rachmaninoff, ravel, strauss_r) were restored with `git checkout`.
- **Data layer:** `library.csv`, `library_bulk.csv` and `data/` untouched; `sync_site_data.py` not run (no rows changed).
- **WANTED:** `/workspace/music/library/files/imslp_incoming/roussel/WANTED.md`: 24 in-scope works still wanted; 35 IMSLP URLs curl-checked (all HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-respighi: Ottorino Respighi (d. 1936), 2026-10-11

- **Approved:** `ottorino respighi` added to `approved_us_pd_only` (`scripts/bulk/pdmx_composers_manual.json`), note "LaDoger priority list 2026-10-11". Scope: works first published 1930 or earlier only. Death year 1936 is inside the default band, so `US_PD_ONLY_MAX_DEATH` is unchanged. Respighi was not listed as excluded or flagged anywhere in the repo.
- **Checklist:** `RESPIGHI` in `scripts/bulk/catalogue_data.py`, 32 rows. First-publication years from IMSLP "First Publication" fields, checked 2026-10-11; catalogue numbers from the Wikipedia list (Pedarra P. numbers).
  - In scope (22): orchestral: Fontane di Roma P.106 (1918), Pini di Roma P.141 (1925), Feste romane P.157 (1929), Vetrate di chiesa P.150 (1927), Trittico botticelliano P.151 (1928), Gli uccelli P.154 (1928), Antiche danze Suite No.1 P.109 (1920) and No.2 P.138 (1924), Ballata delle gnomidi P.124 (1920), Sinfonia drammatica P.102 (1922), Toccata P.156 (1929), Concerto in modo misolidio P.145 (1926), Concerto gregoriano P.135 (1922), Poema autunnale P.146 (1926); stage: Belfagor P.137 (1924), La campana sommersa P.152 (1927); chamber and piano: Violin Sonata P.110 (1919), Quartetto dorico P.144 (1925), Tre preludi P.131 (1922), Sei pezzi P.44 (1904-05), Deità silvane P.107 (1917), Il tramonto P.101 (1918).
  - Excluded, first published 1931 or later (7): Antiche danze Suite No.3 P.172 (1932), Belkis P.177 (suite 1935), Adagio con variazioni P.133 (1932), Metamorphoseon P.169 (1931), Impressioni brasiliane P.153 (IMSLP "1931?"), Concerto a cinque P.174 (1934), Piano Concerto in A minor P.40 (1941).
  - Unverified, not imported (3): Belfagor Overture P.140, Rossiniana P.148 (also an arrangement of Rossini), Lauda P.166. No First Publication field on the IMSLP page.
  - Not on the checklist: La boutique fantasque (1919, a Rossini arrangement; arrangements are skipped), the Ancient Airs piano versions, the Cimarosa and Paisiello revisions, the songs apart from Deità silvane and Il tramonto, the Sei pezzi per bambini (P.149), the Toccata in D Dorian (P.105b) and La pentola magica (IMSLP first publication 1947). Not checked.
- **Imported:** 1 row: `respighi_p_131_tre_preludi_sopra_melodie_gregoriane_p_131` (PDMX, file licence cc-zero, no licence conflict, `licence_scope` US-PD-only, `publication_year` 1922). Written to `parts/BULK_batchP7_rows.csv` (gitignored) and `files/scores/respighi_p_131_...mid` (untracked, as for the other gathers).
- **Importer:** `import_depth_us_pd.py` gained a `respighi` name rule (`\brespighi|\brepighi`). No `SETS` entry: the Respighi checklist uses P. numbers, not multi-piece opus numbers.
- **Source pools:** `--dry-run --composer respighi` harvests 1 (the P.131 row). The PDMX rows that carry Respighi's name were checked: Nebbie, Fontane di Roma, Pini di Roma parts, Die kleinen Hochländer and the Pines of Rome movements carry a licence conflict (not in the no_license_conflict subset); 'PINI DI ROMA (for Piano)' (Tanaka) and the organ transcriptions (Pines of the Appian Way, Pines near a Catacomb) are arrangements; the no-conflict 'Pini di Roma' file is a single unfinished movement (its own title says 'Actually un-finished'), and was not harvested. Mutopia and OpenScore have no Respighi rows.
- **Live layer not rebuilt:** I ran `build_bulk_layer.py` and `sync_site_data.py` in this worktree. This worktree has only `BULK_batchP7_rows.csv`, so `library_bulk.csv` was rebuilt from 22 rows and tracked `data/` files were deleted. I restored `library_bulk.csv`, `data/` and `library_other_editions.json` from git. The P.131 row is therefore not yet live; rebuilding `library_bulk.csv` and running `sync_site_data.py` is for the main checkout, which has all the batch files. Earlier gather commits also skipped sync for this reason.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items). `docs/catalogues/respighi.csv` generated; the six tracked CSVs regenerated by `catalogue_report.py` restored. Coverage: 0 of 22 in scope (the P.131 row is not live yet).
- **WANTED:** `/workspace/music/library/files/imslp_incoming/respighi/WANTED.md`: 21 in-scope works still wanted, 3 unverified, 7 excluded listed for the record. 24 IMSLP URLs curl-checked (all HTTP 200).
- **Data layer:** `library.csv`, `library_bulk.csv` and `data/` are unchanged in the commit.
- **Models:** Haiku 5.5.

## Isaac Albéniz (d.1909): fully PD gather (CP-GATHER-albeniz)

- **Checklist:** `ALBENIZ` in `scripts/bulk/catalogue_data.py`, 43 in-scope entries (Iberia 12 pieces in four books, Suite española Op.47 8 movements, España Op.165 5 pieces, Chants d'Espagne Op.232 5 pieces, Mallorca Op.202, Recuerdos de viaje Op.71 7 pieces, 12 Piezas Op.92 4 pieces, Pavana-capricho Op.12). Three entries are unverified and not imported: España No.4 (not named on IMSLP), Suite española Op.97, and Piano Sonata No.1 Op.28 (IMSLP year "1884??"). Navarra (completed by Séverac), Rapsodia española (two-piano first edition) and Rapsodia cubana and Concierto fantástico (no year) are excluded as unverified. Operas are not on the checklist.
- **Years:** IMSLP "First Publication" fields and dated editions. Iberia uses the IMSLP set range 1906–08 (Edition Mutuelle), with Book 4's year not read separately (entered as 1908). The Suite española uses Wikipedia's 1901 date for the eight-movement suite; the IMSLP work page returns 404 under three title variants. España uses H.B. Stevens 1890/1892; Chants d'Espagne uses Pujol 1892; 12 Piezas uses the earliest dated edition (Dotésio 1912).
- **Scope:** fully PD (died 1909), so no US-PD-only gate and no change to `approved_us_pd_only`.
- **Imported:** 0 new rows. The importer found 3 PDMX Iberia files (Fête-Dieu, Rondeña, Lavapiés). Their scores are byte-identical to live rows (`albeniz_fete_dieu_ai_seville_from_ib`, `albeniz_k2_rondena_from_iberia_by_alben`, `albeniz_lavapies_from_iberia_by_albe`), so I removed them from `parts/BULK_batchP7_rows.csv` and deleted their score files. Gap: the live-library dedupe compares normalised titles (PDMX title vs live title), so these duplicates passed it. A score-hash check would catch this; not changed here.
- **Skipped:** 16 PDMX arrangements (guitar, organ, band and similar) and 2 unmatched files, per the importer's counters.
- **Coverage fix:** `catalogue_report.py` now keys coverage by row title, not catalogue label. Several rows share a label (Iberia books, Op.47, Op.165, Op.232, Op.71, Op.92), so the old key marked every piece in a set as covered whenever one was live. The Albéniz coverage is now 16 of 43. The six tracked CSVs (busoni, elgar, holst, rachmaninoff, ravel, strauss_r) were restored from git; the untracked CSVs (falla, granados, lyadov, …) were regenerated with the new key and may show different coverage than before.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/albeniz/WANTED.md`: 27 in-scope entries without a live row (9 Iberia, 2 Suite, 3 España, 3 Chants, 6 Recuerdos, 3 12 Piezas, 1 Pavana-capricho). IMSLP URLs curl-checked (200): the Iberia set page, España, Chants d'Espagne, Mallorca, Recuerdos de viaje, 12 Piezas, Pavana-capricho, Navarra, Piano Sonata No.1 and Rapsodia española. The Suite española page is not found on IMSLP, so it has no URL.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items).
- **Data layer:** `library.csv`, `library_bulk.csv` and `data/` are unchanged. Sync was not run in this worktree, which has only the P7 batch file (same as CP-GATHER-respighi); the run in the main checkout would make the 0 new rows live.
- **Models:** Haiku 5.5.

## Emmanuel Chabrier (d.1894): fully PD gather (CP-GATHER-chabrier)

- **Checklist:** `CHABRIER` in `scripts/bulk/catalogue_data.py`, 15 in-scope entries: 10 Pièces pittoresques (Enoch Frères et Costallat, ca.1881), Bourrée fantasque (1891), Habanera (1885), España (orchestra, 1884), Joyeuse marche (orchestra, bracketed n.d.[1890]), Suite pastorale (orchestra, 1896). Three unverified entries are not imported: Trois valses romantiques (two-piano first edition, 1883), Danse slave and Fête polonaise (IMSLP pages 404 under these titles). Operas and songs are not on the checklist.
- **Years:** IMSLP "First Publication" fields, checked 2026-10-11. Joyeuse marche has only a bracketed estimate.
- **Scope:** fully PD (died 1894), so no US-PD-only gate and no change to `approved_us_pd_only`.
- **Importer:** `chabrier` NAME_RX (`\bchabrier\b`) and `"Pièces pittoresques"` in `SETS` in `import_depth_us_pd.py`.
- **Imported: 0 new rows.** The PDMX Chabrier files that pass the licence filter are the songs Villanelle des petits canards and L'Invitation au voyage, already live in `library_bulk.csv`. The OpenScore Chabrier rows are also songs (Ballade des gros dindons, Chanson pour Jeanne, Villanelle), already live. Mutopia has no Chabrier rows.
- **WANTED:** `files/imslp_incoming/chabrier/WANTED.md` (in the library checkout): 15 in-scope works still wanted; IMSLP URLs curl-checked (HTTP 200). The Danse slave and Fête polonaise pages have no URL.
- **Checks:** `licence_audit.py`: 0 violations (9474 bulk rows). `build_catalog.py --check`: passes (9787 items).
- **Data layer:** `library.csv`, `library_bulk.csv`, `parts/` and `data/` are untouched; sync not run (no rows changed). The six tracked CSVs regenerated by `catalogue_report.py` were restored from git.
- **Models:** Haiku 5.5.

## Ernest Chausson (d.1899): fully PD gather (CP-GATHER-chausson)

- **Checklist:** `CHAUSSON` in `scripts/bulk/catalogue_data.py`, 17 rows. In scope (10): Quelques danses Op.26 (1896), Paysage Op.38 (n.d. ca.1910, no dated First Publication field), Poème Op.25 (1898), Concert Op.21 (1894), Symphony Op.20 (1891), Viviane Op.5 (1888, reduction), Piano Quartet Op.30 (1898), String Quartet Op.35 (1900 parts / 1907 score), Pièce Op.39 (1917), 5 Fantaisies Op.1 (1879). Unverified (7, not imported): Piano Trio Op.3 (IMSLP '1919 ?'), Sonatinas G and D (manuscripts), 11 Fugues, Marche militaire, Andante and Allegro (manuscripts), Soir de fête Op.32 (no first-publication field). Years are from IMSLP work pages.
- **Scope:** vocal works (mélodies, Poème de l'amour et de la mer, Chanson perpétuelle, the Duos, Ballata), the opera Le roi Arthus, La tempête and the sketches are not on the checklist.
- **Importer:** `import_depth_us_pd.py` gets a `chausson` name rule. No `SETS` change needed (Op.1 and Op.26 were already there).
- **Imported: 0 new rows.** `--dry-run --composer chausson` harvests 0. The PDMX and OpenScore Chausson files are all songs (Op.2, Op.24, Serenade italienne), already live. PDMX Ave Verum Op.6 No.2 has a licence conflict. Mutopia has none.
- **WANTED:** `files/imslp_incoming/chausson/WANTED.md` (library checkout): 10 in-scope works still wanted; 17 IMSLP URLs curl-checked (all HTTP 200).
- **Checks:** `licence_audit.py` 0 violations (9474 bulk rows); `build_catalog.py --check` passes (9787 items). `docs/catalogues/chausson.csv` written (coverage 0 of 10); other composers' CSVs untouched.
- **Data layer:** `library.csv`, `library_bulk.csv`, `parts/` and `data/` untouched; sync not run (no rows changed).
- **Models:** Haiku 5.5.

## Lili Boulanger (d.1918): fully PD gather (CP-GATHER-boulanger)

- **Checklist:** `BOULANGER` in `scripts/bulk/catalogue_data.py`, 28 rows. In scope (20): Faust et Hélène (1913), Psaume XXIV (1924), Psaume CXXIX (1921), Psaume CXXX (1924), Vieille prière bouddhique (1921), Pie Jesu (1922), Soir sur la plaine (1918), Pour les funérailles d'un soldat (1918), Hymne au soleil (1919), Renouveau (1919), Dans l'immense tristesse (1919), 3 Morceaux (1918), Nocturne (1918), Clairières dans le ciel (1919), D'un matin de printemps (1922), D'un soir triste (1993, trio version), Les sirènes (1918), Reflets (1919), Attente (1918), Thème et variations (1993). Unverified (8, not imported): Pièce LB 5, Pendant la tempête, Fugue LB 27, two preludes, Sous-bois, La Source, Le Retour (IMSLP gives a manuscript date and no first-publication field). Years are the IMSLP "Year of First Publication" field.
- **Scope:** the Psaumes are listed by their IMSLP titles (Psaume CXXIX and CXXX use Vulgate numbering, so they may not match the English psalm numbers). The unlisted sketches, the other songs outside Clairières, Reflets, Attente, Les sirènes and Dans l'immense tristesse, and the violin versions of Nocturne and Cortège (2 Pieces, Schirmer 1918) are not separate rows.
- **Name rule:** `import_depth_us_pd.py` gets a `boulanger` rule (`\blili boulanger\b|\bboulanger lili\b|\bl boulanger\b`). Nadia Boulanger (1887-1979) is a different composer and is not matched. `3 Morceaux` and `Clairières` are added to `SETS` so each file keeps its own title.
- **Imported: 0 new rows.** `--dry-run --composer boulanger` harvests 19 rows after the importer's own filter; 16 are already live by normalised title. The other 3 (D'un vieux jardin, Cortège for piano and the piano-titled Nocturne) are the same PDMX files as live rows, which the popularity fields show (identical rating, ratings, favorites, views). The title dedupe misses them because the live titles differ ("Cortège for piano" vs "Cortège for piano - Lili Boulanger"). This is the same gap noted for the Iberia duplicates; a score-hash check would catch it. Not changed here.
- **WANTED:** `files/imslp_incoming/boulanger/WANTED.md` (library checkout): 13 works still wanted (12 rows, plus the D'un jardin clair movement of 3 Morceaux); 13 IMSLP URLs curl-checked (HTTP 200 after redirects).
- **Live coverage:** 8 of 20 in-scope rows (Pie Jesu, Soir sur la plaine, Dans l'immense tristesse, Nocturne, Clairières, Reflets, Attente, and 3 Morceaux partly: D'un vieux jardin and Cortège, not D'un jardin clair).
- **Checks:** `licence_audit.py` 0 violations (9474 bulk rows); `build_catalog.py --check` passes (9787 items). `docs/catalogues/boulanger.csv` written. `catalogue_report.py` regenerates every composer's CSV, so the other CSVs were restored from a backup taken first.
- **Data layer:** `library.csv`, `library_bulk.csv`, `parts/` and `data/` untouched; sync not run (no rows changed).
- **Models:** Haiku 5.5.

## Gabriel Fauré (d.1924): fully PD gather (CP-GATHER-faure)

- **Checklist:** `FAURE` in `scripts/bulk/catalogue_data.py`, 29 rows: 22 in scope, 7 unverified. In scope: Requiem Op.48 (1900), Pavane Op.50 (1888), Sicilienne Op.78 (1898), Pelléas et Mélisande Op.80 (1900), Élégie Op.24 (1883), Dolly Op.56 (1894), Berceuse Op.16 (1879), Ballade Op.19 (1880), Violin Sonata No.1 Op.13 (1877), Piano Quartet No.1 Op.15 (1884), Cello Sonata No.1 Op.109 (1918), Piano Trio Op.120 (1923), String Quartet Op.121 (1925), Thème et variations Op.73 (1897), Barcarolle No.1 Op.26 (1881), Nocturne No.13 Op.119 (1922), Impromptu No.2 Op.31 (1883), La bonne chanson Op.61 (1894), Mirages Op.113 (1919), L'horizon chimérique Op.118 (1922), Poème d'un jour Op.21 (1880), Après un rêve Op.7 No.1 (1878). Unverified (not imported): Préludes Op.103, Valse-caprice Op.38, Romances sans paroles Op.17, Masques et bergamasques Op.112, Quintet No.1 Op.89 (the standard IMSLP titles return 404); Nocturne No.6 Op.63 and Roses d'Ispahan Op.39 No.4 are live already.
- **Name rule:** `import_depth_us_pd.py` gets a `faure` rule (`\bfaure\b`); `NOT_NAME` excludes Jean-Baptiste Faure. `Op.56`, `Op.61`, `Op.113`, `Op.118` and `Op.21` are multi-piece sets in `SETS`, so each file keeps its own title.
- **Imported: 8 new rows.** Dolly Suite Nos 1–6 (`faure_op_56_faure_dolly_suite_no_*`, all six movements), `faure_op_7_no_1_apres_un_reve_song` (PDMX) and `faure_op_50_pavane_chorus_and_orchestra_or_pianob3` (PDMX). `library_bulk.csv` +8 rows; `library_other_editions.json` +25 lines for the dropped PDMX duplicates of the kept rows.
- **Dedupe:** the importer harvested 19 rows. Eight were byte-identical to live Fauré score files (6 Requiem movements, one Pavane variant, the OpenScore Après un rêve; checked by MD5 against `files/scores/faure_*`, excluding the new ids), so they were removed from `parts/BULK_batchP7_rows.csv` and their score files deleted. Three more were dropped by `dedupe.dedupe` as editions of kept rows. The Mutopia Berceuse and Sicilienne, the OpenScore Poème d'un jour songs and the OpenScore String Quartet were dropped by the importer's live-title dedupe (they are live under other titles). The title dedupe misses PDMX files that are live under a different title, as in the Boulanger and Albéniz runs.
- **WANTED:** `files/imslp_incoming/faure/WANTED.md` (library checkout): 13 in-scope works still wanted, with IMSLP URLs curl-checked (HTTP 200). Dolly is no longer wanted (imported). The 5 unverified works are listed without URLs (404 at the standard titles).
- **Coverage:** `docs/catalogues/faure.csv` written: 9 of 22 in-scope works covered. Written by running `catalogue_report.py` for the Fauré entry only, into a temp dir; the shared `.tmp/depth1/catalogue_coverage.json` was restored from backup, and the other composers' CSVs were not touched.
- **Checks:** `licence_audit.py` 0 violations (9482 bulk rows); `build_catalog.py --check` passes against the tracked `data/` snapshot (9787 items).
- **Incident:** `build_bulk_layer.py` was run once by mistake. It rebuilds `library_bulk.csv` from the `parts/BULK_batch*` files present in this worktree (only P7), which dropped the layer from 9501 rows to 31. The file was restored from a backup before anything was committed (`git diff` against HEAD is empty for that file at that point). The script had also rewritten the gitignored `parts/DEDUPE_MANIFEST.csv` and `parts/DEDUPE_REPORT.md` (no longer the earlier contents) and `library_other_editions.json`; the editions file was restored from git and then merged with the Fauré entries. Do not run `build_bulk_layer.py` in this worktree until all batch files are present.
- **Data layer:** `sync_site_data.py` was run and then reverted. It also pulls in other sessions' pending items (21 untracked items from Falla, Bartók, Glazunov, Granados and Lyapunov, and edits to Elgar, Holst, Mahler, Satie and Wagner items), so `data/` is left at HEAD and the 8 Fauré items are not on the site until a sync runs on a clean tree.
- **Models:** Haiku 5.5.

## CP-GATHER-satie: Erik Satie (d. 1925), 2026-10-11

- **Scope:** fully PD (died 1925), so no US-PD-only approval and no publication-year gate. `licence_class` clean, no `licence_scope`. Satie was not on any exclusion list, so `pdmx_composers_manual.json` and `schema.py` are unchanged.
- **Checklist:** `SATIE` in `scripts/bulk/catalogue_data.py`, 26 rows. In scope (21): 3 Gymnopédies (1888), Gnossiennes (1913), 3 Sarabandes (1911), 4 Ogives (1889), Pièces froides (1913), Avant-dernières pensées (1916), Embryons desséchés (1913), Sports et divertissements (1914), 5 Nocturnes (1919), Vexations (1949), Je te veux (1902), Parade (1917), Socrate (1919), Le Piccadilly (1975), 3 Morceaux en forme de poire (1911), 3 Véritables préludes flasques (1912), Heures séculaires et instantanées (1916), Croquis et agaceries (1913), Sonatine bureaucratique (1917), Chapitres tournés en tous sens (1913), Messe des pauvres (1920). Unverified, not imported (5): Descriptions automatiques, Vieux sequins et vieilles cuirasses, Les Pantins dansent (IMSLP title 404), Rêverie de l'enfance de Pantagruel, Relâche.
- **Imported (7 PDMX rows, clean):** `satie_3_gymnopedies_gymnopedie_1`, `_gymnopedie_1b2`, `_gymnopedie_1b3`, `_deuxieme_gymnopedie`, `_troisieme_gymnopedie`, `satie_gnossiennes_1ere_gnossienne`, `satie_socrate_erik_satie_socrate`. Appended to `library_bulk.csv` (7 lines, no other rows changed).
- **Dropped (6 PDMX candidates, byte-identical MIDI to a live or existing score):** Four Ogives, Gnossienne No.3, Gnossienne No.4, Vexations, Je te veux waltz song (same bytes as the live cello-trio Je te veux), and one Gnossienne 1 (same bytes as an existing `files/scores` file with no CSV row). Their score files were removed. `library_other_editions.json` not updated for these.
- **Skipped by the harvester:** 6 arrangements (guitar, big band, flute/harp, lever harp, etc.). 36 unmatched PDMX rows (student and transcription files with no checklist title).
- **Not run:** `build_bulk_layer.py`. This worktree's `parts/` holds only the P7 batch, so the rebuild wrote a 40-row layer and would have dropped the other batches. Reverted (`git diff` clean). Rows were appended directly, as in the Fauré gather.
- **Not run:** `sync_site_data.py`. The 7 rows reach the site after a sync in a clean main checkout.
- **Checks:** `licence_audit.py`: 0 violations (9489 bulk rows). `build_catalog.py --check`: pass (9787 items). No duplicate ids.
- **Coverage:** `docs/catalogues/satie.csv`. 16 of 21 in-scope works have at least one live item (title match); 13 have no clean file yet.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/satie/WANTED.md`, 13 works (3 Sarabandes, Pièces froides, Avant-dernières pensées, Embryons desséchés, Sports et divertissements, 5 Nocturnes, Parade, Le Piccadilly, 3 Véritables préludes flasques, Heures séculaires, Croquis, Sonatine bureaucratique, Chapitres tournés). IMSLP URLs curl-checked (HTTP 200).
- **Models:** Haiku 5.5.

## CP-GATHER-grieg: Edvard Grieg (d. 1907), 2026-10-11

- **Scope:** fully PD (died 1907), so no US-PD-only approval and no publication-year gate. `licence_class` clean, no `licence_scope`. Grieg was not on any exclusion list, so `pdmx_composers_manual.json` and `schema.py` are unchanged.
- **Checklist:** `GRIEG` in `scripts/bulk/catalogue_data.py`, 83 rows. 66 Lyric Pieces (one row per piece, all 10 books; book years from the Wikipedia 'Lyric Pieces' article) and 17 main works (Piano Sonata Op.7, Violin Sonatas Op.8/13/45, Piano Concerto Op.16, Sigurd Jorsalfar Op.22, Peer Gynt Op.23/46/55, Ballade Op.24, String Quartet Op.27, Cello Sonata Op.36, Holberg Suite Op.40, Symphonic Dances Op.64, Haugtussa Op.67, plus Norwegian Dances Op.35 and Slåtter Op.72 as unverified). Work years other than the Lyric Pieces books are general-reference dates, not checked against IMSLP.
- **Importer:** `import_depth_us_pd.py` `grieg` name rule and multi-movement opus numbers in `SETS`. Lyric Pieces stay one row per piece (not in `SETS`), so a whole-book file is not matched.
- **Imported (5 PDMX rows, clean, MIDI in `files/scores/`):** `grieg_op_16_grieg_piano_concerto_in_a_minor_3rd_moveme`, `grieg_op_16_piano_concerto_in_a_minor_opus_16_grieg_2n`, `grieg_op_23_morgenstimmung`, `grieg_op_27_grieg_quartet_in_g_op_27_first_movement`, `grieg_op_46_ase_s_tod`. Appended to `library_bulk.csv`. `parts/BULK_batchP7_rows.csv` holds the same rows minus the dropped ones.
- **Dropped (8 harvested candidates):** 7 PDMX files byte-identical to live or existing score files (Lyric Pieces Op.12 No.1 and No.5, Op.38 No.4, Op.43 No.1, Op.47 No.2, Op.7 movement 2, Anitra's Dance). Their new score files were removed. The Holberg-kantate file is labelled Op.40 by PDMX but is a different work, so it was not imported. The dry run still lists these because it dedupes by title, not by MIDI bytes.
- **Live-title dedupe:** 5 Mutopia and OpenScore candidates (In the Hall of the Mountain King, Troldtog, Wedding-day at Troldhaugen, the Op.27 quartet mxl) matched live titles and were not imported.
- **Coverage:** `docs/catalogues/grieg.csv`. 15 of 81 in-scope works have a live item by title match; 9 of 66 Lyric Pieces are live.
- **WANTED:** `files/imslp_incoming/grieg/WANTED.md` (library checkout): 66 in-scope works (57 Lyric Pieces, grouped by book with one IMSLP book page each; 9 main works). 28 IMSLP URLs curl-checked (26 HTTP 200; Norwegian Dances Op.35 and Slåtter Op.72 returned 404 at the standard title and are listed without URLs).
- **Checks:** `licence_audit.py` 0 violations (9494 bulk rows). `build_catalog.py --check` passes (9787 items).
- **Not run:** `build_bulk_layer.py` (this worktree's `parts/` holds only P7). `sync_site_data.py` (pulls in other sessions' pending items). `data/` untouched.
- **Models:** Haiku 5.5.

## CP-GATHER-liszt: Franz Liszt (d. 1886), 2026-10-11

- **Scope:** fully PD (died 1886): no US-PD-only approval, no publication-year gate. `licence_class` clean, no `licence_scope`. `approved_us_pd_only`, `pdmx_composers_manual.json` and `schema.py` unchanged (Liszt was not excluded).
- **Checklist:** `LISZT` in `scripts/bulk/catalogue_data.py`, 32 rows: 27 in scope, 5 unverified. Late works first (LaDoger list): Nuages gris, Bagatelle sans tonalité, R.W.-Venezia, Am Grabe Richard Wagners, Csárdás macabre, Mephisto Waltz 2, Mephisto Polka, Années III, Via Crucis, En rêve, Schlaflos. Then core cinematic and piano works: Liebesträume 3, Consolations, Hungarian Rhapsodies 2/9/12, Les préludes, Piano Concerto 1, Piano Sonata B minor, Totentanz, Mephisto Waltz 1, Dante and Faust symphonies, Transcendental and Paganini Études, Années II, Ballade 2. Above the 15-25 target because the brief's late-works list already has 14 items.
- **Years:** IMSLP 'First Publication' fields, read 2026-10-11 from the work pages (not Wikipedia). Gate-free, so informational only.
- **Unverified (not imported):** La lugubre gondola I/II (S.134), Unstern! (S.208), Mephisto Waltz No.3, Venezia e Napoli (S.162/3, already live from BULK_batchP9), Historische ungarische Bildnisse. IMSLP returned 404 under every title tried.
- **Importer:** `liszt` name rule in `NAME_RX`; S.139, S.140, S.161, S.163, S.172 in `SETS` (multi-piece sets keep file titles).
- **Harvest and import:** dry run 24 candidates (7 arranged, 35 unmatched, 2 excluded-or-unverified). 3 dropped by live-title dedupe; 20 written to `parts/BULK_batchP7_rows.csv`; 1 failed the 20 s length check (Paganini Étude 6 var. 1 excerpt). Build dedupe then dropped 2 as duplicate pieces (a second Hungarian Rhapsody No.2 file and a second Transcendental Étude No.10 file; byte equality not checked). Their MIDIs were removed from `files/scores/`.
- **Imported (18 rows, clean, MIDI in `files/scores/`):** `liszt_s_541_3_liebestraume_no_3`, `liszt_s_244_2_hungarian_rhapsody_no_2_s_244_2b2`, `liszt_s_172_*` (Consolations I and No.4), `liszt_s_199_nuages_gris_trube_wolken_s_199`, `liszt_s_139_*` (10 Transcendental Études pieces: Paysage, Preludio, Vision, Wilde Jagd, Fusées, Appassionata, Harmonies du soir, S.139/2 Molto vivace, after Paganini No.4, S.140 var. 2), `liszt_s_140_*` (Paganini Études: La campanella, No.3 + No.4 Mazeppa, No.6). Appended to `library_bulk.csv` (18 lines, same column order).
- **Known cosmetic issues:** two Paganini-based rows carry a S.139 `cat` (S. 140 Etude 6 var. 2; Transcendental Études after Paganini No.4 version II) because the PDMX titles are ambiguous; the MIDIs are correct Liszt.
- **Coverage:** `docs/catalogues/liszt.csv`. 8 of 27 in-scope works have a live item by title match.
- **WANTED:** `files/imslp_incoming/liszt/WANTED.md` (library checkout): 19 in-scope works; every URL curl-checked HTTP 200 (after redirects); publication years and publishers from the IMSLP pages.
- **Checks:** `licence_audit.py` 0 violations (9512 bulk rows). `build_catalog.py --check` **not run**.
- **Not run, and why:** `build_bulk_layer.py` and `sync_site_data.py`. This worktree's `parts/` holds only BULK_batchP7. My first attempt at both ran here and rewrote tracked `library_bulk.csv` (58 rows instead of about 9,500) and removed tracked `data/` files. I restored every tracked file to HEAD (`git checkout`), which also reverted my two script edits; I re-applied them and appended the 18 Liszt rows to `library_bulk.csv` by hand. The untracked `data/items/liszt_*.json` that sync wrote were deleted. `data/` is untouched, as in the Grieg run. The data regeneration needs the full `parts/` from the main checkout.
- **Models:** Haiku 5.5.

## CP-GATHER-chaminade (Cécile Chaminade, d.1944, US-PD-only)

- **Approval and gate:** added to `approved_us_pd_only` (LaDoger priority list 2026-10-11). Works published 1930 or earlier only; the Wikipedia list has nothing dated after 1928, so the 1930 gate excludes nothing.
- **Checklist:** `CHAMINADE` in `scripts/bulk/catalogue_data.py`: 35 rows, 32 in scope, 3 unverified (Op.35 set, songs without opus, Ritournelle Op.83 piano).
- **Imported (2):** `chaminade_op_107_concertino_for_flute_and_orchestra_d_majo` (PDMX, CC0, no conflict, pub 1902), `chaminade_op_170_au_pays_bleu` (OpenScore Lieder CC0 song, pub 1928 per Wikipedia 'Air Italien (Au Pays Bleu)').
- **Skipped:** about 30 PDMX rows, all `license_conflict` True (songs and piano pieces, e.g. Danse créole Op.94, Barcarolle Op.7, Berceuse, Alleluia, Madrigal); the OpenScore Ritournelle, a song with no opus or year source. Arrangements: 0 after the Concertino exemption.
- **WANTED:** `files/imslp_incoming/chaminade/WANTED.md` (library checkout): 30 in-scope works; URLs curl-checked (HTTP 200) except Automne (Op.35 No.2) and Album des enfants (Op.123), which are not on IMSLP under the titles tried.
- **Checks:** `licence_audit.py` 0 violations (9514 bulk rows); `build_catalog.py --check` passes.
- **Not run, and why:** `build_bulk_layer.py`, `sync_site_data.py`: this worktree's `parts/` holds only P7 and a sync rewrites tracked data here. `data/` untouched.
- **Models:** Haiku 5.5.

## CP-GATHER-sibelius (Jean Sibelius, d.1957, US-PD-only)

- **Approval and gate:** added to `approved_us_pd_only` (LaDoger priority list 2026-10-11). Works first published 1930 or earlier only. Death year 1957 is past the default 1955 ceiling, so `US_PD_ONLY_MAX_DEATH` in `scripts/bulk/schema.py` lists `"jean sibelius": 1957` (same mechanism as Grechaninov and Stravinsky). The EU is not PD until 2028 (life+70 from 1958): the EU warning applies.
- **Checklist:** `SIBELIUS` in `scripts/bulk/catalogue_data.py`: 35 rows, 20 in scope, 15 unverified. Piano pieces first (Kyllikki Op.41, Impromptus Op.5, Sonatinas Op.67, Op.75, Op.76, Op.85, Op.94, Op.97, Op.99, Op.101, Op.103), then Finlandia, Valse triste, Karelia Suite and Overture, En Saga, Swan of Tuonela, Symphonies 2 and 5, Violin Concerto. Years: IMSLP "First Publication" on each work page. Nothing read so far is dated after 1925, so no work is excluded for the 1930 gate. Unverified (no IMSLP year read, not imported): Op.24, Op.34, Op.58, Op.100, Op.106 (possibly post-1930), Lemminkäinen Op.22, Symphonies 1, 3, 4, 6, 7, Tapiola, Pohjola's Daughter, Violin Sonatina Op.80, Oceanides Op.73.
- **Excluded by year:** Op.44 No.2 "Scene with cranes" (IMSLP: first published 1973, not in the checklist as a row).
- **Imported (0):** Mutopia and OpenScore raw CSVs have no Sibelius rows. The two PDMX Sibelius rows are "Variations on a theme by Golding" (CC0, not in the checklist) and "Come away Death" (song, CC0; not in the checklist). `--dry-run --composer sibelius` harvests 0 rows.
- **WANTED:** `files/imslp_incoming/sibelius/WANTED.md` (library checkout): 20 in-scope works, IMSLP URLs curl-checked (HTTP 200). Valse triste uses the IMSLP title "Valse Triste, Op.44 No.1" (the standard title 404s).
- **Checks:** `licence_audit.py` 0 violations (9514 bulk rows); `build_catalog.py --check` run.
- **Not run, and why:** `build_bulk_layer.py` and `sync_site_data.py` (nothing new to add, and a sync here rewrites tracked data; see CP-GATHER-liszt). `data/` untouched.
- **AGENTS.md:** Sibelius added to the "Approved today" list.
- **Models:** Haiku 5.5.

## CP-GATHER-reger: Max Reger (d. 1916), 2026-10-11

- **Scope:** fully PD (died 1916), so no US-PD-only approval and no publication-year gate. `licence_class` clean, no `licence_scope`. Reger was not on any exclusion list, so `pdmx_composers_manual.json` and `schema.py` are unchanged.
- **Checklist:** `REGER` in `scripts/bulk/catalogue_data.py`, 27 rows: 26 in scope (Silhouetten Op.53, Aus meinem Tagebuch Op.82, Träume am Kamin Op.143, Blätter und Blüten WoO III/12, Bach Variations Op.81, Telemann Variations Op.134, Op.27, 46, 33, 60, 67, 127 organ, Hiller Op.100, Mozart Op.132, Sinfonietta Op.90, Konzert im alten Stil Op.123, Romantic Suite Op.125, Ballet Suite Op.130, Violin Concerto Op.101, Piano Concerto Op.114, Clarinet Quintet Op.146, Clarinet Sonatas Op.49, violin solo Op.42 and Op.91, String Quartet No.4 Op.109, Piano Quintet No.2 Op.64) plus one exclusion row (see below). Years: Wikipedia works table; IMSLP First Publication read for Op.33, Op.130, Op.143 only (the other IMSLP pages carry no such field).
- **Importer:** `import_depth_us_pd.py` `reger` name rule; Op.42, 49, 53, 82, 91, 143 and WoO III/12 added to `SETS` (one file per piece or sonata).
- **Exclusion:** OpenScore Lieder rows (Plattdeutsche Lieder Op.32–34, Lieder Op.125, 3 Lieder Opp.122–124) carry "Max Reger" in the composer column, but the path is `Greger, Luise/`. Without the exclusion row the importer would have taken the Op.125 and Op.33 songs as Reger's Romantic Suite and organ sonata. Eight candidates were dropped.
- **Imported: 0 new rows.** The one instrumental candidate left after the exclusion (String Quartet No.4 Op.109, OpenScore) is already live (`reger_op109_string_quartet_no_4_op_109`). The PDMX Reger rows are songs and choral works outside the checklist; 21 unmatched. One arrangement skipped.
- **Coverage:** `docs/catalogues/reger.csv`, 2 of 26 in-scope works live (Op.42 Mutopia, Op.109 OpenScore). `catalogue_report.py` also rewrites every other composer's CSV; I reverted the tracked ones it touched so this slice holds only `reger.csv`.
- **WANTED:** `files/imslp_incoming/reger/WANTED.md` (library checkout): 24 works, IMSLP work-page URLs curl-checked (all HTTP 200). Publishers not read, so none listed.
- **Checks:** `licence_audit.py` 0 violations (9514 bulk rows). `build_catalog.py --check` passes (9787 items). `sync_site_data.py` and `build_bulk_layer.py` not run (no data change). `data/` untouched.
- **Models:** Haiku 5.5.

## CP-GATHER-karg_elert: Sigfrid Karg-Elert (d. 1933), 2026-10-11

- **Scope:** died 1933, so the US-PD-only gate applies (works first published 1930 or earlier only). PD in the EU and life+70 countries since 2004. LaDoger priority list 2026-10-11, from the brief. Added to `approved_us_pd_only` (note 'LaDoger priority list 2026-10-11') and to the AGENTS.md approval line. The death year 1933 is under the default 1955 ceiling, so `US_PD_ONLY_MAX_DEATH` in `schema.py` is unchanged. The gate is checked: a 1930 work is `flagged` (US-PD-only), a 1931 work is held back.
- **Checklist:** `KARG_ELERT` in `scripts/bulk/catalogue_data.py`, 36 rows: 31 in scope, 4 post-1930 exclusions (Op.142, 144, 145, 150; Op.156 and the later works are not in the list), 1 unverified (Op.143). Years: IMSLP 'Year of First Publication' where the work page has it; otherwise the earliest dated publisher line (Carl Simon, Novello, Elkin, Oxford, Steingräber). Composition dates from Wikipedia and IMSLP were not used as publication years. Nothing outside the checklist is in scope: songs, the W-numbered works and the untitled sets are left out.
- **Judgement calls:** Op.141 Triptych is dated by an Elkin & Co. publisher line '1930' (no First Publication field). It is exactly on the cut-off, so it is in scope; check the plate date before publishing. Op.107 (1918/9) and Op.121 (1921) carry a '?' on IMSLP and are kept on the date printed. Op.46 is 'First Publication 1911 (in part)'. Op.143 (organ symphony, composed 1930) has no IMSLP year, so it is not imported.
- **Importer:** `import_depth_us_pd.py` `karg_elert` name rule (`\bkarg\b`). No set labels added: all checklist cats are single-file rows, so the importer's `SETS` list is unchanged.
- **Imported: 0 new rows.** Mutopia and OpenScore raw CSVs have no Karg-Elert rows. PDMX has one row credited to him: 'Sigfrid Karg-Elert - Organ Symphony in F minor Op. 143 Ending' (CC0, 167 s, composer field 'Op. 143 Siegfried Karg-Elert'). It is held back as unverified: Op.143 has no verified publication year. A dated edition would be needed before import.
- **Coverage:** `docs/catalogues/karg_elert.csv` (36 rows; 0 of 31 in-scope works live). Written by hand from the checklist, not by `catalogue_report.py`, which rewrites every other composer's CSV in the shared tree.
- **WANTED:** `files/imslp_incoming/karg_elert/WANTED.md` (library checkout): 31 works, IMSLP work-page URLs curl-checked (all HTTP 200). Publishers listed only where read on the page; others 'not read'. Post-1930 works and the unverified symphony are listed separately.
- **Checks:** `licence_audit.py` 0 violations (9514 bulk rows). `build_catalog.py --check` passes (9787 items). `sync_site_data.py` and `build_bulk_layer.py` not run (nothing to add; no data change). `data/` untouched.
- **Models:** Haiku 5.5.

## CP-GATHER-lyadov-p2: Anatoly Lyadov (d. 1914), second pass, 2026-10-11

- **Scope:** fully PD (died 1914), no US-PD-only gate, `licence_class` clean, no `licence_scope`. `AGENTS.md` and `pdmx_composers_manual.json` do not exclude Lyadov, so nothing changed there.
- **Checklist:** `LYADOV` in `scripts/bulk/catalogue_data.py` rewritten, 61 rows: 55 in-scope, 6 unverified. Second pass: every piano opus from the IMSLP category (Biryulki Op.2, 6 Morceaux Op.3, Arabesques Op.4, Etude Op.5, Intermezzi Op.7 and Op.8, Morceaux Op.9/10/11/24/31/33/64, Etudes Op.12/37, Preludes Op.13/27/36/39/46/57, Mazurkas Op.15/38, Bagatelles Op.17/30/53, Novellette Op.20, From Bygone Days Op.21, Sur la prairie Op.23, Idylle Op.25, Petite valse Op.26, Marionettes Op.29, Musical Snuffbox Op.32, Canons Op.34, Glinka variations Op.35, Fugues Op.41, Preludes and Mazurka Op.42, Barcarolle Op.44, Etude and Canzonetta Op.48, Polish variations Op.51, Morceaux de ballet Op.52, Morceaux Op.64, the Fugue on La Do Fa and 12 Canons), plus the orchestral and tone-poem works.
- **Years:** IMSLP 'First Publication' field, fetched 2026-10-11 (all 75 works in the IMSLP category scanned, not just the first pass). Corrections from the first pass: Op.11 (1886), Op.19 (1888), Op.42 (1898), Op.51 (1901), Op.56 (1905), Op.63 (1910), Op.66 (1913) and Op.57 (1905) are now in scope with IMSLP years. Op.32, Op.44 and Op.40 are no longer 'earliest edition' guesses: IMSLP gives 1893, 1898 and 1897. Unverified (no first-publication year on IMSLP): Impromptu Op.6, Prelude-Pastorale, Sarabande, The Procession, Dance of the Mosquito (IMSLP 1911 but instrumentation unclear), Dance of the Amazon Op.65.
- **Out of scope:** songs and choral works (Op.18, Op.22, Op.43, Op.50, Op.61, folk-song arrangements), compilations (Opp.2-3, 6, 15; Opp.39, 44; Preludes for Piano 1985-86).
- **Importer (`scripts/bulk/import_depth_us_pd.py`):** Op.9, Op.41 and Op.57 added to `SETS` so each set member keeps its own title. The global `SETS` change also reaches any other composer with the same catalogue label; none of those are run in this gather.
- **Imported:** 0 new rows. `import_depth_us_pd.py --dry-run --composer lyadov` harvests two candidates, both already live (`lyadov_op11no1_prelude_op_11_no_1_anatoly_l`, `lyadov_op40no3_anatoliy_lyadov_prelude_op_4`). A word-bounded search of PDMX composer, title and artist fields finds only those two files (the naive substring search matched 'shadow'). Mutopia and OpenScore raw pools have no Lyadov match. The non-dry run was not made: with no new candidates it would only rewrite `parts/BULK_batchP7_rows.csv`.
- **Skipped:** nothing imported; the 6 unverified rows are not imported.
- **Checks:** `licence_audit.py`: 0 violations (9514 bulk rows). `build_catalog.py --check`: pass (9787 items). `docs/catalogues/lyadov.csv` regenerated: 2 of 55 in-scope covered.
- **Side effect cleaned up:** `catalogue_report.py` (which runs for all composers) rewrote eight tracked CSVs (busoni, elgar, grieg, holst, rachmaninoff, ravel, satie, strauss_r) with live-library coverage changes from other sessions. They were restored with `git checkout`. The untracked CSVs of other composers (falla, granados, chaminade, ...) were regenerated from current data and not restored.
- **Not done:** `sync_site_data.py` not run (no rows added). No push.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/lyadov/WANTED.md`: 55 in-scope rows (Op.11 and Op.40 partly live), 6 unverified rows listed. IMSLP URLs checked (HTTP 200) except Die Braut von Messina (Op.28), which has no IMSLP page.
- **Models:** Haiku 5.5.

## CP-GATHER-arensky-p2: Anton Arensky (d. 1906), second pass, 2026-10-11

- **Scope:** fully PD (died 1906): no US-PD-only approval and no publication-year gate; `licence_status` would be `clean`. No change to `AGENTS.md` or `pdmx_composers_manual.json`.
- **Checklist:** the piano sets are split one row per piece, with catalogue numbers like `Op.36 No.7`: Op.25 (4), Op.28 Essais (6), Op.36 (24), Op.41 (4), Op.42 (3), Op.52 Pres de la mer (6), Op.53 (6, new), Op.63 (12), Op.74 (12). That is 77 piano rows. Titles and keys come from the IMSLP movement lists (checked 2026-10-11). Op.52 pieces have no titles on IMSLP, so they are keyed only. Op.43 and Op.67 stay set-level. The other 17 rows are unchanged. Piece years are the set's first-publication year (Op.74: IMSLP 1906, Wikipedia 1905; Op.28: IMSLP Fritzsch 1897, Wikipedia c.1893).
- **Not on the checklist (left out):** Op.66 Twelve Pieces (four hands, 1903), Op.65 and the other items listed in the WANTED file.
- **Importer:** no code change. Per-piece cat numbers are unique and not in `SETS`, so the checklist title is used and each piece has its own cap. Regexes checked by hand against sample titles (for example "Op. 36 No. 7 Valse" matches Op.36 No.7, and "Op.53 Etude" matches Op.53 No.6).
- **Imported: 0 rows.** `import_depth_us_pd.py --dry-run --composer arensky`: harvested 0 matching rows (1 unmatched: the Lullaby, already live). Candidates checked by hand in PDMX:
  - "Otche nash" Op.40 No.3: `license_conflict` True, excluded.
  - PDMX cc-zero opera-tagged number by Arensky, 84 s, 4 tracks, composer name mojibake ("Ð.ÐÑÐµÐ½ÑÐºÐÐ¹ (1861-1906)"). Not on the checklist and not a piano work. The importer's name rule does not match the mojibake. Left for LaDoger to decide.
  - Four Improvisations (cc-zero anthology of Arensky, Rachmaninoff, Glazunov, Taneyev): not an Arensky work, skipped.
  - Mutopia and OpenScore raw pools have no Arensky rows.
- **Checks:** `licence_audit.py`: 0 violations (9514 bulk rows). `build_catalog.py --check`: pass (9787 items). `docs/catalogues/arensky.csv` regenerated. The other composers' CSVs were regenerated too; the tracked ones were restored with `git checkout`, and the untracked ones (chaminade, falla, granados, kalinnikov, lyapunov, nielsen, prokofiev, sibelius, taneyev) were rewritten by the same run and were not committed.
- **Not run:** `sync_site_data.py` (no library rows changed).
- **WANTED:** `/workspace/music/library/files/imslp_incoming/arensky/WANTED.md`: 94 works (77 piano pieces + 17 others), all still wanted. One IMSLP set page per work (IMSLP has no piece-level pages); 26 URLs curl-checked (HTTP 200, following redirects).
- **Models:** Haiku 5.5.

## CP-GATHER-gottschalk: Louis Moreau Gottschalk (d. 1869), 2026-10-11

- **Scope:** fully PD (died 1869), so no US-PD-only approval and no publication-year gate. Piano works first, per LaDoger priority list 2026-10-11 (brief BRIEF_current.md).
- **Checklist:** `GOTTSCHALK` in `scripts/bulk/catalogue_data.py`, 16 works, all in scope: Bamboula Op.2, La Savane Op.3, Le bananier Op.5, Le mancenillier Op.11, The Banjo Op.15, The Last Hope Op.16, Souvenirs d'Andalousie Op.22, Souvenir de Porto Rico Op.31, Ojos criollos Op.37, Manchega Op.38, Souvenir de la Havane Op.39, Murmures eoliens Op.46, Union Op.48, Tremolo Op.58, Pasquinade Op.59, Grande tarantelle Op.67. Years from IMSLP "First Publication" fields (checked 2026-10-11) and Wikipedia; "uncertain" where IMSLP gives a question mark or only an earliest dated edition. Live works (Dying Swan, Battle Cry, Grande fantaisie, Dying Poet, Le Bananier chiptune) are not on the checklist.
- **Left out for now:** Symphony No.1 'A Night in the Tropics' (RO255; reconstructed editions only) and works with no confirmed first-publication year (Ossian Op.4, Colliers d'or Op.6, Berceuse Op.47, Ballades Op.85-90, La gitanella Op.35, Jota aragonesa Op.14).
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `gottschalk` name rule (`\bgottschalk\b`).
- **Imported: 0 rows.** Dry run (`--composer gottschalk`): 1 matching source row, already live (Le Bananier chiptune). PDMX has 21 lines containing "gottschalk" in its file index; none adds a new checklist work.
- **Checks:** `licence_audit.py`: 0 violations (9514 bulk rows). `build_catalog.py --check`: pass (9787 items). `docs/catalogues/gottschalk.csv` written; other composers' tracked CSVs restored with `git checkout`.
- **Not run:** `sync_site_data.py` (no library rows changed).
- **WANTED:** `/workspace/music/library/files/imslp_incoming/gottschalk/WANTED.md`: 16 works, all still wanted. IMSLP URLs curl-checked (16/16 HTTP 200). Years for Bamboula, Le bananier, The Last Hope, Souvenirs d'Andalousie and Grande tarantelle are uncertain.
- **Models:** Haiku 5.5.

## CP-GATHER-nazareth: Ernesto Nazareth (d. 1934), 2026-10-11

- **Scope:** US-PD-only (died 1934; works first published 1930 or earlier). Piano works first, per LaDoger priority list 2026-10-11 (brief BRIEF_current.md). `approved_us_pd_only` in `scripts/bulk/pdmx_composers_manual.json` gained Nazareth (note 'LaDoger priority list 2026-10-11'); AGENTS.md approval line updated.
- **Checklist:** `NAZARETH` in `scripts/bulk/catalogue_data.py`, 20 rows: 16 in scope (Brejeiro 1893, Odeon 1910, Apanhei-te cavaquinho 1914, Ameno Resedá 1913, Confidências 1913, Batuque 1913, Escorregando 1923, Fon-Fon 1913, Cruz perigo 1879, Não caio n'outra 1881, Floraux 1909, Eponina 1913, Expansiva 1903, Escovado 1904, Gotas de ouro 1916, Famoso 1917).
- **Excluded:** Improviso (first published 1931, after the gate).
- **Unverified (not imported):** Tango-habanera, Polka para mão esquerda, Nocturno Op.1. Each has only a 2008 Musica Brasilis typeset edition on IMSLP.
- **Importer changes (`scripts/bulk/import_depth_us_pd.py`):** `nazareth` name rule (`\bnazar[eé]th\b|\bnazare\b`).
- **Imported: 2 new rows** from the 4 harvested PDMX files: Odeon (`nazareth_tango_brasileiro_odeon`) and Batuque (`nazareth_piano_batuque`). Both flagged US-PD-only with publication_year; appended to `library_bulk.csv`; MIDI in `files/scores/`. The other two PDMX Odeon files are duplicates of the same piece and were removed before commit.
- **Years:** IMSLP work pages (First Publication field) for 14 works; Gotas de ouro and Famoso taken from IMSLP work-page snippets in search results. Orchestral and chamber works not checked.
- **Checks:** `licence_audit.py`: 0 violations (9516 bulk rows). `build_catalog.py --check`: pass (9787 items). `docs/catalogues/nazareth.csv` written; other composers' tracked CSVs regenerated by `catalogue_report.py` were restored. `sync_site_data.py` not run.
- **WANTED:** `/workspace/music/library/files/imslp_incoming/nazareth/WANTED.md`: 14 in-scope works still wanted; 14/14 IMSLP URLs curl-checked (HTTP 200).
- **Models:** Haiku 5.5.

## Darius Milhaud (d.1974), US-PD-only, piano first (CP-GATHER-milhaud, 2026-10-11)

- **Scope:** LaDoger priority list 2026-10-11 approves Milhaud for works first published 1930 or earlier (`approved_us_pd_only`; death ceiling 1974 in `schema.py`). Not PD in the EU, so the EU warning applies. 1931+ publications are excluded.
- **Checklist (`MILHAUD`, `scripts/bulk/catalogue_data.py`):** 32 rows. In scope: 23 (piano 7, chamber and ensemble 12, orchestral 4). Excluded post-1930: Scaramouche (1937), Suite provençale (1936), Cello Concerto No.1 (1934), Concertino de printemps (1934), 4 Romances sans paroles (1933), Piano Sonata No.2 (1949). Unverified, not imported: Enfantines Op.59a (no IMSLP page found), Choral Op.111 (first publication not checked). Arrangement, not imported: Tango des Fratellini Op.58c (Mouton, 1921).
- **Correction to the brief:** Saudades do Brasil piano Op.67 first published 1922 (E. Demets, IMSLP work page). The 1921 date belongs to the orchestral Op.67b (IMSLP search snippet, page not fetched).
- **Caramel mou (Op.68):** voice and jazz band, not piano. In scope as an ensemble row (1921, La Sirène musicale).
- **Importer changes (`import_depth_us_pd.py`):** `milhaud` name rule; set labels `Op.25 / 66`, `Op.67`, `Op.78` (file titles kept).
- **Imported: 0 new rows.** The PDMX pool has one Milhaud file, `III. Brazileira Milhaud D. (PIANO 1 ONLY)` (cc-zero, 55 s). It is a two-piano part and matches no checklist row, so it is skipped.
- **Years:** IMSLP work pages (First Publication field) read 2026-10-11 for all 23 in-scope works (WebFetch summaries; the page itself was not opened in a browser).
- **WANTED:** `/workspace/music/library/files/imslp_incoming/milhaud/WANTED.md`: 23 in-scope works still wanted; 23/23 IMSLP URLs curl-checked (HTTP 200).
- **Checks:** `licence_audit.py`: 0 violations (9516 bulk rows). `sync_site_data.py` and `build_catalog.py --check` not run (no data change). `docs/catalogues/milhaud.csv` not written.
- **AGENTS.md:** approval line updated (Darius Milhaud 2026-10-11).
- **Models:** Haiku 5.5.
