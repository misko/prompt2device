#!/usr/bin/env python3
"""Exact native-envelope lower bound for two quiet-power branch pads."""
from __future__ import annotations

import hashlib
import json
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
BASE = PROJECT / '01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol'
BOARD = PROJECT / '01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
sys.path.insert(0, str(ROOT / 'skills/kicad-pcb/scripts'))
import p1_corridor_capacity as checker  # noqa: E402

EXPECTED = {
    BOARD: 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
    BASE / 'p1_requirements.yaml': 'f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222',
    BASE / 'floorplan.yaml': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    BASE / 'modular_plan.json': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
}
TARGETS = {'N3V3_ADC': 'C_LDO_OUT_1.1', 'N5V_BUCK': 'R_PWR_TOP.1'}
CLUSTERS = {
    'ldo': ['U_LDO', 'C_LDO_OUT_1', 'C_LDO_OUT_2', 'C_LDO_IN',
            'C_LDO_NR4', 'C_LDO_NR5', 'R_LDO_ILIM', 'R_LDO_PG_TOP', 'R_LDO_SET'],
    'pwr': ['U_PWR', 'R_PWR_TOP', 'R_PWR_BOT', 'R_PWR_PU', 'C_PWR', 'C_PWR_CT'],
}


def hull(boxes):
    boxes = list(boxes)
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]


def main():
    for path, wanted in EXPECTED.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != wanted:
            raise SystemExit(f'input drift: {path}')
    board = pcbnew.LoadBoard(str(BOARD))
    native = {fp.GetReference(): fp for fp in board.GetFootprints()}
    plan = json.loads((BASE / 'modular_plan.json').read_text())
    owners = {ref: block['id'] for block in plan['blocks'] for ref in block['refs']}
    if len(native) != 569 or set(native) != set(owners):
        raise SystemExit('569 native/modular owner denominator drift')
    regions = yaml.safe_load((BASE / 'floorplan.yaml').read_text())['placement']['regions']
    envelopes = {ref: checker._physical_envelope(fp) for ref, fp in native.items()}
    pads = {}
    for net, pad_id in TARGETS.items():
        ref, number = pad_id.rsplit('.', 1)
        found = [p for p in native[ref].Pads() if p.GetNumber() == number]
        if len(found) != 1 or found[0].GetNetname() != net or owners[ref] != 'quiet_power':
            raise SystemExit(f'{pad_id}: exact net/owner/pad drift')
        pads[pad_id] = list(checker.box_mm(found[0].GetBoundingBox()))
    pad_hull = hull(pads.values())
    target_body_hull = hull(envelopes[pad_id.rsplit('.', 1)[0]] for pad_id in TARGETS.values())
    foreign = sorted(ref for ref, box in envelopes.items()
                     if owners[ref] != 'quiet_power' and checker.intersects(pad_hull, box))
    if len(foreign) != 58 or {owners[ref] for ref in foreign} != {'adc_reference'}:
        raise SystemExit('foreign body lower bound drift')
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit('native outline unavailable')
    trial_regions = dict(regions, quiet_power=target_body_hull)
    try:
        checker._physical_cells(
            {'physical_cells': [{'id': 'quiet_power', 'owner_block': 'quiet_power',
                                 'refs': ['C_LDO_OUT_1', 'R_PWR_TOP'], 'transit': False}]},
            plan, board, outline, trial_regions, [])
    except checker.ContractError as exc:
        rejected_reason = str(exc)
        if 'unassigned native footprint/pad' not in rejected_reason:
            raise SystemExit(f'unexpected trial rejection: {exc}')
    else:
        raise SystemExit('impossible common owner cell was accepted')
    quiet_refs = sorted(ref for ref, owner in owners.items() if owner == 'quiet_power')
    if len(quiet_refs) != 69:
        raise SystemExit('quiet-power owner denominator drift')
    adc_refs = sorted(ref for ref, owner in owners.items() if owner == 'adc_reference')
    adc_hull = hull(envelopes[ref] for ref in adc_refs)
    clusters = {}
    for name, refs in CLUSTERS.items():
        if any(owners[ref] != 'quiet_power' for ref in refs):
            raise SystemExit(f'{name}: cluster owner drift')
        area = hull(envelopes[ref] for ref in refs)
        clusters[name] = {
            'refs': refs, 'native_envelope_hull_mm': area,
            'foreign_regions': sorted(key for key, region in regions.items()
                                      if key != 'quiet_power' and checker.intersects(area, region)),
            'foreign_native_envelopes': sorted(ref for ref, box in envelopes.items()
                                               if owners[ref] != 'quiet_power' and checker.intersects(area, box)),
        }
    report = {
        'board_sha256': EXPECTED[BOARD], 'native_ref_count': len(native),
        'quiet_power_ref_count': len(quiet_refs),
        'target_pad_bboxes_mm': pads, 'minimum_common_owner_pad_hull_mm': pad_hull,
        'target_full_envelope_hull_mm': target_body_hull,
        'foreign_envelopes_in_minimum_pad_hull': foreign,
        'foreign_envelope_count': len(foreign),
        'minimal_common_cell_checker_rejection': rejected_reason,
        'adc_reference_ref_count': len(adc_refs),
        'adc_reference_native_hull_mm': adc_hull,
        'foreign_envelopes_in_adc_native_hull': sorted(
            ref for ref, box in envelopes.items()
            if owners[ref] != 'adc_reference' and checker.intersects(adc_hull, box)),
        'regions_intersecting_target_body_hull': sorted(
            key for key, region in regions.items() if checker.intersects(target_body_hull, region)),
        'clusters': clusters,
    }
    (HERE / 'conflict_graph.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'foreign_envelope_count': len(foreign),
                      'clusters': {name: row['native_envelope_hull_mm']
                                   for name, row in clusters.items()}}, indent=2))


if __name__ == '__main__':
    main()
