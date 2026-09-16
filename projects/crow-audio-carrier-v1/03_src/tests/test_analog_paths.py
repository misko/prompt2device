"""Independent native source endpoints plus hostile saved-text model fixtures.

These tests do not turn a conditional model into physical DCR qualification.
No live/generated board is written or loaded.
"""
import copy
import contextlib
import io
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

import yaml

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parents[1]
sys.path.insert(0, str(PROJECT/'03_src'))
import check_analog_paths as checker
from test_route_source_contract import load_source
from copper_length_audit import load_groups, grade_declared_paths

BASE = '6b31017090831965530a32c24618cbaecbffa0b8'


def fixture_tracks(length_mm=10., layer='F.Cu', width=.2):
    # This fixture derives the 48 physical net identities from the native
    # circuit, independently of the checker that generates expected paths.
    _, _, _, _, _, pins = load_source()
    names = sorted({n for n in pins.values() if re.fullmatch(r'OPA_[PN][1-8]|FILTER[1-8][PN]|ADC[1-8][PN]', n)})
    assert len(names) == 48
    return '\n' + '\n'.join(f'\t(segment (start 0 0) (end {length_mm} 0) (width {width}) (layer "{layer}") (net "{n}"))' for n in names)


class AnalogPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, cls.nets, cls.stack, cls.comps, cls.pins = load_source()
        cls.groups, _ = load_groups(PROJECT)

    def test_real_shared_loader_and_native_all_leaf_coverage(self):
        result = checker.validate_source(self.groups, self.route, self.pins)
        self.assertEqual((result['groups'], result['nets'], result['endpoints'], result['paths']), (24, 48, 192, 144))
        self.assertEqual(len(self.groups), 26)
        self.assertEqual(result['physical_dcr_status'], 'UNVERIFIED')

    def test_file_report_keeps_full_evidence_and_stdout_compact(self):
        report = {
            'status': 'PASS', 'board_sha256': 'a' * 64,
            'length': {'n_electrical_measured': 155,
                       'n_electrical_declared': 155},
            'large_evidence': list(range(10000)),
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'receipt.json'
            console = io.StringIO()
            with contextlib.redirect_stdout(console):
                checker.emit_report(report, output)
            self.assertEqual(json.loads(output.read_text()), report)
            emitted = console.getvalue()
            self.assertLess(len(emitted), 512)
            self.assertIn('ANALOG-PATHS PASS', emitted)
            self.assertIn('paths=155/155', emitted)
            self.assertNotIn('large_evidence', emitted)

    def test_old_unmatched_source_and_missing_branch_are_rejected(self):
        old = yaml.safe_load(subprocess.check_output(['git','show',BASE+':projects/crow-audio-carrier-v1/03_src/rules/nets.yaml'], cwd=REPO, timeout=15))
        with self.assertRaisesRegex(checker.PathError, 'census'):
            checker.validate_source(old['length_match'], self.route, self.pins)
        bad = copy.deepcopy(self.groups)
        bad['ANALOG_CH1_ADC']['paths']['P'].pop()
        with self.assertRaisesRegex(checker.PathError, 'endpoint paths'):
            checker.validate_source(bad, self.route, self.pins)

    def test_crossed_native_pin_and_ghost_leaf_are_rejected(self):
        for kind in ['cross', 'extra']:
            pins = copy.deepcopy(self.pins)
            if kind == 'cross':
                pins[('U_ADC','40')] = 'ADC1N'
            else:
                pins[('TP_EXTRA','1')] = 'ADC1P'
            with self.assertRaisesRegex(checker.PathError, 'census/identity'):
                checker.validate_source(self.groups, self.route, pins)

    def test_matching_recipe_is_exact_stitch_authority_and_cannot_be_omitted(self):
        recipe = self.route['stitch']['endpoint_length_matching']
        self.assertEqual(recipe, {
            'mechanism': 'canonicalize_chains',
            'groups': sorted(f'ANALOG_CH{n}_{stage}' for n in range(1,9)
                             for stage in ('OUTPUT','FILTER','ADC')),
            'verification': 'copper_length_audit',
        })
        for key in ('mechanism', 'groups', 'verification'):
            bad = copy.deepcopy(self.route)
            bad['stitch']['endpoint_length_matching'].pop(key)
            with self.assertRaisesRegex(checker.PathError, 'recipe'):
                checker.validate_source(self.groups, bad, self.pins)
        bad = copy.deepcopy(self.route)
        passes = bad['stitch']['passes']
        a, b = passes.index('canonicalize_chains'), passes.index('prune_declared_path_offcuts')
        passes[a], passes[b] = passes[b], passes[a]
        with self.assertRaisesRegex(checker.PathError, 'recipe'):
            checker.validate_source(self.groups, bad, self.pins)

    def test_unrelated_digital_matching_and_analog_recipe_preserved(self):
        # Preserve the contracts actually owned by this suite. A reverse
        # whole-tree migration through the removed TPS/buffer architecture is
        # not authority for the current layout or power rails.
        def before(name):
            return yaml.safe_load(subprocess.check_output(
                ['git','show','1b725986:projects/crow-audio-carrier-v1/03_src/'+name],
                cwd=REPO, timeout=15))
        old_nets=before('rules/nets.yaml')
        for name in ('MCH_INPUT_SECTIONS','BUFFERED_DIGITAL_SECTIONS'):
            current = self.nets['length_match'][name]
            previous = old_nets['length_match'][name]
            for key in ('topology','max_spread_mm','members','paths'):
                self.assertEqual(current[key], previous[key])
        old_route=before('route.yaml')
        current_clock=next(w for w in self.route['route']['waves'] if w['name']=='clocks')
        old_clock=next(w for w in old_route['route']['waves'] if w['name']=='clocks')
        self.assertEqual(current_clock['clearance'],old_clock['clearance'])
        self.assertEqual(current_clock['layers'],['F.Cu'])
        for name in ('MCH_INPUT_SECTIONS','BUFFERED_DIGITAL_SECTIONS'):
            self.assertTrue(self.nets['length_match'][name]['no_vias'])
        self.assertEqual(dict(zip(current_clock['power_nets'],current_clock['power_nets_widths'])),
                         dict.fromkeys(self.nets['classes']['ADC_CLOCK']['nets'],.36))
        self.assertEqual(set(self.route['stitch']['endpoint_length_matching']['groups']),
                         {name for name in self.groups if name.startswith('ANALOG_CH')})
        self.assertEqual(self.nets['reference_plane_checks']['ADC_DIGITAL_RETURN'],
                         old_nets['reference_plane_checks']['ADC_DIGITAL_RETURN'])
        self.assertEqual(set(self.nets['reference_plane_checks']),{'ADC_DIGITAL_RETURN'})

    def test_each_grounded_filter_shunt_is_a_required_leaf(self):
        for n in range(1,9):
            for leg in ('P','N'):
                for index in (1,2):
                    bad=copy.deepcopy(self.groups)
                    paths=bad[f'ANALOG_CH{n}_FILTER']['paths'][leg]
                    paths[:]=[p for p in paths if p['id']!=f'shunt{index}']
                    with self.subTest(channel=n,leg=leg,index=index),self.assertRaisesRegex(checker.PathError,'endpoint paths'):
                        checker.validate_source(bad,self.route,self.pins)

    def test_conditional_inventory_charges_all_three_nets_and_keeps_unknowns(self):
        result = checker.inventory_model(fixture_tracks(), {'F.Cu':.035,'B.Cu':.035}, 1.6)
        self.assertEqual(result['model_status'], 'PASS')
        self.assertEqual((len(result['nets']),len(result['legs'])), (48,16))
        self.assertAlmostEqual(result['legs'][0]['inventory_model_ohm'], 2.1643958e-8*.030/(.0002*.000035))
        self.assertEqual(result['reserve_factor'], 2)
        self.assertEqual(result['physical_dcr_status'], 'UNVERIFIED')
        self.assertIn('10 ohm series resistors', result['excluded'])
        self.assertIn('pad spreading', result['excluded'])

    def test_long_trace_and_extra_branch_inventory_fail_screen(self):
        bad = fixture_tracks() + '\n\t(segment (start 10 0) (end 1010 0) (width 0.2) (layer "F.Cu") (net "ADC1P"))'
        result = checker.inventory_model(bad, {'F.Cu':.035,'B.Cu':.035}, 1.6)
        self.assertEqual(result['model_status'],'FAIL')
        self.assertEqual(sum(not r['within_design_screen'] for r in result['legs']), 1)

    def test_adc_escape_floor_is_priced_without_relaxing_other_analog_copper(self):
        base = fixture_tracks()
        adc = base.replace(
            '(width 0.2) (layer "F.Cu") (net "ADC1P")',
            '(width 0.15) (layer "F.Cu") (net "ADC1P")')
        result = checker.inventory_model(
            adc, {'F.Cu': .035, 'B.Cu': .035}, 1.6)
        self.assertGreater(result['nets']['ADC1P']['track_ohm'],
                           result['nets']['FILTER1P']['track_ohm'])
        for bad in (
            adc.replace('(width 0.15)', '(width 0.149)', 1),
            base.replace(
                '(width 0.2) (layer "F.Cu") (net "FILTER1P")',
                '(width 0.15) (layer "F.Cu") (net "FILTER1P")'),
        ):
            with self.assertRaises(checker.PathError):
                checker.inventory_model(
                    bad, {'F.Cu': .035, 'B.Cu': .035}, 1.6)

    def test_missing_nets_underwidth_inner_layer_and_nonfinite_fail(self):
        fixtures = [fixture_tracks().replace('(net "ADC1P")','(net "ABSENT")'),
                    fixture_tracks(width=.18), fixture_tracks(layer='In1.Cu'),
                    fixture_tracks().replace('(end 10.0 0)', '(end 1e999 0)')]
        for bad in fixtures:
            with self.assertRaises(checker.PathError):
                checker.inventory_model(bad, {'F.Cu':.035,'B.Cu':.035}, 1.6)

    def test_arc_via_and_layer_thickness_are_actually_priced(self):
        base = fixture_tracks()
        changed = base + '\n\t(arc (start 10 0) (mid 11 1) (end 12 0) (width 0.2) (layer "B.Cu") (net "ADC1P"))'
        changed += '\n\t(via (at 12 0) (size 0.5) (drill 0.2) (layers "F.Cu" "B.Cu") (net "ADC1P"))'
        result = checker.inventory_model(changed, {'F.Cu':.035,'B.Cu':.0175}, 1.6)['nets']['ADC1P']
        self.assertAlmostEqual(result['track_mm'],10+math.pi)
        self.assertAlmostEqual(result['track_ohm'],2.1643958e-8*1000*(10/(.2*.035)+math.pi/(.2*.0175)))
        self.assertAlmostEqual(result['via_ohm'],2.1643958e-8*1.6*1000/(math.pi*.2*.018))
        for bad in [changed.replace('(drill 0.2)','(drill 0.15)'), base+'\n\t(zone (net "ADC1P"))']:
            with self.assertRaises(checker.PathError):
                checker.inventory_model(bad, {'F.Cu':.035,'B.Cu':.035}, 1.6)

    def test_compact_analog_via_requires_exact_source_identity_and_geometry(self):
        base = fixture_tracks()
        via = '\n\t(via (at 98.575 66.5) (size 0.3) (drill 0.2) (layers "F.Cu" "B.Cu") (net "ADC4P"))'
        result = checker.inventory_model(base+via, {'F.Cu':.035,'B.Cu':.035}, 1.6,
                                         self.route)
        self.assertEqual(result['nets']['ADC4P']['vias'], 1)
        for bad in (via.replace('98.575', '98.574'), via.replace('(size 0.3)', '(size 0.31)'),
                    via.replace('(drill 0.2)', '(drill 0.19)')):
            with self.assertRaisesRegex(checker.PathError, 'exact source seed geometry'):
                checker.inventory_model(base+bad, {'F.Cu':.035,'B.Cu':.035}, 1.6,
                                        self.route)

    def test_relocated_fine_via_requires_enabled_exact_source_recipe(self):
        route = copy.deepcopy(self.route)
        old = dict(at=[98.575,66.5],size=.3,drill=.2,layers=['F.Cu','B.Cu'])
        new = dict(at=[98.6,66.6],size=.3,drill=.2,layers=['F.Cu','B.Cu'])
        recipe = dict(edits=[{'net':'ADC4P','reason':'source relocation','from':old,'to':new}])
        route['stitch']['relocate_exact_vias'] = recipe
        # Isolate this fixture from the now-adopted live relocation pass.
        route['stitch']['passes'] = [p for p in route['stitch']['passes']
                                      if p != 'relocate_exact_vias']
        route['stitch']['passes'].insert(0,'relocate_exact_vias')
        actual = checker._source_via_geometries(route)
        self.assertEqual(actual['ADC4P',98600,66600],dict(size=.3,drill=.2))
        self.assertNotIn(('ADC4P',98575,66500),actual)
        route['stitch']['passes'].remove('relocate_exact_vias')
        actual = checker._source_via_geometries(route)
        self.assertNotIn(('ADC4P',98600,66600),actual)
        self.assertIn(('ADC4P',98575,66500),actual)
        route['stitch']['passes'].insert(0,'relocate_exact_vias')
        for mutation in ('mismatch','duplicate','layer','nan','unbound_fine'):
            bad = copy.deepcopy(route)
            rows = bad['stitch']['relocate_exact_vias']['edits']
            if mutation=='mismatch': rows[0]['from']['size']=.31
            if mutation=='duplicate': rows.append(copy.deepcopy(rows[0]))
            if mutation=='layer': rows[0]['to']['layers']=['F.Cu','In1.Cu']
            if mutation=='nan': rows[0]['to']['at'][0]=float('nan')
            if mutation=='unbound_fine': rows[0]['from']['at']=[95,95]
            with self.assertRaises(checker.PathError):
                checker._source_via_geometries(bad)

    def test_late_geometry_restore_can_only_return_to_exact_source_seed(self):
        route = copy.deepcopy(self.route)
        actual = checker._source_via_geometries(route)
        self.assertEqual(actual['ADC3P',99800,65300],dict(size=.3,drill=.2))
        for mutation in ('target','size','old_seed','disabled'):
            bad = copy.deepcopy(route)
            row = bad['stitch']['restore_exact_geometry']['transactions'][0]
            if mutation == 'target': row['via']['to']['at'] = [99.81,65.3]
            if mutation == 'size': row['via']['to']['size'] = .31
            if mutation == 'old_seed': row['via']['from']['at'] = [99.8,65.3]
            if mutation == 'disabled': bad['stitch']['passes'].remove('restore_exact_geometry')
            if mutation == 'disabled':
                self.assertEqual(checker._source_via_geometries(bad)['ADC3P',99800,65300],
                                 dict(size=.3,drill=.2))
            else:
                with self.assertRaises(checker.PathError):
                    checker._source_via_geometries(bad)

    def test_shared_endpoint_gate_rejects_real_path_skew_and_orphan(self):
        decl = self.groups['ANALOG_CH1_OUTPUT']
        def measure(n_main=10., orphan=False):
            nets, pads = {}, {}
            for leg, y, main in [('P',0.,10.),('N',4.,n_main)]:
                paths = decl['paths'][leg]
                net = paths[0]['segments'][0]['net']
                start = paths[0]['segments'][0]['from']
                ends = [p['segments'][0]['to'] for p in paths]
                pts = [(start,0.,y),(ends[0],main,y),(ends[1],0.,y+1.)]
                pads[net] = [dict(ref=p.rsplit('.',1)[0],pad=p.rsplit('.',1)[1],shape='rect',kind='smd',x=x,y=py,angle=0.,sx=.2,sy=.2,layers=['F.Cu']) for p,x,py in pts]
                segs=[('F.Cu',(0.,y),(main,y),main),('F.Cu',(0.,y),(0.,y+1.),1.)]
                if orphan and leg=='P':segs.append(('F.Cu',(50.,50.),(51.,50.),1.))
                nets[net]=dict(segs=segs,vias=[],zones=0)
            row=dict(verdict='PASS');res=dict(unreached=[],fails=[],n_electrical_measured=0)
            grade_declared_paths('fixture',decl,row,nets,['F.Cu','In1.Cu','In2.Cu','B.Cu'],pads,{},res)
            return row,res
        row,result=measure();self.assertFalse(result['fails']);self.assertFalse(result['unreached'])
        self.assertEqual(result['n_electrical_measured'],4)
        self.assertTrue(any('R-LEN-SPREAD' in r for r in measure(12.)[1]['fails']))
        self.assertTrue(any('R-LEN-OFFPATH' in r for r in measure(orphan=True)[1]['fails']))

    def test_both_conductors_enforce_source_and_saved_copper(self):
        for name in ['rebuild_all.sh','rebuild_reuse.sh']:
            script=(PROJECT/'03_src'/name).read_text()
            self.assertIn('03_src/check_analog_paths.py --source-only',script)
            self.assertIn('03_src/check_analog_paths.py --board',script)
            self.assertLess(script.index('run_stage analog_copper'),script.index('run_stage route_acceptance'))
            self.assertNotIn('check_analog_paths.py || true',script)


if __name__ == '__main__':unittest.main()
