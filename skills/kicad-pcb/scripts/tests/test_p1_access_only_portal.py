"""Opt-in access-only portal: exact Crow ADC7 packet and fail-closed mutations."""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_corridor_capacity as checker  # noqa: E402
from test_p1_linked_path import LinkedPathTest  # noqa: E402


ROOT = Path(__file__).resolve().parents[4]
CROW = ROOT / 'projects/crow-usb-carrier-v1'
BOARD = CROW / '01_docs/research/2026-09-25-ti-adc7-local-osc-probe-sol/candidate.kicad_pcb'
BOARD_SHA = 'c9b758d69867b274f0592bd2eceb9a26d64a80dd2daafa8ab9516d23d5925502'
SOURCE = CROW / '01_docs/research/2026-09-25-ti-usb-linked-two-physical-sol/p1_requirements.yaml'


class AccessOnlyPortalTest(unittest.TestCase):
    def setUp(self):
        self.assertEqual(hashlib.sha256(BOARD.read_bytes()).hexdigest(), BOARD_SHA)
        self.board = pcbnew.LoadBoard(str(BOARD))
        self.outline = pcbnew.SHAPE_POLY_SET()
        self.assertTrue(self.board.GetBoardPolygonOutlines(self.outline, False))
        self.interfaces = json.loads((CROW / '03_src/modular_plan.json').read_text())
        self.regions = yaml.safe_load((CROW / '03_src/floorplan.yaml').read_text())['placement']['regions']
        self.source = yaml.safe_load(SOURCE.read_text())
        self.coverage, _ = checker.graph.source_inventory(self.source, self.interfaces)
        self.aliases = checker.graph.alias_inventory(
            yaml.safe_load((CROW / '02_parts/USB4215-03-A/part.yaml').read_text()))
        _, self.pads = checker.graph.board_index(self.board)
        ident = 'adc7_local_portal'
        affected = [{'source_pad': source_pad,
                     'native_pad': checker.graph.native_identity(source_pad, self.aliases),
                     'net': item['net'], 'block': owner}
                    for item in self.interfaces['interfaces'] if item['net'] in ('ADC7N', 'ADC7P')
                    for owner, sources in item['endpoints'].items() for source_pad in sources]
        self.row = {
            'id': ident, 'allocation_id': 'adc_analog_boundary',
            'nets': ['ADC7N', 'ADC7P'],
            'electrical_owners': ['adc_reference', 'analog_ch7'],
            'transit_owner': 'analog_ch7',
            'planning_overlaps': ['audio_clock_tdm'],
            'portal_bbox': [166, 83.9, 167.12, 85], 'owner_face': 'north',
            'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
            'affected': affected,
            'p2_obligations': [
                {'status': 'P2_REQUIRED', **e, 'portal_id': ident, 'layer': 'F.Cu',
                 'proof': ('native_pad_to_local_port' if e['block'] == 'analog_ch7'
                           else 'native_pad_to_remote_route')}
                for e in affected],
            'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                  'portal_id': ident, 'reference_layer': 'In1.Cu',
                                  'proof': 'continuous_filled_reference'},
            'status': 'INCOMPLETE', 'capacity_slots': None}
        packet = yaml.safe_load((CROW / '01_docs/research/2026-09-25-ti-adc7-access-only-portal-sol/portal.yaml').read_text())
        self.assertEqual(packet, {'access_only_portals': [self.row]})

    def screen(self):
        source = dict(self.source, access_only_portals=[self.row])
        return checker._access_only_portals(source, self.interfaces, self.board,
                                            self.outline, self.regions,
                                            list(self.board.Zones()), self.coverage,
                                            self.aliases, self.pads)

    def test_exact_candidate_is_debt_only(self):
        result = self.screen()
        self.assertEqual(len(self.row['affected']), 8)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['status'], 'INCOMPLETE')
        self.assertIsNone(result[0]['capacity_slots'])
        self.assertEqual(len(result[0]['p2_obligations']), 8)
        self.assertEqual(result[0]['return_obligation']['reference_layer'], 'In1.Cu')

    def test_explicit_null_portal_list_fails(self):
        with self.assertRaisesRegex(checker.ContractError, 'access-only portals malformed'):
            checker._access_only_portals(dict(self.source, access_only_portals=None),
                                         self.interfaces, self.board, self.outline,
                                         self.regions, list(self.board.Zones()),
                                         self.coverage, self.aliases, self.pads)

    def test_missing_and_extra_endpoint_fail(self):
        self.row['affected'].pop()
        with self.assertRaisesRegex(checker.ContractError, 'exact endpoint denominator'):
            self.screen()
        self.row['affected'] = copy.deepcopy(self.row['p2_obligations'])
        with self.assertRaisesRegex(checker.ContractError, 'exact endpoint denominator'):
            self.screen()

    def test_duplicate_source_and_alias_collision_fail(self):
        self.row['affected'].append(copy.deepcopy(self.row['affected'][0]))
        with self.assertRaisesRegex(checker.ContractError, 'exact endpoint denominator'):
            self.screen()
        self.row['affected'].pop()
        alloc = next(a for a in self.source['allocations'] if a['id'] == 'adc_analog_boundary')
        alloc['endpoints']['ADC7N']['analog_ch7'].append('C_ADC_AC7N2.2')
        with self.assertRaisesRegex(checker.ContractError, 'duplicate source terminal'):
            self.screen()
        self.assertRaisesRegex(
            checker.ContractError, 'linked native alias collision',
            checker._linked_native_pad_census,
            'adc7_local_portal',
            {('J_USB.4', 'J_USB.A6', 'ADC7N', 'analog_ch7'),
             ('J_USB.12', 'J_USB.A6', 'ADC7N', 'analog_ch7')},
            {}, {'ADC7N'})

    def test_extra_native_terminal_and_owner_drift_fail(self):
        fp = next(fp for fp in self.board.GetFootprints() if fp.GetReference() == 'U_ADC_B')
        pad = pcbnew.PAD(fp)
        pad.SetNumber('99')
        pad.SetNet(self.board.FindNet('ADC7N'))
        fp.Add(pad)
        _, self.pads = checker.graph.board_index(self.board)
        with self.assertRaisesRegex(checker.ContractError, 'native net pad multiset mismatch'):
            self.screen()
        fp.Remove(pad)
        _, self.pads = checker.graph.board_index(self.board)
        alloc = next(a for a in self.source['allocations'] if a['id'] == 'adc_analog_boundary')
        alloc['endpoints']['ADC7N'] = {'analog_ch7': ['U_ADC_B.11']}
        with self.assertRaisesRegex(checker.ContractError, 'source/modular owner denominator'):
            self.screen()

    def test_audio_is_planning_overlap_not_electrical_owner(self):
        self.row['electrical_owners'].append('audio_clock_tdm')
        with self.assertRaisesRegex(checker.ContractError, 'electrical/planning owner mismatch'):
            self.screen()
        self.row['electrical_owners'].pop()
        self.row['planning_overlaps'] = []
        with self.assertRaisesRegex(checker.ContractError, 'identity/net/role invalid'):
            self.screen()
        self.row['planning_overlaps'] = ['audio_clock_tdm', 'digital_power']
        with self.assertRaisesRegex(checker.ContractError, 'foreign planning overlap mismatch'):
            self.screen()

    def test_edge_foreign_region_and_physical_intrusion_fail(self):
        self.row['portal_bbox'] = [166, 84.1, 167.12, 85]
        with self.assertRaisesRegex(checker.ContractError, 'positive owner-edge contact'):
            self.screen()
        self.row['portal_bbox'] = [166, 83.9, 167.12, 85]
        self.regions['foreign'] = [166, 84, 167.12, 85]
        with self.assertRaisesRegex(checker.ContractError, 'foreign planning overlap mismatch'):
            self.screen()
        del self.regions['foreign']
        fp = next(fp for fp in self.board.GetFootprints() if fp.GetReference() == 'Y_AUDIO')
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(167), pcbnew.FromMM(84)))
        with self.assertRaisesRegex(checker.ContractError, 'native footprint/pad'):
            self.screen()

    def test_off_board_portal_fails(self):
        self.row['portal_bbox'] = [166, 83.9, 241, 85]
        with self.assertRaisesRegex(checker.ContractError, 'off board outline'):
            self.screen()

    def test_p2_return_and_capacity_claim_fail(self):
        self.row['p2_obligations'].pop()
        with self.assertRaisesRegex(checker.ContractError, 'P2/filled-return debt invalid'):
            self.screen()
        self.row['p2_obligations'] = [
            {'status': 'P2_REQUIRED', **e, 'portal_id': 'adc7_local_portal',
             'layer': 'F.Cu', 'proof': ('native_pad_to_local_port' if e['block'] == 'analog_ch7'
                                      else 'native_pad_to_remote_route')}
            for e in self.row['affected']]
        self.row['return_obligation'] = {}
        with self.assertRaisesRegex(checker.ContractError, 'P2/filled-return debt invalid'):
            self.screen()
        self.row['return_obligation'] = {'status': 'P2_REQUIRED', 'net': 'GND',
                                         'portal_id': 'adc7_local_portal',
                                         'reference_layer': 'In1.Cu',
                                         'proof': 'continuous_filled_reference'}
        self.row['capacity_slots'] = 2
        with self.assertRaisesRegex(checker.ContractError, 'identity/net/role invalid'):
            self.screen()
        self.row['capacity_slots'] = None
        self.row['status'] = 'PASS'
        with self.assertRaisesRegex(checker.ContractError, 'identity/net/role invalid'):
            self.screen()

    def test_opt_in_does_not_change_legacy_credit_or_p1_result(self):
        fixture = LinkedPathTest('test_valid_series_stays_incomplete_without_capacity_credit')
        fixture.setUp()
        fixture.floorplan['placement']['regions']['planning'] = [10, 9, 11, 11]
        baseline = fixture.run_case()
        self.assertNotIn('access_only_portals', baseline)
        affected = [{'source_pad': f'{ref}.{pin}', 'native_pad': f'{ref}.{pin}',
                     'net': net, 'block': block}
                    for pin, net in [('1', 'DP'), ('2', 'DN')]
                    for ref, block in [('J', 'edge'), ('E', 'front'), ('X', 'xmos')]]
        ident = 'front_local_portal'
        fixture.source['access_only_portals'] = [{
            'id': ident, 'allocation_id': 'signal', 'nets': ['DP', 'DN'],
            'electrical_owners': ['edge', 'front', 'xmos'],
            'transit_owner': 'front', 'planning_overlaps': ['planning'],
            'portal_bbox': [9.9, 9.9, 10.2, 10.2], 'owner_face': 'north',
            'layer': 'F.Cu', 'reference_layer': 'B.Cu', 'affected': affected,
            'p2_obligations': [
                {'status': 'P2_REQUIRED', **e, 'portal_id': ident, 'layer': 'F.Cu',
                 'proof': ('native_pad_to_local_port' if e['block'] == 'front'
                           else 'native_pad_to_remote_route')}
                for e in affected],
            'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                  'portal_id': ident, 'reference_layer': 'B.Cu',
                                  'proof': 'continuous_filled_reference'},
            'status': 'INCOMPLETE', 'capacity_slots': None}]
        result = fixture.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['allocations'], baseline['allocations'])
        self.assertEqual(result['status'], baseline['status'])
        self.assertEqual(result['p1_accepted'], baseline['p1_accepted'])
        self.assertFalse(result['routing_realized'])
        self.assertEqual(result['access_only_portals'][0]['capacity_slots'], None)


if __name__ == '__main__':
    unittest.main()
