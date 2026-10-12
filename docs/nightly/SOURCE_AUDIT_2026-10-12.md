# Nightly source audit — 2026-10-12

The October 11 run was abandoned after its START checkpoint. This run used origin/main 78190251 (5,929 items), including the approved quality-trim skip lists. Local pending Chopin/Mahler edits were preserved in the main checkout.

## Import decisions

No new score rows cleared the full quality, completeness and source-verification gates. No new composers, US-only approvals, recordings or MP3 previews were added. Existing catalogue entries were retained apart from four duplicate rows, whose editions were attached to canonical works.

Rank-1/2 signature scan found three title matches: Debussy “Nocturne (C.Debussy)” is a solo-piano work, not the orchestral Nocturnes; Saint-Saëns Concerto No.1 and Liszt Venezia e Napoli I already have local editions and did not establish a new complete set. The US-depth dry run found numerous alternate title matches, including composers outside this night's explicit approval list; none were imported.

The piano scan found nine slot matches in eight files. Decisions:

| Candidate | Decision |
|---|---|
| Chopin Nocturne Op.48 No.2 | PDMX composer is NA; rating 2.83/5 from three votes. Not cleared under the no-filler quality bar; source-page verification unavailable (Zenodo returned HTTP 429). |
| Mendelssohn Op.86 No.6 | Explicitly removed by the approved quality trim; do not re-import. |
| Brahms Op.118 No.2 [unedited] | Already present as an edition; no new work. |
| Beethoven Sonata 18 Scherzo | One movement, not a complete sonata; also falsely matched Sonata 3. Matcher corrected. |
| Beethoven Sonata 32, first movement | One movement, not a complete sonata. Matcher corrected. |
| Liszt Hungarian Rhapsody 15 | No ratings; candidate title itself is unreliable. Not cleared by quality/source verification. |
| Debussy Passepied | Explicitly trimmed canonical candidate; do not recreate it under a new id. |
| Debussy Feux d’artifice | Existing local edition; does not establish a new complete book. |

## Pending Chopin correction

[Mutopia piece 1727](https://www.mutopiaproject.org/cgibin/piece-info.cgi?id=1727) explicitly labels its edition Public Domain. Its linked LilyPond source has subtitle “4. Satz”, and the linked MIDI is `chp-op-35-4-scholz-fi.mid`: only movement IV. The prior uncommitted whole-sonata claim is incorrect. The pending file was not published by this run. Sonata No.2 now has four tracked movements; a generic title cannot satisfy the complete set.

IMSLP captcha controls were not bypassed; SA/NC/ND sources were not used. OMR was not imported without a correction and accuracy review.

## Rebuild provenance

The local legacy batches were older than origin/main and lacked 278 published canonical rows. In the isolated worktree, batches were reconciled against the committed bulk snapshot rather than accepting stale pending rows. The final baseline batch is `parts/BULK_batch_NIGHTLY_BASE_rows.csv` in that worktree. All prior other-edition metadata was preserved. Dedupe folded four already-published duplicates: Liszt Consolation No.4, two Satie Gymnopédie 1 copies, and Schumann Carnaval No.12. Final catalogue: 5,925 items, 237 composers; no new works.

Generated coverage is a metadata-matching research aid, not proof that every file contains every note. Explicitly labelled Beethoven single movements no longer count as complete sonatas. Further source/file reviews remain necessary before asserting full-set completeness.
