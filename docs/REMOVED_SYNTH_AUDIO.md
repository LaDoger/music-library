# Removed synth-rendered audio (2026-10-09)

LaDoger decided at 22:09 CEST on 2026-10-09 to remove every synth-rendered audio file. This manifest was written before anything was deleted. Machine-readable copy: `parts/REMOVED_SYNTH_AUDIO_MANIFEST.csv` (git-ignored working copy; this file is the committed copy).

## How files were classified

- **SYNTH (removed):** the row's `recording_source_url` is empty, so its preview was a 15 s FluidSynth (FluidR3_GM) render of the score MIDI. These were made by `scripts/make_preview.py --midi`, `scripts/bulk/download_slice.py` with `midi_clip.py`, and `scripts/batch1_bach`. The row's legal notes said "Preview is an own FluidSynth/MIDI render". The 7 `synth-v1` Release assets are full-length FluidSynth renders made by `scripts/render_synth.py`.
- **REAL (kept):** the row has a `recording_source_url` and a Release `audio-v1` file (`local_audio_path`). README says these previews are cut from the licensed recording. The `audio-v1` Release, the Commons and Internet Archive streams, and `data/stream_urls.json` are all recordings and were not touched.
- **Uncertain, kept:** none. Every MP3 in `previews/` belongs to one of the two classes above.

Counts: 451 synth previews removed from git and from `preview_path`, 7 `synth-v1` Release assets deleted, 64 real-recording previews kept.

Every removed piece still has its score. The site plays the score MIDI with the in-browser html-midi-player (Synth mode).

## Removed

| kind | path / URL | item id | reason |
|---|---|---|---|
| removed_synth_preview | `previews/bach_bwv1007_prelude.mp3` | `bach_bwv1007_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1068_air.mp3` | `bach_bwv1068_air` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/debussy_arabesque_1.mp3` | `debussy_arabesque_1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/debussy_clair_de_lune.mp3` | `debussy_clair_de_lune` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/faure_apres_un_reve.mp3` | `faure_apres_un_reve` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/faure_pavane.mp3` | `faure_pavane` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/faure_sicilienne.mp3` | `faure_sicilienne` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/handel_hwv56_hallelujah.mp3` | `handel_hwv56_hallelujah` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mozart_k525_nachtmusik.mp3` | `mozart_k525_nachtmusik` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/pachelbel_canon_d.mp3` | `pachelbel_canon_d` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/satie_gnossienne_1.mp3` | `satie_gnossienne_1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv208_sheep_may_safely_graze.mp3` | `bach_bwv208_sheep_may_safely_graze` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv230_lobet_den_herrn.mp3` | `bach_bwv230_lobet_den_herrn` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv508_bist_du_bei_mir.mp3` | `bach_bwv508_bist_du_bei_mir` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv528_trio_sonata4.mp3` | `bach_bwv528_trio_sonata4` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv529_trio_sonata5.mp3` | `bach_bwv529_trio_sonata5` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv533_prelude_e_minor.mp3` | `bach_bwv533_prelude_e_minor` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv542_fantasia_fugue.mp3` | `bach_bwv542_fantasia_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv549_prelude_c_minor.mp3` | `bach_bwv549_prelude_c_minor` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv582_passacaglia.mp3` | `bach_bwv582_passacaglia` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv599_nun_komm.mp3` | `bach_bwv599_nun_komm` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv600_gott_durch_deine_gute.mp3` | `bach_bwv600_gott_durch_deine_gute` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv601_herr_christ.mp3` | `bach_bwv601_herr_christ` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv602_lob_sei_dem_allmachtigen.mp3` | `bach_bwv602_lob_sei_dem_allmachtigen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv604_gelobet_seist_du.mp3` | `bach_bwv604_gelobet_seist_du` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv605_der_tag_der_ist.mp3` | `bach_bwv605_der_tag_der_ist` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv606_vom_himmel_hoch.mp3` | `bach_bwv606_vom_himmel_hoch` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv609_lobt_gott.mp3` | `bach_bwv609_lobt_gott` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv610_jesu_meine_freude.mp3` | `bach_bwv610_jesu_meine_freude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv618_o_lamm_gottes.mp3` | `bach_bwv618_o_lamm_gottes` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv619_christe_du_lamm.mp3` | `bach_bwv619_christe_du_lamm` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv622_o_mensch_bewein.mp3` | `bach_bwv622_o_mensch_bewein` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv636_vater_unser.mp3` | `bach_bwv636_vater_unser` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv643_alle_menschen.mp3` | `bach_bwv643_alle_menschen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv646_wo_soll_ich_fliehen.mp3` | `bach_bwv646_wo_soll_ich_fliehen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv647_wer_nur_den_lieben_gott.mp3` | `bach_bwv647_wer_nur_den_lieben_gott` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv648_meine_seele.mp3` | `bach_bwv648_meine_seele` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv649_ach_bleib_bei_uns.mp3` | `bach_bwv649_ach_bleib_bei_uns` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv650_kommst_du_nun.mp3` | `bach_bwv650_kommst_du_nun` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv651_fantasia_komm_heiliger_geist.mp3` | `bach_bwv651_fantasia_komm_heiliger_geist` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv653_an_wasserflussen.mp3` | `bach_bwv653_an_wasserflussen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv654_schmucke_dich.mp3` | `bach_bwv654_schmucke_dich` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv657_nun_danket.mp3` | `bach_bwv657_nun_danket` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv687_aus_tiefer_not.mp3` | `bach_bwv687_aus_tiefer_not` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv720_ein_feste_burg.mp3` | `bach_bwv720_ein_feste_burg` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv727_herzlich_tut_mich.mp3` | `bach_bwv727_herzlich_tut_mich` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv734_nun_freut_euch.mp3` | `bach_bwv734_nun_freut_euch` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv735_valet_will_ich.mp3` | `bach_bwv735_valet_will_ich` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv751_in_dulci_jubilo.mp3` | `bach_bwv751_in_dulci_jubilo` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv769_canonic_variations.mp3` | `bach_bwv769_canonic_variations` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv773_invention2.mp3` | `bach_bwv773_invention2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv774_invention3.mp3` | `bach_bwv774_invention3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv775_invention4.mp3` | `bach_bwv775_invention4` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv776_invention5.mp3` | `bach_bwv776_invention5` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv778_invention7.mp3` | `bach_bwv778_invention7` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv779_invention8.mp3` | `bach_bwv779_invention8` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv781_invention10.mp3` | `bach_bwv781_invention10` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv782_invention11.mp3` | `bach_bwv782_invention11` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv784_invention13.mp3` | `bach_bwv784_invention13` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv785_invention14.mp3` | `bach_bwv785_invention14` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv786_invention15.mp3` | `bach_bwv786_invention15` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv787_sinfonia1.mp3` | `bach_bwv787_sinfonia1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv788_sinfonia2.mp3` | `bach_bwv788_sinfonia2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv789_sinfonia3.mp3` | `bach_bwv789_sinfonia3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv790_sinfonia4.mp3` | `bach_bwv790_sinfonia4` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv791_sinfonia5.mp3` | `bach_bwv791_sinfonia5` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv792_sinfonia6.mp3` | `bach_bwv792_sinfonia6` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv793_sinfonia7.mp3` | `bach_bwv793_sinfonia7` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv794_sinfonia8.mp3` | `bach_bwv794_sinfonia8` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv795_sinfonia9.mp3` | `bach_bwv795_sinfonia9` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv796_sinfonia10.mp3` | `bach_bwv796_sinfonia10` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv797_sinfonia11.mp3` | `bach_bwv797_sinfonia11` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv798_sinfonia12.mp3` | `bach_bwv798_sinfonia12` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv799_sinfonia13.mp3` | `bach_bwv799_sinfonia13` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv800_sinfonia14.mp3` | `bach_bwv800_sinfonia14` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv801_sinfonia15.mp3` | `bach_bwv801_sinfonia15` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv803_duetto2.mp3` | `bach_bwv803_duetto2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv804_duetto3.mp3` | `bach_bwv804_duetto3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv805_duetto4.mp3` | `bach_bwv805_duetto4` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv806_bourree1.mp3` | `bach_bwv806_bourree1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv806_bourree2.mp3` | `bach_bwv806_bourree2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv807_bourree1.mp3` | `bach_bwv807_bourree1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv807_bourree2.mp3` | `bach_bwv807_bourree2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv807_gigue.mp3` | `bach_bwv807_gigue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv816_french_suite5.mp3` | `bach_bwv816_french_suite5` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv825_partita1.mp3` | `bach_bwv825_partita1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv826_partita2_sinfonia.mp3` | `bach_bwv826_partita2_sinfonia` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv827_partita3.mp3` | `bach_bwv827_partita3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv829_partita5.mp3` | `bach_bwv829_partita5` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv830_partita6.mp3` | `bach_bwv830_partita6` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv846_fugue.mp3` | `bach_bwv846_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv847_prelude.mp3` | `bach_bwv847_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv848_prelude.mp3` | `bach_bwv848_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv848_fugue.mp3` | `bach_bwv848_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv849_prelude.mp3` | `bach_bwv849_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv849_fugue.mp3` | `bach_bwv849_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv850_prelude.mp3` | `bach_bwv850_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv851_prelude.mp3` | `bach_bwv851_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv851_fugue.mp3` | `bach_bwv851_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv853_prelude.mp3` | `bach_bwv853_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv853_fugue.mp3` | `bach_bwv853_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv854_prelude.mp3` | `bach_bwv854_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv855_prelude.mp3` | `bach_bwv855_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv855_fugue.mp3` | `bach_bwv855_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv856_prelude.mp3` | `bach_bwv856_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv856_fugue.mp3` | `bach_bwv856_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv860_prelude.mp3` | `bach_bwv860_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv860_fugue.mp3` | `bach_bwv860_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv861_prelude.mp3` | `bach_bwv861_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv861_fugue.mp3` | `bach_bwv861_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv862_prelude.mp3` | `bach_bwv862_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv862_fugue.mp3` | `bach_bwv862_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv865_prelude.mp3` | `bach_bwv865_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv865_fugue.mp3` | `bach_bwv865_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv869_fugue.mp3` | `bach_bwv869_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv870_prelude.mp3` | `bach_bwv870_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv870_fugue.mp3` | `bach_bwv870_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv871_prelude.mp3` | `bach_bwv871_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv871_fugue.mp3` | `bach_bwv871_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv875_prelude.mp3` | `bach_bwv875_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv895_prelude_fugue.mp3` | `bach_bwv895_prelude_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv903_chromatic_fantasia.mp3` | `bach_bwv903_chromatic_fantasia` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv903_fugue.mp3` | `bach_bwv903_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv910_toccata.mp3` | `bach_bwv910_toccata` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv926_little_prelude.mp3` | `bach_bwv926_little_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv928_little_prelude.mp3` | `bach_bwv928_little_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv996_bourree.mp3` | `bach_bwv996_bourree` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv997_prelude.mp3` | `bach_bwv997_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv997_fugue.mp3` | `bach_bwv997_fugue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv997_sarabande.mp3` | `bach_bwv997_sarabande` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv997_gigue.mp3` | `bach_bwv997_gigue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv999_prelude.mp3` | `bach_bwv999_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1002_violin_partita1.mp3` | `bach_bwv1002_violin_partita1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1009_prelude.mp3` | `bach_bwv1009_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1009_bourree.mp3` | `bach_bwv1009_bourree` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1009_gigue.mp3` | `bach_bwv1009_gigue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1010_prelude.mp3` | `bach_bwv1010_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1010_bourree.mp3` | `bach_bwv1010_bourree` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1011_prelude.mp3` | `bach_bwv1011_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1011_sarabande.mp3` | `bach_bwv1011_sarabande` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1011_gigue.mp3` | `bach_bwv1011_gigue` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1013_flute_partita.mp3` | `bach_bwv1013_flute_partita` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1017_siciliano.mp3` | `bach_bwv1017_siciliano` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1030_flute_sonata.mp3` | `bach_bwv1030_flute_sonata` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1031_siciliano.mp3` | `bach_bwv1031_siciliano` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1042_1_allegro.mp3` | `bach_bwv1042_1_allegro` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1042_2_adagio.mp3` | `bach_bwv1042_2_adagio` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1042_3_allegro_assai.mp3` | `bach_bwv1042_3_allegro_assai` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1043_1_vivace.mp3` | `bach_bwv1043_1_vivace` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1043_2_largo.mp3` | `bach_bwv1043_2_largo` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1043_3_allegro.mp3` | `bach_bwv1043_3_allegro` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1046_brandenburg1_1_allegro.mp3` | `bach_bwv1046_brandenburg1_1_allegro` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1046_brandenburg1_2_adagio.mp3` | `bach_bwv1046_brandenburg1_2_adagio` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1047_brandenburg2_1_allegro.mp3` | `bach_bwv1047_brandenburg2_1_allegro` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1047_brandenburg2_2_andante.mp3` | `bach_bwv1047_brandenburg2_2_andante` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1047_brandenburg2_3_allegro_assai.mp3` | `bach_bwv1047_brandenburg2_3_allegro_assai` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1050_brandenburg5_allegro.mp3` | `bach_bwv1050_brandenburg5_allegro` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1056r_largo.mp3` | `bach_bwv1056r_largo` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1079_ricercar_a3.mp3` | `bach_bwv1079_ricercar_a3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1079_ricercar_a6.mp3` | `bach_bwv1079_ricercar_a6` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus1.mp3` | `bach_bwv1080_contrapunctus1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus2.mp3` | `bach_bwv1080_contrapunctus2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus3.mp3` | `bach_bwv1080_contrapunctus3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus4.mp3` | `bach_bwv1080_contrapunctus4` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus5.mp3` | `bach_bwv1080_contrapunctus5` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus6.mp3` | `bach_bwv1080_contrapunctus6` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus7.mp3` | `bach_bwv1080_contrapunctus7` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus8.mp3` | `bach_bwv1080_contrapunctus8` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus9.mp3` | `bach_bwv1080_contrapunctus9` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus10.mp3` | `bach_bwv1080_contrapunctus10` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus11.mp3` | `bach_bwv1080_contrapunctus11` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_canon_octave.mp3` | `bach_bwv1080_canon_octave` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_canon_twelfth.mp3` | `bach_bwv1080_canon_twelfth` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_canon_tenth.mp3` | `bach_bwv1080_canon_tenth` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_canon_augmentation.mp3` | `bach_bwv1080_canon_augmentation` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus12.mp3` | `bach_bwv1080_contrapunctus12` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus13.mp3` | `bach_bwv1080_contrapunctus13` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_fuga_2_clav.mp3` | `bach_bwv1080_fuga_2_clav` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1080_contrapunctus14.mp3` | `bach_bwv1080_contrapunctus14` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/petzold_bwv_anh114_minuet_g.mp3` | `petzold_bwv_anh114_minuet_g` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/petzold_bwv_anh115_minuet_g_minor.mp3` | `petzold_bwv_anh115_minuet_g_minor` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw29_rheinlegendchen.mp3` | `mahler_gmw29_rheinlegendchen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw45_kindertotenlieder1.mp3` | `mahler_gmw45_kindertotenlieder1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw45_kindertotenlieder2.mp3` | `mahler_gmw45_kindertotenlieder2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw45_kindertotenlieder3.mp3` | `mahler_gmw45_kindertotenlieder3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw45_kindertotenlieder4.mp3` | `mahler_gmw45_kindertotenlieder4` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw45_kindertotenlieder5.mp3` | `mahler_gmw45_kindertotenlieder5` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw10_gesellen1.mp3` | `mahler_gmw10_gesellen1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw10_gesellen2.mp3` | `mahler_gmw10_gesellen2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw10_gesellen3.mp3` | `mahler_gmw10_gesellen3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mahler_gmw10_gesellen4.mp3` | `mahler_gmw10_gesellen4` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_wesendonck1_der_engel.mp3` | `wagner_wwv91_wesendonck1_der_engel` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_wesendonck2_stehe_still.mp3` | `wagner_wwv91_wesendonck2_stehe_still` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_wesendonck3_im_treibhaus.mp3` | `wagner_wwv91_wesendonck3_im_treibhaus` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_wesendonck4_schmerzen.mp3` | `wagner_wwv91_wesendonck4_schmerzen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_wesendonck5_traume.mp3` | `wagner_wwv91_wesendonck5_traume` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv75_elsa_procession.mp3` | `wagner_wwv75_elsa_procession` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv86d_gotterdammerung_act3_prelude.mp3` | `wagner_wwv86d_gotterdammerung_act3_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv111_parsifal_prelude.mp3` | `wagner_wwv111_parsifal_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv111_parsifal_good_friday.mp3` | `wagner_wwv111_parsifal_good_friday` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv96_meistersinger_prelude.mp3` | `wagner_wwv96_meistersinger_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv86d_siegfried_funeral_march.mp3` | `wagner_wwv86d_siegfried_funeral_march` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv90_tristan_liebestod.mp3` | `wagner_wwv90_tristan_liebestod` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv70_tannhauser_overture.mp3` | `wagner_wwv70_tannhauser_overture` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/alkan_op31_1_prelude.mp3` | `alkan_op31_1_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/alkan_op31_2_prelude.mp3` | `alkan_op31_2_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/alkan_op31_8_folle.mp3` | `alkan_op31_8_folle` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/alkan_op75_toccatina.mp3` | `alkan_op75_toccatina` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op2_1_etude.mp3` | `scriabin_op2_1_etude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op11_1_prelude.mp3` | `scriabin_op11_1_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op16_1_prelude.mp3` | `scriabin_op16_1_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op16_2_prelude.mp3` | `scriabin_op16_2_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op16_3_prelude.mp3` | `scriabin_op16_3_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op16_4_prelude.mp3` | `scriabin_op16_4_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op16_5_prelude.mp3` | `scriabin_op16_5_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op59_2_prelude.mp3` | `scriabin_op59_2_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_tendres_plaintes.mp3` | `rameau_tendres_plaintes` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_sauvages.mp3` | `rameau_sauvages` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_tambourin.mp3` | `rameau_tambourin` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_rct43_ouverture_1.mp3` | `rameau_rct43_ouverture_1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_rct43_ouverture_2.mp3` | `rameau_rct43_ouverture_2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_rct43_marche.mp3` | `rameau_rct43_marche` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_rct43_tonnerre.mp3` | `rameau_rct43_tonnerre` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_rct43_rossignols.mp3` | `rameau_rct43_rossignols` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rameau_rct43_chaconne.mp3` | `rameau_rct43_chaconne` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_allemande.mp3` | `couperin_art_allemande` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_prelude_1.mp3` | `couperin_art_prelude_1` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_prelude_2.mp3` | `couperin_art_prelude_2` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_prelude_3.mp3` | `couperin_art_prelude_3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_prelude_4.mp3` | `couperin_art_prelude_4` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_prelude_5.mp3` | `couperin_art_prelude_5` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_prelude_6.mp3` | `couperin_art_prelude_6` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_prelude_7.mp3` | `couperin_art_prelude_7` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_art_prelude_8.mp3` | `couperin_art_prelude_8` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_aspiratio.mp3` | `couperin_aspiratio` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_dialogus.mp3` | `couperin_dialogus` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_precatio.mp3` | `couperin_precatio` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_salve_regina.mp3` | `couperin_salve_regina` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_salvum_me_fac.mp3` | `couperin_salvum_me_fac` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/couperin_usquequo.mp3` | `couperin_usquequo` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv155_toccata.mp3` | `buxtehude_buxwv155_toccata` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv185_erhalt_uns.mp3` | `buxtehude_buxwv185_erhalt_uns` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv208_nun_bitten.mp3` | `buxtehude_buxwv208_nun_bitten` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv209_nun_bitten.mp3` | `buxtehude_buxwv209_nun_bitten` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv69_laudate.mp3` | `buxtehude_buxwv69_laudate` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv4_alles.mp3` | `buxtehude_buxwv4_alles` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv75_ad_pedes.mp3` | `buxtehude_buxwv75_ad_pedes` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv75_ad_genua.mp3` | `buxtehude_buxwv75_ad_genua` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv75_ad_manus.mp3` | `buxtehude_buxwv75_ad_manus` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv75_ad_latus.mp3` | `buxtehude_buxwv75_ad_latus` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv75_ad_pectus.mp3` | `buxtehude_buxwv75_ad_pectus` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv75_ad_cor.mp3` | `buxtehude_buxwv75_ad_cor` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv75_ad_faciem.mp3` | `buxtehude_buxwv75_ad_faciem` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/gesualdo_dolcissima.mp3` | `gesualdo_dolcissima` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/franck_fwv30_prelude.mp3` | `franck_fwv30_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/franck_fwv62_ave_maria.mp3` | `franck_fwv62_ave_maria` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bruckner_wab129_perger.mp3` | `bruckner_wab129_perger` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_1_i.mp3` | `reger_op42_1_i` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_1_ii.mp3` | `reger_op42_1_ii` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_1_iii.mp3` | `reger_op42_1_iii` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_2_i.mp3` | `reger_op42_2_i` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_2_ii.mp3` | `reger_op42_2_ii` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_2_iii.mp3` | `reger_op42_2_iii` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_3_i.mp3` | `reger_op42_3_i` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_3_ii.mp3` | `reger_op42_3_ii` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_3_iii.mp3` | `reger_op42_3_iii` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op42_3_iv.mp3` | `reger_op42_3_iv` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op135a_10_grosser_gott.mp3` | `reger_op135a_10_grosser_gott` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_op138_3_nachtlied.mp3` | `reger_op138_3_nachtlied` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/reger_untrene.mp3` | `reger_untrene` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op11_prelude.mp3` | `scriabin_op11_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scriabin_op59_prelude.mp3` | `scriabin_op59_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/cellier_oh_woman_sweet_woman.mp3` | `cellier_oh_woman_sweet_woman` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/lehmann_bouton_de_rose.mp3` | `lehmann_bouton_de_rose` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/horrocks_cottage_cradle_song.mp3` | `horrocks_cottage_cradle_song` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/flegier_le_cor.mp3` | `flegier_le_cor` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mounsey_no_3_i_can_bid_thee_now_fare.mp3` | `mounsey_no_3_i_can_bid_thee_now_fare` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/dvorak_b152_echo_of_songs_b_152.mp3` | `dvorak_b152_echo_of_songs_b_152` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/dvorak_op105_string_quartet_no_14_op_105.mp3` | `dvorak_op105_string_quartet_no_14_op_105` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/dvorak_op34_string_quartet_no_9_op_34.mp3` | `dvorak_op34_string_quartet_no_9_op_34` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/dvorak_op51_string_quartet_no_10_op_51.mp3` | `dvorak_op51_string_quartet_no_10_op_51` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/sullivan_the_long_day_closes.mp3` | `sullivan_the_long_day_closes` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/browne_forever_thine.mp3` | `browne_forever_thine` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/holmes_charme_du_jour.mp3` | `holmes_charme_du_jour` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/saintsaens_o94_pour_cor.mp3` | `saintsaens_o94_pour_cor` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/cpebach_h288_rondo_in_e_flat_major.mp3` | `cpebach_h288_rondo_in_e_flat_major` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/gounod_meditation_sur_le_premier_pr.mp3` | `gounod_meditation_sur_le_premier_pr` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/gounod_le_soir_cg_441.mp3` | `gounod_le_soir_cg_441` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/stanford_op117_no_5_fare_well.mp3` | `stanford_op117_no_5_fare_well` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wood_ethiopia_saluting_the_colour.mp3` | `wood_ethiopia_saluting_the_colour` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/cschumann_die_gute_nacht.mp3` | `cschumann_die_gute_nacht` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/cschumann_lorelei.mp3` | `cschumann_lorelei` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/cschumann_op12_no_02_er_ist_gekommen_in_stu.mp3` | `cschumann_op12_no_02_er_ist_gekommen_in_stu` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/cschumann_op12_no_04_liebst_du_um_schonheit.mp3` | `cschumann_op12_no_04_liebst_du_um_schonheit` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/debussy_no_02_la_grotte_aupres_de_ce.mp3` | `debussy_no_02_la_grotte_aupres_de_ce` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/debussy_no_01_rondel_le_temps_a_lais.mp3` | `debussy_no_01_rondel_le_temps_a_lais` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/debussy_no_03_rondel_pour_ce_que_pla.mp3` | `debussy_no_03_rondel_pour_ce_que_pla` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/debussy_op10_string_quartet_in_g_minor_op.mp3` | `debussy_op10_string_quartet_in_g_minor_op` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/monteverdi_o_tu_ch_innanzi_morte_l_orfe.mp3` | `monteverdi_o_tu_ch_innanzi_morte_l_orfe` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/grandval_chanson_de_barberine.mp3` | `grandval_chanson_de_barberine` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schroter_no_18_amor_im_tanz.mp3` | `schroter_no_18_amor_im_tanz` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/buxtehude_buxwv155_buxwv_155.mp3` | `buxtehude_buxwv155_buxwv_155` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scarlatti_sonata_in_c_major.mp3` | `scarlatti_sonata_in_c_major` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/scarlatti_k11_joh_kuhnau_s_neue_klavierubu.mp3` | `scarlatti_k11_joh_kuhnau_s_neue_klavierubu` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/grieg_o5_ich_liebe_dich.mp3` | `grieg_o5_ich_liebe_dich` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/grieg_o65_bryllupsdag_pa_troldhaugen.mp3` | `grieg_o65_bryllupsdag_pa_troldhaugen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/gambarini_behold_behold_and_listen.mp3` | `gambarini_behold_behold_and_listen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/phillips_cushla_machree.mp3` | `phillips_cushla_machree` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/philp_bye_and_bye.mp3` | `philp_bye_and_bye` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/dickson_destiny.mp3` | `dickson_destiny` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/chabrier_ballade_des_gros_dindons.mp3` | `chabrier_ballade_des_gros_dindons` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/humperdinck_ein_geistlich_abendlied.mp3` | `humperdinck_ein_geistlich_abendlied` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/satie_chez_le_docteur.mp3` | `satie_chez_le_docteur` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/hensel_op277_string_quartet_in_e_flat_maj.mp3` | `hensel_op277_string_quartet_in_e_flat_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mendelssohn_op12_string_quartet_no_1_op_12.mp3` | `mendelssohn_op12_string_quartet_no_1_op_12` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mendelssohn_op13_string_quartet_no_2_op_13.mp3` | `mendelssohn_op13_string_quartet_no_2_op_13` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mendelssohn_op44no1_string_quartet_no_3_op_44_no.mp3` | `mendelssohn_op44no1_string_quartet_no_3_op_44_no` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mendelssohn_op44no2_string_quartet_no_4_in_e_min.mp3` | `mendelssohn_op44no2_string_quartet_no_4_in_e_min` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mendelssohn_op63_no_2_abschiedslied_der_zugvo.mp3` | `mendelssohn_op63_no_2_abschiedslied_der_zugvo` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mendelssohn_op63_no_3_gruss_mwv_j_8.mp3` | `mendelssohn_op63_no_3_gruss_mwv_j_8` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/sor_s35_no_14_etude.mp3` | `sor_s35_no_14_etude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/tarrega_adelita.mp3` | `tarrega_adelita` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/liszt_second_ballade.mp3` | `liszt_second_ballade` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/liszt_s270b_no_2_pace_non_trovo.mp3` | `liszt_s270b_no_2_pace_non_trovo` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d118_gretchen_am_spinnrade_d_118.mp3` | `schubert_d118_gretchen_am_spinnrade_d_118` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d179_liebesrausch_d_179.mp3` | `schubert_d179_liebesrausch_d_179` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d18_string_quartet_in_g_minor_d.mp3` | `schubert_d18_string_quartet_in_g_minor_d` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d280_das_rosenband_d_280.mp3` | `schubert_d280_das_rosenband_d_280` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d328_der_erlkonig_d_328.mp3` | `schubert_d328_der_erlkonig_d_328` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d353_string_quartet_in_e_major_d.mp3` | `schubert_d353_string_quartet_in_e_major_d` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d36_string_quartet_in_b_flat_maj.mp3` | `schubert_d36_string_quartet_in_b_flat_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d547_an_die_musik_d_547.mp3` | `schubert_d547_an_die_musik_d_547` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d651_himmelsfunken_d_651.mp3` | `schubert_d651_himmelsfunken_d_651` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d703_string_quartet_in_c_minor_d.mp3` | `schubert_d703_string_quartet_in_c_minor_d` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d710_im_gegenwartigen_vergangenes.mp3` | `schubert_d710_im_gegenwartigen_vergangenes` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d774_auf_dem_wasser_zu_singen_d_7.mp3` | `schubert_d774_auf_dem_wasser_zu_singen_d_7` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_04_danksagung_an_den_bach.mp3` | `schubert_d795_no_04_danksagung_an_den_bach` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_01_das_wandern.mp3` | `schubert_d795_no_01_das_wandern` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_14_der_jager.mp3` | `schubert_d795_no_14_der_jager` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_19_der_muller_und_der_bac.mp3` | `schubert_d795_no_19_der_muller_und_der_bac` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_06_der_neugierige.mp3` | `schubert_d795_no_06_der_neugierige` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_20_des_baches_wiegenlied.mp3` | `schubert_d795_no_20_des_baches_wiegenlied` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_09_des_mullers_blumen.mp3` | `schubert_d795_no_09_des_mullers_blumen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_17_die_bose_farbe.mp3` | `schubert_d795_no_17_die_bose_farbe` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_16_die_liebe_farbe.mp3` | `schubert_d795_no_16_die_liebe_farbe` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_15_eifersucht_und_stolz.mp3` | `schubert_d795_no_15_eifersucht_und_stolz` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_11_mein.mp3` | `schubert_d795_no_11_mein` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schubert_d795_no_13_mit_dem_grunen_lautenb.mp3` | `schubert_d795_no_13_mit_dem_grunen_lautenb` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/chopin_b130_etudes_de_perfection_de_la_m.mp3` | `chopin_b130_etudes_de_perfection_de_la_m` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/chopin_op10_etude_a_moll.mp3` | `chopin_op10_etude_a_moll` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/chopin_op28_funeral_march.mp3` | `chopin_op28_funeral_march` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/chopin_op28_suffocation.mp3` | `chopin_op28_suffocation` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/chopin_op45_prelude.mp3` | `chopin_op45_prelude` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/chopin_op74_no_2_wiosna.mp3` | `chopin_op74_no_2_wiosna` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/chopin_op74_no_1_zyczenie.mp3` | `chopin_op74_no_1_zyczenie` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/faure_op121_string_quartet_op_121.mp3` | `faure_op121_string_quartet_op_121` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/faure_op21_no_3_adieu.mp3` | `faure_op21_no_3_adieu` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/faure_op21_no_1_rencontre.mp3` | `faure_op21_no_1_rencontre` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/faure_op21_no_2_toujours.mp3` | `faure_op21_no_2_toujours` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/handel_from_the_aylesford_piecesb13.mp3` | `handel_from_the_aylesford_piecesb13` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bizet_no_2_adieux_a_suzon.mp3` | `bizet_no_2_adieux_a_suzon` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rossini_no_5_l_invito.mp3` | `rossini_no_5_l_invito` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/verdi_no_3_in_solitaria_stanza.mp3` | `verdi_no_3_in_solitaria_stanza` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/purcell_fairest_isle.mp3` | `purcell_fairest_isle` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_no_04_das_standchen.mp3` | `wolf_no_04_das_standchen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_no_01_der_freund.mp3` | `wolf_no_01_der_freund` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_no_10_der_glucksritter.mp3` | `wolf_no_10_der_glucksritter` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_no_02_der_musikant.mp3` | `wolf_no_02_der_musikant` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_no_13_der_scholar.mp3` | `wolf_no_13_der_scholar` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_no_09_der_schreckenberger.mp3` | `wolf_no_09_der_schreckenberger` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_no_05_der_soldat_i.mp3` | `wolf_no_05_der_soldat_i` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_no_06_der_soldat_ii.mp3` | `wolf_no_06_der_soldat_ii` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_italian_serenade.mp3` | `wolf_italian_serenade` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wolf_string_quartet.mp3` | `wolf_string_quartet` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/unknown_2e_verset.mp3` | `unknown_2e_verset` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mhaydn_lyons_hymntune.mp3` | `mhaydn_lyons_hymntune` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_matthaus_passion.mp3` | `bach_matthaus_passion` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1068_from_suite_no_3_in_d_bwv_106.mp3` | `bach_bwv1068_from_suite_no_3_in_d_bwv_106` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1079_musicalisches_opfer.mp3` | `bach_bwv1079_musicalisches_opfer` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/bach_bwv1079_musikalisches_opfer.mp3` | `bach_bwv1079_musikalisches_opfer` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/strauss2_thunder_and_lightning.mp3` | `strauss2_thunder_and_lightning` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op121_no_1_denn_es_gehet_dem_mensc.mp3` | `brahms_op121_no_1_denn_es_gehet_dem_mensc` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op121_no_2_ich_wandte_mich_und_sah.mp3` | `brahms_op121_no_2_ich_wandte_mich_und_sah` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op121_no_3_o_tod_wie_bitter_bist_d.mp3` | `brahms_op121_no_3_o_tod_wie_bitter_bist_d` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op121_no_4_wenn_ich_mit_menschen_u.mp3` | `brahms_op121_no_4_wenn_ich_mit_menschen_u` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op14_no_4_ein_sonett.mp3` | `brahms_op14_no_4_ein_sonett` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op14_no_6_gang_zur_liebsten.mp3` | `brahms_op14_no_6_gang_zur_liebsten` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op14_no_3_murrays_ermordung.mp3` | `brahms_op14_no_3_murrays_ermordung` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op14_no_8_sehnsucht.mp3` | `brahms_op14_no_8_sehnsucht` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op14_no_7_standchen.mp3` | `brahms_op14_no_7_standchen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op51no1_string_quartet_no_1_op_51_no.mp3` | `brahms_op51no1_string_quartet_no_1_op_51_no` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op51no2_string_quartet_no_2_op_51_no.mp3` | `brahms_op51no2_string_quartet_no_2_op_51_no` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/brahms_op67_string_quartet_no_3_op_67.mp3` | `brahms_op67_string_quartet_no_3_op_67` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/dowland_ayresandlutesongsi_unquiet_thoughts.mp3` | `dowland_ayresandlutesongsi_unquiet_thoughts` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/haydn_hobiii1_string_quartet_in_b_flat_maj.mp3` | `haydn_hobiii1_string_quartet_in_b_flat_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/haydn_hobiii12_string_quartet_in_b_flat_maj.mp3` | `haydn_hobiii12_string_quartet_in_b_flat_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/haydn_hobiii19_string_quartet_in_c_major_ho.mp3` | `haydn_hobiii19_string_quartet_in_c_major_ho` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/haydn_hobiii2_string_quartet_in_e_flat_maj.mp3` | `haydn_hobiii2_string_quartet_in_e_flat_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/haydn_s10_no_06_a_pastoral_song_hob_xx.mp3` | `haydn_s10_no_06_a_pastoral_song_hob_xx` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/haydn_s10_no_01_despair_hob_xxvia28.mp3` | `haydn_s10_no_01_despair_hob_xxvia28` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/haydn_s10_no_02_fidelity_hob_xxvia30.mp3` | `haydn_s10_no_02_fidelity_hob_xxvia30` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/haydn_s10_no_08_o_tuneful_voice_hob_xx.mp3` | `haydn_s10_no_08_o_tuneful_voice_hob_xx` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/gottschalk_op100_la_mort_du_cygne.mp3` | `gottschalk_op100_la_mort_du_cygne` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op127_string_quartet_no_12_op_127.mp3` | `beethoven_op127_string_quartet_no_12_op_127` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op130_string_quartet_no_13_in_b_ma.mp3` | `beethoven_op130_string_quartet_no_13_in_b_ma` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op131_string_quartet_no_14_in_c_mi.mp3` | `beethoven_op131_string_quartet_no_14_in_c_mi` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op133_grosse_fuge_in_b_flat_major.mp3` | `beethoven_op133_grosse_fuge_in_b_flat_major` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op135_string_quartet_no_16_in_f_ma.mp3` | `beethoven_op135_string_quartet_no_16_in_f_ma` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op48_no_1_bitten.mp3` | `beethoven_op48_no_1_bitten` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op48_no_6_busslied.mp3` | `beethoven_op48_no_6_busslied` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op48_no_4_die_ehre_gottes_aus_der.mp3` | `beethoven_op48_no_4_die_ehre_gottes_aus_der` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op48_no_2_die_liebe_des_nachsten.mp3` | `beethoven_op48_no_2_die_liebe_des_nachsten` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op48_no_5_gottes_macht_und_vorseh.mp3` | `beethoven_op48_no_5_gottes_macht_und_vorseh` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op48_no_3_vom_tode.mp3` | `beethoven_op48_no_3_vom_tode` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op52_no_8_das_blumchen_wunderhold.mp3` | `beethoven_op52_no_8_das_blumchen_wunderhold` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op52_no_3_das_liedchen_von_der_ru.mp3` | `beethoven_op52_no_3_das_liedchen_von_der_ru` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op52_no_2_feuerfarb.mp3` | `beethoven_op52_no_2_feuerfarb` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op52_no_6_lied.mp3` | `beethoven_op52_no_6_lied` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/beethoven_op52_no_4_mailied.mp3` | `beethoven_op52_no_4_mailied` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/rimskykorsakov_extraite_de_fugues_op_17.mp3` | `rimskykorsakov_extraite_de_fugues_op_17` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/gibbons_the_silver_swan.mp3` | `gibbons_the_silver_swan` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/tchaikovsky_danse_napolitaine.mp3` | `tchaikovsky_danse_napolitaine` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_no_1_der_engel.mp3` | `wagner_wwv91_no_1_der_engel` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_no_3_im_treibhaus.mp3` | `wagner_wwv91_no_3_im_treibhaus` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_no_4_schmerzen.mp3` | `wagner_wwv91_no_4_schmerzen` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_no_2_stehe_still.mp3` | `wagner_wwv91_no_2_stehe_still` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/wagner_wwv91_no_5_traume.mp3` | `wagner_wwv91_no_5_traume` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op127_no_2_dein_angesicht.mp3` | `schumann_op127_no_2_dein_angesicht` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op127_no_3_es_leuchtet_meine_liebe.mp3` | `schumann_op127_no_3_es_leuchtet_meine_liebe` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op127_no_4_mein_altes_ross.mp3` | `schumann_op127_no_4_mein_altes_ross` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op127_no_5_schlusslied_des_narren.mp3` | `schumann_op127_no_5_schlusslied_des_narren` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op127_no_1_sangers_trost.mp3` | `schumann_op127_no_1_sangers_trost` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op25_no_15_aus_den_hebraischen_ge.mp3` | `schumann_op25_no_15_aus_den_hebraischen_ge` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op25_no_25_aus_den_ostlichen_rose.mp3` | `schumann_op25_no_25_aus_den_ostlichen_rose` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op25_no_03_der_nussbaum.mp3` | `schumann_op25_no_03_der_nussbaum` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op25_no_10_die_hochlander_witwe.mp3` | `schumann_op25_no_10_die_hochlander_witwe` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op25_no_07_die_lotosblume.mp3` | `schumann_op25_no_07_die_lotosblume` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op25_no_24_du_bist_wie_ein_blume.mp3` | `schumann_op25_no_24_du_bist_wie_ein_blume` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op25_no_02_freisinn.mp3` | `schumann_op25_no_02_freisinn` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op25_no_19_hauptmanns_weib.mp3` | `schumann_op25_no_19_hauptmanns_weib` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op41no1_string_quartet_no_1_op_41_no.mp3` | `schumann_op41no1_string_quartet_no_1_op_41_no` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/schumann_op41no3_string_quartet_no_3_op_41_no.mp3` | `schumann_op41no3_string_quartet_no_3_op_41_no` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/joplin_please_say_you_will.mp3` | `joplin_please_say_you_will` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/traditional_asaku_tomo.mp3` | `traditional_asaku_tomo` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mozart_notte_e_giorno_don_giovanni.mp3` | `mozart_notte_e_giorno_don_giovanni` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mozart_k155_string_quartet_no_2_in_d_maj.mp3` | `mozart_k155_string_quartet_no_2_in_d_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mozart_k156_string_quartet_no_3_in_g_maj.mp3` | `mozart_k156_string_quartet_no_3_in_g_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mozart_k157_string_quartet_no_4_in_c_maj.mp3` | `mozart_k157_string_quartet_no_4_in_c_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mozart_k158_string_quartet_no_5_in_f_maj.mp3` | `mozart_k158_string_quartet_no_5_in_f_maj` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mozart_k6_fragment.mp3` | `mozart_k6_fragment` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| removed_synth_preview | `previews/mozart_k309_piano_sonata_in_c_major_kv_3.mp3` | `mozart_k309_piano_sonata_in_c_major_kv_3` | recording_source_url empty: 15 s FluidSynth (FluidR3_GM) render of the score MIDI; tracked in git |
| deleted_release_asset | `https://github.com/LaDoger/music-library/releases/download/synth-v1/bach_bwv565_toccata_synth.mp3` | `bach_bwv565_toccata` | full-length FluidSynth render of the score MIDI (scripts/render_synth.py, data/cache/synth_renders.json) |
| deleted_release_asset | `https://github.com/LaDoger/music-library/releases/download/synth-v1/beethoven_op67_symphony5_synth.mp3` | `beethoven_op67_symphony5` | full-length FluidSynth render of the score MIDI (scripts/render_synth.py, data/cache/synth_renders.json) |
| deleted_release_asset | `https://github.com/LaDoger/music-library/releases/download/synth-v1/chopin_op10_12_revolutionary_synth.mp3` | `chopin_op10_12_revolutionary` | full-length FluidSynth render of the score MIDI (scripts/render_synth.py, data/cache/synth_renders.json) |
| deleted_release_asset | `https://github.com/LaDoger/music-library/releases/download/synth-v1/dvorak_new_world_finale_synth.mp3` | `dvorak_new_world_finale` | full-length FluidSynth render of the score MIDI (scripts/render_synth.py, data/cache/synth_renders.json) |
| deleted_release_asset | `https://github.com/LaDoger/music-library/releases/download/synth-v1/grieg_peer_gynt_mountain_king_synth.mp3` | `grieg_peer_gynt_mountain_king` | full-length FluidSynth render of the score MIDI (scripts/render_synth.py, data/cache/synth_renders.json) |
| deleted_release_asset | `https://github.com/LaDoger/music-library/releases/download/synth-v1/mussorgsky_night_on_bald_mountain_synth.mp3` | `mussorgsky_night_on_bald_mountain` | full-length FluidSynth render of the score MIDI (scripts/render_synth.py, data/cache/synth_renders.json) |
| deleted_release_asset | `https://github.com/LaDoger/music-library/releases/download/synth-v1/mussorgsky_pictures_great_gate_kiev_synth.mp3` | `mussorgsky_pictures_great_gate_kiev` | full-length FluidSynth render of the score MIDI (scripts/render_synth.py, data/cache/synth_renders.json) |

## Kept: previews cut from real recordings

| path | item id |
|---|---|
| `previews/bach_bwv565_toccata.mp3` | `bach_bwv565_toccata` |
| `previews/bach_bwv846_prelude.mp3` | `bach_bwv846_prelude` |
| `previews/beethoven_op27_2_moonlight1.mp3` | `beethoven_op27_2_moonlight1` |
| `previews/beethoven_op27_2_moonlight3.mp3` | `beethoven_op27_2_moonlight3` |
| `previews/beethoven_op67_symphony5.mp3` | `beethoven_op67_symphony5` |
| `previews/beethoven_op84_egmont.mp3` | `beethoven_op84_egmont` |
| `previews/beethoven_woo59_fur_elise.mp3` | `beethoven_woo59_fur_elise` |
| `previews/berlioz_fantastique_witches_sabbath.mp3` | `berlioz_fantastique_witches_sabbath` |
| `previews/bizet_carmen_toreador.mp3` | `bizet_carmen_toreador` |
| `previews/borodin_quartet2_nocturne.mp3` | `borodin_quartet2_nocturne` |
| `previews/borodin_steppes.mp3` | `borodin_steppes` |
| `previews/brahms_hungarian_dance_5.mp3` | `brahms_hungarian_dance_5` |
| `previews/chopin_op10_12_revolutionary.mp3` | `chopin_op10_12_revolutionary` |
| `previews/chopin_op28_15_raindrop.mp3` | `chopin_op28_15_raindrop` |
| `previews/chopin_op9_2_nocturne.mp3` | `chopin_op9_2_nocturne` |
| `previews/debussy_danse_sacree.mp3` | `debussy_danse_sacree` |
| `previews/dvorak_new_world_finale.mp3` | `dvorak_new_world_finale` |
| `previews/dvorak_new_world_largo.mp3` | `dvorak_new_world_largo` |
| `previews/elgar_pomp_circumstance_1.mp3` | `elgar_pomp_circumstance_1` |
| `previews/grieg_peer_gynt_morning_mood.mp3` | `grieg_peer_gynt_morning_mood` |
| `previews/grieg_peer_gynt_mountain_king.mp3` | `grieg_peer_gynt_mountain_king` |
| `previews/handel_hwv349_hornpipe.mp3` | `handel_hwv349_hornpipe` |
| `previews/holst_planets_jupiter.mp3` | `holst_planets_jupiter` |
| `previews/holst_planets_mars.mp3` | `holst_planets_mars` |
| `previews/liszt_hungarian_rhapsody_2.mp3` | `liszt_hungarian_rhapsody_2` |
| `previews/liszt_la_campanella.mp3` | `liszt_la_campanella` |
| `previews/liszt_liebestraum_3.mp3` | `liszt_liebestraum_3` |
| `previews/mahler_adagietto.mp3` | `mahler_adagietto` |
| `previews/mendelssohn_op26_hebrides.mp3` | `mendelssohn_op26_hebrides` |
| `previews/mozart_k331_rondo_turca.mp3` | `mozart_k331_rondo_turca` |
| `previews/mozart_k550_symphony40.mp3` | `mozart_k550_symphony40` |
| `previews/mussorgsky_night_on_bald_mountain.mp3` | `mussorgsky_night_on_bald_mountain` |
| `previews/mussorgsky_pictures_baba_yaga.mp3` | `mussorgsky_pictures_baba_yaga` |
| `previews/mussorgsky_pictures_great_gate_kiev.mp3` | `mussorgsky_pictures_great_gate_kiev` |
| `previews/mussorgsky_pictures_promenade.mp3` | `mussorgsky_pictures_promenade` |
| `previews/offenbach_orpheus_cancan.mp3` | `offenbach_orpheus_cancan` |
| `previews/rachmaninoff_piano_concerto_2.mp3` | `rachmaninoff_piano_concerto_2` |
| `previews/rachmaninoff_prelude_op3_no2.mp3` | `rachmaninoff_prelude_op3_no2` |
| `previews/ravel_pavane.mp3` | `ravel_pavane` |
| `previews/rimskykorsakov_flight_of_the_bumblebee.mp3` | `rimskykorsakov_flight_of_the_bumblebee` |
| `previews/rimskykorsakov_scheherazade_sea.mp3` | `rimskykorsakov_scheherazade_sea` |
| `previews/rstrauss_zarathustra_sunrise.mp3` | `rstrauss_zarathustra_sunrise` |
| `previews/saintsaens_carnival_aquarium.mp3` | `saintsaens_carnival_aquarium` |
| `previews/saintsaens_danse_macabre.mp3` | `saintsaens_danse_macabre` |
| `previews/saintsaens_samson_bacchanale.mp3` | `saintsaens_samson_bacchanale` |
| `previews/satie_gymnopedie_1.mp3` | `satie_gymnopedie_1` |
| `previews/schubert_d328_erlkonig.mp3` | `schubert_d328_erlkonig` |
| `previews/schumann_op15_7_traumerei.mp3` | `schumann_op15_7_traumerei` |
| `previews/smetana_vltava.mp3` | `smetana_vltava` |
| `previews/strauss1_radetzky.mp3` | `strauss1_radetzky` |
| `previews/strauss2_blue_danube.mp3` | `strauss2_blue_danube` |
| `previews/suppe_light_cavalry.mp3` | `suppe_light_cavalry` |
| `previews/tchaikovsky_1812_overture.mp3` | `tchaikovsky_1812_overture` |
| `previews/tchaikovsky_nutcracker_waltz_of_flowers.mp3` | `tchaikovsky_nutcracker_waltz_of_flowers` |
| `previews/tchaikovsky_piano_concerto_1.mp3` | `tchaikovsky_piano_concerto_1` |
| `previews/tchaikovsky_romeo_and_juliet.mp3` | `tchaikovsky_romeo_and_juliet` |
| `previews/tchaikovsky_swan_lake_act2_scene.mp3` | `tchaikovsky_swan_lake_act2_scene` |
| `previews/verdi_aida_triumphal_march.mp3` | `verdi_aida_triumphal_march` |
| `previews/verdi_requiem_dies_irae.mp3` | `verdi_requiem_dies_irae` |
| `previews/vivaldi_rv269_spring.mp3` | `vivaldi_rv269_spring` |
| `previews/vivaldi_rv315_summer_storm.mp3` | `vivaldi_rv315_summer_storm` |
| `previews/wagner_lohengrin_bridal_chorus.mp3` | `wagner_lohengrin_bridal_chorus` |
| `previews/wagner_tristan_prelude.mp3` | `wagner_tristan_prelude` |
| `previews/wagner_walkure_ride_of_the_valkyries.mp3` | `wagner_walkure_ride_of_the_valkyries` |
