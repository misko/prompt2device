#!/usr/bin/env python3
"""Research-only USB4215 edge-registration coupon; no production board authority."""
import pcbnew
from pathlib import Path
MM = pcbnew.FromMM
out = Path(__file__).with_name('usb4215_edge_registration_coupon_4l_target.kicad_pcb')
board = pcbnew.BOARD()
# Process target only: JLC selectable 4-Cu, 1.60 mm nominal coupon.
board.SetCopperLayerCount(4)
board.GetDesignSettings().SetBoardThickness(MM(1.60))
# 30 x 20 mm coupon. Edge y=0 is datum A; x=15 is centerline datum B.
for a, b in [((0,0),(30,0)),((30,0),(30,20)),((30,20),(0,20)),((0,20),(0,0))]:
    edge = pcbnew.PCB_SHAPE(board)
    edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
    edge.SetStart(pcbnew.VECTOR2I(MM(a[0]),MM(a[1])))
    edge.SetEnd(pcbnew.VECTOR2I(MM(b[0]),MM(b[1])))
    edge.SetLayer(pcbnew.Edge_Cuts)
    edge.SetWidth(MM(.1))
    board.Add(edge)
fp = pcbnew.FootprintLoad(
    str(Path(__file__).parents[3] / '03_src/lib/crow_usb_carrier_v1.pretty'),
    'GCT_USB4215_03_A')
if fp is None:
    raise RuntimeError('exact USB4215 footprint unavailable')
fp.SetReference('J_EDGE')
fp.SetValue('USB4215-03-A / coupon only')
# Drawing-derived mouth marker flush with datum-A board edge, orientation 180.
fp.SetPosition(pcbnew.VECTOR2I(MM(15),MM(2.995)))
fp.SetOrientationDegrees(180)
board.Add(fp)
# Exact USB4215 native contact functions for a mechanical coupon.  This is
# deliberately not a Crow electrical design: it only prevents artificial DRC
# shorts on manufacturer-fused physical lands.
net_by_pad = {
    'A1': 'GND', 'B12': 'GND', 'A12': 'GND', 'B1': 'GND', 'SH': 'GND',
    'A4': 'VBUS', 'B9': 'VBUS', 'A9': 'VBUS', 'B4': 'VBUS',
    'A5': 'CC1', 'B5': 'CC2', 'A6': 'USB_DP', 'B6': 'USB_DP',
    'A7': 'USB_DN', 'B7': 'USB_DN', 'A8': 'SBU1_NC', 'B8': 'SBU2_NC',
}
nets = {}
for name in sorted(set(net_by_pad.values())):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    nets[name] = net
for pad in fp.Pads():
    pad.SetNet(nets[net_by_pad[pad.GetNumber()]])
for text, at in [
    ('RESEARCH ONLY — NO CONNECTOR FULL / P-OUT / RELEASE CREDIT', (15, 17.5)),
    ('DATUM A: EDGE y=0.000   DATUM B: CENTER x=15.000', (15, 15.5)),
    ('PROCESS TARGET: JLC 4 Cu / 1.60 mm; TI KiCad target 4 Cu / 1.63 mm — NOT EQUIVALENT', (15, 13.5)),
    ('MEASURE: edge registration, shell seating, cable mating/exposure', (15, 11.5)),
]:
    item = pcbnew.PCB_TEXT(board)
    item.SetText(text)
    item.SetPosition(pcbnew.VECTOR2I(MM(at[0]),MM(at[1])))
    item.SetLayer(pcbnew.F_Fab)
    item.SetTextSize(pcbnew.VECTOR2I(MM(.75),MM(.75)))
    item.SetTextThickness(MM(.15))
    item.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
    board.Add(item)
board.Save(str(out))
