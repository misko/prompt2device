"""Captured-footprint positive and negative controls; no browser writes."""
import unittest
import mapping
import loaded_j1_analysis as audit


class LoadedJ1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit.analyze()

    def test_baseline_and_rotation_only_fail(self):
        for name in ('A', 'B'):
            errors = self.report['trials'][name]['captured_footprint']
            self.assertGreater(errors['max_pin_mm'], 1)
            self.assertGreater(errors['max_peg_mm'], 1)

    def test_c_aligns_all_features(self):
        errors = self.report['trials']['C']['captured_footprint']
        self.assertLess(errors['max_pin_mm'], .015)
        self.assertLess(errors['max_peg_mm'], .005)
        self.assertFalse(self.report['production_ready'])
        self.assertFalse(self.report['live_C_verified'])

    def test_units_and_origin(self):
        pins, pegs, transform, header = audit.footprint()
        self.assertAlmostEqual(abs(pegs[1][0]-pegs[0][0]), 12.7)
        self.assertAlmostEqual(pins['1'][1], .890016)
        self.assertLess(max(transform['child_centre_delta_mil']), .1)
        self.assertNotEqual(header, audit.MODEL_UUID)

    def test_swapped_pins_are_not_silently_fitted(self):
        pins, pegs, _, _ = audit.footprint()
        row = self.report['trials']['C']['cpl']
        expected = mapping.replay(pins, pegs, row)
        pins['1'], pins['2'] = pins['2'], pins['1']
        errors = mapping.errors(*expected, *mapping.replay(pins, pegs, row))
        self.assertGreater(errors['max_pin_mm'], 2)


if __name__ == '__main__':
    unittest.main()
