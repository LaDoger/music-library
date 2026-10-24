# Nightly depth batch — 2026-10-24

Added **0 works / 0 composers / 0 complete sets**. Catalogue retained at **5,925 works / 237 composers**. Live URL: https://ladoger.github.io/music-library/ .

Resumed rank-1 complete-set leads rather than repeating unchanged broad scans. Debussy Épigraphes still lacks an all-PASS REPORT/VERDICTS: the latest correction log retains piece 5 FAIL at bar 26; pieces 1–4 and 6 PASS. Six final MusicXML/MIDI pairs survive, but file existence does not clear the set. No concurrent correction job was changed.

The normal IMSLP Images I page fetch again showed Dtromp Sibelius engraving #11443 tagged Creative Commons Attribution 3.0. No local editable source was found. Human download, conversion and comparison of all three pieces remain necessary; no captcha bypass or download was attempted. No complete editable Ravel Miroirs set was established. Previous source and territorial exclusions remain binding.

Validation: the initial bulk rebuild had no ignored batch inputs and its reduced outputs were restored. Final `build_bulk_layer.py --check` used committed `library_bulk.csv` as a temporary batch snapshot: **5,590 rows, zero additional duplicates**, PASS. Snapshot removed afterwards. Site rebuild and catalogue check PASS (5,925 works); bulk licence audit PASS (zero violations); UI PASS (11,850-row fixture); player PASS including live MIDI. Generated data and catalogue inputs remain unchanged. Brand/secret checks and diff check passed for publication. Public README's existing local checkout path is a usage example and needs no change for this batch.

Isolated worktree based on origin/main 70931063. START a8dc06bc pushed to main. Main dirty/divergent checkout, incoming scans, OMR and props jobs preserved. No processes killed, no score-only MP3 previews, no new approvals or unreviewed imports. Logs kept outside git. Disk 76%; initial Codex quota snapshot 22%.

Models: Codex coordinator, default effort, exact job tokens/cost unavailable; Claude Haiku 5.5 routine audit/checks, normal effort (medium CLI setting), one hop, no nested harness/model calls. Haiku: 54 input, 64,207 cache-write, 1,509,781 cache-read, 17,389 output tokens including 5,668 thinking; reported cost **$0.04005861**. No paid media generation or audio/video review; Argon fps/resolution/tokens/cost N/A. Known model-cost subtotal $0.04005861; coordinator accounting unavailable.

Next: correct Épigraphes piece 5 bar 26 against its source and independently verify the full six-piece set; obtain Images I #11443 normally and compare all three converted pieces before import. Publish only after source licence, quality and complete-set gates pass.

Publication and live deployment verification follow below.
