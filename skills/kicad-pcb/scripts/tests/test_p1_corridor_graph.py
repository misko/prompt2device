#!/usr/bin/env python3
"""Native topology fixtures for schema-2 P1 graph screening."""
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
import p1_corridor_graph as checker  # noqa: E402


def iu(mm):
    return pcbnew.FromMM(mm)


def add_pad(board, ref, number, net, x, y, size=0.5):
    fp = next((f for f in board.GetFootprints() if f.GetReference() == ref), None)
    if fp is None:
        fp = pcbnew.FOOTPRINT(board)
        fp.SetReference(ref)
        fp.SetValue('fixture')
        fp.SetLayer(pcbnew.F_Cu)
        fp.SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
        board.Add(fp)
    pad = pcbnew.PAD(fp)
    pad.SetNumber(number)
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(pcbnew.VECTOR2I(iu(size), iu(size)))
    pad.SetPosition(pcbnew.VECTOR2I(iu(x), iu(y)))
    pad.SetLayerSet(pcbnew.LSET.FrontMask())
    native_net = board.FindNet(net)
    if native_net is None:
        native_net = pcbnew.NETINFO_ITEM(board, net)
        board.Add(native_net)
    pad.SetNet(native_net)
    fp.Add(pad)
    return fp


class GraphContractTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.board = pcbnew.BOARD()
        edge = [(0, 0), (10, 0), (10, 10), (0, 10)]
        for a, b in zip(edge, edge[1:] + edge[:1]):
            segment = pcbnew.PCB_SHAPE(self.board)
            segment.SetShape(pcbnew.SHAPE_T_SEGMENT)
            segment.SetStart(pcbnew.VECTOR2I(iu(a[0]), iu(a[1])))
            segment.SetEnd(pcbnew.VECTOR2I(iu(b[0]), iu(b[1])))
            segment.SetLayer(pcbnew.Edge_Cuts)
            self.board.Add(segment)
        add_pad(self.board, 'J_USB', 'A6', 'TEST', 2, 5)
        add_pad(self.board, 'J_USB', 'B5', 'OTHER', 3, 5)
        add_pad(self.board, 'J_RIGHT', '1', 'TEST', 8, 5)
        add_pad(self.board, 'J_TOP', '1', 'TEST', 5, 8)
        add_pad(self.board, 'J_G1', '1', 'GND', 2, 2)
        add_pad(self.board, 'J_G2', '1', 'GND', 8, 2)
        self.source = {'schema': 1, 'kind': 'crow-p1-corridor-requirements',
                       'allocations': [{'id': 'signal', 'coverage_nets': ['TEST'],
                                        'endpoints': {'TEST': {'owner': ['J_USB.4', 'J_RIGHT.1', 'J_TOP.1']}}}],
                       'power_boundary_windows': {'coverage_nets': ['GND']}}
        self.interfaces = {'interfaces': [
            {'net': 'TEST', 'endpoints': {'owner': ['J_USB.4', 'J_RIGHT.1', 'J_TOP.1']}},
            {'net': 'GND', 'endpoints': {'owner': ['J_G1.1', 'J_G2.1']}}]}
        self.aliases = {'pin_aliases': {'A6': {'schematic': '4', 'footprint': 'A6'}}}
        self.signal = {
            'id': 'signal', 'coverage_nets': ['TEST'],
            'terminals': [{'source': 'J_USB.4', 'native': 'J_USB.A6', 'net': 'TEST'},
                          {'source': 'J_RIGHT.1', 'native': 'J_RIGHT.1', 'net': 'TEST'},
                          {'source': 'J_TOP.1', 'native': 'J_TOP.1', 'net': 'TEST'}],
            'pockets': [
                {'id': 'left', 'source': 'J_USB.4', 'net': 'TEST', 'layer': 'F.Cu', 'bbox': [1.5, 4.5, 2.6, 5.5]},
                {'id': 'right', 'source': 'J_RIGHT.1', 'net': 'TEST', 'layer': 'F.Cu', 'bbox': [7.5, 4.5, 8.5, 5.5]},
                {'id': 'top', 'source': 'J_TOP.1', 'net': 'TEST', 'layer': 'F.Cu', 'bbox': [4.5, 7.5, 5.5, 8.5]}],
            'junctions': [{'id': 'tee', 'layer': 'F.Cu', 'bbox': [4.75, 4.75, 5.25, 5.25], 'nets': ['TEST']}],
            'segments': [
                {'id': 'left_arm', 'layer': 'F.Cu', 'bbox': [2.25, 4.75, 5, 5.25], 'ports': ['left', 'tee'], 'nets': ['TEST']},
                {'id': 'right_arm', 'layer': 'F.Cu', 'bbox': [5, 4.75, 7.75, 5.25], 'ports': ['tee', 'right'], 'nets': ['TEST']},
                {'id': 'top_arm', 'layer': 'F.Cu', 'bbox': [4.75, 5, 5.25, 7.75], 'ports': ['tee', 'top'], 'nets': ['TEST']}],
        }
        self.power = {'id': 'power_boundary_windows', 'coverage_nets': ['GND'],
                      'terminals': [{'source': 'J_G1.1', 'native': 'J_G1.1', 'net': 'GND'},
                                    {'source': 'J_G2.1', 'native': 'J_G2.1', 'net': 'GND'}]}

    def run_case(self, mutate=None):
        if mutate:
            mutate()
        board = self.root / 'board.kicad_pcb'
        source = self.root / 'source.yaml'
        interfaces = self.root / 'interfaces.json'
        aliases = self.root / 'aliases.yaml'
        contract = self.root / 'contract.json'
        pcbnew.SaveBoard(str(board), self.board)
        source.write_text(yaml.safe_dump(self.source))
        interfaces.write_text(json.dumps(self.interfaces))
        aliases.write_text(yaml.safe_dump(self.aliases))
        payload = {'schema': 2, 'kind': 'p1-corridor-graph',
                   'board_sha256': checker.digest(board), 'source_sha256': checker.digest(source),
                   'interfaces_sha256': checker.digest(interfaces), 'aliases_sha256': checker.digest(aliases),
                   'allocations': [self.signal, self.power]}
        contract.write_text(json.dumps(payload))
        return checker.evaluate(board, contract, source, interfaces, aliases,
                                checker.digest(contract), checker.digest(source),
                                checker.digest(interfaces), checker.digest(aliases))

    def test_connected_branch_is_only_topology_complete(self):
        result = self.run_case()
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertEqual(result['errors'], [])
        self.assertFalse(result['p1_accepted'])
        self.assertEqual(result['allocations'][0]['segment_count'], 3)
        self.assertIn('J_USB.B5', result['allocations'][0]['segments'][0]['obstacle_pads'])

    def test_missing_branch_terminal_is_rejected(self):
        result = self.run_case(lambda: self.signal['segments'].pop())
        self.assertIn('does not reach every terminal', result['allocations'][0]['reason'])

    def test_wrong_alias_is_rejected(self):
        result = self.run_case(lambda: self.signal['terminals'][0].update(native='J_USB.B6'))
        self.assertIn('alias mismatch', result['allocations'][0]['reason'])

    def test_off_board_ordinary_pocket_is_rejected(self):
        result = self.run_case(lambda: self.signal['pockets'][0].update(bbox=[-0.1, 4.5, 2.6, 5.5]))
        self.assertIn('pocket off board', result['allocations'][0]['reason'])

    def test_turn_layer_mismatch_is_rejected(self):
        result = self.run_case(lambda: self.signal['segments'][2].update(layer='B.Cu'))
        self.assertIn('layer-mismatched', result['allocations'][0]['reason'])

    def test_bogus_edge_datum_is_rejected(self):
        self.signal['pockets'][0]['kind'] = 'edge_connector'
        self.signal['pockets'][0]['edge_datum'] = {'footprint_id': 'fixture:USB',
                                                  'drawing_ref': 'fixture drawing edge datum',
                                                  'outline_edge': [[0, 0], [0, 10]],
                                                  'mouth': [1, 5], 'mouth_local': [-1, 0],
                                                  'mouth_to_edge_mm': 1,
                                                  'tolerance_mm': 0.05, 'max_overhang_mm': 1}
        result = self.run_case()
        self.assertIn('edge footprint identity mismatch', result['allocations'][0]['reason'])

    def test_edge_datum_accepts_bound_overhang_but_bad_mouth_fails(self):
        fp = next(f for f in self.board.GetFootprints() if f.GetReference() == 'J_USB')
        fp.SetFPIDAsString('fixture:USB')
        add_pad(self.board, 'J_USB', 'SHELL', 'OTHER', -0.1, 5, size=0.2)
        pocket = self.signal['pockets'][0]
        pocket['kind'] = 'edge_connector'
        pocket['edge_datum'] = {'footprint_id': 'fixture:USB',
                               'drawing_ref': 'fixture drawing edge datum',
                               'outline_edge': [[0, 0], [0, 10]],
                               'mouth': [0.5, 5], 'mouth_local': [-1.5, 0],
                               'mouth_to_edge_mm': 0.5, 'tolerance_mm': 0.05,
                               'max_overhang_mm': 0.3}
        result = self.run_case()
        self.assertEqual(result['allocations'][0]['segment_count'], 3)
        pocket['edge_datum']['mouth_local'] = [-1, 0]
        result = self.run_case()
        self.assertIn('does not follow native footprint transform', result['allocations'][0]['reason'])

    def test_live_crow_source_has_exact_59_net_partition(self):
        project = Path(__file__).resolve().parents[4] / 'projects/crow-usb-carrier-v1'
        source = yaml.safe_load((project / '03_src/rules/p1_corridor_requirements.yaml').read_text())
        interfaces = json.loads((project / '03_src/modular_plan.json').read_text())
        coverage, terminals = checker.source_inventory(source, interfaces)
        self.assertEqual(len(terminals), 59)
        self.assertEqual([len(coverage[name]) for name in
                          ('usb_device_pair', 'xmos_service_escape', 'adc_timing_xmos_bundle',
                           'adc_analog_boundary', 'power_boundary_windows')], [4, 13, 14, 18, 10])

    def test_contract_hash_drift_is_rejected(self):
        result = self.run_case()
        self.assertEqual(result['errors'], [])
        board = self.root / 'board.kicad_pcb'
        contract = self.root / 'contract.json'
        source = self.root / 'source.yaml'
        interfaces = self.root / 'interfaces.json'
        aliases = self.root / 'aliases.yaml'
        result = checker.evaluate(board, contract, source, interfaces, aliases,
                                  '0' * 64, checker.digest(source), checker.digest(interfaces), checker.digest(aliases))
        self.assertIn('contract hash not bound', '\n'.join(result['errors']))


if __name__ == '__main__':
    unittest.main()
