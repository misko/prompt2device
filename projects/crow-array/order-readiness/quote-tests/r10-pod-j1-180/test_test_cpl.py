import unittest
import test_cpl as c


class TestSingleFieldTrial(unittest.TestCase):
    def setUp(self):
        self.base=c.SOURCE.read_bytes()
        self.trial=c.make_trial(self.base)

    def test_exact_change(self):
        self.assertEqual(c.compare(self.base,self.trial),[('J1','Rotation','0.000000','180.000000')])
        self.assertEqual(len(c.rows(self.trial)),29)

    def test_wrong_angle(self):
        with self.assertRaises(ValueError):c.compare(self.base,self.trial.replace(b'J1,10.556000mm,-8.373000mm,180.000000',b'J1,10.556000mm,-8.373000mm,90.000000'))

    def test_wrong_xy(self):
        with self.assertRaises(ValueError):c.compare(self.base,self.trial.replace(b'J1,10.556000mm',b'J1,11.556000mm'))

    def test_other_ref_changed(self):
        with self.assertRaises(ValueError):c.compare(self.base,self.trial.replace(b'C1,25.860000mm',b'C1,26.860000mm'))

    def test_wrong_side(self):
        with self.assertRaises(ValueError):c.compare(self.base,self.trial.replace(b'J1,10.556000mm,-8.373000mm,180.000000,Top',b'J1,10.556000mm,-8.373000mm,180.000000,Bottom'))

    def test_duplicate_ref(self):
        with self.assertRaises(ValueError):c.compare(self.base,self.trial.replace(b'C1,',b'J1,',1))

    def test_missing_row(self):
        with self.assertRaises(ValueError):c.compare(self.base,b'\n'.join(self.trial.split(b'\n')[:-2])+b'\n')

    def test_unexpected_baseline(self):
        with self.assertRaises(ValueError):c.make_trial(self.trial)

    def test_bytes_preserved(self):
        before=self.base.splitlines(keepends=True)
        after=self.trial.splitlines(keepends=True)
        self.assertEqual(sum(a!=b for a,b in zip(before,after)),1)
        with self.assertRaises(ValueError):c.compare(self.base,self.trial.replace(b'\n',b'\r\n'))


if __name__=='__main__':unittest.main()
