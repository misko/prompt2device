"""Exclusive-cell census tests; rough planning regions remain nonexclusive."""
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
import source_region_ownership as census  # noqa: E402


def add_pad(board, ref, x, y):
    fp = pcbnew.FOOTPRINT(board)
    fp.SetReference(ref)
    fp.SetValue('fixture')
    fp.SetLayer(pcbnew.F_Cu)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    fp.Reference().SetVisible(False)
    fp.Value().SetVisible(False)
    pad = pcbnew.PAD(fp)
    pad.SetNumber('1')
    pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    pad.SetShape(pcbnew.PAD_SHAPE_RECT)
    pad.SetSize(pcbnew.VECTOR2I(pcbnew.FromMM(.5), pcbnew.FromMM(.5)))
    pad.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    pad.SetLayerSet(pcbnew.LSET.FrontMask())
    fp.Add(pad)
    board.Add(fp)


class SourceRegionOwnershipTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.board = pcbnew.BOARD()
        add_pad(self.board, 'U_A', 2, 2)
        add_pad(self.board, 'U_B', 8, 2)
        self.floorplan = {'placement': {'regions': {'a': [1, 1, 3, 3],
                                                    'b': [7, 1, 9, 3]}}}
        self.modular = {'blocks': [{'id': 'a', 'refs': ['U_A']},
                                   {'id': 'b', 'refs': ['U_B']}]}
        self.source = {}

    def run_case(self):
        paths = {name: self.root / name for name in
                 ('board.kicad_pcb', 'floorplan.yaml', 'modular.json', 'source.yaml')}
        pcbnew.SaveBoard(str(paths['board.kicad_pcb']), self.board)
        paths['floorplan.yaml'].write_text(yaml.safe_dump(self.floorplan))
        paths['modular.json'].write_text(json.dumps(self.modular))
        paths['source.yaml'].write_text(yaml.safe_dump(self.source))
        expected = {name: census.digest(path) for name, path in zip(
            ('board', 'floorplan', 'modular', 'source'), paths.values())}
        return census.evaluate(*paths.values(), expected)

    def test_rough_regions_are_not_exclusive_without_opt_in(self):
        self.floorplan['placement']['regions']['a'] = [0, 0, 10, 5]
        result = self.run_case()
        self.assertEqual(result['status'], 'NOT_APPLICABLE')
        self.assertEqual(result['findings'], [])
        self.assertIn(('a', 'foreign_inside', 'U_B'),
                      {(f['cell'], f['kind'], f['ref'])
                       for f in result['planning_observations']})

    def test_exclusive_cells_pass_with_exact_occupants(self):
        self.source['physical_cells'] = [
            {'id': 'a', 'owner_block': 'a', 'refs': ['U_A'], 'transit': False},
            {'id': 'b', 'owner_block': 'b', 'refs': ['U_B'], 'transit': False}]
        result = self.run_case()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['findings'], [])
        self.assertFalse(result['p1_accepted'])

    def test_reports_all_owned_outside_and_foreign_inside(self):
        self.source['physical_cells'] = [
            {'id': 'a', 'owner_block': 'a', 'refs': ['U_A'], 'transit': False},
            {'id': 'b', 'owner_block': 'b', 'refs': ['U_B'], 'transit': False}]
        self.floorplan['placement']['regions']['a'] = [3, 1, 9, 3]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn(('a', 'owned_outside', 'U_A'),
                      {(f['cell'], f['kind'], f['ref']) for f in result['findings']})
        self.assertIn(('a', 'foreign_inside', 'U_B'),
                      {(f['cell'], f['kind'], f['ref']) for f in result['findings']})

    def test_wrong_modular_owner_fails_even_when_geometry_fits(self):
        self.source['physical_cells'] = [
            {'id': 'a', 'owner_block': 'a', 'refs': ['U_B'], 'transit': False}]
        result = self.run_case()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('not owned by a', '\n'.join(result['errors']))

    def test_changed_board_hash_fails_before_census(self):
        self.run_case()
        paths = [self.root / name for name in
                 ('board.kicad_pcb', 'floorplan.yaml', 'modular.json', 'source.yaml')]
        expected = {name: census.digest(path) for name, path in zip(
            ('board', 'floorplan', 'modular', 'source'), paths)}
        expected['board'] = '0' * 64
        result = census.evaluate(*paths, expected)
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('board not bound', '\n'.join(result['errors']))


if __name__ == '__main__':
    unittest.main()
