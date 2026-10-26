"""Mechanical repair must not create an electrical/placement escape hatch."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import json
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

import placement as p
import test_placement as fixtures


class Revision(unittest.TestCase):
    def setUp(self):
        self.board=p.pcb.BOARD();self.fp=p.pcb.FOOTPRINT(self.board)
        self.pad=p.pcb.PAD(self.fp);self.pad.SetAttribute(p.pcb.PAD_ATTRIB_NPTH)
        self.pad.SetShape(p.pcb.PAD_SHAPE_CIRCLE);self.pad.SetPosition(p.vector(1,2))
        self.pad.SetSize(p.vector(2,2));self.pad.SetDrillSize(p.vector(2,2))
        self.fp.Add(self.pad);self.board.Add(self.fp)
        self.row=dict(at=[1,2],before_mm=2,after_mm=2.4,
                      before_clearance_mm=None,after_clearance_mm=.4)

    def run_recipe(self):p.revise_npth(self.fp,[self.row])

    def test_exact_hole_change_and_inverse_whole_native(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(tmp)/'before.kicad_pcb';b=Path(tmp)/'after.kicad_pcb'
            p.pcb.SaveBoard(str(a),self.board);self.run_recipe()
            self.assertEqual(self.pad.GetSize(),p.vector(2.4,2.4))
            self.assertEqual(self.pad.GetDrillSize(),p.vector(2.4,2.4))
            self.assertEqual(self.pad.GetLocalClearance(),400000)
            self.pad.SetSize(p.vector(2,2));self.pad.SetDrillSize(p.vector(2,2))
            self.pad.SetLocalClearance(None);p.pcb.SaveBoard(str(b),self.board)
            self.assertEqual(a.read_text(),b.read_text())

    def test_numbered_npth_rejected(self):
        self.pad.SetNumber('1')
        with self.assertRaisesRegex(ValueError,'unnumbered'):self.run_recipe()

    def test_plated_hole_rejected(self):
        self.pad.SetAttribute(p.pcb.PAD_ATTRIB_PTH)
        with self.assertRaisesRegex(ValueError,'unnumbered'):self.run_recipe()

    def test_net_assigned_npth_rejected(self):
        net=p.pcb.NETINFO_ITEM(self.board,'/POWER');self.board.Add(net);self.pad.SetNet(net)
        with self.assertRaisesRegex(ValueError,'unnumbered'):self.run_recipe()

    def test_slot_rejected(self):
        self.pad.SetDrillShape(p.pcb.PAD_DRILL_SHAPE_OBLONG)
        with self.assertRaisesRegex(ValueError,'round NPTH'):self.run_recipe()

    def test_wrong_baseline_rejected(self):
        self.row['before_mm']=1.8
        with self.assertRaisesRegex(ValueError,'baseline'):self.run_recipe()

    def test_unset_not_explicit_zero(self):
        self.row['before_clearance_mm']=0
        with self.assertRaisesRegex(ValueError,'baseline'):self.run_recipe()

    def test_move_is_not_allowed(self):
        self.row['after_at']=[3,4]
        with self.assertRaisesRegex(ValueError,'unsupported'):self.run_recipe()

    def test_missing_hole_is_not_added(self):
        self.row['at']=[3,4]
        with self.assertRaisesRegex(ValueError,'missing'):self.run_recipe()

    def test_duplicate_edit_rejected(self):
        with self.assertRaisesRegex(ValueError,'duplicate'):
            p.revise_npth(self.fp,[self.row,copy.deepcopy(self.row)])

    def test_ambiguous_location_rejected(self):
        extra=p.pcb.PAD(self.fp);extra.SetPosition(p.vector(1,2));self.fp.Add(extra)
        with self.assertRaisesRegex(ValueError,'ambiguous'):self.run_recipe()

    def test_nonfinite_and_negative_rejected(self):
        for key,value in [('after_mm',float('nan')),('after_mm',-1),('after_clearance_mm',-.1)]:
            with self.subTest(key=key,value=value):
                old=self.row[key];self.row[key]=value
                with self.assertRaises(ValueError):self.run_recipe()
                self.row[key]=old

    def test_subresolution_hole_or_location_rejected(self):
        for key,value in [('after_mm',1e-9),('after_mm',2.000000001),('at',[1.000000001,2])]:
            with self.subTest(key=key,value=value):
                old=self.row[key];self.row[key]=value
                with self.assertRaisesRegex(ValueError,'resolution'):self.run_recipe()
                self.row[key]=old

    def test_native_noop_rejected(self):
        self.pad.SetLocalClearance(0)
        self.row.update(before_clearance_mm=0,after_clearance_mm=0,after_mm=2)
        with self.assertRaisesRegex(ValueError,'empty mechanical hole edit'):self.run_recipe()


class Integration(unittest.TestCase):
    def setUp(self):
        fixtures.NativeReplay.setUp(self)
        source=self.root/'lib/Fixture.kicad_mod'
        text=source.read_text();head,tail=text.rsplit(')',1)
        source.write_text(head+'(pad "" np_thru_hole circle (at 0 .5) (size .2 .2) '
                          '(drill .2) (layers "*.Cu" "*.Mask")))'+tail)
        accepted=p.read(self.root/'schematic.json')
        accepted['subjects']['lib/Fixture.kicad_mod']=p.sha(source)
        self.put('schematic.json',json.dumps(accepted))
        self.put('mechanical-facts.md','Synthetic geometry evidence, not engineering approval.')
        self.data=p.read(self.root/'inputs.json')
        self.data['boards']['board']['npth_revisions']={'U1':dict(reason='Synthetic relief',
            evidence=['mechanical-facts.md'],holes=[dict(at=[0,.5],before_mm=.2,after_mm=.3,
                before_clearance_mm=None,after_clearance_mm=.1)])}
        self.put('revised.json',json.dumps(self.data))

    def test_full_source_rebuild_binds_evidence_and_preserves_other_instances(self):
        p.build(self.root,'revised.json','plan.json','revised-out')
        with patch.object(p,'upstream',return_value={}):
            verified=p.verify(self.root,'revised.json','plan.json','revised-out')
        self.assertEqual(verified['checks']['board']['verdict'],'PASS')
        self.assertEqual(verified['subjects']['mechanical-facts.md'],p.sha(self.root/'mechanical-facts.md'))
        b=p.pcb.LoadBoard(str(self.root/'revised-out/board.kicad_pcb'))
        sizes={f.GetReference():[a.GetSize().x for a in f.Pads() if not a.GetNumber()]
               for f in b.GetFootprints()}
        self.assertEqual(sizes['U1'],[300000]);self.assertEqual(sizes['C1'],[200000])

    def test_changed_recipe_rejects_existing_native(self):
        p.build(self.root,'revised.json','plan.json','revised-out')
        self.data['boards']['board']['npth_revisions']['U1']['holes'][0]['after_mm']=.4
        self.put('revised.json',json.dumps(self.data))
        with patch.object(p,'upstream',return_value={}):
            with self.assertRaisesRegex(ValueError,'native placement replay differs'):
                p.verify(self.root,'revised.json','plan.json','revised-out')

    def test_unknown_owner_rejected(self):
        edits=self.data['boards']['board']['npth_revisions'];edits['MISSING']=edits.pop('U1')
        self.put('revised.json',json.dumps(self.data))
        with self.assertRaisesRegex(ValueError,'unknown mechanical revision owner'):p.inputs(self.root,'revised.json')

    def test_missing_evidence_rejected(self):
        self.data['boards']['board']['npth_revisions']['U1']['evidence']=[]
        self.put('revised.json',json.dumps(self.data))
        with self.assertRaisesRegex(ValueError,'lacks evidence'):p.inputs(self.root,'revised.json')

    def test_receipt_rejects_stale_engineering_evidence(self):
        p.build(self.root,'revised.json','plan.json','revised-out')
        with patch.object(p,'upstream',return_value={}):
            verified=p.verify(self.root,'revised.json','plan.json','revised-out')
            review=dict(schema=1,stage='KICAD-PLACEMENT',verdict='PASS',author='fixture author',
                        reviewer='fixture reviewer',inputs='revised.json',plan='plan.json',output='revised-out',
                        subjects=verified['subjects'],checks={k:dict(verdict='PASS',
                        rationale='Synthetic test only',evidence=['mechanical-facts.md']) for k in p.CRITERIA})
            name='08_reviews/2026-10-09-fixture-placement.md'
            self.put(name,'```json\n'+json.dumps(review)+'\n```\n')
            # This test isolates mechanical-evidence binding; native critical
            # route admission is exercised by test_critical_routes.
            with patch('critical_routes.verify',return_value={}):
                receipt=p.certificate(self.root,name)
            self.assertEqual(receipt['role'],'placement_reviewed')
            self.put('mechanical-facts.md','Changed after independent review')
            with self.assertRaisesRegex(ValueError,'stale review subject'):p.certificate(self.root,name)


class ReceiptPaths(unittest.TestCase):
    def test_versioned_issue_check_refuses_overwrite_and_preserves_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);default=root/p.RECEIPT;default.parent.mkdir(parents=True)
            default.write_text('historical fixture bytes')
            certificate=dict(role='placement_reviewed',review='fixture.md',identity='fixture only')
            def invoke(action):
                argv=['placement.py',action,'--project',str(root),'--receipt','version2/placement.json']
                if action=='issue':argv+=['--review','fixture.md']
                with patch.object(sys,'argv',argv),patch.object(p,'certificate',return_value=certificate), \
                        redirect_stdout(io.StringIO()),redirect_stderr(io.StringIO()):
                    return p.main()
            self.assertEqual(invoke('issue'),0)
            self.assertEqual(invoke('check'),0)
            stored=(root/'version2/placement.json').read_bytes()
            self.assertEqual(invoke('issue'),1)
            self.assertEqual((root/'version2/placement.json').read_bytes(),stored)
            self.assertEqual(default.read_text(),'historical fixture bytes')
            certificate['identity']='changed owning result'
            self.assertEqual(invoke('check'),1)


if __name__=='__main__':unittest.main()
