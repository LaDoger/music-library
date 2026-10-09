# Batch 1 — Grok: Bruckner + niche public-domain scores

Date: 2026-10-09. Rows: `parts/BATCH1_grok_rows.csv` (66). Appended to `library.csv` (334 rows). `added_by=grok`, `verified=yes`. Genre is classical (no genre column; `sync_site_data.py` defaults it).

No Bruckner symphony movement had a clean editable file. The one Bruckner row is the organ Perger Präludium, WAB 129, and the notes say so.

## What landed

| | count |
|---|---|
| New rows | **66** |
| Public Domain (Mutopia header + listing) | 19 |
| CC BY 2.5 / 3.0 / 4.0 (attribution) | 26 |
| CC BY-SA 2.5 / 3.0 / 4.0 (share-alike flag in `legal_notes`) | 21 |
| MIDI + LilyPond (`.ly` or `-lys.zip`) | 66 |
| 15 s preview, own FluidSynth render, MP3 192k, −16.5 to −15.7 LUFS | 66 |
| Recordings | 0 |

By composer: Alkan 4 · Scriabin 8 · Rameau 9 (3 clavecin + 6 numbers from *Hippolyte et Aricie*) · Couperin 15 (8 préludes + allemande from *L'Art de toucher le clavecin*, plus 6 motets) · Buxtehude 13 (organ/chorale, BuxWV 4 as one cantata row, Membra Jesu nostri as 7 movement rows) · Gesualdo 1 · Franck 2 · Reger 13 (Op. 42 sonatas split by movement, plus two chorales and the 1913 arrangement *Untreue*) · Bruckner 1.

`scripts/sync_site_data.py` `COMPOSER_ERA` now forces Rameau to Baroque (death year 1764 would otherwise land in Classical), Gesualdo and Byrd to Renaissance, and Balakirev to Romantic. Byrd and Balakirev have no row yet; the overrides are there for the next file that clears the licence check.

## Licence method

Every row is a Mutopia piece whose listing and LilyPond header were both read. PD rows quote the header line "Public Domain" and Mutopia's statement that the contributor dedicated the edition to the public domain (print, sell, change, distribute, record, perform). CC BY rows name the typesetter. CC BY-SA rows say a render of that edition stays share-alike.

Mutopia's legal page links the retired Creative Commons public-domain deed. That URL is not copied into `legal_notes` (the site chips "Retired PD dedication" when the deed path appears). Same treatment as the existing Mutopia Bach rows, which stay `clean`.

*Untreue* is Friedrich Glück's 1814 song in Max Reger's 1913 arrangement. The composer field is Max Reger. Catalog is `arr. 1913`, not a fake opus. Both the song and the arrangement are public domain; the edition is CC BY 4.0 (Klaus Rettinghaus).

Franck FWV 30 on Mutopia is the prélude only, not the fugue or the variation. Ave Maria is the E minor original, FWV 62.

Reger sonata 2's Mutopia opus field says "Heft 1 No. 1". The composer header says Heft 1 No. 2. The row uses No. 2.

Movement MIDI order follows LilyPond `\score` / `\midi` order (first block is the unnumbered `.mid`, then `-1`, `-2`, …). Hippolyte indexes used: ouverture 0 and 1, marche 7, tonnerre 20, Rossignols 103, chaconne 104.

## Top picks for video

- **Alkan, Chanson de la folle au bord de la mer, Op. 31 No. 8** — suspended, bare, and strange. Share-alike edition.
- **Alkan, Toccatina, Op. 75** — quasi prestissimo perpetual motion. Share-alike.
- **Scriabin, Etude Op. 2 No. 1** and **Prelude Op. 11 No. 1** — public-domain editions. The etude is the singing one; the prelude is the agitated C major.
- **Rameau, Les sauvages** and **Tambourin** — short harpsichord hits. **Rossignols amoureux** and the **chaconne** from *Hippolyte* (RCT 43) when a longer operatic cue is needed. Those four opera numbers, plus the two ouverture parts and the marche, are CC BY 3.0 (Nicolas Sceaux).
- **Buxtehude, Toccata BuxWV 155** (PD) and any movement of **Membra Jesu nostri, BuxWV 75** (share-alike). BuxWV 4 is one row: the preview is the opening chorus; the mids zip has all five sections.
- **Franck, Prélude from Prélude, fugue et variation, FWV 30** — long organ line, PD edition.
- **Bruckner, Perger Präludium, WAB 129** — a short organ prelude in C, not a symphony. Share-alike (Sam Bivens).

## Cross-audit (Bach slice)

Spot-check on 2026-10-09, not a full re-read of all 170 rows.

- Mutopia piece 29 (Violin Concerto BWV 1042) still says Copyright: Public Domain. The three local MIDIs match the movement titles: I E major 2/2, II C-sharp minor 3/4 (the Adagio), III E major 3/8.
- Mutopia piece 1136 (Brandenburg Concerto No. 1, first movement) still says Creative Commons Attribution 3.0, typesetter Ben Stewart. That matches `bach_bwv1046_brandenburg1_1_allegro`.
- Claude's note on the retired public-domain deed matches the policy above. I did not reopen the Bach `.ly` headers.

## Gaps (not forced into the CSV)

- **Bruckner symphonies.** Mutopia has only WAB 129. IMSLP Symphony No. 7 (WAB 107) has PDF scans and a CC BY-NC DigitalScores file, and zero synthesized/MIDI files. Haas/Nowak critical editions are not clean. Kunstderfuge sequences are copyrighted by the sequencers and were not used. Wikimedia Commons only had two short rhythm samples under an individual copyright.
- **Byrd, Ave verum corpus, T 92.** The IMSLP work page shows file #916358 (MusicXML, Meg Noah, 2024) tagged Creative Commons Zero 1.0, and file #611815 (LilyPond) tagged CC BY-NC 4.0. The NC file was not downloaded. The CC0 zip did not download: IMSLP's image host answers with a JavaScript bot check and no cookie bypass worked from this environment. No row until the file itself is in hand.
- **Frescobaldi, Busoni, Godowsky, Lyapunov, Balakirev:** Mutopia composer searches returned no pieces. No other editable file was verified. **Godowsky rule, if a file appears later:** he died in 1938, so life+70 territories have been clear since 2009. In the US, publication in 1930 entered the public domain on 1 January 2026. A US publication from 1931 onward is still in term on this date (2026-10-09) and must be flagged, not marked clean.
- **Medtner** (d. 1951) and **Sorabji** are excluded. Not public domain.
- **Couperin, Les Barricades mystérieuses** (and Tic-toc-choc, Les Folies françoises): not on Mutopia. *Les Fêtes de Ramire* (Mutopia 1035, CC BY 3.0) is 53 fragments and was skipped as filler.
- **Franck, Panis angelicus:** not on Mutopia.
- **Gesualdo, Moro lasso:** not in this Mutopia set. *Dolcissima mia vita* is the one verified madrigal.
- OpenScore Lieder has none of these composers. MuseScore.com was not used. CPDL's API returned 403.

## Preview

`python3 scripts/make_preview.py --midi files/scores/<id>.mid --start 0 --out previews/<id>.mp3` with FluidR3_GM. Start is 0 because the chosen themes open the piece. All 66 files are distinct, about 15.05 s, 192 kbps.
