#!/usr/bin/env python3
"""Native KiCad fixtures for the bounded P1 named-corridor screen."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import p1_corridor_capacity as checker  # noqa: E402


def iu(mm):
    return pcbnew.FromMM(mm)


def add_pad(board, ref, x, y, sx=1, sy=1, layer='F.Cu', through=False):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue('fixture')
    fp.SetLayer(pcbnew.F_Cu if layer == 'F.Cu' else pcbnew.B_Cu)
    fp.SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    pad = pcbnew.PAD(fp)
    pad.SetNumber('1')
    pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH if through else pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(pcbnew.VECTOR2I(iu(sx), iu(sy)))
    pad.SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    if through:
        pad.SetDrillSize(pcbnew.VECTOR2I(iu(0.4), iu(0.4)))
    pad.SetLayerSet(pcbnew.LSET.AllCuMask() if through else
                    pcbnew.LSET.FrontMask() if layer == 'F.Cu' else pcbnew.LSET.BackMask())
    net = board.FindNet('TEST')
    if net is None:
        net = pcbnew.NETINFO_ITEM(board, 'TEST')
        board.Add(net)
    pad.SetNet(net)
    fp.Add(pad)
    board.Add(fp)


class CorridorCapacityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.board = pcbnew.BOARD()
        edge = [(-4, -4), (14, -4), (14, 8), (-4, 8)]
        for a, b in zip(edge, edge[1:] + edge[:1]):
            segment = pcbnew.PCB_SHAPE(self.board)
            segment.SetShape(pcbnew.SHAPE_T_SEGMENT)
            segment.SetStart(pcbnew.VECTOR2I(iu(a[0]), iu(a[1])))
            segment.SetEnd(pcbnew.VECTOR2I(iu(b[0]), iu(b[1])))
            segment.SetLayer(pcbnew.Edge_Cuts)
            self.board.Add(segment)
        add_pad(self.board, 'J_LEFT', -2, 2, through=True)
        add_pad(self.board, 'J_RIGHT', 12, 2, through=True)

    def run_contract(self, **changes):
        board_path = self.root / 'fixture.kicad_pcb'
        pcbnew.SaveBoard(str(board_path), self.board)
        row = {'id': 'named-lane', 'axis': 'horizontal',
               'through_lane': [0, 0, 10, 4], 'layers': ['F.Cu'],
               'slot_pitch_mm': 0.9, 'demand_slots': 2,
               'coverage_members': ['J_LEFT.1', 'J_RIGHT.1'],
               'coverage_nets': ['TEST'],
               'endpoint_pockets': [{'ref': 'J_LEFT', 'pad': '1', 'net': 'TEST', 'pocket': [-3, 1, 0, 3]},
                                    {'ref': 'J_RIGHT', 'pad': '1', 'net': 'TEST', 'pocket': [10, 1, 13, 3]}]}
        row.update(changes)
        contract_path = self.root / 'contract.json'
        contract_path.write_text(json.dumps({'schema': 1, 'board_sha256': checker.digest(board_path),
                                             'expected_interface_coverage': {'named-lane': ['TEST']},
                                             'required_rule_areas': [], 'reference_plane_required': False,
                                             'allocations': [row]}))
        return checker.evaluate(board_path, contract_path, checker.digest(contract_path)), board_path, contract_path

    def changed_contract(self, board, contract, change):
        data = json.loads(contract.read_text())
        change(data)
        contract.write_text(json.dumps(data))
        return checker.evaluate(board, contract, checker.digest(contract))

    def test_empty_lane_is_diagnostic_until_native_rules_are_verified(self):
        report, board, contract = self.run_contract()
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertEqual(report['board_sha256'], checker.digest(board))
        self.assertEqual(report['contract_sha256'], checker.digest(contract))
        self.assertFalse(report['routing_realized'])
        self.assertFalse(report['p1_accepted'])
        self.assertEqual(report['allocations'][0]['layers']['F.Cu']['capacity_slots'], 4)
        self.assertTrue(report['allocations'][0]['layers']['F.Cu']['capacity_is_optimistic'])

    def test_foreign_obstacle_reduces_capacity_but_endpoint_pockets_do_not(self):
        add_pad(self.board, 'R_FOREIGN', 5, 2, 1, 2)
        report, _, _ = self.run_contract()
        self.assertEqual(report['status'], 'FAIL')
        lane = report['allocations'][0]['layers']['F.Cu']
        self.assertEqual(lane['capacity_slots'], 1)
        self.assertTrue(any(s.startswith('R_FOREIGN:') for s in lane['foreign_obstacles']))
        self.assertFalse(any('J_LEFT' in s for s in lane['foreign_obstacles']))

    def test_disjoint_necks_fail_even_when_each_cross_section_is_wide(self):
        add_pad(self.board, 'R_LOW', 3, 1, 2, 2)
        add_pad(self.board, 'R_HIGH', 5, 3, 2, 2)
        report, _, _ = self.run_contract(demand_slots=1)
        lane = report['allocations'][0]['layers']['F.Cu']
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(lane['capacity_slots'], 0)
        self.assertFalse(lane['connected_through_lane'])
        self.assertTrue(all(section['max_free_width_mm'] >= 2 for section in lane['cross_sections']))

    def test_existing_copper_can_close_the_entire_lane(self):
        trace = pcbnew.PCB_TRACK(self.board)
        trace.SetStart(pcbnew.VECTOR2I(iu(5), iu(0)))
        trace.SetEnd(pcbnew.VECTOR2I(iu(5), iu(4)))
        trace.SetWidth(iu(1))
        trace.SetLayer(pcbnew.F_Cu)
        self.board.Add(trace)
        report, _, _ = self.run_contract(demand_slots=1)
        lane = report['allocations'][0]['layers']['F.Cu']
        self.assertEqual(report['status'], 'FAIL')
        self.assertEqual(lane['capacity_slots'], 0)
        self.assertIn('existing-copper', lane['foreign_obstacles'])

    def test_layer_results_are_independent_and_all_declared_layers_must_pass(self):
        add_pad(self.board, 'R_FRONT', 5, 2, 1, 2, layer='F.Cu')
        report, _, _ = self.run_contract(layers=['F.Cu', 'B.Cu'])
        self.assertEqual(report['status'], 'FAIL')
        layers = report['allocations'][0]['layers']
        self.assertEqual(layers['F.Cu']['status'], 'FAIL')
        self.assertEqual(layers['B.Cu']['status'], 'INCOMPLETE')

    def test_smd_endpoint_cannot_claim_unconnected_back_layer(self):
        add_pad(self.board, 'J_SMD', 5, -2)
        report, board, contract = self.run_contract()
        def add_endpoint(data):
            row = data['allocations'][0]
            row['layers'] = ['F.Cu', 'B.Cu']
            row['coverage_members'].append('J_SMD.1')
            row['endpoint_pockets'].append({'ref': 'J_SMD', 'pad': '1', 'net': 'TEST',
                                            'pocket': [4, -3, 6, 0]})
        report = self.changed_contract(board, contract, add_endpoint)
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('absent from a declared layer', report['allocations'][0]['reason'])

    def test_missing_geometry_and_hash_drift_fail_closed(self):
        report, board, contract = self.run_contract(endpoint_pockets=[])
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('denominator is zero', report['allocations'][0]['reason'])
        data = json.loads(contract.read_text())
        data['allocations'][0]['endpoint_pockets'] = [
            {'ref': 'J_LEFT', 'pad': '1', 'net': 'TEST', 'pocket': [-3, 1, 1, 3]}]
        contract.write_text(json.dumps(data))
        report = checker.evaluate(board, contract, checker.digest(contract))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('intersects through lane', report['allocations'][0]['reason'])
        board.write_bytes(board.read_bytes() + b'\n')
        report = checker.evaluate(board, contract, checker.digest(contract))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('board hash drift', report['errors'][0])

    def test_offboard_lane_is_incomplete(self):
        _, board, contract = self.run_contract()
        report = self.changed_contract(board, contract, lambda data: data['allocations'][0].update(
            through_lane=[0, 0, 20, 4]))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('off board', report['allocations'][0]['reason'])

    def test_duplicate_reference_is_incomplete(self):
        add_pad(self.board, 'J_LEFT', -2, 3)
        report, _, _ = self.run_contract()
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('duplicate board reference', report['allocations'][0]['reason'])

    def test_wrong_pad_or_net_is_incomplete(self):
        report, board, contract = self.run_contract()
        self.assertEqual(report['status'], 'INCOMPLETE')
        report = self.changed_contract(board, contract, lambda data: data['allocations'][0]['endpoint_pockets'][0].update(net='OTHER'))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('pad/net identity mismatch', report['allocations'][0]['reason'])
        report = self.changed_contract(board, contract, lambda data: data['allocations'][0]['endpoint_pockets'][0].update(pad='99'))
        self.assertIn('pad/net identity mismatch', report['allocations'][0]['reason'])

    def test_disconnected_endpoint_pocket_is_incomplete(self):
        _, board, contract = self.run_contract()
        report = self.changed_contract(board, contract, lambda data: data['allocations'][0]['endpoint_pockets'][0].update(
            pocket=[-3, 1, -1, 3]))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('does not contact through lane', report['allocations'][0]['reason'])

    def test_endpoint_pocket_outside_board_is_incomplete(self):
        _, board, contract = self.run_contract()
        report = self.changed_contract(board, contract, lambda data: data['allocations'][0]['endpoint_pockets'][0].update(
            pocket=[-5, 1, 0, 3]))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('endpoint pocket extends off board', report['allocations'][0]['reason'])

    def test_overlapping_same_layer_allocations_are_incomplete(self):
        _, board, contract = self.run_contract()
        def overlap(data):
            other = dict(data['allocations'][0])
            other['id'] = 'other-lane'
            data['allocations'].append(other)
            data['expected_interface_coverage']['other-lane'] = ['OTHER']
            other['coverage_nets'] = ['OTHER']
        report = self.changed_contract(board, contract, overlap)
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('overlapping named lanes', '\n'.join(report['errors']))

    def test_missing_interface_and_rule_area_are_incomplete(self):
        _, board, contract = self.run_contract()
        report = self.changed_contract(board, contract, lambda data: data['expected_interface_coverage']['named-lane'].append('MISSING'))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('interface coverage mismatch', '\n'.join(report['errors']))
        report = self.changed_contract(board, contract, lambda data: data.update(required_rule_areas=['KEEP_CLEAR']))
        self.assertIn('rule-area presence', '\n'.join(report['errors']))

    def test_claimed_coverage_net_requires_matching_endpoint_pad_net(self):
        _, board, contract = self.run_contract()
        def wrong_net(data):
            data['expected_interface_coverage']['named-lane'] = ['OTHER']
            data['allocations'][0]['coverage_nets'] = ['OTHER']
        report = self.changed_contract(board, contract, wrong_net)
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('coverage_nets must equal verified endpoint pad nets',
                      report['allocations'][0]['reason'])

    def test_one_pad_cannot_serve_as_a_through_corridor(self):
        _, board, contract = self.run_contract()
        def single_endpoint(data):
            row = data['allocations'][0]
            row['endpoint_pockets'] = row['endpoint_pockets'][:1]
            row['coverage_members'] = row['coverage_members'][:1]
        report = self.changed_contract(board, contract, single_endpoint)
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('at least two verified endpoint pads', report['allocations'][0]['reason'])

    def test_native_rule_area_overlap_fails_even_with_exact_inventory(self):
        zone = pcbnew.ZONE(self.board)
        zone.SetIsRuleArea(True)
        zone.SetZoneName('KEEP_CLEAR')
        zone.SetLayer(pcbnew.F_Cu)
        polygon = zone.Outline()
        polygon.NewOutline()
        for x, y in ((4, 1), (6, 1), (6, 3), (4, 3)):
            polygon.Append(pcbnew.VECTOR2I(iu(x), iu(y)))
        self.board.Add(zone)
        _, board, contract = self.run_contract()
        loaded = pcbnew.LoadBoard(str(board))
        native_zone = next(z for z in loaded.Zones() if z.GetIsRuleArea())
        inventory = [{'name': native_zone.GetZoneName(),
                      'bbox': [round(v, 6) for v in checker.box_mm(native_zone.GetBoundingBox())],
                      'layers': sorted(loaded.GetLayerName(i) for i in native_zone.GetLayerSet().Seq())}]
        report = self.changed_contract(board, contract, lambda data: data.update(required_rule_areas=inventory))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertNotIn('rule-area presence', '\n'.join(report['errors']))
        self.assertIn('native rule-area overlaps through lane', report['allocations'][0]['reason'])

    def test_pitch_under_native_minimum_is_incomplete(self):
        _, board, contract = self.run_contract()
        report = self.changed_contract(board, contract, lambda data: data['allocations'][0].update(slot_pitch_mm=0.001))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('understates native minimum', report['allocations'][0]['reason'])

    def test_expected_contract_digest_is_required(self):
        _, board, contract = self.run_contract()
        report = checker.evaluate(board, contract)
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('contract hash not bound', '\n'.join(report['errors']))

    def test_missing_board_still_produces_incomplete_report(self):
        _, board, contract = self.run_contract()
        board.unlink()
        report = checker.evaluate(board, contract, checker.digest(contract))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIsNone(report['board_sha256'])
        self.assertIn('board unavailable', '\n'.join(report['errors']))

    def test_crow_profile_requires_exact_four_allocations_and_plane_proof(self):
        _, board, contract = self.run_contract()
        report = self.changed_contract(board, contract, lambda data: data.update(profile='crow-p1'))
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('allocation IDs differ', '\n'.join(report['errors']))
        self.assertIn('reference-plane/pour continuity', '\n'.join(report['errors']))
        self.assertEqual(sum(map(len, checker.CROW_COVERAGE.values())), 59)

    def test_copper_pour_intersection_is_incomplete(self):
        zone = pcbnew.ZONE(self.board)
        zone.SetLayer(pcbnew.F_Cu)
        polygon = zone.Outline()
        polygon.NewOutline()
        for x, y in ((4, 1), (6, 1), (6, 3), (4, 3)):
            polygon.Append(pcbnew.VECTOR2I(iu(x), iu(y)))
        self.board.Add(zone)
        report, _, _ = self.run_contract()
        self.assertEqual(report['status'], 'INCOMPLETE')
        self.assertIn('copper pour intersects lane', report['allocations'][0]['reason'])


if __name__ == '__main__':
    unittest.main()
