#!/usr/bin/env python3
"""Replay one coupled native P2 placement experiment; no route or P1 credit."""
from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / '2026-09-25-ti-timing-mouth-screen-sol'))
import build_screen as screen  # noqa: E402

pcbnew = screen.pcbnew

BASE = screen.BOARD
SOURCE = screen.SOURCE
FLOORPLAN = screen.FLOORPLAN
BOARD_OUT = HERE / 'candidate.kicad_pcb'
RESULT_OUT = HERE / 'result.json'

# Shift the XU and all of its nearby bypasses as a rigid group by 0.2 mm north.
# The four exceptions below are then positioned relative to that translated group.
GROUP_PREFIXES = ('C_XU_VDD', 'C_XU_USB')
EXCEPTIONS = {
    'C_ADC_I2C_B': (172.8, 98.6, 0),
    'C_XU_VDD_105': (196.5, 96.3, 180),
    'C_XU_VDD_106': (198.6, 99.1, 180),
    'C_XU_VDD_14': (207.8, 109.5, -90),
    'C_XU_VDDIO_17': (209.0, 109.5, -90),
}
MOUTHS = {
    'translator_west_four': ([172.5, 94.2, 174.305, 96.8], 'horizontal', 4),
    'xu_west_data': ([197.5, 97.1, 199.805, 98.5], 'horizontal', 1),
    'xu_south_three': ([209.5, 108.5, 212.5, 109.7], 'vertical', 3),
}


def at(fp):
    p = fp.GetPosition()
    return (round(pcbnew.ToMM(p.x), 4), round(pcbnew.ToMM(p.y), 4),
            round(fp.GetOrientationDegrees(), 4))


def envelope(fp):
    c = fp.GetCourtyard(pcbnew.F_CrtYd)
    return screen.bbox(c.BBox() if c.OutlineCount() else fp.GetBoundingBox(False, False))


def owner_distance(fps, cap, pin):
    a = next(p for p in fps[cap].Pads() if p.GetNumber() == '1').GetPosition()
    b = next(p for p in fps['U_XU'].Pads() if p.GetNumber() == pin).GetPosition()
    return math.hypot(pcbnew.ToMM(a.x - b.x), pcbnew.ToMM(a.y - b.y))


def main():
    hashes = {'board': screen.digest(BASE), 'source': screen.digest(SOURCE),
              'floorplan': screen.digest(FLOORPLAN)}
    if hashes != screen.EXPECTED:
        raise SystemExit(f'bound input drift: {hashes}')
    source = yaml.safe_load(SOURCE.read_text())
    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    fixed = set(source['p1_fixed_refs'])
    if len(fixed) != 27:
        raise SystemExit('fixed denominator drift')
    board = pcbnew.LoadBoard(str(BASE))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    baseline_at = {ref: at(fp) for ref, fp in fps.items()}
    baseline_boxes = {ref: envelope(fp) for ref, fp in fps.items()}
    owner_pins = {ref: ref.rsplit('_', 1)[-1] for ref in fps
                  if ref.startswith(('C_XU_VDD_', 'C_XU_VDDIO_'))}
    baseline_distances = {ref: owner_distance(fps, ref, pin)
                          for ref, pin in owner_pins.items()}
    moves = {}
    for ref, fp in fps.items():
        x, y, angle = baseline_at[ref]
        if ref == 'U_XU' or (ref.startswith(GROUP_PREFIXES) and x >= 190):
            moves[ref] = (x, round(y - 0.2, 4), angle)
    moves.update(EXCEPTIONS)
    if fixed & moves.keys():
        raise SystemExit(f'fixed ref selected for movement: {sorted(fixed & moves.keys())}')
    for ref, (x, y, angle) in moves.items():
        fps[ref].SetOrientationDegrees(angle)
        fps[ref].SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    # Reference legends need a separate silk layout after coupled movement. Keep
    # the identities on F.Fab for this physical probe, including the adjacent
    # translator whose old legend otherwise crosses the moved C_ADC_I2C_B.
    for ref in moves.keys() | {'U_ADC_I2C_XLATE'}:
        fps[ref].Reference().SetLayer(pcbnew.F_Fab)
    if any(at(fps[ref]) != baseline_at[ref] for ref in fixed):
        raise SystemExit('fixed footprint moved')
    endpoints = {}
    for net, identities in screen.TERMINALS.items():
        endpoints[net] = []
        for identity in identities:
            ref, number = identity.rsplit('.', 1)
            pads = [p for p in fps[ref].Pads() if p.GetNumber() == number]
            if len(pads) != 1 or pads[0].GetNetname() != net or not pads[0].IsOnLayer(pcbnew.F_Cu):
                raise SystemExit(f'{identity} identity/net/layer drift')
            p = pads[0].GetPosition()
            endpoints[net].append({'pad': identity,
                                   'centre_mm': [round(pcbnew.ToMM(p.x), 4), round(pcbnew.ToMM(p.y), 4)],
                                   'bbox_mm': [round(v, 4) for v in screen.bbox(pads[0].GetBoundingBox())]})

    boxes = {ref: envelope(fp) for ref, fp in fps.items()}
    baseline_collisions = {(a, b) for a in moves for b in fps if a != b
                           and screen.intersects(baseline_boxes[a], baseline_boxes[b])}
    candidate_collisions = {(a, b) for a in moves for b in fps if a != b
                            and screen.intersects(boxes[a], boxes[b])}
    new_collisions = sorted(candidate_collisions - baseline_collisions)
    if new_collisions:
        raise SystemExit(f'new native envelope collisions: {new_collisions}')

    # Source ownership is a placement group; compare new envelope violations to
    # baseline because some pre-existing east-core placements already cross a face.
    owners = {}
    for pattern in floorplan['placement']['patterns']:
        if 'region' in pattern:
            for ref in pattern['match']:
                owners[ref] = pattern['region']
    regions = floorplan['placement']['regions']
    def outside(ref, box):
        region = regions[owners[ref]]
        return box[0] < region[0] - 1e-6 or box[1] < region[1] - 1e-6 or box[2] > region[2] + 1e-6 or box[3] > region[3] + 1e-6
    new_region_violations = sorted(ref for ref in moves if ref in owners
                                   and outside(ref, boxes[ref]) and not outside(ref, baseline_boxes[ref]))
    if new_region_violations:
        raise SystemExit(f'new source-region envelope violations: {new_region_violations}')

    distances = {ref: owner_distance(fps, ref, pin) for ref, pin in owner_pins.items()}
    worsened = {ref: [round(baseline_distances[ref], 4), round(value, 4)]
                for ref, value in distances.items() if value > baseline_distances[ref] + 1e-6}
    if worsened:
        raise SystemExit(f'XU local bypass distance worsened: {worsened}')
    obstacles = [(ref, box) for ref, box in boxes.items()]
    mouths = {}
    for name, (area, axis, demand) in MOUTHS.items():
        row = screen.mouth_screen(area, axis, obstacles)
        mouths[name] = {'bbox_mm': area, 'axis': axis, 'demand_slots': demand,
                        'screen_pitch_mm': screen.PITCH, **row}
        if row['raw_slots'] < demand:
            raise SystemExit(f'{name} misses rough slot demand: {row}')

    # Full native F.Cu pad bboxes cannot acquire a new overlap between refs.
    def pad_pairs(current_fps, moved):
        all_pads = [(ref, p.GetNumber(), screen.bbox(p.GetBoundingBox()))
                    for ref, fp in current_fps.items() for p in fp.Pads() if p.IsOnLayer(pcbnew.F_Cu)]
        return {(r, n, t, m) for r, n, a in all_pads if r in moved
                for t, m, b in all_pads if r != t and screen.intersects(a, b)}
    candidate_pad_pairs = pad_pairs(fps, moves)
    baseline_board = pcbnew.LoadBoard(str(BASE))
    baseline_fps = {fp.GetReference(): fp for fp in baseline_board.GetFootprints()}
    added_pad_pairs = sorted(candidate_pad_pairs - pad_pairs(baseline_fps, moves))
    if added_pad_pairs:
        raise SystemExit(f'new native F.Cu pad bbox overlaps: {added_pad_pairs[:20]}')

    pcbnew.SaveBoard(str(BOARD_OUT), board)
    zone_rows = [{'net': z.GetNetname(), 'layers': [board.GetLayerName(i) for i in z.GetLayerSet().Seq()],
                  'saved_filled': bool(z.IsFilled())} for z in board.Zones() if not z.GetIsRuleArea()]
    result = {'schema': 1, 'kind': 'bounded-coupled-p2-placement-probe',
              'input_sha256': hashes, 'candidate_board_sha256': hashlib.sha256(BOARD_OUT.read_bytes()).hexdigest(),
              'timing_endpoints': endpoints,
              'moves': {ref: {'from': baseline_at[ref], 'to': at(fps[ref]), 'owner_region': owners.get(ref)}
                        for ref in sorted(moves)}, 'fixed_ref_count': len(fixed),
              'new_envelope_collisions': new_collisions, 'new_fcu_pad_bbox_overlaps': added_pad_pairs,
              'new_source_region_violations': new_region_violations,
              'owner_pin_distance_mm': {ref: {'before': round(baseline_distances[ref], 4),
                                              'after': round(distances[ref], 4)}
                                        for ref in sorted(owner_pins) if ref in moves},
              'mouths': mouths, 'zones': zone_rows,
              'status': 'GEOMETRY_PROBE_ONLY', 'routing_realized': False, 'p1_accepted': False,
              'limitations': ['courtyard aperture is not exact pad access',
                              '0.45 mm is rough source pitch, not effective net-class proof',
                              'saved In1.Cu GND zone remains unfilled; no continuous return proof']}
    RESULT_OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'board_sha256': result['candidate_board_sha256'],
                      'moved': len(moves), 'mouth_slots': {n: [v['raw_slots'], v['demand_slots']]
                                                        for n, v in mouths.items()}}, sort_keys=True))


if __name__ == '__main__':
    main()
