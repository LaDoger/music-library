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
