# Nightly depth batch — 2026-10-23

Added **0 works / 0 composers / 0 complete sets**; published catalogue retained at **5,925 works / 237 composers**. Resumed the October 22 correction/source leads; no broad scans, previews, new approvals or imports.

Correction audit: scratch `out/imp_*/corrected` folders are empty, but final MusicXML/MIDI survive in the main checkout's `files/scores`. Empty scratch is not evidence of lost final scores. Existing main commits and dirty work were preserved; no processes were killed. This run's coordinator was initially misidentified by the routine audit as another running batch; that inference was discarded.

The latest Épigraphes log explicitly retains piece 5 FAIL (bar 26 timing); pieces 1–4 and 6 PASS. All six final MusicXML/MIDI pairs survive as `debussy_omr_imslp913491_epigraphes_<1–6>.*`. No PASS was inferred from file existence. Other recorded unresolved corrections include Ravel Trio movement 2 (missing later bars), Introduction et Allegro, La Valse, Tombeau and Debussy sonatas. Vallée and Menuet antique final files also survive; a single movement does not establish a complete Miroirs set. No unreviewed local score was promoted.

Images I: no fetched Dtromp Sibelius source was found. The previous source audit records IMSLP engraving file #11443, CC BY 3.0, alongside PDF #357447. The Images set 3 PDF and private NC reference files are different sources. No captcha bypass or fresh source-page licence verification was attempted; the earlier evidence remains a lead, not import clearance.

Next: open `files/scores/debussy_omr_imslp913491_epigraphes_5.musicxml`, compare bar 26 against the original scan, correct timing, regenerate MIDI, and independently verify the entire six-piece set with preserved REPORT/VERDICTS before catalogue publication. Locate the original scan or approved backup first if it is unavailable. Do not merely append PASS. For Images I, obtain #11443 through normal human download, preserve source/licence/credit, convert and compare all three pieces before import. Retain Ravel's US-only publication gate and all exclusions.

Validation: an initial bulk rebuild had no ignored batch inputs and produced an invalid reduced catalogue in the isolated worktree; all generated changes were reverted. The final validation uses the committed `library_bulk.csv` as a temporary batch snapshot, never unpublished incoming batches. Final results and publication verification are recorded below.

Models: Codex coordinator (session model/effort and exact token/cost totals not exposed; no high-effort override); Claude Haiku 5.5, explicitly low effort, one invocation and one hop. Haiku usage: 52 input, 88,801 cache-write, 1,838,510 cache-read, 18,343 output (8,061 thinking); reported cost **$0.05211468**. No media generation or audio/video review; Argon fps/resolution/tokens/cost not applicable. No further harness calls. Codex initial quota snapshot 2% used; initial disk 76%.

Git: isolated branch from origin/main `720417bd`; only this report and STATUS checkpoint intended for publication. Main checkout preserved. Raw logs remain outside git.

Final validation: committed-snapshot bulk rebuild PASS (5,590 rows; zero additional duplicates); site sync check and catalogue check PASS (5,925 works / 237 composers); bulk licence audit PASS (zero violations); UI PASS (11,850-row fixture); player PASS including live MIDI. Snapshot rebuild omits historical alternate editions, so that generated file was restored; catalogue inputs and generated data remain unchanged. Changed-report brand/secret and diff checks PASS. Final quota snapshot 2%, disk 77%.
