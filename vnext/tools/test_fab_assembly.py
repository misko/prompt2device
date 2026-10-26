"""Source-bound assembly translation tests; synthetic geometry is not approval."""
import copy
import csv
import io
import json
import re
import unittest

import fab_population as f
import test_fab_population as fixture


class Assembly(unittest.TestCase):
    def setUp(self):
        fixture.Population.setUp(self)
        mapping = {}
        for key, board in self.manifest['boards'].items():
            board['population']['U1']['mode'] = 'factory'
            board['population']['U2']['mode'] = 'consigned'
            mapping[key] = {'source_sha256':f.p.sha(self.root/board['source']),
                'placements':{ref:dict(manufacturer='Maker',mpn='Exact-1',footprint='Test:Part',
                    supplier_code='C123',centroid_offset_mm=[1,-2],rotation_deg=270,
                    evidence=['proof.txt']) for ref in ('U1','U2')}}
        self.manifest['assembly'] = dict(version=1,boards=mapping)

    def output(self):
        result=f.data(self.root,self.manifest)
        return f.assembly_files(self.root,self.manifest,result)

    def rows(self,name): return list(csv.DictReader(io.StringIO(self.output()[name])))

    def test_explicit_geometry_and_split_handling(self):
        rows=self.rows('carrier-factory-cpl.csv')
        self.assertEqual(rows,[{'Designator':'U1','Mid X':'11.000000mm','Mid Y':'-8.000000mm',
                               'Rotation':'270.000000','Layer':'Top'}])
        self.assertEqual(self.rows('carrier-consigned-cpl.csv')[0]['Designator'],'U2')
        self.assertEqual(self.rows('carrier-factory-bom.csv')[0]['Quantity'],'1')
        self.assertEqual(f.data(self.root,self.manifest)['demand'][0]['quantity'],90)

    def test_bottom_is_not_silently_mirrored_or_angle_inferred(self):
        source=self.root/'board.kicad_pcb'; board=f.p.pcb.LoadBoard(str(source))
        fp=board.FindFootprintByReference('U1'); fp.Flip(fp.GetPosition(),False)
        f.p.pcb.SaveBoard(str(source),board)
        for spec in self.manifest['assembly']['boards'].values():spec['source_sha256']=f.p.sha(source)
        row=self.rows('carrier-factory-cpl.csv')[0]
        self.assertEqual(row['Layer'],'Bottom')
        self.assertEqual((row['Mid X'],row['Mid Y'],row['Rotation']),
                         ('11.000000mm','-8.000000mm','270.000000'))

    def test_missing_extra_stale_coverage_rejected(self):
        original=copy.deepcopy(self.manifest)
        for kind in ('board','reference','extra','stale'):
            self.manifest=copy.deepcopy(original); mapping=self.manifest['assembly']['boards']
            if kind=='board': del mapping['pod']
            elif kind=='reference': del mapping['carrier']['placements']['U1']
            elif kind=='extra': mapping['carrier']['placements']['MH1']=mapping['carrier']['placements']['U1']
            else: mapping['carrier']['source_sha256']='0'*64
            with self.assertRaises(ValueError):self.output()

    def test_identity_and_evidence_rejected(self):
        original=copy.deepcopy(self.manifest)
        for name,value in [('manufacturer','Other'),('mpn','Wrong'),('footprint','Other:Part'),
                           ('supplier_code','C999'),('supplier_code',''),('evidence',[])]:
            self.manifest=copy.deepcopy(original)
            self.manifest['assembly']['boards']['carrier']['placements']['U1'][name]=value
            with self.assertRaises(ValueError):self.output()

    def test_geometry_must_be_finite_and_rotation_explicit(self):
        original=copy.deepcopy(self.manifest)
        for name,value in [('centroid_offset_mm',[float('nan'),0]),('centroid_offset_mm',[True,0]),
                           ('centroid_offset_mm',[0]),('rotation_deg',float('inf')),
                           ('rotation_deg',360),('rotation_deg',-1),('rotation_deg',True)]:
            self.manifest=copy.deepcopy(original)
            self.manifest['assembly']['boards']['carrier']['placements']['U1'][name]=value
            with self.assertRaises(ValueError):self.output()

    def test_no_machine_population_keeps_board_header_files(self):
        for key,board in self.manifest['boards'].items():
            for ref in ('U1','U2'):board['population'][ref]['mode']='manual'
            self.manifest['assembly']['boards'][key]['placements']={}
        output=self.output();self.assertEqual(len(output),8)
        self.assertTrue(all(len(text.splitlines())==1 for text in output.values()))
        self.assertEqual(f.data(self.root,self.manifest)['demand'][0]['quantity'],90)

    def test_mapping_evidence_and_native_staleness_invalidate_replay(self):
        output=self.root/'out';f.produce(self.root,self.manifest,output)
        f.verify(self.root,self.manifest,output)
        original=(self.root/'proof.txt').read_bytes()
        (self.root/'proof.txt').write_text('Revised fixture geometry evidence')
        with self.assertRaisesRegex(ValueError,'stale'):f.verify(self.root,self.manifest,output)
        (self.root/'proof.txt').write_bytes(original)
        self.manifest['assembly']['boards']['carrier']['placements']['U1']['rotation_deg']=90
        with self.assertRaisesRegex(ValueError,'stale'):f.verify(self.root,self.manifest,output)

    def test_conflicting_supplier_code_identity_rejected(self):
        # Change both native and intent to a different exact part; the same code
        # still cannot identify both parts in an otherwise consistent mapping.
        source=self.root/'board.kicad_pcb'; board=f.p.pcb.LoadBoard(str(source))
        board.FindFootprintByReference('U2').GetField('MPN').SetText('Exact-2')
        f.p.pcb.SaveBoard(str(source),board)
        self.parts[1]['fields']['MPN']='Exact-2'
        (self.root/'intent.json').write_text(json.dumps({'components':self.parts}))
        for row in self.manifest['assembly']['boards'].values():
            row['source_sha256']=f.p.sha(source);row['placements']['U2']['mpn']='Exact-2'
        with self.assertRaisesRegex(ValueError,'conflicting'):self.output()

    def test_malformed_native_supplier_code_cannot_be_replaced_silently(self):
        source=self.root/'board.kicad_pcb'; board=f.p.pcb.LoadBoard(str(source))
        # Both authoritative sources agree on the malformed field; translation
        # must not use that malformed spelling to bypass identity consistency.
        for fp in board.GetFootprints():
            if fp.GetReference() not in ('U1','U2'):continue
            field=f.p.pcb.PCB_FIELD(fp,f.p.pcb.FIELD_T_USER,'LCSC Part #');field.SetText('C234x')
            fp.Add(field)
        f.p.pcb.SaveBoard(str(source),board)
        for part in self.parts:part['fields']['LCSC Part #']='C234x'
        (self.root/'intent.json').write_text(json.dumps({'components':self.parts}))
        for row in self.manifest['assembly']['boards'].values():row['source_sha256']=f.p.sha(source)
        with self.assertRaisesRegex(ValueError,'supplier code contradicts'):self.output()

    def test_grouping_does_not_multiply_board_quantity(self):
        self.manifest['boards']['carrier']['population']['U2']['mode']='factory'
        row=self.rows('carrier-factory-bom.csv')[0]
        self.assertEqual(row['Designator'],'U1,U2');self.assertEqual(row['Quantity'],'2')
        self.assertEqual(len(self.rows('carrier-factory-cpl.csv')),2)
        self.assertEqual(self.rows('carrier-consigned-bom.csv'),[])

    def test_cpl_and_actual_gerber_share_absolute_datum(self):
        source=self.root/'board.kicad_pcb'; board=f.p.pcb.LoadBoard(str(source))
        board.GetDesignSettings().SetAuxOrigin(f.p.pcb.VECTOR2I(3000000,4000000))
        f.p.pcb.SaveBoard(str(source),board)
        for row in self.manifest['assembly']['boards'].values():row['source_sha256']=f.p.sha(source)
        plots=self.root/'plots';plots.mkdir()
        # Same absolute-origin invocation used by fab_payload; a nonzero board
        # auxiliary origin must not shift just one of the manufacturing files.
        f.p.command(['kicad-cli','pcb','export','gerbers','--no-protel-ext',
                     '--layers','F.Cu','--output',str(plots)+'/',str(source)])
        text=(plots/'board-F_Cu.gbr').read_text()
        match=re.search(r'%TO.P,U1,1\*%.*?X(-?\d+)Y(-?\d+)D03\*',text,re.S)
        self.assertIsNotNone(match)
        x,y=[int(n)/1e6 for n in match.groups()]
        row=self.rows('carrier-factory-cpl.csv')[0]
        self.assertEqual(float(row['Mid X'][:-2]),x+1)
        self.assertEqual(float(row['Mid Y'][:-2]),y+2)


if __name__=='__main__':unittest.main()
