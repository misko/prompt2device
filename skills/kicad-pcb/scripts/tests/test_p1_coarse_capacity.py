#!/usr/bin/env python3
"""Synthetic native fixtures for the coarse P1 reservation profile."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import p1_corridor_capacity as checker  # noqa: E402


def iu(mm):
    return pcbnew.FromMM(mm)


def pad(board, ref, number, net, x, y, size=0.5):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue('fixture')
    fp.SetLayer(pcbnew.F_Cu)
    fp.SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    item = pcbnew.PAD(fp)
    item.SetNumber(number)
    item.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    item.SetShape(pcbnew.PAD_SHAPE_RECT)
    item.SetSize(pcbnew.VECTOR2I(iu(size), iu(size)))
    item.SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    item.SetLayerSet(pcbnew.LSET.FrontMask())
    native_net = board.FindNet(net)
    if native_net is None:
        native_net = pcbnew.NETINFO_ITEM(board, net)
        board.Add(native_net)
    item.SetNet(native_net)
    fp.Add(item)
    board.Add(fp)


class CoarseCapacityTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.board = pcbnew.BOARD()
        corners = [(0, 0), (10, 0), (10, 10), (0, 10)]
        for a, b in zip(corners, corners[1:] + corners[:1]):
            edge = pcbnew.PCB_SHAPE(self.board)
            edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
            edge.SetStart(pcbnew.VECTOR2I(iu(a[0]), iu(a[1])))
            edge.SetEnd(pcbnew.VECTOR2I(iu(b[0]), iu(b[1])))
            edge.SetLayer(pcbnew.Edge_Cuts)
            self.board.Add(edge)
        for row in [('J_LEFT', '1', 'TEST', 2, 5, .5),
                    ('J_RIGHT', '1', 'TEST', 8, 5, .5),
                    ('J_G', '1', 'GND', 2, 2, .5),
                    ('J_G2', '1', 'GND', 8, 2, .5),
                    ('R_MOVE', '1', 'OTHER', 5, 5, 2)]:
            pad(self.board, *row)
        self.source = {'kind': 'crow-p1-corridor-requirements',
                       'p1_fixed_refs': ['J_LEFT', 'J_G'], 'allocations': [
            {'id': 'signal', 'coverage_nets': ['TEST'],
             'endpoints': {'TEST': {'left': ['J_LEFT.1'], 'right': ['J_RIGHT.1']}}}],
            'power_boundary_windows': {'coverage_nets': ['GND']}}
        self.interfaces = {'interfaces': [
            {'net': 'TEST', 'endpoints': {'left': ['J_LEFT.1'], 'right': ['J_RIGHT.1']}},
            {'net': 'GND', 'endpoints': {'power': ['J_G.1', 'J_G2.1']}}]}
        self.floorplan = {'placement': {
            'anchors': {'J_LEFT': [2, 5, 0], 'J_G': [2, 2, 0]},
            'post_anchors': {'J_RIGHT': [8, 5, 0], 'J_G2': [8, 2, 0], 'R_MOVE': [5, 5, 0]},
            'seeds': {}, 'patterns': [],
            'regions': {'left': [0, 3, 4, 7], 'right': [6, 3, 10, 7],
                        'power': [0, 0, 4, 4]}}}
        self.allocations = [
            {'id': 'signal', 'coverage_nets': ['TEST'],
             'boundary_witnesses': [{'source': 'J_LEFT.1', 'native': 'J_LEFT.1', 'net': 'TEST',
                                     'block': 'left', 'layer': 'F.Cu', 'face': 'west',
                                     'boundary_bbox': [1.5, 4.5, 2.5, 5.5], 'reservation_id': 'signal_main'}],
             'reservations': [{'id': 'signal_main', 'kind': 'signal', 'layer': 'F.Cu',
                               'bbox': [2.5, 4, 7.5, 6], 'axis': 'horizontal',
                               'nets': ['TEST'], 'demand_slots': 2, 'slot_pitch_mm': .5}]},
            {'id': 'power_boundary_windows', 'coverage_nets': ['GND'],
             'boundary_witnesses': [{'source': 'J_G.1', 'native': 'J_G.1', 'net': 'GND',
                                     'block': 'power', 'layer': 'F.Cu', 'face': 'west',
                                     'boundary_bbox': [1.5, 1.5, 2.5, 2.5], 'reservation_id': 'power'}],
             'reservations': [{'id': 'power', 'kind': 'power_or_mechanical', 'layer': 'F.Cu',
                               'bbox': [2.5, 1, 7.5, 3], 'nets': ['GND']}]},
        ]

    def add_virtual_right_face(self):
        self.floorplan['placement']['regions']['right'] = [7.5, 3, 10, 7]
        witness = {'kind': 'virtual_block_face', 'source': 'J_RIGHT.1',
                   'native': 'J_RIGHT.1', 'net': 'TEST', 'block': 'right',
                   'region_id': 'right', 'region_face': 'west', 'face': 'east',
                   'layer': 'F.Cu', 'boundary_bbox': [7.5, 4.8, 7.9, 5.2],
                   'reservation_id': 'signal_main',
                   'p2_obligation': {'status': 'P2_REQUIRED', 'source_pad': 'J_RIGHT.1',
                                     'native_pad': 'J_RIGHT.1', 'net': 'TEST', 'block': 'right',
                                     'region_face': 'west', 'layer': 'F.Cu',
                                     'to_reservation': 'signal_main'}}
        self.allocations[0]['boundary_witnesses'].append(witness)
        return witness

    def run_case(self, change=None):
        if change:
            change()
        paths = {name: self.root / name for name in
                 ('board.kicad_pcb', 'contract.json', 'source.yaml', 'interfaces.json',
                  'aliases.yaml', 'floorplan.yaml')}
        pcbnew.SaveBoard(str(paths['board.kicad_pcb']), self.board)
        paths['source.yaml'].write_text(yaml.safe_dump(self.source))
        paths['interfaces.json'].write_text(json.dumps(self.interfaces))
        paths['aliases.yaml'].write_text(yaml.safe_dump({'pin_aliases': {}}))
        paths['floorplan.yaml'].write_text(yaml.safe_dump(self.floorplan))
        hashes = {name: checker.digest(path) for name, path in paths.items() if name != 'contract.json'}
        contract = {'schema': 2, 'kind': 'p1-coarse-reservations', 'profile': 'fixture-coarse',
                    'board_sha256': hashes['board.kicad_pcb'],
                    'source_sha256': hashes['source.yaml'],
                    'interfaces_sha256': hashes['interfaces.json'],
                    'aliases_sha256': hashes['aliases.yaml'],
                    'floorplan_sha256': hashes['floorplan.yaml'], 'allocations': self.allocations}
        paths['contract.json'].write_text(json.dumps(contract))
        return checker.evaluate(paths['board.kicad_pcb'], paths['contract.json'],
                                checker.digest(paths['contract.json']),
                                source_path=paths['source.yaml'], interface_path=paths['interfaces.json'],
                                alias_path=paths['aliases.yaml'], floorplan_path=paths['floorplan.yaml'],
                                expected_source_sha256=hashes['source.yaml'],
                                expected_interface_sha256=hashes['interfaces.json'],
                                expected_alias_sha256=hashes['aliases.yaml'],
                                expected_floorplan_sha256=hashes['floorplan.yaml'])

    def test_movable_obstruction_is_named_debt_without_false_p1_failure(self):
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['routing_realized'])
        self.assertFalse(result['p1_accepted'])
        reservation = result['allocations'][0]['reservations'][0]
        self.assertIn('R_MOVE', reservation['movable_relocation_debt'])
        self.assertGreaterEqual(reservation['potential_slots'], 2)
        self.assertLess(reservation['current_slots'], 2)

    def test_fixed_anchor_closing_reservation_fails(self):
        self.floorplan['placement']['post_anchors'].pop('R_MOVE')
        self.floorplan['placement']['anchors']['R_MOVE'] = [5, 5, 0]
        self.source['p1_fixed_refs'].append('R_MOVE')
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('R_MOVE', result['allocations'][0]['reservations'][0]['fixed_obstacles'])

    def test_source_anchor_can_still_be_p2_movable(self):
        self.floorplan['placement']['post_anchors'].pop('R_MOVE')
        self.floorplan['placement']['anchors']['R_MOVE'] = [5, 5, 0]
        result = self.run_case()
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertIn('R_MOVE', result['allocations'][0]['reservations'][0]['movable_relocation_debt'])

    def test_post_anchor_overrides_seed_and_anchor_for_fixed_pose(self):
        self.floorplan['placement']['seeds']['J_RIGHT'] = [3, 3, 0]
        self.floorplan['placement']['anchors']['J_RIGHT'] = [4, 4, 0]
        self.source['p1_fixed_refs'].append('J_RIGHT')
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['allocations'][0]['reservation_count'], 1)
        self.assertFalse(result['p1_accepted'])

    def test_missing_and_wrong_witness_fail_closed(self):
        result = self.run_case(lambda: self.allocations[0]['boundary_witnesses'].clear())
        self.assertIn('denominator missing', result['allocations'][0]['reason'])
        self.setUp()
        result = self.run_case(lambda: self.allocations[0]['boundary_witnesses'][0].update(native='J_RIGHT.1'))
        self.assertIn('alias mismatch', result['allocations'][0]['reason'])

    def test_witness_native_net_mismatch_is_rejected(self):
        fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'J_LEFT')
        next(iter(fp.Pads())).SetNet(self.board.FindNet('OTHER'))
        result = self.run_case()
        self.assertIn('native pad/net mismatch', result['allocations'][0]['reason'])

    def test_off_outline_reservation_and_wrong_face_fail_closed(self):
        result = self.run_case(lambda: self.allocations[0]['reservations'][0].update(bbox=[2.5, 4, 10.5, 6]))
        self.assertIn('off board outline', result['allocations'][0]['reason'])
        self.setUp()
        result = self.run_case(lambda: self.allocations[0]['boundary_witnesses'][0].update(face='east'))
        self.assertIn('block face does not contact', result['allocations'][0]['reason'])

    def test_long_witness_bridge_cannot_claim_local_block_face(self):
        self.allocations[0]['boundary_witnesses'][0]['boundary_bbox'] = [1.5, 4.5, 7.5, 5.5]
        self.allocations[0]['reservations'][0]['bbox'] = [7.5, 4, 9.5, 6]
        result = self.run_case()
        self.assertIn('nonlocal bridge across source region', result['allocations'][0]['reason'])

    def test_movable_virtual_face_defers_pad_to_face_to_p2(self):
        self.add_virtual_right_face()
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['allocations'][0]['witness_count'], 2)
        self.assertEqual(len(result['allocations'][0]['p2_obligations']), 1)
        self.assertEqual(result['allocations'][0]['p2_obligations'][0]['native_pad'], 'J_RIGHT.1')
        self.assertFalse(result['p1_accepted'])

    def test_virtual_face_rejects_bad_region_or_missing_obligation(self):
        witness = self.add_virtual_right_face()
        witness['region_face'] = 'east'
        result = self.run_case()
        self.assertIn('region/reservation face mismatch', result['allocations'][0]['reason'])
        self.setUp()
        witness = self.add_virtual_right_face()
        witness.pop('p2_obligation')
        result = self.run_case()
        self.assertIn('P2 pad-to-face obligation missing', result['allocations'][0]['reason'])

    def test_virtual_face_rejects_corner_and_wrong_owner(self):
        witness = self.add_virtual_right_face()
        witness['boundary_bbox'] = [7.5, 3, 7.9, 3.4]
        result = self.run_case()
        self.assertIn('ambiguous region corner', result['allocations'][0]['reason'])
        self.setUp()
        witness = self.add_virtual_right_face()
        witness['block'] = 'power'
        result = self.run_case()
        self.assertIn('source/block ownership mismatch', result['allocations'][0]['reason'])

    def test_movable_pad_cannot_use_physical_witness_and_fixed_cannot_use_virtual(self):
        self.source['p1_fixed_refs'].remove('J_LEFT')
        result = self.run_case()
        self.assertIn('P2-movable owner requires virtual', result['allocations'][0]['reason'])
        self.setUp()
        self.allocations[0]['boundary_witnesses'][0]['kind'] = 'virtual_block_face'
        result = self.run_case()
        self.assertIn('fixed P1 ref cannot use virtual', result['allocations'][0]['reason'])

    def test_native_rule_area_overlap_fails_closed(self):
        zone = pcbnew.ZONE(self.board)
        zone.SetIsRuleArea(True)
        zone.SetZoneName('NO_SIGNAL')
        zone.SetLayer(pcbnew.F_Cu)
        polygon = zone.Outline()
        polygon.NewOutline()
        for x, y in ((4, 4), (6, 4), (6, 6), (4, 6)):
            polygon.Append(pcbnew.VECTOR2I(iu(x), iu(y)))
        self.board.Add(zone)
        result = self.run_case()
        self.assertIn('immutable native rule area', result['allocations'][0]['reason'])

    def test_same_layer_cross_allocation_overlap_fails(self):
        self.allocations[1]['reservations'][0]['bbox'] = [2.5, 4, 7.5, 6]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('overlapping named allocations', '\n'.join(result['errors']))

    def test_pretend_p2_pocket_proof_is_rejected(self):
        result = self.run_case(lambda: self.allocations[0].update(endpoint_pockets=[]))
        self.assertIn('attempts P2/P3 all-terminal proof', '\n'.join(result['errors']))

    def test_crow_profile_rejects_non_59_fixture(self):
        # A fixture never becomes a Crow PASS by merely changing its profile.
        result = self.run_case()
        contract = self.root / 'contract.json'
        payload = json.loads(contract.read_text())
        payload['profile'] = 'crow-p1-coarse'
        contract.write_text(json.dumps(payload))
        result = checker.evaluate(self.root / 'board.kicad_pcb', contract, checker.digest(contract),
                                  source_path=self.root / 'source.yaml', interface_path=self.root / 'interfaces.json',
                                  alias_path=self.root / 'aliases.yaml', floorplan_path=self.root / 'floorplan.yaml',
                                  expected_source_sha256=checker.digest(self.root / 'source.yaml'),
                                  expected_interface_sha256=checker.digest(self.root / 'interfaces.json'),
                                  expected_alias_sha256=checker.digest(self.root / 'aliases.yaml'),
                                  expected_floorplan_sha256=checker.digest(self.root / 'floorplan.yaml'))
        self.assertIn('59-net source coverage mismatch', '\n'.join(result['errors']))

    def test_missing_source_fixed_set_is_incomplete(self):
        result = self.run_case(lambda: self.source.pop('p1_fixed_refs'))
        self.assertIn('p1_fixed_refs authority', '\n'.join(result['errors']))

    def test_native_npth_cannot_bypass_source_fixed_pose_authority(self):
        fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'R_MOVE')
        next(iter(fp.Pads())).SetAttribute(pcbnew.PAD_ATTRIB_NPTH)
        result = self.run_case()
        self.assertIn('NPTH references missing p1_fixed_refs', '\n'.join(result['errors']))

    def test_signal_allocation_cannot_hide_as_power_capacity(self):
        self.allocations[0]['reservations'][0]['kind'] = 'power_or_mechanical'
        result = self.run_case()
        self.assertIn('only source-authorized power-like nets may omit signal capacity',
                      result['allocations'][0]['reason'])

    def test_source_authorized_usb_vbus_can_use_power_window(self):
        native_net = pcbnew.NETINFO_ITEM(self.board, 'VBUS_USB')
        self.board.Add(native_net)
        for fp in self.board.GetFootprints():
            if fp.GetReference() in ('J_LEFT', 'J_RIGHT'):
                next(iter(fp.Pads())).SetNet(native_net)
        source_row = self.source['allocations'][0]
        source_row['id'] = 'usb_device_pair'
        source_row['coverage_nets'] = ['VBUS_USB']
        source_row['endpoints']['VBUS_USB'] = source_row['endpoints'].pop('TEST')
        source_row['demands'] = [{'id': 'usb_local_power', 'nets': ['VBUS_USB'],
                                  'status': 'INCOMPLETE'}]
        self.interfaces['interfaces'][0]['net'] = 'VBUS_USB'
        row = self.allocations[0]
        row['id'] = 'usb_device_pair'
        row['coverage_nets'] = ['VBUS_USB']
        row['boundary_witnesses'][0]['net'] = 'VBUS_USB'
        row['reservations'][0]['nets'] = ['VBUS_USB']
        row['reservations'][0]['kind'] = 'power_or_mechanical'
        row['reservations'][0].pop('axis')
        row['reservations'][0].pop('demand_slots')
        row['reservations'][0].pop('slot_pitch_mm')
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['allocations'][0]['reservation_count'], 1)
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['p1_accepted'])


if __name__ == '__main__':
    unittest.main()
