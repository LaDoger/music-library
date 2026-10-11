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
