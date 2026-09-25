#!/usr/bin/env /usr/bin/python3
"""Read-only, exact-board rectangular aperture screen for Crow service/timing."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import yaml

ROOT = Path(__file__).resolve().parents[5]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
PACKET = PROJECT / '01_docs/research/2026-09-25-ti-expanded-locked-p1-sol'
NATIVE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad'
FILES = {
    'board': NATIVE / 'crow_carrier.kicad_pcb',
    'rules_project': NATIVE / 'crow_carrier.kicad_pro',
    'rules_custom': NATIVE / 'crow_carrier.kicad_dru',
    'source': PACKET / 'p1_requirements.yaml',
    'floorplan': PACKET / 'floorplan.yaml',
    'contract': PACKET / 'coarse.json',
    'modular_plan': PACKET / 'modular_plan.json',
    'capacity_helper': ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py',
}
EXPECTED = {
    'board': 'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16',
    'rules_project': '7977bc9edb88e1ef723eb256f07949871493dfda3d2c2491dd5d5b6087ddc094',
    'rules_custom': '00ab83d8484368f132392523972c1f41fc9073423d3c600feec962684f9c3b0a',
    'source': 'e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92',
    'floorplan': '8a805d92d4f57c3a0db00a45d1c9aef57958eb0c219d44f9ca89e5531021d8b4',
    'contract': '9faaed39333c0db45c188003d2ac6bacc69562f259f8332d0d6a79db7d25037f',
    'modular_plan': '02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'capacity_helper': 'fdbf97c70a105205423a7b4430f584344346a2250ddb63a0f71260e7cb284dd0',
}
HELPER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
sys.path.insert(0, str(HELPER.parent))
import p1_corridor_capacity as capacity  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def hits(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def study():
    hashes = {key: sha(path) for key, path in FILES.items()}
    assert hashes == EXPECTED, hashes
    source = yaml.safe_load(FILES['source'].read_text())
    contract = json.loads(FILES['contract'].read_text())
    project = json.loads(FILES['rules_project'].read_text())
    board = capacity.pcbnew.LoadBoard(str(FILES['board']))
    allocs = {a['id']: a for a in source['allocations']}
    ids = ('xmos_service_escape', 'adc_timing_xmos_bundle')
    pads = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            pads.setdefault(f'{fp.GetReference()}.{pad.GetNumber()}', []).append(pad)
    endpoints = {}
    for aid in ids:
        allocation = allocs[aid]
        members = {}
        assert set(allocation['endpoints']) == set(allocation['coverage_nets'])
        for net, owners in allocation['endpoints'].items():
            refs = [ref for group in owners.values() for ref in group]
            assert len(refs) == len(set(refs))
            for ref in refs:
                found = pads.get(ref, [])
                assert found and all(p.GetNetname() == net and p.IsOnLayer(capacity.pcbnew.F_Cu) for p in found), (ref, net)
            members[net] = refs
        endpoints[aid] = {'nets': len(members), 'terminals': sum(map(len, members.values())), 'members': members}
    assert endpoints['xmos_service_escape']['nets'] == 13
    assert endpoints['xmos_service_escape']['terminals'] == 33
    assert endpoints['adc_timing_xmos_bundle']['nets'] == 14
    assert endpoints['adc_timing_xmos_bundle']['terminals'] == 54

    settings = project['board']['design_settings']['rules']
    classes = project['net_settings']['classes']
    default = next(c for c in classes if c['name'] == 'Default')
    patterns = {p['pattern'] for p in project['net_settings']['netclass_patterns']}
    assert not (set(endpoints['xmos_service_escape']['members']) | set(endpoints['adc_timing_xmos_bundle']['members'])) & patterns
    width = default['track_width']
    clearance = default['clearance']
    assert width == .2 and clearance == .15 and settings['min_track_width'] == .15
    assert 'AUDIO_MCLK_1V8' in endpoints['adc_timing_xmos_bundle']['members']

    # Native pad effective shapes are projected to conservative rectangles.
    # Component envelopes and existing copper are rectangles as in the
    # maintained P1 helper; nothing is excluded as a convenient endpoint.
    obstacles = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if fp.GetLayerName() == 'F.Cu':
            obstacles.append((ref + ':body', capacity.box_mm(fp.GetBoundingBox(False, False))))
        for pad in fp.Pads():
            if pad.IsOnLayer(capacity.pcbnew.F_Cu):
                shape = pad.GetEffectiveShape(capacity.pcbnew.F_Cu)
                obstacles.append((ref + ':pad' + pad.GetNumber(), capacity.box_mm(shape.BBox())))
    for item in board.GetTracks():
        if item.IsOnLayer(capacity.pcbnew.F_Cu):
            obstacles.append(('existing-copper', capacity.box_mm(item.GetBoundingBox())))
    expanded = [(name, [box[0]-clearance, box[1]-clearance, box[2]+clearance, box[3]+clearance])
                for name, box in obstacles]
    reservations = [(a['id'], r['id'], r.get('bbox')) for a in contract['allocations']
                    for r in a.get('reservations', []) if r.get('bbox')]
    trials = {
        'qspi_gap_trunk': ([219.2,110.5,223.2,118.5], 'vertical', 6, 'xmos_service_escape'),
        'jtag_strip_trunk': ([221,65,226,84], 'vertical', 4, 'xmos_service_escape'),
        'xtal_handoff': ([217.2,107,218.95,110.5], 'vertical', 2, 'xmos_service_escape'),
        'timing_direct_west': ([182.475,94,199.825,100], 'horizontal', 4, 'adc_timing_xmos_bundle'),
        'timing_boundary_neck': ([188,94,190,99.84], 'horizontal', 4, 'adc_timing_xmos_bundle'),
    }
    sections = {}
    for name, (box, axis, need, owner) in trials.items():
        x0,y0,x1,y1 = box
        inner = [x0+clearance,y0+clearance,x1-clearance,y1-clearance]
        assert inner[0] < inner[2] and inner[1] < inner[3]
        check = capacity.connected_capacity(inner, expanded, axis, width+clearance)
        aperture = check['connected_width_mm']
        slots = max(0, math.floor((aperture + clearance + 1e-9)/(width+clearance)))
        overlap = sorted(f'{aid}:{rid}' for aid,rid,bbox in reservations if rid != name and hits(box,bbox))
        sections[name] = {'box_mm':box,'axis':axis,'required_nets':need,
                          'rectangular_aperture_mm':aperture,'max_parallel_default_traces':slots,
                          'native_obstacles':check['foreign_obstacles'],
                          'other_reservation_overlaps':overlap,
                          'limiting_sections':sorted(check['cross_sections'],key=lambda s:s['reachable_width_mm'])[:3]}
    corridors = {x['id']:x for x in source['integration_corridors'] if x['allocation_id']=='xmos_service_escape'}
    faces = {}
    for key in ('qspi_gap','jtag_strip','xtal_south_cap'):
        faces[key] = [{'block':f['block'],'bbox':f['bbox'],
                       'span_mm':round((f['bbox'][2]-f['bbox'][0]) if key != 'xtal_south_cap' or f['region_face']=='north' else (f['bbox'][3]-f['bbox'][1]),3)}
                      for f in corridors[key]['faces']]
    jtag = next(a for a in contract['allocations'] if a['id']=='xmos_service_escape')
    access = {r['id']:{'min_segment_width_mm':round(min(min(s[2]-s[0],s[3]-s[1]) for s in r['segments']),3),
                       'segment_count':len(r['segments'])}
              for r in jtag['reservations'] if r['id'].startswith('jtag_access_')}
    return {'hashes':hashes,'rules':{'absolute_min_track_mm':settings['min_track_width'],
            'default_track_mm':width,'default_clearance_mm':clearance},
            'endpoints':endpoints,'sections':sections,'service_faces':faces,
            'jtag_authored_access':access,'native_track_count':len(board.GetTracks()),
            'claim':'read-only rectangular F.Cu screen; no P1 admission or route proof'}


if __name__ == '__main__':
    print(json.dumps(study(),indent=2,sort_keys=True))
