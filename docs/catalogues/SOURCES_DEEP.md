# Deep-source log (depth run 1, 2026-10-10)

What each score source can still give for the featured composers (`featured_rank` 1-2 in
`scripts/featured_composers.json`), what was imported, and what is blocked. Numbers are from the
run on 2026-10-10 (live count 9,221 → 9,330).

## Summary by source

| source | status | per-file licence check | yield for featured composers |
|---|---|---|---|
| PDMX (Zenodo 15571083), `subset:no_license_conflict`, PD / CC0 | **used, exhausted** | yes (`license` column per file) | Pool for rank 1-2 composers: Ravel 52, Debussy 78, Satie 52, Mahler 23, Bruckner 23, Wagner 63, R. Strauss 12, Elgar 29, Holst 37, Rachmaninoff 43, Scriabin 14, Tchaikovsky 77, Dvořák 46, Mussorgsky 24, Rimsky-Korsakov 23, Berlioz 7, Grieg 65, Saint-Saëns 46, Verdi 34, Fauré 33, Liszt 58 clean rows. Almost all were already live or are third-party arrangements (brass/wind/jazz/choir "arr."). Signature-gap pass (`import_pdmx_signature_gaps.py`): 9 rows, 3 net new works (Bruckner Locus iste + Christus factus est, Saint-Saëns concertos, Liszt Venezia e Napoli). |
| PDMX, US-PD-only composers | **new** (`import_depth_us_pd.py`) | yes + checklist publication year ≤ 1930 | 108 rows from Ravel, R. Strauss, Elgar, Holst, Rachmaninoff checklists (`docs/catalogues/*.csv`): +80 live items. |
| OpenScore Lieder / StringQuartets (GitHub, CC0) | **mirrored fully**; those are the only two OpenScore repos (`api.github.com/orgs/OpenScore/repos`) | repo CC0 | Debussy 20 songs + quartet, Satie 17 songs, Mahler 10 songs, Wagner 5, Strauss 4 + quartet, Elgar 10 + quartet, Dvořák 18 quartets, Fauré 20: all candidates already imported or folded as `other_editions`. OpenScore orchestral/piano scores exist only on musescore.com (login, forbidden). |
| Mutopia | **used**; rest is CC BY-SA | yes (`editable_license`) | Remaining unimported pieces are CC BY-SA (excluded by rule): Satie 13, Mussorgsky 16 (Pictures at an Exhibition etc.), Rachmaninoff 10 (Op. 23 Preludes), Scriabin 6, Rimsky-Korsakov 4, Debussy 3, Grieg 2. **Decision for LaDoger:** allowing BY-SA scores as `sharealike` rows (the site already has that licence class) would add about 55 featured-composer works. Not done. |
| music21 corpus | **scanned, nothing new** (`scan_music21_rights.py`) | `<rights>` element per file | 654 MusicXML files scanned: 561 carry no rights line (Bach chorales included: no per-file PD header, so not importable), 12 other (copyright / CC BY-SA / all rights reserved), 6 PD/CC0/CC BY (Lusitano, Weber, Corelli already live; Johnson, Foster, Liliuokalani non-featured). 75 raw-GitHub fetch errors (large files). Corpus-level terms: "some encodings may not be used commercially" (`docs/licences/music21_corpus.md`). |
| CCARH / Humdrum / KernScores | **excluded** (`docs/licences/kernscores.md`) | repo LICENSE files are CC BY-NC-SA or absent | 0. |
| Wikimedia Commons MIDI | **new** (`import_commons_midi.py`, hand-vetted) | Commons licence tag via API (`Public domain` / `CC0` only) | 32 complete pieces ≥ 60 s imported (28 survive dedupe): Debussy Children's Corner 2-5, Grieg Holberg Suite + 2 Lyric Pieces, Dvořák Humoresque, Liszt Valse-Impromptu, Mussorgsky Pictures (2), Satie Ogives 1-4, Scriabin Fantasy Op. 28, Sonatas 5 and 9, 8 études/preludes/mazurkas, Wagner Kaisermarsch finale. Everything else found is a 3-20 s analysis excerpt (Wikipedia chord examples, 100+ Ring leitmotif fragments by Peter Billam, PD) or CC BY-SA / GPL: skipped (quality bar). |
| IMSLP user MIDI / MusicXML / .mscz | **listing only** (`imslp_scan.py`) | per-file `Copyright=` field from the work page wikitext | 116 PD/CC0/CC BY files of 179 found (below). File downloads are behind a captcha bot check ("Click the button below to verify you are human"). This run does not script around it; usable files are listed for a human to fetch. |
| CPDL (choral) | not scanned | edition licences are mixed ("CPDL licence", CC BY-NC...) | Not on the approved source list; Bruckner motets would be the main prize. Needs LaDoger's call on the CPDL licence. |
| Wikifonia-era CC sets, ABC / folk | excluded | policy (`briefs/SOURCES_POLICY.md`) | 0. |
| MuseScore.com | forbidden (login) | n/a | 0. |

## IMSLP candidates (manual download list)

Scan 2026-10-10 (`scripts/bulk/imslp_scan.py`: category listing + work-page wikitext, ~1 request/s per process, two processes, no file URL requested; both `imslpfile` and `imslpaudio` blocks are parsed). **179 MIDI / MusicXML / .mscz files found on 1068 work pages; 116 carry a PD / CC0 / CC BY tag**, the other 63 are BY-SA or NC (WIMA project files are NC).

| IMSLP category | work pages scanned | files found | PD / CC0 / CC BY |
|---|---:|---:|---:|
| Ravel, Maurice | 84 | 2 | 2 |
| Satie, Erik | 84 | 34 | 5 |
| Debussy, Claude | 107 | 17 | 10 |
| Mahler, Gustav | 22 | 2 | 2 |
| Bruckner, Anton | 152 | 7 | 0 |
| Wagner, Richard | 55 | 3 | 2 |
| Scriabin, Aleksandr | 91 | 6 | 4 |
| Elgar, Edward | 193 | 95 | 80 |
| Strauss, Richard | 127 | 3 | 1 |
| Holst, Gustav | 72 | 4 | 4 |
| Rachmaninoff, Sergei | 81 | 6 | 6 |

Downloads are gated: requesting a file URL returns an IMSLP "Bot Check" page ("Click the button below to verify you are human"). This run does **not** script around it. The usable files are in `docs/catalogues/imslp_candidates.csv` for a human to fetch (page URL per file). Highlights (everything except the 80 Elgar files, 76 of them are CC BY 4.0 MIDI renderings of a third party's orchestrations ("Morrison") of Elgar songs: arrangements, not Elgar's own scoring, so not a priority):

| composer | work | file | licence |
|---|---|---|---|
| Ravel | À la manière de Borodine, M.63/1 | `PMLP7950-maniere_de_Borodine.mid` | CC Attribution 4.0 |
| Ravel | Daphnis et Chloé Suite No.2, M.57b | `PMLP80636-08_-_Daphnis_et_Chloé_Suite_No_2_-_Percussion.mscz` | CC Zero 1.0 |
| Satie | Gnossiennes | `PMLP7506-Gnossienne-1-quintet.mscz` | CC Attribution 4.0 |
| Satie | Gnossiennes | `PMLP7506-Gnossienne-1-quartet.mscz` | CC Attribution 4.0 |
| Satie | 3 Gymnopédies | `PMLP4215-Gymnopedie-1.mscz` | CC Attribution 4.0 |
| Satie | Je te veux | `PMLP19702-Je-te-veux.mscz` | CC Attribution 4.0 |
| Satie | Messe des pauvres | `PMLP9667-Satie_Prière_pour_le_salut_de_mon_âme.mscz` | CC Attribution 4.0 |
| Debussy | 2 Arabesques, CD 74 | `PMLP2383-Arabesque-1-Debussy.mscz` | CC Attribution 4.0 |
| Debussy | 2 Arabesques, CD 74 | `PMLP2383-arabesque_no2.mscz` | CC Attribution 4.0 |
| Debussy | 2 Arabesques, CD 74 | `PMLP2383-Arabesque-2-Debussy.mscz` | CC Attribution 4.0 |
| Debussy | D'un cahier d'esquisses, CD 112 | `PMLP9130-cahier_score.mid` | CC Attribution 4.0 |
| Debussy | Children's Corner, CD 119 | `PMLP2387-Golliwoggs-Cake-Walk.mscz` | CC Attribution 4.0 |
| Debussy | Préludes, Livre 1, CD 125 | `PMLP2394-Des_pas_sur_la_neige.mid` | CC Attribution 4.0 |
| Debussy | Préludes, Livre 1, CD 125 | `PMLP2394-cathedral.mid` | CC Attribution 4.0 |
| Debussy | Suite bergamasque, CD 82 | `PMLP2397-clair_de_lune.mscz` | CC Attribution 4.0 |
| Debussy | Suite bergamasque, CD 82 | `PMLP2397-Clair-de-Lune.mscz` | CC Attribution 4.0 |
| Debussy | Suite bergamasque, CD 82 | `PMLP2397-Clair-de-Lune-in-C.mscz` | CC Attribution 4.0 |
| Mahler | Symphony No.1, GMW 11 | `PMLP15427-Symphony-1-2-Mahler.mscz` | CC Attribution 4.0 |
| Mahler | Symphony No.4, GMW 37 | `PMLP58739-Mahler4FirstNormalTuning.mxl` | CC Zero 1.0 |
| Wagner | Götterdämmerung, WWV 86D | `PMLP34545-Death_of_Siegfried.mscz` | CC Zero 1.0 |
| Wagner | Tannhäuser, WWV 70 | `PMLP21243-Tannhauser_Overture_Selections.mscz` | CC Zero 1.0 |
| Scriabin | 2 Impromptus, Op.10 | `PMLP25663-Impromptu.mid` | CC Attribution 4.0 |
| Scriabin | Prelude and Nocturne for the Left Hand, Op.9 | `PMLP20227-Prelude.mid` | CC Attribution 4.0 |
| Scriabin | Vers la flamme, Op.72 | `PMLP8451-Vers_la_flamme.mscz` | CC Zero 1.0 |
| Scriabin | Vers la flamme, Op.72 | `PMLP8451-vers_la_flamme_orchestra.mscz` | CC Attribution 4.0 |
| Strauss | Capriccio, Op.85 | `PMLP56075-Sonett_from_Capriccio.mid` | CC Zero 1.0 |
| Holst | Ave Maria, Op.9b | `PMLP406958-Holst_ave_maria.mid` | CC Attribution 4.0 |
| Holst | I vow to thee, my country, H.148 | `PMLP367232-Psalm98Sco.mid` | CC Attribution 3.0 |
| Holst | St. Paul's Suite, Op.29 No.2 | `PMLP48902-Saint-Pauls-Suite.mscz` | CC Attribution 4.0 |
| Holst | St. Paul's Suite, Op.29 No.2 | `PMLP48902-Saint-Pauls-Suite-Quintet.mscz` | CC Attribution 4.0 |
| Rachmaninoff | Isle of the Dead, Op.29 | `PMLP45655-Die_Toteninsel.mscz` | CC Zero 1.0 |
| Rachmaninoff | Morceaux de fantaisie, Op.3 | `PMLP5664-rachmaninoff_prelude_in_c_sharp_minor.mscz` | CC Attribution 4.0 |
| Rachmaninoff | 10 Preludes, Op.23 | `PMLP2017-Op._23,_No._10.mid` | CC Attribution 4.0 |
| Rachmaninoff | 13 Preludes, Op.32 | `PMLP2018-Op.32,_No.4.mid` | CC Attribution 4.0 |
| Rachmaninoff | Romance in A minor | `PMLP1312694-Serguéi_Rachmaninoff_-_Romance_in_A_Minor.mid` | CC Zero 1.0 |
| Rachmaninoff | Suite No.2, Op.17 | `PMLP8797-III_Romance.mid` | CC Attribution 4.0 |

`.mscz` files are MuseScore projects uploaded to IMSLP by users (not MuseScore.com downloads); `mscore3` can convert them to MIDI. `.mxl` = compressed MusicXML. Bruckner: the 7 files found are all NC.

## Composer-by-composer notes (rank 1-2)

* **Ravel** (US-PD-only, checklist `ravel.csv`): PDMX gave 19 of 47 in-scope works; no Mutopia/OpenScore Ravel; IMSLP lists CC0 Daphnis Suite 2 percussion part only. Gaps: Rapsodie espagnole, Introduction et Allegro, Piano Trio, Tzigane, Violin Sonata 2, Valses nobles, Miroirs 1/2/4/5, Ondine, Scarbo, song cycles, stage works.
* **Debussy**: 71 live items; missing La mer, Faune, Nocturnes, Estampes, Syrinx, Images, Pelléas in clean sources (Commons has only 3-20 s excerpts of Syrinx, Faune, Cathédrale engloutie, Fille aux cheveux de lin).
* **Satie**: Gymnopédies/Gnossiennes live; Mutopia has 13 more but BY-SA.
* **Mahler**: 28 live; IMSLP Symphony 4 (CC0 .mxl) and Symphony 1 (CC BY .mscz) are the only clean encodings found (manual download).
* **Bruckner**: 18 live (motets from PDMX); symphonies absent from every clean source. IMSLP WIMA files are NC.
* **Wagner**: 48 live; strong on title match (12/12 signature works) but only 17 distinct WWV numbers.
* **R. Strauss, Elgar, Holst, Rachmaninoff**: checklists in `docs/catalogues/`; coverage 23% / 23% / 41% / 55%.
* **Scriabin**: +9 from Commons (PD/CC0), including Sonatas 5 and 9.

## Re-run

```
python3 scripts/bulk/scan_music21_rights.py            # ~1 min
python3 scripts/bulk/imslp_scan.py "Ravel, Maurice" --max-pages 350   # ~1 req/s, resumable cache .tmp/depth1/imslp
python3 scripts/bulk/import_commons_midi.py            # edit ACCEPT in the script (or .tmp/depth1/commons_accept_extra.json)
python3 scripts/bulk/import_pdmx_signature_gaps.py     # ~3 min (scans PDMX.csv)
```
