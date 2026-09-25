#!/usr/bin/env python3
"""Read-only exact-board VBUS edge-owner schema probe; writes research files only."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
import sys

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
BASE = PROJECT / '01_docs/research/2026-09-25-ti-usb-linked-path-slice-sol'
BOARD = PROJECT / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED_BOARD = '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_checker():
    spec = importlib.util.spec_from_file_location('vbus_p1_checker', CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run():
    checker = load_checker()
    if sha(BOARD) != EXPECTED_BOARD:
        raise RuntimeError('exact TI board hash drift')
    source = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())
    floorplan = yaml.safe_load((BASE / 'floorplan.yaml').read_text())
    interfaces = json.loads((BASE / 'modular_plan.json').read_text())
    contract = json.loads((BASE / 'coarse.json').read_text())
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    endpoints = next(row['endpoints'] for row in interfaces['interfaces'] if row['net'] == 'VBUS_USB')
    expected = {'usb_edge_connector': ['J_USB.10', 'J_USB.15', 'J_USB.2', 'J_USB.7'],
                'usb_frontend': ['C_USB_VBUS.1', 'R_USB_VBUS_BLEED.1', 'U_USB_VBUS_ESD.3'],
                'usb_vbus_sense': ['R_VBUS_B.1']}
    if endpoints != expected or checker.graph.native_identity('J_USB.2', aliases) != 'J_USB.A4' or checker.graph.native_identity('J_USB.10', aliases) != 'J_USB.B4':
        raise RuntimeError('source endpoint or alias authority drift')
    board = checker.pcbnew.LoadBoard(str(BOARD))
    outline = checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise RuntimeError('outline missing')
    refs, pads = checker.graph.board_index(board)
    vbus_pad_boxes = {source_pad: checker.box_mm(pads[checker.graph.native_identity(source_pad, aliases)][0].GetBoundingBox())
                      for source_pad in endpoints['usb_edge_connector']}
    if not (vbus_pad_boxes['J_USB.2'] == vbus_pad_boxes['J_USB.15'] == (232.1, 26.1, 232.7, 27.25)
            and vbus_pad_boxes['J_USB.10'] == vbus_pad_boxes['J_USB.7'] == (227.3, 26.1, 227.9, 27.25)):
        raise RuntimeError('fused VBUS physical sites drift')
    demand = next(a for a in source['allocations'] if a['id'] == 'usb_device_pair')['demands']
    old = next(d for d in demand if d['id'] == 'usb_local_power')
    old['nets'] = ['VBUS_PRESENT_N']
    demand.append({'id': 'vbus_edge_power', 'nets': ['VBUS_USB'], 'status': 'INCOMPLETE',
                   'reason': 'edge handoff and current/return geometry unproved'})
    floorplan['placement']['regions']['board_integration_usb_edge'] = [227, 28, 233, 29]
    order = ['usb_edge_connector', 'usb_frontend', 'usb_vbus_sense']
    def rows(owners):
        return [{'source_pad': source_pad,
                 'native_pad': checker.graph.native_identity(source_pad, aliases),
                 'net': 'VBUS_USB', 'block': owner}
                for owner in owners for source_pad in endpoints[owner]]
    physical_affected = rows(order[:2])
    virtual_affected = rows(order[1:])
    faces = [{'block': 'usb_edge_connector', 'region_face': 'south',
              'bbox': [227.1, 27.8, 232.9, 28]},
             {'block': 'usb_frontend', 'region_face': 'north',
              'bbox': [227.1, 29, 232.9, 29.2]}]
    physical = {'id': 'vbus_edge_stage', 'kind': 'physical_corridor',
                'owner': 'board_integration', 'region_id': 'board_integration_usb_edge',
                'allocation_id': 'usb_device_pair', 'participants': order[:2],
                'faces': faces, 'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
                'nets': ['VBUS_USB'], 'reservation_id': 'vbus_edge_stage_trunk',
                'affected': physical_affected,
                'p2_obligations': [{'status': 'P2_REQUIRED', **e,
                                    'corridor_id': 'vbus_edge_stage',
                                    'region_face': 'south' if e['block'] == order[0] else 'north',
                                    'layer': 'F.Cu', 'to_reservation': 'vbus_edge_stage_trunk'}
                                   for e in physical_affected],
                'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                      'corridor_id': 'vbus_edge_stage',
                                      'reference_layer': 'In1.Cu',
                                      'proof': 'continuous_filled_reference'},
                'fixed_accesses': [{'source_pad': s,
                                    'native_pad': checker.graph.native_identity(s, aliases),
                                    'net': 'VBUS_USB', 'block': order[0], 'face': 'north',
                                    'bbox': [b[0], b[3], b[2], 28]}
                                   for s,b in vbus_pad_boxes.items()],
                'axis': 'vertical', 'slot_pitch_mm': 0.45, 'demand_slots': 1}
    virtual = {'id': 'vbus_frontend_to_sense_pending', 'kind': 'unresolved_virtual_span',
               'participants': order[1:], 'nets': ['VBUS_USB'], 'layer': 'F.Cu',
               'reference_layer': 'In1.Cu', 'affected': virtual_affected,
               'geometry': None, 'capacity_slots': None, 'status': 'INCOMPLETE',
               'p2_obligations': [{'status': 'P2_REQUIRED', **e,
                                   'stage_id': 'vbus_frontend_to_sense_pending',
                                   'layer': 'F.Cu', 'to_reservation': 'vbus_edge_series'}
                                  for e in virtual_affected],
               'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                                     'stage_id': 'vbus_frontend_to_sense_pending',
                                     'reference_layer': 'In1.Cu',
                                     'proof': 'continuous_filled_reference'}}
    path = {'id': 'vbus_edge_series', 'allocation_id': 'usb_device_pair',
            'nets': ['VBUS_USB'], 'owner_order': order,
            'reservation_id': 'vbus_edge_series', 'layer': 'F.Cu',
            'reference_layer': 'In1.Cu', 'stages': [physical, virtual],
            'joins': [{'from': physical['id'], 'to': virtual['id'],
                       'owner': order[1], 'net': 'VBUS_USB', 'source_pad': s,
                       'kind': 'pad_anchored_virtual_interstage'}
                      for s in sorted(endpoints[order[1]])]}
    source['linked_paths'] = [path]
    alloc = next(a for a in contract['allocations'] if a['id'] == 'usb_device_pair')
    alloc['linked_paths'] = [{'id': path['id'], 'kind': 'linked_path',
                              'nets': path['nets'], 'status': 'INCOMPLETE'}]
    source_file = HERE / 'p1_requirements.yaml'
    floorplan_file = HERE / 'floorplan.yaml'
    contract_file = HERE / 'coarse.json'
    source_file.write_text(yaml.safe_dump(source, sort_keys=False))
    floorplan_file.write_text(yaml.safe_dump(floorplan, sort_keys=False))
    contract['source_sha256'] = sha(source_file)
    contract['floorplan_sha256'] = sha(floorplan_file)
    contract_file.write_text(json.dumps(contract, indent=2) + '\n')
    # Probe the exact source-stage declaration first, before the old top-level
    # VBUS reservations and the four fused fixed-access paths are considered.
    coverage, _ = checker.graph.source_inventory(source, interfaces)
    regions = floorplan['placement']['regions']
    zones = list(board.Zones())
    cells = checker._physical_cells(source, interfaces, board, outline, regions,
                                    floorplan['placement']['patterns'])
    ports = checker._shared_ports(source, interfaces, board, outline, regions,
                                  zones, coverage, aliases, pads)
    owned = defaultdict(set)
    for item in interfaces['interfaces']:
        for owner, sources in item['endpoints'].items():
            owned[(item['net'], owner)].update(sources)
    fixed = set(source['p1_fixed_refs'])
    native = board.GetDesignSettings()
    pitch = checker.pcbnew.ToMM(native.m_TrackMinWidth + native.m_MinClearance)
    def probe(c):
        try:
            checker._linked_paths(source, c, interfaces, board, outline, regions,
                                  zones, coverage, aliases, pads, owned, fixed,
                                  set(refs)-fixed, ports, cells, pitch)
        except Exception as exc:
            return str(exc)
        return 'UNEXPECTED_PASS'
    ordinary_rejection = probe(contract)
    isolated = copy.deepcopy(contract)
    a = next(a for a in isolated['allocations'] if a['id'] == 'usb_device_pair')
    a['boundary_witnesses'] = [w for w in a['boundary_witnesses'] if w['net'] != 'VBUS_USB']
    a['reservations'] = [r for r in a['reservations'] if 'VBUS_USB' not in r['nets']]
    fused_rejection = probe(isolated)
    original_data_path = yaml.safe_load((BASE / 'p1_requirements.yaml').read_text())['linked_paths'][0]
    source['linked_paths'] = [original_data_path, path]
    concurrent = copy.deepcopy(isolated)
    ca = next(a for a in concurrent['allocations'] if a['id'] == 'usb_device_pair')
    ca['linked_paths'] = [{'id': original_data_path['id'], 'kind': 'linked_path',
                           'nets': original_data_path['nets'], 'status': 'INCOMPLETE'},
                          {'id': path['id'], 'kind': 'linked_path',
                           'nets': path['nets'], 'status': 'INCOMPLETE'}]
    concurrent_rejection = probe(concurrent)
    source['linked_paths'] = [path]
    wrong_alias = {'source': 'J_USB.2', 'native': 'J_USB.B4',
                   'net': 'VBUS_USB', 'block': 'usb_edge_connector',
                   'layer': 'F.Cu', 'face': 'north',
                   'boundary_bbox': list(vbus_pad_boxes['J_USB.10']),
                   'kind': 'fixed_connector_access',
                   'corridor_id': physical['id'],
                   'p2_obligation': physical['p2_obligations'][0]}
    try:
        checker._coarse_witness(board, wrong_alias, 'VBUS_USB', owned,
                                aliases, pads, outline, regions, fixed, ports, {}, {}, cells)
    except Exception as exc:
        wrong_alias_rejection = str(exc)
    else:
        wrong_alias_rejection = 'UNEXPECTED_PASS'
    access_boxes = {a['source_pad']: a['bbox'] for a in physical['fixed_accesses']}
    fused_site_collision = {
        'A4_B9': access_boxes['J_USB.2'] == access_boxes['J_USB.15'],
        'B4_A9': access_boxes['J_USB.10'] == access_boxes['J_USB.7'],
    }
    expected_rejections = (
        ('competing ordinary credit/witness', ordinary_rejection),
        ('U_USB_CC_ESD intersects integration corridor/face', fused_rejection),
        ('linked path contract declaration mismatch', concurrent_rejection),
        ('witness source/native alias mismatch', wrong_alias_rejection),
    )
    if (any(fragment not in observed for fragment, observed in expected_rejections)
            or not all(fused_site_collision.values())):
        raise RuntimeError('fail-closed VBUS trial predicate drift')
    receipt = {'board_sha256': sha(BOARD), 'checker_sha256': sha(CHECKER),
               'source_sha256': sha(source_file), 'floorplan_sha256': sha(floorplan_file),
               'alias_sha256': sha(ALIASES), 'full_vbus_endpoints': endpoints,
               'native_connector_pad_boxes_mm': vbus_pad_boxes,
               'ordinary_credit_rejection': ordinary_rejection,
               'after_removing_ordinary_vbus_credit': fused_rejection,
               'concurrent_data_vbus_path_rejection': concurrent_rejection,
               'wrong_A4_B4_alias_rejection': wrong_alias_rejection,
               'fused_site_access_boxes_identical': fused_site_collision,
               'p1_accepted': False}
    (HERE / 'result.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'ordinary': ordinary_rejection,
                      'isolated': fused_rejection,
                      'concurrent': concurrent_rejection,
                      'alias': wrong_alias_rejection,
                      'fused': fused_site_collision}, indent=2))

if __name__ == '__main__':
    run()
