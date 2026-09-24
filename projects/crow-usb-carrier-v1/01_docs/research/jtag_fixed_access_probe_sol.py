#!/usr/bin/env python3
"""Fail-closed, source-only JTAG fixed-access probe on the pinned QSPI-gap board."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PACKET = HERE / 'xu_service_variant/p1_qspi_packet'
BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
INTERFACES = ROOT / 'projects/crow-usb-carrier-v1/03_src/modular_plan.json'
ALIASES = ROOT / 'projects/crow-usb-carrier-v1/02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
PINS = [('JTAG_TMS', 'J_JTAG.2', 'U_XU.44'),
        ('JTAG_TCK', 'J_JTAG.4', 'U_XU.51'),
        ('JTAG_TDO', 'J_JTAG.6', 'U_XU.37'),
        ('JTAG_TDI', 'J_JTAG.8', 'U_XU.36')]
EXPECTED_BOARD = 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact(path, expected):
    actual = sha(path)
    if actual != expected:
        raise RuntimeError(f'{path}: expected {expected}, got {actual}')


def run():
    exact(BOARD, EXPECTED_BOARD)
    exact(PACKET / 'floorplan_qspi_gap.yaml', 'cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925')
    exact(PACKET / 'p1_source_variant.yaml', '9a13c0999d29f17280bb5d8ffb98a5e0d59afe3ee4511eb004e436bffc13ece4')
    exact(INTERFACES, '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e')
    exact(ALIASES, 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e')
    source = yaml.safe_load((PACKET / 'p1_source_variant.yaml').read_text())
    floorplan = yaml.safe_load((PACKET / 'floorplan_qspi_gap.yaml').read_text())
    contract = json.loads((PACKET / 'coarse_contract.json').read_text())
    regions = floorplan['placement']['regions']
    if regions['usb_frontend'] != [200, 35, 236, 70] or regions['debug_connector'] != [218, 35, 238, 65]:
        raise RuntimeError('baseline source regions drift')
    regions['usb_frontend'] = [200, 35, 238.5, 40]
    regions['debug_connector'] = [221, 40, 238, 65]
    regions['board_integration_jtag'] = [221, 65, 226, 84]
    allocation_source = next(a for a in source['allocations'] if a['id'] == 'xmos_service_escape')
    old_demand = next(d for d in allocation_source['demands'] if d['id'] == 'jtag_reset')
    old_demand.update(id='jtag', nets=[n for n, _, _ in PINS], slots=4, required_width_mm=1.8)
    allocation_source['demands'].append({'id': 'xu_reset', 'nets': ['XU_RESET_N'],
                                         'layers': ['F.Cu'], 'slots': 1,
                                         'slot_pitch_mm': .45, 'required_width_mm': .45})
    faces = [{'block': 'debug_connector', 'region_face': 'south', 'bbox': [221.1, 64.7, 225.9, 65]},
             {'block': 'xmos_core', 'region_face': 'north', 'bbox': [221.1, 84, 225.9, 84.3]}]
    endpoints = [{'source_pad': pad, 'native_pad': pad, 'net': net, 'block': block}
                 for net, fixed, xu in PINS for block, pad in
                 [('debug_connector', fixed), ('xmos_core', xu)]]
    face_map = {f['block']: f for f in faces}
    def obligation(endpoint):
        return {'status': 'P2_REQUIRED', **endpoint, 'corridor_id': 'jtag_strip',
                'region_face': face_map[endpoint['block']]['region_face'],
                'layer': 'F.Cu', 'to_reservation': 'jtag_strip_trunk'}
    source['integration_corridors'].append({
        'id': 'jtag_strip', 'owner': 'board_integration',
        'region_id': 'board_integration_jtag', 'allocation_id': 'xmos_service_escape',
        'participants': ['debug_connector', 'xmos_core'], 'faces': faces,
        'layer': 'F.Cu', 'reference_layer': 'In1.Cu',
        'nets': [n for n, _, _ in PINS], 'reservation_id': 'jtag_strip_trunk',
        'affected': endpoints, 'p2_obligations': [obligation(e) for e in endpoints],
        'return_obligation': {'status': 'P2_REQUIRED', 'net': 'GND',
                              'corridor_id': 'jtag_strip', 'reference_layer': 'In1.Cu',
                              'proof': 'continuous_filled_reference'}})
    spec = importlib.util.spec_from_file_location('p1_corridor_capacity', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    board = checker.pcbnew.LoadBoard(str(BOARD))
    outline = checker.pcbnew.SHAPE_POLY_SET()
    if not board.GetBoardPolygonOutlines(outline, False):
        raise RuntimeError('native outline unavailable')
    interfaces = json.loads(INTERFACES.read_text())
    _, native_pads = checker.graph.board_index(board)
    aliases = checker.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    coverage, _ = checker.graph.source_inventory(source, interfaces)
    corridors = checker._integration_corridors(source, interfaces, board, outline,
        regions, list(board.Zones()), coverage, aliases, native_pads, {})
    if set(corridors) != {'qspi_gap', 'jtag_strip'}:
        raise RuntimeError('corridor declarations drift')
    pads = {f'{fp.GetReference()}.{p.GetNumber()}': checker.box_mm(p.GetBoundingBox())
            for fp in board.GetFootprints() for p in fp.Pads()}
    allocation = next(a for a in contract['allocations'] if a['id'] == 'xmos_service_escape')
    allocation['reservations'] = [r for r in allocation['reservations'] if r['id'] != 'jtag_north']
    allocation['reservations'].insert(0, {'id': 'jtag_strip_trunk', 'kind': 'integration_corridor',
        'corridor_id': 'jtag_strip', 'owner': 'board_integration',
        'region_id': 'board_integration_jtag', 'layer': 'F.Cu',
        'bbox': regions['board_integration_jtag'], 'nets': [n for n, _, _ in PINS]})
    allocation['reservations'].append({'id': 'reset_unresolved', 'kind': 'signal', 'layer': 'F.Cu',
        'bbox': [221, 84, 226, 91], 'nets': ['XU_RESET_N'], 'axis': 'vertical',
        'demand_slots': 1, 'slot_pitch_mm': .45})
    allocation['boundary_witnesses'] = [w for w in allocation['boundary_witnesses']
        if w['net'] not in {n for n, _, _ in PINS}]
    for e in endpoints:
        if e['block'] == 'xmos_core':
            allocation['boundary_witnesses'].append({'kind': 'integration_corridor_handoff',
                'corridor_id': 'jtag_strip', 'source': e['source_pad'], 'native': e['native_pad'],
                'net': e['net'], 'block': e['block'], 'face': 'south', 'layer': 'F.Cu',
                'region_face': 'north', 'boundary_bbox': faces[1]['bbox'],
                'reservation_id': 'jtag_strip_trunk', 'p2_obligation': obligation(e)})
    contacts = []
    for net, fixed, _ in PINS:
        pad = pads[fixed]
        # A southward strip can be reached by contact on the pad's bottom or
        # left side. The other two sides point away from the strip and cannot
        # make a single axis-aligned rectangle touch both pad and strip.
        candidates = {'north': [225.85, pad[3], pad[2], 65],
                      'east': [225.85, pad[3] - .01, pad[0], 65]}
        rows = []
        owned = {(n, b): {p} for n, f, x in PINS for b, p in
                 [('debug_connector', f), ('xmos_core', x)]}
        for face, access in candidates.items():
            witness = {'kind': 'fixed_connector_access', 'corridor_id': 'jtag_strip',
                'source': fixed, 'native': fixed, 'net': net, 'block': 'debug_connector',
                'face': face, 'layer': 'F.Cu', 'region_face': 'south',
                'boundary_bbox': list(pad), 'reservation_id': f'access_{fixed.rsplit(".", 1)[1]}',
                'p2_obligation': obligation(next(e for e in endpoints if e['source_pad'] == fixed))}
            reservation = {'id': witness['reservation_id'], 'kind': 'fixed_connector_access',
                'corridor_id': 'jtag_strip', 'layer': 'F.Cu', 'bbox': access, 'nets': [net]}
            checked = checker._coarse_witness(board, witness, net, owned, aliases,
                native_pads, outline, regions, set(source['p1_fixed_refs']), {}, corridors)
            if not checker._witness_touches_reservation(checked, reservation):
                raise RuntimeError(f'{fixed}: {face} witness does not touch access')
            if (not checker.contains(regions['debug_connector'], access) or
                    not checker.intersects(access, faces[0]['bbox']) or
                    not checker._witness_touches_reservation(
                        {'boundary_bbox': access, 'face': 'north'},
                        {'bbox': regions['board_integration_jtag']})):
                raise RuntimeError(f'{fixed}: {face} access does not join source corridor')
            hits = sorted(key for key, box in pads.items()
                          if key != fixed and checker.intersects(access, box))
            bodies = sorted(fp.GetReference() for fp in board.GetFootprints()
                if fp.GetReference() != 'J_JTAG' and fp.GetLayerName() == 'F.Cu'
                and checker.intersects(access, checker._physical_envelope(fp)))
            tracks = sum(item.IsOnLayer(board.GetLayerID('F.Cu')) and
                         checker.intersects(access, checker.box_mm(item.GetBoundingBox()))
                         for item in board.GetTracks())
            rule_areas = sum(zone.GetIsRuleArea() and
                'F.Cu' in {board.GetLayerName(i) for i in zone.GetLayerSet().Seq()} and
                checker.intersects(access, checker.box_mm(zone.GetBoundingBox()))
                for zone in board.Zones())
            other_reservations = sorted(r['id'] for a in contract['allocations']
                for r in a['reservations'] if r.get('layer') == 'F.Cu' and
                r['id'] != 'jtag_strip_trunk' and
                checker.intersects(access, r['bbox']))
            rows.append({'contact_face': face, 'access_bbox_mm': access,
                'native_pad_hits': hits, 'foreign_body_hits': bodies,
                'existing_copper_hits': tracks, 'rule_area_hits': rule_areas,
                'other_reservation_hits': other_reservations,
                'checker_geometry_clear': not (hits or bodies or tracks or rule_areas or other_reservations)})
            if face == 'east' and fixed == 'J_JTAG.8':
                allocation['boundary_witnesses'].append(witness)
                allocation['reservations'].append(reservation)
        for face, reason in [('south', 'reservation north of pad cannot reach y=65'),
                             ('west', 'reservation east of pad cannot reach strip x<=226')]:
            # The checker demands edge equality for these faces. That equality
            # would put the entire rectangle on the wrong side of this pad.
            wrong_side = checker._witness_touches_reservation(
                {'boundary_bbox': pad, 'face': face}, {'bbox': candidates['east']})
            if wrong_side:
                raise RuntimeError(f'{fixed}: unexpected {face} contact to south strip')
            rows.append({'contact_face': face, 'feasible_to_south_strip': False,
                         'checker_contact_with_strip': wrong_side, 'reason': reason})
        contacts.append({'net': net, 'fixed_pad': fixed,
                         'fixed_pad_bbox_mm': list(pad), 'contacts': rows})
    if [r['contacts'][1]['checker_geometry_clear'] for r in contacts] != [False, False, False, True]:
        raise RuntimeError('left-contact geometry outcome drift')
    # Keep one exact fixed access in the whole-packet attempt. The pre-existing
    # reset witness fails before access geometry is consumed by evaluate_coarse.
    first_access = next(w for w in allocation['boundary_witnesses']
                        if w.get('kind') == 'fixed_connector_access')
    allocation['boundary_witnesses'] = [first_access] + [w for w in allocation['boundary_witnesses']
        if w.get('kind') != 'fixed_connector_access']
    allocation['reservations'] = [r for r in allocation['reservations']
        if r.get('kind') != 'fixed_connector_access' or r['id'] == first_access['reservation_id']]
    with tempfile.TemporaryDirectory(prefix='crow-jtag-access-') as tmp:
        tmp = Path(tmp)
        source_path, floor_path, contract_path = [tmp / name for name in
            ('source.yaml', 'floorplan.yaml', 'contract.json')]
        source_path.write_text(yaml.safe_dump(source, sort_keys=False))
        floor_path.write_text(yaml.safe_dump(floorplan, sort_keys=False))
        contract.update(board_sha256=sha(BOARD), source_sha256=sha(source_path),
                        floorplan_sha256=sha(floor_path), interfaces_sha256=sha(INTERFACES),
                        aliases_sha256=sha(ALIASES))
        contract_path.write_text(json.dumps(contract, indent=2) + '\n')
        result = checker.evaluate_coarse(BOARD, contract_path, sha(contract_path),
            source_path=source_path, interface_path=INTERFACES, alias_path=ALIASES,
            floorplan_path=floor_path, expected_source_sha256=sha(source_path),
            expected_interface_sha256=sha(INTERFACES), expected_alias_sha256=sha(ALIASES),
            expected_floorplan_sha256=sha(floor_path))
    report = {'status': 'FAIL', 'scope': 'RESEARCH_ONLY', 'board_sha256': sha(BOARD),
              'checker': str(CHECKER.relative_to(ROOT)), 'fixed_pad_count': 4,
              'xu_pad_count': 4, 'source_region': regions['debug_connector'],
              'strip_region': regions['board_integration_jtag'], 'contacts': contacts,
              'whole_packet': result}
    service = next(a for a in result['allocations'] if a['id'] == 'xmos_service_escape')
    if (result['status'] != 'FAIL' or result['p1_accepted'] or result['routing_realized'] or
            service.get('status') != 'FAIL' or service.get('reason') !=
            'U_XU.38: witness bbox is a nonlocal bridge across source region' or
            result['errors'] != [
                'qspi_gap: integration affected endpoint/layer denominator mismatch',
                'jtag_strip: integration affected endpoint/layer denominator mismatch']):
        raise RuntimeError('unexpected checker rejection outcome')
    (HERE / 'jtag_fixed_access_probe_sol.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'contacts': contacts,
                      'checker_reason': next(a for a in result['allocations']
                                             if a['id'] == 'xmos_service_escape')}, indent=2))


if __name__ == '__main__':
    run()
