#!/usr/bin/env python3
"""Bounded strict physical-cell feasibility probe; no canonical writes."""
import hashlib, json, sys
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
sys.path[:0] = [str(ROOT / 'skills/kicad-pcb/scripts'), str(BOUNDARY)]
import p1_corridor_capacity as checker
import probe as boundary
EXPECTED = {
    BOARD: 'e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef',
    BASE / 'p1_requirements.yaml': 'f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222',
    BASE / 'floorplan.yaml': '7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    BASE / 'modular_plan.json': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
}
OWNERS = ('analog_ch2', 'analog_ch3', 'analog_ch4')
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def hull(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes)]
def main():
    for path, digest in EXPECTED.items():
        if sha(path) != digest: raise SystemExit(f'input SHA drift: {path}')
    board = pcbnew.LoadBoard(str(BOARD)); native = {f.GetReference(): f for f in board.GetFootprints()}
    plan = json.loads((BASE / 'modular_plan.json').read_text())
    owners = {ref: row['id'] for row in plan['blocks'] for ref in row['refs']}
    if len(native) != 569 or set(native) != set(owners): raise SystemExit('569 owner denominator drift')
    source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
    floor = yaml.safe_load((BASE / 'floorplan.yaml').read_text())
    floor['placement']['post_anchors']['Q_PRE'] = [46, 107.15, 0]
    groups = json.loads((PRIOR / 'result.json').read_text())['groups']
    regions, patterns, _ = boundary.partition(plan, source, floor, groups, 69, 100.5)
    result_cells, connector_envelopes = {}, {}
    # Replace only the three broad rectangles with a complete, one-cell-per-owner
    # partition. This maximizes each candidate cell and is intentionally a
    # feasibility bound, not an adopted physical-cell decomposition.
    for owner in OWNERS:
        refs = sorted(ref for ref, block in owners.items() if block == owner)
        envelope = {ref: checker._physical_envelope(native[ref]) for ref in refs}
        cell_id = owner + '_full'
        result_cells[cell_id] = {'owner': owner, 'refs': refs, 'bbox_mm': hull(envelope.values())}
        connector_envelopes[owner] = {ref: list(box) for ref, box in envelope.items()
                                      if ref.startswith('J')}
        del regions[owner]
        regions[cell_id] = result_cells[cell_id]['bbox_mm']
        source['physical_cells'].append({'id': cell_id, 'owner_block': owner,
                                         'refs': refs, 'transit': False})
        rewritten = []
        for pattern in patterns:
            inside = [ref for ref in pattern['match'] if ref in refs]
            outside = [ref for ref in pattern['match'] if ref not in refs]
            if inside: rewritten.append(dict(pattern, match=inside, region=cell_id))
            if outside: rewritten.append(dict(pattern, match=outside))
        patterns = rewritten
    outline = pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False): raise SystemExit('native outline unavailable')
    try:
        checker._physical_cells(source, plan, board, outline, regions, patterns)
    except checker.ContractError as exc:
        failure = str(exc)
    else:
        raise SystemExit('unexpected full owner-cell acceptance')
    if failure != 'analog_ch2_full: physical cell off board outline':
        raise SystemExit('unexpected first strict failure: ' + failure)
    result = {'status': 'INCOMPLETE', 'p1_accepted': False, 'routing_realized': False,
              'board_sha256': sha(BOARD), 'checker_sha256': sha(ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'),
              'native_ref_count': len(native), 'candidate_cells': result_cells,
              'edge_connector_envelopes': connector_envelopes,
              'first_checker_failure': failure}
    (HERE / 'result.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))
if __name__ == '__main__': main()
