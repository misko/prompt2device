#!/usr/bin/env python3
"""Replay one isolated analog-ch8/VMID geometry candidate on the exact four-part board."""
from __future__ import annotations
import hashlib, importlib.util, json, math, sys
from pathlib import Path
import yaml
try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
P = ROOT / 'projects/crow-usb-carrier-v1'
BASE = P / '01_docs/research/2026-09-25-ti-adc7-four-part-margin-sol/candidate.kicad_pcb'
FLOOR = P / '01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/floorplan.yaml'
SOURCE = P / '01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/p1_requirements.yaml'
HELPER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
OUT = HERE / 'candidate.kicad_pcb'
EXPECTED = {'board': '046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0',
            'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
            'source': '60b7062e53bfd930ee7e9e2a8694b87098b1a5625d4a48c06eddb2f8bd8b5be7'}
POSES = {
    'C_ADC_AC8N1': (198.2, 60.25), 'C_A8P': (188.45, 57.0),
    'C_FILTER8N1': (197.15, 56.5), 'C_FILTER8P2': (198.5, 48.0),
    'U_ISO8': (199.0, 53.0), 'R_B8P': (193.75, 61.0),
    'C_FILTER8N2': (184.75, 54.8), 'C_SPOKE_IN8': (191.8, 52.6),
    **{f'R_B{i}P': (25 + 22*i - 1.6, 68.5) for i in range(1, 8)},
}
BODY_GAP = .15
PORTAL = (166.0, 83.9, 167.12, 85.0)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def mmpos(item):
    p = item.GetPosition()
    return (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))
def gap(a, b):
    return math.hypot(max(b[0]-a[2], a[0]-b[2], 0), max(b[1]-a[3], a[1]-b[3], 0))
def pad_key(fp):
    x, y = mmpos(fp)
    return sorted((p.GetNumber(), p.GetNetname(), tuple(fp.GetBoard().GetLayerName(i) for i in p.GetLayerSet().Seq()),
                   p.GetShape(), p.GetAttribute(), tuple(p.GetSize()), tuple(p.GetDrillSize()),
                   round(mmpos(p)[0]-x, 6), round(mmpos(p)[1]-y, 6)) for p in fp.Pads())

def main():
    input_paths = {'board': BASE, 'floorplan': FLOOR, 'source': SOURCE}
    for name, path in input_paths.items():
        if sha(path) != EXPECTED[name]: raise SystemExit(f'{name} SHA drift')
    spec = importlib.util.spec_from_file_location('p1helper', HELPER)
    h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
    b = pcbnew.LoadBoard(str(BASE))
    baseline = {f.GetReference(): f for f in b.GetFootprints()}
    old = {ref: {'pose': mmpos(fp), 'angle': fp.GetOrientationDegrees(), 'pads': pad_key(fp),
                 'envelope': h._physical_envelope(fp)} for ref, fp in baseline.items()}
    fixed = yaml.safe_load(SOURCE.read_text())['p1_fixed_refs']
    if len(fixed) != 27 or any(ref in POSES for ref in fixed): raise SystemExit('fixed-set mismatch')
    regions = yaml.safe_load(FLOOR.read_text())['placement']['regions']
    for ref, (x, y) in POSES.items():
        baseline[ref].SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    fps = {f.GetReference(): f for f in b.GetFootprints()}
    boxes = {ref: h._physical_envelope(fp) for ref, fp in fps.items()}
    if any(mmpos(fps[ref]) != old[ref]['pose'] or fps[ref].GetOrientationDegrees() != old[ref]['angle'] for ref in fixed):
        raise SystemExit('fixed native pose drift')
    if any(pad_key(fp) != old[ref]['pads'] or fp.GetOrientationDegrees() != old[ref]['angle']
           for ref, fp in fps.items()): raise SystemExit('pad identity/geometry or angle drift')
    if any(mmpos(fp) != (POSES[ref] if ref in POSES else old[ref]['pose']) for ref, fp in fps.items()):
        raise SystemExit('unexpected footprint pose change')
    ownership = []
    for ref in sorted(POSES):
        owner = f'analog_ch{ref[3]}' if ref.startswith('R_B') else 'analog_ch8'
        bb = boxes[ref]
        if not h.contains(regions[owner], bb): raise SystemExit(f'{ref}: outside owner')
        foreign = [name for name, region in regions.items() if name != owner and h.intersects(bb, region)]
        if foreign: raise SystemExit(f'{ref}: foreign regions {foreign}')
        if any(not h.contains(bb, h.box_mm(pad.GetBoundingBox())) for pad in fps[ref].Pads()):
            raise SystemExit(f'{ref}: pad protrudes outside physical envelope')
        gaps = sorted((round(gap(bb, other), 6), name) for name, other in boxes.items() if name != ref)
        if gaps[0][0] < BODY_GAP - 1e-6: raise SystemExit(f'{ref}: body gap {gaps[0]}')
        ownership.append({'ref': ref, 'from_mm': old[ref]['pose'], 'to_mm': mmpos(fps[ref]),
                          'move_mm': round(math.dist(old[ref]['pose'], mmpos(fps[ref])), 6),
                          'owner': owner, 'physical_bbox_mm': [round(v, 6) for v in bb],
                          'owner_edge_margins_mm': [round(bb[0]-regions[owner][0], 6),
                                                    round(bb[1]-regions[owner][1], 6),
                                                    round(regions[owner][2]-bb[2], 6),
                                                    round(regions[owner][3]-bb[3], 6)],
                          'nearest_envelopes_mm': gaps[:3]})
    portal_gaps = sorted((round(gap(PORTAL, box), 6), ref) for ref, box in boxes.items())[:5]
    if portal_gaps[0][0] < .15: raise SystemExit(f'portal body obstruction: {portal_gaps}')
    def pd(ref, pin, other, other_pin, prior=False):
        fp = fps[ref]; op = fps[other]
        p = next(p for p in fp.Pads() if p.GetNumber() == pin)
        q = next(p for p in op.Pads() if p.GetNumber() == other_pin)
        a = mmpos(p); z = mmpos(q)
        if prior:
            a = tuple(a[i] + old[ref]['pose'][i] - mmpos(fp)[i] for i in (0, 1))
            z = tuple(z[i] + old[other]['pose'][i] - mmpos(op)[i] for i in (0, 1))
        return round(math.dist(a, z), 6)
    partners = [('C_ADC_AC8N1','1','U_ISO8','6'), ('C_ADC_AC8N1','2','C_ADC_CM8N','1'),
                ('C_A8P','2','R_B8P','1'), ('C_FILTER8N1','1','U_ISO8','9'),
                ('C_FILTER8P2','1','U_ISO8','7'), ('C_FILTER8N2','1','R_X8N','2'),
                ('C_SPOKE_IN8','1','U_SPOKE8','1')]
    for i in range(1,8): partners.append((f'R_B{i}P','1',f'C_A{i}P','2'))
    distances = [{'pads': [f'{r}.{p}',f'{s}.{q}'], 'old_mm': pd(r,p,s,q,True),
                  'new_mm': pd(r,p,s,q)} for r,p,s,q in partners]
    pcbnew.SaveBoard(str(OUT), b)
    result = {'schema': 1, 'kind': 'isolated-coupled-vmid-channel8-placement',
              'status': 'GEOMETRY_SCREEN_ONLY', 'p1_accepted': False, 'p2_accepted': False,
              'route_credit': False, 'return_credit': False,
              'inputs_sha256': {name: sha(path) for name, path in input_paths.items()} |
                               {'helper': sha(HELPER)},
              'candidate_sha256': sha(OUT), 'fixed_ref_count': len(fixed),
              'fixed_poses_identical': True, 'pad_net_layer_shape_and_relative_pose_identical': True,
              'unchanged_nonlisted_poses': True, 'outline_and_stack_unmodified': True,
              'moved': ownership, 'related_pad_distances': distances,
              'adc7_portal_mm': PORTAL, 'portal_nearest_envelopes_mm': portal_gaps,
              'gnd_reference': [{'net': z.GetNetname(), 'filled': z.IsFilled(),
                                 'layers': [b.GetLayerName(i) for i in z.GetLayerSet().Seq()]}
                                for z in b.Zones() if z.GetNetname() == 'GND'],
              'limitations': 'No traces, vias, copper fill, source recut, P1 capacity, or return path is established. '
                             '0.56-mm mouths are envelope separations, not routed width.'}
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__': main()
