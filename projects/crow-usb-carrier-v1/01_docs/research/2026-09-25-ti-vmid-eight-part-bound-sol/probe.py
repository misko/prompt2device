#!/usr/bin/env python3
"""Bounded 0.1-mm native-envelope placement search; no accepted placement."""
from __future__ import annotations

import hashlib
import importlib.util
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
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
FOUR = PROJECT / '01_docs/research/2026-09-25-ti-adc7-four-part-margin-sol/candidate.kicad_pcb'
TI = PROJECT / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb'
SOURCE = PROJECT / '01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/p1_requirements.yaml'
FLOOR = PROJECT / '01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/floorplan.yaml'
INTERFACES = PROJECT / '01_docs/research/2026-09-25-ti-adc-analog-88-accounting-sol/modular_plan.json'
HELPER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED = {
    'four_board': '046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0',
    'ti_board': '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10',
    'floorplan': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'source': '60b7062e53bfd930ee7e9e2a8694b87098b1a5625d4a48c06eddb2f8bd8b5be7',
    'interfaces': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'helper': '0827824c749206fc11194f27daa6e732a3253b348054a6d93218e960fe138a93',
}
STEP_MM = 0.1
BODY_GAP_MM = 0.15
ROUTE_MOUTH_MM = 0.56
LOCAL_DISTANCE_RATIO = 1.5  # Exploratory filter, not a source design rule.


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def gap(a, b):
    return math.hypot(max(b[0]-a[2], a[0]-b[2], 0),
                      max(b[1]-a[3], a[1]-b[3], 0))


def translated(box, dx, dy):
    return (box[0]+dx, box[1]+dy, box[2]+dx, box[3]+dy)


def mmpos(item):
    p = item.GetPosition()
    return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)


def pads_by_net(board):
    result = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            result.setdefault(pad.GetNetname(), []).append((fp.GetReference(), pad.GetNumber(), pad))
    return result


def main():
    paths = {'four_board': FOUR, 'ti_board': TI, 'source': SOURCE, 'floorplan': FLOOR,
             'interfaces': INTERFACES, 'helper': HELPER}
    for name, path in paths.items():
        if sha(path) != EXPECTED[name]:
            raise SystemExit(f'{name} SHA drift')
    spec = importlib.util.spec_from_file_location('p1_capacity', HELPER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    board = pcbnew.LoadBoard(str(FOUR))
    ti = pcbnew.LoadBoard(str(TI))
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    baseline_fps = {fp.GetReference(): fp for fp in ti.GetFootprints()}
    fixed = yaml.safe_load(SOURCE.read_text())['p1_fixed_refs']
    if len(fixed) != 27 or any(mmpos(fps[ref]) != mmpos(baseline_fps[ref]) or
                               fps[ref].GetOrientationDegrees() != baseline_fps[ref].GetOrientationDegrees()
                               for ref in fixed):
        raise SystemExit('27 fixed native poses drift')
    def pad_inventory(native):
        return sorted((fp.GetReference(), pad.GetNumber(), pad.GetNetname(),
                       tuple(native.GetLayerName(i) for i in pad.GetLayerSet().Seq()))
                      for fp in native.GetFootprints() for pad in fp.Pads())
    if pad_inventory(board) != pad_inventory(ti):
        raise SystemExit('native pad/net/layer identity drift')
    regions = yaml.safe_load(FLOOR.read_text())['placement']['regions']
    boxes = {ref: helper._physical_envelope(fp) for ref, fp in fps.items()}
    for ref in [f'R_B{i}P' for i in range(1, 9)] + ['C_ADC_AC8N1']:
        if any(not helper.contains(boxes[ref], helper.box_mm(pad.GetBoundingBox()))
               for pad in fps[ref].Pads()):
            raise SystemExit(f'{ref}: pad protrudes outside screened physical envelope')
    net_pads = pads_by_net(board)
    resistors = []
    for number in range(1, 9):
        ref = f'R_B{number}P'
        fp = fps[ref]
        ox, oy = mmpos(fp)
        body = boxes[ref]
        region = regions[f'analog_ch{number}']
        target = next(pad for other, pin, pad in net_pads[f'BIAS_P{number}']
                      if other == f'C_A{number}P' and pin == '2')
        target_xy = mmpos(target)
        bias_pad = next(pad for pad in fp.Pads() if pad.GetNumber() == '1')
        bx, by = mmpos(bias_pad)
        baseline_distance = math.hypot(bx-target_xy[0], by-target_xy[1])
        # Only a bounded local 6-mm west, +/-8-mm vertical neighborhood.
        static = [box for name, box in boxes.items() if name != ref and
                  gap(box, [region[0]-6, 54, region[2]+6, 72]) < 1]
        legal = []
        routable_mouth = []
        for ix in range(round((ox-6)*10), round(ox*10)+1):
            x = ix / 10
            for iy in range(round((oy-8)*10), round((oy+8)*10)+1):
                y = iy / 10
                bb = translated(body, x-ox, y-oy)
                if not helper.contains(region, bb):
                    continue
                nearest = min(gap(bb, other) for other in static)
                if nearest < BODY_GAP_MM-1e-6:
                    continue
                distance = math.hypot((bx+x-ox)-target_xy[0],
                                      (by+y-oy)-target_xy[1])
                row = {'origin_mm': [x, y], 'move_mm': round(math.hypot(x-ox, y-oy), 6),
                       'physical_bbox_mm': [round(v, 6) for v in bb],
                       'min_other_envelope_gap_mm': round(nearest, 6),
                       'bias_partner_center_mm': round(distance, 6),
                       'bias_partner_ratio': round(distance/baseline_distance, 6),
                       'east_owner_margin_mm': round(region[2]-bb[2], 6)}
                legal.append(row)
                if (row['east_owner_margin_mm'] >= ROUTE_MOUTH_MM-1e-6 and
                        nearest >= ROUTE_MOUTH_MM-1e-6):
                    routable_mouth.append(row)
        legal.sort(key=lambda row: (row['move_mm'], row['bias_partner_center_mm']))
        routable_mouth.sort(key=lambda row: (row['move_mm'], row['bias_partner_center_mm']))
        resistors.append({'ref': ref, 'original_origin_mm': [ox, oy],
                          'original_physical_bbox_mm': body,
                          'owner_region_mm': region,
                          'west_shift_lower_bound_mm': round(body[2]-region[2], 6),
                          'original_bias_partner_center_mm': round(baseline_distance, 6),
                          'legal_local_count': len(legal),
                          'nearest_legal_local': legal[0] if legal else None,
                          'route_mouth_screen_count': len(routable_mouth),
                          'nearest_route_mouth_screen': routable_mouth[0] if routable_mouth else None})
    # Complete owner-cell search for the ADC8 AC input cap. Whole physical
    # envelope must also avoid the overlapping usb_vbus_sense source region.
    ref = 'C_ADC_AC8N1'
    fp = fps[ref]
    ox, oy = mmpos(fp)
    body = boxes[ref]
    owner = regions['analog_ch8']
    foreign = regions['usb_vbus_sense']
    static = [box for name, box in boxes.items() if name != ref and
              gap(box, [owner[0]-5, owner[1]-5, owner[2]+5, owner[3]+5]) < 1]
    cap_pads = {pad.GetNumber(): pad for pad in fp.Pads()}
    related = {}
    for pin, partner in [('1', 'U_ISO8.6'), ('2', 'C_ADC_CM8N.1')]:
        other_ref, other_pin = partner.rsplit('.', 1)
        other = next(pad for pad in fps[other_ref].Pads() if pad.GetNumber() == other_pin)
        px, py = mmpos(cap_pads[pin])
        qx, qy = mmpos(other)
        related[pin] = {'partner': partner, 'pad_offset_mm': [px-ox, py-oy],
                        'partner_center_mm': [qx, qy],
                        'baseline_distance_mm': math.hypot(px-qx, py-qy)}
    candidates = 0
    legal = []
    for ix in range(round((owner[0]+(ox-body[0]))*10),
                    round((owner[2]-(body[2]-ox))*10)+1):
        x = ix / 10
        for iy in range(round((owner[1]+(oy-body[1]))*10),
                        round((owner[3]-(body[3]-oy))*10)+1):
            y = iy / 10
            bb = translated(body, x-ox, y-oy)
            if not helper.contains(owner, bb) or helper.intersects(bb, foreign):
                continue
            candidates += 1
            nearest = min(gap(bb, other) for other in static)
            if nearest < BODY_GAP_MM-1e-6:
                continue
            distances = {}
            ratios = []
            for pin, data in related.items():
                px = x + data['pad_offset_mm'][0]
                py = y + data['pad_offset_mm'][1]
                qx, qy = data['partner_center_mm']
                distance = math.hypot(px-qx, py-qy)
                distances[pin] = round(distance, 6)
                ratios.append(distance/data['baseline_distance_mm'])
            legal.append({'origin_mm': [x, y],
                          'move_mm': round(math.hypot(x-ox, y-oy), 6),
                          'physical_bbox_mm': [round(v, 6) for v in bb],
                          'min_other_envelope_gap_mm': round(nearest, 6),
                          'related_pad_distances_mm': distances,
                          'worst_related_distance_ratio': round(max(ratios), 6)})
    by_move = sorted(legal, key=lambda row: row['move_mm'])
    by_ratio = sorted(legal, key=lambda row: row['worst_related_distance_ratio'])
    local = [row for row in legal if row['worst_related_distance_ratio'] <= LOCAL_DISTANCE_RATIO]
    if local:
        raise SystemExit('nearby ADC8 cap pose unexpectedly passed locality screen')
    result = {'schema': 1, 'kind': 'ti-vmid-eight-resistor-adc8-cap-placement-bound',
              'status': 'REJECTED_LOCALITY_SCREEN', 'p1_accepted': False,
              'p2_accepted': False, 'routing_realized': False,
              'hashes': {name: sha(path) for name, path in paths.items()},
              'fixed_ref_count': len(fixed), 'fixed_ref_poses_identical': True,
              'pad_net_layer_identity_identical': True,
              'moved_pad_shapes_inside_screened_envelopes': True,
              'grid_step_mm': STEP_MM, 'minimum_physical_gap_mm': BODY_GAP_MM,
              'illustrative_route_mouth_mm': ROUTE_MOUTH_MM,
              'illustrative_max_related_pad_distance_ratio': LOCAL_DISTANCE_RATIO,
              'resistors': resistors,
              'adc8_cap': {'ref': ref, 'original_origin_mm': [ox, oy],
                           'original_physical_bbox_mm': body,
                           'owner_region_mm': owner, 'foreign_region_mm': foreign,
                           'related_pads': related,
                           'owner_and_foreign_clear_grid_count': candidates,
                           'body_clear_grid_count': len(legal),
                           'within_locality_grid_count': len(local),
                           'nearest_body_clear_pose': by_move[0] if by_move else None,
                           'best_related_distance_pose': by_ratio[0] if by_ratio else None},
              'gnd_reference': [{'net': z.GetNetname(), 'filled': z.IsFilled(),
                                 'layers': [board.GetLayerName(i) for i in z.GetLayerSet().Seq()]}
                                for z in board.Zones() if z.GetNetname() == 'GND'],
              'limitation': '0.1-mm grid, unchanged rotations and all other poses fixed. '
                            'No actual trace/return room or DRC-validated combined placement is proved.'}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
