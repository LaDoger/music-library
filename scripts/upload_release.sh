#!/bin/bash
set -euo pipefail
cd /workspace/music/library/files/audio
mapfile -t files < <(ls -1)
echo "Uploading ${#files[@]} assets to audio-v1..."
batch=()
flush() {
  (( ${#batch[@]} )) || return 0
  echo "batch ${#batch[@]}"
  gh release upload audio-v1 -R LaDoger/music-library --clobber "${batch[@]}"
  batch=()
}
for f in "${files[@]}"; do
  batch+=("$f")
  if (( ${#batch[@]} >= 5 )); then flush; fi
done
flush
echo DONE count=$(gh release view audio-v1 -R LaDoger/music-library --json assets -q '.assets|length')
