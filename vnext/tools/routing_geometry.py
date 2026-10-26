"""Read-only native assembly/keepout screen; never an acceptance verifier.

Caller owns rectangle applicability and the annulus-gap design allocation.
Tenting, filled-via processes and true three-dimensional fit need review.
"""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import pcbnew as pcb


def screen(source, annulus_gap_mm=0.0, front_rectangle=None):
    import math
    if not math.isfinite(annulus_gap_mm) or annulus_gap_mm < 0:
        raise ValueError('annulus gap must be finite and nonnegative')
    source = Path(source)
    board = pcb.LoadBoard(str(source))
    smd = [(foot.GetReference(), pad) for foot in board.GetFootprints()
           for pad in foot.Pads() if pad.GetAttribute() == pcb.PAD_ATTRIB_SMD]
    tracks = list(board.GetTracks())
    overlaps, gaps, interior = [], [], []
    rect = None
    if front_rectangle:
        x0,y0,x1,y1 = front_rectangle
        if not all(math.isfinite(v) for v in front_rectangle) or x1 <= x0 or y1 <= y0:
            raise ValueError('rectangle must be finite with positive area')
        rect = pcb.SHAPE_RECT(pcb.VECTOR2I(pcb.FromMM(x0),pcb.FromMM(y0)),
                              pcb.FromMM(x1-x0),pcb.FromMM(y1-y0))
    lengths = defaultdict(lambda: {'length_mm':0, 'vias':0, 'layers':set(), 'widths_mm':set()})
    for track in tracks:
        via = isinstance(track,pcb.PCB_VIA)
        net = lengths[track.GetNetname()]
        if via: net['vias'] += 1
        else:
            net['length_mm'] += pcb.ToMM(track.GetLength())
            net['layers'].add(board.GetLayerName(track.GetLayer()))
            net['widths_mm'].add(pcb.ToMM(track.GetWidth()))
        identity = {'uuid':track.m_Uuid.AsString(), 'net':track.GetNetname(),
                    'kind':'via' if via else 'track',
                    'start_mm':[pcb.ToMM(track.GetStart().x),pcb.ToMM(track.GetStart().y)],
                    'end_mm':[pcb.ToMM(track.GetEnd().x),pcb.ToMM(track.GetEnd().y)]}
        if rect is not None and (via or track.GetLayer()==pcb.F_Cu):
            if track.GetEffectiveShape(pcb.F_Cu).Collide(rect,0): interior.append(identity)
        if not via: continue
        for ref,pad in smd:
            for layer in (pcb.F_Cu,pcb.B_Cu):
                if not pad.GetLayerSet().Contains(layer) or not track.IsOnLayer(layer): continue
                entry = dict(identity,ref=ref,pad=pad.GetNumber(),layer=board.GetLayerName(layer))
                shape=pad.GetEffectiveShape(layer)
                if track.GetEffectiveHoleShape().Collide(shape,0): overlaps.append(entry)
                if track.GetEffectiveShape(layer).Collide(shape,pcb.FromMM(annulus_gap_mm)):
                    gaps.append(entry)
    for net in lengths.values():
        net['layers']=sorted(net['layers']); net['widths_mm']=sorted(net['widths_mm'])
        net['length_mm']=round(net['length_mm'],6)
    return {'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'tool_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scope':'native geometry screen; no fabrication, electrical or stage acceptance',
            'annulus_gap_allocation_mm':annulus_gap_mm,'front_rectangle_mm':front_rectangle,
            'via_drill_smd_overlaps':overlaps,'via_annulus_smd_gap_findings':gaps,
            'front_rectangle_collisions':interior,'net_geometry':dict(sorted(lengths.items()))}


def main():
    args=argparse.ArgumentParser(description=__doc__)
    args.add_argument('source'); args.add_argument('output')
    args.add_argument('--annulus-gap',type=float,default=0.0,
                      help='Explicit designer allocation in mm; default tests contact only')
    args.add_argument('--front-rectangle',type=float,nargs=4)
    a=args.parse_args()
    result=screen(a.source,a.annulus_gap,a.front_rectangle)
    with Path(a.output).open('x') as dest: json.dump(result,dest,indent=2); dest.write('\n')
    print(json.dumps({k:len(result[k]) for k in ('via_drill_smd_overlaps',
        'via_annulus_smd_gap_findings','front_rectangle_collisions')}))


if __name__=='__main__': main()
