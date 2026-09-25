#!/usr/bin/env python3
"""Synthetic native fixtures for the coarse P1 reservation profile."""
from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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
    fp.Reference().SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    fp.Value().SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
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
        for row in [('J_LEFT', '1', 'TEST', 3.5, 5, .5),
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
            'anchors': {'J_LEFT': [3.5, 5, 0], 'J_G': [2, 2, 0]},
            'post_anchors': {'J_RIGHT': [8, 5, 0], 'J_G2': [8, 2, 0], 'R_MOVE': [5, 5, 0]},
            'seeds': {}, 'patterns': [],
            'regions': {'left': [0, 3, 4, 7], 'right': [6, 3, 10, 7],
                        'power': [0, 0, 4, 4]}}}
        self.allocations = [
            {'id': 'signal', 'coverage_nets': ['TEST'],
             'boundary_witnesses': [{'source': 'J_LEFT.1', 'native': 'J_LEFT.1', 'net': 'TEST',
                                     'block': 'left', 'layer': 'F.Cu', 'face': 'west',
                                     'boundary_bbox': [3, 4.5, 4, 5.5], 'reservation_id': 'signal_main'}],
             'reservations': [{'id': 'signal_main', 'kind': 'signal', 'layer': 'F.Cu',
                               'bbox': [4, 4, 7.5, 6], 'axis': 'horizontal',
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

    def add_shared_port(self):
        self.interfaces['blocks'] = [
            {'id': 'left', 'refs': ['J_LEFT']},
            {'id': 'right', 'refs': ['J_RIGHT', 'R_MOVE']},
            {'id': 'power', 'refs': ['J_G', 'J_G2']}]
        self.floorplan['placement']['regions']['left'] = [0, 3, 5, 7]
        endpoint = {'source_pad': 'J_RIGHT.1', 'native_pad': 'J_RIGHT.1',
                    'net': 'TEST', 'block': 'right'}
        obligation = {'status': 'P2_REQUIRED', **endpoint, 'port_id': 'joint',
                      'layer': 'F.Cu', 'to_reservation': 'signal_main'}
        port = {'id': 'joint', 'owner': 'board_integration',
                'participants': ['left', 'right'],
                'geometry': {'type': 'union_rectangles',
                             'rectangles': [[4, 3, 7, 7], [7, 3, 8, 7]]},
                'bbox': [6.2, 4.2, 6.5, 4.6], 'face': 'east',
                'layers': ['F.Cu'], 'reservation_id': 'signal_main',
                'reservation_bbox': [4, 4, 6.2, 6], 'affected': [endpoint],
                'p2_obligations': [obligation],
                'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                      'port_id': 'joint', 'layers': ['F.Cu'],
                                      'proof': 'continuous_filled_reference'}}
        self.source['shared_transition_ports'] = [port]
        self.allocations[0]['reservations'][0]['bbox'] = [4, 4, 6.2, 6]
        witness = {'kind': 'shared_transition_port', 'port_id': 'joint',
                   'source': 'J_RIGHT.1', 'native': 'J_RIGHT.1', 'net': 'TEST',
                   'block': 'right', 'layer': 'F.Cu', 'face': 'east',
                   'boundary_bbox': port['bbox'][:], 'reservation_id': 'signal_main',
                   'p2_obligation': obligation.copy()}
        self.allocations[0]['boundary_witnesses'].append(witness)
        return port, witness

    def add_integration_corridor(self):
        """A six-net QSPI-shaped gap with two source-owned adjacent faces."""
        nets = [f'QSPI_{suffix}' for suffix in ('CLK', 'CS_N', 'D0', 'D1', 'D2', 'D3')]
        self.floorplan['placement']['post_anchors']['R_MOVE'] = [8, 8, 0]
        movable = next(f for f in self.board.GetFootprints() if f.GetReference() == 'R_MOVE')
        movable.SetPosition(pcbnew.VECTOR2I(iu(8), iu(8)))
        self.floorplan['placement']['regions']['board_integration_qspi'] = [4, 3, 6, 7]
        self.interfaces['blocks'] = [
            {'id': 'left', 'refs': ['J_LEFT']}, {'id': 'right', 'refs': ['J_RIGHT', 'R_MOVE']},
            {'id': 'power', 'refs': ['J_G', 'J_G2']},
            {'id': 'board_integration', 'refs': []}]
        endpoints = {}
        affected = []
        for index, net in enumerate(nets):
            left, right = f'U_L{index}', f'U_R{index}'
            y = 3.7 + index * .45
            pad(self.board, left, '1', net, 2, y, .25)
            pad(self.board, right, '1', net, 8, y, .25)
            self.floorplan['placement']['post_anchors'][left] = [2, y, 0]
            self.floorplan['placement']['post_anchors'][right] = [8, y, 0]
            self.interfaces['blocks'][0]['refs'].append(left)
            self.interfaces['blocks'][1]['refs'].append(right)
            endpoints[net] = {'left': [left + '.1'], 'right': [right + '.1']}
            affected.extend([{'source_pad': left + '.1', 'native_pad': left + '.1',
                              'net': net, 'block': 'left'},
                             {'source_pad': right + '.1', 'native_pad': right + '.1',
                              'net': net, 'block': 'right'}])
        self.source['allocations'][0] = {'id': 'signal', 'coverage_nets': nets,
                                          'endpoints': endpoints,
                                          'demands': [{'id': 'qspi', 'nets': nets}]}
        self.interfaces['interfaces'] = [{'net': net, 'endpoints': endpoints[net]}
                                         for net in nets] + [self.interfaces['interfaces'][1]]
        faces = [{'block': 'left', 'region_face': 'east', 'bbox': [3.8, 4.5, 4, 5.3]},
                 {'block': 'right', 'region_face': 'west', 'bbox': [6, 4.5, 6.2, 5.3]}]
        obligation = lambda e: {'status': 'P2_REQUIRED', **e, 'corridor_id': 'qspi',
                                'region_face': 'east' if e['block'] == 'left' else 'west',
                                'layer': 'F.Cu', 'to_reservation': 'qspi_trunk'}
        corridor = {'id': 'qspi', 'owner': 'board_integration',
                    'region_id': 'board_integration_qspi', 'allocation_id': 'signal',
                    'participants': ['left', 'right'], 'faces': faces, 'layer': 'F.Cu',
                    'reference_layer': 'B.Cu', 'nets': nets,
                    'reservation_id': 'qspi_trunk', 'affected': affected,
                    'p2_obligations': [obligation(e) for e in affected],
                    'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                          'corridor_id': 'qspi', 'reference_layer': 'B.Cu',
                                          'proof': 'continuous_filled_reference'}}
        self.source['integration_corridors'] = [corridor]
        self.allocations[0] = {'id': 'signal', 'coverage_nets': nets,
                               'boundary_witnesses': [
                                   {'kind': 'integration_corridor_handoff',
                                    'corridor_id': 'qspi', 'source': e['source_pad'],
                                    'native': e['native_pad'], 'net': e['net'],
                                    'block': e['block'], 'layer': 'F.Cu',
                                    'face': 'west' if e['block'] == 'left' else 'east',
                                    'region_face': 'east' if e['block'] == 'left' else 'west',
                                    'boundary_bbox': faces[0 if e['block'] == 'left' else 1]['bbox'][:],
                                    'reservation_id': 'qspi_trunk', 'p2_obligation': obligation(e)}
                                   for e in affected],
                               'reservations': [{'id': 'qspi_trunk', 'kind': 'integration_corridor',
                                                 'corridor_id': 'qspi', 'owner': 'board_integration',
                                                 'region_id': 'board_integration_qspi', 'layer': 'F.Cu',
                                                 'bbox': [4, 3, 6, 7], 'nets': nets}]}
        return corridor

    def add_physical_cell_corridor(self):
        corridor = self.add_integration_corridor()
        self.floorplan['placement']['regions']['left'] = [0, 3, 3, 7]
        self.floorplan['placement']['regions']['left_face'] = [3, 3, 4, 7]
        self.floorplan['placement']['regions']['power'] = [0, 0, 4, 3]
        self.source['physical_cells'] = [
            {'id': 'left', 'owner_block': 'left',
             'refs': [f'U_L{i}' for i in range(6)], 'transit': False},
            {'id': 'left_face', 'owner_block': 'left',
             'refs': ['J_LEFT'], 'transit': False}]
        corridor['faces'][0]['physical_cell_id'] = 'left_face'
        for obligation in corridor['p2_obligations']:
            if obligation['block'] == 'left':
                obligation['physical_cell_id'] = 'left_face'
        for witness in self.allocations[0]['boundary_witnesses']:
            if witness['block'] == 'left':
                witness['physical_cell_id'] = 'left_face'
                witness['p2_obligation']['physical_cell_id'] = 'left_face'
        return corridor

    def add_fixed_connector_access(self):
        corridor = self.add_integration_corridor()
        self.source['p1_fixed_refs'].append('U_L0')
        corridor['faces'][0]['bbox'] = [3.8, 4.25, 4, 5.2]
        for item in self.allocations[0]['boundary_witnesses']:
            if item['block'] == 'left':
                item['boundary_bbox'] = corridor['faces'][0]['bbox'][:]
        # Keep all other synthetic endpoints clear of the fixed physical
        # access rectangle.  They retain virtual corridor handoffs.
        for index in range(1, 6):
            ref = f'U_L{index}'
            fp = next(f for f in self.board.GetFootprints() if f.GetReference() == ref)
            fp.SetPosition(pcbnew.VECTOR2I(iu(1), iu(3.7 + index * .45)))
            self.floorplan['placement']['post_anchors'][ref] = [1, 3.7 + index * .45, 0]
        witness = next(w for w in self.allocations[0]['boundary_witnesses']
                       if w['source'] == 'U_L0.1')
        witness.update(kind='fixed_connector_access', face='west',
                       boundary_bbox=[1.875, 3.575, 2.125, 3.825],
                       reservation_id='fixed_left_access')
        self.allocations[0]['reservations'].append({
            'id': 'fixed_left_access', 'kind': 'fixed_connector_access',
            'corridor_id': 'qspi', 'layer': 'F.Cu',
            'bbox': [2.125, 3.55, 4, 4.5], 'nets': ['QSPI_CLK']})
        return witness

    def add_segmented_fixed_access(self):
        witness = self.add_fixed_connector_access()
        witness['kind'] = 'fixed_connector_access_segmented'
        access = self.allocations[0]['reservations'][-1]
        access['kind'] = 'fixed_connector_access_segmented'
        access['bbox'] = [2.125, 3.575, 4, 4.4]
        access['segments'] = [[2.125, 3.575, 2.5, 3.825],
                              [2.3, 3.825, 2.5, 4.4],
                              [2.5, 4.2, 4, 4.4]]
        return witness, access

    def add_second_segmented_fixed_access(self):
        self.add_segmented_fixed_access()
        self.source['p1_fixed_refs'].append('U_L1')
        witness = next(w for w in self.allocations[0]['boundary_witnesses']
                       if w['source'] == 'U_L1.1')
        witness.update(kind='fixed_connector_access_segmented', face='west',
                       boundary_bbox=[.875, 4.025, 1.125, 4.275],
                       reservation_id='fixed_left_access_1')
        access = {'id': 'fixed_left_access_1', 'kind': 'fixed_connector_access_segmented',
                  'corridor_id': 'qspi', 'layer': 'F.Cu',
                  'bbox': [1.125, 4.025, 4, 4.65], 'nets': ['QSPI_CS_N'],
                  'segments': [[1.125, 4.025, 1.5, 4.275],
                               [1.3, 4.275, 1.5, 4.65],
                               [1.5, 4.45, 4, 4.65]]}
        self.allocations[0]['reservations'].append(access)
        return access

    def test_segmented_fixed_access_bypasses_envelope_obstacle_without_credit(self):
        self.add_segmented_fixed_access()
        pad(self.board, 'U_BLOCK', '1', 'OTHER', 3, 3.9, .2)
        self.source['p1_fixed_refs'].append('U_BLOCK')
        self.floorplan['placement']['post_anchors']['U_BLOCK'] = [3, 3.9, 0]
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['p1_accepted'])
        reservation = result['allocations'][0]['reservations'][-1]
        self.assertEqual(reservation['status'], 'INCOMPLETE')
        self.assertNotIn('capacity_slots', reservation)

    def test_segmented_fixed_access_peers_can_share_only_their_envelopes(self):
        self.add_second_segmented_fixed_access()
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')

    def test_segmented_fixed_access_peers_reject_actual_segment_overlap(self):
        self.add_second_segmented_fixed_access()
        access = self.allocations[0]['reservations'][-2]
        access['segments'][2][3] = 4.6
        access['bbox'][3] = 4.6
        self.assertIn('fixed access overlaps other reservation',
                      self.run_case()['allocations'][0]['reason'])

    def test_segmented_fixed_access_rejects_waypoint_and_native_obstacles(self):
        _, access = self.add_segmented_fixed_access()
        original = [part[:] for part in access['segments']]
        access['segments'][1][1] = 3.9
        self.assertIn('disconnected or overlapping waypoints',
                      self.run_case()['allocations'][0]['reason'])
        access['segments'] = [part[:] for part in original]
        access['segments'][2][2] = 3.9
        access['bbox'][2] = 3.9
        self.assertIn('does not contact integration corridor',
                      self.run_case()['allocations'][0]['reason'])
        access['segments'] = [part[:] for part in original]
        access['bbox'][2] = 4
        pad(self.board, 'U_BLOCK', '1', 'OTHER', 3, 4.3, .2)
        self.source['p1_fixed_refs'].append('U_BLOCK')
        self.floorplan['placement']['post_anchors']['U_BLOCK'] = [3, 4.3, 0]
        self.assertIn('fixed access intersects native body U_BLOCK',
                      self.run_case()['allocations'][0]['reason'])

    def test_segmented_fixed_access_rejects_false_envelope_and_wrong_denominator(self):
        witness, access = self.add_segmented_fixed_access()
        access['bbox'][0] = 2.0
        self.assertIn('bbox differs from segment envelope',
                      self.run_case()['allocations'][0]['reason'])
        access['bbox'][0] = 2.125
        witness['source'] = 'U_L1.1'
        self.assertIn('witness source/block ownership mismatch',
                      self.run_case()['allocations'][0]['reason'])

    def test_segmented_fixed_access_requires_the_actual_pad_boundary(self):
        witness, _ = self.add_segmented_fixed_access()
        # This enlarged declaration used to let the first segment leave an
        # invented face at x=2.125 instead of the U_L0.1 pad at x=2.125.
        witness['boundary_bbox'][0] = 1.5
        self.assertIn('boundary is not the physical pad',
                      self.run_case()['allocations'][0]['reason'])

    def test_segmented_fixed_access_allows_unfilled_copper_zone(self):
        self.add_segmented_fixed_access()
        zone = pcbnew.ZONE(self.board)
        zone.SetLayer(pcbnew.F_Cu)
        polygon = zone.Outline()
        polygon.NewOutline()
        for x, y in ((2.8, 4.25), (3.1, 4.25), (3.1, 4.35), (2.8, 4.35)):
            polygon.Append(pcbnew.VECTOR2I(iu(x), iu(y)))
        self.board.Add(zone)
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')

    def test_segmented_fixed_access_rejects_saved_filled_copper_zone(self):
        self.add_segmented_fixed_access()
        zone = pcbnew.ZONE(self.board)
        zone.SetLayer(pcbnew.F_Cu)
        polygon = zone.Outline()
        polygon.NewOutline()
        filled = pcbnew.SHAPE_POLY_SET()
        filled.NewOutline()
        for x, y in ((2.8, 4.25), (3.1, 4.25), (3.1, 4.35), (2.8, 4.35)):
            point = pcbnew.VECTOR2I(iu(x), iu(y))
            polygon.Append(point)
            filled.Append(point)
        zone.SetFilledPolysList(pcbnew.F_Cu, filled)
        self.board.Add(zone)
        self.assertIn('fixed access intersects existing copper',
                      self.run_case()['allocations'][0]['reason'])

    def test_segmented_fixed_access_rejects_native_rule_area(self):
        self.add_segmented_fixed_access()
        zone = pcbnew.ZONE(self.board)
        zone.SetIsRuleArea(True)
        zone.SetLayer(pcbnew.F_Cu)
        polygon = zone.Outline()
        polygon.NewOutline()
        for x, y in ((2.8, 4.25), (3.1, 4.25), (3.1, 4.35), (2.8, 4.35)):
            polygon.Append(pcbnew.VECTOR2I(iu(x), iu(y)))
        self.board.Add(zone)
        self.assertIn('fixed access overlaps immutable native rule area',
                      self.run_case()['allocations'][0]['reason'])

    def test_segmented_fixed_access_rejects_competing_reservation(self):
        self.add_segmented_fixed_access()
        self.allocations[0]['reservations'].append({
            'id': 'competing', 'kind': 'signal', 'layer': 'F.Cu',
            'bbox': [2.8, 4.25, 3.1, 4.35], 'axis': 'horizontal',
            'nets': ['QSPI_CLK'], 'demand_slots': 1, 'slot_pitch_mm': .5})
        self.assertIn('fixed access overlaps other reservation',
                      self.run_case()['allocations'][0]['reason'])

    def test_fixed_connector_access_preserves_native_pad_and_corridor_debt(self):
        self.add_fixed_connector_access()
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['p1_accepted'])
        self.assertEqual(result['allocations'][0]['reservations'][-1]['status'], 'INCOMPLETE')

    def test_fixed_connector_access_requires_physical_cell_in_p2_debt(self):
        witness = self.add_fixed_connector_access()
        self.floorplan['placement']['regions']['power'] = [0, 0, 4, 3]
        self.source['physical_cells'] = [
            {'id': 'left', 'owner_block': 'left',
             'refs': ['J_LEFT'] + [f'U_L{i}' for i in range(6)], 'transit': False}]
        corridor = self.source['integration_corridors'][0]
        corridor['faces'][0]['physical_cell_id'] = 'left'
        for obligation in corridor['p2_obligations']:
            if obligation['block'] == 'left':
                obligation['physical_cell_id'] = 'left'
        for candidate in self.allocations[0]['boundary_witnesses']:
            if candidate['block'] == 'left':
                candidate['physical_cell_id'] = 'left'
                candidate['p2_obligation']['physical_cell_id'] = 'left'
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')
        witness['p2_obligation'].pop('physical_cell_id')
        self.assertIn('fixed access P2 pad-to-corridor obligation missing',
                      self.run_case()['allocations'][0]['reason'])

    def test_fixed_connector_access_rejects_movable_or_wrong_pad(self):
        witness = self.add_fixed_connector_access()
        self.source['p1_fixed_refs'].remove('U_L0')
        result = self.run_case()
        self.assertIn('fixed access requires P1-fixed ref', result['allocations'][0]['reason'])
        self.source['p1_fixed_refs'].append('U_L0')
        witness['boundary_bbox'] = [2.5, 3.575, 2.75, 3.825]
        result = self.run_case()
        self.assertIn('boundary is not the physical pad', result['allocations'][0]['reason'])

    def test_fixed_connector_access_rejects_detached_or_wrong_corridor(self):
        witness = self.add_fixed_connector_access()
        access = self.allocations[0]['reservations'][-1]
        access['bbox'] = [2.125, 3.55, 3.9, 4.5]
        result = self.run_case()
        self.assertIn('does not join source face', result['allocations'][0]['reason'])
        access['bbox'] = [2.125, 3.55, 4, 4.5]
        witness['corridor_id'] = 'missing'
        result = self.run_case()
        self.assertIn('undeclared fixed access corridor', result['allocations'][0]['reason'])

    def test_fixed_connector_access_rejects_other_reservation_overlap(self):
        self.add_fixed_connector_access()
        self.allocations[0]['reservations'].append({
            'id': 'competing', 'kind': 'signal', 'layer': 'F.Cu',
            'bbox': [3, 3.6, 3.5, 4.4], 'axis': 'horizontal',
            'nets': ['QSPI_CLK'], 'demand_slots': 1, 'slot_pitch_mm': .5})
        result = self.run_case()
        self.assertIn('fixed access overlaps other reservation',
                      result['allocations'][0]['reason'])

    def test_fixed_access_skips_only_declared_geometry_free_branch(self):
        branch = {'id': 'reset_tree', 'reservation_id': 'reset_unplaced',
                  'net': 'RESET', 'layer': 'F.Cu'}
        reservation = {'id': 'reset_unplaced', 'kind': 'unresolved_multiterminal_branch',
                       'branch_id': 'reset_tree', 'layer': 'F.Cu', 'nets': ['RESET']}
        self.assertTrue(checker._is_geometry_free_branch_reservation(
            reservation, {'reset_tree': branch}))
        for extra in ({'bbox': [3, 3, 4, 4]}, {'segments': [[3, 3, 4, 4]]},
                      {'capacity_slots': 1}, {'demand_slots': 1}):
            with self.subTest(extra=extra):
                with self.assertRaisesRegex(checker.ContractError,
                                            'cannot reserve geometry/capacity'):
                    checker._is_geometry_free_branch_reservation(
                        {**reservation, **extra}, {'reset_tree': branch})
        with self.assertRaisesRegex(checker.ContractError,
                                    'cannot reserve geometry/capacity'):
            checker._is_geometry_free_branch_reservation(reservation, {})

    def test_fixed_connector_access_rejects_native_pad_obstacle(self):
        self.add_fixed_connector_access()
        pad(self.board, 'U_BLOCK', '1', 'OTHER', 3, 4, .2)
        self.source['p1_fixed_refs'].append('U_BLOCK')
        self.floorplan['placement']['post_anchors']['U_BLOCK'] = [3, 4, 0]
        result = self.run_case()
        self.assertIn('fixed access intersects native body U_BLOCK',
                      result['allocations'][0]['reason'])

    def test_fixed_connector_access_rejects_courtyard_only_obstacle(self):
        for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            with self.subTest(layer=layer):
                self.setUp()
                self.add_fixed_connector_access()
                pad(self.board, 'U_BLOCK', '1', 'OTHER', 1, 3.7, .2)
                self.source['p1_fixed_refs'].append('U_BLOCK')
                self.floorplan['placement']['post_anchors']['U_BLOCK'] = [1, 3.7, 0]
                fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'U_BLOCK')
                access = self.allocations[0]['reservations'][-1]['bbox']
                self.assertFalse(checker.intersects(
                    checker.box_mm(fp.GetBoundingBox(False, False)), access))
                points = [(3, 3.6), (3.2, 3.6), (3.2, 3.8), (3, 3.8)]
                for start, end in zip(points, points[1:] + points[:1]):
                    edge = pcbnew.PCB_SHAPE(fp)
                    edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
                    edge.SetStart(pcbnew.VECTOR2I(iu(start[0]), iu(start[1])))
                    edge.SetEnd(pcbnew.VECTOR2I(iu(end[0]), iu(end[1])))
                    edge.SetLayer(layer)
                    edge.SetWidth(iu(.05))
                    fp.Add(edge)
                self.assertTrue(checker.intersects(checker._physical_envelope(fp), access))
                result = self.run_case()
                self.assertIn('fixed access intersects native body U_BLOCK',
                              result['allocations'][0]['reason'])

    def test_integration_corridor_is_declared_debt_without_capacity_credit(self):
        self.add_integration_corridor()
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['p1_accepted'])
        reservation = result['allocations'][0]['reservations'][0]
        self.assertEqual(reservation['status'], 'INCOMPLETE')
        self.assertNotIn('potential_slots', reservation)
        self.assertEqual(len(result['allocations'][0]['p2_obligations']), 12)

    def test_physical_cells_keep_modular_endpoint_owner_and_debt(self):
        self.add_physical_cell_corridor()
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['p1_accepted'])
        self.assertEqual(len(result['allocations'][0]['p2_obligations']), 12)

    def test_physical_cell_rejects_missing_and_wrong_face_binding(self):
        corridor = self.add_physical_cell_corridor()
        corridor['faces'][0].pop('physical_cell_id')
        self.assertIn('physical cell identity missing', self.run_case()['errors'][0])
        self.setUp()
        corridor = self.add_physical_cell_corridor()
        corridor['faces'][0]['physical_cell_id'] = 'right'
        self.assertIn('physical cell owner mismatch', self.run_case()['errors'][0])
        self.setUp()
        self.add_physical_cell_corridor()
        self.allocations[0]['boundary_witnesses'][0].pop('physical_cell_id')
        result = self.run_case()
        self.assertIn('physical cell identity missing', result['allocations'][0]['reason'])

    def test_physical_cell_rejects_wrong_modular_owner_and_ref_denominator(self):
        self.add_physical_cell_corridor()
        self.source['physical_cells'][1]['owner_block'] = 'right'
        self.assertIn('ref ownership', self.run_case()['errors'][0])
        self.setUp()
        self.add_physical_cell_corridor()
        self.source['physical_cells'][0]['refs'].pop()
        self.assertIn('unassigned native footprint/pad U_L5', self.run_case()['errors'][0])
        self.setUp()
        self.add_physical_cell_corridor()
        self.source['physical_cells'][1]['refs'].append('U_L0')
        self.assertIn('ref ownership/uniqueness mismatch', self.run_case()['errors'][0])
        self.setUp()
        self.add_physical_cell_corridor()
        self.allocations[0]['boundary_witnesses'][0]['block'] = 'left_face'
        self.assertIn('source/block ownership mismatch',
                      self.run_case()['allocations'][0]['reason'])

    def test_physical_cell_rejects_overlap_and_foreign_region(self):
        self.add_physical_cell_corridor()
        self.floorplan['placement']['regions']['left_face'] = [2.9, 3, 4, 7]
        self.assertIn('physical cells overlap', self.run_case()['errors'][0])
        self.setUp()
        self.add_physical_cell_corridor()
        self.floorplan['placement']['regions']['foreign'] = [3.5, 6, 4.5, 6.5]
        self.assertIn('physical cell overlaps foreign region', self.run_case()['errors'][0])

    def test_physical_cell_rejects_disconnected_transit(self):
        self.add_physical_cell_corridor()
        self.floorplan['placement']['regions']['isolated'] = [8, 0, 9, 1]
        self.source['physical_cells'].append(
            {'id': 'isolated', 'owner_block': 'left', 'refs': [], 'transit': True})
        self.assertIn('physical transit cell disconnected', self.run_case()['errors'][0])

    def test_physical_cell_rejects_unassigned_native_occupant_and_pattern_drift(self):
        self.add_physical_cell_corridor()
        pad(self.board, 'U_FOREIGN', '1', 'OTHER', 3.5, 6)
        self.floorplan['placement']['post_anchors']['U_FOREIGN'] = [3.5, 6, 0]
        self.assertIn('unassigned native footprint/pad U_FOREIGN', self.run_case()['errors'][0])
        self.setUp()
        self.add_physical_cell_corridor()
        self.floorplan['placement']['patterns'].append(
            {'match': ['J_LEFT'], 'region': 'left'})
        self.assertIn('floorplan pattern disagrees', self.run_case()['errors'][0])

    def test_integration_corridor_missing_return_or_endpoint_fails(self):
        row = self.add_integration_corridor()
        row.pop('return_obligation')
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('filled-reference return obligation missing', result['errors'][0])
        self.setUp()
        row = self.add_integration_corridor()
        row['affected'].pop()
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('endpoint denominator mismatch', result['errors'][0])

    def test_integration_corridor_corner_and_owner_mismatch_fail(self):
        row = self.add_integration_corridor()
        row['faces'][0]['bbox'] = [3.8, 3, 4, 3.5]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('non-corner shared edge', result['errors'][0])
        self.setUp()
        row = self.add_integration_corridor()
        row['owner'] = 'left'
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('identity/owner/region invalid', result['errors'][0])

    def test_integration_corridor_native_hit_and_double_credit_fail(self):
        self.add_integration_corridor()
        pad(self.board, 'J_HIT', '1', 'OTHER', 5, 5)
        self.floorplan['placement']['post_anchors']['J_HIT'] = [5, 5, 0]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('native footprint/pad', result['errors'][0])
        self.setUp()
        self.add_integration_corridor()
        self.allocations[0]['reservations'].append({'id': 'second', 'kind': 'signal',
                                                      'layer': 'F.Cu', 'bbox': [7, 7, 9, 9],
                                                      'nets': ['QSPI_CLK'], 'axis': 'horizontal',
                                                      'demand_slots': 1, 'slot_pitch_mm': .5})
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('double reservation credit', ' '.join(result['errors']))

    def test_integration_corridor_partial_demand_and_claimed_pass_fail(self):
        row = self.add_integration_corridor()
        row['nets'] = row['nets'][:-1]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('partial or undeclared source demand', result['errors'][0])
        self.setUp()
        self.add_integration_corridor()
        self.allocations[0]['reservations'][0]['status'] = 'PASS'
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('source mismatch', result['allocations'][0]['reason'])

    def test_integration_corridor_reused_id_and_wrong_witness_fail(self):
        self.add_integration_corridor()
        self.allocations[1]['reservations'][0]['id'] = 'qspi_trunk'
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('duplicate global reservation id', result['errors'][0])
        self.setUp()
        self.add_integration_corridor()
        self.allocations[0]['boundary_witnesses'][0]['block'] = 'right'
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('ownership mismatch', result['allocations'][0]['reason'])

    def test_integration_corridor_shared_port_reservation_id_collision_fails(self):
        self.add_integration_corridor()
        port = {'id': 'elsewhere', 'reservation_id': 'qspi_trunk',
                'bbox': (0.1, .1, .2, .2), 'reservation_bbox': (.1, .1, .2, .2),
                'zone_rectangles': [(0.1, .1, .2, .2)]}
        with patch.object(checker, '_shared_ports', return_value={'elsewhere': port}):
            result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('shared port/integration corridor reservation identity reused', result['errors'][0])

    def test_integration_corridor_native_track_hit_fails(self):
        self.add_integration_corridor()
        track = pcbnew.PCB_TRACK(self.board)
        track.SetStart(pcbnew.VECTOR2I(iu(4.5), iu(5)))
        track.SetEnd(pcbnew.VECTOR2I(iu(5.5), iu(5)))
        track.SetWidth(iu(.2))
        track.SetLayer(pcbnew.B_Cu)
        self.board.Add(track)
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('native copper intersects', result['errors'][0])

    def test_integration_corridor_ignores_movable_reference_text_not_body(self):
        self.add_integration_corridor()
        fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'U_L0')
        fp.Reference().SetVisible(True)
        fp.Reference().SetPosition(pcbnew.VECTOR2I(iu(5), iu(5)))
        fp.Value().SetVisible(True)
        fp.Value().SetPosition(pcbnew.VECTOR2I(iu(5), iu(5)))
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')

    def test_integration_corridor_non_text_graphic_hit_fails(self):
        self.add_integration_corridor()
        fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'U_L0')
        graphic = pcbnew.PCB_SHAPE(fp)
        graphic.SetShape(pcbnew.SHAPE_T_SEGMENT)
        graphic.SetStart(pcbnew.VECTOR2I(iu(4.5), iu(5)))
        graphic.SetEnd(pcbnew.VECTOR2I(iu(5.5), iu(5)))
        graphic.SetLayer(pcbnew.F_SilkS)
        fp.Add(graphic)
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('native footprint/pad', result['errors'][0])

    def test_integration_corridor_courtyard_only_intrusion_fails(self):
        for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            with self.subTest(layer=layer):
                self.setUp()
                self.add_integration_corridor()
                fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'U_L0')
                corridor = (4, 3, 6, 7)
                self.assertFalse(checker.intersects(
                    checker.box_mm(fp.GetBoundingBox(False, False)), corridor))
                self.assertTrue(all(not checker.intersects(
                    checker.box_mm(pad.GetBoundingBox()), corridor) for pad in fp.Pads()))
                points = [(4.5, 4.5), (5.5, 4.5), (5.5, 5.5), (4.5, 5.5)]
                for start, end in zip(points, points[1:] + points[:1]):
                    edge = pcbnew.PCB_SHAPE(fp)
                    edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
                    edge.SetStart(pcbnew.VECTOR2I(iu(start[0]), iu(start[1])))
                    edge.SetEnd(pcbnew.VECTOR2I(iu(end[0]), iu(end[1])))
                    edge.SetLayer(layer)
                    edge.SetWidth(iu(.05))
                    fp.Add(edge)
                self.assertGreater(fp.GetCourtyard(layer).OutlineCount(), 0)
                result = self.run_case()
                self.assertEqual(result['status'], 'FAIL')
                self.assertIn('native footprint/pad U_L0 intersects integration corridor/face',
                              result['errors'][0])

    def test_integration_corridor_courtyard_stroke_only_near_edge_fails(self):
        self.add_integration_corridor()
        fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'U_L0')
        corridor = (4, 3, 6, 7)
        pads = list(fp.Pads())
        self.assertEqual(len(pads), 1)
        self.assertFalse(checker.intersects(checker.box_mm(pads[0].GetBoundingBox()), corridor))
        # The contour stops 0.01 mm before the corridor. Its 0.05 mm native
        # stroke extends 0.015 mm inside; vertices alone miss the violation.
        points = [(3.5, 4.5), (3.99, 4.5), (3.99, 5.5), (3.5, 5.5)]
        for start, end in zip(points, points[1:] + points[:1]):
            edge = pcbnew.PCB_SHAPE(fp)
            edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
            edge.SetStart(pcbnew.VECTOR2I(iu(start[0]), iu(start[1])))
            edge.SetEnd(pcbnew.VECTOR2I(iu(end[0]), iu(end[1])))
            edge.SetLayer(pcbnew.F_CrtYd)
            edge.SetWidth(iu(.05))
            fp.Add(edge)
        courtyard = fp.GetCourtyard(pcbnew.F_CrtYd)
        self.assertGreater(courtyard.OutlineCount(), 0)
        rightmost_vertex = max(pcbnew.ToMM(courtyard.COutline(i).CPoint(k).x)
                               for i in range(courtyard.OutlineCount())
                               for k in range(courtyard.COutline(i).PointCount()))
        self.assertLess(rightmost_vertex, corridor[0])
        self.assertTrue(checker.intersects(checker.box_mm(courtyard.BBox()), corridor))

        class BodyOnly:
            def GetBoundingBox(self, *_):
                return pads[0].GetBoundingBox()

            def GetCourtyard(self, layer):
                return fp.GetCourtyard(layer)

        self.assertTrue(checker.intersects(checker._physical_envelope(BodyOnly()), corridor))
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('native footprint/pad U_L0 intersects integration corridor/face',
                      result['errors'][0])

    def test_two_terminal_crossing_full_allocation_stays_no_credit(self):
        entries = [{'source_pad':s, 'native_pad':s, 'net':'TEST', 'block':block}
                   for s, block in [('J_LEFT.1','left'), ('J_RIGHT.1','right')]]
        duties = [{'status':'P2_REQUIRED', **entry, 'branch_id':'two',
                   'layer':'F.Cu', 'proof':'native_pad_to_unplaced_tree'}
                  for entry in entries]
        row = {'id':'two', 'owner':'board_integration', 'allocation_id':'signal',
               'net':'TEST', 'layer':'F.Cu', 'reference_layer':'B.Cu',
               'reservation_id':'two_reservation', 'endpoints':entries,
               'terminal_count':2, 'minimum_tree_edges':1,
               'physical_blockers':[], 'capacity_slots':None,
               'p2_obligations':duties,
               'tree_obligation':{'status':'P3_REQUIRED', 'net':'TEST',
                                  'terminal_count':2, 'minimum_tree_edges':1,
                                  'proof':'one_connected_native_net_without_unrelated_branches'},
               'return_obligation':{'status':'P2_REQUIRED', 'net':'GND',
                                    'branch_id':'two', 'reference_layer':'B.Cu',
                                    'proof':'continuous_filled_reference_under_actual_tree'}}
        self.source['unresolved_two_terminal_crossings'] = [row]
        self.allocations[0]['boundary_witnesses'] = [{
            'kind':'unresolved_two_terminal_crossing', 'branch_id':'two',
            'source':'J_LEFT.1', 'native':'J_LEFT.1', 'net':'TEST', 'block':'left',
            'layer':'F.Cu', 'face':'west', 'boundary_bbox':[3.25,4.75,3.75,5.25],
            'reservation_id':'two_reservation', 'p2_obligation':duties[0]}]
        self.allocations[0]['reservations'] = [{
            'id':'two_reservation', 'kind':'unresolved_two_terminal_crossing',
            'branch_id':'two', 'layer':'F.Cu', 'nets':['TEST']}]
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertFalse(result['p1_accepted'])
        measured = result['allocations'][0]['reservations'][0]
        self.assertEqual(measured['status'], 'INCOMPLETE')
        self.assertIsNone(measured['capacity_slots'])
        self.assertEqual(len(measured['p2_obligations']), 2)
        self.allocations[0]['reservations'][0]['demand_slots'] = 1
        damaged = self.run_case()
        self.assertEqual(damaged['status'], 'FAIL')
        self.assertIn('two-terminal reservation fields invalid',
                      damaged['allocations'][0]['reason'])
        del self.allocations[0]['reservations'][0]['demand_slots']
        self.allocations[0]['reservations'][0]['status'] = 'PASS'
        self.assertIn('two-terminal reservation fields invalid',
                      self.run_case()['allocations'][0]['reason'])
        del self.allocations[0]['reservations'][0]['status']
        self.allocations[0]['boundary_witnesses'][0]['capacity_slots'] = 1
        self.assertIn('two-terminal witness fields invalid',
                      self.run_case()['allocations'][0]['reason'])

    def run_case(self, change=None, *, diagnose_all=False):
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
                                expected_floorplan_sha256=hashes['floorplan.yaml'],
                                diagnose_all=diagnose_all)

    def test_diagnostic_mode_collects_independent_items_without_changing_verdict(self):
        self.allocations[0]['boundary_witnesses'][0]['boundary_bbox'] = [0, 4.5, 4, 5.5]
        self.allocations[1]['boundary_witnesses'][0]['boundary_bbox'] = [0, 0, 3, 3]
        self.allocations[0]['reservations'][0]['bbox'] = [0, 0, 11, 2]
        self.allocations[1]['reservations'][0]['bbox'] = [0, 0, 12, 2]
        normal = self.run_case()
        detailed = self.run_case(diagnose_all=True)
        self.assertNotIn('diagnostics', normal)
        self.assertEqual({k: v for k, v in detailed.items() if k != 'diagnostics'}, normal)
        self.assertEqual({(d['allocation'], d['kind']) for d in detailed['diagnostics']},
                         {('signal', 'boundary_witness'), ('power_boundary_windows', 'boundary_witness'),
                          ('signal', 'reservation'), ('power_boundary_windows', 'reservation')})
        self.assertEqual(len(detailed['diagnostics']), 4)
        self.assertTrue(all(d['reason'] for d in detailed['diagnostics']))

    def test_diagnostic_mode_clean_fixture_has_no_local_errors(self):
        result = self.run_case(diagnose_all=True)
        self.assertEqual(result['diagnostics'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')

    def test_check_only_replays_without_rewriting_historical_receipt(self):
        expected = self.run_case()
        self.assertEqual(expected['status'], 'INCOMPLETE')
        self.assertFalse(expected['p1_accepted'])
        self.assertIn('independent P1 engineering review', expected['unproved_by_screen'])
        paths = {name: self.root / name for name in
                 ('board.kicad_pcb', 'contract.json', 'source.yaml', 'interfaces.json',
                  'aliases.yaml', 'floorplan.yaml')}
        historical = self.root / 'historical_failed_receipt.json'
        historical.write_bytes(b'{"status":"FAILED_RESEARCH"}\n')
        before = historical.read_bytes()
        files_before_replay = set(self.root.iterdir())
        command = [sys.executable, str(Path(checker.__file__)),
                   str(paths['board.kicad_pcb']), str(paths['contract.json']),
                   '--check-only', '--expected-contract-sha256', checker.digest(paths['contract.json']),
                   '--source-requirements', str(paths['source.yaml']),
                   '--interfaces', str(paths['interfaces.json']),
                   '--aliases', str(paths['aliases.yaml']),
                   '--floorplan', str(paths['floorplan.yaml']),
                   '--expected-source-sha256', checker.digest(paths['source.yaml']),
                   '--expected-interface-sha256', checker.digest(paths['interfaces.json']),
                   '--expected-alias-sha256', checker.digest(paths['aliases.yaml']),
                   '--expected-floorplan-sha256', checker.digest(paths['floorplan.yaml'])]
        replay = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(replay.returncode, 1, replay.stderr)
        self.assertEqual(json.loads(replay.stdout), expected)
        self.assertEqual(historical.read_bytes(), before)
        self.assertEqual(set(self.root.iterdir()), files_before_replay)

        ordinary = self.root / 'ordinary_receipt.json'
        saved = subprocess.run(command[:4] + [str(ordinary)] + command[5:],
                               capture_output=True, text=True)
        self.assertEqual(saved.returncode, replay.returncode, saved.stderr)
        self.assertEqual(ordinary.read_text(), replay.stdout)

        with_output = subprocess.run(command[:4] + [str(historical)] + command[4:],
                                     capture_output=True, text=True)
        self.assertEqual(with_output.returncode, 2)
        self.assertIn('output must be omitted', with_output.stderr)
        self.assertEqual(historical.read_bytes(), before)

        # Independent expected digests reject a source edit even if the old
        # contract and the historical receipt are left in place.
        paths['source.yaml'].write_text(paths['source.yaml'].read_text() + '\n# changed\n')
        stale = subprocess.run(command, capture_output=True, text=True)
        self.assertNotEqual(stale.returncode, 0)
        stale_result = json.loads(stale.stdout)
        self.assertFalse(stale_result['p1_accepted'])
        self.assertIn('source not bound to independent expected digest', stale_result['errors'])
        self.assertEqual(historical.read_bytes(), before)

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
        result = self.run_case(lambda: self.allocations[0]['reservations'][0].update(bbox=[4, 4, 10.5, 6]))
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

    def test_shared_port_is_source_bound_and_never_claims_capacity(self):
        self.add_shared_port()
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['allocations'][0]['witness_count'], 2)
        self.assertNotIn('potential_slots', result['allocations'][0]['reservations'][0])
        self.assertFalse(result['routing_realized'])
        self.assertFalse(result['p1_accepted'])

    def test_power_shared_port_cannot_replace_full_net_with_one_pad(self):
        port, _ = self.add_shared_port()
        outline = pcbnew.SHAPE_POLY_SET()
        self.assertTrue(self.board.GetBoardPolygonOutlines(outline, False))
        _, pads = checker.graph.board_index(self.board)
        args = (self.interfaces, self.board, outline,
                self.floorplan['placement']['regions'], list(self.board.Zones()),
                {'power_boundary_windows': {'TEST'}}, {}, pads)
        # The same local affected subset remains valid for a signal port.
        self.assertIn('joint', checker._shared_ports(self.source, *args))
        power_source = dict(self.source, power_boundary_windows={'coverage_nets': ['TEST']})
        with self.assertRaisesRegex(checker.ContractError,
                                    'power port exact endpoint denominator missing for TEST'):
            checker._shared_ports(power_source, *args)
        # Merely listing the other modular pad is insufficient if native
        # copper has an additional undeclared terminal on that power net.
        second = {'source_pad': 'J_LEFT.1', 'native_pad': 'J_LEFT.1',
                  'net': 'TEST', 'block': 'left'}
        port['affected'].append(second)
        port['p2_obligations'].append({'status': 'P2_REQUIRED', **second,
                                      'port_id': 'joint', 'layer': 'F.Cu',
                                      'to_reservation': 'signal_main'})
        pad(self.board, 'J_EXTRA', '1', 'TEST', 9, 9)
        _, pads = checker.graph.board_index(self.board)
        with self.assertRaisesRegex(checker.ContractError,
                                    'native net pad multiset mismatch'):
            checker._shared_ports(power_source, *args[:-1], pads)

    def test_shared_port_witness_requires_named_source_record(self):
        self.add_shared_port()
        self.source.pop('shared_transition_ports')
        result = self.run_case()
        self.assertIn('undeclared shared transition port', result['allocations'][0]['reason'])

    def test_shared_port_rejects_undeclared_endpoint_layer_and_scope(self):
        port, witness = self.add_shared_port()
        witness['net'] = 'GND'
        result = self.run_case()
        self.assertIn('net outside allocation', result['allocations'][0]['reason'])
        self.setUp()
        port, witness = self.add_shared_port()
        port['affected'][0]['block'] = 'left'
        result = self.run_case()
        self.assertIn('exact source owner', '\n'.join(result['errors']))
        self.setUp()
        port, witness = self.add_shared_port()
        witness['layer'] = 'B.Cu'
        result = self.run_case()
        self.assertIn('face/layer/geometry mismatch', result['allocations'][0]['reason'])
        self.setUp()
        port, witness = self.add_shared_port()
        self.allocations[0]['reservations'][0]['bbox'] = [4, 3.9, 6.2, 6]
        result = self.run_case()
        self.assertIn('outside declared shared port scope', result['allocations'][0]['reason'])

    def test_shared_port_rejects_foreign_region_footprint_and_port_collision(self):
        port, witness = self.add_shared_port()
        self.floorplan['placement']['regions']['intruder'] = [5, 4, 5.5, 5]
        result = self.run_case()
        self.assertIn('unowned overlap', '\n'.join(result['errors']))
        self.setUp()
        port, witness = self.add_shared_port()
        self.interfaces['blocks'][1]['refs'].remove('R_MOVE')
        result = self.run_case()
        self.assertIn('foreign footprint R_MOVE', '\n'.join(result['errors']))
        self.setUp()
        port, witness = self.add_shared_port()
        port['bbox'] = [5.5, 4.5, 6, 5]
        witness['boundary_bbox'] = port['bbox'][:]
        result = self.run_case()
        self.assertIn('native footprint/pad R_MOVE', '\n'.join(result['errors']))

    def test_shared_port_rejects_off_outline_and_missing_return(self):
        port, witness = self.add_shared_port()
        port['geometry']['rectangles'][1] = [6, 3, 11, 7]
        result = self.run_case()
        self.assertIn('off board outline', '\n'.join(result['errors']))
        self.setUp()
        port, witness = self.add_shared_port()
        port.pop('return_obligation')
        result = self.run_case()
        self.assertIn('filled-reference return obligation missing', '\n'.join(result['errors']))

    def test_shared_port_rejects_native_rule_area_and_p2_obligation_drift(self):
        self.add_shared_port()
        zone = pcbnew.ZONE(self.board)
        zone.SetIsRuleArea(True)
        zone.SetLayer(pcbnew.F_Cu)
        polygon = zone.Outline()
        polygon.NewOutline()
        for x, y in ((6.1, 4.1), (6.6, 4.1), (6.6, 4.7), (6.1, 4.7)):
            polygon.Append(pcbnew.VECTOR2I(iu(x), iu(y)))
        self.board.Add(zone)
        result = self.run_case()
        self.assertIn('immutable native rule area intersects shared zone/port', '\n'.join(result['errors']))
        self.setUp()
        port, witness = self.add_shared_port()
        witness['p2_obligation']['port_id'] = 'other'
        result = self.run_case()
        self.assertIn('P2 pad-to-port obligation missing', result['allocations'][0]['reason'])

    def test_shared_port_rejects_scope_outside_zone_and_zone_only_rule_area(self):
        port, witness = self.add_shared_port()
        port['reservation_bbox'] = [4, 4, 8.5, 6]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('reservation scope outside declared zone', '\n'.join(result['errors']))
        self.setUp()
        self.add_shared_port()
        zone = pcbnew.ZONE(self.board)
        zone.SetIsRuleArea(True)
        zone.SetLayer(pcbnew.F_Cu)
        polygon = zone.Outline()
        polygon.NewOutline()
        for x, y in ((7.2, 3.5), (7.4, 3.5), (7.4, 3.8), (7.2, 3.8)):
            polygon.Append(pcbnew.VECTOR2I(iu(x), iu(y)))
        self.board.Add(zone)
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('immutable native rule area intersects shared zone/port', '\n'.join(result['errors']))

    def test_virtual_face_rejects_other_source_region_at_face(self):
        self.add_virtual_right_face()
        self.floorplan['placement']['regions']['intruder'] = [7.6, 4.9, 8.1, 5.1]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('virtual boundary enters intruder source region',
                      result['allocations'][0]['reason'])

    def test_virtual_reservation_rejects_other_source_region_away_from_face(self):
        self.add_virtual_right_face()
        self.floorplan['placement']['regions']['intruder'] = [4.5, 4.5, 5, 5.5]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('virtual reservation enters intruder source region',
                      result['allocations'][0]['reason'])

    def test_fixed_physical_witness_does_not_use_virtual_region_rule(self):
        self.floorplan['placement']['regions']['intruder'] = [3.2, 4.8, 3.8, 5.2]
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['allocations'][0]['witness_count'], 1)

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


class CrowUsbPartialPortTest(unittest.TestCase):
    """Exact native partial Q_VBUS port; no XU port or P1/route claim."""

    def setUp(self):
        fixture = Path(__file__).parent / 'fixtures' / 'crow_usb_partial_port'
        board_path = fixture / 'board.kicad_pcb'
        self.assertEqual(hashlib.sha256(board_path.read_bytes()).hexdigest(),
                         '60a903b5ae5c7c7ef084fb3bd5dd50abf26e1e0e134a928f46107a6c90934b17')
        self.board = pcbnew.LoadBoard(str(board_path))
        self.plan = json.loads((fixture / 'modular_plan.json').read_text())
        self.floorplan = yaml.safe_load((fixture / 'floorplan.yaml').read_text())
        self.source = yaml.safe_load((fixture / 'p1_corridor_requirements.yaml').read_text())
        self.outline = pcbnew.SHAPE_POLY_SET()
        self.assertTrue(self.board.GetBoardPolygonOutlines(self.outline, False))
        _, self.pads = checker.graph.board_index(self.board)
        endpoint = {'source_pad': 'Q_VBUS.3', 'native_pad': 'Q_VBUS.3',
                    'net': 'VBUS_PRESENT_N', 'block': 'usb_vbus_sense'}
        self.p2 = {'status': 'P2_REQUIRED', **endpoint, 'port_id': 'q_vbus_partial',
                   'layer': 'F.Cu', 'to_reservation': 'q_vbus_partial_reservation'}
        self.port = {'id': 'q_vbus_partial', 'owner': 'board_integration',
                     'participants': ['usb_vbus_sense', 'xmos_core'],
                     'geometry': {'type': 'union_rectangles',
                                  'rectangles': [[215.42, 70, 217.5, 74.8]]},
                     'bbox': [215.42, 74.2, 215.52, 74.8], 'face': 'west',
                     'layers': ['F.Cu'], 'reservation_id': 'q_vbus_partial_reservation',
                     'reservation_bbox': [215.52, 70, 217.5, 74.8],
                     'affected': [endpoint], 'p2_obligations': [self.p2],
                     'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                           'port_id': 'q_vbus_partial', 'layers': ['F.Cu'],
                                           'proof': 'continuous_filled_reference'}}

    def check_port(self):
        return checker._shared_ports(
            {'shared_transition_ports': [self.port]}, self.plan, self.board,
            self.outline, self.floorplan['placement']['regions'],
            list(self.board.Zones()), {'usb_device_pair': {'VBUS_PRESENT_N'}},
            {}, self.pads)

    def test_exact_board_partial_port_remains_only_an_obligation(self):
        ports = self.check_port()
        witness = {'kind': 'shared_transition_port', 'port_id': 'q_vbus_partial',
                   'source': 'Q_VBUS.3', 'native': 'Q_VBUS.3',
                   'net': 'VBUS_PRESENT_N', 'block': 'usb_vbus_sense',
                   'layer': 'F.Cu', 'face': 'west',
                   'boundary_bbox': self.port['bbox'],
                   'reservation_id': self.port['reservation_id'],
                   'p2_obligation': self.p2}
        checked = checker._coarse_witness(
            self.board, witness, 'VBUS_PRESENT_N',
            {('VBUS_PRESENT_N', 'usb_vbus_sense'): {'Q_VBUS.3'}},
            {}, self.pads, self.outline,
            self.floorplan['placement']['regions'], set(), ports)
        self.assertEqual(checked['p2_obligation']['status'], 'P2_REQUIRED')
        self.assertTrue(checker._witness_touches_reservation(
            checked, {'bbox': self.port['reservation_bbox']}))
        self.assertNotIn('capacity_slots', checked)

    def test_exact_board_ignores_reference_text_outside_physical_envelope(self):
        fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'Q_VBUS')
        fp.Reference().SetVisible(True)
        fp.Reference().SetPosition(pcbnew.VECTOR2I(iu(215.47), iu(74.5)))
        self.assertTrue(checker.intersects(
            checker.box_mm(fp.GetBoundingBox(True, True)), self.port['bbox']))
        self.assertFalse(checker.intersects(checker._physical_envelope(fp), self.port['bbox']))
        self.check_port()

    def test_exact_board_rejects_physical_body_overlap(self):
        # The physical body ends at x=213.955 mm; text is intentionally irrelevant.
        self.port['geometry']['rectangles'][0][0] = 213.8
        self.port['bbox'] = [213.9, 74.2, 213.95, 74.8]
        with self.assertRaisesRegex(checker.ContractError, 'native footprint/pad Q_VBUS'):
            self.check_port()

    def test_exact_board_rejects_pad_overlap(self):
        # Pad 3 is [212.2, 74.2, 213.675, 74.8] mm.
        self.port['geometry']['rectangles'][0][0] = 212.1
        self.port['bbox'] = [212.3, 74.3, 212.4, 74.4]
        with self.assertRaisesRegex(checker.ContractError, 'native footprint/pad Q_VBUS'):
            self.check_port()

    def test_exact_board_rejects_courtyard_overlap(self):
        fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'Q_VBUS')
        points = [(215.35, 74.1), (215.6, 74.1), (215.6, 74.9), (215.35, 74.9)]
        for start, end in zip(points, points[1:] + points[:1]):
            edge = pcbnew.PCB_SHAPE(fp)
            edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
            edge.SetStart(pcbnew.VECTOR2I(iu(start[0]), iu(start[1])))
            edge.SetEnd(pcbnew.VECTOR2I(iu(end[0]), iu(end[1])))
            edge.SetLayer(pcbnew.F_CrtYd)
            edge.SetWidth(iu(.05))
            fp.Add(edge)
        self.assertTrue(checker.intersects(checker._physical_envelope(fp), self.port['bbox']))
        with self.assertRaisesRegex(checker.ContractError, 'native footprint/pad Q_VBUS'):
            self.check_port()

    def test_exact_board_rejects_foreign_region(self):
        self.floorplan['placement']['regions']['foreign'] = [216, 73, 216.5, 74]
        with self.assertRaisesRegex(checker.ContractError, 'unowned overlap'):
            self.check_port()

    def test_exact_board_rejects_native_ref_owner_reassignment(self):
        for block in self.plan['blocks']:
            if block['id'] == 'usb_vbus_sense':
                block['refs'].remove('Q_VBUS')
            elif block['id'] == 'xmos_core':
                block['refs'].append('Q_VBUS')
        with self.assertRaisesRegex(checker.ContractError,
                                    'affected native footprint/block owner mismatch'):
            self.check_port()
        # Exercise the complete schema-2 evaluator: a source validation error
        # must be FAIL, never an INCOMPLETE result that could look admissible.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = {'source': root / 'source.yaml', 'interfaces': root / 'interfaces.json',
                     'aliases': root / 'aliases.yaml', 'floorplan': root / 'floorplan.yaml',
                     'contract': root / 'contract.json'}
            self.source['shared_transition_ports'] = [self.port]
            paths['source'].write_text(yaml.safe_dump(self.source))
            paths['interfaces'].write_text(json.dumps(self.plan))
            paths['aliases'].write_text(yaml.safe_dump({'pin_aliases': {}}))
            paths['floorplan'].write_text(yaml.safe_dump(self.floorplan))
            board_path = Path(__file__).parent / 'fixtures' / 'crow_usb_partial_port' / 'board.kicad_pcb'
            hashes = {name: checker.digest(path) for name, path in paths.items() if name != 'contract'}
            hashes['board'] = checker.digest(board_path)
            allocations = [{'id': row['id'], 'coverage_nets': row['coverage_nets']}
                           for row in self.source['allocations']]
            allocations.append({'id': 'power_boundary_windows',
                                'coverage_nets': self.source['power_boundary_windows']['coverage_nets']})
            contract = {'schema': 2, 'kind': 'p1-coarse-reservations',
                        'profile': 'crow-p1-coarse', 'allocations': allocations,
                        **{name + '_sha256': value for name, value in hashes.items()}}
            paths['contract'].write_text(json.dumps(contract))
            report = checker.evaluate_coarse(
                board_path, paths['contract'], checker.digest(paths['contract']),
                source_path=paths['source'], interface_path=paths['interfaces'],
                alias_path=paths['aliases'], floorplan_path=paths['floorplan'],
                expected_source_sha256=hashes['source'],
                expected_interface_sha256=hashes['interfaces'],
                expected_alias_sha256=hashes['aliases'],
                expected_floorplan_sha256=hashes['floorplan'])
        self.assertEqual(report['status'], 'FAIL')
        self.assertIn('affected native footprint/block owner mismatch', '\n'.join(report['errors']))
        self.assertFalse(report['p1_accepted'])


class UnresolvedBranchTest(unittest.TestCase):
    def setUp(self):
        self.board = pcbnew.BOARD()
        for ref,x,y in [('J_A',2,2),('J_B',5,5),('J_C',6,5)]:
            pad(self.board,ref,'1','TREE',x,y,.4)
        self.regions = {'a':[1,1,3,3], 'b':[4,4,7,6], 'foreign':[5.7,4.7,6.5,5.5]}
        self.interfaces = {'interfaces':[{'net':'TREE','endpoints':
            {'a':['J_A.1'],'b':['J_B.1','J_C.1']}}]}
        self.endpoints = [{'source_pad':p,'native_pad':p,'net':'TREE','block':block}
            for p,block in [('J_A.1','a'),('J_B.1','b'),('J_C.1','b')]]
        self.obligations = [{'status':'P2_REQUIRED',**e,'branch_id':'tree',
            'layer':'F.Cu','proof':'native_pad_to_unplaced_tree'} for e in self.endpoints]
        self.branch = {'id':'tree','owner':'board_integration','allocation_id':'signal',
            'net':'TREE','layer':'F.Cu','reference_layer':'B.Cu',
            'reservation_id':'unplaced','terminal_count':3,'minimum_tree_edges':2,
            'endpoints':self.endpoints,'p2_obligations':self.obligations,
            'physical_blockers':[{'source_pad':'J_C.1','native_pad':'J_C.1',
                'block':'b','foreign_regions':['foreign']}],
            'tree_obligation':{'status':'P3_REQUIRED','net':'TREE',
                'terminal_count':3,'minimum_tree_edges':2,
                'proof':'one_connected_native_net_without_unrelated_branches'},
            'return_obligation':{'status':'P2_REQUIRED','net':'GND',
                'branch_id':'tree','reference_layer':'B.Cu',
                'proof':'continuous_filled_reference_under_actual_tree'}}
        _,self.pads = checker.graph.board_index(self.board)

    def validate(self):
        return checker._unresolved_branches(
            {'unresolved_multiterminal_branches':[self.branch]},self.interfaces,
            self.board,self.regions,{'signal':{'TREE'}},{},self.pads)

    def test_exact_tree_is_explicitly_unresolved(self):
        self.assertEqual(set(self.validate()),{'tree'})
        self.assertEqual(self.branch['physical_blockers'][0]['foreign_regions'],['foreign'])
        self.assertNotIn('bbox',self.branch)
        self.assertNotIn('capacity_slots',self.branch)

    def test_missing_terminal_or_tree_edge_rejected(self):
        omitted = self.branch['endpoints'].pop()
        with self.assertRaisesRegex(checker.ContractError,'endpoint denominator'):
            self.validate()
        self.branch['endpoints'].append(omitted)
        self.branch['minimum_tree_edges']=1
        with self.assertRaisesRegex(checker.ContractError,'tree lower bound'):
            self.validate()

    def test_undeclared_native_terminal_rejected(self):
        # The source interface is the authoritative five/three-terminal set;
        # a board-only fourth pad would make the promised tree false even if
        # every declared terminal is still present.
        pad(self.board, 'J_EXTRA', '1', 'TREE', 7, 5, .4)
        _, self.pads = checker.graph.board_index(self.board)
        with self.assertRaisesRegex(checker.ContractError,
                                    'exact native branch terminal set'):
            self.validate()

    def test_distinct_source_aliases_cannot_collapse_to_one_native_terminal(self):
        self.board = pcbnew.BOARD()
        for ref, number, x, y in [('J_USB','1',2,2), ('J_B','1',5,5),
                                  ('J_C','1',6,5)]:
            pad(self.board, ref, number, 'TREE', x, y, .4)
        _, self.pads = checker.graph.board_index(self.board)
        self.interfaces['interfaces'][0]['endpoints'] = {
            'a':['J_USB.A1','J_USB.B1'], 'b':['J_B.1','J_C.1']}
        self.branch['endpoints'] = [
            {'source_pad':source, 'native_pad':native, 'net':'TREE', 'block':block}
            for source, native, block in [('J_USB.A1','J_USB.1','a'),
                                           ('J_USB.B1','J_USB.1','a'),
                                           ('J_B.1','J_B.1','b'),
                                           ('J_C.1','J_C.1','b')]]
        self.branch['p2_obligations'] = [
            {'status':'P2_REQUIRED', **entry, 'branch_id':'tree',
             'layer':'F.Cu', 'proof':'native_pad_to_unplaced_tree'}
            for entry in sorted(self.branch['endpoints'], key=lambda e:e['source_pad'])]
        self.branch['terminal_count'] = 4
        self.branch['minimum_tree_edges'] = 3
        self.branch['tree_obligation']['terminal_count'] = 4
        self.branch['tree_obligation']['minimum_tree_edges'] = 3
        aliases = {'A1':'1', 'B1':'1'}
        with self.assertRaisesRegex(checker.ContractError, 'terminal alias collision'):
            checker._unresolved_branches(
                {'unresolved_multiterminal_branches':[self.branch]}, self.interfaces,
                self.board, self.regions, {'signal':{'TREE'}}, aliases, self.pads)

        # Separate fused connector contacts on the same net remain valid when
        # each schematic contact maps to its own exact native pad.
        usb_fp = self.board.FindFootprintByReference('J_USB')
        second = pcbnew.PAD(usb_fp)
        second.SetNumber('2')
        second.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        second.SetShape(pcbnew.PAD_SHAPE_RECT)
        second.SetSize(pcbnew.VECTOR2I(iu(.4), iu(.4)))
        second.SetPosition(pcbnew.VECTOR2I(iu(2.5), iu(2)))
        second.SetLayerSet(pcbnew.LSET.FrontMask())
        second.SetNet(self.board.FindNet('TREE'))
        usb_fp.Add(second)
        _, self.pads = checker.graph.board_index(self.board)
        aliases['B1'] = '2'
        self.branch['endpoints'][1]['native_pad'] = 'J_USB.2'
        next(row for row in self.branch['p2_obligations']
             if row['source_pad'] == 'J_USB.B1')['native_pad'] = 'J_USB.2'
        self.assertEqual(set(checker._unresolved_branches(
            {'unresolved_multiterminal_branches':[self.branch]}, self.interfaces,
            self.board, self.regions, {'signal':{'TREE'}}, aliases, self.pads)),
            {'tree'})

    def test_unreported_overlap_and_fake_geometry_rejected(self):
        self.branch['physical_blockers']=[]
        with self.assertRaisesRegex(checker.ContractError,'blocker inventory'):
            self.validate()
        self.branch['physical_blockers']=[{'source_pad':'J_C.1','native_pad':'J_C.1',
            'block':'b','foreign_regions':['foreign']}]
        self.branch['bbox']=[1,1,7,6]
        with self.assertRaisesRegex(checker.ContractError,'cannot claim geometry'):
            self.validate()


class UnresolvedBranchPhysicalCellTest(unittest.TestCase):
    def setUp(self):
        UnresolvedBranchTest.setUp(self)
        self.regions.update(b=[4,4,5.5,6], b_east=[5.6,4,7,6],
                            foreign=[8,8,9,9])
        self.branch['physical_blockers'] = []
        self.branch['endpoints'][2]['physical_cell_id'] = 'b_east'
        self.cells = {'b': {'owner_block':'b', 'refs':{'J_B'}, 'transit':False,
                            'bbox':(4,4,5.5,6)},
                      'b_east': {'owner_block':'b', 'refs':{'J_C'}, 'transit':False,
                                 'bbox':(5.6,4,7,6)}}
        self.patterns = [{'match':['J_C'], 'region':'b_east'}]

    def validate(self):
        return checker._unresolved_branches(
            {'unresolved_multiterminal_branches':[self.branch]},self.interfaces,
            self.board,self.regions,{'signal':{'TREE'}},{},self.pads,
            self.cells,self.patterns)

    def test_remote_cell_preserves_exact_tree_and_obligations(self):
        self.assertEqual(set(self.validate()), {'tree'})
        self.assertEqual(len(self.branch['endpoints']), 3)
        self.assertEqual(len(self.branch['p2_obligations']), 3)
        self.assertEqual(self.branch['minimum_tree_edges'], 2)
        self.assertIsNone(self.branch.get('capacity_slots'))

    def test_missing_or_wrong_cell_fails_closed(self):
        del self.branch['endpoints'][2]['physical_cell_id']
        with self.assertRaisesRegex(checker.ContractError, 'outside source owner region'):
            self.validate()
        self.branch['endpoints'][2]['physical_cell_id'] = 'b'
        with self.assertRaisesRegex(checker.ContractError, 'owner/ref/region mismatch'):
            self.validate()
        self.branch['endpoints'][2]['physical_cell_id'] = 'a_unknown'
        with self.assertRaisesRegex(checker.ContractError, 'owner/ref/region mismatch'):
            self.validate()

    def test_wrong_owner_region_body_and_pattern_fail_closed(self):
        self.cells['b_east']['owner_block'] = 'a'
        with self.assertRaisesRegex(checker.ContractError, 'owner/ref/region mismatch'):
            self.validate()
        self.cells['b_east']['owner_block'] = 'b'
        self.cells['b_east']['bbox'] = (5.8,4,7,6)
        with self.assertRaisesRegex(checker.ContractError, 'owner/ref/region mismatch'):
            self.validate()
        self.cells['b_east']['bbox'] = (5.6,4,7,6)
        self.regions['b_east'] = [5.9,4,7,6]
        self.cells['b_east']['bbox'] = (5.9,4,7,6)
        with self.assertRaisesRegex(checker.ContractError, 'body/pad/pattern mismatch'):
            self.validate()
        self.regions['b_east'] = [5.6,4,7,6]
        self.cells['b_east']['bbox'] = (5.6,4,7,6)
        self.patterns[0]['region'] = 'b'
        with self.assertRaisesRegex(checker.ContractError, 'body/pad/pattern mismatch'):
            self.validate()

    def test_extra_endpoint_field_or_undeclared_native_pad_rejected(self):
        self.branch['endpoints'][2]['unknown'] = 'claim'
        with self.assertRaisesRegex(checker.ContractError, 'physical cell declaration invalid'):
            self.validate()
        del self.branch['endpoints'][2]['unknown']
        pad(self.board, 'J_EXTRA', '1', 'TREE', 8, 5, .4)
        _, self.pads = checker.graph.board_index(self.board)
        with self.assertRaisesRegex(checker.ContractError, 'exact native branch terminal set'):
            self.validate()


class UnresolvedTwoTerminalTest(unittest.TestCase):
    def setUp(self):
        UnresolvedBranchTest.setUp(self)
        self.board.Remove(self.board.FindFootprintByReference('J_C'))
        _, self.pads = checker.graph.board_index(self.board)
        self.interfaces['interfaces'][0]['endpoints']['b'] = ['J_B.1']
        self.branch['endpoints'] = self.branch['endpoints'][:2]
        self.branch['p2_obligations'] = self.branch['p2_obligations'][:2]
        self.branch['terminal_count'] = 2
        self.branch['minimum_tree_edges'] = 1
        self.branch['tree_obligation']['terminal_count'] = 2
        self.branch['tree_obligation']['minimum_tree_edges'] = 1
        self.branch['physical_blockers'] = []
        self.branch['capacity_slots'] = None

    def validate(self):
        return checker._unresolved_branches(
            {'unresolved_two_terminal_crossings':[self.branch]}, self.interfaces,
            self.board, self.regions, {'signal':{'TREE'}}, {}, self.pads)

    def test_exact_two_owner_crossing_is_no_credit(self):
        rows = self.validate()
        self.assertEqual(rows['tree']['_kind'], 'unresolved_two_terminal_crossing')
        self.assertEqual(rows['tree']['terminal_count'], 2)
        self.assertEqual(rows['tree']['minimum_tree_edges'], 1)
        self.assertIsNone(rows['tree']['capacity_slots'])

    def test_third_terminal_or_one_owner_rejected(self):
        pad(self.board, 'J_EXTRA', '1', 'TREE', 6, 5, .4)
        _, self.pads = checker.graph.board_index(self.board)
        with self.assertRaisesRegex(checker.ContractError, 'exact native branch terminal set'):
            self.validate()
        self.board.Remove(self.board.FindFootprintByReference('J_EXTRA'))
        _, self.pads = checker.graph.board_index(self.board)
        self.interfaces['interfaces'][0]['endpoints'] = {'a':['J_A.1','J_B.1']}
        with self.assertRaisesRegex(checker.ContractError, 'cross source owners'):
            self.validate()

    def test_wrong_obligations_or_success_credit_rejected(self):
        self.branch['p2_obligations'].pop()
        with self.assertRaisesRegex(checker.ContractError, 'exact P2'):
            self.validate()
        self.branch['p2_obligations'] = self.obligations[:2]
        self.branch['return_obligation']['status'] = 'PASS'
        with self.assertRaisesRegex(checker.ContractError, 'P2 return/P3'):
            self.validate()
        self.branch['return_obligation']['status'] = 'P2_REQUIRED'
        self.branch['capacity_slots'] = 1
        with self.assertRaisesRegex(checker.ContractError, 'cannot claim geometry/capacity'):
            self.validate()
        self.branch['capacity_slots'] = None
        self.branch['status'] = 'PASS'
        with self.assertRaisesRegex(checker.ContractError, 'source fields invalid'):
            self.validate()

    def test_wrong_tree_edge_count_or_legacy_key_rejected(self):
        self.branch['minimum_tree_edges'] = 2
        with self.assertRaisesRegex(checker.ContractError, 'tree lower bound'):
            self.validate()
        self.branch['minimum_tree_edges'] = 1
        with self.assertRaisesRegex(checker.ContractError, 'endpoint denominator'):
            checker._unresolved_branches(
                {'unresolved_multiterminal_branches':[self.branch]}, self.interfaces,
                self.board, self.regions, {'signal':{'TREE'}}, {}, self.pads)


if __name__ == '__main__':
    unittest.main()
