#!/usr/bin/env python3
"""Reproduce one isolated, unrouted TI TDM/XU placement screen."""
from __future__ import annotations

import fnmatch
import hashlib
import importlib.util
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
PACKET = PROJECT / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
BOARD = PACKET / '04_kicad/crow_carrier.kicad_pcb'
RULES = PACKET / '03_src/rules/p1_corridor_requirements.yaml'
FLOOR = PACKET / '03_src/floorplan.yaml'
BOARD_SHA = '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10'
RULES_SHA = '191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3'
FLOOR_SHA = '0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868'
POSES = {'C_XU_USB18': (198.6, 91.5),
         'C_XU_VDD_104': (197.3, 88.9)}
TEXT_REF = 'R_ADC_I2C_SCL_B_PU'
TEXT_POS = (150.0, 90.0)
OWNER = {'C_XU_USB18': 'xmos_core',
         'C_XU_VDD_104': 'xmos_core',
         'R_ADC_I2C_SCL_B_PU': 'audio_clock_tdm'}
LANE = [182.475, 93.6, 199.825, 100.0]
ORIGINAL_LANE = [182.475, 94.0, 199.825, 100.0]
ENDPOINTS = {'U_TDM_XLATE', 'U_XU'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def poses(board):
    return {fp.GetReference(): [round(pcbnew.ToMM(fp.GetPosition().x), 6),
                                round(pcbnew.ToMM(fp.GetPosition().y), 6),
                                round(fp.GetOrientationDegrees(), 6)]
            for fp in board.GetFootprints()}


def pad_signatures(board):
    return sorted((fp.GetReference(), pad.GetNumber(), pad.GetNetname(),
                   tuple(board.GetLayerName(layer) for layer in pad.GetLayerSet().Seq()))
                  for fp in board.GetFootprints() for pad in fp.Pads())


def physical_pairs(fps, helper):
    boxes = {ref: helper._physical_envelope(fp) for ref, fp in fps.items()}
    names = sorted(boxes)
    return {f'{a}|{b}' for i, a in enumerate(names) for b in names[i+1:]
            if helper.intersects(boxes[a], boxes[b])}


def xu_proximity(board):
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    xu_pads = list(fps['U_XU'].Pads())
    result = {}
    for ref in ('C_XU_USB18', 'C_XU_VDD_104'):
        power = next(pad for pad in fps[ref].Pads() if pad.GetNumber() == '1')
        matches = []
        for pad in xu_pads:
            if pad.GetNetname() == power.GetNetname():
                dx = pcbnew.ToMM(power.GetPosition().x - pad.GetPosition().x)
                dy = pcbnew.ToMM(power.GetPosition().y - pad.GetPosition().y)
                matches.append((round(math.hypot(dx, dy), 6), pad.GetNumber()))
        nearest = min(matches)
        result[ref] = {'power_net': power.GetNetname(),
                       'nearest_xu_pad': nearest[1],
                       'pad_center_distance_mm': nearest[0]}
    return result


def check(board, original, rules, floor, helper):
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    original_fps = {fp.GetReference(): fp for fp in original.GetFootprints()}
    if len(fps) != len(list(board.GetFootprints())) or set(fps) != set(original_fps):
        raise SystemExit('native reference denominator changed')
    if pad_signatures(board) != pad_signatures(original):
        raise SystemExit('pad/net/layer identity changed')
    fixed = set(rules['p1_fixed_refs'])
    if len(fixed) != 27 or any(poses(board)[ref] != poses(original)[ref] for ref in fixed):
        raise SystemExit('P1 fixed pose changed')
    regions = floor['placement']['regions']
    for ref in OWNER:
        matches = {pattern['region'] for pattern in floor['placement']['patterns']
                   for match in pattern['match'] if fnmatch.fnmatchcase(ref, match)}
        if matches != {OWNER[ref]}:
            raise SystemExit(f'{ref}: source owner mapping changed')
        bbox = helper.box_mm(fps[ref].GetBoundingBox(True, True))
        if not helper.contains(regions[OWNER[ref]], bbox):
            raise SystemExit(f'{ref}: full footprint leaves source owner')
        if helper.intersects(LANE, bbox):
            raise SystemExit(f'{ref}: full footprint enters lane')
    if LANE[1] <= regions['analog_ch7'][3] or LANE[1] <= regions['analog_ch8'][3]:
        raise SystemExit('lane enters ch7/8 zone')
    before = physical_pairs(original_fps, helper)
    after = physical_pairs(fps, helper)
    new_pairs = sorted(after - before)
    if new_pairs:
        raise SystemExit(f'new body/courtyard intersections: {new_pairs}')
    obstacles = [(ref, helper.box_mm(fp.GetBoundingBox(True, True)))
                 for ref, fp in fps.items()
                 if fp.GetLayerName() == 'F.Cu' and ref not in ENDPOINTS]
    measured = helper.connected_capacity(LANE, obstacles, 'horizontal', .45)
    original_lane_measured = helper.connected_capacity(ORIGINAL_LANE, obstacles,
                                                       'horizontal', .45)
    if measured['capacity_slots'] < 4 or original_lane_measured['capacity_slots'] < 4:
        raise SystemExit('four-slot full-envelope lane not achieved')
    text = fps[TEXT_REF].Reference().GetPosition()
    if [round(pcbnew.ToMM(text.x), 6), round(pcbnew.ToMM(text.y), 6)] != list(TEXT_POS):
        raise SystemExit('resistor reference-text pose changed')
    if poses(board)[TEXT_REF] != poses(original)[TEXT_REF]:
        raise SystemExit('resistor electrical footprint moved')
    return {'full_bbox_mm': {ref: helper.box_mm(fps[ref].GetBoundingBox(True, True))
                             for ref in OWNER},
            'physical_bbox_mm': {ref: helper._physical_envelope(fps[ref]) for ref in OWNER},
            'new_physical_collision_pairs': new_pairs,
            'baseline_physical_collision_pair_count': len(before),
            'candidate_physical_collision_pair_count': len(after),
            'lane': {'bbox_mm': LANE, 'slot_pitch_mm': .45,
                     'demand_slots': 4,
                     'connected_width_mm': measured['connected_width_mm'],
                     'capacity_slots': measured['capacity_slots'],
                     'foreign_full_footprints': measured['foreign_obstacles']},
            'original_band_lane': {'bbox_mm': ORIGINAL_LANE, 'slot_pitch_mm': .45,
                                   'demand_slots': 4,
                                   'connected_width_mm': original_lane_measured['connected_width_mm'],
                                   'capacity_slots': original_lane_measured['capacity_slots']},
            'fixed_ref_count': len(fixed),
            'fixed_poses_identical': True,
            'pad_net_layer_identity_identical': True,
            'analog_ch7_ch8_port_zones_avoided': True}


def drc_delta(variant):
    """Check with the original project rules and footprint library context."""
    def key(row):
        return (row['type'], row['severity'], row['description'],
                tuple(sorted(item.get('uuid', '') for item in row['items'])))

    with tempfile.TemporaryDirectory(prefix='ti-tdm-xu-drc-') as directory:
        scratch = Path(directory)
        project = scratch / 'project'
        target = project / '04_kicad'
        target.mkdir(parents=True)
        (project / '03_src').symlink_to(PACKET / '03_src', target_is_directory=True)
        for filename in ('crow_carrier.kicad_pro', 'crow_carrier.kicad_dru', 'fp-lib-table'):
            shutil.copy2(PACKET / '04_kicad' / filename, target / filename)
        shutil.copy2(variant, target / 'crow_carrier.kicad_pcb')
        reports = []
        for index, board in enumerate((BOARD, target / 'crow_carrier.kicad_pcb')):
            report = scratch / f'drc-{index}.json'
            subprocess.run(['kicad-cli', 'pcb', 'drc', '--format', 'json',
                            '--output', str(report), str(board)],
                           check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            reports.append(json.loads(report.read_text()))
    before, after = reports
    if sorted(map(key, before['violations'])) != sorted(map(key, after['violations'])):
        raise SystemExit('candidate introduces or changes native DRC violations')
    if len(before['unconnected_items']) != len(after['unconnected_items']):
        raise SystemExit('candidate changes unconnected-item denominator')
    return {'baseline_violations': len(before['violations']),
            'candidate_violations': len(after['violations']),
            'baseline_unconnected_items': len(before['unconnected_items']),
            'candidate_unconnected_items': len(after['unconnected_items']),
            'violation_set_identical': True}


def main():
    for path, expected in ((BOARD, BOARD_SHA), (RULES, RULES_SHA), (FLOOR, FLOOR_SHA)):
        if sha(path) != expected:
            raise SystemExit(f'exact TI packet SHA mismatch: {path}')
    if len(sys.argv) != 2:
        raise SystemExit('usage: probe.py OUTPUT_DIRECTORY')
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    helper_path = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
    spec = importlib.util.spec_from_file_location('p1_capacity', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    rules = yaml.safe_load(RULES.read_text())
    floor = yaml.safe_load(FLOOR.read_text())
    original = pcbnew.LoadBoard(str(BOARD))
    candidate = pcbnew.LoadBoard(str(BOARD))
    fps = {fp.GetReference(): fp for fp in candidate.GetFootprints()}
    old_poses = poses(candidate)
    old_ref = candidate.GetFootprints()
    old_ref_pos = next(fp.Reference().GetPosition() for fp in old_ref
                       if fp.GetReference() == TEXT_REF)
    for ref, (x, y) in POSES.items():
        fps[ref].SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    fps[TEXT_REF].Reference().SetPosition(
        pcbnew.VECTOR2I(pcbnew.FromMM(TEXT_POS[0]), pcbnew.FromMM(TEXT_POS[1])))
    result = check(candidate, original, rules, floor, helper)
    variant = out / 'crow_carrier_tdm_xu_three_ref.kicad_pcb'
    pcbnew.SaveBoard(str(variant), candidate)
    # KiCad may generate a default project sidecar when saving in a new dir;
    # DRC below uses the exact original project configuration in scratch.
    for suffix in ('.kicad_pro', '.kicad_prl'):
        sidecar = variant.with_suffix(suffix)
        if sidecar.exists():
            sidecar.unlink()
    # Validate the serialized native board, not only the in-memory transform.
    result = check(pcbnew.LoadBoard(str(variant)), original, rules, floor, helper)
    result['native_drc_delta'] = drc_delta(variant)
    result['nearest_same_net_xu_pad'] = {'original': xu_proximity(original),
                                         'candidate': xu_proximity(candidate)}
    result['gnd_reference'] = [{'net': zone.GetNetname(), 'filled': zone.IsFilled(),
                                 'layers': [candidate.GetLayerName(layer)
                                            for layer in zone.GetLayerSet().Seq()]}
                                for zone in candidate.Zones()
                                if zone.GetNetname() == 'GND']
    result.update({'schema': 1, 'kind': 'ti-tdm-xu-three-reference-research',
                   'status': 'INCOMPLETE', 'p1_accepted': False,
                   'routing_realized': False,
                   'hashes': {'original_board': sha(BOARD), 'variant_board': sha(variant),
                              'rules': sha(RULES), 'floorplan': sha(FLOOR),
                              'capacity_helper': sha(helper_path)},
                   'original_poses_mm_deg': {ref: old_poses[ref] for ref in OWNER},
                   'candidate_poses_mm_deg': {ref: poses(candidate)[ref] for ref in OWNER},
                   'original_resistor_reference_text_mm': [pcbnew.ToMM(old_ref_pos.x),
                                                            pcbnew.ToMM(old_ref_pos.y)],
                   'candidate_resistor_reference_text_mm': list(TEXT_POS),
                   'endpoint_trunk_exemptions': sorted(ENDPOINTS),
                   'limitation': 'Raw full-envelope corridor only; terminal fanout, routed '
                                 'topology, XU decoupling loop integrity and filled GND return '
                                 'are not proved.'})
    (out / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'variant_sha256': sha(variant),
                      'capacity_slots': result['lane']['capacity_slots'],
                      'new_physical_collision_pairs': result['new_physical_collision_pairs']}))


if __name__ == '__main__':
    main()
