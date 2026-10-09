#!/usr/bin/env python3
"""Cut a Standard MIDI File to its first N seconds.

FluidSynth renders the whole file before the preview is trimmed. A quartet
MIDI can be half an hour. Keeping the opening 20 seconds makes the 15 second
preview cheap and still starts at the beginning of the piece.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def _read_varlen(data: bytes, index: int) -> tuple[int, int]:
    value = 0
    while True:
        if index >= len(data):
            raise ValueError("truncated variable-length quantity")
        byte = data[index]
        index += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, index


def _write_varlen(value: int) -> bytes:
    buffer = [value & 0x7F]
    value >>= 7
    while value:
        buffer.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(buffer))


def _parse_track(body: bytes) -> list[tuple[int, int, bytes]]:
    """Return (tick, status, raw-including-status) events. Meta status is 0xFF."""
    events = []
    index = 0
    tick = 0
    running = None
    while index < len(body):
        delta, index = _read_varlen(body, index)
        tick += delta
        if index >= len(body):
            break
        byte = body[index]
        if byte & 0x80:
            status = byte
            index += 1
            if status < 0xF0:
                running = status
            else:
                running = None
        else:
            status = running
            if status is None:
                raise ValueError("running status with no previous status")
        if status == 0xFF:
            kind = body[index]
            index += 1
            length, index = _read_varlen(body, index)
            payload = body[index:index + length]
            index += length
            raw = bytes([0xFF, kind]) + _write_varlen(length) + payload
            events.append((tick, 0xFF, raw))
            continue
        if status in (0xF0, 0xF7):
            length, index = _read_varlen(body, index)
            payload = body[index:index + length]
            index += length
            raw = bytes([status]) + _write_varlen(length) + payload
            events.append((tick, status, raw))
            continue
        needed = 1 if status & 0xF0 in (0xC0, 0xD0) else 2
        payload = body[index:index + needed]
        index += needed
        if len(payload) < needed:
            break
        events.append((tick, status, bytes([status]) + payload))
    return events


def _tick_to_us(tick: int, changes: list[tuple[int, int]], ticks_per_beat: int) -> int:
    microseconds = 0
    previous = 0
    tempo = 500000
    for at, new_tempo in changes:
        if at >= tick:
            break
        microseconds += (at - previous) * tempo // ticks_per_beat
        previous = at
        tempo = new_tempo
    microseconds += (tick - previous) * tempo // ticks_per_beat
    return microseconds


def _us_to_tick(limit: int, changes: list[tuple[int, int]], ticks_per_beat: int) -> int:
    previous = 0
    tempo = 500000
    elapsed = 0
    for at, new_tempo in changes:
        span = (at - previous) * tempo // ticks_per_beat
        if elapsed + span >= limit:
            remain = limit - elapsed
            return previous + (remain * ticks_per_beat // max(tempo, 1))
        elapsed += span
        previous = at
        tempo = new_tempo
    remain = limit - elapsed
    return previous + (remain * ticks_per_beat // max(tempo, 1))


def _encode_track(events: list[tuple[int, bytes]]) -> bytes:
    if not events or not events[-1][1].startswith(b"\xff\x2f"):
        events = list(events) + [(events[-1][0] if events else 0, b"\xff\x2f\x00")]
    blob = bytearray()
    last = 0
    for tick, raw in events:
        blob += _write_varlen(max(0, tick - last))
        blob += raw
        last = tick
    return bytes(blob)


def clip_midi(src: Path, dest: Path, seconds: float = 20.0) -> int:
    """Write a MIDI that stops at `seconds`. Return the cut tick."""
    data = Path(src).read_bytes()
    if data[:4] != b"MThd" or len(data) < 14:
        raise ValueError(f"not a standard MIDI file: {src}")
    header_len = int.from_bytes(data[4:8], "big")
    track_count = int.from_bytes(data[10:12], "big")
    division = int.from_bytes(data[12:14], "big", signed=True)
    pos = 8 + header_len
    tracks = []
    for _ in range(track_count):
        if data[pos:pos + 4] != b"MTrk":
            raise ValueError("missing MTrk")
        length = int.from_bytes(data[pos + 4:pos + 8], "big")
        tracks.append(_parse_track(data[pos + 8:pos + 8 + length]))
        pos += 8 + length
    if division <= 0:
        dest.write_bytes(data)
        return 0
    changes = [(0, 500000)]
    for events in tracks:
        for tick, status, raw in events:
            if status == 0xFF and len(raw) >= 6 and raw[1] == 0x51:
                # FF 51 03 tttttt
                length = raw[2]
                if length == 3:
                    changes.append((tick, int.from_bytes(raw[3:6], "big")))
    changes.sort()
    # collapse duplicate ticks, last tempo wins
    folded = []
    for tick, tempo in changes:
        if folded and folded[-1][0] == tick:
            folded[-1] = (tick, tempo)
        else:
            folded.append((tick, tempo))
    cut_us = int(seconds * 1_000_000)
    cut_tick = _us_to_tick(cut_us, folded, division)
    out_tracks = []
    for events in tracks:
        kept = []
        sounding = {}
        for tick, status, raw in events:
            if tick > cut_tick:
                break
            if status == 0xFF and len(raw) > 1 and raw[1] == 0x2F:
                continue
            kept.append((tick, raw))
            if status and status < 0xF0 and (status & 0xF0) == 0x90 and len(raw) >= 3:
                channel = status & 0x0F
                note = raw[1]
                velocity = raw[2]
                if velocity:
                    sounding[(channel, note)] = True
                else:
                    sounding.pop((channel, note), None)
            elif status and status < 0xF0 and (status & 0xF0) == 0x80 and len(raw) >= 3:
                sounding.pop((status & 0x0F, raw[1]), None)
        for channel, note in sounding:
            kept.append((cut_tick, bytes([0x80 | channel, note, 0])))
        kept.append((cut_tick, b"\xff\x2f\x00"))
        kept.sort(key=lambda item: item[0])
        out_tracks.append(_encode_track(kept))
    blob = bytearray()
    blob += b"MThd" + (6).to_bytes(4, "big")
    blob += int.from_bytes(data[8:10], "big").to_bytes(2, "big")
    blob += len(out_tracks).to_bytes(2, "big")
    blob += data[12:14]
    for body in out_tracks:
        blob += b"MTrk" + len(body).to_bytes(4, "big") + body
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(blob)
    return cut_tick


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=Path)
    parser.add_argument("dest", type=Path)
    parser.add_argument("--seconds", type=float, default=20.0)
    args = parser.parse_args()
    tick = clip_midi(args.src, args.dest, args.seconds)
    print(f"clipped {args.src} -> {args.dest} cut_tick={tick}")


if __name__ == "__main__":
    main()
