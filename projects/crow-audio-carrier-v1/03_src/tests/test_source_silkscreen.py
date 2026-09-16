"""Local source-silk regressions; not full placement or printed-board acceptance.

September 8 native DRC identified D_IN/L_BUCK own-pad clipping and J9 silk
beyond the board edge. These tests were run RED on the unedited libraries at
8d542d4c before repair. The old exact source remains the hostile fixture.
Native effective shapes grade authored graphics; no emitter geometry is used.
The current source is deliberately reopened to catch future source regressions.
"""
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

import pcbnew
import yaml

SRC = Path(__file__).resolve().parents[1]
ROOT = SRC.parents[2]
LIB = SRC/'lib/crow_audio_carrier.pretty'
BASE = '8d542d4ccb5aace11648aed7551fc752754e31e4'
NAMES = ('Littelfuse_SMBJ15A_SMB_Exact', 'Coilcraft_XGL4020_Exact',
         'Molex_43650-0200_RA_Exact')
CHANNEL_TEXTS = {f'CH{i}' for i in range(1,9)}
LEGACY_BANK_TEXT = 'J1-J8: 1 +12V  2 GND  3 AUDIO+  4 AUDIO-'
BANK_TEXT = 'POD AUDIO +12V / NOT ETHERNET OR POE'
CAPTION_TEXTS = {
    'CROW AUDIO CARRIER v1  FIRST ARTICLE / DO NOT ORDER',
    BANK_TEXT,
    'J10=MCH J1 TDM   J11=MCH J3 SENSE   DO NOT SWAP',
    'J9: 12V ISOLATED INPUT; NO HOT PLUG', 'CH3',
}
LEGACY_CAPTION_TEXTS = CAPTION_TEXTS - {BANK_TEXT} | {LEGACY_BANK_TEXT}


def old_source(name):
    path = (LIB/(name+'.kicad_mod')).relative_to(ROOT)
    return subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT,text=True,timeout=15)


def source_projection(text):
    """Keep every non-silk node, including pads, mask, fab, courtyard and model."""
    tokens = re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',text)
    stack, roots = [], []
    for token in tokens:
        if token == '(':
            node = []
            (stack[-1] if stack else roots).append(node)
            stack.append(node)
        elif token == ')':
            assert stack
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert len(roots) == 1 and not stack
    return [r for r in roots[0] if not (isinstance(r,list) and
            r[0].startswith('fp_') and ['layer','F.SilkS'] in r)]


def load(name, library=LIB):
    fp = pcbnew.FootprintLoad(str(library),name)
    assert fp is not None, name
    return fp


def silk(fp):
    return [g for g in fp.GraphicalItems() if g.GetLayer()==pcbnew.F_SilkS]


def own_mask_hits(fp):
    graphics = silk(fp)
    pads = [p for p in fp.Pads() if p.IsOnLayer(pcbnew.F_Mask)]
    assert graphics and pads
    hits = []
    for i,g in enumerate(graphics):
        for p in pads:
            # These three exact libraries and this board use zero mask expansion.
            assert p.GetLocalSolderMaskMargin() in (None,0)
            if g.GetEffectiveShape().Collide(p.GetEffectiveShape(pcbnew.F_Cu),100000):
                hits.append((i,p.GetNumber()))
    return hits, len(graphics)*len(pads)


def west_edge_hits(fp, floor=None):
    if floor is None:floor = yaml.safe_load((SRC/'floorplan.yaml').read_text())
    x,y,angle = floor['placement']['anchors']['J9']
    fp.SetPosition(pcbnew.VECTOR2I_MM(x,y))
    fp.SetOrientationDegrees(angle)
    # Independent positive 0.10mm ink-to-edge budget, not the global zero floor.
    west = pcbnew.FromMM(floor['board']['outline']['x0']+.1)
    graphics = silk(fp)
    assert graphics
    return [i for i,g in enumerate(graphics) if g.GetBoundingBox().GetLeft()<west]


def caption_rows(floor):
    return {r['text'] if isinstance(r,dict) else r[0]: r
            for r in floor['silk']['captions']}


def caption_box_hits(floor, board, footprints=None, texts=None):
    """Conservative native glyph boxes vs supplied body/pad boxes, not ink DRC.

    Live tests supply current source-placed native library footprints; the
    historical board supplies only the glyph context. Old negative controls
    use that board's own obstacles. Native DRC and visual review remain owed.
    """
    def box(b):
        return (b.GetLeft()/1e6,b.GetTop()/1e6,b.GetRight()/1e6,b.GetBottom()/1e6)
    def overlap(a,b):
        return a[0]-.15 < b[2] and b[0]-.15 < a[2] and a[1]-.15 < b[3] and b[1]-.15 < a[3]
    obstacles = [(fp.GetReference(),box(fp.GetBoundingBox(False,False)))
                 for fp in (board.GetFootprints() if footprints is None else footprints)]
    assert len(obstacles)==(309 if footprints is None else 333)
    selected = caption_rows(floor)
    texts = CAPTION_TEXTS if texts is None else texts
    assert texts <= selected.keys()
    hits, boxes = [], []
    for text in sorted(texts):
        row = selected[text]
        x,y = row['at'] if isinstance(row,dict) else row[1:3]
        size = max(floor['silk']['min_text_height'],row['size'] if isinstance(row,dict) else row[3])
        angle = row.get('rot',0) if isinstance(row,dict) else 0
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text); t.SetLayer(pcbnew.F_SilkS)
        # Conservative 0.17mm ink envelope covers the selected 0.7mm legends'
        # emitted 0.13mm strokes, without importing the producer's formula.
        t.SetTextSize(pcbnew.VECTOR2I_MM(size,size)); t.SetTextThickness(170000)
        t.SetTextAngleDegrees(angle); t.SetPosition(pcbnew.VECTOR2I_MM(x,y))
        b = box(t.GetBoundingBox())
        frame = floor['board']['outline']
        if not (b[0]>=frame['x0']+.4 and b[1]>=frame['y0']+.4 and
                b[2]<=frame['x1']-.4 and b[3]<=frame['y1']-.4):
            hits.append((text,'board-frame'))
        hits.extend((text,ref) for ref,obstacle in obstacles+boxes if overlap(b,obstacle))
        boxes.append((text,b))
    return hits


class CaptionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scratch = tempfile.TemporaryDirectory(prefix='carrier-caption-oracle-')
        cls.addClassCleanup(cls.scratch.cleanup)
        relative = SRC.parent.relative_to(ROOT)
        board_path = Path(cls.scratch.name)/'pinned.kicad_pcb'
        board_path.write_bytes(subprocess.check_output(['git','show',
            f'{BASE}:{relative}/04_kicad/crow_audio_carrier_v1.kicad_pcb'],cwd=ROOT,timeout=15))
        cls.board = pcbnew.LoadBoard(str(board_path))
        cls.old = yaml.safe_load(subprocess.check_output(['git','show',
            f'{BASE}:{relative}/03_src/floorplan.yaml'],cwd=ROOT,text=True,timeout=15))
        cls.current = yaml.safe_load((SRC/'floorplan.yaml').read_text())

    def test_selected_source_legends_clear_current_component_geometry(self):
        # Never reuse the historical board's placement as a current obstacle.
        from test_digital_launch_source import native_geometry
        geometry = native_geometry(self.current)
        refs = sorted({p['id'].split('.')[0] for p in geometry['pads']})
        self.assertEqual(len(refs),333)
        for ref,fp in zip(refs,geometry['footprints']):
            fp.SetReference(ref)
        self.assertEqual(caption_box_hits(self.current,self.board,geometry['footprints']),[])

    def test_all_channel_legends_clear_current_bodies_and_keep_ownership(self):
        # RED on 4a9c58f5 source: CH1/2/4/5/6/7/8 are under connectors.
        # Native independently loaded source geometry grades all eight sites;
        # no generator slot search or hard-coded accepted coordinates are used.
        from test_digital_launch_source import native_geometry
        geometry = native_geometry(self.current)
        refs = sorted({p['id'].split('.')[0] for p in geometry['pads']})
        self.assertEqual(len(refs),333)
        for ref,fp in zip(refs,geometry['footprints']):
            fp.SetReference(ref)
        self.assertEqual(caption_box_hits(self.current,self.board,
                                         geometry['footprints'],
                                         CHANNEL_TEXTS),[])
        connectors = {fp.GetReference():fp for fp in geometry['footprints']
                      if fp.GetReference() in {f'J{i}' for i in range(1,9)}}
        self.assertEqual(len(connectors),8)
        for text,row in caption_rows(self.current).items():
            if text not in CHANNEL_TEXTS:
                continue
            x,y = row['at'] if isinstance(row,dict) else row[1:3]
            distances = {ref: (fp.GetPosition().x/1e6-x)**2 +
                         (fp.GetPosition().y/1e6-y)**2
                         for ref,fp in connectors.items()}
            own = 'J'+text[2:]
            self.assertLess(distances[own],min(d for ref,d in distances.items()
                                              if ref!=own),text)

    def test_connector_occlusion_control_names_all_seven_bad_channels(self):
        # Restore the exact seven defective source poses while retaining
        # today's full native obstacles: this must remain a failing control.
        from copy import deepcopy
        from test_digital_launch_source import native_geometry
        hostile = deepcopy(self.current)
        old = caption_rows(self.old)
        bad = CHANNEL_TEXTS-{'CH3'}
        hostile['silk']['captions'] = [deepcopy(old[text]) if text in bad else row
                for row in hostile['silk']['captions']
                for text in [row['text'] if isinstance(row,dict) else row[0]]]
        geometry = native_geometry(self.current)
        refs = sorted({p['id'].split('.')[0] for p in geometry['pads']})
        for ref,fp in zip(refs,geometry['footprints']):
            fp.SetReference(ref)
        hits = caption_box_hits(hostile,self.board,geometry['footprints'],bad)
        self.assertEqual({text for text,ref in hits},bad)

    def test_original_crowded_legends_are_rejected(self):
        failures = caption_box_hits(self.old,self.board,texts=LEGACY_CAPTION_TEXTS)
        self.assertEqual({text for text,ref in failures},LEGACY_CAPTION_TEXTS)

    def assert_legend_messages(self, floor):
        current,old = caption_rows(floor),caption_rows(self.old)
        # The adopted RJ45 interface replaces the obsolete four-pin bank
        # legend with an explicit non-Ethernet/non-PoE warning. Keep the old
        # text only in the historical collision fixture, never on this board.
        self.assertEqual(set(current),set(old)-{LEGACY_BANK_TEXT}|{BANK_TEXT})
        self.assertEqual(len(current),len(floor['silk']['captions']))
        for text in current.keys()-CAPTION_TEXTS-CHANNEL_TEXTS-{'MAIN'}:
            self.assertEqual(current[text],old[text])
        self.assertEqual(current['MAIN'],
                         {'text':'MAIN','at':[32.5,73.3],'size':.5,'nudge':False})

    def test_legend_messages_and_other_captions_survive(self):
        self.assert_legend_messages(self.current)

    def test_missing_duplicate_or_retired_bank_warning_is_rejected(self):
        from copy import deepcopy
        for mutation in ('missing','duplicate','retired'):
            with self.subTest(mutation=mutation):
                hostile = deepcopy(self.current)
                rows = hostile['silk']['captions']
                row = next(r for r in rows if isinstance(r,dict)
                           and r['text']==BANK_TEXT)
                if mutation=='missing':
                    rows.remove(row)
                elif mutation=='duplicate':
                    rows.append(deepcopy(row))
                else:
                    row['text'] = LEGACY_BANK_TEXT
                with self.assertRaises(AssertionError):
                    self.assert_legend_messages(hostile)


class SourceSilkTests(unittest.TestCase):
    def test_selected_library_graphics_clear_own_mask(self):
        for name in NAMES:
            with self.subTest(name=name):
                hits,total = own_mask_hits(load(name))
                self.assertGreater(total,0)
                self.assertEqual(hits,[])

    def test_j9_graphics_stay_on_board_without_mating_pose_change(self):
        self.assertEqual(west_edge_hits(load(NAMES[2])),[])

    def test_historical_clipping_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='carrier-old-silk-') as target:
            for name in NAMES:
                (Path(target)/(name+'.kicad_mod')).write_text(old_source(name))
            for name in NAMES[:2]:
                self.assertTrue(own_mask_hits(load(name,Path(target)))[0])
            historical_floor=yaml.safe_load(subprocess.check_output(['git','show',f'{BASE}:projects/crow-audio-carrier-v1/03_src/floorplan.yaml'],cwd=ROOT,text=True,timeout=15))
            self.assertTrue(west_edge_hits(load(NAMES[2],Path(target)),historical_floor))

    def test_non_silk_authority_unchanged(self):
        for name in NAMES:
            self.assertEqual(source_projection((LIB/(name+'.kicad_mod')).read_text()),
                             source_projection(old_source(name)))

    def test_projection_rejects_pad_model_and_fab_drift(self):
        text = old_source(NAMES[0])
        for before,after in [('(size 2.5 2.3)','(size 2.4 2.3)'),
                             ('D_SMB.step','wrong.step'),
                             ('(start -2.45 -1.90)','(start -2.40 -1.90)')]:
            self.assertIn(before,text)
            self.assertNotEqual(source_projection(text),source_projection(text.replace(before,after,1)))

    def test_polarity_and_start_lead_marks_retained(self):
        diode = load(NAMES[0])
        bars = [g for g in silk(diode) if g.GetShape()==pcbnew.SHAPE_T_SEGMENT
                and g.GetWidth()==200000]
        self.assertEqual(len(bars),1)
        self.assertLess(bars[0].GetStart().x,0)
        self.assertLess(bars[0].GetEnd().x,0)
        self.assertGreater(abs(bars[0].GetStart().y-bars[0].GetEnd().y),3000000)
        dots = [g for g in silk(load(NAMES[1])) if g.GetShape()==pcbnew.SHAPE_T_CIRCLE]
        self.assertEqual(len(dots),1)
        self.assertLess(dots[0].GetCenter().x,0)
        self.assertGreater(dots[0].GetRadius(),100000)


if __name__=='__main__':
    unittest.main(verbosity=2)
