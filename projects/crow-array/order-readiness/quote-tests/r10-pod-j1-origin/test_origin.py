import copy
import unittest
import origin_test as c


class OriginTrial(unittest.TestCase):
    def setUp(self):
        self.b = (c.AB / c.ab.TRIAL).read_bytes()
        self.pos = [10.556, 9.390]
        self.trial = c.make_c(self.b, self.pos)
        self.native = {str(n): [7+(n-1)*1.016, 8.5 if n%2 else 10.28] for n in range(1,9)}
        self.vendor = {n: [self.pos[i]-v[i] for i in (0,1)] for n,v in self.native.items()}
        self.npegs = [[4.210,5.960], [16.910,5.960]]
        self.vpegs = [[self.pos[i]-p[i] for i in (0,1)] for p in self.npegs]

    def test_single_field(self):
        self.assertEqual(c.compare(self.b,self.trial,self.pos), [('J1','Mid Y','-8.373000mm','-9.390000mm')])
        self.assertEqual(sum(a!=b for a,b in zip(self.b.splitlines(),self.trial.splitlines())),1)

    def test_derived_geometry(self):
        self.assertAlmostEqual(c.derive(self.native,self.vendor,self.npegs,self.vpegs)['conditional_catalog_insertion_native_mm'][1],9.390)

    def test_bad_numbering(self):
        self.vendor['1'],self.vendor['8'] = self.vendor['8'],self.vendor['1']
        with self.assertRaises(ValueError):c.derive(self.native,self.vendor,self.npegs,self.vpegs)

    def test_bad_peg(self):
        self.vpegs[0][1] += 1
        with self.assertRaises(ValueError):c.derive(self.native,self.vendor,self.npegs,self.vpegs)

    def test_missing_pin(self):
        del self.vendor['8']
        with self.assertRaises(ValueError):c.derive(self.native,self.vendor,self.npegs,self.vpegs)

    def test_A_not_B(self):
        with self.assertRaises(ValueError):c.make_c((c.AB/c.ab.BASELINE).read_bytes(),self.pos)

    def test_changed_other_ref(self):
        with self.assertRaises(ValueError):c.compare(self.b,self.trial.replace(b'C1,25.860000mm',b'C1,26.860000mm'),self.pos)

    def test_bad_pose_or_bytes(self):
        for data in (self.trial.replace(b'-9.390000mm',b'-7.356000mm'), self.trial.replace(b'180.000000,Top',b'0.000000,Top'), self.trial.replace(b'\n',b'\r\n')):
            with self.subTest(data=data[-80:]):
                with self.assertRaises(ValueError):c.compare(self.b,data,self.pos)

    def test_unexpected_new_origin(self):
        with self.assertRaises(ValueError):c.make_c(self.b,[10.556,8.373])

    def test_real_sources(self):
        geo=c.geometry()
        self.assertLess(geo['max_pin_error_mm'],.015)
        self.assertLess(geo['max_peg_error_mm'],.005)


if __name__ == '__main__':unittest.main()
