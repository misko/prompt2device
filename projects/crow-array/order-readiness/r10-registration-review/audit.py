"""Read-only native/CPL witness extraction and stack arithmetic; no vendor acceptance."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import pcbnew as pcb

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / 'quote-draft/r10-2c8p-outward-power'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sources = {}
def bind(path):
    sources[os.path.relpath(path,ROOT)] = sha(path)
    return path
def xy(value):
    return [round(pcb.ToMM(value.x), 6), round(pcb.ToMM(value.y), 6)]
def world(foot, local):
    x, y = xy(foot.GetPosition())
    a = math.radians(foot.GetOrientationDegrees())
    return [round(x + local[0]*math.cos(a) + local[1]*math.sin(a), 6),
            round(y - local[0]*math.sin(a) + local[1]*math.cos(a), 6)]

rows = []
for label in ('carrier', 'pod'):
    path = bind(PACKAGE / f'native/pcb/{label}/{label}.kicad_pcb')
    board = pcb.LoadBoard(str(path))
    with bind(PACKAGE / f'{label}-cpl.csv').open() as stream:
        cpl = {row['Designator']: row for row in csv.DictReader(stream)}
    for foot in board.GetFootprints():
        ref = foot.GetReference()
        if ref not in (['J1'] + [f'J{i}' for i in range(101,109)] if label == 'carrier' else ['J1']):
            continue
        jack = label == 'carrier' and ref == 'J1'
        assert foot.GetFieldText('MPN') == ('PJ-102AH' if jack else 'RJHSE-5080')
        assert not foot.IsFlipped()
        center = world(foot, [0,6.5] if jack else [3.556,-.127])
        expected = {'1':[0,0], '2':[0,6], '3':[4.7,3]} if jack else {
            str(i):[(i-1)*1.016, 1.778 if i%2==0 else 0] for i in range(1,9)}
        pads = {p.GetNumber():xy(p.GetPosition()) for p in foot.Pads() if p.GetNumber()}
        assert set(pads) == set(expected)
        for number, local in expected.items():
            assert math.dist(pads[number],world(foot,local)) <= .006
        pegs = sorted(xy(p.GetPosition()) for p in foot.Pads() if not p.GetNumber())
        expected_pegs = [] if jack else sorted(world(foot,p) for p in [[-2.794,-2.54],[9.906,-2.54]])
        assert len(pegs) == len(expected_pegs)
        assert all(math.dist(a,b) <= .006 for a,b in zip(pegs,expected_pegs))
        actual = cpl[ref]
        assert abs(float(actual['Mid X'].removesuffix('mm'))-center[0]) < 1e-6
        assert abs(float(actual['Mid Y'].removesuffix('mm'))+center[1]) < 1e-6
        assert float(actual['Rotation']) == foot.GetOrientationDegrees()
        assert actual['Layer'] == 'Top'
        rows.append(dict(board=label, reference=ref, mpn=foot.GetFieldText('MPN'),
            native_pads=pads, native_locator_holes=pegs, body_center_native=center,
            cpl=actual, actual_physical_180_counterfactual_pads={
                k:[round(2*center[i]-v[i],6) for i in range(2)] for k,v in pads.items()},
            actual_physical_180_counterfactual_pegs=[
                [round(2*center[i]-v[i],6) for i in range(2)] for v in pegs]))

carrier = PACKAGE / 'native/pcb/carrier/carrier.kicad_pcb'
stack = carrier.read_text().split('(stackup',1)[1].split('(copper_finish',1)[0]
plies = [float(n) for n in re.findall(r'\(thickness ([0-9.]+)\)',stack)]
assert plies == [.035,.218,.0764,.0152,.865,.0152,.0764,.218,.035]
assert abs(sum(plies)-1.5542)<1e-9
model = json.loads(bind(PACKAGE/'engineering/clock-model.json').read_text())
for name in ('JLC-R10-MACBOOK-SESSION-20261101.md','BACKEND-R10-JLC-BLOCKERS-HANDOFF-20261101.md',
             'R10-INSTRUCTIONS.md','R9-RJ45-ORIENTATION-REVIEW-20261101.md',
             'power-jack-r10-review/REVIEW.md','power-jack-r10-review/review.json'):
    bind(ROOT/name)
sources['r10-registration-review/audit.py'] = sha(Path(__file__))
historical = ROOT.parent/'releases/crow-prototype-v3-first-run-5c10p-public-v1/historical/documentation/carrier'
for name in ('process/04-2026-10-08-ls20-engineering.md', 'process/33-process.md',
             'instructions/40-module-controls.md', 'instructions/42-controls.md'):
    bind(historical/name)
result = dict(status='DIAGNOSTIC_ONLY_NO_VENDOR_REGISTRATION_OR_STACK_ACCEPTANCE',
    source_commit='278309e057c10f46d7c3d638931a495737699169', sources=sources,
    stack=dict(native_plies_mm=plies, nominal_sum_mm=round(sum(plies),6),
        portal_nominal_mm=1.5542, portal_tolerance_fraction=.10,
        portal_range_mm=[round(1.5542*.9,6),round(1.5542*1.1,6)],
        difference_from_CAD_1_6_mm=[round(1.5542*.9-1.6,6),round(1.5542*1.1-1.6,6)],
        clock_screen_outer_gap_cases_mm=sorted({c['parameters']['h'] for c in model['fast_cases']}),
        total_tolerance_is_not_per_ply_tolerance=True),
    connector_witnesses=sorted(rows,key=lambda row:(row['board'],row['reference'])),
    vendor_witnesses_available=False)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=Path)
args = parser.parse_args()
if args.output:
    with args.output.open('x') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(result=result['status'],connectors=len(rows),stack=result['stack'],output=str(args.output)),indent=2))
else:
    print(json.dumps(result,indent=2))
