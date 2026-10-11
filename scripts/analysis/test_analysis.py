#!/usr/bin/env python3
"""Tests for failure modes that can make chord checks falsely reassuring."""
import unittest,tempfile
from pathlib import Path
import mido
from verify_chords import verify
from common import bars_for,spelling

class VerificationTests(unittest.TestCase):
    def check_notes(self,pitches,symbol='C',extra_span=False):
        with tempfile.TemporaryDirectory(prefix='music-analysis-test-') as d:
            path=Path(d)/'test.mid';m=mido.MidiFile(ticks_per_beat=480);tr=mido.MidiTrack();m.tracks.append(tr)
            for p in pitches:tr.append(mido.Message('note_on',note=p,velocity=64,time=0))
            for i,p in enumerate(pitches):tr.append(mido.Message('note_off',note=p,time=480 if i==0 else 0))
            m.save(path)
            b={'meta':{'source_file':str(path),'quarter_range':[0,2]},'bars':[{'bar':1,'start_quarter':0,'duration_quarters':1,'chords':[{'beat':1,'symbol':symbol}]}]}
            if extra_span:b['bars'].append({'bar':2,'start_quarter':1,'duration_quarters':1,'chords':[{'beat':1,'symbol':'?'}]})
            return verify(b)
    def test_complete_chord_passes(self):
        self.assertEqual(self.check_notes([60,64,67])['chord_note_match_pct'],100)
    def test_missing_third_fails_despite_high_coverage(self):
        v=self.check_notes([60,67]);self.assertEqual(v['chord_note_match_pct'],0);self.assertIn(4,v['spans'][0]['missing_pcs'])
    def test_non_chord_mass_is_not_removed(self):
        v=self.check_notes([48,60,64,67,62,74,65,77]);self.assertEqual(v['chord_note_match_pct'],0);self.assertEqual(v['spans'][0]['coverage'],.5)
    def test_unknown_is_not_a_match(self):
        v=self.check_notes([60,64,67],extra_span=True);self.assertEqual(v['matched_spans'],1);self.assertEqual(v['unknown_spans'],1);self.assertEqual(v['labelled_span_pct'],50)
    def test_double_sharp_leading_tone(self):
        self.assertEqual(spelling(67,'g#').name,'F##')
    def test_checked_meter_layout_wins(self):
        layout=[{'bar':0,'start_quarter':0,'duration_quarters':.25},{'bar':1,'start_quarter':.25,'duration_quarters':4,'time_signature':'4/4'}]
        self.assertEqual(bars_for({'bar_layout':layout}),layout)
if __name__=='__main__':unittest.main()
