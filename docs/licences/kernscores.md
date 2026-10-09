# KernScores / craigsapp Humdrum repos: licence check (2026-10-09)

Verdict: **EXCLUDE everything. No rows, no harvester.**

| collection | evidence | verdict |
|---|---|---|
| kern.humdrum.org site | `curl -I https://kern.humdrum.org/` returned `HTTP/1.1 503 Service Unavailable` on 2026-10-09; no terms page could be fetched. The terms we know of limit many files to non-commercial / research use. | exclude (no verifiable commercial licence) |
| craigsapp/bach-370-chorales | https://github.com/craigsapp/bach-370-chorales/blob/main/LICENSE.txt: "Licensed with Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)" | exclude (NC, SA) |
| craigsapp/mozart-piano-sonatas | LICENSE.txt: "Copyright (C) 2004-2018 Craig Stuart Sapp ... (CC BY-NC-SA 4.0)" | exclude (NC, SA) |
| craigsapp/joplin | LICENSE.txt: "Copyright (C) 2004-2021 Craig Stuart Sapp ... (CC BY-NC-SA 4.0)" | exclude (NC, SA) |
| craigsapp/scarlatti-keyboard-sonatas | LICENSE.txt: "Copyright (C) 2021 Craig Stuart Sapp ... (CC BY-NC-SA 4.0)" | exclude (NC, SA) |
| craigsapp/beethoven-piano-sonatas, chopin-preludes, chopin-mazurkas, beethoven-string-quartets, hummel-preludes, haydn-string-quartets, art-of-the-fugue, vivaldi-op6, haydn-piano-sonatas, densmore-teton-sioux | GitHub API `/repos/craigsapp/<repo>/license` returned "Not Found" (no LICENSE file), or LICENSE.txt returned 404. READMEs have no licence text and point to kern.ccarh.org. Sampled kern headers carry `!!!YEC: Copyright 2008 by Craig Stuart Sapp` with no open licence. | exclude (all rights reserved by default) |
| humdrum-tools/humdrum-data | GitHub API: repo "Not Found" | exclude |
| Kern files mirrored in the music21 corpus (e.g. palestrina/*.krn) | `!!!YEC: Copyright 2000, John Miller` / `!!!YEM: Rights to all derivative electronic formats reserved.` | exclude |

Other craigsapp repos with a GitHub licence (humlib, midifile, hum2ly, musicxml2hum, ratioscore: BSD-2-Clause; midi-player: LGPL-3.0; Leland: OFL) are software or fonts, not score data.

Re-check if Sapp relicenses a repo under CC BY / CC0, or if kern.humdrum.org comes back with per-file open terms.
