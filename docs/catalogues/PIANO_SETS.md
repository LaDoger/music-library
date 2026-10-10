# Top piano repertoire: complete sets

Priority track (LaDoger, 2026-10-10): fill complete sets, not single pieces. Counts from the live catalog after IMSLP run 1 via `.tmp/imslp1/piano_sets.py`-style title/catalogue regex (heuristic: a set at 0 may have pieces titled without Op./No. numbers, e.g. Schubert; verify before importing).
See OMR_QUEUE.md for Debussy/Ravel/Satie/Scriabin/Brahms sets.

| Set | Present | Missing |
|-----|---------|---------|
| Chopin Études Op.10 | 9/12 | No. 2, No. 7, No. 9 |
| Chopin Études Op.25 | 9/12 | No. 1, No. 9, No. 10 |
| Chopin Préludes Op.28 | 15/24 | No. 2, No. 5, No. 6, No. 9, No. 10, No. 11, No. 14, No. 17, No. 22 |
| Chopin 4 Ballades | 3/4 | No. 3 |
| Chopin 4 Scherzi | 2/4 | No. 1, No. 3 |
| Chopin Nocturnes Op.9 | 2/3 | No. 3 |
| Chopin Nocturnes Op.27 | 1/2 | No. 1 |
| Chopin Nocturnes Op.48 | 1/2 | No. 2 |
| Chopin Waltzes Op.64 | 2/3 | No. 3 |
| Chopin Waltzes Op.34 | 0/3 | No. 1, No. 2, No. 3 |
| Beethoven Sonata 8 Pathétique Op.13 | COMPLETE | - |
| Beethoven Sonata 14 Moonlight Op.27/2 | COMPLETE | - |
| Beethoven Sonata 23 Appassionata Op.57 | COMPLETE | - |
| Bach WTC Book I BWV 846-869 | 20/24 | BWV 852, BWV 863, BWV 866, BWV 867 |
| Bach Goldberg Variations BWV 988 | COMPLETE | - |
| Schumann Kinderszenen Op.15 | 1/13 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6, No. 8, No. 9, No. 10, No. 11, No. 12, No. 13 |
| Schumann Carnaval Op.9 | COMPLETE | - |
| Schubert Impromptus D.899 | 0/4 | No. 1, No. 2, No. 3, No. 4 |
| Schubert Impromptus D.935 | 0/4 | No. 1, No. 2, No. 3, No. 4 |
| Schubert Moments musicaux D.780 | 0/6 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6 |
| Mendelssohn Songs without Words Op.19b | 1/6 | No. 1, No. 2, No. 3, No. 4, No. 5 |
| Mendelssohn Songs without Words Op.62 | 0/6 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6 |
| Liszt Consolations S.172 | 1/6 | No. 2, No. 3, No. 4, No. 5, No. 6 |
| Liszt Liebesträume S.541 | 1/3 | No. 1, No. 2 |
| Mozart Sonata K.331 | COMPLETE | - |
| Grieg Lyric Pieces Op.12 | 2/8 | No. 2, No. 3, No. 4, No. 6, No. 7, No. 8 |
| Tchaikovsky The Seasons Op.37a | 2/12 | January, February, April, May, June, July, September, October, November, December |
| Rachmaninoff Preludes Op.23 | 1/10 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6, No. 7, No. 8, No. 9 |
| Rachmaninoff Preludes Op.32 | 1/13 | No. 1, No. 2, No. 3, No. 5, No. 6, No. 7, No. 8, No. 9, No. 10, No. 11, No. 12, No. 13 |
| Rachmaninoff Études-tableaux Op.33 | 0/8 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6, No. 7, No. 8 |
| Rachmaninoff Études-tableaux Op.39 | 1/9 | No. 1, No. 3, No. 4, No. 5, No. 6, No. 7, No. 8, No. 9 |
| Brahms Fantasien Op.116 | 2/7 | No. 1, No. 3, No. 5, No. 6, No. 7 |
| Brahms Intermezzi Op.117 | 0/3 | No. 1, No. 2, No. 3 |
| Brahms Klavierstücke Op.118 | 1/6 | No. 1, No. 3, No. 4, No. 5, No. 6 |
| Brahms Klavierstücke Op.119 | 0/4 | No. 1, No. 2, No. 3, No. 4 |

## Best clean source to try per set (licence must be checked per file)
- Chopin Études/Préludes/Ballades/Scherzi/Nocturnes/Waltzes, Bach WTC I gaps, Schumann Kinderszenen, Schubert D.899/D.935/D.780, Mendelssohn Lieder ohne Worte, Grieg Op.12: **Mutopia** first (many are Public Domain or CC BY; skip CC BY-SA unless LaDoger approves the share-alike rows), then **PDMX** rows with no_license_conflict, then **IMSLP** user MIDI/MusicXML/.mscz files tagged CC0/CC BY (human/browser fetch, same flow as this run).
- Liszt Consolations/Liebesträume, Tchaikovsky Seasons: PDMX (well represented) then IMSLP CC BY engravings.
- Rachmaninoff Preludes Op.23/32, Études-tableaux Op.33/39 (US-PD-only, published 1903-1920): IMSLP CC BY synthesized MIDIs exist for some (Op.23/10, Op.32/4 imported); Mutopia has Op.23 under CC BY-SA (pending decision).
- Brahms Opp.116-119: Mutopia/IMSLP; OMR if none clean.
Nothing imported for this track in this run.
