import unittest
import pcbnew
import check


class DiodeReviewTests(unittest.TestCase):
    def test_current_native_and_bound_sources(self):
        r=check.run()
        self.assertFalse(r['production_ready'])
        self.assertAlmostEqual(r['calculations']['off_rail_V'],2.59693693827)

    def test_old_1800_ohm_value_fails(self):
        with self.assertRaisesRegex(ValueError,'off-rail'):
            check.arithmetic(rc=1800)

    def test_missing_sink_fails(self):
        with self.assertRaisesRegex(ValueError,'off-rail'):
            check.arithmetic(sink=10000)

    def test_missing_output_isolation_fails(self):
        with self.assertRaisesRegex(ValueError,'current screen'):
            check.arithmetic(rp=10)

    def test_swapped_pin_labels_fail_in_memory(self):
        board=pcbnew.LoadBoard(str(check.BASE/'native/pcb/pod/pod.kicad_pcb'))
        pads={p.GetNumber():p for p in board.FindFootprintByReference('D2').Pads()}
        pads['1'].SetNumber('2');pads['2'].SetNumber('1')
        with self.assertRaisesRegex(ValueError,'pin mapping'):
            check.check_pod(board)


if __name__=='__main__':unittest.main()
