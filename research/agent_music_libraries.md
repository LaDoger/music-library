# Agent-oriented music libraries: does one already exist?

Research date: 2026-10-09. Researcher: Grok Build (grok-4.7). Scope: a machine-readable catalogue of legally usable music (public domain or Creative Commons) with editable scores (MIDI and/or MusicXML), recordings, per-item licence metadata fit for commercial video, and agent access (API, MCP, dataset, CLI, or structured JSON/CSV). Human sheet-music sites without that packaging are noted only as bulk sources.

Closeness is scored 0–5. A 5 would be the whole package: per-item commercial-video clearance, editable scores, recordings with their own licences, an agent query surface, and multi-genre material good enough to drop into a video. Nothing found scored 4 or 5.

Direct fetches of a few hosts (`freepd.com`, `incompetech.com`, `thesession.org`) were blocked from this environment (SSRF filter). Those claims rest on search snippets of the primary pages and are marked as such.

## 1. Executive summary

**Novel? Yes**, as an agent-facing production library.

No public project found in this pass combines all of the following in one catalogue an agent can query: (1) music that is public domain or Creative Commons and cleared, per file, for commercial video; (2) editable scores (MIDI and/or MusicXML, or LilyPond that renders to those); (3) recordings whose licence is separate from the composition; (4) an API, MCP server, dataset loader, or stable JSON/CSV built for production use rather than a one-off research dump. The pieces exist apart. PDMX, OpenScore, and Mutopia are large or careful public-domain score corpora with files and metadata, and they stop there: no performance recordings as a product, and no agent server. Jamendo, Freesound, the Free Music Archive dataset, Incompetech’s `pieces.json`, and Epidemic Sound’s Partner API are agent- or developer-facing audio catalogues, and they stop there: no editable scores, and often a licence that is non-commercial, attribution-only, or a paid sync deal rather than PD/CC. ASAP is the rare research set that really pairs MusicXML with performances, under CC BY-NC-SA, so it is not a commercial-video source. MCP registries (Glama, Smithery, PulseMCP, mcp.so, and community lists) are full of composition tools and DAW bridges (MuseScore, Ableton, MIDI file writers). None of those is a licensed library. The gap worth building is the curated join: vetted score plus vetted recording, mood and video-use metadata, and a small query surface. The music itself should be reused, not re-engraved from scratch.

## 2. Closest projects

| name | score | URL | access | gaps |
| --- | --- | --- | --- | --- |
| PDMX | 3 | https://github.com/pnlong/PDMX/ and https://zenodo.org/records/15571083 | Zenodo bulk download; Python `pdmx` loader; per-song metadata JSON, MXL, PDF, MIDI | No performance recordings. No search API or MCP. Authors flag a MuseScore public-vs-internal licence conflict on 12.29% (31,221) of files and tell users to keep the `no_license_conflict` subset (222,856 of 254,077). Quality is user-generated and piano-heavy. Not curated for video. |
| OpenScore (Lieder, String Quartets, orchestral) | 3 | https://fourscoreandmore.org/openscore/ , https://github.com/OpenScore/Lieder , https://github.com/OpenScore/StringQuartets | Git clone; YAML metadata (`scores.yaml`, `composers.yaml`); Zenodo snapshot of Lieder (https://zenodo.org/records/15450144). HF mirrors exist for OMR, not as a music API | CC0 scores only. No licensed performance audio. Classical subsets (song, quartet, a smaller orchestral set). GitHub org page lists Lieder and String Quartets; the 2025 orchestral collection is described on the project site with “full index to follow.” Not an agent server. |
| Mutopia Project | 3 | https://www.mutopiaproject.org/ and https://github.com/MutopiaProject/MutopiaProject | Website, FTP (listed by re3data as https://www.mutopiaproject.org/ftp/), full LilyPond tree on GitHub | Homepage states 2,124 pieces in PDF, MIDI, and LilyPond, each with its own PD or CC licence. MIDI is a synth preview, not a performance. No query API. Mostly classical, guitar and keyboard heavy. Repo activity noted through Nov 2024; the “2,124” figure may lag the git tree. |
| ASAP | 2 | https://github.com/fosfrancesco/asap-dataset | GitHub dataset; `metadata.csv` joins MusicXML, score MIDI, performance MIDI, and some audio | Closest public *pairing* of editable scores and performances (222 scores, 1,067 performances; many audio files point at MAESTRO). Dataset README: CC BY-NC-SA 4.0. Piano only. Research alignment corpus, not a video library. |
| Incompetech agent catalogue | 2 | https://incompetech.com/llms.txt (snippet; direct fetch blocked) | `llms.txt` points agents at a full-catalogue JSON (`https://incompetech.com/music/royalty-free/pieces.json` per that file) | CC BY 4.0 recordings by Kevin MacLeod. Attribution required. No scores. Not public domain (the same author’s FreePD tracks are the CC0 exception). Strongest “here is JSON for an agent” pattern found for stock music. |
| Jamendo API | 2 | https://developer.jamendo.com/ | REST JSON at `api.jamendo.com` (v3.0 documented on the developer site). Non-commercial apps cited at up to 35,000 requests/month by a secondary summary of the API | Audio plus per-track CC licence. No scores. Many tracks are NC or ND. Jamendo’s own licensing pages say commercial video is a separate paid product (Jamendo Licensing), not the free CC stream. |
| FMA dataset | 2 | https://github.com/mdeff/fma | Static CSV + audio. Hugging Face pack: https://huggingface.co/datasets/benjamin-paine/free-music-archive-full | 106k CC tracks, metadata under CC BY 4.0, per-file licences, including a commercial-use filter in the HF pack. Live FMA API was shut down (https://freemusicarchive.org/app-developers). No scores. Rights are whatever each artist chose, including NC. |
| Freesound API (+ MCP wrappers) | 2 | https://freesound.org/docs/api/ | Token REST API; OAuth2 for original-quality download. MCP servers such as https://github.com/johnkimdw/freesound-mcp-server and https://glama.ai/mcp/servers/timjrobinson/FreesoundMCPServer | CC audio with a `license` field (Attribution, Attribution NonCommercial, CC0). Sound-effects first. API terms: free only for non-commercial use; commercial API use needs a separate licence. Previews do not need OAuth; originals do. No scores. |
| IMSLP API | 2 | https://imslp.org/wiki/IMSLP:API | Ad-hoc JSON/PHP work lists (`API.ISCR.php?account=worklist/...`) plus MediaWiki API. Clients: https://github.com/jlumbroso/imslp , https://github.com/xgreymx/easy-imslp | Huge PD score library for humans. Files are mostly scans, not MIDI/MusicXML. Recordings on the site have their own copyright. Download waits and a subscription sit in front of some files. Not an agent production catalogue. |
| Internet Archive search + Wikimedia Commons | 2 | https://archive.org/advancedsearch.php and https://commons.wikimedia.org/w/api.php | Lucene JSON (`output=json`) on Archive; MediaWiki `imageinfo` / `extmetadata` on Commons, plus the Wikimedia REST file API | Real PD and CC audio, including U.S. Marine Band performances and some Musopen sets. Licence is whatever the uploader declared; many items have none. No joined score. Not curated for video mood or quality. |

Honourable mentions at 2, not in the ten: The Session (ABC + JSON API), SoundSafari’s CC0 audio dump, FreePD, music21’s bundled corpus, Epidemic Sound’s Partner API, Free To Use’s public API, dig.ccMixter’s query API. They are written up below. Composition and DAW MCP servers score 1: they make or edit music, they do not serve a licensed library.

## 3. Detailed findings by category

### 3.1 Score and symbolic datasets

**PDMX** is the largest copyright-free MusicXML collection in the open literature. The ICASSP 2025 paper (arXiv:2409.10831) describes 254,077 files, about 6,250 hours, taken from MuseScore items marked Public Domain Mark or CC0, with genre, tag, description, and popularity metadata. Zenodo v9 (1 June 2025) adds MXL, PDF, and MIDI where conversion worked. The same record documents the licence discrepancy: public MuseScore labels and the copyright field inside the file disagree for 31,221 songs. Use `subset:no_license_conflict` (222,856). The dataset is a training corpus. It is not a video cue library, ratings are a weak quality filter, and a large share is solo piano. There is no HTTP search API.

**OpenScore** (Mark Gotham, Peter Jonas, and volunteers) is the high-quality end of the same idea. Lieder: 1,300+ nineteenth-century songs, CC0, MuseScore sources, YAML catalogue, batch-convert JSON for MusicXML/MIDI/PDF via MuseScore’s CLI. String quartets: CC0; the 2023 DLfM paper reported 100+ quartets / 350+ movements, and the project site later says about 700 movements across about 200 quartets. A third, orchestral, collection is announced on https://fourscoreandmore.org/openscore/ (“c.100 movements”, index still forthcoming). Hugging Face sets `guangyangmusic/OpenScore-Lieder` and `guangyangmusic/OpenScore-StringQuartets` are OMR page-image derivatives (CC BY on the derivation; underlying scores CC0), not playback libraries.

**Mutopia** typesets public-domain editions in LilyPond and ships PDF, MIDI, and `.ly`. The homepage says every piece may be downloaded, modified, performed, and recorded, under a per-piece PD or CC licence. re3data lists FTP as the machine interface. This is the cleanest small classical engraving corpus with an explicit licence on each work. It is not multi-genre popular music, and the MIDI is not a performance.

**music21 corpus** (https://github.com/cuthbertLab/music21, BSD for the code). The README states that the underlying music is believed to be public domain in the US, EU, and Canada, and that encodings are public domain or used by permission. A no-corpus distribution exists for people who need a strict BSD tree. Access is `corpus.parse(...)` inside Python. Useful as a seed and as a parser. Far too small, and too mixed in encoding licence, to be the production library.

**KernScores** (https://kern.ccarh.org/, Humdrum `**kern`, also mirrored in https://github.com/humdrum-tools/humdrum-data). Craig Sapp’s library; the site reports on the order of 7.9 million notes in about 109,000 files, with MIDI translations. Public-domain holdings are open; copyrighted holdings need a login. Good symbolic source after a PD filter. Not MusicXML-native, no recordings, no agent API beyond HTTP file fetch (`humcat` shortcuts).

**ASAP** pairs MusicXML and quantized MIDI scores with performance MIDI and, for a subset, audio, plus beat and key annotations. Many audio paths are MAESTRO files. The dataset README’s licence is CC BY-NC-SA 4.0, which rules out commercial video. Piano only, 15 composers. Structurally the nearest “score plus recording” dataset, legally the wrong one.

**MAESTRO** (https://magenta.withgoogle.com/datasets/maestro): about 200 hours of Disklavier piano, aligned audio and MIDI, CSV/JSON metadata. Google’s licence is CC BY-NC-SA 4.0. Virtuosic performances, not a score library, not commercial.

**GiantMIDI-Piano** (https://github.com/bytedance/GiantMIDI-Piano): 10,855 transcribed solo-piano MIDIs, CC BY 4.0 on the release. Sources are web/YouTube recordings run through a transcriber trained on MAESTRO. Even when the composition is old, the performance and the transcription of that recording are a poor fit for a clean commercial-video licence. Research corpus.

**Lakh MIDI** (https://colinraffel.com/projects/lmd/): 176,581 unique MIDI files; 45,129 matched to the Million Song Dataset. The *collection* is CC BY 4.0. Raffel states he did not transcribe the files and that MIDI copyright meta-events are too inconsistent to attribute them. The matched audio is pop, largely still in copyright. Unusable as a commercial-video score source. Derivatives (Lakh Pianoroll, Slakh2100 synthesized audio at https://github.com/ethman/Slakh, also CC BY 4.0) inherit that problem. Slakh is useful as a demo of “MIDI rendered to stems,” not as repertoire.

**Other MIDI piles, scored 1.** Discover MIDI (https://huggingface.co/datasets/projectlosangeles/Discover-MIDI-Dataset) claims 6.74M files under CC BY-NC-SA 4.0. Aria-MIDI (https://huggingface.co/datasets/loubb/aria-midi) is 1.18M transcribed piano hours, CC BY-NC-SA 4.0. nightingale-ai/midi-data (https://github.com/nightingale-ai/midi-data) is 221,599 MIDIs “freely available online,” with no per-file licence. BitMidi (https://github.com/feross/bitmidi.com) is a popular-music MIDI jukebox, not a PD catalogue. Wikifonia lead sheets (~6,000 MusicXML) circulate in converters such as https://github.com/frothywater/wikifonia-dataset, whose README calls the set public domain; that claim is not safe. Wikifonia was withdrawn over copyright, and the text2score dataset card (below) still marks Wikifonia non-commercial. MetaMIDI and SymphonyNet show up in the PDMX comparison table as large MIDI sets; they are not PD production libraries.

**text2score** (https://huggingface.co/datasets/emotionwave-company/text2score): 621,162 ABC pieces, including 253,339 from PDMX. The card says the full mix is non-commercial because ASAP is CC BY-NC-SA and Wikifonia is restricted. A reminder that “contains PDMX” does not make the bundle safe.

**MuseTrainer library** (https://github.com/musetrainer/library): a small public-domain MusicXML teaching set (Für Elise, Gymnopédie, and similar) with a generated site. Score 2 as a tiny clean sample, not a corpus.

**CPDL / ChoralWiki** (https://www.cpdl.org/wiki/index.php/Main_Page): on the order of 50,000+ free choral score pages (main page counter; the 2018 anniversary note was ~31,000). Mostly PD editions plus some composer-donated modern works. Files are PDF and often MXL/MIDI. It is MediaWiki, so a MediaWiki API exists; forum threads from 2014 through 2026 show outsiders asking for it and being told there is no custom catalogue API, and that a full mirror is not freely redistributable because some editions are not free. Per-edition licence must be read. Human library, scrape-only for agents. Score 2 as a source of choral PD editions, 1 as an agent product.

### 3.2 Audio datasets and royalty-free catalogues

**Free Music Archive.** The 2017 FMA research set (Defferrard et al., https://github.com/mdeff/fma) is still the practical dump: full-length CC audio, genre taxonomy, track-level licence fields. Metadata CC BY 4.0; code MIT. The HF “full” pack notes a configuration that keeps only commercially usable files. The live site (https://freemusicarchive.org/app-developers) says the old developer API was turned off because of load, forbids hotlinking, and forbids unapproved scraping. Agents can use the frozen dataset. They cannot treat FMA as a live API.

**Freesound** is the best live CC audio API. Search filters include tags, duration, and licence. Sound records expose `license` and preview URLs without OAuth; original download requires OAuth2. Terms (https://freesound.org/docs/api/terms_of_use.html, pointing at https://freesound.org/help/tos_api/): free API use is non-commercial; commercial applications must contact Freesound. A 2024 API-list reply from Frederic Font confirms originals need OAuth and that a commercial app needs a commercial API licence even for CC0/CC-BY sounds. Content is mostly effects and field recordings, with a music category. Several MCP wrappers search it for video editors. That is agent access to CC audio, not to scores.

**Jamendo.** Developer portal: https://developer.jamendo.com/. The catalogue is independent music under mixed CC terms (BY, SA, NC, ND), and the API returns stream URLs and the licence. Jamendo’s legal pages (https://www.jamendo.com/legal/licenses and https://licensing.jamendo.com/) separate “free for personal use” from Jamendo Licensing, the paid sync product for commercial video. An agent that treats “it’s on Jamendo” as “safe for a monetised video” will be wrong on a large share of tracks.

**Pixabay Music.** Content Licence (summary: https://pixabay.com/service/license-summary/) allows commercial use, modification, and no required attribution, and forbids standalone redistribution. FAQ (https://pixabay.com/service/faq/) explicitly allows music inside videos that are sold, including client work, and warns that some tracks still trip YouTube Content ID. Pre-9 January 2019 uploads were CC0; newer uploads are the Pixabay licence, not CC. The developer API (https://pixabay.com/api/docs/) searches images and videos only. There is no documented music endpoint. Agents can scrape the site; that is not an API. Score 2 as a video-music source, 1 as agent infrastructure.

**Epidemic Sound Partner API** (https://www.epidemicsound.com/business/developers/, docs at https://developers.epidemicsite.com/docs/ and https://developers.epidemicsound.com/). About 55,000 tracks and 250,000 effects, mood/genre/BPM search, stems, beat timing, and a video-soundtracking flow. A free tier exists for prototyping and is marked not-for-production; paid plans carry the commercial licence. Epidemic owns the catalogue (sync, mechanical, and performance, on their account). This is the most serious “music API for apps and agents that make video.” It is not PD or CC, and it has no editable scores. Score 2 against our brief, higher if the brief were “any cleared music for video.”

**Incompetech.** The `llms.txt` fetched via search (page dated in snippet 15 Aug 2026) documents an agent section and a machine-readable catalogue at `pieces.json`, with CC BY 4.0 on the music and a required credit line. Direct fetch from this environment failed, so treat the JSON URL as reported by that file, and re-check before depending on it. This is the clearest precedent for “put a JSON catalogue where agents will look,” applied to attribution-required stock music rather than to scores.

**FreePD** (https://freepd.com/). Kevin MacLeod’s CC0 library for commercial use with no attribution. A Codeberg mirror (https://codeberg.org/fineless71/FreePD) documents a community audit: some “page 2” tracks were not CC0 and were later removed from the site. Search snippets disagree about October 2026 status: one result is a closure notice (“taken the service offline” after 17 years); another still describes an “Agent Section” for robots. Direct fetch was blocked. Treat FreePD as a CC0 *source* whose files should be copied from a pinned archive, not as a live API, until the homepage is re-checked.

**SoundSafari/CC0-1.0-Music** (https://github.com/SoundSafari/CC0-1.0-Music): about 7,000 tracks, about 40 GB, grouped by source site (Freesound, Pixabay, Chosic, FMA, FreePD). CC0 on the repo. No normalisation, no per-track licence record beyond the folder name, no scores. The README’s “largest CC0 corpus” claim is about audio files, not about verified metadata. Useful as a scratch dump after re-verification. Score 2.

**Chosic** (policy: https://www.chosic.com/free-music-policy/): a human mood browser over CC0 and CC-BY tracks, commercial use allowed, attribution only when the track says so. No official developer API (a third-party scraper markets one; that is not Chosic’s API). Score 1 as agent infrastructure, 2 as a pointer to sources.

**ccMixter / dig.ccMixter.** Community CC music aimed at video and podcasts. dig.ccmixter distinguishes full CC (commercial with credit) from NC and from a paid royalty-free option. A public ccHost query API is described on https://ccmixter.org/isitlegal and http://dix.ccmixter.org/about. A small downloader (https://github.com/dohliam/ccmixter-download) can filter by licence token (`by`, `pd`, `nc`, …). Ageing, audio only, attribution culture. Score 2.

**open-lofi** (https://github.com/btahir/open-lofi): 150+ lo-fi tracks, CC0, with `catalog.json`. The README says they were generated on Suno v5 and then dedicated. That is a real JSON catalogue and a real legal question: whether Suno’s terms allow a CC0 dedication. Do not ingest until that is checked. Score 2 as a pattern, not as a source to copy blindly.

**Free To Use** (https://www.producthunt.com/products/free-to-use and the 17 Sep 2026 API write-up at https://freetouse.com/blog/royalty-free-music-api-for-the-apps-you-build): a keyless HTTP API (`api.freetouse.com/v3`, OpenAPI JSON cited at `api.freetouse.com/v3/openapi.json`) of music the company says it owns. The free tier described in that post is non-commercial and requires title, artist, and a link; premium tracks are excluded. No scores. Score 2. Another “agents, here is OpenAPI” precedent.

**YouTube Audio Library, Mixkit, Bensound, Artlist, Soundstripe.** These are human or subscription stock libraries. Inferse’s 5 Oct 2026 stock-music roundup lists public APIs for several paid houses (Soundstripe, Pond5, Epidemic, Artlist) and for Incompetech. None is a PD score library. mockfreeli (Show HN, https://news.ycombinator.com/item?id=49743031) embeds YouTube Audio Library, NoCopyrightSounds, and Internet Archive audio for similarity search. Useful as a UX idea. The corpus is not a redistributable PD/CC score catalogue.

### 3.3 MCP servers and registries

Searched: Glama (MuseScore and Freesound listings), Smithery, mcp.so, PulseMCP, ChatForest’s March 2026 music-MCP survey, and GitHub. The official `modelcontextprotocol/servers` tree did not surface a music-library server in these queries. What exists is control and generation:

| server | URL | what it is | score |
| --- | --- | --- | --- |
| music.build | https://github.com/deer/music.build | 47 MCP tools to compose and export MIDI/LilyPond. Apache-2.0. No catalogue. | 1 |
| mcp-score | https://github.com/tskovlund/mcp-score and https://pypi.org/project/mcp-score-server/ | Natural language to MusicXML via music21; live MuseScore 4.4.2+ edit; render PDF/MIDI/audio. | 1 |
| music21-mcp | https://github.com/SimonsonM/music21-mcp | Key, Roman numerals, counterpoint, parse MIDI/MusicXML. | 1 |
| midi-mcp-server | https://github.com/tubone24/midi-mcp-server | JSON to MIDI, chord names, piano-roll preview. Also on Glama. | 1 |
| fcp-midi | https://github.com/os-tack/fcp-midi | Semantic MIDI session (notes, chords, crescendo) on top of mido. | 1 |
| mcp-muse | https://github.com/alextrzyna/mcp-muse | Agent playback and WAV export, GM soundfont, synth design. | 1 |
| mcp-server-midi | https://github.com/sandst1/mcp-server-midi | Virtual MIDI port into a DAW. PulseMCP: https://www.pulsemcp.com/servers/sandst1-midi-output | 1 |
| mcp-musescore and forks | https://github.com/ghchen99/mcp-musescore , https://github.com/JordanSucher/musescore-mcp , Glama “Best MuseScore MCP Servers”, https://mcp.so/servers/musescore-mcp | Drive a local MuseScore score. Not the musescore.com catalogue. | 1 |
| smithery mcp-music-studio | https://smithery.ai/server/linxule/mcp-music-studio | ABC to playback, plus Strudel live coding. | 1 |
| synth-mcp | https://pypi.org/project/synth-mcp/ | MusicXML in, WAV out, part selection. A render tool, not a library. | 1 |
| Freesound MCP servers | https://github.com/johnkimdw/freesound-mcp-server and Glama entries | Search CC audio for picture edit. See §3.2 for licence limits. | 2 |
| Ableton / FL Studio / Spotify | Surveyed by ChatForest (http://chatforest.com/reviews/music-audio-production-mcp-servers, 15 Mar 2026). Ableton (reported: `ahujasid/ableton-mcp`) is DAW control. Spotify servers on PulseMCP are playback of a commercial catalogue. | 1 |

No registry hit was a public-domain score-and-recording catalogue. The MCP ecosystem will happily *consume* our library. It does not already publish one.

### 3.4 PyPI, npm, Product Hunt, Hacker News

**PyPI.** `mcp-score-server` and `synth-mcp` are notation tools. `imslp` (https://pypi.org/project/imslp/) and `easy-imslp` wrap IMSLP metadata. Freesound’s client is https://github.com/MTG/freesound-python (install from the repo; POST/upload is unsupported). MusPy (docs at https://hermandong.com/muspy/) ships loaders for Lakh and MAESTRO, which is convenient and does not clear rights. No package found whose purpose is “search a PD/CC score-and-recording library for video.”

**npm.** `freesound-client` (https://github.com/amilajack/freesound-client) and `vibe-composer-midi-mcp` (composition / MIDI out, from the earlier GitHub pass) are clients and instruments. No catalogue package.

**Product Hunt.** Launches in this neighbourhood are generative or stock APIs: Mubert API (31 Jul 2026, stems and streaming), SOUNDRAW API, Muzaic (AI soundtrack-as-a-service, 16 Apr 2024), MIDIGEN (royalty-free MIDI *melodies*, Sep 2024), Tonefold (describe a song, get editable MIDI, listed the week of 8 Oct 2026), Free To Use (owned catalogue, attribution or a plan). None is a PD/CC score library.

**Hacker News.** CC Hound (https://news.ycombinator.com/item?id=24745874, thread pointing at a 2018 Show HN) is a curated CC music browser for video, with commenters asking for a licence filter. mockfreeli (above) is similarity search over licence-free audio. Other Show HNs are MIDI players, audio-to-MIDI, and an MCP server for a Novation Circuit (https://news.ycombinator.com/item?id=47804220). No Show HN of a joined score-and-recording agent library.

**Indexes of libraries, not libraries.** https://github.com/fiehrfly/muses is a curated markdown list of video-safe music sites (Pixabay, Mixkit, FMA, Internet Archive, Jamendo, Chosic) with account and attribution notes. https://github.com/albertmeronyo/awesome-midi-sources lists MIDI sites, including copyrighted pop archives. Both are maps. Score 1 as products, useful as bibliographies.

### 3.5 What “agent access” actually looks like today

| pattern | who | fit |
| --- | --- | --- |
| Bulk archive + metadata table | PDMX, FMA, ASAP, OpenScore git, Mutopia git | Agents can vendor a snapshot. No live query, no update stream. |
| Public REST, per-item licence | Freesound, Jamendo, Epidemic, Free To Use, Archive advanced search, Commons API | Right shape for audio. Wrong content or wrong licence for our brief. |
| `llms.txt` + JSON catalogue | Incompetech (reported) | The pattern to copy for a static site. |
| MCP tool wrapping someone else’s API | Freesound MCP servers | Thin. Does not create a catalogue. |
| MCP tool that writes notes | music.build, mcp-score, midi servers | Orthogonal. Our library would feed these, not compete with them. |
| MediaWiki API | IMSLP, CPDL | Metadata and links. Files and licences still need a human pass. |

## 4. Reusable bulk sources, ranked

Ranked for *our* library: commercial or social video, per-file licence, editable score preferred, recording welcome, multi-genre later. “Reuse” means ingest after a local licence check, not blind copy.

1. **PDMX `no_license_conflict`** (222,856). Best bulk MusicXML + MIDI + tags. Re-check the Zenodo licence column anyway. Filter on user rating and instrumentation before anything is called “good.” Do not ship MuseScore-generated MIDI as if it were a performance. Source: https://zenodo.org/records/15571083.

2. **OpenScore Lieder and String Quartets, then the orchestral set when the index is actually downloadable.** Best engraving quality and the cleanest CC0 statement. YAML is already catalogue-shaped. Narrow genre. https://github.com/OpenScore/Lieder , https://github.com/OpenScore/StringQuartets.

3. **Mutopia `ftp/` tree on GitHub.** LilyPond is the editable source; MIDI and PDF are derivatives we can regenerate. Per-piece licence headers are the model for our `legal_notes`. Small, classical. https://github.com/MutopiaProject/MutopiaProject.

4. **music21 corpus, file by file.** Already parsed, mostly PD repertoire (Bach chorales and similar). Read each file’s header. Do not depend on the whole corpus as one licence. https://github.com/cuthbertLab/music21.

5. **KernScores public-domain subset only.** Symbolic, convertible, large. Drop anything behind the copyright login. https://kern.ccarh.org/.

6. **U.S. Marine Band and other U.S. federal performances on Commons and Archive.** A work made by a federal employee in their job is not copyrighted in the United States. Commons categories: https://commons.wikimedia.org/wiki/Category:Audio_files_of_music_by_the_United_States_Marine_Band (classical subcategory, 106 files at last listing) and the parent category. Archive examples with an explicit PD mark: https://archive.org/details/MorningColorsMusic , https://archive.org/details/StarsAndStripesForever. The recording can be PD while the composition is not (or not worldwide). Pair a PD composition from items 1–5 with one of these recordings. Verify the Commons template on each file. Some Elgar, Gershwin, and later works in that category are performance-PD only.

7. **Musopen recordings that were actually released, via Archive, not via the freemium site.** https://archive.org/details/MusopenCollectionAsFlac is marked Public Domain Mark 1.0 (Kickstarter-era set, FLAC). https://archive.org/details/MusopenKickstarterRecordingsLossless is marked CC0. Wikipedia (https://en.wikipedia.org/wiki/Musopen) describes the live site as freemium (daily download cap, paid lossless). No public API turned up. Prefer the Archive items whose licence field you have read. Sheet-music PDFs on Musopen are a separate, scan-heavy collection.

8. **IMSLP as a discovery index, not a dump.** https://imslp.org/wiki/IMSLP:API lists people and works. Download only files whose own licence is PD or CC0/CC-BY, and prefer an existing MusicXML/MIDI edition over a scan. Recordings on IMSLP are often copyrighted. Respect the site’s rate and disclaimer parameters (`disclaimer=accepted`).

9. **The Session, only for folk.** https://thesession.org/api (JSON, XML, RSS; up to 50 per page) and weekly dumps https://github.com/adactio/TheSession-data. Tunetable’s README describes the dump as Open Database License (ODbL); confirm on `LICENSE.md` before a commercial product embeds the database rather than individual tunes. ABC is editable and traditional dance music is often PD, but settings and chords are contributor text. Wrong genre for a cinematic cue library; right genre for a folk slice.

10. **CC0 / CC-BY audio for a `modern_cc` shelf, one file at a time.** FreePD (pin a mirror; site status uncertain), FMA rows whose licence is CC0 or CC-BY, Freesound CC0/CC-BY *if* the API commercial terms are solved or the files are downloaded by a logged-in user and re-hosted, Pixabay tracks under the Content Licence (not CC, and not in the public API). Store the source URL and the exact licence string. These do not bring scores.

11. **CPDL for choral PD editions that already have MXL.** MediaWiki search, then the edition’s licence. No bulk redistribution (admin reply on the 2021 archive-request thread). https://www.cpdl.org/wiki/index.php/Main_Page.

**Do not bulk-import:** Lakh and every Lakh derivative, GiantMIDI-Piano, MAESTRO, ASAP audio, Aria-MIDI, Discover MIDI, MetaMIDI, BitMidi, nightingale-ai/midi-data, Wikifonia, text2score as a whole, MuseScore.com beyond the PDMX conflict-free filter, anything NC or ND, and any recording whose page you have not opened. A PD composition never clears a recording.

## 5. Recommendation: MCP, JSON API, or both

**Both, with the JSON catalogue as the source of truth and MCP as a thin client.**

Ship a stable, cacheable document first: `catalog.json` (id, title, composer, genre, mood, licence status, whether a score and a recording exist, preview URL, score URL, audio URL) plus one JSON record per piece. CSV can mirror it. Put the same files on the static site. That is enough for any agent that can HTTP-GET, including ones with no MCP client, and it matches the only agent-facing pattern that already works in public (Incompetech’s `llms.txt` + `pieces.json`, Free To Use’s OpenAPI, OpenScore’s YAML). A short `llms.txt` or `AGENTS.md` should point at the catalogue and state the licence rules in plain text.

Add an MCP server only as a wrapper over that catalogue: `search`, `get`, `licence_check`, and `render` (MIDI through FluidSynth). Do not invent a second database inside the server. MCP registries are crowded with note-generators; a library server is how those tools find lawful material. MCP alone would hide the catalogue from agents that only read URLs, and a JSON API alone would skip the clients (Claude Desktop, Cursor, and similar) that discover tools rather than files.

Do not block the catalogue on MCP. The data is the product. The server is a convenience once the records and the licences are boringly correct.

A live HTTP API (search, filter by mood, genre, licence, “has score”, “has recording”) is worth adding when the catalogue is large enough that pulling the whole JSON is rude. Until then a static file plus MCP is the smaller honest surface. If a third-party audio API is wrapped later (Freesound, Jamendo, Commons), keep it behind the same licence vocabulary and never mark a remote CC-BY-NC hit as clean.

## 6. Sources consulted

### Search queries

- music MCP server MIDI MusicXML creative commons agent
- PDMX dataset public domain MusicXML MIDI Hugging Face
- site:github.com music-mcp OR "music mcp" MIDI library API
- Hugging Face dataset public domain MIDI MusicXML creative commons music library
- Smithery MCP music MIDI MuseScore Freesound server
- site:glama.ai MCP music MIDI MuseScore Freesound
- PulseMCP music MIDI server registry
- mcp.so music MIDI Freesound MuseScore server
- OpenScore Lieder corpus MusicXML license download dataset
- Free Music Archive API status 2025 2026 dataset FMA
- Jamendo API music license commercial use developer
- Freesound API v2 license filter CC0 music download documentation
- Pixabay music API documentation license commercial video
- Epidemic Sound API developer partner music library
- Musopen API public domain recordings download dataset
- Mutopia Project LilyPond public domain bulk download
- "public domain" OR "creative commons" MusicXML OR MIDI API OR MCP "video" library dataset agent
- Lakh MIDI dataset license copyright commercial use Colin Raffel
- MAESTRO dataset license GiantMIDI-Piano license music21 corpus license
- IMSLP API Petrucci Music Library developer access
- thesession.org API tunes ABC creative commons documentation
- Internet Archive advanced search API audio mediatype music license
- Wikimedia Commons API audio files category music license query
- ccMixter API dig.ccmixter creative commons music
- Show HN public domain MIDI OR "creative commons music" OR freesound MCP site:news.ycombinator.com
- OpenScore String Quartets GitHub CC0
- KernScores Humdrum dataset license music21 corpus contents
- FreePD.com public domain music Kevin MacLeod license API
- United States Marine Band public domain recordings Internet Archive Wikimedia
- site:github.com/modelcontextprotocol/servers music OR midi OR audio OR spotify OR freesound
- Chosic public domain music API OR dataset CC0
- Choral Public Domain Library CPDL API OR download
- Product Hunt royalty free music API OR "public domain" MIDI library launch
- ASAP dataset piano license CC BY-NC-SA MusicXML

### Key primary URLs

Scores and corpora: https://github.com/pnlong/PDMX/ , https://zenodo.org/records/15571083 , https://arxiv.org/abs/2409.10831 , https://arxiv.org/html/2409.10831 , https://fourscoreandmore.org/openscore/ , https://github.com/OpenScore/Lieder , https://github.com/OpenScore/StringQuartets , https://zenodo.org/records/15450144 , https://www.mutopiaproject.org/ , https://github.com/MutopiaProject/MutopiaProject , https://github.com/cuthbertLab/music21 , https://kern.ccarh.org/ , https://github.com/humdrum-tools/humdrum-data , https://github.com/fosfrancesco/asap-dataset , https://magenta.withgoogle.com/datasets/maestro , https://github.com/bytedance/GiantMIDI-Piano , https://colinraffel.com/projects/lmd/ , https://github.com/ethman/Slakh , https://imslp.org/wiki/IMSLP:API , https://github.com/jlumbroso/imslp , https://www.cpdl.org/wiki/index.php/Main_Page , https://thesession.org/api , https://github.com/adactio/TheSession-data , https://github.com/musetrainer/library

Audio and APIs: https://github.com/mdeff/fma , https://freemusicarchive.org/app-developers , https://huggingface.co/datasets/benjamin-paine/free-music-archive-full , https://freesound.org/docs/api/ , https://freesound.org/docs/api/overview.html , https://freesound.org/docs/api/terms_of_use.html , https://freesound.org/help/developers/ , https://developer.jamendo.com/ , https://www.jamendo.com/legal/licenses , https://licensing.jamendo.com/en , https://pixabay.com/api/docs/ , https://pixabay.com/service/license-summary/ , https://pixabay.com/service/faq/ , https://www.epidemicsound.com/business/developers/ , https://developers.epidemicsite.com/docs/ , https://developers.epidemicsound.com/ , https://incompetech.com/llms.txt , https://freepd.com/ , https://codeberg.org/fineless71/FreePD , https://github.com/SoundSafari/CC0-1.0-Music , https://www.chosic.com/free-music-policy/ , https://dig.ccmixter.org/credits , https://ccmixter.org/isitlegal , https://github.com/dohliam/ccmixter-download , https://github.com/btahir/open-lofi , https://freetouse.com/blog/royalty-free-music-api-for-the-apps-you-build , https://archive.org/advancedsearch.php , https://archive.org/details/MusopenCollectionAsFlac , https://archive.org/details/MusopenKickstarterRecordingsLossless , https://archive.org/details/MorningColorsMusic , https://commons.wikimedia.org/wiki/Commons:Audio , https://commons.wikimedia.org/wiki/Category:Audio_files_of_music_by_the_United_States_Marine_Band , https://en.wikipedia.org/wiki/Musopen

Agent surfaces: https://github.com/deer/music.build , https://github.com/tskovlund/mcp-score , https://pypi.org/project/mcp-score-server/ , https://pypi.org/project/synth-mcp/ , https://github.com/SimonsonM/music21-mcp , https://github.com/tubone24/midi-mcp-server , https://github.com/alextrzyna/mcp-muse , https://github.com/ghchen99/mcp-musescore , https://github.com/os-tack/fcp-midi , https://github.com/sandst1/mcp-server-midi , https://github.com/johnkimdw/freesound-mcp-server , https://github.com/MTG/freesound-python , https://github.com/amilajack/freesound-client , https://smithery.ai/server/linxule/mcp-music-studio , https://glama.ai/mcp/servers/integrations/musescore , https://glama.ai/mcp/servers/timjrobinson/FreesoundMCPServer , https://mcp.so/servers/musescore-mcp , https://www.pulsemcp.com/servers/sandst1-midi-output , http://chatforest.com/reviews/music-audio-production-mcp-servers , https://github.com/fiehrfly/muses , https://news.ycombinator.com/item?id=24745874 , https://news.ycombinator.com/item?id=49743031 , https://huggingface.co/datasets/projectlosangeles/Discover-MIDI-Dataset , https://huggingface.co/datasets/loubb/aria-midi , https://huggingface.co/datasets/emotionwave-company/text2score , https://huggingface.co/datasets/guangyangmusic/OpenScore-Lieder

### Uncertainty

- No 4 or 5 was found. A private or unlisted product could exist; this pass covered the public registries and the usual corpora, not every paid stock-music vendor’s API.
- FreePD’s live homepage and Incompetech’s `pieces.json` were not fetched directly.
- PDMX’s conflict filter is necessary and not a substitute for opening a file before publication.
- U.S. federal recordings are public domain in the United States. Composition copyright, and copyright in other countries, is a separate test.
- open-lofi’s CC0 dedication may conflict with Suno’s terms. Not verified.
- MCP servers appear often. The registry survey is a snapshot on 2026-10-09, not a guarantee that a catalogue server will not be published next week.

## Cross-check errata (Codex)

Cross-checked 2026-10-09. Full evidence and revised recommendations: [CROSSCHECK_codex.md](CROSSCHECK_codex.md).

- **Narrow the novelty claim.** [Keynata Commons](https://carf-coder.github.io/keynata-commons/release/index.json) is a working CC0-declared MIDI/MP3/JSON library: 203 tracks, seven categories, per-track metadata. Codex scores it **4**, with generated-music, quality and provenance limitations. “Nothing above 3” is incorrect. Recognisable repertoire with independently documented score/recording rights remains a plausible differentiation.
- **OpenScore Orchestra is downloadable now** in [Hauptstimme](https://github.com/MarkGotham/Hauptstimme): CC0 scores, CC BY-SA annotations, MIT code. Also add MusicNet, Open Goldberg/OpenWTC and OpenGameArt MIDI/audio packs as substantial partial matches.
- **PDMX counts are confirmed**, but [Zenodo v9](https://zenodo.org/records/15571083) licenses the dataset CC BY 4.0, separately from source-score CC0/PDM labels. The conflict filter does not establish clearance. Prefer curated OpenScore/Mutopia editions before bulk expansion.
- **Incompetech endpoints are confirmed live.** [pieces.json](https://incompetech.com/music/royalty-free/pieces.json) has 1,443 rows and 41 sheet-music entries (PDF or PDF ZIP); it exposes no editable-score links or `uuid`/`wav` keys. The author's bulk-pack announcement also mentions MIDI, so “no scores” is too broad. [FreePD](https://freepd.com/) explicitly reports permanent closure.
- **Counts:** ASAP's current repository says **1,068 performances**; its NC licence is correctly reported. Aria-MIDI has **1,186,253 files / approximately 100,629 hours**, not 1.18M hours. MuseTrainer's “clean” characterisation is unsupported by per-file rights evidence.
- **Catalogue MCP already exists:** [Epidemic's official MCP](https://developers.epidemicsound.com/docs/mcp/) searches and downloads its proprietary catalogue. It still lacks PD/CC terms and editable scores. The listed community repositories resolved; some secondary HTTP links remained unconfirmed.
- **Reuse qualifications:** Jamendo requires per-track CC checks, not a universal paid-licence assumption. Freesound commercial API restrictions are confirmed; logged-in downloads do not establish permission for a commercial ingestion workaround. Pixabay prohibits standalone redistribution, so its current Content Licence tracks do not belong in a redistributable PD/CC shelf.
