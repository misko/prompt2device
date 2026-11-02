import copy
import math
import tempfile
from pathlib import Path
import unittest
import render_board as r


class RenderBoard(unittest.TestCase):
    def test_all_angles(self):
        v=r.views();self.assertEqual(len(v),22)
        directions={tuple(round(x/math.sqrt(sum(a*a for a in d)),6) for x in d) for d,u in v.values()}
        self.assertEqual(len(directions),22)
        for name,(d,u) in v.items():
            if name.startswith(('upper','lower')):
                self.assertAlmostEqual(abs(d[2]),math.sqrt(.5))
                self.assertAlmostEqual(sum(x*x for x in d),1)

    def sample(self):
        f=dict(ref='J1',mpn='example',position=[10,20],angle=0,bottom=False,
               pads=[dict(number='1',position=[10,20],drill=[1,1]),
                     dict(number='2',position=[12,21],drill=[1,1]),
                     dict(number='',position=[9,18],drill=[3,3])])
        s=dict(mpn='example',source='independent drawing',limitations='diagnostic',
               expected_pads={'1':[0,0],'2':[2,1]},expected_pegs=[[-1,-2]],tolerance_mm=.01,
               mouth_direction=[0,-1],intended_direction=[0,-1])
        return f,s

    def test_matching_witnesses(self):
        f,s=self.sample();c=r.connector_check(f,s)
        self.assertEqual((c['registration'],c['direction']),('PASS','PASS'))

    def test_reversed_part_fails(self):
        f,s=self.sample();s['mouth_direction']=[0,1]
        self.assertEqual(r.connector_check(f,s)['direction'],'FAIL')

    def test_bad_peg_fails(self):
        f,s=self.sample();f['pads'][2]['position'][1]+=4.8
        self.assertEqual(r.connector_check(f,s)['registration'],'FAIL')

    def test_90_degree_native_transform(self):
        f,s=self.sample();f['angle']=90
        self.assertEqual(r.native_point([2,1],f),[11,18])
        s['expected_pegs']=[]
        f['pads'][1]['position']=[11,18];s['intended_direction']=[-1,0]
        c=r.connector_check(f,s);self.assertEqual((c['registration'],c['direction']),('PASS','PASS'))

    def test_bottom_not_silently_mirrored(self):
        f,s=self.sample();f['bottom']=True
        with self.assertRaisesRegex(ValueError,'Bottom'):r.connector_check(f,s)

    def test_missing_pad_rejected(self):
        f,s=self.sample();f['pads']=f['pads'][1:]
        with self.assertRaisesRegex(ValueError,'Missing numbered'):r.connector_check(f,s)

    def test_wrong_model_identity_rejected(self):
        f,s=self.sample();f['mpn']='another-device'
        with self.assertRaisesRegex(ValueError,'MPN'):r.connector_check(f,s)

    def test_tamper_rejected(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);p=root/'top.png';p.write_bytes(b'original')
            (root/'manifest.json').write_text(json.dumps({'top.png':r.sha(p)}))
            p.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'Output bytes'):r.verify(root)


if __name__=='__main__':unittest.main(verbosity=2)
