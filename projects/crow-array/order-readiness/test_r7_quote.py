import json
from pathlib import Path
import tempfile
import unittest
import r7_quote as r


def fabrication_tree(text):
    """Ignore only non-fabricated metadata/model/Fab/courtyard graphics."""
    def visit(n):
        kind=r.q.atom(n)
        if kind in ('property','descr','tags','model'): return None
        if kind.startswith('fp_') and any(isinstance(c,list) and
                r.q.atom(c)=='layer' and r.q.atom(c,1) in ('"F.Fab"','"F.CrtYd"') for c in n):return None
        result=[]
        for i,c in enumerate(n):
            if i==1 and kind=='footprint':continue
            v=visit(c) if isinstance(c,list) else c.group()
            if v is not None:result.append(v)
        return result
    return visit(r.q.forms(text)[-1])


class R7Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='crow-r7-test-')
        cls.out=Path(cls.tmp.name)/'package';r.build(cls.out)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_replay(self):self.assertEqual(r.verify(self.out)['result'],'PASS')

    def test_copper_drills_silk_and_fabrication_preserved(self):
        for b in ('carrier','pod'):
            rel=f'native/pcb/{b}/{b}.kicad_pcb'
            self.assertEqual(fabrication_tree((r.BASE/rel).read_text()),
                             fabrication_tree((self.out/rel).read_text()))
            self.assertEqual((r.BASE/f'{b}-gerbers.zip').read_bytes(),(self.out/f'{b}-gerbers.zip').read_bytes())

    def test_exact_identities_quantities_and_coverage(self):
        totals={'1206L010/30NR':0,'TSR 1-2450':0}
        for b,n in [('carrier',2),('pod',8)]:
            bom=r.q.read_csv(self.out/f'{b}-bom.csv'); cpl=r.q.read_csv(self.out/f'{b}-cpl.csv')
            refs=[v for row in bom for v in row['Designator'].split(',')]
            self.assertEqual(len(refs),len(set(refs)))
            self.assertEqual(sorted(refs),sorted(x['Designator'] for x in cpl))
            for row in bom:
                self.assertEqual(int(row['Quantity']),len(row['Designator'].split(',')))
                if row['MPN'] in totals:totals[row['MPN']]+=n*int(row['Quantity'])
                if row['MPN'] in totals:self.assertEqual(row['Comment'],row['MPN'])
            old=r.q.read_csv(r.BASE/f'{b}-bom.csv')
            self.assertEqual([v for v in old if v['MPN'].startswith('CB3LV')],
                             [v for v in bom if v['MPN'].startswith('CB3LV')])
        self.assertEqual(totals,{'1206L010/30NR':24,'TSR 1-2450':2})
        scope=r.q.read_csv(self.out/'scope.csv')
        self.assertEqual(sum(int(x['installed_batch']) for x in scope),524)
        self.assertEqual(next(x['footprint'] for x in scope if x['reference']=='U10'),r.NEW_FP)

    def test_only_u10_cpl_change(self):
        old=r.q.read_csv(r.BASE/'carrier-cpl.csv');new=r.q.read_csv(self.out/'carrier-cpl.csv')
        self.assertEqual([a['Designator'] for a,b in zip(old,new) if a!=b],['U10'])
        u=next(x for x in new if x['Designator']=='U10')
        self.assertEqual((u['Mid X'],u['Mid Y']),('184.53mm','-36.25mm'))
        self.assertEqual((r.BASE/'pod-cpl.csv').read_bytes(),(self.out/'pod-cpl.csv').read_bytes())

    def test_reject_changed_cts(self):
        p=self.out/'carrier-bom.csv';old=p.read_bytes()
        try:
            p.write_bytes(old.replace(b'CB3LV-3I-12M288000',b'WRONG-CLOCK'))
            with self.assertRaises(ValueError):r.verify(self.out)
        finally:p.write_bytes(old)

    def test_refuse_overwrite(self):
        with self.assertRaises(ValueError):r.build(self.out)

    def test_no_production_promotion(self):
        m=json.loads((self.out/'manifest.json').read_text())
        self.assertFalse(m['production_ready']);self.assertFalse(m['purchase_authorized'])
        self.assertEqual(m['assembled'],{'carrier':2,'pod':8})
        self.assertEqual(m['fabricated'],{'carrier':5,'pod':10})


if __name__=='__main__':unittest.main()
