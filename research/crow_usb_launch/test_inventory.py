#!/usr/bin/env python3
"""Focused, board-pinned regression check for geometry.json."""
import json
import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
BOARD = pathlib.Path('/tmp/crow-usb-fcu-north-sol-20260924/04_kicad/crow_carrier.kicad_pcb')


class InventoryTest(unittest.TestCase):
    def test_pinned_board_reproduces_committed_geometry(self):
        if not BOARD.is_file():
            self.skipTest(f'Pinned scratch board unavailable: {BOARD}')
        result = subprocess.run([sys.executable, str(HERE / 'inventory.py'), str(BOARD)],
                                check=True, capture_output=True, text=True)
        actual = json.loads(result.stdout)
        expected = json.loads((HERE / 'geometry.json').read_text())
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual['neck_track_uuids']), 6)
        self.assertEqual({(z['net'], z['layer']) for z in actual['zones_all']},
                         {('', 'F.Cu'), ('GND', 'In1.Cu')})
        self.assertTrue(any(p['ref'] == 'U_XU' and p['number'] == '59' for p in actual['pads_fcu_intersecting_roi']))
        self.assertTrue(any(p['ref'] == 'U_XU' and p['number'] == '60' for p in actual['pads_fcu_intersecting_roi']))


if __name__ == '__main__':
    unittest.main()
