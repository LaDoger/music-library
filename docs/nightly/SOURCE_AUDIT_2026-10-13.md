# Nightly source audit — 2026-10-13

Started from published origin/main `0e215c85`, preserving the dirty main checkout. The October 12 resume decisions and approved quality-trim exclusions remain binding.

## Source checks

- [Zenodo PDMX](https://zenodo.org/records/15571083) is readable again on this run. Its source page documents the conflicting-licence issue and recommends the `no_license_conflict` subset. Compilation access is no longer the October 12 blocker; individual quality/completeness decisions remain unchanged. No source files were downloaded from MuseScore.com.
- [Mutopia 1727](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1727) was rechecked; the prior audit establishes movement IV only, so it cannot fill Chopin Sonata No.2 as a whole.
- Targeted searches for Schumann Kreisleriana, Debussy La mer/Sarabande and Chopin Op.48 No.2 produced no newly cleared editable complete set. [Mutopia 1590](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1590) is Op.9 No.2, CC BY-SA 3.0; excluded. [Schumann FTP listing](https://www.mutopiaproject.org/ftp/SchumannR/) contains Op.15/25/28/48/68/124, not Kreisleriana Op.16.
- IMSLP remains a manual/captcha-gated download source under the nightly brief. No bypass attempted. No unreviewed OMR imported.

## Resume

Obtain human-fetched IMSLP PD/CC0/CC BY editable full-set files using the source-page workflow, then review identity, completeness and score accuracy before importing. Do not recreate quality-trimmed rows, mistake single movements for whole sets, or import SA/NC/ND editions. No new composer approvals are inferred.

## US-only candidate review

The approved-composer scan harvested 112 matches, retained 110 before live-title filtering, and left 13 alternate-title candidates. Pomp and Circumstance, Prelude Op.3 No.2 and Vocalise already have canonical works; additions would be editions. Rachmaninoff Suite Op.5 movement IV and Op.22 variation 19 do not complete their cycles. Op.39, Ravel folk-song titles and Holst Mars have no ratings and do not establish a reviewed full set. The Op.23 entries do not establish the missing complete prelude set. Elgar There is Sweet Music points to a Mutopia `-lys/` include directory rather than a verified ready MIDI/full-set download; retained as a source-research candidate, not published. These are unchanged pools from the prior run; no complete-set claim is inferred from title matching.

Elgar candidate MIDI URL was independently probed with HTTP HEAD and returned **404**, confirming it is not a ready import source.

## Rebuild and signature scan

The rank-1/2 signature scan again found three title matches, identical to October 12: Debussy solo-piano Nocturne is not orchestral Nocturnes; Saint-Saëns Concerto No.1 and Liszt Venezia e Napoli I are existing editions and do not establish new complete sets. No rows imported.

Rebuild uses the previous reconciled baseline batch, preserves all 2,350 canonical works' other-edition metadata from the committed snapshot, and reproduces 5,925 works / 5,590 bulk rows. Four already-folded duplicates remain folded; no further works removed. Two generated alternate score links referenced untracked local files absent from the deployed site (both independently return HTTP 404): `bach_bwv999_prelude_in_d_minorb51.mid` and `holst_op_32_mars_bringer_of_warb51.mid`. Regeneration removes these broken links; canonical scores remain present. No JSON was hand-edited.

## Refreshed piano scan

The current matcher produces **13 slot matches in 13 files**, versus the previous plan's nine matches. They are not import clearance. Unfinished Beethoven Op.90/111 movement-II titles are rejected even though `is_draft=False`; this illustrates why metadata-slot coverage is not completeness proof. Chopin Op.48/2 remains rated 2.83/5 with unknown composer metadata; Mendelssohn Op.86/6 and Debussy Passepied remain quality-trim exclusions. Brahms Op.118/2 and Debussy Feux d'artifice remain existing editions. Liszt Rhapsody 15 remains unrated with unreliable title wording.

Additional generic whole-sonata matches: Chopin Op.35 and Beethoven Op.10/1, Op.13, Op.57, Op.78. Four source MIDIs are absent from the retained local corpus; no full-file review has been established. Beethoven Op.78 has local MIDI but the existing catalogue already contains both movements separately; an edition is not a new completed set. These candidates require full-file review, rather than being asserted complete from a generic title. A normal Zenodo MIDI archive fetch was attempted to resolve the missing local files; result recorded below.

The archive request timed out after 120 seconds (166,710,808 / 214,395,208 bytes); it is explicitly **partial**, not cached as a complete archive. Three intact MIDI members were recovered for review: Chopin Op.35 (two tracks, 14,477 note-ons, 1,314 seconds), Beethoven Op.10/1 (two tracks, 7,250 note-ons, 1,029 seconds), and Beethoven Op.57 (two tracks, 15,548 note-ons, 1,452 seconds). MIDI parsing succeeds and their meter sequences suggest multiple movements, but no movement markers or independent score comparison establishes quality-cleared completeness. Numerous inserted odd meters (including Chopin 5/4 and 9/8, Beethoven Op.10/1 5/8) need score comparison rather than assuming the generic title guarantees accurate notes. Retained unpublished for a full-file/critical-score review. No MP3 rendered. The remaining Op.13 member was not recovered. Recovered files, structure summaries and candidate metadata are in `.tmp/review-midi/` and `.tmp/piano-candidates.json`.
