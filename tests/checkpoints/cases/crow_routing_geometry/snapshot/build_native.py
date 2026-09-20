#!/usr/bin/env python3
"""Rebuild the reduced ADC launch board for local KiCad inspection.

This helper intentionally has no grading verdict: use the checkpoint grader for
the protected connectivity, zero-via, and DRC decisions.
"""
import json
from pathlib import Path
import pcbnew


def mm(value): return pcbnew.FromMM(float(value))


def pad(board, net, ref, number, point):
    fp = pcbnew.FOOTPRINT(board); fp.SetReference(ref); fp.Reference().SetVisible(False)
    item = pcbnew.PAD(fp); item.SetNumber(number); item.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
    item.SetShape(pcbnew.PAD_SHAPE_RECT); item.SetSize(pcbnew.VECTOR2I(mm(1.2), mm(1.2)))
    layers = pcbnew.LSET(); layers.AddLayer(pcbnew.F_Cu); layers.AddLayer(pcbnew.F_Mask)
    item.SetLayerSet(layers); item.SetPosition(pcbnew.VECTOR2I(mm(point[0]), mm(point[1])))
    item.SetNet(net); fp.Add(item); board.Add(fp)


def segment(board, net, start, end, width, layer):
    item = pcbnew.PCB_TRACK(board)
    item.SetStart(pcbnew.VECTOR2I(mm(start[0]), mm(start[1])))
    item.SetEnd(pcbnew.VECTOR2I(mm(end[0]), mm(end[1])))
    item.SetWidth(mm(width)); item.SetLayer(layer); item.SetNet(net); board.Add(item)


doc = json.loads(Path('geometry.json').read_text())
board = pcbnew.BOARD(); signal = pcbnew.NETINFO_ITEM(board, 'ADC_DOUT'); ground = pcbnew.NETINFO_ITEM(board, 'GND')
board.Add(signal); board.Add(ground)
pad(board, signal, 'U_ADC', 'DOUT', doc['pads_mm'][0]); pad(board, signal, 'J_ADC', '1', doc['pads_mm'][1])
pad(board, ground, 'WALL_GND_A', '1', [40, 17]); pad(board, ground, 'WALL_GND_B', '1', [40, 23])
segment(board, ground, [40, 17], [40, 23], .8, pcbnew.F_Cu)
layer = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu}[doc['route']['layer']]
for start, end in zip(doc['route']['points_mm'], doc['route']['points_mm'][1:]):
    segment(board, signal, start, end, doc['route']['width_mm'], layer)
for start, end in zip([[10,10],[70,10],[70,30],[10,30]], [[70,10],[70,30],[10,30],[10,10]]):
    edge = pcbnew.PCB_SHAPE(board); edge.SetShape(pcbnew.SHAPE_T_SEGMENT)
    edge.SetStart(pcbnew.VECTOR2I(mm(start[0]), mm(start[1]))); edge.SetEnd(pcbnew.VECTOR2I(mm(end[0]), mm(end[1])))
    edge.SetLayer(pcbnew.Edge_Cuts); board.Add(edge)
Path('native').mkdir(exist_ok=True)
pcbnew.SaveBoard('native/adc_launch.kicad_pcb', board)
print('wrote native/adc_launch.kicad_pcb; run kicad-cli pcb drc --severity-all native/adc_launch.kicad_pcb')
