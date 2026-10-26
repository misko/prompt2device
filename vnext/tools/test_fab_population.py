"""Population component regressions on self-contained native fixtures, not approval."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import fab_population as f


class Population(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='vnext-population-test-')
        self.addCleanup(self.tmp.cleanup); self.root = Path(self.tmp.name)
        (self.root/'proof.txt').write_text('Synthetic manual assembly policy, not approved.')
        (self.root/'Part.kicad_mod').write_text('''(footprint "Part" (version 20260206)
 (generator "pcbnew") (layer "F.Cu") (attr smd)
 (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu" "F.Mask" "F.Paste")))''')
        self.parts = [dict(ref=ref, value='part', footprint='Test:Part', physical=True,
            fields={'Manufacturer':'Maker','MPN':'Exact-1','Assembly':'SMT','Supplier':'C123'},
            pins=[{'number':'1','net':'N'}]) for ref in ('U1','U2')]
        (self.root/'intent.json').write_text(json.dumps({'components':self.parts}))
        spec = dict(footprints={'Test:Part':'Part.kicad_mod'}, _components=self.parts)
        plan = dict(layers=2, outline=[30,20], mounts=[[3,3,2,4]],
                    placements={'U1':[10,10,90], 'U2':[20,10,0]})
        f.p.make_board(self.root, spec, plan, self.root/'board.kicad_pcb')
        row = dict(source='board.kicad_pcb', intent='intent.json', quantity=5,
                   population={ref:dict(mode='mechanical' if ref=='MH1' else 'manual',
                       reason='fixture policy', evidence=['proof.txt']) for ref in ('U1','U2','MH1')})
        self.manifest = dict(version=1, boards={'carrier':row,'pod':copy.deepcopy(row)})
        self.manifest['boards']['pod']['quantity'] = 40

    def result(self): return f.data(self.root, self.manifest)

    def test_whole_system_quantities_and_native_coordinates(self):
        result = self.result()
        self.assertEqual(result['demand'], [{'manufacturer':'Maker','mpn':'Exact-1','quantity':90}])
        self.assertEqual(len(result['population']), 6); self.assertEqual(len(result['positions']), 4)
        self.assertEqual(result['positions'][0]['x_mm'], 10)
        self.assertEqual(result['positions'][0]['kicad_angle_deg'], 90)
        self.assertIn('C123', result['population'][1]['fields_json'])

    def test_dnp_accounted_but_not_procured(self):
        self.manifest['boards']['pod']['population']['U2']['mode'] = 'dnp'
        result = self.result(); self.assertEqual(result['demand'][0]['quantity'], 50)
        self.assertEqual(len(result['positions']), 3)

    def test_missing_extra_and_wrong_population_fail(self):
        original = copy.deepcopy(self.manifest)
        for kind in ('missing','extra','mechanical','no_evidence'):
            self.manifest = copy.deepcopy(original); policies=self.manifest['boards']['carrier']['population']
            if kind == 'missing': del policies['U1']
            elif kind == 'extra': policies['GHOST'] = copy.deepcopy(policies['U1'])
            elif kind == 'mechanical': policies['U1']['mode'] = 'mechanical'
            else: policies['U1']['evidence'] = []
            with self.assertRaises(ValueError): self.result()

    def test_native_identity_and_dnp_contradictions_fail(self):
        source = self.root/'board.kicad_pcb'; original=source.read_bytes()
        for kind in ('mpn','supplier','assembly','value','native_dnp'):
            source.write_bytes(original); board=f.p.pcb.LoadBoard(str(source))
            fp=board.FindFootprintByReference('U1')
            if kind == 'value': fp.SetValue('other')
            elif kind == 'native_dnp': fp.SetDNP(True)
            else: fp.GetField({'mpn':'MPN','supplier':'Supplier','assembly':'Assembly'}[kind]).SetText('other')
            f.p.pcb.SaveBoard(str(source),board)
            with self.assertRaises(ValueError): self.result()

    def test_quantity_and_duplicate_intent_fail(self):
        for quantity in (0,-1,True,1.5,'5'):
            self.manifest['boards']['carrier']['quantity']=quantity
            with self.assertRaises(ValueError): self.result()
        self.manifest['boards']['carrier']['quantity']=5
        (self.root/'intent.json').write_text(json.dumps({'components':self.parts+[self.parts[0]]}))
        with self.assertRaisesRegex(ValueError,'duplicate'): self.result()

    def test_replay_tampering_and_existing_output(self):
        output=self.root/'out'; result=f.produce(self.root,self.manifest,output)
        self.assertFalse(result['accepted']); self.assertEqual(result['order_status'],'DO-NOT-ORDER')
        self.assertEqual(f.verify(self.root,self.manifest,output),result)
        with self.assertRaisesRegex(ValueError,'existing'): f.produce(self.root,self.manifest,output)
        (output/'positions.csv').write_text('forged')
        with self.assertRaisesRegex(ValueError,'stale'): f.verify(self.root,self.manifest,output)

    def test_extra_and_linked_output_rejected(self):
        output=self.root/'out'; f.produce(self.root,self.manifest,output)
        (output/'extra').write_text('unexpected')
        with self.assertRaisesRegex(ValueError,'census'): f.verify(self.root,self.manifest,output)
        (output/'extra').unlink(); (output/'positions.csv').rename(self.root/'saved.csv')
        (output/'positions.csv').symlink_to(self.root/'saved.csv')
        with self.assertRaisesRegex(ValueError,'census'): f.verify(self.root,self.manifest,output)

    def test_linked_output_directory_rejected(self):
        output=self.root/'out'; f.produce(self.root,self.manifest,output)
        linked=self.root/'linked'; linked.symlink_to(output, target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'linked population output'):
            f.verify(self.root,self.manifest,linked)

    def test_public_export_requires_layout_acceptance(self):
        with patch.object(f.seal,'check',side_effect=ValueError('no layout seal')):
            with self.assertRaisesRegex(ValueError,'no layout seal'):
                f.export(self.root,'manifest.json','out')
        self.assertFalse((self.root/'out').exists())

    def test_malformed_input_refused_without_partial_output(self):
        with self.assertRaisesRegex(ValueError,'manifest required'): f.data(self.root, [])
        (self.root/'board.kicad_pcb').write_text('(kicad_pcb (broken')
        with self.assertRaisesRegex(ValueError,'invalid native board'):
            f.produce(self.root,self.manifest,self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_context_change_does_not_silently_renew_export(self):
        output=self.root/'out'; f.produce(self.root,self.manifest,output,{'layout':'old'})
        with self.assertRaisesRegex(ValueError,'stale population output'):
            f.verify(self.root,self.manifest,output,{'layout':'new'})

    def test_public_export_accepted_binding_and_substitution_guards(self):
        # Upstream review is mocked only in this unit fixture, never for Crow.
        (self.root/'sealed-manifest.json').write_text(json.dumps({'boards':{'carrier':{},'pod':{}}}))
        (self.root/'inputs.json').write_text(json.dumps({'boards':{
            key:{'intent':'intent.json'} for key in self.manifest['boards']}}))
        receipt=self.root/f.seal.RECEIPT; receipt.parent.mkdir(parents=True)
        receipt.write_text('synthetic receipt, not engineering acceptance')
        for key, row in self.manifest['boards'].items():
            name='sealed/'+key+'/native/'+key+'.kicad_pcb'; target=self.root/name
            target.parent.mkdir(parents=True); target.write_bytes((self.root/'board.kicad_pcb').read_bytes())
            row['source']=name
        policy=self.root/'policy.json'; policy.write_text(json.dumps(self.manifest))
        with patch.object(f.seal,'check',return_value={'review':'synthetic'}), \
             patch.object(f.seal.r,'review_json',return_value={'manifest':'sealed-manifest.json','output':'sealed'}), \
             patch.object(f.seal.r,'upstream',return_value=({}, {'inputs':'inputs.json'}, {})):
            result=f.export(self.root,'policy.json','out')
            self.assertEqual(result,f.export(self.root,'policy.json','out',True))
            self.assertEqual(result['acceptance_context']['layout_receipt_sha256'],f.p.sha(receipt))
            original=copy.deepcopy(self.manifest)
            self.manifest['boards']['carrier']['source']='board.kicad_pcb'
            policy.write_text(json.dumps(self.manifest))
            with self.assertRaisesRegex(ValueError,'source differs'): f.export(self.root,'policy.json','bad')
            self.manifest=original; del self.manifest['boards']['pod']
            policy.write_text(json.dumps(self.manifest))
            with self.assertRaisesRegex(ValueError,'coverage differs'): f.export(self.root,'policy.json','bad')
            self.assertFalse((self.root/'bad').exists())

    def test_factory_native_exclusions_and_manual_disposition(self):
        source=self.root/'board.kicad_pcb'; original=source.read_bytes()
        for exclusion in ('SetExcludedFromBOM','SetExcludedFromPosFiles'):
            source.write_bytes(original); board=f.p.pcb.LoadBoard(str(source))
            getattr(board.FindFootprintByReference('U1'),exclusion)(True)
            f.p.pcb.SaveBoard(str(source),board)
            policy=self.manifest['boards']['carrier']['population']['U1']; policy['mode']='factory'
            with self.assertRaisesRegex(ValueError,'exclusion contradicts'): self.result()
            policy['mode']='manual'; self.result()
            if exclusion == 'SetExcludedFromPosFiles':
                policy['mode']='consigned'
                with self.assertRaisesRegex(ValueError,'exclusion contradicts'): self.result()
                policy['mode']='manual'

    def test_explicit_all_dnp_retains_coverage_with_zero_demand(self):
        for row in self.manifest['boards'].values():
            for ref in ('U1','U2'): row['population'][ref]['mode']='dnp'
        output=self.root/'out'; result=f.produce(self.root,self.manifest,output)
        self.assertEqual(result['counts']['carrier']['electrical'],2)
        self.assertEqual(result['counts']['carrier']['populated'],0)
        self.assertEqual((output/'demand.csv').read_text(),'manufacturer,mpn,quantity\n')
        self.assertEqual(len((output/'positions.csv').read_text().splitlines()),1)
        self.assertEqual(f.verify(self.root,self.manifest,output),result)


if __name__=='__main__': unittest.main()
