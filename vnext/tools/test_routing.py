"""Real native routing regressions; fixture upstream is mocked, not engineering."""
import json
import re
import shutil
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import routing as r


class Rules(unittest.TestCase):
    def report(self, **changes):
        x = dict(coordinate_units='mm', ignored_checks=[], violations=[],
                 unconnected_items=[], schematic_parity=[])
        x.update(changes); return x

    def test_complete(self):
        self.assertTrue(r.drc_summary(self.report())['route_complete'])

    def test_open_short_and_demotion_are_not_acceptance(self):
        for data in [self.report(unconnected_items=[{}]),
                     self.report(violations=[{'type':'shorting_items','severity':'warning'}]),
                     self.report(violations=[{'type':'clearance','severity':'exclusion'}])]:
            self.assertFalse(r.drc_summary(data)['route_complete'])

    def test_hidden_checks_rejected(self):
        with self.assertRaisesRegex(ValueError, 'ignored'):
            r.drc_summary(self.report(ignored_checks=[{'key':'clearance'}]))

    def test_review_failure_and_missing_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            review = dict(schema=1, stage='KICAD-MATING-IMPORT', verdict='FAIL')
            with self.assertRaisesRegex(ValueError, 'not PASS'):
                r.validate_review(root, review, 'mating', {})
            review.update(verdict='PASS',author='a',reviewer='b',subjects={},checks={})
            with self.assertRaisesRegex(ValueError, 'missing required'):
                r.validate_review(root, review, 'mating', {'source':'digest'})


class Native(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='vnext-route-test-')
        self.addCleanup(self.tmp.cleanup); self.root = Path(self.tmp.name)
        self.write('lib/Pad.kicad_mod', '''(footprint "Pad" (version 20260206) (generator "pcbnew")
 (layer "F.Cu") (attr smd)
 (property "Reference" "R" (at 0 -2) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))
 (property "Value" "Pad" (at 0 2) (layer "F.Fab") (effects (font (size 1 1) (thickness .15))))
 (fp_rect (start -1 -1) (end 1 1) (stroke (width .05) (type default)) (fill none) (layer "F.CrtYd"))
 (pad "1" smd rect (at 0 0) (size 1 1) (layers "F.Cu" "F.Paste" "F.Mask")))''')
        spec = {'footprints':{'Test:Pad':'lib/Pad.kicad_mod'},'_components':[
            {'ref':ref,'value':'Pad','footprint':'Test:Pad','pins':[{'number':'1','net':'N'}]}
            for ref in ('U1','U2')]}
        plan = {'layers':2,'outline':[30,20],'mounts':[],
                'placements':{'U1':[5,5,0],'U2':[15,5,0]}}
        r.p.make_board(self.root,spec,plan,self.root/'placed.kicad_pcb')
        board = r.p.pcb.LoadBoard(str(self.root/'placed.kicad_pcb'))
        track = r.p.pcb.PCB_TRACK(board);track.SetStart(r.p.vector(5,5));track.SetEnd(r.p.vector(15,5))
        track.SetWidth(250000);track.SetLayer(r.p.pcb.F_Cu);track.SetNetCode(board.FindNet('N').GetNetCode());board.Add(track)
        r.p.pcb.SaveBoard(str(self.root/'source.kicad_pcb'),board)
        ignored = ('missing_courtyard','track_not_centered_on_via','tuning_profile_track_geometries',
                   'footprint_filters_mismatch','footprint_type_mismatch')
        self.write('source.kicad_pro',json.dumps({'board':{'design_settings':{
            'drc_exclusions':[], 'rule_severities':dict.fromkeys(ignored,'error'),
            'rules':{'min_clearance':.2,'min_track_width':.15}}}}))
        self.data = {'version':1,'boards':{'test':{'source':'source.kicad_pcb','project':'source.kicad_pro'}}}
        self.write('manifest.json',json.dumps(self.data))

    def write(self,name,text):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)

    def produce(self):
        return r.produce(self.root,self.data,self.root/'out')

    def verify(self):
        with patch.object(r,'inputs',return_value=(self.data,{})):
            return r.verify(self.root,'manifest.json','out')

    def test_real_native_build_and_replay(self):
        result=self.produce();self.assertTrue(result['test']['route_complete'],result)
        self.verify()

    def test_documented_manifest_binds_transitive_evidence(self):
        # Exercise the actual documented JSON through the real input parser;
        # mocked upstream acceptance is fixture-only, not a Crow approval.
        manual=(r.p.ROOT/r.MANUAL).read_text()
        data=json.loads(re.findall(r'```json\s*\n(.*?)\n```',manual,re.S)[0])
        self.write('manifest.json',json.dumps(data))
        self.write('producer.py','# fixture producer, never executed\n')
        self.write('producer-inputs.json','{"fixture":true}\n')
        (self.root/'accepted').mkdir()
        shutil.copyfile(self.root/'placed.kicad_pcb',self.root/'accepted/main.kicad_pcb')
        self.write(r.MATING,'{}')
        with patch.object(r,'upstream',return_value=({}, {'output':'accepted'},
                                                    {'boards':{'main':{}}})), \
             patch.object(r,'check',return_value={}), \
             patch.object(r,'base_subjects',return_value={}):
            parsed,subjects=r.inputs(self.root,'manifest.json')
            self.assertEqual(parsed,data)
            for name in data['evidence']:
                self.assertEqual(subjects[name],r.p.sha(self.root/name))
            data['boards']['main']['evidence']=data.pop('evidence')
            self.write('manifest.json',json.dumps(data))
            with self.assertRaisesRegex(ValueError,'unsupported board source fields'):
                r.inputs(self.root,'manifest.json')

    def test_missing_track_and_forged_report(self):
        board=r.p.pcb.LoadBoard(str(self.root/'source.kicad_pcb'))
        for t in list(board.GetTracks()):board.Remove(t)
        r.p.pcb.SaveBoard(str(self.root/'source.kicad_pcb'),board)
        self.assertFalse(self.produce()['test']['route_complete'])
        self.write('out/checks.json','{}')
        with self.assertRaisesRegex(ValueError,'forged'):self.verify()

    def test_native_tamper_rejected(self):
        self.produce();target=self.root/'out/test.kicad_pcb'
        board=r.p.pcb.LoadBoard(str(target));track=next(iter(board.GetTracks()))
        track.SetEnd(r.p.vector(14,5));r.p.pcb.SaveBoard(str(target),board)
        with self.assertRaisesRegex(ValueError,'stale routing artifact'):self.verify()

    def test_pad_or_placement_change_not_hidden_by_copper(self):
        base=r.identity(self.root/'placed.kicad_pcb')
        self.assertEqual(base,r.identity(self.root/'source.kicad_pcb'))
        board=r.p.pcb.LoadBoard(str(self.root/'source.kicad_pcb'))
        pad=next(iter(board.FindFootprintByReference('U1').Pads()));pad.SetSize(r.p.vector(2,2))
        r.p.pcb.SaveBoard(str(self.root/'source.kicad_pcb'),board)
        self.assertNotEqual(base,r.identity(self.root/'source.kicad_pcb'))

    def test_existing_candidate_not_overwritten(self):
        self.produce()
        with self.assertRaises(FileExistsError):self.produce()

    def test_real_short_cannot_pass(self):
        board=r.p.pcb.LoadBoard(str(self.root/'source.kicad_pcb'))
        net=r.p.pcb.NETINFO_ITEM(board,'OTHER');board.Add(net)
        track=r.p.pcb.PCB_TRACK(board);track.SetStart(r.p.vector(10,3));track.SetEnd(r.p.vector(10,7))
        track.SetWidth(250000);track.SetLayer(r.p.pcb.F_Cu);track.SetNetCode(net.GetNetCode());board.Add(track)
        r.p.pcb.SaveBoard(str(self.root/'source.kicad_pcb'),board)
        result=self.produce()['test']
        self.assertFalse(result['route_complete']);self.assertGreater(result['physical_faults'],0)

    def test_stale_zone_fill_rejected(self):
        board=r.p.pcb.LoadBoard(str(self.root/'source.kicad_pcb'))
        zone=r.p.pcb.ZONE(board);zone.SetLayer(r.p.pcb.F_Cu);zone.SetNetCode(board.FindNet('N').GetNetCode())
        zone.SetLocalClearance(200000);zone.SetThermalReliefGap(200000);zone.SetThermalReliefSpokeWidth(250000)
        polygon=zone.Outline();polygon.NewOutline()
        for x,y in [(2,2),(28,2),(28,18),(2,18)]:polygon.Append(x*1000000,y*1000000)
        board.Add(zone);r.p.pcb.SaveBoard(str(self.root/'source.kicad_pcb'),board)
        self.produce();target=self.root/'out/test.kicad_pcb'
        board=r.p.pcb.LoadBoard(str(target))
        self.assertTrue(any(z.IsFilled() for z in board.Zones()))
        for z in board.Zones():z.UnFill()
        r.p.pcb.SaveBoard(str(target),board)
        with self.assertRaisesRegex(ValueError,'stale routing artifact'):self.verify()


class Admission(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='vnext-route-admission-');self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.put('authority.md','Synthetic authority, not Crow acceptance.')
        self.old={'review':'08_reviews/2026-10-05-placement.md','identity':'old'}
        self.put(r.p.RECEIPT,self.old)
        self.contract={'version':1,'authority':'authority.md','authority_sha256':r.p.sha(self.root/'authority.md'),
                       'placement_receipt_sha256':r.p.sha(self.root/r.p.RECEIPT)}
        self.put(r.CONTRACT,self.contract)
        self.put('plan.json',{'boards':{'board':{}}})
        self.put('08_reviews/2026-10-05-placement.md','```json\n'+json.dumps({'plan':'plan.json'})+'\n```')
        self.put('fit.md','Synthetic geometry evidence, not an actual fit approval.')
        self.name='08_reviews/2026-10-06-mating.md'
        subjects=r.base_subjects(self.root,self.contract)
        subjects['fit.md']=r.p.sha(self.root/'fit.md')
        self.review={'schema':1,'stage':'KICAD-MATING-IMPORT','author':'a','reviewer':'b','verdict':'PASS',
                     'applicability':'applicable','scope_evidence':['fit.md'],'geometry_evidence':['fit.md'],
                     'subjects':subjects,'checks':{k:{'verdict':'PASS','evidence':['fit.md'],'rationale':'Fixture only'}
                                                 for k in r.CRITERIA['mating']}}

    def put(self,name,value):
        path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value,dict) else value)

    def certificate(self):
        self.put(self.name,'```json\n'+json.dumps(self.review)+'\n```')
        with patch.object(r.p,'certificate',return_value=self.old):return r.receipt(self.root,self.name,'mating',historical=True)

    def test_new_prose_only_mating_admission_is_rejected(self):
        self.put(self.name,'```json\n'+json.dumps(self.review)+'\n```')
        with patch.object(r.p,'certificate',return_value=self.old):
            with self.assertRaisesRegex(ValueError,'registered 3D contract'):
                r.receipt(self.root,self.name,'mating')

    def test_applicable_and_justified_not_applicable(self):
        self.assertEqual(self.certificate()['role'],'mating_clearance')
        self.review['applicability']='not_applicable';self.review.pop('geometry_evidence')
        self.assertEqual(self.certificate()['role'],'mating_clearance')

    def test_unknown_missing_geometry_collision_and_stale_evidence(self):
        self.review['applicability']='unknown'
        with self.assertRaisesRegex(ValueError,'unknown mating'):self.certificate()
        self.review['applicability']='applicable';self.review['geometry_evidence']=[]
        with self.assertRaisesRegex(ValueError,'geometry evidence'):self.certificate()
        self.review['geometry_evidence']=['fit.md'];self.review['checks']['geometry']['verdict']='FAIL'
        with self.assertRaisesRegex(ValueError,'incomplete review'):self.certificate()
        self.review['checks']['geometry']['verdict']='PASS';self.put('fit.md','Changed geometry')
        with self.assertRaisesRegex(ValueError,'stale review subject'):self.certificate()

    def test_upstream_failure_not_replaced_by_old_receipt_hash(self):
        with patch.object(r.p,'certificate',side_effect=ValueError('placement replay differs')):
            with self.assertRaisesRegex(ValueError,'placement replay'):r.upstream(self.root)

    def test_versioned_placement_selected_without_overwriting_historical(self):
        old_bytes=(self.root/r.p.RECEIPT).read_bytes()
        successor='06_build/checkpoints/revision2/placement_reviewed.json'
        fresh={**self.old,'identity':'successor'};self.put(successor,fresh)
        self.contract.update(version=2,placement_receipt=successor,
                             placement_receipt_sha256=r.p.sha(self.root/successor))
        self.put(r.CONTRACT,self.contract)
        with patch.object(r.p,'certificate',return_value=fresh) as check:
            r.upstream(self.root);check.assert_called_once_with(self.root,fresh['review'])
        subjects=r.base_subjects(self.root,self.contract)
        self.assertIn(successor,subjects);self.assertNotIn(r.p.RECEIPT,subjects)
        self.assertEqual(old_bytes,(self.root/r.p.RECEIPT).read_bytes())
        self.put(successor,{**fresh,'identity':'tampered'})
        with self.assertRaisesRegex(ValueError,'re-adoption'):r.upstream(self.root)

    def test_versioned_hash_cannot_replace_owning_check(self):
        successor='06_build/checkpoints/revision2/placement_reviewed.json';self.put(successor,self.old)
        self.contract.update(version=2,placement_receipt=successor,
                             placement_receipt_sha256=r.p.sha(self.root/successor))
        self.put(r.CONTRACT,self.contract)
        with patch.object(r.p,'certificate',side_effect=ValueError('placement replay differs')):
            with self.assertRaisesRegex(ValueError,'placement replay'):r.upstream(self.root)

    def test_version_downgrade_and_missing_selection_rejected(self):
        with self.assertRaisesRegex(ValueError,'version1 cannot'):
            r.placement_receipt_path(dict(version=1,placement_receipt='new.json'))
        with self.assertRaisesRegex(ValueError,'explicit placement receipt'):
            r.placement_receipt_path(dict(version=2))

    def test_placement_backtrack_requires_readoption_and_new_review(self):
        previous=self.certificate()
        # Simulate the owning placement verifier issuing a replacement receipt.
        # This test does NOT claim to simulate autonomous engineering decisions.
        self.old={'review':'08_reviews/2026-10-05-placement.md','identity':'new'}
        self.put(r.p.RECEIPT,self.old)
        with self.assertRaisesRegex(ValueError,'re-adoption'):self.certificate()
        self.contract['placement_receipt_sha256']=r.p.sha(self.root/r.p.RECEIPT)
        self.put(r.CONTRACT,self.contract)
        with self.assertRaisesRegex(ValueError,'missing required review subjects'):self.certificate()
        self.review['subjects'].update(r.base_subjects(self.root,self.contract))
        self.assertNotEqual(previous,self.certificate())


if __name__=='__main__':unittest.main()
