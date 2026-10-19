# Nightly source audit — 2026-10-19

Baseline: origin/main 6c0f9bc3, 5,925 works / 237 composers. Research only: no imports or edition changes.

Debussy and Ravel were checked first. Alternative routes investigated beyond the exhausted local PDMX/Mutopia/OpenScore pools:

- [Noctave Debussy](https://noctavepiano.com/en/sheet-music/debussy-clair-de-lune/): source page explicitly labels its MusicXML/PDF CC0 and traces Clair de lune to Keith OHara's Mutopia edition. Its four listed Debussy pieces are Clair de lune, an easy version, La fille aux cheveux de lin and Arabesque No.1. Existing catalogue covers these works; an easy adaptation does not fill a complete-set gap. No download/import needed.
- [Noctave Ravel](https://noctavepiano.com/partitions/ravel-pavane/): only Pavane listed, already present. Although offered as CC0, the detailed provenance explicitly says the upstream MuseScore page licence is unverified (`TODO(owner)`). Not a new cleared source for missing Ravel works. No MuseScore.com downloads attempted.
- [CPDL Debussy cycle](https://www.cpdl.org/wiki/index.php/Trois_Chansons_de_Charles_d%27Orl%C3%A9ans_(Claude_Debussy)) and [Ravel cycle](https://www.cpdl.org/wiki/index.php/Trois_chansons_(Maurice_Ravel)): ordinary page requests returned HTTP 403; no circumvention attempted. Do not treat the site's name or default wiki licence as an individual edition's permission. Main checkout already contains pending CPDL/OMR material owned by other jobs; left untouched.
- [CPDL Romance](https://www.cpdl.org/wiki/index.php/Romance_(Claude_Debussy)): accessible source identifies David Newman edition 17586 as Public Domain, but does not establish a new complete editable set. Both Deux Romances already appear as debussy_s2_no_1_l_ame_evaporee and debussy_s2_no_2_les_cloches. No import.
- [Kunst der Fuge terms](https://www.kunstderfuge.com/notes.htm): personal-use restriction; not cleared for commercial redistribution. Historical CC coverage is insufficient to override current file-specific rights. No files fetched.
- [BitMidi Ravel Menuet antique](https://bitmidi.com/ravel_menuet_antique-mid): download availability without an explicit per-file open licence does not clear the encoding. No file fetched.
- [Musicalion terms](https://www.musicalion.com/general/Docs/en_EN/terms.pdf): modification/redistribution restrictions rule it out as an open editable-score route.
- [DCML Debussy](https://github.com/DCMLab/debussy_piano): CC BY-NC-SA, retained as private reference only; never an import source.

No candidate cleared both missing-work/completeness and licence gates. This is a bounded audit, not a claim that every online source is exhausted. No new US-only approvals, excluded works, SA/NC/ND imports, captcha bypass or MP3 previews.

Resume: check the active correction/cataloguing jobs before sourcing the same pieces again. For genuinely missing works, obtain an accessible source page with explicit edition licence plus a complete editable score, then verify identity/completeness and use the established import/build workflow. Keep CPDL requests stopped while forbidden; human-provided source evidence is needed before using those editions.
