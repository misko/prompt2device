#!/usr/bin/env python3
"""Conservative, hash-bound P1 placement corridor screens.

Contract JSON schema 1: ``board_sha256``, ``expected_interface_coverage``
(allocation ID to net list), ``required_rule_areas`` (native name/bbox/layers
records), ``reference_plane_required``, and nonempty ``allocations``. The
optional ``profile: crow-p1`` pins the four allocation IDs and all 59 interface
nets, including ``power_boundary_nets``. Each allocation has a unique ``id``,
``coverage_nets``, ``axis`` (horizontal/vertical), ``through_lane``
[x0,y0,x1,y1] in mm, nonempty ``layers`` (KiCad copper layer names), positive
``slot_pitch_mm`` and ``demand_slots``, exact ``coverage_members`` ref.pad IDs,
and ``endpoint_pockets`` [{"ref": "J1", "pad": "1", "net": "N",
"pocket": [x0,y0,x1,y1]}]. Pockets must contact but not intersect the
lane and contain their footprint geometry. The CLI requires an independently
expected contract SHA-256 as well as the contract's bound board SHA-256.

The screen bounds outer-layer footprint bodies, copper pads, and existing
copper items on each named layer. Its raw slot count is optimistic because
effective per-net width/clearance and pad access are not yet measured. A lane
with enough raw slots therefore remains INCOMPLETE; a lane with too few fails.
Rule-area or pour overlap also returns INCOMPLETE. This tool makes no route,
DRC, connector FULL, or P1 engineering-acceptance claim.

Schema 2 ``p1-coarse-reservations`` checks source-bound coverage, selected
boundary witnesses and rough reservation capacity without all-terminal pockets.
It requires an explicit source-owned ``p1_fixed_refs`` set; other P2-movable
occupants are reported as relocation debt. It cannot accept P1 on its own.
An optional source ``shared_transition_ports`` list authorizes a named
``board_integration`` port across declared logical regions. Each record binds
the union zone, participants, exact affected source/native ref.pad/net/block
tuples, port bbox/face/layers, reservation scope, P2 pad-to-port obligations,
and a P2 filled-reference return obligation. A matching witness can use only
that port and never receives a rough capacity credit.
An optional ``integration_corridors`` source list binds an empty, disjoint
``board_integration`` floorplan region, two adjacent source faces, exact
endpoints/net demand and P2 pad-to-face/filled-reference obligations. Its
matching ``integration_corridor`` reservation remains INCOMPLETE without raw
slot credit; geometry cannot establish native access or return continuity.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import yaml

_graph_spec = importlib.util.spec_from_file_location(
    'p1_corridor_graph', Path(__file__).with_name('p1_corridor_graph.py'))
if _graph_spec is None or _graph_spec.loader is None:
    raise ImportError('adjacent p1_corridor_graph.py unavailable')
graph = importlib.util.module_from_spec(_graph_spec)
_graph_spec.loader.exec_module(graph)

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew


class ContractError(ValueError):
    pass


CROW_COVERAGE = {
    'usb_device_pair': 'USB_DN USB_DP VBUS_USB VBUS_PRESENT_N',
    'xmos_service_escape': 'QSPI_CLK QSPI_CS_N QSPI_D0 QSPI_D1 QSPI_D2 QSPI_D3 JTAG_TCK JTAG_TDI JTAG_TDO JTAG_TMS XU_RESET_N XTAL_IN XTAL_OUT',
    'adc_timing_xmos_bundle': 'ADC_BCLK ADC_FSYNC ADC_DOUT1 AUDIO_MCLK_1V8 TDM_BCLK_1V8 TDM_DATA_1V8 TDM_FSYNC_1V8 ADC_I2C_SCL ADC_I2C_SDA ADC_READY AUDIO_EN XU_I2C_SCL_1V8 XU_I2C_SDA_1V8 ADC_DIGITAL_BAD',
    'adc_analog_boundary': 'ADC1N ADC1P ADC2N ADC2P ADC3N ADC3P ADC4N ADC4P ADC5N ADC5P ADC6N ADC6P ADC7N ADC7P ADC8N ADC8P VMID1_EXT VMID2_EXT',
    'power_boundary_windows': 'CHASSIS GND N0V9 N12V_PROTECTED N1V8 N3V3X N3V3_ADC N5V_BUCK N5V_LDO_HOLD PWR_EN',
}
CROW_COVERAGE = {name: set(value.split()) for name, value in CROW_COVERAGE.items()}


def _coarse_hash(path, label, errors):
    if path is None:
        errors.append(f'{label} path missing')
        return None
    try:
        return digest(Path(path))
    except OSError as exc:
        errors.append(f'{label} unavailable: {exc}')
        return None


def _coarse_witness(board, witness, net, owned_pads, aliases, pads, outline,
                    regions, fixed_refs, shared_ports, integration_corridors=None):
    source = witness.get('source')
    native = witness.get('native')
    block = witness.get('block')
    if not isinstance(source, str) or source not in owned_pads.get((net, block), set()):
        raise ContractError(f'{net}: witness source/block ownership mismatch')
    if native != graph.native_identity(source, aliases):
        raise ContractError(f'{source}: witness source/native alias mismatch')
    found = pads.get(native, [])
    if not found or any(p.GetNetname() != net for p in found):
        raise ContractError(f'{native}: witness native pad/net mismatch')
    layer = witness.get('layer')
    if not isinstance(layer, str) or layer not in {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq()
                                                   if pcbnew.IsCopperLayer(i)}:
        raise ContractError(f'{source}: witness layer unavailable')
    face = witness.get('face')
    if face not in ('north', 'south', 'east', 'west'):
        raise ContractError(f'{source}: witness block face missing')
    area = rectangle(witness.get('boundary_bbox'), f'{source} boundary bbox')
    if not lane_inside_outline(outline, area):
        raise ContractError(f'{source}: witness boundary off board')
    region = rectangle(regions.get(block), f'{block} source region')
    region_span = min(region[2] - region[0], region[3] - region[1])
    kind = witness.get('kind', 'native_pad_face')
    if kind != 'shared_transition_port' and (area[2] - area[0] > region_span / 4 + 1e-6 or area[3] - area[1] > region_span / 4 + 1e-6):
        raise ContractError(f'{source}: witness bbox is a nonlocal bridge across source region')
    ref = native.rsplit('.', 1)[0]
    if kind == 'native_pad_face':
        if ref not in fixed_refs:
            raise ContractError(f'{source}: P2-movable owner requires virtual block-face witness')
        if not all(p.IsOnLayer(board.GetLayerID(layer)) for p in found):
            raise ContractError(f'{source}: physical witness pad not on declared layer')
        if not all(contains(area, box_mm(p.GetBoundingBox())) for p in found):
            raise ContractError(f'{source}: physical witness pad outside block-face boundary')
        obligation = None
    elif kind == 'virtual_block_face':
        if ref in fixed_refs:
            raise ContractError(f'{source}: fixed P1 ref cannot use virtual witness')
        if witness.get('region_id') != block:
            raise ContractError(f'{source}: virtual witness source-region identity mismatch')
        if not contains(region, area):
            raise ContractError(f'{source}: virtual witness leaves owning source region')
        region_face = witness.get('region_face')
        opposites = {'west': 'east', 'east': 'west', 'north': 'south', 'south': 'north'}
        if region_face != opposites[face]:
            raise ContractError(f'{source}: virtual region/reservation face mismatch')
        edge_index = {'west': 0, 'north': 1, 'east': 2, 'south': 3}[region_face]
        if abs(area[edge_index] - region[edge_index]) > 1e-6:
            raise ContractError(f'{source}: virtual witness does not touch source region face')
        if any(abs(area[i] - region[i]) <= 1e-6 for i in range(4) if i != edge_index):
            raise ContractError(f'{source}: virtual witness touches ambiguous region corner')
        obligation = witness.get('p2_obligation')
        expected_obligation = {'status': 'P2_REQUIRED', 'source_pad': source,
                               'native_pad': native, 'net': net, 'block': block,
                               'region_face': region_face, 'layer': layer,
                               'to_reservation': witness.get('reservation_id')}
        if obligation != expected_obligation:
            raise ContractError(f'{source}: explicit P2 pad-to-face obligation missing')
        if not any(p.IsOnLayer(i) for p in found for i in board.GetEnabledLayers().Seq()
                   if pcbnew.IsCopperLayer(i)):
            raise ContractError(f'{source}: virtual source pad has no native copper layer')
    elif kind == 'shared_transition_port':
        port = shared_ports.get(witness.get('port_id'))
        if port is None:
            raise ContractError(f'{source}: undeclared shared transition port')
        exact_endpoint = {'source_pad': source, 'native_pad': native, 'net': net, 'block': block}
        if exact_endpoint not in port['affected']:
            raise ContractError(f'{source}: shared port endpoint/net/owner not source declared')
        if layer not in port['layers'] or face != port['face'] or area != port['bbox']:
            raise ContractError(f'{source}: shared port face/layer/geometry mismatch')
        if witness.get('reservation_id') != port['reservation_id']:
            raise ContractError(f'{source}: shared port reservation identity mismatch')
        obligation = witness.get('p2_obligation')
        expected_obligation = {'status': 'P2_REQUIRED', **exact_endpoint,
                               'port_id': port['id'], 'layer': layer,
                               'to_reservation': port['reservation_id']}
        if obligation != expected_obligation:
            raise ContractError(f'{source}: exact P2 pad-to-port obligation missing')
        if not any(p.IsOnLayer(board.GetLayerID(layer)) for p in found):
            raise ContractError(f'{source}: native source pad not on shared port layer')
    elif kind == 'integration_corridor_handoff':
        corridor = (integration_corridors or {}).get(witness.get('corridor_id'))
        if corridor is None:
            raise ContractError(f'{source}: undeclared integration corridor')
        if ref in fixed_refs:
            raise ContractError(f'{source}: fixed P1 ref cannot use integration handoff')
        if witness.get('reservation_id') != corridor['reservation_id'] or layer != corridor['layer']:
            raise ContractError(f'{source}: integration reservation/layer mismatch')
        faces = {item['block']: item for item in corridor['faces']}
        selected = faces.get(block)
        if selected is None or witness.get('region_face') != selected['region_face'] or area != selected['bbox']:
            raise ContractError(f'{source}: integration owner/face mismatch')
        opposites = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        if face != opposites[selected['region_face']]:
            raise ContractError(f'{source}: integration face direction mismatch')
        endpoint = {'source_pad': source, 'native_pad': native, 'net': net, 'block': block}
        if endpoint not in corridor['affected']:
            raise ContractError(f'{source}: integration endpoint not declared')
        obligation = witness.get('p2_obligation')
        expected = {'status': 'P2_REQUIRED', **endpoint,
                    'corridor_id': corridor['id'], 'region_face': selected['region_face'],
                    'layer': layer, 'to_reservation': corridor['reservation_id']}
        if obligation != expected:
            raise ContractError(f'{source}: integration P2 pad-to-face obligation missing')
        if not any(p.IsOnLayer(board.GetLayerID(layer)) for p in found):
            raise ContractError(f'{source}: native source pad not on integration layer')
    else:
        raise ContractError(f'{source}: unknown boundary witness kind')
    return {'source': source, 'native': native, 'net': net, 'block': block,
            'face': face, 'layer': layer, 'boundary_bbox': area,
            'kind': kind, 'p2_obligation': obligation}


def _witness_touches_reservation(witness, reservation):
    a = witness['boundary_bbox']
    b = rectangle(reservation.get('bbox'), 'reservation bbox')
    face = witness['face']
    tol = 1e-6
    if face in ('west', 'east'):
        shared = min(a[3], b[3]) - max(a[1], b[1]) > tol
        return shared and (abs(a[2] - b[0]) <= tol if face == 'west' else abs(a[0] - b[2]) <= tol)
    shared = min(a[2], b[2]) - max(a[0], b[0]) > tol
    return shared and (abs(a[3] - b[1]) <= tol if face == 'north' else abs(a[1] - b[3]) <= tol)


def _virtual_region_clearance(witness, reservation, regions):
    """A virtual face and its exterior reservation cannot consume another cell.

    Shared board-integration transitions need an explicit source authority and
    separate model; there is no implicit exception for overlapping regions.
    Physical witnesses have their fixed native pad/pose checks instead.
    """
    if witness.get('kind') != 'virtual_block_face':
        return
    boundary = rectangle(witness.get('boundary_bbox'), 'virtual boundary bbox')
    reserved = rectangle(reservation.get('bbox'), 'virtual reservation bbox')
    for region_id, value in regions.items():
        region = rectangle(value, f'{region_id} source region')
        if region_id != witness['block'] and intersects(boundary, region):
            raise ContractError(f"{witness['source']}: virtual boundary enters {region_id} source region")
        if intersects(reserved, region):
            raise ContractError(f"{witness['source']}: virtual reservation enters {region_id} source region")


def _shared_ports(source, interfaces, board, outline, regions, zones, coverage, aliases, pads):
    """Validate source-owned, measured exceptions before any witness may use one."""
    rows = source.get('shared_transition_ports', [])
    if not isinstance(rows, list):
        raise ContractError('shared transition ports malformed')
    owner_rows = interfaces.get('blocks')
    if rows and not isinstance(owner_rows, list):
        raise ContractError('shared transition ports require modular block ownership')
    owners = {}
    for row in owner_rows or []:
        for ref in row.get('refs', []):
            if ref in owners:
                raise ContractError(f'{ref}: duplicate modular footprint owner')
            owners[ref] = row.get('id')
    enabled = {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq() if pcbnew.IsCopperLayer(i)}
    ports = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ContractError('shared transition port record malformed')
        ident = row.get('id')
        if not isinstance(ident, str) or not ident or ident in ports or row.get('owner') != 'board_integration':
            raise ContractError('shared transition port identity/owner invalid')
        participants = row.get('participants')
        if not isinstance(participants, list) or len(participants) < 2 or len(participants) != len(set(participants)) or not set(participants) <= set(regions):
            raise ContractError(f'{ident}: shared port participants invalid')
        geometry = row.get('geometry')
        if not isinstance(geometry, dict) or geometry.get('type') != 'union_rectangles':
            raise ContractError(f'{ident}: shared port union geometry missing')
        zone_rects = geometry.get('rectangles')
        if not isinstance(zone_rects, list) or not zone_rects:
            raise ContractError(f'{ident}: shared port zone rectangles missing')
        zone_rects = [rectangle(v, f'{ident} zone') for v in zone_rects]
        bbox = rectangle(row.get('bbox'), f'{ident} port')
        scope = rectangle(row.get('reservation_bbox'), f'{ident} reservation scope')
        if any(not lane_inside_outline(outline, r) for r in zone_rects + [bbox, scope]):
            raise ContractError(f'{ident}: shared port off board outline')
        if not any(contains(r, bbox) for r in zone_rects):
            raise ContractError(f'{ident}: port outside declared zone')
        if not any(contains(r, scope) for r in zone_rects):
            raise ContractError(f'{ident}: reservation scope outside declared zone')
        for participant in participants:
            if not any(intersects(r, rectangle(regions[participant], f'{participant} region')) for r in zone_rects):
                raise ContractError(f'{ident}: participant does not intersect zone')
        for region_id, value in regions.items():
            if region_id not in participants and any(intersects(r, rectangle(value, f'{region_id} region')) for r in zone_rects + [scope]):
                raise ContractError(f'{ident}: unowned overlap with {region_id} source region')
        layers = row.get('layers')
        if not isinstance(layers, list) or not layers or len(layers) != len(set(layers)) or not set(layers) <= enabled:
            raise ContractError(f'{ident}: shared port layers unavailable')
        face = row.get('face')
        if face not in ('north', 'south', 'east', 'west') or not isinstance(row.get('reservation_id'), str):
            raise ContractError(f'{ident}: shared port face/reservation missing')
        if any(existing['reservation_id'] == row['reservation_id'] for existing in ports.values()):
            raise ContractError(f'{ident}: shared port reservation identity reused')
        affected = row.get('affected')
        if not isinstance(affected, list) or not affected or any(not isinstance(e, dict) or set(e) != {'source_pad', 'native_pad', 'net', 'block'} for e in affected):
            raise ContractError(f'{ident}: exact affected endpoints missing')
        if len({tuple(sorted(e.items())) for e in affected}) != len(affected):
            raise ContractError(f'{ident}: duplicate affected endpoint')
        for e in affected:
            if e['block'] not in participants or e['net'] not in set().union(*coverage.values()):
                raise ContractError(f'{ident}: undeclared net/owner')
            if not any(e['source_pad'] in item.get('endpoints', {}).get(e['block'], [])
                       for item in interfaces['interfaces'] if item.get('net') == e['net']):
                raise ContractError(f'{ident}: affected endpoint has no exact source owner')
            if e['native_pad'] != graph.native_identity(e['source_pad'], aliases):
                raise ContractError(f'{ident}: affected native alias mismatch')
            if owners.get(e['native_pad'].rsplit('.', 1)[0]) != e['block']:
                raise ContractError(f'{ident}: affected native footprint/block owner mismatch')
            found = pads.get(e['native_pad'], [])
            if not found or any(p.GetNetname() != e['net'] for p in found):
                raise ContractError(f'{ident}: affected native pad/net mismatch')
        expected_p2 = [{'status': 'P2_REQUIRED', **e, 'port_id': ident,
                        'layer': layer, 'to_reservation': row['reservation_id']}
                       for e in affected for layer in layers]
        if row.get('p2_obligations') != expected_p2:
            raise ContractError(f'{ident}: source P2 pad-to-port obligations incomplete')
        for fp in board.GetFootprints():
            ref = fp.GetReference()
            body = box_mm(fp.GetBoundingBox(True, True))
            pad_boxes = [box_mm(p.GetBoundingBox()) for p in fp.Pads()]
            if any(intersects(shape, r) for shape in [body] + pad_boxes for r in zone_rects + [scope]):
                if owners.get(ref) not in participants:
                    raise ContractError(f'{ident}: foreign footprint {ref} intersects shared zone/reservation')
            if any(intersects(shape, bbox) for shape in [body] + pad_boxes):
                raise ContractError(f'{ident}: native footprint/pad {ref} intersects shared port')
        for zone in zones:
            if zone.GetIsRuleArea() and set(layers) & {board.GetLayerName(i) for i in zone.GetLayerSet().Seq()} and any(intersects(r, box_mm(zone.GetBoundingBox())) for r in zone_rects + [bbox, scope]):
                raise ContractError(f'{ident}: immutable native rule area intersects shared zone/port')
        expected_return = {'status': 'P2_REQUIRED', 'net': 'GND', 'port_id': ident,
                           'layers': layers, 'proof': 'continuous_filled_reference'}
        if row.get('return_obligation') != expected_return:
            raise ContractError(f'{ident}: P2 filled-reference return obligation missing')
        ports[ident] = {**row, 'bbox': bbox, 'reservation_bbox': scope, 'zone_rectangles': zone_rects}
    return ports


def _integration_corridors(source, interfaces, board, outline, regions, zones,
                           coverage, aliases, pads, shared_ports):
    """Validate a disjoint source cell; declarations are P2 debt, never proof."""
    rows = source.get('integration_corridors', [])
    if not isinstance(rows, list):
        raise ContractError('integration corridors malformed')
    blocks = interfaces.get('blocks')
    if rows and not isinstance(blocks, list):
        raise ContractError('integration corridors require modular block ownership')
    owners = {}
    for block in blocks or []:
        for ref in block.get('refs', []):
            if ref in owners:
                raise ContractError(f'{ref}: duplicate modular footprint owner')
            owners[ref] = block.get('id')
    enabled = {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq()
               if pcbnew.IsCopperLayer(i)}
    corridors, reservations = {}, set()
    for row in rows:
        if not isinstance(row, dict):
            raise ContractError('integration corridor record malformed')
        ident, region_id, reservation_id = (row.get(k) for k in ('id', 'region_id', 'reservation_id'))
        if (not all(isinstance(v, str) and v for v in (ident, region_id, reservation_id)) or
                ident in corridors or reservation_id in reservations or
                row.get('owner') != 'board_integration' or region_id not in regions):
            raise ContractError('integration corridor identity/owner/region invalid')
        reservations.add(reservation_id)
        area = rectangle(regions[region_id], f'{ident} region')
        if not lane_inside_outline(outline, area):
            raise ContractError(f'{ident}: integration region off board outline')
        for other_id, other in regions.items():
            if other_id != region_id and intersects(area, rectangle(other, f'{other_id} region')):
                raise ContractError(f'{ident}: integration region overlaps {other_id}')
        participants = row.get('participants')
        faces = row.get('faces')
        if (not isinstance(participants, list) or len(participants) != 2 or
                len(set(participants)) != 2 or region_id in participants or
                any(p not in regions for p in participants) or
                not isinstance(faces, list) or len(faces) != 2 or
                {f.get('block') for f in faces if isinstance(f, dict)} != set(participants)):
            raise ContractError(f'{ident}: integration participants/faces invalid')
        layer = row.get('layer')
        if layer not in enabled:
            raise ContractError(f'{ident}: integration signal layer unavailable')
        net_list = row.get('nets')
        allocation_id = row.get('allocation_id')
        if (not isinstance(net_list, list) or not net_list or len(set(net_list)) != len(net_list) or
                allocation_id not in coverage or not set(net_list) <= coverage[allocation_id]):
            raise ContractError(f'{ident}: integration net/allocation invalid')
        source_alloc = next((a for a in source.get('allocations', [])
                             if a.get('id') == allocation_id), None)
        if source_alloc is None or not any(set(d.get('nets', [])) == set(net_list)
                                           for d in source_alloc.get('demands', [])):
            raise ContractError(f'{ident}: partial or undeclared source demand')
        normalized_faces = []
        for face in faces:
            block, direction = face.get('block'), face.get('region_face')
            if direction not in ('north', 'south', 'east', 'west'):
                raise ContractError(f'{ident}: integration face direction invalid')
            owner = rectangle(regions[block], f'{block} region')
            boundary = rectangle(face.get('bbox'), f'{ident} {block} face')
            edge = {'west': 0, 'north': 1, 'east': 2, 'south': 3}[direction]
            if (not contains(owner, boundary) or
                    abs(boundary[edge] - owner[edge]) > 1e-6 or
                    any(abs(boundary[i] - owner[i]) <= 1e-6 for i in range(4) if i != edge) or
                    not _witness_touches_reservation(
                        {'boundary_bbox': boundary,
                         'face': {'north': 'south', 'south': 'north',
                                  'east': 'west', 'west': 'east'}[direction]},
                        {'bbox': area})):
                raise ContractError(f'{ident}: integration face lacks positive non-corner shared edge')
            for foreign_id, foreign in regions.items():
                if foreign_id != block and intersects(boundary, rectangle(foreign, f'{foreign_id} region')):
                    raise ContractError(f'{ident}: integration face overlaps foreign region {foreign_id}')
            normalized_faces.append({**face, 'bbox': boundary})
        for port in shared_ports.values():
            shapes = [port['bbox'], port['reservation_bbox']] + port['zone_rectangles']
            if any(intersects(shape, area) or any(intersects(shape, f['bbox']) for f in normalized_faces)
                   for shape in shapes):
                raise ContractError(f'{ident}: integration corridor overlaps shared port {port["id"]}')
        affected = row.get('affected')
        if (not isinstance(affected, list) or not affected or
                any(not isinstance(e, dict) or set(e) != {'source_pad', 'native_pad', 'net', 'block'}
                    for e in affected) or
                len({tuple(sorted(e.items())) for e in affected}) != len(affected)):
            raise ContractError(f'{ident}: integration affected endpoints invalid')
        expected = set()
        for item in interfaces['interfaces']:
            if item['net'] in net_list:
                for block in participants:
                    for source_pad in item.get('endpoints', {}).get(block, []):
                        expected.add((source_pad, graph.native_identity(source_pad, aliases),
                                      item['net'], block))
        actual = {(e['source_pad'], e['native_pad'], e['net'], e['block']) for e in affected}
        if actual != expected or {e['net'] for e in affected} != set(net_list):
            raise ContractError(f'{ident}: integration endpoint denominator mismatch')
        for e in affected:
            native_pad = e['native_pad']
            if (owners.get(native_pad.rsplit('.', 1)[0]) != e['block'] or
                    not pads.get(native_pad) or
                    any(p.GetNetname() != e['net'] or not p.IsOnLayer(board.GetLayerID(layer))
                        for p in pads[native_pad])):
                raise ContractError(f'{ident}: integration native owner/pad/net/layer mismatch')
        face_by_block = {f['block']: f for f in normalized_faces}
        expected_p2 = [{'status': 'P2_REQUIRED', **e, 'corridor_id': ident,
                        'region_face': face_by_block[e['block']]['region_face'],
                        'layer': layer, 'to_reservation': reservation_id} for e in affected]
        if row.get('p2_obligations') != expected_p2:
            raise ContractError(f'{ident}: integration P2 pad-to-face obligations incomplete')
        reference = row.get('reference_layer')
        if reference not in enabled or reference == layer or row.get('return_obligation') != {
                'status': 'P2_REQUIRED', 'net': 'GND', 'corridor_id': ident,
                'reference_layer': reference, 'proof': 'continuous_filled_reference'}:
            raise ContractError(f'{ident}: integration P2 filled-reference return obligation missing')
        for fp in board.GetFootprints():
            shapes = [box_mm(fp.GetBoundingBox(True, True))] + [box_mm(p.GetBoundingBox()) for p in fp.Pads()]
            if any(intersects(shape, area) or any(intersects(shape, f['bbox']) for f in normalized_faces)
                   for shape in shapes):
                raise ContractError(f'{ident}: native footprint/pad {fp.GetReference()} intersects integration corridor/face')
        for item in board.GetTracks():
            if (any(item.IsOnLayer(board.GetLayerID(copper)) for copper in enabled) and
                    any(intersects(box_mm(item.GetBoundingBox()), shape)
                        for shape in [area] + [f['bbox'] for f in normalized_faces])):
                raise ContractError(f'{ident}: native copper intersects integration corridor')
        for zone in zones:
            if zone.GetIsRuleArea() and any(intersects(box_mm(zone.GetBoundingBox()), shape)
                                                for shape in [area] + [f['bbox'] for f in normalized_faces]):
                raise ContractError(f'{ident}: immutable native rule area intersects integration corridor/face')
        corridors[ident] = {**row, 'bbox': area, 'faces': normalized_faces}
    return corridors


def _coarse_reservation(board, row, outline, fixed_refs, movable_refs, zones, native_pitch,
                        *, power_boundary, power_like_nets):
    ident = row.get('id')
    layer = row.get('layer')
    bbox = rectangle(row.get('bbox'), f'{ident} reservation')
    if not isinstance(ident, str) or not ident:
        raise ContractError('reservation id missing')
    if not lane_inside_outline(outline, bbox):
        raise ContractError(f'{ident}: reservation off board outline')
    enabled = {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq() if pcbnew.IsCopperLayer(i)}
    if layer not in enabled:
        raise ContractError(f'{ident}: reservation layer unavailable')
    for zone in zones:
        if zone.GetIsRuleArea() and layer in {board.GetLayerName(i) for i in zone.GetLayerSet().Seq()} and intersects(bbox, box_mm(zone.GetBoundingBox())):
            raise ContractError(f'{ident}: immutable native rule area overlaps reservation')
    nets = row.get('nets')
    if not isinstance(nets, list) or not nets or len(nets) != len(set(nets)):
        raise ContractError(f'{ident}: reservation net demand missing')
    if row.get('kind') == 'power_or_mechanical':
        if not power_boundary and not set(nets) <= power_like_nets:
            raise ContractError(f'{ident}: only source-authorized power-like nets may omit signal capacity')
        return {'id': ident, 'status': 'INCOMPLETE', 'nets': nets,
                'reason': 'current, return, thermal, or mechanical capacity unmeasured'}
    if row.get('kind') != 'signal':
        raise ContractError(f'{ident}: reservation kind missing')
    axis = row.get('axis')
    pitch, demand = row.get('slot_pitch_mm'), row.get('demand_slots')
    if axis not in ('horizontal', 'vertical') or isinstance(pitch, bool) or not isinstance(pitch, (int, float)) or not math.isfinite(pitch) or pitch < native_pitch or isinstance(demand, bool) or not isinstance(demand, int) or demand < 1:
        raise ContractError(f'{ident}: nonzero native-compatible rough demand missing')
    # Relocatable P2 parts are excluded only from the *potential* bound. Their
    # current intersection remains explicit debt, never a capacity credit.
    potential = connected_capacity(bbox, layer_obstacles(board, layer, movable_refs), axis, pitch)
    current = connected_capacity(bbox, layer_obstacles(board, layer, set()), axis, pitch)
    movable_hits = sorted({fp.GetReference() for fp in board.GetFootprints()
                           if fp.GetReference() in movable_refs and
                           (intersects(bbox, box_mm(fp.GetBoundingBox(False, False))) or
                            any(p.IsOnLayer(board.GetLayerID(layer)) and intersects(bbox, box_mm(p.GetBoundingBox())) for p in fp.Pads()))})
    fixed_hits = sorted({name.split(':')[0] for name in potential['foreign_obstacles'] if name != 'existing-copper'})
    status = 'FAIL' if potential['capacity_slots'] < demand else 'INCOMPLETE'
    return {'id': ident, 'status': status, 'nets': nets, 'demand_slots': demand,
            'potential_slots': potential['capacity_slots'], 'current_slots': current['capacity_slots'],
            'fixed_obstacles': fixed_hits, 'movable_relocation_debt': movable_hits,
            'existing_copper_obstacle': 'existing-copper' in potential['foreign_obstacles'],
            'reason': 'fixed/raw neck below demand' if status == 'FAIL' else
                      'rough capacity only; movable debt, effective rules, reference and P2 access unproved'}


def evaluate_coarse(board_path, contract_path, expected_contract_sha256=None, *,
                    source_path=None, interface_path=None, alias_path=None, floorplan_path=None,
                    expected_source_sha256=None, expected_interface_sha256=None,
                    expected_alias_sha256=None, expected_floorplan_sha256=None):
    errors, results, hashes = [], [], {}
    shared_ports_configured = integration_configured = False
    paths = {'board': board_path, 'contract': contract_path, 'source': source_path,
             'interfaces': interface_path, 'aliases': alias_path, 'floorplan': floorplan_path}
    for label, path in paths.items():
        hashes[label] = _coarse_hash(path, label, errors)
    expected = {'contract': expected_contract_sha256, 'source': expected_source_sha256,
                'interfaces': expected_interface_sha256, 'aliases': expected_alias_sha256,
                'floorplan': expected_floorplan_sha256}
    for label, value in expected.items():
        if value is None or value != hashes[label]:
            errors.append(f'{label} not bound to independent expected digest')
    if all(hashes.values()):
        try:
            contract = json.loads(Path(contract_path).read_text())
            source = yaml.safe_load(Path(source_path).read_text())
            shared_ports_configured = isinstance(source, dict) and 'shared_transition_ports' in source
            integration_configured = isinstance(source, dict) and 'integration_corridors' in source
            interfaces = json.loads(Path(interface_path).read_text())
            aliases = graph.alias_inventory(yaml.safe_load(Path(alias_path).read_text()))
            floorplan = yaml.safe_load(Path(floorplan_path).read_text())
            if contract.get('schema') != 2 or contract.get('kind') != 'p1-coarse-reservations':
                raise ContractError('coarse contract kind/schema mismatch')
            for label in ('board', 'source', 'interfaces', 'aliases', 'floorplan'):
                if contract.get(label + '_sha256') != hashes[label]:
                    errors.append(f'{label} hash drift in coarse contract')
            coverage, terminals = graph.source_inventory(source, interfaces)
            if source.get('schema') == 1 and contract.get('profile') != 'crow-p1-coarse':
                raise ContractError('production P1 source requires crow-p1-coarse profile')
            if contract.get('profile') == 'crow-p1-coarse':
                if len(terminals) != 59 or coverage != CROW_COVERAGE:
                    raise ContractError('crow-p1-coarse 59-net source coverage mismatch')
            elif contract.get('profile') != 'fixture-coarse':
                raise ContractError('unsupported coarse profile')
            board = pcbnew.LoadBoard(str(board_path))
            outline = pcbnew.SHAPE_POLY_SET()
            if board is None or not board.GetBoardPolygonOutlines(outline, False) or outline.OutlineCount() != 1:
                raise ContractError('native outline unavailable or unsupported')
            refs, pads = graph.board_index(board)
            placement = floorplan.get('placement', {})
            anchors = placement.get('anchors')
            post_anchors = placement.get('post_anchors', {})
            seeds = placement.get('seeds', {})
            regions = placement.get('regions', {})
            if not isinstance(anchors, dict) or not isinstance(post_anchors, dict) or not isinstance(seeds, dict):
                raise ContractError('source-owned fixed/movable placement classification missing')
            if not isinstance(regions, dict):
                raise ContractError('source floorplan regions missing')
            # Generator precedence is post_anchors > anchors > seeds. A ref may
            # intentionally have a seed and a reviewed final post-anchor pose.
            # Validate P1-fixed refs against the effective pose below.
            patterns = placement.get('patterns', [])
            if not isinstance(patterns, list) or any(not isinstance(p, dict) or not isinstance(p.get('match'), list) for p in patterns):
                raise ContractError('source placement patterns malformed')
            pattern_refs = {ref for pattern in patterns for ref in pattern['match']}
            unknown = set(refs) - set(anchors) - set(post_anchors) - set(seeds) - pattern_refs
            if unknown:
                raise ContractError(f'unclassified native footprint roles: {sorted(unknown)[:5]}')
            fixed_declared = source.get('p1_fixed_refs')
            if (not isinstance(fixed_declared, list) or not fixed_declared or
                    len(fixed_declared) != len(set(fixed_declared)) or
                    any(ref not in refs or ref not in set(anchors) | set(post_anchors)
                        for ref in fixed_declared)):
                raise ContractError('source-owned p1_fixed_refs authority missing or invalid')
            fixed_refs = set(fixed_declared)
            for ref in fixed_refs:
                expected_pose = (anchors | post_anchors)[ref]
                actual_position = refs[ref].GetPosition()
                actual_pose = (pcbnew.ToMM(actual_position.x), pcbnew.ToMM(actual_position.y),
                               refs[ref].GetOrientationDegrees())
                if len(expected_pose) != 3 or any(abs(float(a) - float(b)) > 1e-3
                                                  for a, b in zip(expected_pose, actual_pose)):
                    raise ContractError(f'{ref}: fixed P1 source/native pose mismatch')
            movable_refs = set(refs) - fixed_refs
            # A mechanical hole cannot be silently reclassified as movable.  It
            # must be in the source-owned fixed set so its pose was validated
            # above, rather than merely influencing the native capacity scan.
            npth_refs = {ref for ref, fp in refs.items()
                         if any(p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH for p in fp.Pads())}
            omitted_npth = sorted(npth_refs - fixed_refs)
            if omitted_npth:
                raise ContractError(f'NPTH references missing p1_fixed_refs: {omitted_npth[:5]}')
            owned_pads = defaultdict(set)
            for item in interfaces['interfaces']:
                for block, sources in item['endpoints'].items():
                    owned_pads[(item['net'], block)].update(sources)
            allocations = contract.get('allocations')
            if not isinstance(allocations, list) or len(allocations) != len(coverage):
                raise ContractError('coarse allocation denominator mismatch')
            names = [r.get('id') for r in allocations if isinstance(r, dict)]
            if len(names) != len(set(names)) or set(names) != set(coverage):
                raise ContractError('coarse allocation identities mismatch')
            zones = list(board.Zones())
            shared_ports = _shared_ports(source, interfaces, board, outline, regions,
                                         zones, coverage, aliases, pads)
            corridors = _integration_corridors(source, interfaces, board, outline, regions,
                                               zones, coverage, aliases, pads, shared_ports)
            used_port_endpoints = defaultdict(set)
            used_corridor_endpoints = defaultdict(set)
            native = board.GetDesignSettings()
            native_pitch = pcbnew.ToMM(native.m_TrackMinWidth + native.m_MinClearance)
            if native_pitch <= 0:
                raise ContractError('native routing pitch unavailable')
            reservations_seen = [(allocation.get('id'), reservation)
                                 for allocation in allocations if isinstance(allocation, dict)
                                 for reservation in allocation.get('reservations', [])
                                 if isinstance(reservation, dict)]
            all_ids = [r.get('id') for _, r in reservations_seen]
            if len(all_ids) != len(set(all_ids)):
                raise ContractError('duplicate global reservation id')
            if {p['reservation_id'] for p in shared_ports.values()} & {c['reservation_id'] for c in corridors.values()}:
                raise ContractError('shared port/integration corridor reservation identity reused')
            for allocation in allocations:
                name = allocation['id']
                try:
                    power_like_nets = set()
                    if name == 'usb_device_pair':
                        source_row = next((item for item in source['allocations'] if item.get('id') == name), {})
                        local_power = [item for item in source_row.get('demands', [])
                                       if item.get('id') == 'usb_local_power' and item.get('status') == 'INCOMPLETE']
                        if len(local_power) == 1 and 'VBUS_USB' in local_power[0].get('nets', []):
                            # VBUS_PRESENT_N shares the source demand but is a
                            # logic signal and retains scalar signal capacity.
                            power_like_nets.add('VBUS_USB')
                    nets = allocation.get('coverage_nets')
                    if not isinstance(nets, list) or len(nets) != len(set(nets)) or set(nets) != coverage[name]:
                        raise ContractError(f'{name}: exact source net coverage mismatch')
                    witnesses = allocation.get('boundary_witnesses')
                    reservations = allocation.get('reservations')
                    if not isinstance(witnesses, list) or not witnesses or not isinstance(reservations, list) or not reservations:
                        raise ContractError(f'{name}: witness/reservation denominator missing')
                    checked = []
                    for witness in witnesses:
                        if witness.get('net') not in coverage[name]:
                            raise ContractError(f'{name}: witness net outside allocation')
                        checked.append(_coarse_witness(board, witness, witness['net'], owned_pads,
                                                       aliases, pads, outline, regions, fixed_refs,
                                                       shared_ports, corridors))
                    if {w['net'] for w in checked} != coverage[name]:
                        raise ContractError(f'{name}: missing per-net boundary witness')
                    if len({(w['source'], w['net']) for w in checked}) != len(checked):
                        raise ContractError(f'{name}: duplicate boundary witness')
                    virtual_claims = [(w['net'], w['block'], w.get('region_face'),
                                       w['layer'], w.get('reservation_id'))
                                      for w in witnesses if w.get('kind') == 'virtual_block_face']
                    if len(virtual_claims) != len(set(virtual_claims)):
                        raise ContractError(f'{name}: duplicate virtual net-face claim')
                    reservation_map = {r.get('id'): r for r in reservations if isinstance(r, dict)}
                    if len(reservation_map) != len(reservations):
                        raise ContractError(f'{name}: duplicate reservation id')
                    for witness, verified in zip(witnesses, checked):
                        target = reservation_map.get(witness.get('reservation_id'))
                        if (target is None or verified['net'] not in target.get('nets', []) or
                                verified['layer'] != target.get('layer') or
                                not _witness_touches_reservation(verified, target)):
                            raise ContractError(f"{verified['source']}: block face does not contact assigned reservation")
                        _virtual_region_clearance(witness, target, regions)
                        if witness.get('kind') == 'shared_transition_port':
                            port = shared_ports[witness['port_id']]
                            if (target.get('id') != port['reservation_id'] or
                                    target.get('layer') not in port['layers'] or
                                    set(target.get('nets', [])) != {e['net'] for e in port['affected']} or
                                    not contains(port['reservation_bbox'], rectangle(target.get('bbox'), 'shared reservation'))):
                                raise ContractError(f"{verified['source']}: reservation outside declared shared port scope")
                            used_port_endpoints[port['id']].add((verified['source'], verified['native'],
                                                                  verified['net'], verified['block'], verified['layer']))
                        if witness.get('kind') == 'integration_corridor_handoff':
                            corridor = corridors[witness['corridor_id']]
                            if (name != corridor['allocation_id'] or
                                    target.get('id') != corridor['reservation_id'] or
                                    target.get('kind') != 'integration_corridor' or
                                    target.get('corridor_id') != corridor['id'] or
                                    target.get('owner') != 'board_integration' or
                                    target.get('region_id') != corridor['region_id'] or
                                    rectangle(target.get('bbox'), 'integration reservation') != corridor['bbox']):
                                raise ContractError(f"{verified['source']}: integration reservation owner/scope mismatch")
                            used_corridor_endpoints[corridor['id']].add((verified['source'], verified['native'],
                                                                         verified['net'], verified['block'], verified['layer']))
                    measured = []
                    for reservation in reservations:
                        if not set(reservation.get('nets', [])) <= coverage[name]:
                            raise ContractError(f'{name}: reservation net outside allocation')
                        associated = [p for p in shared_ports.values() if p['reservation_id'] == reservation.get('id')]
                        integration = [c for c in corridors.values() if c['reservation_id'] == reservation.get('id')]
                        if integration or reservation.get('kind') == 'integration_corridor':
                            if (len(integration) != 1 or name != integration[0]['allocation_id'] or
                                    'status' in reservation or
                                    reservation.get('kind') != 'integration_corridor' or
                                    reservation.get('corridor_id') != integration[0]['id'] or
                                    reservation.get('owner') != 'board_integration' or
                                    reservation.get('region_id') != integration[0]['region_id'] or
                                    reservation.get('layer') != integration[0]['layer'] or
                                    set(reservation.get('nets', [])) != set(integration[0]['nets']) or
                                    rectangle(reservation.get('bbox'), 'integration reservation') != integration[0]['bbox']):
                                raise ContractError(f'{name}: integration reservation source mismatch')
                            measured.append({'id': reservation['id'], 'status': 'INCOMPLETE',
                                             'nets': reservation['nets'],
                                             'reason': 'P2 native pad-to-face, filled-reference return and effective capacity unproved'})
                            continue
                        if associated:
                            if len(associated) != 1 or not contains(associated[0]['reservation_bbox'], rectangle(reservation.get('bbox'), 'shared reservation')):
                                raise ContractError(f'{name}: reservation outside declared shared port scope')
                            measured.append({'id': reservation['id'], 'status': 'INCOMPLETE',
                                             'nets': reservation['nets'],
                                             'reason': 'P2 pad-to-port, return, effective capacity and routing unproved'})
                            continue
                        measured.append(_coarse_reservation(
                            board, reservation, outline, fixed_refs, movable_refs, zones, native_pitch,
                            power_boundary=name == 'power_boundary_windows',
                            power_like_nets=power_like_nets))
                    if {net for r in measured for net in r['nets']} != coverage[name]:
                        raise ContractError(f'{name}: missing per-net reservation')
                    results.append({'id': name, 'status': 'FAIL' if any(r['status'] == 'FAIL' for r in measured) else 'INCOMPLETE',
                                    'witness_count': len(checked), 'reservation_count': len(measured),
                                    'p2_obligations': [w['p2_obligation'] for w in checked if w['p2_obligation']],
                                    'reservations': measured})
                except (ContractError, TypeError, KeyError, AttributeError) as exc:
                    reason = str(exc)
                    definite_geometry_failure = ('off board outline' in reason or
                                                 'immutable native rule area' in reason or
                                                 'virtual boundary enters' in reason or
                                                 'virtual reservation enters' in reason or
                                                 any(w.get('kind') == 'shared_transition_port'
                                                     for w in (allocation.get('boundary_witnesses') or [])
                                                     if isinstance(w, dict)) or
                                                 any(w.get('kind') == 'integration_corridor_handoff'
                                                     for w in (allocation.get('boundary_witnesses') or [])
                                                     if isinstance(w, dict)) or
                                                 any(r.get('kind') == 'integration_corridor'
                                                     for r in (allocation.get('reservations') or [])
                                                     if isinstance(r, dict)))
                    results.append({'id': name, 'status': 'FAIL' if definite_geometry_failure else 'INCOMPLETE',
                                    'reason': reason})
            for ident, port in shared_ports.items():
                expected_uses = {(e['source_pad'], e['native_pad'], e['net'], e['block'], layer)
                                 for e in port['affected'] for layer in port['layers']}
                if used_port_endpoints[ident] != expected_uses:
                    errors.append(f'{ident}: shared port affected endpoint/layer denominator mismatch')
            for ident, corridor in corridors.items():
                expected_uses = {(e['source_pad'], e['native_pad'], e['net'], e['block'], corridor['layer'])
                                 for e in corridor['affected']}
                if used_corridor_endpoints[ident] != expected_uses:
                    errors.append(f'{ident}: integration affected endpoint/layer denominator mismatch')
                matches = [(name, r) for name, r in reservations_seen
                           if r.get('id') == corridor['reservation_id']]
                if len(matches) != 1:
                    errors.append(f'{ident}: integration reservation denominator mismatch')
                for name, reservation in reservations_seen:
                    if (reservation.get('id') != corridor['reservation_id'] and
                            set(reservation.get('nets', [])) & set(corridor['nets'])):
                        errors.append(f'{ident}: integration net double reservation credit in {name}')
                    if (reservation.get('id') != corridor['reservation_id'] and
                            intersects(rectangle(reservation.get('bbox'), 'reservation'), corridor['bbox'])):
                        errors.append(f'{ident}: integration corridor overlaps reservation in {name}')
            for index, (left_name, left) in enumerate(reservations_seen):
                for right_name, right in reservations_seen[index + 1:]:
                    if (left_name != right_name and left.get('layer') == right.get('layer') and
                            intersects(rectangle(left.get('bbox'), 'reservation'), rectangle(right.get('bbox'), 'reservation'))):
                        errors.append(f'overlapping named allocations on one layer: {left_name}/{right_name}')
            if any('endpoint_pockets' in row or 'coverage_members' in row or 'through_lane' in row or
                   row.get('local_endpoint_completion') in ('PASS', 'P1_REQUIRED') for row in allocations):
                errors.append('coarse P1 contract attempts P2/P3 all-terminal proof')
        except (ContractError, ValueError, TypeError, AttributeError, RuntimeError, KeyError) as exc:
            errors.append(str(exc))
    status = 'FAIL' if (any(row['status'] == 'FAIL' for row in results) or
                        ((shared_ports_configured or integration_configured) and errors) or
                        any('overlapping named allocations' in error or 'shared port' in error or
                            'shared transition port' in error or 'unowned overlap' in error or
                            'foreign footprint' in error for error in errors)) else 'INCOMPLETE'
    return {'schema': 2, 'kind': 'p1-coarse-reservation-screen', 'status': status,
            'hashes': hashes, 'errors': errors, 'allocations': results,
            'allocation_denominator': len(results), 'routing_realized': False,
            'p1_accepted': False,
            'reason': 'independent filled-reference, effective-capacity and P1 review not supplied'}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rectangle(value, name):
    if (not isinstance(value, (list, tuple)) or len(value) != 4 or
            any(isinstance(v, bool) or not isinstance(v, (int, float)) or
                not math.isfinite(v) for v in value)):
        raise ContractError(f'{name} must be four finite numbers')
    x0, y0, x1, y1 = map(float, value)
    if x0 >= x1 or y0 >= y1:
        raise ContractError(f'{name} has zero or negative extent')
    return x0, y0, x1, y1


def intersects(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def contains(outer, inner):
    return outer[0] <= inner[0] and outer[1] <= inner[1] and outer[2] >= inner[2] and outer[3] >= inner[3]


def touches_lane(pocket, lane):
    return ((abs(pocket[2] - lane[0]) < 1e-6 or abs(pocket[0] - lane[2]) < 1e-6)
            and max(pocket[1], lane[1]) < min(pocket[3], lane[3])) or (
            (abs(pocket[3] - lane[1]) < 1e-6 or abs(pocket[1] - lane[3]) < 1e-6)
            and max(pocket[0], lane[0]) < min(pocket[2], lane[2]))


def box_mm(box):
    return tuple(pcbnew.ToMM(v) for v in (box.GetLeft(), box.GetTop(), box.GetRight(), box.GetBottom()))


def lane_inside_outline(outline, lane):
    if outline.OutlineCount() != 1:
        return False
    lane_poly = pcbnew.SHAPE_POLY_SET()
    lane_poly.NewOutline()
    for x, y in ((lane[0], lane[1]), (lane[2], lane[1]),
                 (lane[2], lane[3]), (lane[0], lane[3])):
        lane_poly.Append(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    whole_area = lane_poly.Area()
    lane_poly.BooleanIntersection(outline)
    return abs(lane_poly.Area() - whole_area) <= max(1.0, whole_area * 1e-9)


def free_intervals(lo, hi, blocked):
    merged = []
    for a, b in sorted((max(lo, a), min(hi, b)) for a, b in blocked):
        if b <= a:
            continue
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    result, cursor = [], lo
    for a, b in merged:
        if a > cursor:
            result.append((cursor, a))
        cursor = max(cursor, b)
    if cursor < hi:
        result.append((cursor, hi))
    return result


def layer_obstacles(board, layer, endpoint_refs):
    """Return conservative occupied rectangles, retaining source identities."""
    obstacles = []
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in endpoint_refs:
            continue
        # Body bounds apply on the component side. Pads apply on any layer
        # they occupy, including every copper layer for through-hole pads.
        side = fp.GetLayerName()
        if side == 'F.Cu' and layer == 'F.Cu' or side == 'B.Cu' and layer == 'B.Cu':
            obstacles.append((ref + ':body', box_mm(fp.GetBoundingBox(False, False))))
        for pad in fp.Pads():
            if pad.IsOnLayer(board.GetLayerID(layer)):
                obstacles.append((ref + ':pad' + pad.GetNumber(), box_mm(pad.GetBoundingBox())))
    for item in board.GetTracks():
        if item.IsOnLayer(board.GetLayerID(layer)):
            obstacles.append(('existing-copper', box_mm(item.GetBoundingBox())))
    return obstacles


def connected_capacity(lane, obstacles, axis, pitch):
    """Max bottleneck width of a continuous path across rectangle-event strips."""
    along = (0, 2) if axis == 'horizontal' else (1, 3)
    across = (1, 3) if axis == 'horizontal' else (0, 2)
    start, end = lane[along[0]], lane[along[1]]
    lo, hi = lane[across[0]], lane[across[1]]
    relevant = [(name, box) for name, box in obstacles if intersects(lane, box)]
    cuts = {start, end}
    for _, box in relevant:
        cuts.update((max(start, box[along[0]]), min(end, box[along[1]])))
    cuts = sorted(cuts)
    prior = []
    bottleneck = 0.0
    sections = []
    for a, b in zip(cuts, cuts[1:]):
        mid = (a + b) / 2
        blocked = [(box[across[0]], box[across[1]]) for _, box in relevant
                   if box[along[0]] < mid < box[along[1]]]
        free = free_intervals(lo, hi, blocked)
        current = []
        for interval in free:
            width = interval[1] - interval[0]
            if not sections:
                reachable = width
            else:
                reachable = max((min(value, width, min(old[1], interval[1]) - max(old[0], interval[0]))
                                 for old, value in prior if min(old[1], interval[1]) > max(old[0], interval[0])),
                                default=0.0)
            current.append((interval, reachable))
        sections.append({'at_mm': round(mid, 6),
                         'max_free_width_mm': round(max((v-u for u, v in free), default=0.0), 6),
                         'reachable_width_mm': round(max((v for _, v in current), default=0.0), 6)})
        prior = current
    bottleneck = max((value for _, value in prior), default=0.0)
    slots = max(0, math.floor((bottleneck + 1e-9) / pitch))
    return {'connected_through_lane': bottleneck > 0,
            'connected_width_mm': round(bottleneck, 6),
            'capacity_slots': slots,
            'foreign_obstacles': sorted({name for name, _ in relevant}),
            'cross_sections': sections}


def measure_allocation(board, row, outline):
    if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id'].strip():
        raise ContractError('allocation requires a nonempty id')
    lane = rectangle(row.get('through_lane'), 'through_lane')
    axis = row.get('axis')
    if axis not in ('horizontal', 'vertical'):
        raise ContractError('axis must be horizontal or vertical')
    layers = row.get('layers')
    if not isinstance(layers, list) or not layers or len(layers) != len(set(layers)):
        raise ContractError('layers must be a nonempty unique list')
    valid_layers = {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq() if pcbnew.IsCopperLayer(i)}
    if any(layer not in valid_layers for layer in layers):
        raise ContractError('layer absent from enabled board copper layers')
    pitch, demand = row.get('slot_pitch_mm'), row.get('demand_slots')
    if (isinstance(pitch, bool) or not isinstance(pitch, (float, int)) or
            not math.isfinite(pitch) or pitch <= 0 or isinstance(demand, bool) or
            not isinstance(demand, int) or demand <= 0):
        raise ContractError('positive slot_pitch_mm and demand_slots required')
    members = row.get('coverage_members')
    pockets = row.get('endpoint_pockets')
    if not isinstance(members, list) or not members or len(members) != len(set(members)):
        raise ContractError('nonempty unique coverage_members required')
    if not isinstance(pockets, list) or not pockets:
        raise ContractError('endpoint_pockets denominator is zero')
    footprints = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in footprints:
            raise ContractError(f'duplicate board reference {ref}')
        footprints[ref] = fp
    endpoint_refs, endpoint_ids = set(), set()
    for pocket in pockets:
        if not isinstance(pocket, dict) or not isinstance(pocket.get('ref'), str) or not isinstance(pocket.get('pad'), str) or not isinstance(pocket.get('net'), str):
            raise ContractError('endpoint pocket requires ref, pad, and net')
        ref, pad_number, net = pocket['ref'], pocket['pad'], pocket['net']
        identity = ref + '.' + pad_number
        if not pad_number or not net or identity in endpoint_ids or ref not in footprints:
            raise ContractError(f'duplicate or missing endpoint identity {identity}')
        area = rectangle(pocket.get('pocket'), f'{ref} pocket')
        if not lane_inside_outline(outline, area):
            raise ContractError(f'{identity} endpoint pocket extends off board outline')
        if intersects(area, lane):
            raise ContractError(f'{ref} endpoint pocket intersects through lane')
        if not touches_lane(area, lane):
            raise ContractError(f'{ref} endpoint pocket does not contact through lane')
        pads = [p for p in footprints[ref].Pads() if p.GetNumber() == pad_number]
        if len(pads) != 1 or pads[0].GetNetname() != net:
            raise ContractError(f'{identity} pad/net identity mismatch or missing')
        if not all(pads[0].IsOnLayer(board.GetLayerID(layer)) for layer in layers):
            raise ContractError(f'{identity} pad is absent from a declared layer')
        if not contains(area, box_mm(pads[0].GetBoundingBox())):
            raise ContractError(f'{identity} pad outside pocket')
        if not contains(area, box_mm(footprints[ref].GetBoundingBox(False, False))):
            raise ContractError(f'{identity} endpoint footprint extends beyond pocket')
        endpoint_refs.add(ref)
        endpoint_ids.add(identity)
    if set(members) != endpoint_ids:
        raise ContractError('coverage_members must equal endpoint pad identities exactly')
    claimed_nets = row.get('coverage_nets')
    pocket_nets = {pocket['net'] for pocket in pockets}
    if not isinstance(claimed_nets, list) or set(claimed_nets) != pocket_nets:
        raise ContractError('coverage_nets must equal verified endpoint pad nets exactly')
    if any(sum(pocket['net'] == net for pocket in pockets) < 2 for net in claimed_nets):
        raise ContractError('each coverage net requires at least two verified endpoint pads')
    layer_rows = {}
    for layer in layers:
        item = connected_capacity(lane, layer_obstacles(board, layer, endpoint_refs), axis, pitch)
        item['status'] = 'FAIL' if item['capacity_slots'] < demand else 'INCOMPLETE'
        if item['status'] == 'INCOMPLETE':
            item['reason'] = 'effective per-net width/clearance, obstacle edge envelope, and pad-to-lane access are unverified'
            item['capacity_is_optimistic'] = True
        layer_rows[layer] = item
    return {'id': row['id'], 'status': 'FAIL' if any(v['status'] == 'FAIL' for v in layer_rows.values()) else 'INCOMPLETE',
            'demand_slots': demand, 'slot_pitch_mm': pitch, 'coverage_denominator': len(members),
            'endpoint_pockets': len(pockets), 'layers': layer_rows}


def evaluate(board_path: Path, contract_path: Path, expected_contract_sha256: str | None = None, *,
             source_path=None, interface_path=None, alias_path=None, floorplan_path=None,
             expected_source_sha256=None, expected_interface_sha256=None,
             expected_alias_sha256=None, expected_floorplan_sha256=None):
    try:
        candidate = json.loads(contract_path.read_text())
        if isinstance(candidate, dict) and candidate.get('schema') == 2:
            return evaluate_coarse(board_path, contract_path, expected_contract_sha256,
                                   source_path=source_path, interface_path=interface_path,
                                   alias_path=alias_path, floorplan_path=floorplan_path,
                                   expected_source_sha256=expected_source_sha256,
                                   expected_interface_sha256=expected_interface_sha256,
                                   expected_alias_sha256=expected_alias_sha256,
                                   expected_floorplan_sha256=expected_floorplan_sha256)
    except (OSError, ValueError):
        pass
    errors, rows = [], []
    try:
        board_hash = digest(board_path)
    except OSError as exc:
        board_hash = None
        errors.append(f'board unavailable: {exc}')
    try:
        contract_hash = digest(contract_path)
    except OSError as exc:
        contract_hash = None
        errors.append(f'contract unavailable: {exc}')
    try:
        if board_hash is None or contract_hash is None:
            raise ContractError('hash-bound inputs unavailable')
        contract = json.loads(contract_path.read_text())
        if not isinstance(contract, dict) or contract.get('schema') != 1:
            raise ContractError('contract schema must be 1')
        if contract.get('board_sha256') != board_hash:
            errors.append('board hash drift or missing board_sha256')
        if expected_contract_sha256 != contract_hash:
            errors.append('contract hash not bound to expected digest')
        allocations = contract.get('allocations')
        if not isinstance(allocations, list) or not allocations:
            raise ContractError('allocations denominator is zero')
        board = pcbnew.LoadBoard(str(board_path))
        if board is None:
            raise ContractError('board could not be loaded')
        outlines = pcbnew.SHAPE_POLY_SET()
        if not board.GetBoardPolygonOutlines(outlines, False) or outlines.OutlineCount() != 1:
            errors.append('missing or unsupported native board outline')
        zones = list(board.Zones())
        rule_areas = [zone for zone in zones if zone.GetIsRuleArea()]
        expected_rules = contract.get('required_rule_areas')
        actual_rules = [{'name': zone.GetZoneName(),
                         'bbox': [round(v, 6) for v in box_mm(zone.GetBoundingBox())],
                         'layers': sorted(board.GetLayerName(i) for i in zone.GetLayerSet().Seq())}
                        for zone in rule_areas]
        if (not isinstance(expected_rules, list) or
                sorted(json.dumps(item, sort_keys=True) for item in expected_rules) !=
                sorted(json.dumps(item, sort_keys=True) for item in actual_rules)):
            errors.append('native rule-area presence/name parity unverified')
        if contract.get('reference_plane_required') is not False or contract.get('profile') == 'crow-p1':
            errors.append('reference-plane/pour continuity not measured by this checker')
        native = board.GetDesignSettings()
        native_pitch = pcbnew.ToMM(native.m_TrackMinWidth + native.m_MinClearance)
        if native_pitch <= 0:
            errors.append('native routing pitch unavailable')
        expected_coverage = contract.get('expected_interface_coverage')
        if contract.get('profile') == 'crow-p1':
            expected_coverage = {name: sorted(nets) for name, nets in CROW_COVERAGE.items()}
        if not isinstance(expected_coverage, dict) or not expected_coverage:
            errors.append('expected interface coverage absent')
            expected_coverage = {}
        expected_ids = set(expected_coverage) - {'power_boundary_windows'}
        if set(row.get('id') for row in allocations if isinstance(row, dict)) != expected_ids:
            errors.append('allocation IDs differ from expected interface coverage')
        covered = []
        for row in allocations:
            if not isinstance(row, dict):
                continue
            nets = row.get('coverage_nets')
            if not isinstance(nets, list) or len(nets) != len(set(nets)) or set(nets) != set(expected_coverage.get(row.get('id'), [])):
                errors.append(f"{row.get('id')} interface coverage mismatch")
            else:
                covered.extend(nets)
        power = contract.get('power_boundary_nets', [])
        if 'power_boundary_windows' in expected_coverage:
            if not isinstance(power, list) or len(power) != len(set(power)) or set(power) != set(expected_coverage['power_boundary_windows']):
                errors.append('power boundary interface coverage mismatch')
            else:
                covered.extend(power)
        all_expected = [net for nets in expected_coverage.values() for net in nets]
        if len(covered) != len(set(covered)) or set(covered) != set(all_expected):
            errors.append('interface coverage is not exact-once')
        seen = set()
        for row in allocations:
            name = row.get('id') if isinstance(row, dict) else None
            try:
                if name in seen:
                    raise ContractError(f'duplicate allocation id {name}')
                seen.add(name)
                lane = rectangle(row.get('through_lane'), 'through_lane')
                if outlines.OutlineCount() == 1 and not lane_inside_outline(outlines, lane):
                    raise ContractError('through lane extends off board outline')
                if isinstance(row.get('slot_pitch_mm'), (int, float)) and row['slot_pitch_mm'] + 1e-9 < native_pitch:
                    raise ContractError(f"slot pitch understates native minimum {native_pitch:.3f} mm")
                for zone in zones:
                    if intersects(lane, box_mm(zone.GetBoundingBox())):
                        if zone.GetIsRuleArea():
                            raise ContractError('native rule-area overlaps through lane; restrictions unverified')
                        raise ContractError('copper pour intersects lane; reference continuity unverified')
                rows.append(measure_allocation(board, row, outlines))
            except (ContractError, TypeError, AttributeError) as exc:
                rows.append({'id': name, 'status': 'INCOMPLETE', 'reason': str(exc)})
        for index, left in enumerate(allocations):
            if not isinstance(left, dict):
                continue
            try:
                left_rect = rectangle(left.get('through_lane'), 'through_lane')
                left_layers = set(left.get('layers', []))
                for right in allocations[index + 1:]:
                    if isinstance(right, dict) and left_layers.intersection(right.get('layers', [])) and intersects(left_rect, rectangle(right.get('through_lane'), 'through_lane')):
                        errors.append(f"overlapping named lanes on same layer: {left.get('id')} / {right.get('id')}")
            except (ContractError, TypeError):
                pass
    except (ValueError, OSError, TypeError, RuntimeError) as exc:
        errors.append(str(exc))
    status = ('INCOMPLETE' if errors or not rows or any(r['status'] == 'INCOMPLETE' for r in rows)
              else 'FAIL' if any(r['status'] == 'FAIL' for r in rows) else 'PASS')
    return {'schema': 1, 'kind': 'p1-named-corridor-capacity', 'status': status,
            'routing_realized': False, 'p1_accepted': False,
            'board_sha256': board_hash, 'contract_sha256': contract_hash,
            'allocation_denominator': len(rows), 'errors': errors, 'allocations': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('board', type=Path)
    parser.add_argument('contract', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--expected-contract-sha256', required=True)
    parser.add_argument('--source-requirements', type=Path)
    parser.add_argument('--interfaces', type=Path)
    parser.add_argument('--aliases', type=Path)
    parser.add_argument('--floorplan', type=Path)
    parser.add_argument('--expected-source-sha256')
    parser.add_argument('--expected-interface-sha256')
    parser.add_argument('--expected-alias-sha256')
    parser.add_argument('--expected-floorplan-sha256')
    args = parser.parse_args()
    result = evaluate(args.board, args.contract, args.expected_contract_sha256,
                      source_path=args.source_requirements, interface_path=args.interfaces,
                      alias_path=args.aliases, floorplan_path=args.floorplan,
                      expected_source_sha256=args.expected_source_sha256,
                      expected_interface_sha256=args.expected_interface_sha256,
                      expected_alias_sha256=args.expected_alias_sha256,
                      expected_floorplan_sha256=args.expected_floorplan_sha256)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
