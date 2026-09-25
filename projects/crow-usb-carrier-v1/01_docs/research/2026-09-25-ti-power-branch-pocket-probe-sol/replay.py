#!/usr/bin/env python3
"""Read-only native geometry probe for sparse power branch owner pockets."""
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
PRIOR = PROJECT / '01_docs/research/2026-09-25-quiet-power-functional-cells-sol'
BOUNDARY = PROJECT / '01_docs/research/2026-09-25-power-boundary-two-face-probe-sol'
BOARD = PROJECT / '01_docs/research/2026-09-25-ti-cin3-qpre-owner-repair-sol/candidate.kicad_pcb'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
sys.path.insert(0, str(ROOT / 'skills/kicad-pcb/scripts'))
sys.path.insert(0, str(BOUNDARY))
import p1_corridor_capacity as checker  # noqa: E402
import probe as boundary  # noqa: E402


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hull(boxes):
    boxes = list(boxes)
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]


def main():
    for path, expected in boundary.EXPECTED.items():
        if digest(path) != expected:
            raise SystemExit(f'governed input drift: {path}')
    board = pcbnew.LoadBoard(str(BOARD))
    native = {fp.GetReference(): fp for fp in board.GetFootprints()}
    plan = json.loads((BASE / 'modular_plan.json').read_text())
    owners = {ref: block['id'] for block in plan['blocks'] for ref in block['refs']}
    if len(native) != 569 or len(owners) != 569 or set(native) != set(owners):
        raise SystemExit('569-member native owner denominator drift')
    source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
    floor = yaml.safe_load((BASE / 'floorplan.yaml').read_text())
    floor['placement']['post_anchors']['Q_PRE'] = [46.0, 107.15, 0]
    groups = json.loads((PRIOR / 'result.json').read_text())['groups']
    regions, patterns, _ = boundary.partition(plan, source, floor, groups, 69, 100.5)
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise SystemExit('native outline missing')
    cells = checker._physical_cells(source, plan, board, outline, regions, patterns)
    if len(groups) != 13 or len(cells) < 13:
        raise SystemExit('accepted 13-cell basis drift')

    source_count = {net: sum(len(v) for v in iface['endpoints'].values())
                    for iface in plan['interfaces']
                    for net in [iface['net']] if net in boundary.NETS}
    expected = {'N1V8': 42, 'N3V3X': 27, 'N3V3_ADC': 68, 'N5V_BUCK': 34}
    if source_count != expected or sum(source_count.values()) != 171:
        raise SystemExit('171-terminal full-source denominator drift')

    envelopes = {ref: checker._physical_envelope(fp) for ref, fp in native.items()}
    padboxes = {ref: [checker.box_mm(p.GetBoundingBox()) for p in fp.Pads()]
                for ref, fp in native.items()}
    hashes = {'board': digest(BOARD),
              'floorplan': hashlib.sha256(yaml.safe_dump(floor, sort_keys=False).encode()).hexdigest(),
              'alias': digest(ALIASES)}
    targets = {'U_AFE2': ('analog_ch2', 'N3V3_ADC'),
               'U_AFE3': ('analog_ch3', 'N3V3_ADC'),
               'U_BUCK': ('input_buck', 'N5V_BUCK')}
    trials = {}
    for ref, (owner, net) in targets.items():
        ident = f'{ref.lower()}_branch_pocket'
        row = {'id': ident, 'owner_block': owner, 'refs': [ref],
               'bbox': list(envelopes[ref]),
               'branch_ids': [f'power_{net.lower()}_unplaced_tree'],
               'board_sha256': hashes['board'], 'floorplan_sha256': hashes['floorplan'],
               'alias_sha256': hashes['alias']}
        try:
            checker._branch_owner_pockets({'branch_owner_pockets': [row]}, plan,
                                           board, outline, regions, hashes, patterns)
        except checker.ContractError as exc:
            outcome = {'accepted': False, 'reason': str(exc)}
        else:
            outcome = {'accepted': True, 'reason': None}
        trials[ref] = {'owner': owner, 'net': net, 'full_native_envelope_mm': row['bbox'],
                       'pocket': outcome,
                       'foreign_regions': sorted(name for name, box in regions.items()
                           if name != owner and checker.intersects(row['bbox'], box)),
                       'other_native_intersections': sorted(other for other in native
                           if other != ref and (checker.intersects(row['bbox'], envelopes[other])
                           or any(checker.intersects(row['bbox'], box)
                                  for box in padboxes[other])))}
    if trials['U_AFE2']['pocket']['accepted'] or trials['U_AFE3']['pocket']['accepted'] or trials['U_BUCK']['pocket']['accepted']:
        raise SystemExit('unexpected singleton pocket acceptance')

    recuts = {}
    for owner, right_ref, next_owner in [('analog_ch3', 'U_AFE2', 'analog_ch2'),
                                         ('analog_ch4', 'U_AFE3', 'analog_ch3')]:
        new_left = envelopes[right_ref][2]
        displaced = sorted(ref for ref, native_owner in owners.items()
                           if native_owner == owner and envelopes[ref][0] < new_left)
        recuts[owner] = {'old_left_mm': regions[owner][0], 'required_left_mm': new_left,
                         'displaced_native_refs': displaced,
                         'nearest_displaced_envelopes_mm': {ref: list(envelopes[ref]) for ref in displaced}}

    # Fixed-point rectangular closure from U_BUCK. Every intersecting native
    # footprint must join the refs; first foreign owner is a hard obstruction.
    closure = []
    members = {'U_BUCK'}
    for _ in range(len(native)):
        box = hull(envelopes[ref] for ref in members)
        touching = {ref for ref in native if ref not in members and
                    (checker.intersects(box, envelopes[ref]) or
                     any(checker.intersects(box, pad) for pad in padboxes[ref]))}
        foreign = sorted(ref for ref in touching if owners[ref] != 'input_buck')
        closure.append({'refs': sorted(members), 'bbox_mm': box,
                        'new_same_owner_refs': sorted(touching - set(foreign)),
                        'foreign_refs': foreign})
        if foreign or not touching:
            break
        members.update(touching)
    else:
        raise SystemExit('pocket closure did not terminate')
    if not closure[-1]['foreign_refs']:
        raise SystemExit('unexpected U_BUCK closure')

    result = {'status': 'INCOMPLETE', 'p1_accepted': False,
              'routing_realized': False, 'board_sha256': hashes['board'],
              'checker_sha256': digest(ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'),
              'native_ref_count': len(native), 'quiet_power_cell_count': len(groups),
              'full_power_terminal_counts': source_count,
              'pocket_trials': trials, 'analog_region_recuts': recuts,
              'input_buck_rectangular_pocket_closure': closure}
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
