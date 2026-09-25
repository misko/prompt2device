#!/usr/bin/env python3
"""Read-only full-envelope lower bound for AUDIO_EN owner repair."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT/'projects/crow-usb-carrier-v1'
RESEARCH = PROJECT/'01_docs/research'
BOARD = RESEARCH/'2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
FLOOR = RESEARCH/'2026-09-25-ti-two-terminal-timing-sol/floorplan.yaml'
PLAN = RESEARCH/'2026-09-25-ti-two-terminal-timing-sol/modular_plan.json'
TRIAL = RESEARCH/'2026-09-25-ti-audio-en-source-probe-sol/receipt.json'
CHECKER = ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED = {
    'board':'d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
    'floor':'7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'plan':'02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
}
TARGETS = ('R_AUDIO_PD', 'U_AUDIO', 'U_ISO1')
PARTNERS = (('U_AUDIO','4','C_AUDIO','1'), ('U_AUDIO','5','C_AUDIO_CT1','1'),
            ('U_AUDIO','5','C_AUDIO_CT2','1'), ('U_ISO1','8','C_ISO1','1'),
            ('R_AUDIO_PD','1','R_AUDIO_PU','2'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def xy(item):
    pos = item.GetPosition()
    return (pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y))


def move_box(box, dx=0, dy=0):
    return (box[0]+dx, box[1]+dy, box[2]+dx, box[3]+dy)


def overlap(box, other):
    return (round(max(0,min(box[2],other[2])-max(box[0],other[0])),6),
            round(max(0,min(box[3],other[3])-max(box[1],other[1])),6))


def screen():
    for name, path in {'board':BOARD,'floor':FLOOR,'plan':PLAN}.items():
        if sha(path) != EXPECTED[name]:
            raise RuntimeError(f'{name}: pinned input drift')
    spec = importlib.util.spec_from_file_location('audio_bound_checker', CHECKER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    board = pcbnew.LoadBoard(str(BOARD))
    fps = {fp.GetReference():fp for fp in board.GetFootprints()}
    floor = yaml.safe_load(FLOOR.read_text())
    regions = floor['placement']['regions']
    plan = json.loads(PLAN.read_text())
    owners = {ref:block['id'] for block in plan['blocks'] for ref in block['refs']}
    if len(fps) != 569 or len(owners) != 569 or set(fps) != set(owners):
        raise RuntimeError('569 exact ref/functional-owner denominator drift')
    boxes = {ref:helper._physical_envelope(fp) for ref,fp in fps.items()}
    targets = []
    for ref in TARGETS:
        fp = fps[ref]
        owner = owners[ref]
        if owner != ('analog_ch1' if ref == 'U_ISO1' else 'quiet_power'):
            raise RuntimeError(f'{ref}: modular owner drift')
        body = boxes[ref]
        audio = [p for p in fp.Pads() if p.GetNetname() == 'AUDIO_EN']
        if len(audio) != 1:
            raise RuntimeError(f'{ref}: AUDIO_EN pad denominator drift')
        pad = audio[0]
        pad_box = helper.box_mm(pad.GetBoundingBox())
        nearest = sorted((round(math.hypot(max(body[0]-other[2],other[0]-body[2],0),
                                           max(body[1]-other[3],other[1]-body[3],0)),6),name)
                         for name,other in boxes.items() if name != ref)[:5]
        targets.append({'ref':ref,'owner':owner,'origin_mm':xy(fp),
                        'body_bbox_mm':body,'audio_en_pad':f'{ref}.{pad.GetNumber()}',
                        'audio_en_pad_bbox_mm':pad_box,
                        'owner_region_mm':regions[owner],
                        'body_owner_contained':helper.contains(regions[owner],body),
                        'pad_owner_contained':helper.contains(regions[owner],pad_box),
                        'minimum_translation_for_body_mm':{
                            'east':round(max(0,regions[owner][0]-body[0]),6),
                            'south':round(max(0,regions[owner][1]-body[1]),6)},
                        'nearest_native_envelopes_mm':nearest})
    recut = {'quiet_power':[min(boxes['R_AUDIO_PD'][0],boxes['U_AUDIO'][0]),
                            min(boxes['R_AUDIO_PD'][1],regions['quiet_power'][1]),
                            regions['quiet_power'][2],regions['quiet_power'][3]],
             'analog_ch1':[boxes['U_ISO1'][0],*regions['analog_ch1'][1:]]}
    new_foreign = {}
    for owner,area in recut.items():
        prior = regions[owner]
        entrants = []
        for ref,fp in fps.items():
            if owners[ref] == owner:
                continue
            for pad in fp.Pads():
                box = helper.box_mm(pad.GetBoundingBox())
                if helper.intersects(box,area) and not helper.intersects(box,prior):
                    entrants.append(f'{ref}.{pad.GetNumber()}')
        new_foreign[owner] = sorted(entrants)
    resistor = boxes['R_AUDIO_PD']
    ct1 = boxes['C_AUDIO_CT1']
    audio_body = boxes['U_AUDIO']
    south = regions['quiet_power'][1]-resistor[1]
    resistor_at_owner = move_box(resistor,dy=south)
    first_overlap = overlap(resistor_at_owner,ct1)
    ct1_south = max(0,resistor_at_owner[3]-ct1[1])
    ct1_at_clearance = move_box(ct1,dy=ct1_south)
    second_overlap = overlap(ct1_at_clearance,audio_body)
    if (round(south,6) != .875 or first_overlap[0] <= 0 or first_overlap[1] <= 0 or
            second_overlap[0] <= 0 or second_overlap[1] <= 0 or
            not {'C_IN3.1','C_IN3.2'} <= set(new_foreign['quiet_power'])):
        raise RuntimeError('local coupled-placement/region-recut lower bound drift')
    distances = []
    for a,ap,b,bp in PARTNERS:
        left = next(p for p in fps[a].Pads() if p.GetNumber() == ap)
        right = next(p for p in fps[b].Pads() if p.GetNumber() == bp)
        if left.GetNetname() != right.GetNetname():
            raise RuntimeError(f'{a}.{ap}/{b}.{bp}: electrical relation drift')
        distances.append({'pads':[f'{a}.{ap}',f'{b}.{bp}'],
                          'net':left.GetNetname(),
                          'native_pad_center_distance_mm':round(math.dist(xy(left),xy(right)),6)})
    trial = json.loads(TRIAL.read_text())
    if (trial['status'] != 'REJECTED_LOCALITY_DRC_FOREIGN' or
            trial['sha256']['exact'] != EXPECTED['board'] or trial['p1_accepted'] or
            trial['p2_accepted'] or trial['fixed_ref_count'] != 27 or
            trial['trial_pose_diff_from_exact'] != sorted(TARGETS)):
        raise RuntimeError('previous source-generated trial disposition drift')
    return {'kind':'crow-audio-en-owner-lower-bound',
            'status':'NO_SMALL_EXCLUSIVE_REPAIR_PROVED', 'p1_accepted':False,
            'p2_accepted':False,'route_credit':False,
            'board_sha256':sha(BOARD), 'floorplan_sha256':sha(FLOOR),
            'modular_plan_sha256':sha(PLAN), 'source_trial_receipt_sha256':sha(TRIAL),
            'targets':targets, 'same_net_local_distances':distances,
            'minimal_rectangular_owner_recut_mm':recut,
            'new_foreign_native_pads_in_recut':new_foreign,
            'minimal_resistor_south_move_mm':round(south,6),
            'resistor_to_ct1_overlap_mm':first_overlap,
            'ct1_south_to_clear_resistor_mm':round(ct1_south,6),
            'ct1_to_audio_overlap_after_clearance_mm':second_overlap,
            'prior_source_generated_trial_status':trial['status'],
            'prior_trial_foreign_body_regions':{row['ref']:row['foreign_regions']
                                                for row in trial['moved']},
            'prior_trial_new_drc_errors':[
                row['items'] for row in trial['native_drc']['added']
                if row['severity'] == 'error']}


if __name__ == '__main__':
    receipt = screen()
    (HERE/'receipt.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(receipt,indent=2,sort_keys=True))
