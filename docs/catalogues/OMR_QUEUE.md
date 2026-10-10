# OMR queue: complete sets first (famous piano works)

Rule (LaDoger, 2026-10-10): complete suites over single pieces. OMR only for famous Ravel/Debussy/Satie/Scriabin (plus Brahms Opp. 116-119 sets) movements where no licence-clean MIDI/editable file exists anywhere.
Before OMR, check: live library, IMSLP (docs/catalogues/imslp_candidates.csv, CC0/CC BY only), PDMX no_license_conflict, Mutopia (PD/CC0/CC BY files only; BY-SA needs LaDoger's approval), OpenScore, Commons.
Tool: Audiveris 5.11 (/workspace/music/tools/omr). Ravel = US-PD-only (pub. <=1930). Debussy/Satie/Scriabin/Brahms = PD everywhere.
Completeness = live clean files per movement, computed by `python3 scripts/bulk/set_coverage.py` (title/catalogue regex; a complete set in one file counts as complete). Updated 2026-10-10 11:51 after IMSLP run 1.

| Set | Scope | Present | Movements present (clean files) | Missing |
|-----|-------|---------|------------------|---------|
| Debussy Children's Corner L.113 | PD | 5/6 | 1 Doctor Gradus, 2 Jimbo's Lullaby, 3 Serenade for the Doll, 4 The Snow Is Dancing, 6 Golliwogg's Cakewalk | 5 The Little Shepherd |
| Ravel Le Tombeau de Couperin M.68 | US-PD-only | COMPLETE | complete (6 mvts in one file) | - |
| Ravel Valses nobles et sentimentales M.61 | US-PD-only | 0/8 | - | Valse 1, Valse 2, Valse 3, Valse 4, Valse 5, Valse 6, Valse 7, Valse 8 |
| Scriabin 2 Poèmes Op.32 | PD | 1/2 | No. 1 | No. 2 |
| Brahms 7 Fantasien Op.116 | PD | 2/7 | No. 2, No. 4 | No. 1, No. 3, No. 5, No. 6, No. 7 |
| Brahms 3 Intermezzi Op.117 | PD | 0/3 | - | No. 1, No. 2, No. 3 |
| Brahms 6 Klavierstücke Op.118 | PD | 1/6 | No. 2 | No. 1, No. 3, No. 4, No. 5, No. 6 |
| Brahms 4 Klavierstücke Op.119 | PD | 0/4 | - | No. 1, No. 2, No. 3, No. 4 |
| Debussy Suite bergamasque L.75 | PD | 3/4 | Prélude, Menuet, Clair de lune | Passepied |
| Debussy 2 Arabesques L.66 | PD | COMPLETE | No. 1, No. 2 | - |
| Debussy Estampes L.100 | PD | 0/3 | - | Pagodes, La soirée dans Grenade, Jardins sous la pluie |
| Debussy Pour le piano L.95 | PD | 1/3 | Sarabande | Prélude, Toccata |
| Debussy Images I L.110 | PD | 1/3 | Hommage à Rameau | Reflets dans l'eau, Mouvement |
| Debussy Images II L.111 | PD | 1/3 | Cloches à travers les feuilles | Et la lune descend, Poissons d'or |
| Debussy Préludes Book I L.117 | PD | 3/12 | Le vent dans la plaine, Des pas sur la neige, La cathédrale engloutie | Danseuses de Delphes, Voiles, Les sons et les parfums, Les collines d'Anacapri, Ce qu'a vu le vent d'ouest, La fille aux cheveux de lin, La sérénade interrompue, La danse de Puck, Minstrels |
| Debussy Préludes Book II L.123 | PD | 1/12 | Bruyères | Brouillards, Feuilles mortes, La puerta del Vino, Les fées sont d'exquises danseuses, Général Lavine, La terrasse des audiences, Ondine, Hommage à S. Pickwick, Canope, Les tierces alternées, Feux d'artifice |
| Ravel Miroirs M.43 | US-PD-only | 0/5 | - | Noctuelles, Oiseaux tristes, Une barque sur l'océan, Alborada del gracioso, La vallée des cloches |
| Ravel Gaspard de la nuit M.55 | US-PD-only | 1/3 | Le gibet | Ondine, Scarbo |
| Ravel Sonatine M.40 | US-PD-only | COMPLETE | complete or mvts | - |
| Satie 3 Gymnopédies | PD | COMPLETE | No. 1, No. 2, No. 3 | - |
| Satie Gnossiennes 1-6 | PD | 5/6 | No. 1, No. 2, No. 3, No. 4, No. 6 | No. 5 |
| Satie 3 Sarabandes | PD | 0/3 | - | No. 1, No. 2, No. 3 |
| Scriabin 12 Études Op.8 | PD | 1/12 | No. 12 | No. 1, No. 2, No. 3, No. 4, No. 5, No. 6, No. 7, No. 8, No. 9, No. 10, No. 11 |
| Scriabin 8 Études Op.42 | PD | 3/8 | No. 1, No. 5, No. 6 | No. 2, No. 3, No. 4, No. 7, No. 8 |

## Work order (complete sets nearest completion first, then famous empty sets)
1. Ravel Valses nobles M.61: OMR + correction in progress (tools/omr, PID 1449981), all 8.
2. Debussy Children's Corner: only No. 5 The Little Shepherd missing → completes the set.
3. Debussy Suite bergamasque: Passepied missing → completes the set.
4. Scriabin Op.32: No. 2 missing. Satie Gnossiennes: No. 5 missing.
5. Brahms Opp. 116, 117, 118, 119 (20 pieces, 3 present): look for Mutopia/PDMX clean files first, OMR the rest.
6. Debussy Estampes (3), Pour le piano (2), Images I/II (4), Ravel Miroirs (5), Gaspard (Ondine, Scarbo).
7. Debussy Préludes I (9 missing) and II (11 missing); Scriabin Op.8 (11) and Op.42 (5); Satie Sarabandes (3).
