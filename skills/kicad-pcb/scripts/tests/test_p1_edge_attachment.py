"""Exact fixed north-edge courtyard-only physical-cell controls."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

SCRIPT = Path(__file__).resolve().parents[1] / 'p1_corridor_capacity.py'
spec = importlib.util.spec_from_file_location('edge_checker', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
BOARD = (Path(__file__).resolve().parents[4] / 'projects/crow-usb-carrier-v1/'
         '01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb')


def attachment(ref, cell_id=None):
    part = checker._EDGE_PARTS[ref]
    return {'ref': ref, 'physical_cell_id': cell_id or ref.lower() + '_edge',
            'edge': 'north', 'board_sha256': checker._EDGE_BOARD_SHA256,
            'outline_sha256': checker._EDGE_OUTLINE_SHA256,
            'footprint_sha256': part[2], 'drawing_sha256': part[3],
            'pose_mm': list(part[4]), 'maximum_courtyard_projection_mm': 0.045}


class EdgeAttachment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.board = pcbnew.LoadBoard(str(BOARD))
        cls.outline = pcbnew.SHAPE_POLY_SET()
        assert cls.board.GetBoardPolygonOutlines(cls.outline, False)
        cls.native = {fp.GetReference(): fp for fp in cls.board.GetFootprints()}
        assert checker.digest(BOARD) == checker._EDGE_BOARD_SHA256

    def source(self, ref='J1'):
        row = attachment(ref)
        return {'physical_cell_edge_attachments': [row], 'p1_fixed_refs': [ref],
                'physical_cells': [{'id': row['physical_cell_id'], 'owner_block': 'owner',
                                    'refs': [ref], 'transit': False}]}

    def cell(self, source, ref):
        cell_id = source['physical_cells'][0]['id']
        envelope = checker._physical_envelope(self.native[ref])
        regions = {cell_id: list(envelope)}
        plan = {'blocks': [{'id': 'owner', 'refs': [ref]}]}
        patterns = [{'match': [ref], 'region': cell_id}]
        return checker._physical_cells(source, plan, self.board, self.outline,
                                       regions, patterns, checker._EDGE_BOARD_SHA256)

    def test_exact_fixed_connector_cells_only(self):
        for ref in checker._EDGE_PARTS:
            with self.subTest(ref=ref):
                source = self.source(ref)
                cells = self.cell(source, ref)
                self.assertEqual(set(cells), {source['physical_cells'][0]['id']})
                self.assertFalse(checker.lane_inside_outline(
                    self.outline, cells[source['physical_cells'][0]['id']]['bbox']))

    def test_wrong_authority_and_claims_fail_closed(self):
        for label, mutate in {
            'wrong_board': lambda s: s['physical_cell_edge_attachments'][0].update(board_sha256='0'*64),
            'wrong_outline': lambda s: s['physical_cell_edge_attachments'][0].update(outline_sha256='0'*64),
            'wrong_footprint': lambda s: s['physical_cell_edge_attachments'][0].update(footprint_sha256='0'*64),
            'wrong_drawing': lambda s: s['physical_cell_edge_attachments'][0].update(drawing_sha256='0'*64),
            'wrong_pose': lambda s: s['physical_cell_edge_attachments'][0].update(pose_mm=[50, 27, 0]),
            'wrong_direction': lambda s: s['physical_cell_edge_attachments'][0].update(edge='south'),
            'projection_046': lambda s: s['physical_cell_edge_attachments'][0].update(maximum_courtyard_projection_mm=0.046),
            'not_fixed': lambda s: s.update(p1_fixed_refs=[]),
            'capacity': lambda s: s['physical_cell_edge_attachments'][0].update(capacity_slots=1),
            'pass': lambda s: s['physical_cell_edge_attachments'][0].update(status='PASS'),
            'full': lambda s: s['physical_cell_edge_attachments'][0].update(connector_full='PASS'),
            'extra_ref': lambda s: s['physical_cells'][0]['refs'].append('J2'),
        }.items():
            with self.subTest(label=label):
                source = self.source()
                mutate(source)
                with self.assertRaises(checker.ContractError):
                    self.cell(source, 'J1')
        source = self.source()
        source['physical_cell_edge_attachments'][0]['ref'] = 'J_USB'
        with self.assertRaises(checker.ContractError):
            self.cell(source, 'J1')
        source = self.source()
        source.pop('physical_cells')
        with self.assertRaises(checker.ContractError):
            checker._physical_cells(source, {'blocks': []}, self.board,
                                    self.outline, {}, [], checker._EDGE_BOARD_SHA256)
        with self.assertRaises(checker.ContractError):
            checker._physical_cell_edge_attachments(self.source(), self.board,
                                                    self.outline, '0'*64)

    def test_offboard_pads_drills_material_and_excess_cell_fail(self):
        source = self.source('J_PWR')
        ref = 'J_PWR'
        cell = source['physical_cells'][0]['id']
        plan = {'blocks': [{'id': 'owner', 'refs': [ref]}]}
        patterns = [{'match': [ref], 'region': cell}]
        def check(board, area):
            return checker._physical_cells(source, plan, board, self.outline,
                                           {cell: area}, patterns,
                                           checker._EDGE_BOARD_SHA256)
        base = list(checker._physical_envelope(self.native[ref]))
        with self.assertRaises(checker.ContractError):
            check(self.board, [base[0], 19.954, base[2], base[3]])
        board = pcbnew.LoadBoard(str(BOARD))
        fp = next(f for f in board.GetFootprints() if f.GetReference() == ref)
        pad = next(iter(fp.Pads()))
        pad.SetPosition(pcbnew.VECTOR2I(pad.GetPosition().x, pcbnew.FromMM(19.5)))
        with self.assertRaises(checker.ContractError):
            check(board, base)
        board = pcbnew.LoadBoard(str(BOARD))
        fp = next(f for f in board.GetFootprints() if f.GetReference() == ref)
        pad = next(p for p in fp.Pads() if p.HasHole())
        pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(50), pcbnew.FromMM(50)))
        with self.assertRaises(checker.ContractError):
            check(board, base)
        board = pcbnew.LoadBoard(str(BOARD))
        fp = next(f for f in board.GetFootprints() if f.GetReference() == ref)
        fab = next(i for i in fp.GraphicalItems()
                   if i.GetLayer() == pcbnew.F_Fab and i.GetClass() != 'PCB_TEXT')
        fab.Move(pcbnew.VECTOR2I(0, -pcbnew.FromMM(2)))
        with self.assertRaises(checker.ContractError):
            check(board, base)
        board = pcbnew.LoadBoard(str(BOARD))
        fp = next(f for f in board.GetFootprints() if f.GetReference() == ref)
        extra = pcbnew.PCB_SHAPE(fp)
        extra.SetShape(pcbnew.SHAPE_T_RECT)
        extra.SetLayer(pcbnew.F_CrtYd)
        extra.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(38), pcbnew.FromMM(19.96)))
        extra.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(39), pcbnew.FromMM(20.5)))
        fp.Add(extra)
        fp.BuildCourtyardCaches()
        with self.assertRaisesRegex(checker.ContractError, 'extra exterior lobe'):
            check(board, base)


if __name__ == '__main__':
    unittest.main()
