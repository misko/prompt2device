"""Read-only native inventory, run using the KiCad Python interpreter."""
import json
import sys
import pcbnew as p


def xy(v):
    return [p.ToMM(v.x), p.ToMM(v.y)]


def snapshot(path):
    board = p.LoadBoard(path)
    out = []
    for f in board.GetFootprints():
        boxes = [g.GetBoundingBox() for g in f.GraphicalItems() if g.GetLayer() == p.F_Fab
                 and not isinstance(g, p.PCB_TEXT)]
        if not boxes:
            boxes = [a.GetBoundingBox() for a in f.Pads()]
        if not boxes:
            continue
        bounds = [min(p.ToMM(b.GetLeft()) for b in boxes), min(p.ToMM(b.GetTop()) for b in boxes),
                  max(p.ToMM(b.GetRight()) for b in boxes), max(p.ToMM(b.GetBottom()) for b in boxes)]
        try: mpn=f.GetFieldText('MPN')
        except KeyError: mpn=None
        out.append(dict(ref=f.GetReference(), value=f.GetValue(), mpn=mpn, footprint=f.GetFPIDAsString(),
                        position=xy(f.GetPosition()), angle=f.GetOrientationDegrees(),
                        bottom=f.IsFlipped(), dnp=f.IsDNP(), bounds=bounds,
                        pads=[dict(number=a.GetNumber(), position=xy(a.GetPosition()),
                                   drill=xy(a.GetDrillSize())) for a in f.Pads()]))
    return dict(thickness_mm=p.ToMM(board.GetDesignSettings().GetBoardThickness()), footprints=out)


if __name__ == '__main__':
    print(json.dumps(snapshot(sys.argv[1])))
