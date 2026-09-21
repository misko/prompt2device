#!/usr/bin/env python3
"""Create the fixed native coupon used by independent checkpoint grading."""
import sys
from pathlib import Path

import pcbnew

root = Path(sys.argv[1]).resolve()
board_path = root / "04_kicad/crow_decision_coupon.kicad_pcb"
board_path.parent.mkdir(parents=True, exist_ok=True)
board = pcbnew.CreateEmptyBoard()
nets = {}
for name in ("CLK_P", "CLK_N"):
    net = pcbnew.NETINFO_ITEM(board, name)
    board.Add(net)
    nets[name] = net
for row, (ref, value, pins) in enumerate((
        ("J1", "CONN", (("1", "CLK_P"), ("2", "CLK_N"),
                         ("3", "CLK_P"), ("4", "CLK_N"))),
        ("U1", "TERM", (("1", "CLK_P"), ("2", "CLK_N"))))):
    footprint = pcbnew.FOOTPRINT(board)
    footprint.SetReference(ref)
    footprint.SetValue(value)
    footprint.SetLayer(pcbnew.F_Cu)
    board.Add(footprint)
    for index, (number, net_name) in enumerate(pins):
        pad = pcbnew.PAD(footprint)
        pad.SetNumber(number)
        pad.SetShape(pcbnew.PAD_SHAPE_RECT)
        pad.SetSize(pcbnew.VECTOR2I_MM(1, 1))
        pad.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        pad.SetLayerSet(pcbnew.PAD.SMDMask())
        pad.SetNet(nets[net_name])
        footprint.Add(pad)
        pad.SetPosition(pcbnew.VECTOR2I_MM(10 + index * 1.5, 10 + row * 5))
pcbnew.SaveBoard(str(board_path), board)
