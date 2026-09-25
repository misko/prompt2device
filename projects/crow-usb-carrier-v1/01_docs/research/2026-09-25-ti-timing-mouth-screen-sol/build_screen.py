#!/usr/bin/env python3
"""Reproduce bounded, conservative TDM mouth screens; no route credit."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
PACKET = RESEARCH / '2026-09-25-ti-unified-p1-diagnostic-sol'
BOARD = RESEARCH / '2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
SOURCE = PACKET / 'p1_requirements.yaml'
FLOORPLAN = PACKET / 'floorplan.yaml'
EXPECTED = {
    'board': 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
    'source': 'f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222',
    'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
}
TERMINALS = {
    'AUDIO_MCLK_1V8': ('U_TDM_XLATE.6', 'U_XU.23'),
    'TDM_BCLK_1V8': ('U_TDM_XLATE.4', 'U_XU.22'),
    'TDM_DATA_1V8': ('U_TDM_XLATE.7', 'U_XU.107'),
    'TDM_FSYNC_1V8': ('U_TDM_XLATE.5', 'U_XU.20'),
}
MOUTHS = {
    'translator_west_four': {'bbox': [172.5, 94.2, 174.305, 96.8], 'axis': 'horizontal', 'demand': 4},
    'xu_west_data': {'bbox': [197.5, 97.695, 199.805, 98.705], 'axis': 'horizontal', 'demand': 1},
    'xu_south_three': {'bbox': [209.5, 108.7, 212.5, 109.9], 'axis': 'vertical', 'demand': 3},
}
PITCH = 0.45  # Source TDM rough slot pitch; effective rules remain unmeasured.


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bbox(native_box):
    return tuple(pcbnew.ToMM(v) for v in (
        native_box.GetLeft(), native_box.GetTop(),
        native_box.GetRight(), native_box.GetBottom()))


def intersects(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def free(lo, hi, blocked):
    merged = []
    for a, b in sorted((max(lo, a), min(hi, b)) for a, b in blocked):
        if b <= a:
            continue
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    result, cursor = [], lo
    for a, b in merged:
        if a > cursor:
            result.append((cursor, a))
        cursor = max(cursor, b)
    if cursor < hi:
        result.append((cursor, hi))
    return result


def mouth_screen(area, axis, obstacles):
    along, across = ((0, 2), (1, 3)) if axis == 'horizontal' else ((1, 3), (0, 2))
    start, end = area[along[0]], area[along[1]]
    lo, hi = area[across[0]], area[across[1]]
    hits = [(name, box) for name, box in obstacles if intersects(area, box)]
    cuts = sorted({start, end, *(max(start, box[along[0]]) for _, box in hits),
                   *(min(end, box[along[1]]) for _, box in hits)})
    prior, sections = [], []
    for a, b in zip(cuts, cuts[1:]):
        mid = (a + b) / 2
        spans = free(lo, hi, [(box[across[0]], box[across[1]]) for _, box in hits
                              if box[along[0]] < mid < box[along[1]]])
        current = []
        for span in spans:
            width = span[1] - span[0]
            reach = width if not sections else max(
                (min(value, width, min(old[1], span[1]) - max(old[0], span[0]))
                 for old, value in prior if min(old[1], span[1]) > max(old[0], span[0])),
                default=0.0)
            current.append((span, reach))
        sections.append({'station_mm': round(mid, 4),
                         'max_free_width_mm': round(max((v-u for u, v in spans), default=0), 4),
                         'reachable_width_mm': round(max((v for _, v in current), default=0), 4)})
        prior = current
    width = max((value for _, value in prior), default=0.0)
    return {'connected_width_mm': round(width, 4), 'raw_slots': math.floor((width + 1e-9) / PITCH),
            'intersecting_native_envelopes': sorted({name for name, _ in hits}),
            'cross_sections': sections}


def main():
    paths = {'board': BOARD, 'source': SOURCE, 'floorplan': FLOORPLAN}
    hashes = {key: digest(path) for key, path in paths.items()}
    if hashes != EXPECTED:
        raise SystemExit(f'bound input drift: {hashes}')
    source = yaml.safe_load(SOURCE.read_text())
    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    fixed = set(source['p1_fixed_refs'])
    if len(fixed) != 27:
        raise SystemExit('27-ref fixed denominator drift')
    board = pcbnew.LoadBoard(str(BOARD))
    footprints = {fp.GetReference(): fp for fp in board.GetFootprints()}
    obstacles = []
    for ref, fp in footprints.items():
        courtyard = fp.GetCourtyard(pcbnew.F_CrtYd)
        geometry = courtyard.BBox() if courtyard.OutlineCount() else fp.GetBoundingBox(False, False)
        obstacles.append((ref + ':courtyard_or_body', bbox(geometry)))
        for pad in fp.Pads():
            if pad.IsOnLayer(pcbnew.F_Cu):
                obstacles.append((ref + ':pad' + pad.GetNumber(), bbox(pad.GetBoundingBox())))
    endpoints = {}
    for net, members in TERMINALS.items():
        rows = []
        for identity in members:
            ref, number = identity.rsplit('.', 1)
            pads = [pad for pad in footprints[ref].Pads() if pad.GetNumber() == number]
            if len(pads) != 1 or pads[0].GetNetname() != net or not pads[0].IsOnLayer(pcbnew.F_Cu):
                raise SystemExit(f'{identity}: exact native pad/net/layer drift')
            at = pads[0].GetPosition()
            rows.append({'pad': identity, 'centre_mm': [round(pcbnew.ToMM(at.x), 4),
                                                         round(pcbnew.ToMM(at.y), 4)],
                         'bbox_mm': [round(v, 4) for v in bbox(pads[0].GetBoundingBox())]})
        endpoints[net] = rows
    regions = floorplan['placement']['regions']
    checks = {}
    rule_areas = [(z.GetZoneName(), bbox(z.GetBoundingBox())) for z in board.Zones()
                  if z.GetIsRuleArea() and z.IsOnLayer(pcbnew.F_Cu)]
    for name, spec in MOUTHS.items():
        area = spec['bbox']
        result = mouth_screen(area, spec['axis'], obstacles)
        checks[name] = {'bbox_mm': area, 'axis': spec['axis'], 'demand_slots': spec['demand'],
                        'screen_pitch_mm': PITCH, **result,
                        'fixed_ref_hits': sorted({ref for ref in fixed if any(
                            name.startswith(ref + ':') for name in result['intersecting_native_envelopes'])}),
                        'native_fcu_rule_area_hits': sorted(zname for zname, zbox in rule_areas
                                                           if intersects(area, zbox)),
                        'source_regions_intersected': sorted(name for name, region in regions.items()
                                                             if intersects(area, region))}
    zones = [{'net': z.GetNetname(), 'layers': [board.GetLayerName(i) for i in z.GetLayerSet().Seq()],
              'rule_area': bool(z.GetIsRuleArea()), 'bbox_mm': [round(v, 4) for v in bbox(z.GetBoundingBox())],
              'saved_filled': bool(z.IsFilled())} for z in board.Zones()]
    output = {'schema': 1, 'kind': 'tdm-full-envelope-mouth-screen', 'status': 'STOP_COUPLED_PLACEMENT',
              'hashes': hashes, 'fixed_ref_count': len(fixed), 'fixed_refs': sorted(fixed),
              'endpoints': endpoints, 'mouths': checks, 'zones': zones,
              'owner_regions': {key: regions[key] for key in ('audio_clock_tdm', 'xmos_core')},
              'method': 'F.Cu native courtyard/body and pad bbox event-strip aperture diagnostic; no trace, bend, same-net access, SI, or return proof',
              'p1_accepted': False, 'routing_realized': False}
    (HERE / 'result.json').write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
    print(json.dumps({name: [row['connected_width_mm'], row['raw_slots'], row['demand_slots']]
                      for name, row in checks.items()}, sort_keys=True))


if __name__ == '__main__':
    main()
