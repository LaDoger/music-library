# MusicBot review of one annotated-score draft

Use Haiku for straightforward short piano pieces; Sol for dense,
chromatic or ambiguous works. Run one review at a time; no audio renders.
Stay in the current worktree. Do not alter original MIDI or CSV rights.

Inputs provided by the runner: `ID`, `DRAFT_SPEC`, `REVIEWED_SPEC` and this
brief. Read `ANALYSIS_FORMAT.md` and `scripts/analysis/vocabulary.json`.
Read the item's full JSON, legal notes, source MIDI (and original MusicXML
if available), and the draft. Every heuristic is a candidate, not a fact.

1. Inspect note onsets AND sounding durations per proposed chord span.
   Confirm bar origin, pickup, meter, key spelling and source range. MIDI
   may already unfold repeats; do not double them. Check each chord,
   inversion, Roman numeral and local key; fix mistaken root heuristics.
2. Add only note-supported events from the controlled vocabulary. Verify
   cadences against bass/melody and phrase boundaries, distinguish
   tonicization from established modulation, and do not infer dynamics
   from a chromatic pitch change. Use `?` and a reason when uncertain.
3. Write form sections, start/continuation/turn/arrival story, per-section
   mood, a concise summary/tricks, loop/hook ranges and concrete K-pop
   uses. Preserve asymmetric phrases. Do not invent a final-chorus lift.
4. Set `draft:false`, `reviewed_by` to reviewer/model and date, and retain
   interpretive doubts in `review_flags`. Write **REVIEWED_SPEC**. Build:
   `python3 scripts/analysis/build_annotated.py --spec REVIEWED_SPEC`.
5. Run `verify_chords.py` on the built JSON. Require >=90% asserted matches,
   or explicitly identify every failed span and every unknown with a
   reason. Review all unknowns; never raise the percentage by relabelling
   unsupported complete chords as passing. Read the labelled-span coverage
   alongside the match rate. Inspect the MusicXML rendering for notation
   mistakes; preserve inherited score licence and credit.
6. Run the sync script and the targeted player check. The runner commits
   the reviewed spec, bundle and generated data only after verification;
   do not push or commit from the review command itself.

Runner setup: `MUSICLIB_ANALYSIS_REVIEW_CMD` is an explicit local command
string with `{id}`, `{draft_spec}`, `{reviewed_spec}`, `{brief}` placeholders.
The runner shell-quotes the substituted arguments. Configure it to your
chosen agent executable; there is no implicit service or token use.
Example interface: `review-agent --brief {brief} --id {id}
--input {draft_spec} --output {reviewed_spec}`. The executable must exist,
complete the note-level review, and write the reviewed spec.
