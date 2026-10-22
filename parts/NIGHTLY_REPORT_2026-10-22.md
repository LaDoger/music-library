# Nightly depth batch — 2026-10-22

Works added: **0**. Composers added: **0**. Sets completed: **0**. Published catalogue retained at **5,925 works / 237 composers**.

Read the required brief, universal rules and checkpoint protocol. START checkpoint published as d7794355. Worked from origin/main 1bee81ea in an isolated worktree; the divergent main checkout and existing incoming scans/correction jobs were preserved.

No candidate cleared the licence and complete-set quality gates. Previous unfinished, quality-trimmed and unreviewed sonata candidates remain unpublished. Fresh rank-1 research identified a concrete editable lead: Dtromp's complete Debussy Images I Sibelius files on IMSLP, explicitly CC BY 3.0. Human fetch, conversion and independent score comparison are still required. Ray Alston's CC0 edition there is PDF only. Source evidence and resume steps: [source audit](../docs/nightly/SOURCE_AUDIT_2026-10-22.md).

No new composer approvals, excluded works, guessed licences, SA/NC/ND imports, captcha bypasses or score-only MP3 previews. Only the redundant check invocation started by this run and its descendants were stopped by exact PID after the independent regression checks passed. No pre-existing processes were touched.

Live URL: https://ladoger.github.io/music-library/ . Homepage, index manifest and catalogue returned HTTP 200; catalogue count 5,925 works / 237 composers. Eleven rank-1 composers' MIDI endpoints returned valid MThd headers. START Pages deployment 39721057123 succeeded.

Models: Codex coordinator, default effort (usage helper labels Codex gpt-6.1-sol; exact session model and token/cost totals not exposed); Claude Haiku, default effort, for routine checks, one hop. No audio/video review or paid media generation; Argon fps/resolution/tokens/cost not applicable. Codex quota snapshot 57% used; disk 86% at START, 87% after worktree creation. Haiku cost/token totals and final checks recorded below.

Next: finish existing source-verified Ravel/Debussy complete-set corrections, or obtain and review the Images I Sibelius source before import. Keep territorial restrictions and quality exclusions. Research scratch and temporary worktree are removed after publication.

Final checks: bulk snapshot build/dedupe PASS (5,590 rows, zero additional duplicates); catalogue and site rebuild checks PASS (5,925 works); licence audit PASS (5,590 rows, zero violations); UI PASS (11,850-row fixture); player PASS including live MIDI; public-content brand and changed-file secret/diff checks PASS. No catalogue inputs changed, so rebuild validation used check mode and the committed bulk snapshot in scratch rather than unpublished incoming batches.

Candidate scans: depth dry run completed (227 metadata matches / 226 retained before live-title filtering); broader helper output was filtered against this batch's explicit composer approvals. Signature dry run completed with the same three rejected matches as October 21. Piano dry run reached its 600-second limit without producing a result; it is incomplete, not a completed-set audit. No incomplete scan was used to authorize an import.

Haiku 5.5 known usage across two completed invocations: 56 input, 53,269 cache-write, 846,648 cache-read, 12,089 output tokens (including 3,115 thinking); reported cost $0.02517038. A third invocation was stopped after its candidate scans/checks; its final token/cost total is unavailable, so $0.02517 is a known subtotal, not a complete job cost. No generation spend. Codex final available usage snapshot 59%; exact job totals unavailable.
