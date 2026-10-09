# Music library

Searchable public-domain / Creative Commons classical library for video work (Michael Saylor / Strategy style edits), with **15-second audition previews** and downloadable **editable scores** (MIDI / MusicXML / LilyPond).

**Live site:** https://ladoger.github.io/music-library/  
**Repo:** https://github.com/LaDoger/music-library  
**Full recordings:** GitHub Release [`audio-v1`](https://github.com/LaDoger/music-library/releases/tag/audio-v1) (not in git — too large)

## Goal
Take any major-composer work (starting with the full Bach BWV catalogue), find a clean editable score, and re-genre / render it for video. **Editable scores are the priority.** Recordings are secondary.


75 classical pieces (or movements) collected for commercial and public social video, such as Michael Saylor / Strategy posts on X.
Every row has a local recording or editable score, plus a 15-second audition MP3.

| | count |
|---|---|
| Pieces (rows) | 75 |
| Rows with a downloaded editable score | 30 |
| Rows with a downloaded recording | 64 |
| Preview MP3s | 75 |
| `verified=yes` (license text seen on the source page) | 71 |

The master list is **`library.csv`** (columns are defined in `SCHEMA.md`). `library.xlsx` holds the same data with a frozen header and filters.

## Folder layout

```
library.csv / library.xlsx   master list, one row per piece/movement
SCHEMA.md                    column definitions and license policy
README.md                    this file
STATUS.txt                   build log, one line per stage
files/audio/<id>.<ext>       full recordings (FLAC / OGG / Opus / MP3 originals, not re-encoded)
files/scores/<id>.<ext>      editable scores: MIDI, LilyPond (.ly), PDF, Mutopia zips
                             (<id>_lilypond.zip / <id>_midi.zip; shared sets like
                             mussorgsky_pictures_at_an_exhibition-*.zip, dvorak_new_world-*.zip)
previews/<id>.mp3            15 s audition clips
previews/index.html          audition page (all clips, mood tags, license line, filter box)
parts/                       per-agent source CSVs and summaries, MERGE_NOTES.md (merge log)
logs/                        license evidence, source pages, download manifests, rename map
scripts/                     make_preview.py, build_preview_index.py, merge_library.py, Commons helpers
```

Files are named by `id`, which already contains the composer, catalogue number and short title (e.g. `beethoven_op67_symphony5.flac`).
A few codex entries also keep their LilyPond source (`.ly`) or the original ALAC file (`chopin_op9_2_nocturne.m4a`) next to the file the CSV points to.

## How to audition

1. Open `previews/index.html` in a browser. Opening it straight from disk works; there are no external dependencies.
2. Type in the filter box to search by composer, title or mood (e.g. `epic`, `dark`, `calm`, `triumphant`).
3. Each card shows the mood tags, the tempo/energy, who added it, and the recording and score licenses. Rows that are not fully verified are labelled.
4. When you like a clip, find its `id` in `library.csv`. Check `legal_notes` and use the full file in `files/audio/`. Use `notable_excerpt` to find the strongest part.

Every preview is 15 s, MP3 192 kbps, 44.1 kHz stereo, normalised to about -16 LUFS (measured -16.9 to -15.1), with 0.35 s / 0.45 s fades.
Previews are cut from the licensed recording where there is one. Otherwise they are our own FluidSynth renders of the licensed MIDI.
The MIDI renders are bach_bwv1007_prelude, bach_bwv1068_air, debussy_arabesque_1, debussy_clair_de_lune, faure_*, handel_hwv56_hallelujah, mozart_k525_nachtmusik, pachelbel_canon_d and satie_gnossienne_1.
They are not human performances.

## License rules

A public-domain composition does not mean a public-domain recording. Read **both** `recording_license` and `editable_license`, and treat `legal_notes` as binding.

**1. Safe: commercial or social use, no attribution needed.**
- The composition is PD, and the recording is PD, CC0, PDM or US-government.
- Or: your own render from a PD/CC0 score.
- Examples: Musopen PD/CC0 releases, and US Marine, Army, Navy or Air Force Band recordings.
- US-government recordings are PD in the US. Other countries do not always agree; the row notes say so.
- Courtesy credit is still recommended where the source asks for it: Beethoven 5 (Skidmore/Musopen), Moonlight I (Paul Pitman/Musopen), Moonlight III and Träumerei (Musopen).

**2. Safe with attribution (CC BY or Commons "attribution").** Put the credit in the post or video description.

| id | credit |
|---|---|
| bach_bwv565_toccata | Norbert Schenk (organ), CC BY 4.0 |
| rstrauss_zarathustra_sunrise | Kevin MacLeod (incompetech.com), CC BY 3.0 |
| schubert_d328_erlkonig | recording credited on source page, CC BY 3.0 |
| holst_planets_jupiter | Skidmore College Orchestra / Musopen (Commons attribution template) |
| pachelbel_canon_d | preview is a render of a CC BY 4.0 Mutopia edition (Michael Fischer v. Mollard / Mutopia) |
| mussorgsky_night_on_bald_mountain | **score only** CC BY 3.0. The recording itself is PD. |

**3. Flag only: do not treat as clean.**
- *Share-alike recordings:*
  - mussorgsky_pictures_baba_yaga (CC BY-SA 2.0 DE)
  - saintsaens_carnival_aquarium (CC BY-SA 2.0)
  - wagner_tristan_prelude (EFF Open Audio License, which works like BY-SA)
  - verdi_requiem_dies_irae (CC BY-SA 4.0, and also `unverified`)
- *Share-alike scores:* the matching recordings are PD/CC0, so only score renders are affected.
  - bizet_carmen_toreador (Carmen Prelude score)
  - dvorak_new_world_largo and dvorak_new_world_finale
  - mussorgsky_pictures_* (promenade, great_gate_kiev, baba_yaga)
  - strauss2_blue_danube (Mutopia MIDI; the preview uses the PD Marine Band recording)
  - satie_gnossienne_1 and faure_pavane: here the **preview itself** is a render of the BY-SA edition.
- *Unverified* (could not confirm the recording's clearance): tchaikovsky_swan_lake_act2_scene, rimskykorsakov_scheherazade_sea, brahms_hungarian_dance_5, verdi_requiem_dies_irae.
- *Composer-term caveats:*
  - Holst (d. 1934, The Planets): PD in the US and in life+70/life+80 countries; not PD where terms run longer (e.g. life+100 in Mexico). The Mars file is only a 61 s excerpt.
  - Rachmaninoff (d. 1943): PD in life+70 countries. Both works were published before 1926, so both are PD in the US.
  - R. Strauss (d. 1949): Zarathustra (1896) is PD in the US and in life+70 countries since 2020.
  - Elgar (d. 1934): Pomp and Circumstance No. 1 (1901) is PD in the US and in life+70 countries.
- *Arrangements:* military-band arrangements with a non-government arranger carry low but non-zero risk. This covers liszt_hungarian_rhapsody_2 and tchaikovsky_nutcracker_waltz_of_flowers.
- *Other:*
  - offenbach_orpheus_cancan uses the retired CC PD dedication, which may not hold outside the US.
  - Vivaldi uses a PDM-owner declaration, not CC0.
  - ravel_pavane is a virtual-piano render.

**4. Excluded (not in the library):**
- Composers: Orff, Prokofiev, Shostakovich, Stravinsky.
- Ravel's Boléro (disputed).
- Anything CC BY-NC, all-rights-reserved, or with a guessed license.
- Recordings tagged PD-EU-audio only, which are still protected in the US (e.g. Barbirolli's 1947 Nimrod).

## Top 15 picks for Saylor-style videos

All picks are `verified=yes`. Picks 1–11 and 14 are fully clean. Picks 12, 13 and 15 need a credit (Moonlight I is a courtesy credit). Picks 3 and 10 are PD in the US as government works.

| # | id | why |
|---|---|---|
| 1 | grieg_peer_gynt_mountain_king | Slow-to-frantic build: ideal for "adoption curve" or rising-price montages. PD recording and PD score. |
| 2 | beethoven_op67_symphony5 | The fate motif, a four-note thesis statement for bold announcements. PD (courtesy credit Skidmore/Musopen). |
| 3 | tchaikovsky_1812_overture | Cannons and bells finale for all-time-high or "victory" moments. US Army Band, PD-US. |
| 4 | mussorgsky_pictures_great_gate_kiev | Monumental, cathedral-like grandeur for "digital capital / monument" visuals. PD. |
| 5 | dvorak_new_world_finale | Brass march of progress, "the new world" message built in. PD recording. |
| 6 | beethoven_op84_egmont | Victorious coda in a 48/24 FLAC. Triumphant closer after a struggle. PD. |
| 7 | mozart_k550_symphony40 | Restless urgency under analytical voice-over, e.g. "inflation is eroding your money". PD FLAC. |
| 8 | chopin_op10_12_revolutionary | Defiant, stormy piano for "revolution in money" lines. PD, named performer. |
| 9 | vivaldi_rv315_summer_storm | Furious strings for volatility or market-storm cuts. PDM-owner declaration. |
| 10 | verdi_aida_triumphal_march | Ceremonial trumpets for corporate milestones and treasury reveals. US Marine Band, PD-US. |
| 11 | tchaikovsky_piano_concerto_1 | Huge opening chords for a grand, confident intro. CC0 (mono). |
| 12 | bach_bwv565_toccata | The most recognisable dramatic organ opening there is. CC BY 4.0, credit Norbert Schenk. |
| 13 | rstrauss_zarathustra_sunrise | "2001" sunrise awe for dawn-of-a-new-era reveals. CC BY 3.0, credit Kevin MacLeod. |
| 14 | mussorgsky_night_on_bald_mountain | Dark and chaotic, for "fiat collapse" or bear-market segments. PD recording. |
| 15 | beethoven_op27_2_moonlight1 | Calm, mysterious contrast for reflective long-term-thinking passages. PD (courtesy credit Paul Pitman/Musopen). |

Honourable mentions:
- holst_planets_mars: relentless and martial, CC0, but carries the Holst territorial flag and is only 61 s.
- mendelssohn_op26_hebrides: mysterious, majestic; PD FLAC.
- handel_hwv349_hornpipe: regal; US Marine Band.
- elgar_pomp_circumstance_1: ceremonial; US Marine Band.
- chopin_op9_2_nocturne: calm and polished, CC0.

## How to re-render previews

```bash
cd /workspace/music/library
# from a recording (start as seconds or MM:SS)
python3 scripts/make_preview.py --audio files/audio/<id>.<ext> --start 1:42 --out previews/<id>.mp3
# from a MIDI score (FluidSynth + /usr/share/sounds/sf2/FluidR3_GM.sf2)
python3 scripts/make_preview.py --midi files/scores/<id>.mid --start 0 --out previews/<id>.mp3
# rebuild the audition page from library.csv
python3 scripts/build_preview_index.py
```

`make_preview.py` cuts 15 s and applies the fades. It then normalises in two passes (loudnorm measure, then linear apply at -16 LUFS / -1.5 dBTP) and checks the encoded MP3, correcting the gain if it misses by more than 0.5 LU.
If you change the clip, update `notable_excerpt` in `library.csv` too.

To rebuild `library.csv` / `library.xlsx` from the part files, run `python3 scripts/merge_library.py`.
This normalises filenames, re-renders any missing or off-loudness previews, and is safe to re-run.
It overwrites `library.csv`, so make manual CSV edits in `parts/*_rows.csv`, or don't re-run the merge after editing `library.csv`.

## MuseScore.com: left for later

MuseScore.com downloads need a login, so nothing was downloaded from there, and **no `musescore_url` values were filled in** (the column is empty in every row).
If you later log in and want editable files, these are the pieces with no local editable score. Look them up and record the page URL in `musescore_url` first:
- Holst Mars and Jupiter
- Mozart Symphony 40
- Beethoven Egmont and Moonlight I and III
- Mendelssohn Hebrides
- Vivaldi Spring and Summer
- Handel Water Music
- Tchaikovsky (all)
- Wagner (all)
- Rachmaninoff
- Saint-Saëns
- Liszt
- Smetana, Borodin and Mahler

Check each MuseScore score's own license. Many user uploads are all-rights-reserved or non-commercial, which this library excludes. Prefer the CC0 OpenScore editions.
