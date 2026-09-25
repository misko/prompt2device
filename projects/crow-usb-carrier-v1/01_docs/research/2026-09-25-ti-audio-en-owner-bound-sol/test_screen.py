#!/usr/bin/env python3
"""Focused exact-board AUDIO_EN lower-bound checks."""
import unittest

import screen


class AudioEnOwnerBoundTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = screen.screen()

    def test_rectangular_recut_admits_foreign_input_buck_pads(self):
        self.assertEqual(self.receipt['new_foreign_native_pads_in_recut']['quiet_power'],
                         ['C_IN3.1','C_IN3.2'])
        self.assertEqual(self.receipt['new_foreign_native_pads_in_recut']['analog_ch1'], [])
        self.assertFalse(any(x['body_owner_contained'] for x in self.receipt['targets']))

    def test_minimal_resistor_move_propagates_to_audio_ic(self):
        self.assertEqual(self.receipt['minimal_resistor_south_move_mm'], .875)
        self.assertEqual(self.receipt['resistor_to_ct1_overlap_mm'], (1.03,.625))
        self.assertEqual(self.receipt['ct1_to_audio_overlap_after_clearance_mm'],
                         (2.49,.15))
        self.assertEqual(self.receipt['prior_source_generated_trial_status'],
                         'REJECTED_LOCALITY_DRC_FOREIGN')


if __name__ == '__main__':
    unittest.main()
