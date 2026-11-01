"""Run /usr/bin/python3 -B test_r8_quote.py; no network or order actions."""
import json
from pathlib import Path
import re
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
import pcbnew as pcb
import r8_quote as r


def normalized_export(data):
    text=data.decode()
    text=re.sub(r'(?m)^%TF\.CreationDate,[^\n]*$', '%TF.CreationDate,TIMESTAMP*%',text)
    text=re.sub(r'(?m)^(G04 Created by KiCad .* date )[^\n]*$',r'\1TIMESTAMP*',text)
    text=re.sub(r'(?m)^(; DRILL file KiCad .* date )[^\n]*$',r'\1TIMESTAMP',text)
    text=re.sub(r'(?m)^; #@! TF\.CreationDate,[^\n]*$', '; #@! TF.CreationDate,TIMESTAMP',text)
    return text


class Quote(unittest.TestCase):
    def test_quantities_and_scope(self):
        rows=r.q.read_csv(r.OUT/'scope.csv')
        counts={owner:sum(int(x['installed_batch']) for x in rows if x['owner']==owner)
                for owner in ('JLC_SMT','JLC_THT','HOME')}
        self.assertEqual(counts,{'JLC_SMT':478,'JLC_THT':28,'HOME':18})
        plan={x['mpn']:x for x in r.q.read_csv(r.OUT/'procurement-plan.csv')}
        self.assertEqual(plan[r.MPN]['installed_2c8p'],'2')
        self.assertEqual(plan['CL21B105KBFNNNE']['installed_2c8p'],'14')
        before=r.q.read_csv(r.BASE/'scope.csv')
        changed=[(a['board'],a['reference']) for a,b in zip(before,rows) if a!=b]
        self.assertEqual(sorted(changed),[('carrier','C4'),('carrier','X1')])

    def test_native_cpl_and_pad_nets(self):
        b=pcb.LoadBoard(str(r.OUT/'native/pcb/carrier/carrier.kicad_pcb'))
        old=pcb.LoadBoard(str(r.BASE/'native/pcb/carrier/carrier.kicad_pcb'))
        fps={f.GetReference():f for f in b.GetFootprints()}
        prior={f.GetReference():f for f in old.GetFootprints()}
        self.assertEqual(set(fps),set(prior))
        def nets(f):return sorted((p.GetNumber(),p.GetNetname()) for p in f.Pads() if p.GetNumber())
        def pose(f):return (f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees())
        for ref,f in fps.items():
            self.assertEqual(nets(f),nets(prior[ref]),ref)
            if ref not in ('X1','C4'):self.assertEqual(pose(f),pose(prior[ref]),ref)
        rows={x['Designator']:x for x in r.q.read_csv(r.OUT/'carrier-cpl.csv')}
        for ref in ('X1','C4'):
            f=fps[ref];row=rows[ref]
            self.assertAlmostEqual(float(row['Mid X'].removesuffix('mm')),pcb.ToMM(f.GetPosition().x))
            self.assertAlmostEqual(float(row['Mid Y'].removesuffix('mm')),-pcb.ToMM(f.GetPosition().y))
            self.assertAlmostEqual(float(row['Rotation']),f.GetOrientationDegrees())
            self.assertEqual(row['Layer'],'Top')
        self.assertEqual(fps['X1'].GetFPIDAsString(),r.FP)
        self.assertEqual(fps['X1'].GetFieldText('MPN'),r.MPN)
        self.assertEqual(fps['C4'].GetFieldText('MPN'),'CL21B105KBFNNNE')

    def test_connectivity_unchanged(self):
        def nets(path):
            tree=ET.parse(path).getroot()
            return sorted((n.attrib['name'],sorted((p.attrib['ref'],p.attrib['pin']) for p in n.findall('node')))
                          for n in tree.findall('./nets/net'))
        self.assertEqual(nets(r.ROOT/'substitutions-20261101/r7-validation/carrier-r7.xml'),nets(r.OUT/'checks/netlist.xml'))

    def test_gerber_drill_replay(self):
        with tempfile.TemporaryDirectory(prefix='crow-r8-test-exports-') as tmp:
            folder=Path(tmp);board=r.OUT/'native/pcb/carrier/carrier.kicad_pcb'
            r.command('kicad-cli','pcb','export','gerbers','--no-protel-ext','--layers',r.LAYERS,'-o',str(folder)+'/',board)
            r.command('kicad-cli','pcb','export','drill','--excellon-separate-th','--drill-origin','absolute','-o',str(folder)+'/',board)
            with zipfile.ZipFile(r.OUT/'carrier-gerbers.zip') as z:
                names={p.name for p in folder.iterdir() if p.suffix in ('.gbr','.drl')}
                self.assertEqual(names,set(z.namelist()));self.assertEqual(len(names),13)
                for name in names:self.assertEqual(normalized_export(z.read(name)),normalized_export((folder/name).read_bytes()),name)
        self.assertNotEqual(r.q.sha(r.OUT/'carrier-gerbers.zip'),r.q.sha(r.BASE/'carrier-gerbers.zip'))

    def test_tampering_rejected(self):
        with tempfile.TemporaryDirectory(prefix='crow-r8-tamper-') as tmp:
            target=Path(tmp)/'copy';shutil.copytree(r.OUT,target)
            p=target/'carrier-cpl.csv';p.write_text(p.read_text().replace('86.0mm','86.1mm'))
            with self.assertRaisesRegex(ValueError,'Changed/missing/extra payload'):r.verify(target)

    def test_pdf_and_authority(self):
        text=r.command('pdftotext',r.OUT/'carrier-schematic.pdf','-')
        self.assertIn(r.MPN,text);self.assertIn('1uF 50V X7R 10% CLOCK',text)
        self.assertNotIn('CB3LV-3I-12M288000',text)
        m=json.loads((r.OUT/'manifest.json').read_text())
        self.assertFalse(m['production_ready']);self.assertFalse(m['purchase_authorized'])
        self.assertFalse(m['stage_acceptance_issued']);self.assertIsNone(m['oscillator_warehouse_date'])


if __name__=='__main__':unittest.main(verbosity=2)
