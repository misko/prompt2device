"""First-slice linked path: one physical stage and one unresolved virtual span."""
from __future__ import annotations

import json
import copy
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


def footprint(board, ref, x, y, pad_nets):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue('fixture')
    fp.SetLayer(pcbnew.F_Cu)
    fp.SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    for number, net, dx in pad_nets:
        pad = pcbnew.PAD(fp)
        pad.SetNumber(str(number))
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(pcbnew.VECTOR2I(iu(.4), iu(.4)))
        pad.SetPosition(pcbnew.VECTOR2I(iu(x + dx), iu(y)))
        pad.SetLayerSet(pcbnew.LSET.FrontMask())
        native_net = board.FindNet(net)
        if native_net is None:
            native_net = pcbnew.NETINFO_ITEM(board, net)
            board.Add(native_net)
        pad.SetNet(native_net)
        fp.Add(pad)
    board.Add(fp)


class LinkedPathTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.board = pcbnew.BOARD()
        corners = [(0, 0), (20, 0), (20, 20), (0, 20)]
        for a, b in zip(corners, corners[1:] + corners[:1]):
            edge = pcbnew.PCB_SHAPE(self.board)
            edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
            edge.SetStart(pcbnew.VECTOR2I(iu(a[0]), iu(a[1])))
            edge.SetEnd(pcbnew.VECTOR2I(iu(b[0]), iu(b[1])))
            edge.SetLayer(pcbnew.Edge_Cuts)
            self.board.Add(edge)
        for ref, x, y in [('J', 8, 4), ('E', 8, 8), ('X', 8, 15)]:
            footprint(self.board, ref, x, y,
                      [('1', 'DP', -.5), ('2', 'DN', .5)])
        footprint(self.board, 'G', 2, 2, [('1', 'GND', 0)])
        self.floorplan = {'placement': {
            'anchors': {'J': [8, 4, 0], 'G': [2, 2, 0]},
            'post_anchors': {'E': [8, 8, 0], 'X': [8, 15, 0]},
            'seeds': {}, 'patterns': [],
            'regions': {'edge': [6, 1, 10, 5], 'front': [6, 6, 10, 10],
                        'xmos': [6, 13, 10, 18], 'gap': [7, 5, 9, 6],
                        'power': [0, 0, 4, 4]}}}
        self.interfaces = {'blocks': [
            {'id': 'edge', 'refs': ['J']}, {'id': 'front', 'refs': ['E']},
            {'id': 'xmos', 'refs': ['X']}, {'id': 'power', 'refs': ['G']}],
            'interfaces': [
                {'net': net, 'endpoints': {'edge': [f'J.{pin}'],
                                          'front': [f'E.{pin}'],
                                          'xmos': [f'X.{pin}']}}
                for pin, net in [('1', 'DP'), ('2', 'DN')]] +
            [{'net': 'GND', 'endpoints': {'power': ['G.1']}}]}
        affected = [{'source_pad': f'{ref}.{pin}', 'native_pad': f'{ref}.{pin}',
                     'net': net, 'block': owner}
                    for pin, net in [('1', 'DP'), ('2', 'DN')]
                    for ref, owner in [('J', 'edge'), ('E', 'front')]]
        face_for = {'edge': 'south', 'front': 'north'}
        physical = {'id': 'edge_stage', 'kind': 'physical_corridor',
                    'owner': 'board_integration', 'region_id': 'gap',
                    'allocation_id': 'signal', 'participants': ['edge', 'front'],
                    'faces': [{'block': 'edge', 'region_face': 'south',
                               'bbox': [7, 4.8, 9, 5]},
                              {'block': 'front', 'region_face': 'north',
                               'bbox': [7, 6, 9, 6.2]}],
                    'layer': 'F.Cu', 'reference_layer': 'B.Cu',
                    'nets': ['DP', 'DN'], 'reservation_id': 'edge_stage_trunk',
                    'affected': affected,
                    'p2_obligations': [
                        {'status': 'P2_REQUIRED', **e, 'corridor_id': 'edge_stage',
                         'region_face': face_for[e['block']], 'layer': 'F.Cu',
                         'to_reservation': 'edge_stage_trunk'} for e in affected],
                    'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                          'corridor_id': 'edge_stage',
                                          'reference_layer': 'B.Cu',
                                          'proof': 'continuous_filled_reference'},
                    'fixed_accesses': [
                        {'source_pad': f'J.{pin}', 'native_pad': f'J.{pin}',
                         'net': net, 'block': 'edge', 'face': 'north',
                         'bbox': [x0, 4.2, x1, 5]}
                        for pin, net, x0, x1 in
                        [('1', 'DP', 7.3, 7.7), ('2', 'DN', 8.3, 8.7)]],
                    'axis': 'vertical', 'slot_pitch_mm': .5,
                    'demand_slots': 2}
        virtual_affected = [{'source_pad': f'{ref}.{pin}',
                             'native_pad': f'{ref}.{pin}', 'net': net,
                             'block': owner}
                            for pin, net in [('1', 'DP'), ('2', 'DN')]
                            for ref, owner in [('E', 'front'), ('X', 'xmos')]]
        virtual = {'id': 'xu_pending', 'kind': 'unresolved_virtual_span',
                   'participants': ['front', 'xmos'], 'nets': ['DP', 'DN'],
                   'layer': 'F.Cu', 'reference_layer': 'B.Cu',
                   'affected': virtual_affected, 'geometry': None,
                   'capacity_slots': None, 'status': 'INCOMPLETE',
                   'p2_obligations': [
                       {'status': 'P2_REQUIRED', **e, 'stage_id': 'xu_pending',
                        'layer': 'F.Cu', 'to_reservation': 'series'}
                       for e in virtual_affected],
                   'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                         'stage_id': 'xu_pending',
                                         'reference_layer': 'B.Cu',
                                         'proof': 'continuous_filled_reference'}}
        self.source = {'kind': 'crow-p1-corridor-requirements',
                       'p1_fixed_refs': ['J', 'G'],
                       'allocations': [{'id': 'signal',
                                        'coverage_nets': ['DP', 'DN'],
                                        'demands': [{'id': 'pair',
                                                     'nets': ['DP', 'DN']}],
                                        'endpoints': {
                                            net: {'edge': [f'J.{pin}'],
                                                  'front': [f'E.{pin}'],
                                                  'xmos': [f'X.{pin}']}
                                            for pin, net in [('1', 'DP'), ('2', 'DN')]}}],
                       'power_boundary_windows': {'coverage_nets': ['GND']},
                       'linked_paths': [{'id': 'series', 'allocation_id': 'signal',
                                         'nets': ['DP', 'DN'],
                                         'owner_order': ['edge', 'front', 'xmos'],
                                         'reservation_id': 'series',
                                         'layer': 'F.Cu', 'reference_layer': 'B.Cu',
                                         'stages': [physical, virtual],
                                         'joins': [
                                             {'from': 'edge_stage', 'to': 'xu_pending',
                                              'owner': 'front', 'net': net,
                                              'source_pad': f'E.{pin}',
                                              'kind': 'pad_anchored_virtual_interstage'}
                                             for pin, net in [('1', 'DP'), ('2', 'DN')]]}]}
        self.allocations = [
            {'id': 'signal', 'coverage_nets': ['DP', 'DN'],
             'boundary_witnesses': [], 'reservations': [],
             'linked_paths': [{'id': 'series', 'kind': 'linked_path',
                               'nets': ['DP', 'DN'], 'status': 'INCOMPLETE'}]},
            {'id': 'power_boundary_windows', 'coverage_nets': ['GND'],
             'boundary_witnesses': [{'source': 'G.1', 'native': 'G.1',
                                     'net': 'GND', 'block': 'power',
                                     'layer': 'F.Cu', 'face': 'west',
                                     'boundary_bbox': [1.8, 1.8, 2.2, 2.2],
                                     'reservation_id': 'power'}],
             'reservations': [{'id': 'power', 'kind': 'power_or_mechanical',
                               'layer': 'F.Cu', 'bbox': [2.2, 1, 4, 3],
                               'nets': ['GND']}]},
        ]

    def run_case(self):
        paths = {name: self.root / name for name in
                 ('board.kicad_pcb', 'source.yaml', 'interfaces.json',
                  'aliases.yaml', 'floorplan.yaml', 'contract.json')}
        pcbnew.SaveBoard(str(paths['board.kicad_pcb']), self.board)
        paths['source.yaml'].write_text(yaml.safe_dump(self.source))
        paths['interfaces.json'].write_text(json.dumps(self.interfaces))
        paths['aliases.yaml'].write_text(yaml.safe_dump({'pin_aliases': {}}))
        paths['floorplan.yaml'].write_text(yaml.safe_dump(self.floorplan))
        hashes = {name: checker.digest(path) for name, path in paths.items()
                  if name != 'contract.json'}
        contract = {'schema': 2, 'kind': 'p1-coarse-reservations',
                    'profile': 'fixture-coarse',
                    'board_sha256': hashes['board.kicad_pcb'],
                    'source_sha256': hashes['source.yaml'],
                    'interfaces_sha256': hashes['interfaces.json'],
                    'aliases_sha256': hashes['aliases.yaml'],
                    'floorplan_sha256': hashes['floorplan.yaml'],
                    'allocations': self.allocations}
        paths['contract.json'].write_text(json.dumps(contract))
        return checker.evaluate(paths['board.kicad_pcb'], paths['contract.json'],
                                checker.digest(paths['contract.json']),
                                source_path=paths['source.yaml'],
                                interface_path=paths['interfaces.json'],
                                alias_path=paths['aliases.yaml'],
                                floorplan_path=paths['floorplan.yaml'],
                                expected_source_sha256=hashes['source.yaml'],
                                expected_interface_sha256=hashes['interfaces.json'],
                                expected_alias_sha256=hashes['aliases.yaml'],
                                expected_floorplan_sha256=hashes['floorplan.yaml'])

    def make_second_physical(self):
        self.floorplan['placement']['regions']['gap2'] = [7, 10, 9, 13]
        path = self.source['linked_paths'][0]
        virtual = path['stages'][1]
        affected = virtual['affected']
        face_for = {'front': 'south', 'xmos': 'north'}
        physical = {'id': 'xu_stage', 'kind': 'physical_corridor',
                    'owner': 'board_integration', 'region_id': 'gap2',
                    'allocation_id': 'signal', 'participants': ['front', 'xmos'],
                    'faces': [{'block': 'front', 'region_face': 'south',
                               'bbox': [7, 9.8, 9, 10]},
                              {'block': 'xmos', 'region_face': 'north',
                               'bbox': [7, 13, 9, 13.2]}],
                    'layer': 'F.Cu', 'reference_layer': 'B.Cu',
                    'nets': ['DP', 'DN'], 'reservation_id': 'xu_stage_trunk',
                    'affected': affected,
                    'p2_obligations': [
                        {'status': 'P2_REQUIRED', **e, 'corridor_id': 'xu_stage',
                         'region_face': face_for[e['block']], 'layer': 'F.Cu',
                         'to_reservation': 'xu_stage_trunk'} for e in affected],
                    'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                          'corridor_id': 'xu_stage',
                                          'reference_layer': 'B.Cu',
                                          'proof': 'continuous_filled_reference'},
                    'fixed_accesses': [], 'axis': 'vertical',
                    'slot_pitch_mm': .5, 'demand_slots': 2}
        path['stages'][1] = physical
        for join in path['joins']:
            join['to'] = 'xu_stage'
            join['kind'] = 'pad_anchored_physical_interstage'

    def add_pad(self, ref, number, net, dx):
        fp = next(fp for fp in self.board.GetFootprints() if fp.GetReference() == ref)
        pad = pcbnew.PAD(fp)
        pad.SetNumber(str(number))
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(pcbnew.VECTOR2I(iu(.4), iu(.4)))
        pos = fp.GetPosition()
        pad.SetPosition(pcbnew.VECTOR2I(pos.x + iu(dx), pos.y))
        pad.SetLayerSet(pcbnew.LSET.FrontMask())
        native_net = self.board.FindNet(net)
        if native_net is None:
            native_net = pcbnew.NETINFO_ITEM(self.board, net)
            self.board.Add(native_net)
        pad.SetNet(native_net)
        fp.Add(pad)

    def test_valid_series_stays_incomplete_without_capacity_credit(self):
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['status'], 'INCOMPLETE')
        path = result['allocations'][0]['linked_paths'][0]
        self.assertIsNone(path['capacity_slots'])
        self.assertIsNone(path['stages'][1]['capacity_slots'])
        self.assertFalse(result['p1_accepted'])

    def test_gap_without_typed_join_fails(self):
        self.source['linked_paths'][0]['joins'] = []
        self.assertIn('missing or parallel interstage join',
                      '\n'.join(self.run_case()['errors']))

    def test_physical_face_gap_fails(self):
        self.floorplan['placement']['regions']['gap'] = [7, 5.1, 9, 6]
        self.assertIn('integration face lacks positive non-corner shared edge',
                      '\n'.join(self.run_case()['errors']))

    def test_parallel_same_net_credit_fails(self):
        self.allocations[0]['reservations'].append(
            {'id': 'parallel', 'kind': 'signal', 'layer': 'F.Cu',
             'bbox': [11, 5, 12, 6], 'axis': 'vertical',
             'nets': ['DP'], 'demand_slots': 1, 'slot_pitch_mm': .5})
        self.assertIn('competing ordinary credit', '\n'.join(self.run_case()['errors']))

    def test_omitted_endpoint_fails(self):
        virtual = self.source['linked_paths'][0]['stages'][1]
        virtual['affected'] = [e for e in virtual['affected'] if e['source_pad'] != 'X.2']
        self.assertIn('virtual endpoint denominator mismatch',
                      '\n'.join(self.run_case()['errors']))

    def test_foreign_region_overlap_fails(self):
        self.floorplan['placement']['regions']['power'] = [7.2, 5.2, 8.2, 5.8]
        self.assertIn('integration region overlaps power',
                      '\n'.join(self.run_case()['errors']))

    def test_virtual_geometry_or_missing_return_fails(self):
        virtual = self.source['linked_paths'][0]['stages'][1]
        virtual['geometry'] = [7, 10, 9, 13]
        self.assertIn('geometry/capacity free', '\n'.join(self.run_case()['errors']))
        virtual['geometry'] = None
        virtual['return_obligation'] = {}
        self.assertIn('virtual P2/filled-return', '\n'.join(self.run_case()['errors']))

    def test_two_physical_stages_remain_incomplete_without_summed_credit(self):
        self.make_second_physical()
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        linked = result['allocations'][0]['linked_paths'][0]
        self.assertEqual(linked['status'], 'INCOMPLETE')
        self.assertIsNone(linked['capacity_slots'])
        self.assertIn('rough_capacity', linked['stages'][1])

    def test_physical_join_rejects_virtual_kind(self):
        self.make_second_physical()
        self.source['linked_paths'][0]['joins'][0]['kind'] = 'pad_anchored_virtual_interstage'
        self.assertIn('missing or parallel interstage join',
                      '\n'.join(self.run_case()['errors']))

    def test_extra_native_linked_net_pad_fails(self):
        self.add_pad('E', 3, 'DP', 0)
        self.assertIn('linked native net pad multiset mismatch',
                      '\n'.join(self.run_case()['errors']))

    def test_duplicate_native_pad_number_fails(self):
        self.add_pad('E', 1, 'DP', 0)
        self.assertIn('linked native net pad multiset mismatch',
                      '\n'.join(self.run_case()['errors']))

    def test_source_alias_collision_fails_closed(self):
        terminals = {('J_USB.2', 'J_USB.A4', 'DP', 'edge'),
                     ('J_USB.15', 'J_USB.A4', 'DP', 'edge')}
        with self.assertRaisesRegex(checker.ContractError, 'linked native alias collision'):
            checker._linked_native_pad_census('series', terminals, {}, {'DP'})

    def test_physical_stage_cannot_claim_outcome_fields(self):
        self.source['linked_paths'][0]['stages'][0]['status'] = 'PASS'
        self.assertIn('physical stage schema/outcome fields invalid',
                      '\n'.join(self.run_case()['errors']))
        del self.source['linked_paths'][0]['stages'][0]['status']
        self.make_second_physical()
        self.source['linked_paths'][0]['stages'][1]['capacity_slots'] = 999
        self.assertIn('second physical stage schema/outcome fields invalid',
                      '\n'.join(self.run_case()['errors']))

    def test_each_physical_stage_requires_one_slot_per_net(self):
        self.source['linked_paths'][0]['stages'][0]['demand_slots'] = 1
        self.assertIn('physical stage rough capacity declaration invalid',
                      '\n'.join(self.run_case()['errors']))
        self.make_second_physical()
        self.source['linked_paths'][0]['stages'][0]['demand_slots'] = 2
        self.source['linked_paths'][0]['stages'][1]['demand_slots'] = 1
        self.assertIn('second physical stage rough capacity declaration invalid',
                      '\n'.join(self.run_case()['errors']))

    def test_second_physical_face_gap_and_missing_return_fail(self):
        self.make_second_physical()
        self.floorplan['placement']['regions']['gap2'] = [7, 10.1, 9, 13]
        self.assertIn('integration face lacks positive non-corner shared edge',
                      '\n'.join(self.run_case()['errors']))
        self.floorplan['placement']['regions']['gap2'] = [7, 10, 9, 13]
        self.source['linked_paths'][0]['stages'][1]['return_obligation'] = {}
        self.assertIn('integration P2 filled-reference return obligation missing',
                      '\n'.join(self.run_case()['errors']))

    def test_second_physical_native_obstacle_fails(self):
        self.make_second_physical()
        footprint(self.board, 'OB', 8, 11, [('1', 'ALT', 0)])
        self.source['p1_fixed_refs'].append('OB')
        self.floorplan['placement']['anchors']['OB'] = [8, 11, 0]
        self.assertIn('native footprint/pad OB intersects integration corridor/face',
                      '\n'.join(self.run_case()['errors']))

    def test_extra_intermediate_pad_is_branch_and_fails(self):
        self.add_pad('E', 3, 'DP', 0)
        self.interfaces['interfaces'][0]['endpoints']['front'].append('E.3')
        self.source['allocations'][0]['endpoints']['DP']['front'].append('E.3')
        path = self.source['linked_paths'][0]
        for stage in path['stages']:
            endpoint = {'source_pad': 'E.3', 'native_pad': 'E.3',
                        'net': 'DP', 'block': 'front'}
            stage['affected'].append(endpoint)
            if stage['kind'] == 'physical_corridor':
                stage['p2_obligations'].append({
                    'status': 'P2_REQUIRED', **endpoint,
                    'corridor_id': stage['id'], 'region_face': 'north',
                    'layer': 'F.Cu', 'to_reservation': stage['reservation_id']})
            else:
                stage['p2_obligations'].append({
                    'status': 'P2_REQUIRED', **endpoint,
                    'stage_id': stage['id'], 'layer': 'F.Cu',
                    'to_reservation': path['reservation_id']})
        path['joins'].append({'from': 'edge_stage', 'to': 'xu_pending',
                              'owner': 'front', 'net': 'DP', 'source_pad': 'E.3',
                              'kind': 'pad_anchored_virtual_interstage'})
        self.assertIn('interstage join multiplicity invalid',
                      '\n'.join(self.run_case()['errors']))

    def test_different_net_path_cannot_reuse_physical_stage(self):
        for ref in ('J', 'E', 'X'):
            self.add_pad(ref, 3, 'ALT', 0)
        self.interfaces['interfaces'].append(
            {'net': 'ALT', 'endpoints': {'edge': ['J.3'],
                                        'front': ['E.3'], 'xmos': ['X.3']}})
        self.source['allocations'].append(
            {'id': 'signal_alt', 'coverage_nets': ['ALT'],
             'demands': [{'id': 'alt', 'nets': ['ALT']}],
             'endpoints': {'ALT': {'edge': ['J.3'], 'front': ['E.3'],
                                   'xmos': ['X.3']}}})
        self.allocations.append(
            {'id': 'signal_alt', 'coverage_nets': ['ALT'],
             'boundary_witnesses': [], 'reservations': [],
             'linked_paths': [{'id': 'series_alt', 'kind': 'linked_path',
                               'nets': ['ALT'], 'status': 'INCOMPLETE'}]})
        alt = copy.deepcopy(self.source['linked_paths'][0])
        alt.update(id='series_alt', allocation_id='signal_alt', nets=['ALT'],
                   reservation_id='series_alt')
        first, second = alt['stages']
        first.update(id='edge_stage_alt', allocation_id='signal_alt',
                     nets=['ALT'], reservation_id='edge_stage_alt_trunk',
                     demand_slots=1)
        first['affected'] = [
            {'source_pad': 'J.3', 'native_pad': 'J.3', 'net': 'ALT', 'block': 'edge'},
            {'source_pad': 'E.3', 'native_pad': 'E.3', 'net': 'ALT', 'block': 'front'}]
        first['p2_obligations'] = [
            {'status': 'P2_REQUIRED', **e, 'corridor_id': 'edge_stage_alt',
             'region_face': 'south' if e['block'] == 'edge' else 'north',
             'layer': 'F.Cu', 'to_reservation': 'edge_stage_alt_trunk'}
            for e in first['affected']]
        first['fixed_accesses'] = [
            {'source_pad': 'J.3', 'native_pad': 'J.3', 'net': 'ALT',
             'block': 'edge', 'face': 'north', 'bbox': [7.8, 4.2, 8.2, 5]}]
        first['return_obligation']['corridor_id'] = 'edge_stage_alt'
        second.update(id='xu_pending_alt', nets=['ALT'])
        second['affected'] = [
            {'source_pad': 'E.3', 'native_pad': 'E.3', 'net': 'ALT', 'block': 'front'},
            {'source_pad': 'X.3', 'native_pad': 'X.3', 'net': 'ALT', 'block': 'xmos'}]
        second['p2_obligations'] = [
            {'status': 'P2_REQUIRED', **e, 'stage_id': 'xu_pending_alt',
             'layer': 'F.Cu', 'to_reservation': 'series_alt'}
            for e in second['affected']]
        second['return_obligation']['stage_id'] = 'xu_pending_alt'
        alt['joins'] = [{'from': 'edge_stage_alt', 'to': 'xu_pending_alt',
                         'owner': 'front', 'net': 'ALT', 'source_pad': 'E.3',
                         'kind': 'pad_anchored_virtual_interstage'}]
        self.source['linked_paths'].append(alt)
        self.assertIn('linked physical stage identity reused',
                      '\n'.join(self.run_case()['errors']))

    def test_segmented_fixed_access_for_physical_stage_pending(self):
        """A source-bound L-shaped fixed access should retain one path credit."""
        self.make_second_physical()
        self.source['linked_paths'][0]['stages'][0]['fixed_accesses'][0].update(
            bbox=[7.3, 4.2, 8.0, 5],
            segments=[[7.3, 4.2, 7.7, 4.5],
                      [7.3, 4.5, 8.0, 4.9],
                      [7.6, 4.9, 8.0, 5]])
        result = self.run_case()
        self.assertEqual(result['errors'], [])

    def make_shared_host_case(self):
        """One disjoint-net ordinary host and one linked three-terminal net."""
        self.make_second_physical()
        path=self.source['linked_paths'][0]
        path['nets']=['DP']
        path['joins']=[j for j in path['joins'] if j['net']=='DP']
        for stage in path['stages']:
            stage['nets']=['DP']
            stage['affected']=[e for e in stage['affected'] if e['net']=='DP']
            stage['p2_obligations']=[e for e in stage['p2_obligations'] if e['net']=='DP']
            if stage['kind']=='physical_corridor':
                stage['fixed_accesses']=[e for e in stage['fixed_accesses'] if e['net']=='DP']
        path['stages'][0]['faces'][1]['bbox']=[7.8,6,8.2,6.2]
        self.source['allocations'][0]['coverage_nets']=['DP']
        self.source['allocations'][0]['demands'][0]['nets']=['DP']
        del self.source['allocations'][0]['endpoints']['DN']
        self.interfaces['interfaces']=[e for e in self.interfaces['interfaces'] if e['net']!='DN']
        self.allocations[0]['coverage_nets']=['DP']
        self.allocations[0]['linked_paths'][0]['nets']=['DP']
        for ref in ('J', 'E'):
            self.add_pad(ref, 3, 'ALT', 0)
        self.interfaces['interfaces'].append(
            {'net':'ALT','endpoints':{'edge':['J.3'],'front':['E.3']}})
        allocation = self.source['allocations'][0]
        allocation['coverage_nets'].append('ALT')
        allocation['demands'].append({'id':'host_demand','nets':['ALT'],'slots':1})
        allocation['endpoints']['ALT']={'edge':['J.3'],'front':['E.3']}
        affected=[{'source_pad':f'{ref}.3','native_pad':f'{ref}.3',
                   'net':'ALT','block':owner}
                  for ref,owner in [('J','edge'),('E','front')]]
        host=copy.deepcopy(self.source['linked_paths'][0]['stages'][0])
        host.update(id='host',nets=['ALT'],reservation_id='host_trunk',
                    affected=affected)
        for key in ('kind','fixed_accesses','axis','slot_pitch_mm','demand_slots'):
            del host[key]
        host['p2_obligations']=[{'status':'P2_REQUIRED',**e,'corridor_id':'host',
            'region_face':'south' if e['block']=='edge' else 'north',
            'layer':'F.Cu','to_reservation':'host_trunk'} for e in affected]
        host['return_obligation']['corridor_id']='host'
        self.source['integration_corridors']=[host]
        row=self.allocations[0]
        row['coverage_nets'].append('ALT')
        row['reservations'] += [
            {'id':'host_trunk','kind':'integration_corridor','corridor_id':'host',
             'owner':'board_integration','region_id':'gap','layer':'F.Cu',
             'bbox':[7,5,9,6],'nets':['ALT']},
            {'id':'host_access','kind':'fixed_connector_access',
             'corridor_id':'host','layer':'F.Cu','bbox':[7.8,4.2,8.2,5],
             'nets':['ALT']}]
        row['boundary_witnesses'] += [
            {'kind':'fixed_connector_access','corridor_id':'host',
             'source':'J.3','native':'J.3','net':'ALT','block':'edge',
             'face':'north','layer':'F.Cu','region_face':'south',
             'boundary_bbox':[7.8,3.8,8.2,4.2],
             'reservation_id':'host_access','p2_obligation':host['p2_obligations'][0]},
            {'kind':'integration_corridor_handoff','corridor_id':'host',
             'source':'E.3','native':'E.3','net':'ALT','block':'front',
             'face':'south','layer':'F.Cu','region_face':'north',
             'boundary_bbox':[7.8,6,8.2,6.2],
             'reservation_id':'host_trunk','p2_obligation':host['p2_obligations'][1]}]
        baseline=self.run_case()
        self.assertIn('physical stage overlaps ordinary reservation',
                      '\n'.join(baseline['errors']))
        path['terminal_count']=3
        path['minimum_tree_edges']=2
        path['tree_obligation']={'status':'P3_REQUIRED','net':'DP',
            'terminal_count':3,'minimum_tree_edges':2,
            'proof':'one_connected_native_net_without_unrelated_branches'}
        self.source['linked_paths'][0]['stages'][0]['shared_with']='host_trunk'

    def test_linked_stage_explicit_host_sharing_pending(self):
        self.make_shared_host_case()
        result=self.run_case()
        self.assertEqual(result['errors'], [], result['allocations'])
        rough=result['allocations'][0]['linked_paths'][0]['stages'][0]['rough_capacity']
        self.assertEqual(rough['nets'], ['ALT', 'DP'])
        self.assertEqual(rough['demand_slots'], 2)

    def test_branch_declaration_without_shared_host_fails(self):
        self.make_shared_host_case()
        del self.source['linked_paths'][0]['stages'][0]['shared_with']
        self.assertIn('branch declaration requires shared host',
                      '\n'.join(self.run_case()['errors']))

    def test_shared_host_selector_geometry_and_net_tamper_fail(self):
        self.make_shared_host_case()
        first=self.source['linked_paths'][0]['stages'][0]
        first['shared_with']='unknown_host'
        self.assertIn('shared host reservation identity/owner invalid',
                      '\n'.join(self.run_case()['errors']))
        first['shared_with']='host_trunk'
        first['faces'][0]['bbox']=[7.1,4.8,9,5]
        self.assertIn('shared host source/geometry mismatch',
                      '\n'.join(self.run_case()['errors']))
        first['faces'][0]['bbox']=[7,4.8,9,5]
        self.allocations[0]['reservations'][0]['nets']=['DP']
        self.assertIn('linked path net has competing ordinary credit/witness',
                      '\n'.join(self.run_case()['errors']))

    def test_shared_host_joint_demand_and_tree_tamper_fail(self):
        self.make_shared_host_case()
        path=self.source['linked_paths'][0]
        first=path['stages'][0]
        first['demand_slots']=1
        self.assertIn('physical stage rough capacity declaration invalid',
                      '\n'.join(self.run_case()['errors']))
        first['demand_slots']=2
        path['terminal_count']=4
        self.assertIn('shared branch terminal/tree denominator mismatch',
                      '\n'.join(self.run_case()['errors']))
        path['terminal_count']=3
        path['minimum_tree_edges']=1
        self.assertIn('shared branch terminal/tree denominator mismatch',
                      '\n'.join(self.run_case()['errors']))
        path['minimum_tree_edges']=2
        path['stages'][1]['affected'].pop()
        self.assertIn('integration endpoint denominator mismatch',
                      '\n'.join(self.run_case()['errors']))

    def test_shared_host_p2_and_return_tamper_fail(self):
        self.make_shared_host_case()
        first=self.source['linked_paths'][0]['stages'][0]
        first['p2_obligations'].pop()
        self.assertIn('integration P2 pad-to-face obligations incomplete',
                      '\n'.join(self.run_case()['errors']))
        endpoint=first['affected'][-1]
        first['p2_obligations'].append({'status':'P2_REQUIRED',**endpoint,
            'corridor_id':first['id'],'region_face':'north',
            'layer':'F.Cu','to_reservation':first['reservation_id']})
        first['return_obligation']={}
        self.assertIn('integration P2 filled-reference return obligation missing',
                      '\n'.join(self.run_case()['errors']))

    def test_segmented_fixed_access_disconnection_and_pad_hit_fail(self):
        self.make_second_physical()
        access=self.source['linked_paths'][0]['stages'][0]['fixed_accesses'][0]
        access.update(bbox=[7.3,4.2,8.0,5],
                      segments=[[7.3,4.2,7.7,4.5],
                                [7.3,4.5,8.0,4.9],
                                [7.6,4.9,8.0,5]])
        access['segments'][1][1]=4.55
        self.assertIn('disconnected or overlapping waypoints',
                      '\n'.join(self.run_case()['errors']))
        access['segments'][1][1]=4.5
        footprint(self.board,'OB',7.5,4.3,[('1','ALT',0)])
        self.source['p1_fixed_refs'].append('OB')
        self.floorplan['placement']['anchors']['OB']=[7.5,4.3,0]
        self.assertIn('fixed access intersects native body OB',
                      '\n'.join(self.run_case()['errors']))


if __name__ == '__main__':
    unittest.main()
