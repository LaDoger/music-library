# MIDI player bundle

`midi-player.bundle.js` is the unchanged jsDelivr combination listed in its header:

| Package | Version | Licence | Included notice |
|---|---|---|---|
| Tone.js | 14.7.58 | MIT | [tone.txt](licenses/tone.txt) |
| @magenta/music | 1.23.1 | Apache-2.0 | [magenta-music.txt](licenses/magenta-music.txt) |
| focus-visible | 5.2.1 | W3C Software and Document (2015) | [focus-visible.txt](licenses/focus-visible.txt), [full text](licenses/w3c-software-document-2015.txt) |
| html-midi-player | 1.5.0 | BSD-2-Clause | [html-midi-player.txt](licenses/html-midi-player.txt) |

Tone, focus-visible and html-midi-player notices come from the corresponding npm package tarballs. Magenta's npm package declares Apache-2.0 but omits the licence file; its repository's [LICENSE](https://github.com/magenta/magenta-js/blob/master/LICENSE) supplies that text. Existing embedded notices in the combined bundle are retained.

The app loads this bundle only when live MIDI is requested. The SGM+ samples are fetched at runtime from `https://storage.googleapis.com/magentadata/js/soundfonts/sgm_plus`; no soundfont is redistributed here. Music and score licences are recorded separately in the item data.
