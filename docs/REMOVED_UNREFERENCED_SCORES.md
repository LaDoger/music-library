# Removed unreferenced score files

Untracked files in `files/scores/` that no row referenced: not a `local_score_path` (or other file path/basename) in `library.csv` or `library_bulk.csv`, and not an alternate-edition id in `library_other_editions.json`. They were never committed, so nothing on the site linked to them. Mostly unfinished PDMX uploads (WIP / draft titles that the bulk gate rejects) and duplicate MIDIs dropped by the dedupe pass. Size and SHA-256 per file: `parts/REMOVED_UNREFERENCED_SCORES.csv` (git-ignored). PDMX files can be re-extracted from the Zenodo `mid.tar.gz` (record 15571083).

## CP-SCALE3-1 cleanup (2026-10-09): 20 files

- `files/scores/anonymous_agni_parthene_wip.mid`
- `files/scores/anonymous_agni_parthene_wipb2.mid`
- `files/scores/anonymous_dolce_nemica_mia_rough_draft.mid`
- `files/scores/anonymous_dolce_nemica_mia_rough_draftb2.mid`
- `files/scores/bach_bwv543_wip_bach_bwv_543_prelude_and.mid`
- `files/scores/beethoven_op120_diabelli_variations_wip.mid`
- `files/scores/beethoven_op120_diabelli_variations_wipb2.mid`
- `files/scores/beethoven_symphony_no_9_iiii_mov_prest.mid`
- `files/scores/beethoven_symphony_no_9_iiii_mov_prestb2.mid`
- `files/scores/debussy_claude_debussy_pelleas_et_me.mid`
- `files/scores/debussy_claude_debussy_pelleas_et_meb2.mid`
- `files/scores/diabelli_wip_diabelli_differentes_pie.mid`
- `files/scores/haydn_hobi52_first_movement_from_joseph_h.mid`
- `files/scores/haydn_hobi52_first_movement_from_joseph_hb2.mid`
- `files/scores/mahler_mahler_symphony_no_1_mvt_1_w.mid`
- `files/scores/mahler_mahler_symphony_no_1_mvt_1_wb2.mid`
- `files/scores/schumann_op41no2_string_quartet_no_2_op_41_no.mxl`
- `files/scores/traditional_terra_beata_hymntune.mid`
- `files/scores/vivaldi_rv93_wip_vivaldi_rv_93_lute_conce.mid`
- `files/scores/vivaldi_rv93_wip_vivaldi_rv_93_lute_conceb2.mid`

## CP-SCALE3-3 cleanup (P4 row dropped: archaic title spelling trips the brand-scrub grep) (2026-10-09): 1 files

- `files/scores/marais_marin_marais_the_female_sayl.mid`
