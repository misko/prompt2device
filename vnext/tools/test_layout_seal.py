"""Native finishing regressions; mocked admission is not Crow acceptance."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import layout_seal as s
import test_routing as fixture
import workflow


class Native(unittest.TestCase):
    write = fixture.Native.write

    def setUp(self):
        fixture.Native.setUp(self)
        self.data['boards']['test']['resources'] = {}
        self.data['closure'] = {'stack': {'status': 'open', 'rationale': 'fixture', 'evidence': []}}
        self.contract = {'obligations': [{'id': 'stack'}]}

    def mutate(self, action):
        board = s.p.pcb.LoadBoard(str(self.root/'source.kicad_pcb'))
        action(board)
        s.p.pcb.SaveBoard(str(self.root/'candidate.kicad_pcb'), board)
        return s.classify(self.root/'source.kicad_pcb', self.root/'candidate.kicad_pcb')

    def test_reference_presentation_allowed_but_content_preserved(self):
        self.assertEqual(self.mutate(lambda b: b.FindFootprintByReference('U1').Reference().SetPosition(s.p.vector(9,9))), 'document_only')
        self.assertEqual(self.mutate(lambda b: b.FindFootprintByReference('U1').SetReference('U9')), 'engineering_change')

    def test_copper_pad_placement_and_net_changes_rejected(self):
        actions = [lambda b: next(iter(b.GetTracks())).SetWidth(300000),
                   lambda b: next(iter(b.FindFootprintByReference('U1').Pads())).SetSize(s.p.vector(2,2)),
                   lambda b: b.FindFootprintByReference('U1').SetPosition(s.p.vector(6,5))]
        for action in actions:
            with self.subTest(action=action): self.assertEqual(self.mutate(action), 'engineering_change')
        # SaveBoard may repair an attempted SetNetCode(0); mutate authored net
        # tokens directly to exercise admission, not a serializer no-op.
        original=(self.root/'source.kicad_pcb').read_text()
        changed=original.replace('"N"','"OTHER"')
        self.assertNotEqual(original,changed)
        self.write('candidate.kicad_pcb',changed)
        self.assertEqual(s.classify(self.root/'source.kicad_pcb',self.root/'candidate.kicad_pcb'),'engineering_change')

    def test_unknown_physical_tokens_remain(self):
        for token in ['pad', 'zone', 'setup', 'model', 'property']:
            node = s.parse(f'({token} "arbitrary" (layer "F.Cu") (at 1 2))')
            self.assertEqual(s.physical(node), node)
        courtyard = s.parse('(fp_line (start 1 2) (layer "F.CrtYd"))')
        self.assertEqual(s.physical(courtyard), courtyard)

    def test_local_library_coverage_required(self):
        source=self.root/'source.kicad_pcb'
        with self.assertRaisesRegex(ValueError,'unbound footprint'):s.resources(self.root,{},source)
        self.write('fp-lib-table','(fp_lib_table (lib (name "Test") (type "KiCad") (uri "${KIPRJMOD}/Test.pretty") (options "")))')
        mapping={'fp-lib-table':'fp-lib-table','Test.pretty/Pad.kicad_mod':'lib/Pad.kicad_mod'}
        s.resources(self.root,mapping,source)
        self.write('fp-lib-table','(fp_lib_table (lib (name "Test") (type "KiCad") (uri "/tmp/Test.pretty")))')
        with self.assertRaisesRegex(ValueError,'project-local'):s.resources(self.root,mapping,source)

    def test_real_build_replay_and_tamper(self):
        checks = s.produce(self.root, self.data, self.root/'out')
        self.assertTrue(checks['test']['route_complete'])
        with patch.object(s, 'inputs', return_value=(self.contract,self.data,{})):
            result = s.verify(self.root, 'manifest.json', 'out')
            self.assertFalse(result['engineering_closed'])
            self.write('out/unbound.txt','unexpected output')
            with self.assertRaisesRegex(ValueError,'inventory differs'):
                s.verify(self.root,'manifest.json','out')
            (self.root/'out/unbound.txt').unlink()
            self.write('out/checks.json', '{}')
            with self.assertRaisesRegex(ValueError, 'stale layout artifact'):
                s.verify(self.root, 'manifest.json', 'out')

    def test_library_rejects_board_only_anchor_not_nested_pad_position(self):
        mapping = {'Test.pretty/Pad.kicad_mod': 'lib/Pad.kicad_mod'}
        original = (self.root/'lib/Pad.kicad_mod').read_text()
        s.resources(self.root, mapping)
        self.assertTrue(any(isinstance(v, list) and v[:1] == ['pad']
                            for v in s.parse(original)))
        for anchor in ['(at 0 0)', '(at 165 27.55)', '(at 165 27.55 90)']:
            with self.subTest(anchor=anchor):
                self.write('lib/Pad.kicad_mod', original[:original.rfind(')')]+anchor+')')
                with self.assertRaisesRegex(ValueError, 'board-only footprint position'):
                    s.resources(self.root, mapping)
        self.write('lib/Pad.kicad_mod', original)
        s.resources(self.root, mapping)


class Gates(unittest.TestCase):
    def test_no_cosmetic_waivers_or_ignored_checks(self):
        report = dict(coordinate_units='mm', ignored_checks=[], violations=[], unconnected_items=[], schematic_parity=[])
        self.assertTrue(s.strict_summary(report)['layout_clean'])
        report['violations'] = [{'type': 'text_height', 'severity': 'warning'}]
        self.assertFalse(s.strict_summary(report)['layout_clean'])
        report['ignored_checks'] = [{'key': 'text_height'}]
        with self.assertRaises(ValueError): s.strict_summary(report)

    def test_missing_and_unproven_obligations(self):
        c = {'obligations': [{'id': 'stack'}]}
        with self.assertRaisesRegex(ValueError, 'coverage'): s.closure_status(c, {})
        data = {'closure': {'stack': {'status': 'closed', 'rationale': 'claim', 'evidence': []}}}
        with self.assertRaisesRegex(ValueError, 'evidence'): s.closure_status(c, data)
        data['closure']['stack']['status'] = 'open'
        self.assertFalse(s.closure_status(c, data))
        data['closure']['stack']['rationale'] = '   '
        with self.assertRaisesRegex(ValueError,'invalid obligation'):s.closure_status(c,data)

    def test_independent_review_exact_subjects(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'evidence').write_text('fixture only')
            digest=s.p.sha(root/'evidence')
            criterion={'verdict':'PASS','rationale':'Synthetic test, not real engineering','evidence':['evidence']}
            review={'schema':1,'stage':'KICAD-LAYOUT-SEAL','verdict':'PASS','author':'a','reviewer':'b',
                    'subjects':{'evidence':digest},'checks':{k:dict(criterion) for k in s.CRITERIA},
                    'obligations':{'stack':dict(criterion)}}
            s.validate_review(root,review,{'evidence':digest},['stack'])
            review['checks']['engineering']['rationale']='  '
            with self.assertRaisesRegex(ValueError,'incomplete independent'):s.validate_review(root,review,{},['stack'])
            review['checks']['engineering']['rationale']='fixture'
            review['reviewer']='A'
            with self.assertRaisesRegex(ValueError,'independent reviewer'):s.validate_review(root,review,{},['stack'])
            review['reviewer']='b';(root/'evidence').write_text('changed')
            with self.assertRaisesRegex(ValueError,'stale review'):s.validate_review(root,review,{},['stack'])

    def test_clean_drc_does_not_seal_open_engineering(self):
        with patch.object(s.r, 'review_json', return_value={'manifest': 'm', 'output': 'o'}), \
             patch.object(s, 'verify', return_value={'boards': {'a': {'layout_clean': True}}, 'engineering_closed': False}):
            with self.assertRaisesRegex(ValueError, 'obligations remain open'):
                s.certificate(Path('/unused'), 'review')

    def test_resource_escape_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root/'source').write_text('x')
            with self.assertRaises(ValueError): s.resources(root, {'../escape.kicad_mod': 'source'})

    def test_upstream_is_actually_checked(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name in ['authority',s.r.RECEIPT]:
                path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('{}')
            c={'version':1,'authority':'authority','authority_sha256':s.p.sha(root/'authority'),
               'routing_receipt_sha256':s.p.sha(root/s.r.RECEIPT)}
            path=root/s.CONTRACT;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(c))
            with patch.object(s.r,'check',side_effect=ValueError('upstream stale')):
                with self.assertRaisesRegex(ValueError,'upstream stale'):s.upstream(root)


class Visibility(unittest.TestCase):
    def test_current_does_not_mean_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'01_docs').mkdir()
            (root/workflow.STATUS).write_text(workflow.STATUS_MARKER+'\nstage: layout_seal\nstate: hold\n')
            view=workflow.render(root)
            self.assertIn('KICAD-LAYOUT-SEAL — CURRENT (reported)',view)
            self.assertIn('no receipt',view)
            self.assertNotIn('owning check PASS',view)
            receipt=root/'06_build/checkpoints/routed_board.json';receipt.parent.mkdir(parents=True);receipt.write_text('{}')
            self.assertIn('receipt present; NOT verified',workflow.render(root))
            def fail(*args):raise ValueError('stale fixture')
            self.assertIn('owning check FAILED: stale fixture',workflow.render(root,verify_acceptance=True,checker=fail))
            self.assertIn('owning check PASS',workflow.render(root,verify_acceptance=True,checker=lambda *args:None))


if __name__=='__main__':unittest.main()
