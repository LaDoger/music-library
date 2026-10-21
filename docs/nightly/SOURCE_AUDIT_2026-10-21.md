# Nightly source audit — 2026-10-21

Baseline: published origin/main f50239ff, 5,925 works / 237 composers. Resumed the October 15 report and October 19 source audit. The main checkout is divergent and contains unrelated unpublished score/cataloguing work; it was not used as a publishable baseline.

Fresh rank-1 piano-set source checks:

- [Ravel Miroirs on Free-scores](https://www.free-scores.com/partitions_telecharger.php?partition=61125): source page labels the edition Public Domain and lists the five pieces, but offers only a 48-page PDF, without an editable file. Existing local OMR work already has a Miroirs scan; no duplicate download or new import.
- [Ravel Miroirs on Cantorion](https://cantorion.org/music/1177/Miroirs-Piano): Public domain label, 48-page scan linked to Archive.org; no editable encoding offered. No download or complete-set claim.
- [DCML Estampes documentation](https://dcmlab.github.io/debussy_estampes/introduction): editable MuseScore files exist, but the source explicitly states CC BY-NC-SA 4.0. Excluded from commercial catalogue; private-reference policy retained.

IMSLP download gates were not bypassed. No new composer approvals inferred, no SA/NC/ND imports, no excluded works, no score-only MP3 previews. Existing pending OMR and recovered sonata MIDIs were left unpublished; metadata and successful MIDI parsing do not establish score accuracy or completeness.

Local scans use read-only links to retained metadata, not a copy of the dirty checkout catalogue. Title/slot matches require the same October 12–13 quality and complete-set review; they are research candidates, not cleared additions.

Resume: finish existing source-verified correction jobs for rank-1 complete sets before fetching duplicates. Obtain complete editable editions with explicit source licence, compare against the score, then import in tier order using established scripts. Keep the approved territorial restrictions and quality-trim exclusions.

Dry-run results: approved US-only scan harvested 112 matches, retained 110 before live-title filtering, leaving the same 13 candidates reviewed on October 13. No new approved work or complete set established. Signature-gap scan returned the same three matches: Debussy solo Nocturne is not orchestral Nocturnes; Saint-Saëns Cello Concerto No.1 and Liszt Venezia e Napoli I are existing editions, not new complete sets.

Bulk rebuild gate/dedupe check from the committed 5,590-row snapshot passed: 5,590 retained, zero additional duplicate pieces dropped. This avoids reconstructing the published catalogue from unrelated ignored batch files. Site rebuild check retained 5,925 rows; no generated data changes required.

The full piano-set dry run was bounded and stopped by exact owned PID 2252410 after more than 19 minutes without a plan. It did not finish and is not reported as a passed scan. No piano candidates were imported; the existing October 13 candidate-quality decisions remain in force. All source-cache symlinks and snapshot scratch are removed with this run's worktree.

Correction after collecting final process output: piano dry-run EXIT 0, pool 2,589, 13 slot matches in 13 files. The process finished before the attempted SIGTERM (which returned No such process); no PID was killed. The earlier incomplete/stopped statement is superseded. Results match October 13: low-quality Chopin Op.48/2; quality-trim exclusions Mendelssohn Op.86/6 and Debussy Passepied; existing Brahms Op.118/2 and Debussy Feux d’artifice; unrated Liszt Rhapsody 15; explicitly unfinished Beethoven Op.90/111; generic Chopin Op.35 and Beethoven Op.10/1, 13, 57, 78 requiring independent score review. No import clearance follows from slot matching.
