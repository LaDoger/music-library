# Top piano repertoire: complete sets

Priority track (LaDoger, 2026-10-10): fill complete sets, not single pieces. Counts from the live catalog after IMSLP run 1 via `.tmp/imslp1/piano_sets.py`-style title/catalogue regex (heuristic: a set at 0 may have pieces titled without Op./No. numbers, e.g. Schubert; verify before importing).
See OMR_QUEUE.md for Debussy/Ravel/Satie/Scriabin/Brahms sets.

Counts regenerated 2026-10-10 by `python3 scripts/bulk/set_coverage.py` (new matcher `scripts/bulk/piano_set_defs.py`: titles without numbers, D/Op. aliases e.g. Schubert D.899 = Op.90, nicknames, Kinderszenen/Seasons/Debussy titles; arrangements excluded). Fill script: `scripts/bulk/import_piano_sets.py` (batch PS). IMSLP CC BY files for the browser: `imslp_batch_next.csv`.

| Set | Scope | Present | Missing |
|-----|-------|---------|---------|
| Chopin Études Op.10 | PD | 9/12 | No. 2, No. 7, No. 9 |
| Chopin Études Op.25 | PD | 9/12 | No. 1, No. 9, No. 10 |
| Chopin Préludes Op.28 | PD | 16/24 | No. 2, No. 5, No. 6, No. 9, No. 10, No. 14, No. 17, No. 22 |
| Chopin 4 Ballades | PD | COMPLETE | - |
| Chopin 4 Scherzi | PD | 2/4 | No. 1 Op.20, No. 3 Op.39 |
| Chopin Nocturnes Op.9 | PD | 2/3 | No. 3 |
| Chopin Nocturnes Op.15 | PD | 1/3 | No. 1, No. 3 |
| Chopin Nocturnes Op.27 | PD | 1/2 | No. 1 |
| Chopin Nocturnes Op.32 | PD | 0/2 | No. 1, No. 2 |
| Chopin Nocturnes Op.48 | PD | 1/2 | No. 2 |
| Chopin Nocturnes Op.55 | PD | COMPLETE | - |
| Chopin Nocturnes Op.62 | PD | 0/2 | No. 1, No. 2 |
| Chopin Nocturne C# minor (posth.) B.49 | PD | COMPLETE | - |
| Chopin Waltzes Op.18 | PD | COMPLETE | - |
| Chopin Waltzes Op.34 | PD | 0/3 | No. 1, No. 2, No. 3 |
| Chopin Waltzes Op.42 | PD | 0/1 | Waltz in A-flat |
| Chopin Waltzes Op.64 | PD | 2/3 | No. 3 |
| Chopin Waltzes Op.69 | PD | 1/2 | No. 1 |
| Chopin Waltzes Op.70 | PD | 0/3 | No. 1, No. 2, No. 3 |
| Schubert Impromptus D.899 (Op.90) | PD | 1/4 | No. 2, No. 3, No. 4 |
| Schubert Impromptus D.935 (Op.142) | PD | 1/4 | No. 1, No. 3, No. 4 |
| Schubert Moments musicaux D.780 (Op.94) | PD | 1/6 | No. 1, No. 2, No. 4, No. 5, No. 6 |
| Mendelssohn Songs without Words Op.19b | PD | 1/6 | No. 1, No. 2, No. 3, No. 4, No. 5 |
| Mendelssohn Songs without Words Op.30 | PD | 2/6 | No. 2, No. 3, No. 4, No. 5 |
| Mendelssohn Songs without Words Op.62 | PD | 0/6 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6 |
| Mendelssohn Songs without Words Op.67 | PD | 0/6 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6 |
| Schumann Kinderszenen Op.15 | PD | 8/13 | 8 Am Kamin, 9 Ritter vom Steckenpferde, 10 Fast zu ernst, 11 Fürchtenmachen, 13 Der Dichter spricht |
| Brahms Fantasien Op.116 | PD | 2/7 | No. 1, No. 3, No. 5, No. 6, No. 7 |
| Brahms Intermezzi Op.117 | PD | 0/3 | No. 1, No. 2, No. 3 |
| Brahms Klavierstücke Op.118 | PD | 1/6 | No. 1, No. 3, No. 4, No. 5, No. 6 |
| Brahms Klavierstücke Op.119 | PD | 0/4 | No. 1, No. 2, No. 3, No. 4 |
| Tchaikovsky The Seasons Op.37a | PD | 6/12 | April, May, June, July, September, November |
| Grieg Lyric Pieces Op.12 | PD | 2/8 | 2 Waltz, 3 Watchman's Song, 4 Elfin Dance, 6 Norwegian, 7 Album Leaf, 8 National Song |
| Grieg Lyric Pieces Op.43 | PD | 2/6 | 2 Solitary Traveller, 3 In My Native Country, 4 Little Bird, 5 Erotikon |
| Grieg Lyric Pieces Op.65 | PD | 1/6 | No. 1, No. 2, No. 3, No. 4, No. 5 |
| Bach WTC Book I BWV 846-869 | PD | COMPLETE | - |
| Bach WTC Book II BWV 870-893 | PD | COMPLETE | - |
| Beethoven 32 Piano Sonatas | PD | 21/32 | No. 3 Op.2/3, No. 4 Op.7, No. 7 Op.10/3, No. 9 Op.14/1, No. 11 Op.22, No. 12 Op.26, No. 15 Op.28, No. 18 Op.31/3, No. 22 Op.54, No. 28 Op.101, No. 32 Op.111 |
| Liszt Consolations S.172 | PD | 2/6 | No. 2, No. 3, No. 5, No. 6 |
| Liszt Liebesträume S.541 | PD | 1/3 | No. 1, No. 2 |
| Liszt Paganini Études S.141 | PD | 1/6 | No. 1, No. 2, No. 4, No. 5, No. 6 |
| Liszt Hungarian Rhapsodies S.244 (1-19) | PD | 3/19 | No. 1, No. 3, No. 4, No. 5, No. 7, No. 8, No. 9, No. 11, No. 12, No. 13, No. 14, No. 15, No. 16, No. 17, No. 18, No. 19 |
| Debussy Children's Corner L.113 | PD | COMPLETE | - |
| Debussy Suite bergamasque L.75 | PD | COMPLETE | - |
| Debussy Estampes L.100 | PD | 0/3 | Pagodes, La soirée dans Grenade, Jardins sous la pluie |
| Debussy Préludes Book I L.117 | PD | 3/12 | danseuses de delphes, voiles, les sons et les parfums, collines d.anacapri, ce qu.a vu le vent, fille aux cheveux de lin, serenade interrompue, danse de puck, minstrels |
| Debussy Préludes Book II L.123 | PD | 7/12 | puerta del vino, ondine, canope, tierces alternees, feux d.artifice |
| Satie Gymnopédies | PD | COMPLETE | - |
| Satie Gnossiennes 1-6 | PD | 4/6 | No. 5, No. 6 |
| Satie 3 Sarabandes | PD | 0/3 | No. 1, No. 2, No. 3 |
| Scriabin 2 Poèmes Op.32 | PD | 1/2 | No. 2 |
| Scriabin 12 Études Op.8 | PD | 1/12 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6, No. 7, No. 8, No. 9, No. 10, No. 11 |
| Ravel Valses nobles et sentimentales M.61 | US-PD-only | 0/8 | Valse 1, Valse 2, Valse 3, Valse 4, Valse 5, Valse 6, Valse 7, Valse 8 |
| Ravel Le Tombeau de Couperin M.68 | US-PD-only | COMPLETE | - |
| Rachmaninoff Preludes Op.23 | US-PD-only | 1/10 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6, No. 7, No. 8, No. 9 |
| Rachmaninoff Preludes Op.32 | US-PD-only | 1/13 | No. 1, No. 2, No. 3, No. 5, No. 6, No. 7, No. 8, No. 9, No. 10, No. 11, No. 12, No. 13 |

## Best clean source to try per set (licence must be checked per file)
- Chopin Études/Préludes/Ballades/Scherzi/Nocturnes/Waltzes, Bach WTC I gaps, Schumann Kinderszenen, Schubert D.899/D.935/D.780, Mendelssohn Lieder ohne Worte, Grieg Op.12: **Mutopia** first (many are Public Domain or CC BY; skip CC BY-SA unless LaDoger approves the share-alike rows), then **PDMX** rows with no_license_conflict, then **IMSLP** user MIDI/MusicXML/.mscz files tagged CC0/CC BY (human/browser fetch, same flow as this run).
- Liszt Consolations/Liebesträume, Tchaikovsky Seasons: PDMX (well represented) then IMSLP CC BY engravings.
- Rachmaninoff Preludes Op.23/32, Études-tableaux Op.33/39 (US-PD-only, published 1903-1920): IMSLP CC BY synthesized MIDIs exist for some (Op.23/10, Op.32/4 imported); Mutopia has Op.23 under CC BY-SA (pending decision).
- Brahms Opp.116-119: Mutopia/IMSLP; OMR if none clean.
Nothing imported for this track in this run.
