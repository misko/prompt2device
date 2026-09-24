#!/usr/bin/env python3
"""Regression guard for the rejected three-cell shared-zone research probe."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
VARIANT = PROJECT / '01_docs/research/2026-09-24-p1-audio-xmos-clock-shared-zone-variant-terra.yaml'
AUDIT = PROJECT / '03_src/diagnostics/p1_shared_zone_variant_audit.py'
PLAN = PROJECT / '03_src/modular_plan.json'

class SharedZoneVariantTest(unittest.TestCase):
    def test_union_is_rejected_without_changing_fixed_authority(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'audit.json'
            subprocess.run(['/usr/bin/python3', str(AUDIT), str(VARIANT), str(PLAN), str(out)],
                           check=True, capture_output=True, text=True)
            report = json.loads(out.read_text())
        self.assertEqual(report['status'], 'REJECTED')
        self.assertFalse(report['p1_accepted'])
        self.assertFalse(report['routing_realized'])
        self.assertTrue(report['fixed_refs']['exact_current_authority'])
        self.assertEqual(report['fixed_refs']['count'], 27)
        self.assertEqual(report['fixed_refs']['zone_intersections'], [])
        self.assertEqual(report['zone']['member_owners'], {
            'audio_clock_tdm': 39, 'clock_flash_debug': 8, 'xmos_core': 29})
        self.assertGreater(report['zone']['full_footprint_intersections'], 76)
        self.assertTrue(report['zone']['foreign_footprints'])
        self.assertTrue(report['zone']['boundary_intersections'])

if __name__ == '__main__':
    unittest.main()
