#!/usr/bin/env python3
"""Specific video-use notes for bulk rows, replacing the seven generic templates.

Every bulk row (library_bulk.csv) carries one of seven generic `video_use_ideas` lines.
This script asks `codex exec` (low reasoning effort) for one short note per row, written from the
row's own metadata (title, composer, catalogue, movement, mood, tempo/energy,
instrumentation, genre, era), in batches of ~100 rows. Each batch is checkpointed in
parts/video_notes_progress.json (git-ignored). The merged result goes to
scripts/video_notes.json, which scripts/video_ideas.py loads as an override layer below its
curated IDEAS. library_bulk.csv itself is not edited.

  python3 scripts/bulk/video_notes.py --status                 count done / pending
  python3 scripts/bulk/video_notes.py --minutes 40             run batches until the budget is spent
  python3 scripts/bulk/video_notes.py --dry-run                print the first prompt, no model call

Resume: re-run the same command; finished ids are skipped. Then run
python3 scripts/sync_site_data.py and python3 scripts/video_ideas.py --check.
"""
import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import video_ideas  # noqa: E402

BULK_CSV = os.path.join(ROOT, "library_bulk.csv")
PROGRESS = os.path.join(ROOT, "parts", "video_notes_progress.json")
OUT = os.path.join(ROOT, "scripts", "video_notes.json")
FIELDS = ["id", "title", "composer", "catalog", "movement", "mood_tags", "tempo_energy",
          "instrumentation", "genre", "era"]
MAX_LEN = 160
MAX_ATTEMPTS = 3

PROMPT = """You write short video-edit notes for a general-purpose music library. For each piece below,
write ONE sentence (6 to 20 words) saying what it suits in a video: its mood, its tempo or energy,
its instrumentation, and a typical edit it fits (opener, voice-over bed, montage, reveal, closing
card, transition, quiet scene).

Rules:
- Lean on the title, form and era: a madrigal, motet, mass movement, lied, jig, reel, march,
  waltz, étude, nocturne or carol each suggests a specific scene (period drama, sacred interior,
  pub or festival montage, travel, wintry/holiday shot, study or focus bed, romantic close-up).
- Never mention track counts (\"1 tracks\", \"six tracks\") or the words \"classical\" and \"lyrical\";
  the mood tags are often generic, so do not echo them.
- If the instrumentation is unknown, simply leave it out; never write \"scoring unspecified\".
- Use only the metadata given. Do not invent a key, a BPM, dates or facts about the composer.
- Stay generic: no brand, company, product or platform names, and no finance or commerce wording.
- No quotation marks around the sentence, no numbering, no commentary outside the JSON.
- Vary the wording; do not start every sentence with the same verb.

Return ONLY a JSON object that maps each id to its sentence, for example:
{"bach_example_id": "Calm organ bed for a title card, with slow, stately pacing."}

Pieces (JSON):
"""


def bulk_rows():
    with open(BULK_CSV, encoding="utf-8", newline="") as f:
        return [{k: (v or "").strip() for k, v in r.items()} for r in csv.DictReader(f)]


def pending_rows(rows, notes):
    """Bulk rows with no generated note yet and no curated IDEAS override."""
    return [r for r in rows if r["id"] not in notes and r["id"] not in video_ideas.IDEAS]


def valid(note):
    if not isinstance(note, str):
        return False
    n = note.strip()
    return 6 <= len(n.split()) and len(n) <= MAX_LEN and "\n" not in n and not video_ideas.needs_rewrite(n)


def parse_reply(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in reply")
    data = json.loads(m.group(0))
    if not isinstance(data, dict):
        raise ValueError("reply is not a JSON object")
    return data


def ask_model(payload, timeout):
    prompt = PROMPT + json.dumps(payload, ensure_ascii=False, indent=0)
    # Codex at low reasoning effort (cheap tier); prompt on stdin, final message to a temp file.
    import tempfile
    with tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False) as tf:
        outfile = tf.name
    cmd = ["codex", "exec", "--skip-git-repo-check", "--ephemeral", "-s", "read-only",
           "-c", f"model_reasoning_effort={os.environ.get('MUSICBOT_NOTES_EFFORT', 'low')}",
           "-o", outfile, "-"]
    if os.environ.get("MUSICBOT_NOTES_MODEL"):
        cmd[2:2] = ["-m", os.environ["MUSICBOT_NOTES_MODEL"]]
    p = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd="/tmp")
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout or f"exit {p.returncode}").strip()[-300:])
    with open(outfile, encoding="utf-8") as f:
        text = f.read()
    os.unlink(outfile)
    return parse_reply(text)


def load_progress(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"notes": {}, "batches": 0}


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--minutes", type=float, default=40, help="time budget for new batches")
    ap.add_argument("--batch", type=int, default=100, help="rows per model call")
    ap.add_argument("--limit-batches", type=int, default=None, help="stop after N batches")
    ap.add_argument("--progress", default=PROGRESS, help="checkpoint file")
    ap.add_argument("--status", action="store_true", help="only report counts")
    ap.add_argument("--dry-run", action="store_true", help="print the first prompt and exit")
    ap.add_argument("--no-write", action="store_true", help="do not rewrite scripts/video_notes.json")
    args = ap.parse_args()

    progress = load_progress(args.progress)
    notes = progress["notes"]
    rows = bulk_rows()
    pending = pending_rows(rows, notes)
    print(f"bulk rows {len(rows)}; generated {len(notes)}; pending {len(pending)}")
    if args.status:
        return 0
    if args.dry_run:
        first = [{k: r.get(k, "") for k in FIELDS} for r in pending[:args.batch]]
        print(PROMPT + json.dumps(first, ensure_ascii=False, indent=0))
        return 0

    deadline = time.monotonic() + args.minutes * 60
    attempts = {}
    gave_up = []
    batches = 0
    while pending and (args.limit_batches is None or batches < args.limit_batches):
        left = deadline - time.monotonic()
        if left <= 0:
            print("time budget spent")
            break
        chunk, pending = pending[:args.batch], pending[args.batch:]
        payload = [{k: r.get(k, "") for k in FIELDS} for r in chunk]
        try:
            reply = ask_model(payload, timeout=max(60, min(600, left)))
        except (RuntimeError, ValueError, subprocess.TimeoutExpired) as e:
            print(f"batch failed: {e}")
            reply = {}
        retry = []
        for r in chunk:
            note = reply.get(r["id"])
            if isinstance(note, str):
                note = re.sub(r",? (?:with|and) (?:scoring|instrumentation) (?:unspecified|unknown)", "", note).strip()
            if valid(note):
                notes[r["id"]] = note.strip()
            else:
                retry.append(r)
        batches += 1
        progress["batches"] += 1
        save_json(args.progress, progress)
        print(f"batch {progress['batches']}: {len(chunk) - len(retry)}/{len(chunk)} ok; "
              f"generated {len(notes)}; pending {len(pending) + len(retry)}")
        for r in retry:
            attempts[r["id"]] = attempts.get(r["id"], 0) + 1
            if attempts[r["id"]] < MAX_ATTEMPTS:
                pending.append(r)
            else:
                gave_up.append(r["id"])

    if not args.no_write:
        save_json(OUT, dict(sorted(notes.items())))
    print(f"done {len(notes)}; still pending {len(pending)}; gave up {len(gave_up)}"
          + (f" ({', '.join(gave_up[:10])})" if gave_up else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
