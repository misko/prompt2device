"""Exact fixed north-edge courtyard-only physical-cell controls."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
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
POWER_BOARD = (Path(__file__).resolve().parents[4] / 'projects/crow-usb-carrier-v1/'
               '01_docs/research/2026-09-25-ti-cin3-qpre-owner-repair-sol/candidate.kicad_pcb')
AUTHORITY_PATH = (Path(__file__).resolve().parents[4] / 'projects/crow-usb-carrier-v1/'
                  '03_src/rules/physical_cell_edge_authority.json')
AUTHORITY_SHA256 = '0b60dece42aca3e84b085fd0c30847dd358a5f96dd2e26773a6b75eb22b494b4'
AUTHORITY = checker._load_edge_authority(AUTHORITY_PATH, AUTHORITY_SHA256)
PARTS = {row['ref']: row for row in AUTHORITY['connectors']}
D0_SHA256 = AUTHORITY['board_subjects'][0]['board_sha256']
POWER_SHA256 = AUTHORITY['board_subjects'][1]['board_sha256']
OUTLINE_SHA256 = AUTHORITY['board_subjects'][0]['outline_sha256']


def attachment(ref, cell_id=None):
    part = PARTS[ref]
    return {'ref': ref, 'physical_cell_id': cell_id or ref.lower() + '_edge',
            'edge': 'north', 'board_sha256': D0_SHA256,
            'outline_sha256': OUTLINE_SHA256,
            'footprint_sha256': part['footprint_sha256'],
            'drawing_sha256': part['drawing_sha256'],
            'pose_mm': part['pose_mm'], 'maximum_courtyard_projection_mm': 0.045}


class EdgeAttachment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.board = pcbnew.LoadBoard(str(BOARD))
        cls.outline = pcbnew.SHAPE_POLY_SET()
        assert cls.board.GetBoardPolygonOutlines(cls.outline, False)
        cls.native = {fp.GetReference(): fp for fp in cls.board.GetFootprints()}
        assert checker.digest(BOARD) == D0_SHA256

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
                                       regions, patterns, D0_SHA256, AUTHORITY)

    def test_exact_fixed_connector_cells_only(self):
        for ref in PARTS:
            with self.subTest(ref=ref):
                source = self.source(ref)
                cells = self.cell(source, ref)
                self.assertEqual(set(cells), {source['physical_cells'][0]['id']})
                self.assertFalse(checker.lane_inside_outline(
                    self.outline, cells[source['physical_cells'][0]['id']]['bbox']))

    def test_separately_pinned_power_board_has_same_nine_edge_cells(self):
        self.assertEqual(checker.digest(POWER_BOARD), POWER_SHA256)
        board = pcbnew.LoadBoard(str(POWER_BOARD))
        outline = pcbnew.SHAPE_POLY_SET()
        self.assertTrue(board.GetBoardPolygonOutlines(outline, False))
        self.assertEqual(checker._edge_outline_digest(outline), OUTLINE_SHA256)
        native = {fp.GetReference(): fp for fp in board.GetFootprints()}
        self.assertEqual(len(native), 569)
        for ref in PARTS:
            with self.subTest(ref=ref):
                self.assertEqual(checker._physical_envelope(native[ref]),
                                 checker._physical_envelope(self.native[ref]))
                source = self.source(ref)
                source['physical_cell_edge_attachments'][0]['board_sha256'] = (
                    POWER_SHA256)
                cell_id = source['physical_cells'][0]['id']
                area = list(checker._physical_envelope(native[ref]))
                cells = checker._physical_cells(
                    source, {'blocks': [{'id': 'owner', 'refs': [ref]}]},
                    board, outline, {cell_id: area},
                    [{'match': [ref], 'region': cell_id}],
                    POWER_SHA256, AUTHORITY)
                self.assertEqual(set(cells), {cell_id})
        stale = self.source('J_PWR')
        cell_id = stale['physical_cells'][0]['id']
        with self.assertRaisesRegex(checker.ContractError, 'identity/direction'):
            checker._physical_cells(
                stale, {'blocks': [{'id': 'owner', 'refs': ['J_PWR']}]}, board,
                outline, {cell_id: list(checker._physical_envelope(native['J_PWR']))},
                [{'match': ['J_PWR'], 'region': cell_id}],
                POWER_SHA256, AUTHORITY)

    def test_wrong_authority_and_claims_fail_closed(self):
        with self.assertRaisesRegex(checker.ContractError, 'independently pinned authority'):
            checker._physical_cells(self.source(), {'blocks': [{'id': 'owner', 'refs': ['J1']}]},
                                    self.board, self.outline,
                                    {'j1_edge': list(checker._physical_envelope(self.native['J1']))},
                                    [{'match': ['J1'], 'region': 'j1_edge'}], D0_SHA256)
        with self.assertRaisesRegex(checker.ContractError, 'independent expected digest'):
            checker._load_edge_authority(AUTHORITY_PATH, None)
        with self.assertRaisesRegex(checker.ContractError, 'digest mismatch'):
            checker._load_edge_authority(AUTHORITY_PATH, '0' * 64)
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
                                    self.outline, {}, [], D0_SHA256, AUTHORITY)
        with self.assertRaises(checker.ContractError):
            checker._physical_cell_edge_attachments(self.source(), self.board,
                                                    self.outline, '0'*64, AUTHORITY)

    def test_non_crow_synthetic_project_authority(self):
        def mm(value):
            return pcbnew.FromMM(value)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            board = pcbnew.BOARD()
            corners = [(0, 0), (100, 0), (100, 100), (0, 100)]
            for a, b in zip(corners, corners[1:] + corners[:1]):
                edge = pcbnew.PCB_SHAPE(board)
                edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
                edge.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
                edge.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
                edge.SetLayer(pcbnew.Edge_Cuts)
                board.Add(edge)
            fp = pcbnew.FOOTPRINT(board)
            fp.SetReference('J_SYN')
            fp.SetFPIDAsString('fixture:SyntheticEdge')
            fp.SetPosition(pcbnew.VECTOR2I(mm(50), mm(5)))
            board.Add(fp)
            for layer, points in ((pcbnew.F_CrtYd, [(48, .05), (52, .05),
                                                    (52, 8), (48, 8)]),
                                  (pcbnew.F_Fab, [(48, .5), (52, .5),
                                                 (52, 8), (48, 8)])):
                for a, b in zip(points, points[1:] + points[:1]):
                    line = pcbnew.PCB_SHAPE(fp)
                    line.SetShape(pcbnew.SHAPE_T_SEGMENT)
                    line.SetStart(pcbnew.VECTOR2I(mm(a[0]), mm(a[1])))
                    line.SetEnd(pcbnew.VECTOR2I(mm(b[0]), mm(b[1])))
                    line.SetLayer(layer)
                    line.SetWidth(mm(.1))
                    fp.Add(line)
            pad = pcbnew.PAD(fp)
            pad.SetNumber('1')
            pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
            pad.SetShape(pcbnew.PAD_SHAPE_RECT)
            pad.SetSize(pcbnew.VECTOR2I(mm(1), mm(1)))
            pad.SetPosition(pcbnew.VECTOR2I(mm(50), mm(4)))
            pad.SetLayerSet(pcbnew.LSET.FrontMask())
            fp.Add(pad)
            fp.BuildCourtyardCaches()
            outline = pcbnew.SHAPE_POLY_SET()
            self.assertTrue(board.GetBoardPolygonOutlines(outline, False))
            board_path = root / 'synthetic.kicad_pcb'
            pcbnew.SaveBoard(str(board_path), board)
            for name in ('footprint.kicad_mod', 'drawing.pdf', 'review.md'):
                (root / name).write_bytes(('synthetic ' + name).encode())
            board_sha = checker.digest(board_path)
            record = {'schema': 1,
                      'kind': 'physical-cell-north-edge-courtyard-authority',
                      'scope': 'single-fixed-connector-courtyard-only',
                      'board_subjects': [{'board_sha256': board_sha,
                                          'outline_sha256': checker._edge_outline_digest(outline),
                                          'outline_bbox_mm': [0, 0, 100, 100]}],
                      'review_provenance': [{'path': 'review.md', 'board_sha256': board_sha,
                                             'sha256': checker.digest(root / 'review.md')}],
                      'connectors': [{'ref': 'J_SYN', 'edge': 'north',
                                      'pose_mm': [50, 5, 0],
                                      'footprint_lib_item': 'SyntheticEdge',
                                      'footprint_path': 'footprint.kicad_mod',
                                      'footprint_sha256': checker.digest(root / 'footprint.kicad_mod'),
                                      'drawing_path': 'drawing.pdf',
                                      'drawing_sha256': checker.digest(root / 'drawing.pdf'),
                                      'maximum_courtyard_projection_mm': .045}]}
            manifest = root / 'authority.json'
            manifest.write_text(json.dumps(record))
            with self.assertRaises(checker.ContractError):
                checker._load_edge_authority(manifest, None)
            authority = checker._load_edge_authority(manifest, checker.digest(manifest))
            item = record['connectors'][0]
            claim = {'ref': 'J_SYN', 'physical_cell_id': 'synthetic_edge',
                     'edge': 'north', 'board_sha256': board_sha,
                     'outline_sha256': record['board_subjects'][0]['outline_sha256'],
                     'footprint_sha256': item['footprint_sha256'],
                     'drawing_sha256': item['drawing_sha256'],
                     'pose_mm': item['pose_mm'],
                     'maximum_courtyard_projection_mm': .045}
            source = {'p1_fixed_refs': ['J_SYN'],
                      'physical_cell_edge_attachments': [claim],
                      'physical_cells': [{'id': 'synthetic_edge',
                                          'owner_block': 'synthetic_owner',
                                          'refs': ['J_SYN'], 'transit': False}]}
            region = {'synthetic_edge': list(checker._physical_envelope(fp))}
            plan = {'blocks': [{'id': 'synthetic_owner', 'refs': ['J_SYN']}]}
            patterns = [{'match': ['J_SYN'], 'region': 'synthetic_edge'}]
            cells = checker._physical_cells(source, plan, board, outline,
                                            region, patterns, board_sha, authority)
            self.assertEqual(set(cells), {'synthetic_edge'})
            (root / 'review.md').write_text('changed after review')
            with self.assertRaisesRegex(checker.ContractError, 'review provenance drift'):
                checker._load_edge_authority(manifest, checker.digest(manifest))

    def test_offboard_pads_drills_material_and_excess_cell_fail(self):
        source = self.source('J_PWR')
        ref = 'J_PWR'
        cell = source['physical_cells'][0]['id']
        plan = {'blocks': [{'id': 'owner', 'refs': [ref]}]}
        patterns = [{'match': [ref], 'region': cell}]
        def check(board, area):
            return checker._physical_cells(source, plan, board, self.outline,
                                           {cell: area}, patterns,
                                           D0_SHA256, AUTHORITY)
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
