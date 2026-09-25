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
Optional ``physical_cells`` partition one modular owner into disjoint named
floorplan regions. Corridor faces and witnesses name a physical cell while
their exact endpoint ``block`` remains the modular owner. Each row has ``id``
(a floorplan region key), ``owner_block``, exact ``refs`` and ``transit``;
transit cells have no refs and must edge-connect to occupied same-owner cells.
Owners using this extension must assign all modular refs exactly once, include
their primary region when present, and name cells explicitly on witnesses,
corridor faces and P2 obligations. No source alias or P1 credit is implied.
On the exact reviewed Crow board, ``physical_cell_edge_attachments`` can admit
only the nominal 0.045-mm north F.CrtYd projection of fixed J_PWR/J1--J8 in
a one-ref physical cell. Material, pads, drills and all other geometry stay
inboard. This affects physical-cell containment only, never route or P1 credit.
A ``fixed_connector_access`` witness keeps a P1-fixed pad physical and binds a
separate, disjoint access reservation to a named integration corridor. It is
only a topology/geometry declaration and carries no routing capacity credit.
``fixed_connector_access_segmented`` uses ordered, edge-joined rectangles in
``segments`` instead of one access rectangle. The ``bbox`` is their exact
envelope; native obstacles are checked against every segment. It remains
INCOMPLETE and grants no capacity or P1 credit.
An ``unresolved_multiterminal_branch`` binds every exact native endpoint of
one cross-owner net and its return/tree obligations, while recording pad-level
source-region conflicts. Its reservation deliberately has no geometry or
capacity and remains INCOMPLETE.
An opt-in ``unresolved_two_terminal_crossings`` record uses the same exact
no-credit checks for precisely two native terminals on distinct owners. Its
matching witness/reservation kind is ``unresolved_two_terminal_crossing``.
Schema-2 ``--diagnose-all`` adds one independent validation error per boundary
witness or reservation to a ``diagnostics`` array. It does not replace the
normal fail-closed verdict or prove cross-item endpoint/overlap accounting.
An opt-in ``linked_paths`` slice accounts for one same-net series path with
exactly three modular owners and two ordered stages. The first is a native-
checked physical corridor; the second is either another independently checked
physical corridor or a geometry-free unresolved virtual span. Exact
intermediate pads join them. Each physical stage reports separate rough
capacity, never a sum; P2 access/return and P1 remain INCOMPLETE. Paths with
branches or additional stages fail closed until separately implemented.
Opt-in ``access_only_portals`` screen a body/copper-free local boundary where
a planning region overlaps a true endpoint owner's transit space. Electrical
owners, transit owner and non-electrical planning overlaps are distinct. Every
native net terminal and P2/filled-return obligation is exact; this record
creates no reservation, capacity slot, routing claim or P1 acceptance.
Opt-in ``branch_owner_pockets`` bind sparse, complete native footprint envelopes
to exact unresolved-branch endpoints. They are not physical cells or route
reservations and retain every terminal, P2 access, P3 tree and return debt.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
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
                    regions, fixed_refs, shared_ports, integration_corridors=None,
                    unresolved_branches=None, physical_cells=None, owner_pockets=None):
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
    cell_id = witness.get('physical_cell_id')
    cells = physical_cells or {}
    if cell_id is not None:
        if cell_id not in cells or cells[cell_id]['owner_block'] != block:
            raise ContractError(f'{source}: physical cell owner mismatch')
    elif any(c['owner_block'] == block for c in cells.values()):
        raise ContractError(f'{source}: physical cell identity missing')
    pocket_id = witness.get('branch_owner_pocket_id')
    if pocket_id is not None and cell_id is not None:
        raise ContractError(f'{source}: branch owner pocket cannot be a physical cell')
    region_id = cell_id or block
    region = rectangle(regions.get(region_id), f'{region_id} source region')
    region_span = min(region[2] - region[0], region[3] - region[1])
    kind = witness.get('kind', 'native_pad_face')
    if pocket_id is not None and kind not in UNRESOLVED_KINDS:
        raise ContractError(f'{source}: branch owner pocket cannot serve another witness')
    if kind != 'shared_transition_port' and not (kind == 'integration_corridor_handoff' and cell_id is not None) and (area[2] - area[0] > region_span / 4 + 1e-6 or area[3] - area[1] > region_span / 4 + 1e-6):
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
        if witness.get('region_id') != region_id:
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
        if cell_id is not None:
            expected_obligation['physical_cell_id'] = cell_id
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
        if (selected is None or witness.get('physical_cell_id') != selected.get('physical_cell_id') or
                witness.get('region_face') != selected['region_face'] or area != selected['bbox']):
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
        if cell_id is not None:
            expected['physical_cell_id'] = cell_id
        if obligation != expected:
            raise ContractError(f'{source}: integration P2 pad-to-face obligation missing')
        if not any(p.IsOnLayer(board.GetLayerID(layer)) for p in found):
            raise ContractError(f'{source}: native source pad not on integration layer')
    elif kind in UNRESOLVED_KINDS:
        if kind == 'unresolved_two_terminal_crossing' and set(witness) not in (
                {'kind', 'branch_id', 'source', 'native', 'net', 'block', 'layer',
                 'face', 'boundary_bbox', 'reservation_id', 'p2_obligation'},
                {'kind', 'branch_id', 'source', 'native', 'net', 'block', 'layer',
                 'face', 'boundary_bbox', 'reservation_id', 'p2_obligation',
                 'physical_cell_id'}):
            raise ContractError(f'{source}: two-terminal witness fields invalid')
        branch = (unresolved_branches or {}).get(witness.get('branch_id'))
        if (branch is None or branch['_kind'] != kind or
                branch['net'] != net or branch['layer'] != layer):
            raise ContractError(f'{source}: unresolved branch identity mismatch')
        if any('branch_owner_pocket_id' in e for e in branch['endpoints']) and set(witness) != {
                'kind', 'branch_id', 'source', 'native', 'net', 'block', 'layer',
                'face', 'boundary_bbox', 'reservation_id', 'p2_obligation',
                *({'branch_owner_pocket_id'} if pocket_id is not None else set())}:
            raise ContractError(f'{source}: pocketed branch witness fields invalid')
        endpoint = {'source_pad':source,'native_pad':native,'net':net,'block':block}
        matched = [e for e in branch['endpoints'] if all(e.get(k) == v for k,v in endpoint.items())]
        if len(matched) != 1:
            raise ContractError(f'{source}: unresolved branch endpoint mismatch')
        selected_pocket = matched[0].get('branch_owner_pocket_id')
        if pocket_id != selected_pocket:
            raise ContractError(f'{source}: unresolved branch owner pocket witness mismatch')
        if pocket_id is not None:
            pocket = (owner_pockets or {}).get(pocket_id)
            if (pocket is None or pocket['owner_block'] != block or
                    native.rsplit('.', 1)[0] not in pocket['refs'] or
                    branch['id'] not in pocket['branch_ids']):
                raise ContractError(f'{source}: unresolved branch owner pocket invalid')
            region = pocket['bbox']
        if not all(p.IsOnLayer(board.GetLayerID(layer)) and
                   area == box_mm(p.GetBoundingBox()) for p in found):
            raise ContractError(f'{source}: unresolved branch boundary is not native pad')
        if not contains(region, area):
            raise ContractError(f'{source}: unresolved branch pad leaves owner region')
        if witness.get('reservation_id') != branch['reservation_id']:
            raise ContractError(f'{source}: unresolved branch reservation mismatch')
        obligation = witness.get('p2_obligation')
        if obligation != next(o for o in branch['p2_obligations']
                              if o['source_pad'] == source):
            raise ContractError(f'{source}: unresolved branch P2 obligation mismatch')
    elif kind in ('fixed_connector_access', 'fixed_connector_access_segmented'):
        corridor = (integration_corridors or {}).get(witness.get('corridor_id'))
        if corridor is None:
            raise ContractError(f'{source}: undeclared fixed access corridor')
        if ref not in fixed_refs:
            raise ContractError(f'{source}: fixed access requires P1-fixed ref')
        if layer != corridor['layer']:
            raise ContractError(f'{source}: fixed access layer mismatch')
        endpoint = {'source_pad': source, 'native_pad': native, 'net': net, 'block': block}
        if endpoint not in corridor['affected']:
            raise ContractError(f'{source}: fixed access endpoint not corridor declared')
        # This is an access declaration from a physical pad, so a generous
        # witness rectangle cannot stand in for the pad boundary.  Otherwise a
        # segment could start at an invented face some distance from the pad.
        if not all(p.IsOnLayer(board.GetLayerID(layer)) and
                   area == box_mm(p.GetBoundingBox()) for p in found):
            raise ContractError(f'{source}: fixed access boundary is not the physical pad')
        if not contains(region, area):
            raise ContractError(f'{source}: fixed access pad boundary leaves source region')
        obligation = witness.get('p2_obligation')
        selected = next(f for f in corridor['faces'] if f['block'] == block)
        expected = {'status': 'P2_REQUIRED', **endpoint,
                    'corridor_id': corridor['id'], 'region_face': selected['region_face'],
                    'layer': layer, 'to_reservation': corridor['reservation_id']}
        if cell_id is not None:
            expected['physical_cell_id'] = cell_id
        if obligation != expected:
            raise ContractError(f'{source}: fixed access P2 pad-to-corridor obligation missing')
    else:
        raise ContractError(f'{source}: unknown boundary witness kind')
    return {'source': source, 'native': native, 'net': net, 'block': block,
            'physical_cell_id': cell_id,
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


def _positive_edge_contact(a, b):
    """Require a positive-length shared edge, without area overlap."""
    tol = 1e-6
    return not intersects(a, b) and (
        ((abs(a[2] - b[0]) <= tol or abs(a[0] - b[2]) <= tol) and
         min(a[3], b[3]) - max(a[1], b[1]) > tol) or
        ((abs(a[3] - b[1]) <= tol or abs(a[1] - b[3]) <= tol) and
         min(a[2], b[2]) - max(a[0], b[0]) > tol))


def _fixed_access_shapes(target, witness, corridor, source_region):
    """Return a checked access chain; legacy rectangle semantics stay intact."""
    envelope = rectangle(target.get('bbox'), 'fixed connector access')
    if target.get('kind') == 'fixed_connector_access':
        return [envelope]
    raw = target.get('segments')
    if not isinstance(raw, list) or len(raw) < 2:
        raise ContractError('segmented fixed access needs at least two segments')
    shapes = [rectangle(value, 'fixed access segment') for value in raw]
    actual = (min(s[0] for s in shapes), min(s[1] for s in shapes),
              max(s[2] for s in shapes), max(s[3] for s in shapes))
    if envelope != actual:
        raise ContractError('segmented fixed access bbox differs from segment envelope')
    if any(not contains(source_region, shape) for shape in shapes):
        raise ContractError('segmented fixed access leaves source region')
    if not _witness_touches_reservation(witness, {'bbox': shapes[0]}):
        raise ContractError('segmented fixed access does not leave physical pad boundary')
    for index, shape in enumerate(shapes):
        if index and not _positive_edge_contact(shapes[index - 1], shape):
            raise ContractError('segmented fixed access has disconnected or overlapping waypoints')
        if index > 1 and any(intersects(shape, prior) for prior in shapes[:index - 1]):
            raise ContractError('segmented fixed access self-overlaps')
    if not _positive_edge_contact(shapes[-1], corridor):
        raise ContractError('segmented fixed access does not contact integration corridor')
    return shapes


def _is_geometry_free_branch_reservation(reservation, branches):
    """Only a declared, geometry-free branch may bypass fixed-access overlap."""
    if reservation.get('kind') not in UNRESOLVED_KINDS:
        return False
    matches = [branch for branch in branches.values()
               if branch['reservation_id'] == reservation.get('id')]
    if (len(matches) != 1 or
            reservation.get('kind') != matches[0].get('_kind', 'unresolved_multiterminal_branch') or
            reservation.get('branch_id') != matches[0]['id'] or
            reservation.get('nets') != [matches[0]['net']] or
            reservation.get('layer') != matches[0]['layer'] or
            any(key in reservation for key in
                ('bbox', 'segments', 'capacity_slots', 'demand_slots', 'slot_pitch_mm'))):
        raise ContractError('unresolved branch cannot reserve geometry/capacity')
    return True


def _filled_zone_intersects(zone, layer_id, shape):
    """Check saved copper polygons, never a refillable zone outline."""
    if not zone.IsOnLayer(layer_id):
        return False
    try:
        filled = zone.GetFilledPolysList(layer_id)
        if filled.OutlineCount() == 0:
            return False
        access = pcbnew.SHAPE_POLY_SET()
        access.NewOutline()
        for x, y in ((shape[0], shape[1]), (shape[2], shape[1]),
                     (shape[2], shape[3]), (shape[0], shape[3])):
            access.Append(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        filled = filled.CloneDropTriangulation()
        filled.BooleanIntersection(access)
        return filled.OutlineCount() > 0 and filled.Area() > 0
    except (AttributeError, RuntimeError, TypeError) as exc:
        raise ContractError(f'saved zone fill geometry unreadable: {exc}') from exc


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
        if region_id != witness.get('physical_cell_id', witness['block']) and intersects(boundary, region):
            raise ContractError(f"{witness['source']}: virtual boundary enters {region_id} source region")
        if intersects(reserved, region):
            raise ContractError(f"{witness['source']}: virtual reservation enters {region_id} source region")


UNRESOLVED_KINDS = frozenset({'unresolved_multiterminal_branch',
                              'unresolved_two_terminal_crossing'})


def _branch_owner_pockets(source, interfaces, board, outline, regions, hashes,
                          patterns=None):
    """Validate sparse branch locations without assigning a whole owner cell."""
    rows = source.get('branch_owner_pockets')
    if rows is None:
        return {}
    if not isinstance(rows, list) or not rows or not isinstance(interfaces.get('blocks'), list):
        raise ContractError('branch owner pockets require modular block ownership')
    blocks = {b['id']: set(b['refs']) for b in interfaces['blocks']}
    native = {fp.GetReference(): fp for fp in board.GetFootprints()}
    patterns = patterns or []
    pockets, assigned = {}, set()
    keys = {'id', 'owner_block', 'refs', 'bbox', 'branch_ids',
            'board_sha256', 'floorplan_sha256', 'alias_sha256'}
    for row in rows:
        if not isinstance(row, dict) or set(row) != keys:
            raise ContractError('branch owner pocket fields invalid')
        ident, owner, refs, branch_ids = (row['id'], row['owner_block'],
                                          row['refs'], row['branch_ids'])
        if (not isinstance(ident, str) or not ident or ident in pockets or
                not isinstance(owner, str) or owner not in blocks or
                not isinstance(refs, list) or not refs or
                any(not isinstance(ref, str) for ref in refs) or
                len(refs) != len(set(refs)) or
                not isinstance(branch_ids, list) or not branch_ids or
                any(not isinstance(branch, str) or not branch for branch in branch_ids) or
                len(branch_ids) != len(set(branch_ids)) or
                not set(refs) <= blocks[owner] or
                any(ref not in native or ref in assigned for ref in refs)):
            raise ContractError(f'{ident}: branch owner pocket owner/ref/branch invalid')
        if any(row[key + '_sha256'] != hashes[key] for key in ('board', 'floorplan', 'alias')):
            raise ContractError(f'{ident}: branch owner pocket hash drift')
        area = rectangle(row['bbox'], f'{ident} branch owner pocket')
        if not lane_inside_outline(outline, area):
            raise ContractError(f'{ident}: branch owner pocket off board outline')
        for ref in refs:
            fp = native[ref]
            if any(pattern.get('region') not in (None, owner, ident)
                   for pattern in patterns if ref in pattern['match']):
                raise ContractError(f'{ident}: source pattern disagrees with owner pocket {ref}')
            if not contains(area, _physical_envelope(fp)) or any(
                    not contains(area, box_mm(p.GetBoundingBox())) for p in fp.Pads()):
                raise ContractError(f'{ident}: native body/pad {ref} clipped by owner pocket')
        for ref, fp in native.items():
            if ref not in refs and (intersects(area, _physical_envelope(fp)) or any(
                    intersects(area, box_mm(p.GetBoundingBox())) for p in fp.Pads())):
                raise ContractError(f'{ident}: foreign native body/pad {ref} enters owner pocket')
        for region_id, value in regions.items():
            if region_id != owner and intersects(area, rectangle(value, f'{region_id} source region')):
                raise ContractError(f'{ident}: foreign source region {region_id} enters owner pocket')
        if any(intersects(area, pocket['bbox']) for pocket in pockets.values()):
            raise ContractError(f'{ident}: branch owner pockets overlap')
        assigned.update(refs)
        pockets[ident] = {'id': ident, 'owner_block': owner, 'refs': set(refs),
                          'branch_ids': set(branch_ids), 'bbox': area}
    return pockets


def _unresolved_branches(source, interfaces, board, regions, coverage, aliases, pads,
                         physical_cells=None, patterns=None, owner_pockets=None):
    """Validate exact multi-terminal ownership without claiming route geometry.

    An unresolved branch has no bbox, slots, or copper credit.  Its blocker
    inventory names every native pad that intersects a foreign source region.
    This is an admission debt record, not a physical corridor exception.
    """
    groups = (('unresolved_multiterminal_branch',
               source.get('unresolved_multiterminal_branches', [])),
              ('unresolved_two_terminal_crossing',
               source.get('unresolved_two_terminal_crossings', [])))
    if any(not isinstance(rows, list) for _, rows in groups):
        raise ContractError('unresolved branch list invalid')
    declared = {}
    cells = physical_cells or {}
    pockets = owner_pockets or {}
    used_pockets = defaultdict(set)
    patterns = patterns or []
    native_refs = {fp.GetReference(): fp for fp in board.GetFootprints()}
    iface_by_net = {item['net']: item for item in interfaces['interfaces']}
    for kind, row in ((kind, row) for kind, rows in groups for row in rows):
        if not isinstance(row, dict):
            raise ContractError('unresolved branch record invalid')
        pocketed = any(isinstance(e, dict) and 'branch_owner_pocket_id' in e
                       for e in row.get('endpoints', []) if isinstance(row.get('endpoints'), list))
        if pocketed and (kind != 'unresolved_multiterminal_branch' or
                set(row) != {'id', 'owner', 'allocation_id', 'net', 'layer',
                             'reference_layer', 'reservation_id', 'endpoints',
                             'terminal_count', 'minimum_tree_edges',
                             'physical_blockers', 'capacity_slots', 'p2_obligations',
                             'tree_obligation', 'return_obligation'}):
            raise ContractError('pocketed branch source fields invalid')
        if kind == 'unresolved_two_terminal_crossing' and set(row) != {
                'id', 'owner', 'allocation_id', 'net', 'layer', 'reference_layer',
                'reservation_id', 'endpoints', 'terminal_count', 'minimum_tree_edges',
                'physical_blockers', 'capacity_slots', 'p2_obligations',
                'tree_obligation', 'return_obligation'}:
            raise ContractError('two-terminal crossing source fields invalid')
        ident = row.get('id')
        net = row.get('net')
        allocation = row.get('allocation_id')
        layer = row.get('layer')
        reference_layer = row.get('reference_layer')
        copper_layers = {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq()
                         if pcbnew.IsCopperLayer(i)}
        if (not isinstance(ident, str) or not ident or ident in declared or
                row.get('owner') != 'board_integration' or
                net not in iface_by_net or net not in coverage.get(allocation, set()) or
                not isinstance(layer, str) or layer not in copper_layers or
                not isinstance(reference_layer, str) or reference_layer not in copper_layers or
                reference_layer == layer):
            raise ContractError('unresolved branch identity/owner/net/layer invalid')
        expected_rows = [(source_pad, graph.native_identity(source_pad, aliases), net, block)
                         for block, names in iface_by_net[net]['endpoints'].items()
                         for source_pad in names]
        if (len(expected_rows) != len({item[0] for item in expected_rows}) or
                len(expected_rows) != len({item[1] for item in expected_rows})):
            raise ContractError(f'{ident}: branch source/native terminal alias collision')
        expected = set(expected_rows)
        if len({block for _,_,_,block in expected}) < 2:
            raise ContractError(f'{ident}: branch must cross source owners')
        entries = row.get('endpoints')
        if (not isinstance(entries, list) or
                (len(expected) != 2 if kind == 'unresolved_two_terminal_crossing'
                 else len(expected) < 3) or
                len(entries) != len(expected) or
                {(e.get('source_pad'), e.get('native_pad'), e.get('net'), e.get('block'))
                 for e in entries if isinstance(e, dict)} != expected):
            raise ContractError(f'{ident}: exact branch endpoint denominator mismatch')
        entry_by_source = {}
        for entry in entries:
            if not isinstance(entry, dict):
                raise ContractError(f'{ident}: branch endpoint record invalid')
            cell_id = entry.get('physical_cell_id')
            pocket_id = entry.get('branch_owner_pocket_id')
            allowed = {'source_pad', 'native_pad', 'net', 'block'}
            if cell_id is not None:
                allowed.add('physical_cell_id')
            if pocket_id is not None:
                allowed.add('branch_owner_pocket_id')
            if cell_id is not None and pocket_id is not None:
                raise ContractError(f'{ident}: branch cannot use physical cell and owner pocket')
            if set(entry) != allowed or entry['source_pad'] in entry_by_source:
                raise ContractError(f'{ident}: branch endpoint physical cell declaration invalid')
            entry_by_source[entry['source_pad']] = entry
        # Declaring each expected terminal is not enough: the native net must
        # not carry a sixth, undeclared terminal that turns the stated tree
        # into a different electrical obligation.  Keep the physical count as
        # well as the identities, since a malformed footprint can repeat a
        # pad number.
        expected_native = {native_pad for _, native_pad, _, _ in expected}
        actual_native = [fp.GetReference() + '.' + pad.GetNumber()
                         for fp in board.GetFootprints() for pad in fp.Pads()
                         if pad.GetNetname() == net]
        if (len(actual_native) != len(expected_native) or
                set(actual_native) != expected_native):
            raise ContractError(f'{ident}: exact native branch terminal set mismatch')
        if row.get('terminal_count') != len(expected) or row.get('minimum_tree_edges') != len(expected)-1:
            raise ContractError(f'{ident}: branch tree lower bound mismatch')
        if (row.get('tree_obligation') != {'status':'P3_REQUIRED', 'net':net,
                'terminal_count':len(expected),'minimum_tree_edges':len(expected)-1,
                'proof':'one_connected_native_net_without_unrelated_branches'} or
                row.get('return_obligation') != {'status':'P2_REQUIRED', 'net':'GND',
                'branch_id':ident,'reference_layer':row.get('reference_layer'),
                'proof':'continuous_filled_reference_under_actual_tree'}):
            raise ContractError(f'{ident}: P2 return/P3 tree obligation missing')
        reservation_id = row.get('reservation_id')
        if not isinstance(reservation_id, str) or not reservation_id:
            raise ContractError(f'{ident}: unresolved branch reservation id missing')
        required = [{'status':'P2_REQUIRED','source_pad':s,'native_pad':n,
                     'net':net,'block':block,'branch_id':ident,'layer':layer,
                     'proof':'native_pad_to_unplaced_tree',
                     **({'branch_owner_pocket_id':entry_by_source[s]['branch_owner_pocket_id']}
                        if 'branch_owner_pocket_id' in entry_by_source[s] else {})}
                    for s,n,_,block in sorted(expected)]
        if row.get('p2_obligations') != required:
            raise ContractError(f'{ident}: exact P2 pad-to-tree obligations missing')
        blockers = []
        for source_pad,native_pad,_,block in sorted(expected):
            found = pads.get(native_pad, [])
            if (not found or any(p.GetNetname()!=net or
                    not p.IsOnLayer(board.GetLayerID(layer)) for p in found)):
                raise ContractError(f'{native_pad}: unresolved branch native pad/layer mismatch')
            entry = entry_by_source[source_pad]
            cell_id = entry.get('physical_cell_id')
            pocket_id = entry.get('branch_owner_pocket_id')
            ref = native_pad.rsplit('.', 1)[0]
            if pocket_id is not None:
                pocket = pockets.get(pocket_id)
                if (pocket is None or pocket['owner_block'] != block or
                        ref not in pocket['refs'] or ident not in pocket['branch_ids']):
                    raise ContractError(f'{native_pad}: branch owner pocket owner/ref/branch mismatch')
                owner_region = pocket['bbox']
                used_pockets[pocket_id].add((ident, ref))
            elif cell_id is not None:
                cell = cells.get(cell_id)
                if (not isinstance(cell_id, str) or not cell or
                        cell['owner_block'] != block or ref not in cell['refs'] or
                        cell_id not in regions or
                        tuple(cell['bbox']) != rectangle(regions[cell_id],
                                                         f'{cell_id} branch physical cell')):
                    raise ContractError(f'{native_pad}: branch physical cell owner/ref/region mismatch')
                owner_region = rectangle(regions[cell_id], f'{cell_id} branch physical cell')
                fp = native_refs.get(ref)
                if (fp is None or not contains(owner_region, _physical_envelope(fp)) or
                        any(not contains(owner_region, box_mm(p.GetBoundingBox()))
                            for p in fp.Pads()) or
                        any(pattern.get('region') not in (None, cell_id)
                            for pattern in patterns if ref in pattern['match'])):
                    raise ContractError(f'{native_pad}: branch physical cell body/pad/pattern mismatch')
            else:
                owner_region = rectangle(regions.get(block), f'{block} branch owner region')
            for pad in found:
                native_box = box_mm(pad.GetBoundingBox())
                if not contains(owner_region, native_box):
                    raise ContractError(f'{native_pad}: branch pad outside source owner region')
                foreign = sorted(name for name,value in regions.items()
                                 if name != block and name != cell_id and
                                 not (name in cells and cells[name]['owner_block'] == block) and
                                 intersects(native_box,
                                     rectangle(value, f'{name} foreign source region')))
                if foreign:
                    blockers.append({'source_pad':source_pad,'native_pad':native_pad,
                                     'block':block,'foreign_regions':foreign})
        if row.get('physical_blockers') != blockers:
            raise ContractError(f'{ident}: physical source-region blocker inventory mismatch')
        if row.get('capacity_slots') is not None or 'bbox' in row:
            raise ContractError(f'{ident}: unresolved branch cannot claim geometry/capacity')
        declared[ident] = {**row, '_kind': kind}
    for pocket_id, pocket in pockets.items():
        if used_pockets[pocket_id] != {(branch, ref) for branch in pocket['branch_ids']
                                       for ref in pocket['refs']}:
            raise ContractError(f'{pocket_id}: branch owner pocket endpoint use incomplete')
    return declared


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
    # A local signal port may name only the pads entering that port.  A power
    # window represents the whole net's boundary/current obligation, so a
    # selected pad must not stand in for its other native terminals.
    power_nets = set(source.get('power_boundary_windows', {}).get('coverage_nets', []))
    for allocation in source.get('allocations', []):
        for demand in allocation.get('demands', []):
            if demand.get('id') == 'usb_local_power':
                power_nets.update(net for net in demand.get('nets', []) if net == 'VBUS_USB')
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
        for net in {e['net'] for e in affected} & power_nets:
            item = next((item for item in interfaces['interfaces'] if item.get('net') == net), None)
            if item is None or not isinstance(item.get('endpoints'), dict):
                raise ContractError(f'{ident}: power port modular denominator missing')
            expected = {(source_pad, graph.native_identity(source_pad, aliases), net, block)
                        for block, names in item['endpoints'].items() for source_pad in names}
            declared = {(e['source_pad'], e['native_pad'], e['net'], e['block'])
                        for e in affected if e['net'] == net}
            if len(declared) != len(expected) or declared != expected:
                raise ContractError(f'{ident}: power port exact endpoint denominator missing for {net}')
            _linked_native_pad_census(ident, expected, pads, {net})
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
            body = _physical_envelope(fp)
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
                           coverage, aliases, pads, shared_ports, physical_cells=None):
    """Validate a disjoint source cell; declarations are P2 debt, never proof."""
    rows = source.get('integration_corridors', [])
    if not isinstance(rows, list):
        raise ContractError('integration corridors malformed')
    blocks = interfaces.get('blocks')
    if rows and not isinstance(blocks, list):
        raise ContractError('integration corridors require modular block ownership')
    cells = physical_cells or {}
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
            cell_id = face.get('physical_cell_id')
            if cell_id is not None:
                if cell_id not in cells or cells[cell_id]['owner_block'] != block:
                    raise ContractError(f'{ident}: integration physical cell owner mismatch')
            elif any(c['owner_block'] == block for c in cells.values()):
                raise ContractError(f'{ident}: integration physical cell identity missing')
            region_id_for_face = cell_id or block
            owner = rectangle(regions[region_id_for_face], f'{region_id_for_face} region')
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
                if foreign_id != region_id_for_face and intersects(boundary, rectangle(foreign, f'{foreign_id} region')):
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
        expected_p2 = []
        for e in affected:
            selected = face_by_block[e['block']]
            obligation = {'status': 'P2_REQUIRED', **e, 'corridor_id': ident,
                          'region_face': selected['region_face'],
                          'layer': layer, 'to_reservation': reservation_id}
            if selected.get('physical_cell_id') is not None:
                obligation['physical_cell_id'] = selected['physical_cell_id']
            expected_p2.append(obligation)
        if row.get('p2_obligations') != expected_p2:
            raise ContractError(f'{ident}: integration P2 pad-to-face obligations incomplete')
        reference = row.get('reference_layer')
        if reference not in enabled or reference == layer or row.get('return_obligation') != {
                'status': 'P2_REQUIRED', 'net': 'GND', 'corridor_id': ident,
                'reference_layer': reference, 'proof': 'continuous_filled_reference'}:
            raise ContractError(f'{ident}: integration P2 filled-reference return obligation missing')
        for fp in board.GetFootprints():
            shapes = [_physical_envelope(fp)] + [box_mm(p.GetBoundingBox()) for p in fp.Pads()]
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


def _linked_native_pad_census(ident, expected, pads, nets):
    """Bind every linked-net source terminal to exactly one native pad instance.

    Manufacturer-fused contacts with distinct native pad IDs remain distinct
    terminals. Mapping two source IDs to one native ID has no same-land proof
    in this first-slice schema and therefore fails closed.
    """
    by_native = {}
    for source_pad, native_pad, net, _ in expected:
        prior = by_native.setdefault(native_pad, source_pad)
        if prior != source_pad:
            raise ContractError(f'{ident}: linked native alias collision {prior}/{source_pad}')
    wanted = Counter((net, native_pad) for _, native_pad, net, _ in expected)
    actual = Counter((pad.GetNetname(), native_pad)
                     for native_pad, instances in pads.items()
                     for pad in instances if pad.GetNetname() in nets)
    if actual != wanted:
        missing = sorted((wanted - actual).elements())
        extra = sorted((actual - wanted).elements())
        raise ContractError(f'{ident}: linked native net pad multiset mismatch '
                            f'(missing={missing}, extra={extra})')


def _access_only_portals(source, interfaces, board, outline, regions, zones,
                         coverage, aliases, pads, contract_allocations=None,
                         physical_cells=None):
    """Screen local access geometry without creating a reservation or P1 credit."""
    if 'access_only_portals' not in source:
        return []
    rows = source['access_only_portals']
    if not isinstance(rows, list) or not rows or not isinstance(interfaces.get('blocks'), list):
        raise ContractError('access-only portals malformed')
    owners = {ref: block['id'] for block in interfaces['blocks'] for ref in block.get('refs', [])}
    if len(owners) != sum(len(block.get('refs', [])) for block in interfaces['blocks']):
        raise ContractError('access-only portal duplicate modular footprint owner')
    by_net = {item['net']: item for item in interfaces['interfaces']}
    enabled = {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq()
               if pcbnew.IsCopperLayer(i)}
    required = {'id', 'allocation_id', 'nets', 'electrical_owners', 'transit_owner',
                'planning_overlaps', 'portal_bbox', 'owner_face', 'layer',
                'reference_layer', 'affected', 'p2_obligations',
                'return_obligation', 'status', 'capacity_slots'}
    used_ids, used_nets, screened = set(), set(), []
    for row in rows:
        if not isinstance(row, dict) or set(row) != required:
            raise ContractError('access-only portal schema/outcome fields invalid')
        ident, allocation, nets = row['id'], row['allocation_id'], row['nets']
        transit, overlaps = row['transit_owner'], row['planning_overlaps']
        if (not isinstance(ident, str) or not ident or ident in used_ids or
                allocation not in coverage or not isinstance(nets, list) or not nets or
                len(nets) != len(set(nets)) or not set(nets) <= coverage[allocation] or
                used_nets & set(nets) or not isinstance(transit, str) or transit not in regions or
                not isinstance(overlaps, list) or not overlaps or
                len(overlaps) != len(set(overlaps)) or
                any(not isinstance(name, str) or name not in regions or name == transit
                    for name in overlaps) or
                row['status'] != 'INCOMPLETE' or row['capacity_slots'] is not None):
            raise ContractError(f'{ident}: access-only portal identity/net/role invalid')
        used_ids.add(ident)
        used_nets.update(nets)
        source_alloc = next((a for a in source['allocations'] if a.get('id') == allocation), None)
        if source_alloc is None:
            raise ContractError(f'{ident}: access-only portal source allocation missing')
        expected = set()
        electrical = set()
        for net in nets:
            item = by_net.get(net)
            if item is None or not isinstance(item.get('endpoints'), dict):
                raise ContractError(f'{ident}: access-only portal modular net missing')
            source_owners = source_alloc.get('endpoints', {}).get(net)
            if not isinstance(source_owners, dict):
                raise ContractError(f'{ident}: access-only portal source/modular owner denominator mismatch')
            if any(not isinstance(refs, list) or len(refs) != len(set(refs))
                   for owner_rows in (item['endpoints'], source_owners)
                   for refs in owner_rows.values()):
                raise ContractError(f'{ident}: access-only portal duplicate source terminal')
            if any(len([pad for refs in owner_rows.values() for pad in refs]) !=
                   len({pad for refs in owner_rows.values() for pad in refs})
                   for owner_rows in (item['endpoints'], source_owners)):
                raise ContractError(f'{ident}: access-only portal duplicate source terminal')
            if ({owner: set(refs) for owner, refs in source_owners.items()} !=
                    {owner: set(refs) for owner, refs in item['endpoints'].items()}):
                raise ContractError(f'{ident}: access-only portal source/modular owner denominator mismatch')
            electrical.update(item['endpoints'])
            for block, sources in item['endpoints'].items():
                for source_pad in sources:
                    expected.add((source_pad, graph.native_identity(source_pad, aliases), net, block))
        if (not isinstance(row['electrical_owners'], list) or
                len(row['electrical_owners']) != len(set(row['electrical_owners'])) or
                set(row['electrical_owners']) != electrical or transit not in electrical or
                electrical & set(overlaps)):
            raise ContractError(f'{ident}: access-only portal electrical/planning owner mismatch')
        affected = row['affected']
        if (not isinstance(affected, list) or any(not isinstance(e, dict) or
                set(e) != {'source_pad', 'native_pad', 'net', 'block'} for e in affected) or
                len(affected) != len(expected) or
                {(e['source_pad'], e['native_pad'], e['net'], e['block']) for e in affected} != expected):
            raise ContractError(f'{ident}: access-only portal exact endpoint denominator mismatch')
        _linked_native_pad_census(ident, expected, pads, set(nets))
        layer, reference = row['layer'], row['reference_layer']
        if layer not in enabled or reference not in enabled or layer == reference:
            raise ContractError(f'{ident}: access-only portal layer/reference invalid')
        if any(owners.get(native.rsplit('.', 1)[0]) != block or
               not all(p.IsOnLayer(board.GetLayerID(layer)) for p in pads[native])
               for _, native, _, block in expected):
            raise ContractError(f'{ident}: access-only portal native owner/layer mismatch')
        portal = rectangle(row['portal_bbox'], f'{ident} portal')
        if not lane_inside_outline(outline, portal):
            raise ContractError(f'{ident}: access-only portal off board outline')
        owner_area = rectangle(regions[transit], f'{transit} owner region')
        face = row['owner_face']
        if face not in ('north', 'south', 'east', 'west'):
            raise ContractError(f'{ident}: access-only portal owner face invalid')
        if face == 'north':
            touches = portal[1] < owner_area[3] < portal[3] and max(portal[0], owner_area[0]) < min(portal[2], owner_area[2])
        elif face == 'south':
            touches = portal[1] < owner_area[1] < portal[3] and max(portal[0], owner_area[0]) < min(portal[2], owner_area[2])
        elif face == 'east':
            touches = portal[0] < owner_area[2] < portal[2] and max(portal[1], owner_area[1]) < min(portal[3], owner_area[3])
        else:
            touches = portal[0] < owner_area[0] < portal[2] and max(portal[1], owner_area[1]) < min(portal[3], owner_area[3])
        if not touches:
            raise ContractError(f'{ident}: access-only portal lacks positive owner-edge contact')
        actual_overlaps = {name for name, area in regions.items()
                           if name != transit and intersects(portal, rectangle(area, f'{name} region'))}
        if actual_overlaps != set(overlaps):
            raise ContractError(f'{ident}: access-only portal foreign planning overlap mismatch')
        if contract_allocations is not None:
            if not isinstance(contract_allocations, list):
                raise ContractError(f'{ident}: ordinary allocation inventory malformed')
            for allocation_row in contract_allocations:
                for reservation in allocation_row.get('reservations', []):
                    if reservation.get('layer') != layer:
                        continue
                    if 'bbox' not in reservation:
                        if reservation.get('kind') in UNRESOLVED_KINDS:
                            continue
                        raise ContractError(f'{ident}: ordinary reservation geometry missing')
                    if intersects(portal, rectangle(reservation['bbox'], 'ordinary reservation')):
                        raise ContractError(f'{ident}: overlaps ordinary reservation {reservation.get("id")}')
        for corridor in source.get('integration_corridors', []):
            if corridor.get('layer') == layer and intersects(
                    portal, rectangle(regions[corridor['region_id']], 'integration region')):
                raise ContractError(f'{ident}: overlaps integration corridor {corridor.get("id")}')
        for path in source.get('linked_paths', []):
            for stage in path.get('stages', []):
                if stage.get('kind') == 'physical_corridor' and stage.get('layer') == layer and intersects(
                        portal, rectangle(regions[stage['region_id']], 'linked stage region')):
                    raise ContractError(f'{ident}: overlaps linked physical stage {stage.get("id")}')
        for port in source.get('shared_transition_ports', []):
            shapes = [port[key] for key in ('bbox', 'reservation_bbox')]
            shapes.extend(port.get('geometry', {}).get('rectangles', []))
            if layer in port.get('layers', []) and any(
                    intersects(portal, rectangle(shape, 'shared port scope')) for shape in shapes):
                raise ContractError(f'{ident}: overlaps shared transition port {port.get("id")}')
        for cell_id, cell in (physical_cells or {}).items():
            if cell['owner_block'] != transit and intersects(portal, cell['bbox']):
                raise ContractError(f'{ident}: overlaps foreign physical cell {cell_id}')
        for fp in board.GetFootprints():
            if any(intersects(portal, shape) for shape in
                   [_physical_envelope(fp)] + [box_mm(p.GetBoundingBox()) for p in fp.Pads()]):
                raise ContractError(f'{ident}: native footprint/pad {fp.GetReference()} enters access-only portal')
        if any(intersects(portal, box_mm(track.GetBoundingBox())) for track in board.GetTracks()):
            raise ContractError(f'{ident}: native copper enters access-only portal')
        for zone in zones:
            if zone.GetIsRuleArea() and intersects(portal, box_mm(zone.GetBoundingBox())):
                raise ContractError(f'{ident}: native rule area enters access-only portal')
            if not zone.GetIsRuleArea() and _filled_zone_intersects(zone, board.GetLayerID(layer), portal):
                raise ContractError(f'{ident}: filled signal copper enters access-only portal')
        expected_p2 = [{'status': 'P2_REQUIRED', **e, 'portal_id': ident,
                        'layer': layer, 'proof': ('native_pad_to_local_port' if e['block'] == transit
                                                else 'native_pad_to_remote_route')}
                       for e in affected]
        if row['p2_obligations'] != expected_p2 or row['return_obligation'] != {
                'status': 'P2_REQUIRED', 'net': 'GND', 'portal_id': ident,
                'reference_layer': reference, 'proof': 'continuous_filled_reference'}:
            raise ContractError(f'{ident}: access-only portal P2/filled-return debt invalid')
        if any(intersects(portal, prior['bbox']) and layer == prior['layer'] for prior in screened):
            raise ContractError(f'{ident}: access-only portals overlap')
        screened.append({'id': ident, 'status': 'INCOMPLETE', 'nets': nets,
                         'bbox': portal, 'layer': layer, 'capacity_slots': None,
                         'p2_obligations': expected_p2,
                         'return_obligation': row['return_obligation']})
    return screened


def _linked_paths(source, contract, interfaces, board, outline, regions, zones,
                  coverage, aliases, pads, owned_pads, fixed_refs, movable_refs,
                  shared_ports, physical_cells, native_pitch):
    """Three-owner series path with independently validated stage geometry.

    The path is one allocation reservation, not two credits. Legacy corridor
    records are untouched, and a virtual span can never establish P1 capacity.
    """
    rows = source.get('linked_paths')
    claimed = [a for a in contract['allocations'] if a.get('linked_paths')]
    if rows is None:
        if claimed:
            raise ContractError('linked path contract lacks source declaration')
        return {}
    if not isinstance(rows, list) or not rows:
        raise ContractError('linked paths malformed')
    if not isinstance(interfaces.get('blocks'), list):
        raise ContractError('linked paths require modular block ownership')
    owners = {ref: block['id'] for block in interfaces['blocks'] for ref in block.get('refs', [])}
    result, used_ids, used_nets = {}, set(), set()
    used_stage_ids, used_reservation_ids, used_regions = set(), set(), set()
    used_stage_areas, used_access_areas = [], []
    enabled = {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq()
               if pcbnew.IsCopperLayer(i)}
    ordinary = [(a['id'], r) for a in contract['allocations']
                for r in a.get('reservations', [])]
    for path in rows:
        if not isinstance(path, dict) or set(path) != {
                'id', 'allocation_id', 'nets', 'owner_order', 'reservation_id',
                'layer', 'reference_layer', 'stages', 'joins'}:
            raise ContractError('linked path record malformed')
        ident, allocation_id, nets = path['id'], path['allocation_id'], path['nets']
        order, stages = path['owner_order'], path['stages']
        if (not isinstance(ident, str) or not ident or ident in used_ids or
                allocation_id not in coverage or not isinstance(nets, list) or
                not nets or len(nets) != len(set(nets)) or
                not set(nets) <= coverage[allocation_id] or used_nets & set(nets) or
                not isinstance(order, list) or len(order) != 3 or len(set(order)) != 3 or
                any(owner not in regions for owner in order) or
                not isinstance(stages, list) or len(stages) != 2 or
                path['layer'] not in enabled or path['reference_layer'] not in enabled or
                path['layer'] == path['reference_layer'] or
                not isinstance(path['reservation_id'], str) or not path['reservation_id']):
            raise ContractError(f'{ident}: linked path identity/order/net/layer invalid')
        used_ids.add(ident)
        used_nets.update(nets)
        alloc = next(a for a in contract['allocations'] if a['id'] == allocation_id)
        if alloc.get('linked_paths') != [{'id': ident, 'kind': 'linked_path',
                                          'nets': nets, 'status': 'INCOMPLETE'}]:
            raise ContractError(f'{ident}: linked path contract declaration mismatch')
        if any(set(r.get('nets', [])) & set(nets) for _, r in ordinary) or any(
                w.get('net') in nets for w in alloc.get('boundary_witnesses', [])):
            raise ContractError(f'{ident}: linked path net has competing ordinary credit/witness')
        if any(r.get('id') == path['reservation_id'] for _, r in ordinary):
            raise ContractError(f'{ident}: linked path reservation id reused')
        physical, second = stages
        physical_keys = {'id', 'kind', 'owner', 'region_id', 'allocation_id',
                         'participants', 'faces', 'layer', 'reference_layer',
                         'nets', 'reservation_id', 'affected', 'p2_obligations',
                         'return_obligation', 'fixed_accesses', 'axis',
                         'slot_pitch_mm', 'demand_slots'}
        if not isinstance(physical, dict) or set(physical) != physical_keys:
            raise ContractError(f'{ident}: physical stage schema/outcome fields invalid')
        if (physical.get('kind') != 'physical_corridor' or
                physical.get('participants') != order[:2] or
                physical.get('allocation_id') != allocation_id or
                physical.get('nets') != nets or physical.get('layer') != path['layer'] or
                physical.get('reference_layer') != path['reference_layer'] or
                not isinstance(second, dict) or second.get('kind') not in
                ('unresolved_virtual_span', 'physical_corridor') or
                second.get('participants') != order[1:] or second.get('nets') != nets or
                second.get('layer') != path['layer'] or
                second.get('reference_layer') != path['reference_layer'] or
                second.get('id') == physical.get('id')):
            raise ContractError(f'{ident}: linked stage order/identity invalid')
        second_physical = second['kind'] == 'physical_corridor'
        if second_physical and set(second) != physical_keys:
            raise ContractError(f'{ident}: second physical stage schema/outcome fields invalid')
        physical_stages = [physical, second] if second_physical else [physical]
        stage_ids = [stage.get('id') for stage in stages]
        reservation_ids = [path['reservation_id']] + [stage.get('reservation_id')
                                                    for stage in physical_stages]
        region_ids = [stage.get('region_id') for stage in physical_stages]
        if (any(not isinstance(value, str) or not value for value in
                stage_ids + reservation_ids + region_ids) or
                len(set(stage_ids)) != len(stage_ids) or
                len(set(reservation_ids)) != len(reservation_ids) or
                len(set(region_ids)) != len(region_ids) or
                set(stage_ids) & used_stage_ids or
                set(reservation_ids) & used_reservation_ids or
                set(region_ids) & used_regions):
            raise ContractError(f'{ident}: linked physical stage identity reused')
        if not second_physical and (
                set(second) != {'id', 'kind', 'participants', 'nets', 'layer',
                                'reference_layer', 'affected', 'geometry',
                                'capacity_slots', 'status', 'p2_obligations',
                                'return_obligation'} or
                second['geometry'] is not None or second['capacity_slots'] is not None or
                second['status'] != 'INCOMPLETE'):
            raise ContractError(f'{ident}: virtual span must be geometry/capacity free')
        if second_physical and (
                second.get('allocation_id') != allocation_id or
                second.get('owner') != 'board_integration' or
                second.get('reservation_id') in
                (physical.get('reservation_id'), path['reservation_id']) or
                second.get('region_id') == physical.get('region_id')):
            raise ContractError(f'{ident}: second physical stage identity invalid')
        physical_source = dict(source, integration_corridors=[physical])
        corridor = _integration_corridors(physical_source, interfaces, board,
                                          outline, regions, zones, coverage,
                                          aliases, pads, shared_ports,
                                          physical_cells)[physical['id']]
        second_corridor = None
        if second_physical:
            second_source = dict(source, integration_corridors=[second])
            second_corridor = _integration_corridors(
                second_source, interfaces, board, outline, regions, zones,
                coverage, aliases, pads, shared_ports, physical_cells)[second['id']]
            if intersects(corridor['bbox'], second_corridor['bbox']):
                raise ContractError(f'{ident}: physical stages overlap')
            if second.get('fixed_accesses') != []:
                raise ContractError(f'{ident}: second physical stage fixed accesses unsupported')
            if any(e['native_pad'].rsplit('.', 1)[0] in fixed_refs
                   for e in second['affected']):
                raise ContractError(f'{ident}: second physical stage has unhandled fixed endpoint')
        stage_areas = [corridor['bbox']] + ([second_corridor['bbox']] if second_physical else [])
        if any(layer == path['layer'] and intersects(area, prior)
               for area in stage_areas
               for layer, prior in used_stage_areas + used_access_areas):
            raise ContractError(f'{ident}: linked physical stage overlaps another linked path')
        for _, reservation in ordinary:
            if (reservation.get('layer') == path['layer'] and
                    reservation.get('kind') not in UNRESOLVED_KINDS and
                    any(intersects(rectangle(reservation.get('bbox'), 'ordinary reservation'),
                                   stage['bbox']) for stage in
                        ([corridor, second_corridor] if second_physical else [corridor]))):
                raise ContractError(f'{ident}: physical stage overlaps ordinary reservation')
        if (not isinstance(physical.get('fixed_accesses'), list) or
                not isinstance(physical.get('axis'), str) or
                physical.get('axis') not in ('horizontal', 'vertical')):
            raise ContractError(f'{ident}: physical stage access/capacity declaration missing')
        access_by_source = {}
        for access in physical['fixed_accesses']:
            if (not isinstance(access, dict) or set(access) !=
                    {'source_pad', 'native_pad', 'net', 'block', 'face', 'bbox'} or
                    access['source_pad'] in access_by_source):
                raise ContractError(f'{ident}: fixed access malformed or duplicate')
            access_by_source[access['source_pad']] = access
        fixed_affected = {e['source_pad'] for e in physical['affected']
                          if e['native_pad'].rsplit('.', 1)[0] in fixed_refs}
        if set(access_by_source) != fixed_affected:
            raise ContractError(f'{ident}: fixed access endpoint denominator mismatch')
        access_shapes = []
        for endpoint in physical['affected']:
            source_pad = endpoint['source_pad']
            if source_pad not in access_by_source:
                continue
            access = access_by_source[source_pad]
            if any(access[k] != endpoint[k] for k in
                   ('source_pad', 'native_pad', 'net', 'block')):
                raise ContractError(f'{source_pad}: fixed access endpoint mismatch')
            obligation = next(o for o in physical['p2_obligations']
                              if o['source_pad'] == source_pad)
            native_pad = endpoint['native_pad']
            pad_box = box_mm(pads[native_pad][0].GetBoundingBox())
            witness = {'source': source_pad, 'native': native_pad,
                       'net': endpoint['net'], 'block': endpoint['block'],
                       'layer': path['layer'], 'face': access['face'],
                       'boundary_bbox': pad_box,
                       'kind': 'fixed_connector_access',
                       'corridor_id': physical['id'], 'p2_obligation': obligation}
            if next(f for f in corridor['faces'] if f['block'] == endpoint['block']).get('physical_cell_id'):
                witness['physical_cell_id'] = next(
                    f['physical_cell_id'] for f in corridor['faces']
                    if f['block'] == endpoint['block'])
            _coarse_witness(board, witness, endpoint['net'], owned_pads,
                            aliases, pads, outline, regions, fixed_refs,
                            shared_ports, {physical['id']: corridor}, {}, physical_cells)
            area = rectangle(access['bbox'], f'{source_pad} fixed access')
            face = next(f for f in corridor['faces'] if f['block'] == endpoint['block'])
            approach = {'north': 'south', 'south': 'north',
                        'east': 'west', 'west': 'east'}[face['region_face']]
            if (not contains(rectangle(regions[witness.get('physical_cell_id') or endpoint['block']],
                                       'fixed access owner'), area) or
                    not _witness_touches_reservation(witness, {'bbox': area}) or
                    not intersects(area, face['bbox']) or
                    not _witness_touches_reservation(
                        {'boundary_bbox': area, 'face': approach}, {'bbox': corridor['bbox']})):
                raise ContractError(f'{source_pad}: fixed access does not join source face')
            for other_source, other_area in access_shapes:
                if intersects(area, other_area):
                    raise ContractError(f'{source_pad}: fixed access overlaps {other_source}')
            if any(layer == path['layer'] and intersects(area, prior)
                   for layer, prior in used_stage_areas + used_access_areas):
                raise ContractError(f'{source_pad}: fixed access overlaps another linked path')
            for _, reservation in ordinary:
                if (reservation.get('layer') == path['layer'] and
                        reservation.get('kind') not in UNRESOLVED_KINDS and
                        intersects(area, rectangle(reservation.get('bbox'), 'ordinary reservation'))):
                    raise ContractError(f'{source_pad}: fixed access overlaps ordinary reservation')
            access_shapes.append((source_pad, area))
            for fp in board.GetFootprints():
                ref = fp.GetReference()
                if ref != native_pad.rsplit('.', 1)[0] and intersects(area, _physical_envelope(fp)):
                    raise ContractError(f'{source_pad}: fixed access intersects native body {ref}')
                if any(f'{ref}.{pad.GetNumber()}' != native_pad and
                       pad.IsOnLayer(board.GetLayerID(path['layer'])) and
                       intersects(area, box_mm(pad.GetBoundingBox())) for pad in fp.Pads()):
                    raise ContractError(f'{source_pad}: fixed access intersects foreign pad {ref}')
            if any(item.IsOnLayer(board.GetLayerID(path['layer'])) and
                   intersects(area, box_mm(item.GetBoundingBox())) for item in board.GetTracks()):
                raise ContractError(f'{source_pad}: fixed access intersects native copper')
            if any(not zone.GetIsRuleArea() and
                   _filled_zone_intersects(zone, board.GetLayerID(path['layer']), area)
                   for zone in zones):
                raise ContractError(f'{source_pad}: fixed access intersects filled copper')
            if any(zone.GetIsRuleArea() and intersects(area, box_mm(zone.GetBoundingBox()))
                   for zone in zones):
                raise ContractError(f'{source_pad}: fixed access intersects rule area')
        if (not isinstance(second['affected'], list) or
                any(not isinstance(e, dict) or set(e) !=
                    {'source_pad', 'native_pad', 'net', 'block'} for e in second['affected'])):
            raise ContractError(f'{ident}: second-stage endpoint records malformed')
        expected_second = set()
        for item in interfaces['interfaces']:
            if item['net'] in nets:
                for owner in order[1:]:
                    for source_pad in item['endpoints'].get(owner, []):
                        expected_second.add((source_pad, graph.native_identity(source_pad, aliases),
                                              item['net'], owner))
        actual_second = {(e['source_pad'], e['native_pad'], e['net'], e['block'])
                         for e in second['affected']}
        if actual_second != expected_second or len(actual_second) != len(second['affected']):
            label = 'second physical' if second_physical else 'virtual'
            raise ContractError(f'{ident}: {label} endpoint denominator mismatch')
        for e in second['affected']:
            if (owners.get(e['native_pad'].rsplit('.', 1)[0]) != e['block'] or
                    not pads.get(e['native_pad']) or
                    any(p.GetNetname() != e['net'] or
                        not p.IsOnLayer(board.GetLayerID(path['layer']))
                        for p in pads[e['native_pad']])):
                raise ContractError(f"{e['source_pad']}: second-stage native owner/pad/net/layer mismatch")
        if not second_physical:
            expected_p2 = [{'status': 'P2_REQUIRED', **e,
                            'stage_id': second['id'], 'layer': path['layer'],
                            'to_reservation': path['reservation_id']}
                           for e in second['affected']]
            if second['p2_obligations'] != expected_p2 or second['return_obligation'] != {
                    'status': 'P2_REQUIRED', 'net': 'GND', 'stage_id': second['id'],
                    'reference_layer': path['reference_layer'],
                    'proof': 'continuous_filled_reference'}:
                raise ContractError(f'{ident}: virtual P2/filled-return obligations incomplete')
        expected_all = set()
        for item in interfaces['interfaces']:
            if item['net'] in nets:
                if set(item['endpoints']) != set(order):
                    raise ContractError(f'{ident}: path owner denominator mismatch')
                for owner in order:
                    for source_pad in item['endpoints'][owner]:
                        expected_all.add((source_pad, graph.native_identity(source_pad, aliases),
                                          item['net'], owner))
        actual_all = {(e['source_pad'], e['native_pad'], e['net'], e['block'])
                      for stage in stages for e in stage['affected']}
        if actual_all != expected_all:
            raise ContractError(f'{ident}: path terminal denominator mismatch')
        _linked_native_pad_census(ident, expected_all, pads, set(nets))
        physical_set = {(e['source_pad'], e['net'], e['block']) for e in physical['affected']}
        second_set = {(e['source_pad'], e['net'], e['block']) for e in second['affected']}
        shared = physical_set & second_set
        if ({owner for _, _, owner in shared} != {order[1]} or
                {net: sum(1 for _, shared_net, _ in shared if shared_net == net)
                 for net in nets} != {net: 1 for net in nets}):
            raise ContractError(f'{ident}: interstage join multiplicity invalid')
        expected_joins = [{'from': physical['id'], 'to': second['id'],
                           'owner': order[1], 'net': net, 'source_pad': source_pad,
                           'kind': ('pad_anchored_physical_interstage' if second_physical
                                    else 'pad_anchored_virtual_interstage')}
                          for source_pad, net, owner in sorted(shared)]
        if path['joins'] != expected_joins or {owner for _, _, owner in shared} != {order[1]}:
            raise ContractError(f'{ident}: missing or parallel interstage join')
        pitch, demand = physical.get('slot_pitch_mm'), physical.get('demand_slots')
        if (isinstance(pitch, bool) or not isinstance(pitch, (int, float)) or
                not math.isfinite(pitch) or pitch < native_pitch or
                isinstance(demand, bool) or
                not isinstance(demand, int) or demand < len(nets)):
            raise ContractError(f'{ident}: physical stage rough capacity declaration invalid')
        rough = _coarse_reservation(board, {'id': physical['id'], 'kind': 'signal',
                                          'layer': path['layer'], 'bbox': corridor['bbox'],
                                          'axis': physical['axis'], 'nets': nets,
                                          'demand_slots': demand, 'slot_pitch_mm': pitch},
                                    outline, fixed_refs, movable_refs, zones, native_pitch,
                                    power_boundary=False, power_like_nets=set())
        if rough['status'] == 'FAIL':
            raise ContractError(f'{ident}: physical stage raw capacity below demand')
        if second_physical:
            pitch2, demand2 = second.get('slot_pitch_mm'), second.get('demand_slots')
            if (second.get('axis') not in ('horizontal', 'vertical') or
                    isinstance(pitch2, bool) or not isinstance(pitch2, (int, float)) or
                    not math.isfinite(pitch2) or pitch2 < native_pitch or
                    isinstance(demand2, bool) or not isinstance(demand2, int) or
                    demand2 < len(nets)):
                raise ContractError(f'{ident}: second physical stage rough capacity declaration invalid')
            rough2 = _coarse_reservation(
                board, {'id': second['id'], 'kind': 'signal',
                        'layer': path['layer'], 'bbox': second_corridor['bbox'],
                        'axis': second['axis'], 'nets': nets,
                        'demand_slots': demand2, 'slot_pitch_mm': pitch2},
                outline, fixed_refs, movable_refs, zones, native_pitch,
                power_boundary=False, power_like_nets=set())
            if rough2['status'] == 'FAIL':
                raise ContractError(f'{ident}: second physical stage raw capacity below demand')
            second_result = {'id': second['id'], 'status': 'INCOMPLETE',
                             'rough_capacity': rough2}
        else:
            second_result = {'id': second['id'], 'status': 'INCOMPLETE',
                             'capacity_slots': None}
        result[allocation_id] = {'id': ident, 'status': 'INCOMPLETE', 'nets': nets,
                                 'capacity_slots': None,
                                 'stages': [{'id': physical['id'], 'status': 'INCOMPLETE',
                                             'rough_capacity': rough},
                                            second_result]}
        used_stage_ids.update(stage_ids)
        used_reservation_ids.update(reservation_ids)
        used_regions.update(region_ids)
        used_stage_areas.extend((path['layer'], area) for area in stage_areas)
        used_access_areas.extend((path['layer'], area) for _, area in access_shapes)
    if len(claimed) != len(rows) or len(result) != len(rows):
        raise ContractError('linked path allocation denominator mismatch')
    return result


def _physical_envelope(fp):
    """Body plus both native courtyards; exclude movable reference/value text."""
    body = list(box_mm(fp.GetBoundingBox(False, False)))
    for layer in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        courtyard = fp.GetCourtyard(layer)
        if courtyard.OutlineCount():
            x0, y0, x1, y1 = box_mm(courtyard.BBox())
            body = [min(body[0], x0), min(body[1], y0),
                    max(body[2], x1), max(body[3], y1)]
    return tuple(body)


_EDGE_BOARD_SHA256 = 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7'
_EDGE_OUTLINE_SHA256 = '8c777cc8717eb7d54ee6581a199d69d0184c0ceb184e2639e6fdecba3822cb6c'
_EDGE_PROJECT_ROOT = Path(__file__).resolve().parents[3] / 'projects/crow-usb-carrier-v1'
_EDGE_PARTS = {
    'J_PWR': ('crow_usb_power_aux.pretty/Molex_43650-0200.kicad_mod',
              '43650-0200/Molex_436501000_SD_revD8.pdf',
              'a5270e0a7273bf96318cc832753a160d61d49ecf18b1bc6f184506f53bd45ce2',
              'b8942b95bc3fe4c02171de9e714d99b2688055e249ba1524e3c2a8c3cf78eaa3',
              (30.0, 29.42, 0.0), 'Molex_43650-0200'),
    **{f'J{n}': ('crow_usb_analog.pretty/Wurth_615008160221_RJ45.kicad_mod',
                 '615008160221/Wurth_615008160221_rev001003.pdf',
                 'c8286c258474bde37022ef16730c7976e488d5fd7312699870ed54ee0dccc7d6',
                 '6ed18749211d4e6cbffd99cd0b90461dfe4ec6d70f558ceceeb5901651f0e048',
                 (50.0 + 22.0 * (n-1), 26.86, 0.0),
                 'Wurth_615008160221_RJ45') for n in range(1, 9)},
}


def _edge_outline_digest(outline):
    if outline.OutlineCount() != 1 or outline.HoleCount(0):
        raise ContractError('edge attachment outline topology invalid')
    points = sorted((point.x, point.y) for point in outline.Outline(0).CPoints())
    return hashlib.sha256(json.dumps(points, separators=(',', ':')).encode()).hexdigest()


def _physical_cell_edge_attachments(source, board, outline, board_sha256):
    """Verify exact nominal drawing-only north-edge attachments for cell use."""
    rows = source.get('physical_cell_edge_attachments')
    if rows is None:
        return {}
    if not isinstance(rows, list) or not rows or board_sha256 != _EDGE_BOARD_SHA256:
        raise ContractError('edge attachment board hash missing or unreviewed')
    outline_hash = _edge_outline_digest(outline)
    if (outline_hash != _EDGE_OUTLINE_SHA256 or
            box_mm(outline.BBox()) != (20.0, 20.0, 240.0, 140.0)):
        raise ContractError('edge attachment native outline drift')
    native = {fp.GetReference(): fp for fp in board.GetFootprints()}
    allowed = {'ref', 'physical_cell_id', 'edge', 'board_sha256', 'outline_sha256',
               'footprint_sha256', 'drawing_sha256', 'pose_mm',
               'maximum_courtyard_projection_mm'}
    result = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != allowed:
            raise ContractError('physical-cell edge attachment fields invalid')
        ref, cell_id = row['ref'], row['physical_cell_id']
        if (ref not in _EDGE_PARTS or ref in result or not isinstance(cell_id, str) or
                not cell_id or row['edge'] != 'north' or
                row['board_sha256'] != _EDGE_BOARD_SHA256 or
                row['outline_sha256'] != _EDGE_OUTLINE_SHA256 or
                row['maximum_courtyard_projection_mm'] != 0.045 or
                ref not in source.get('p1_fixed_refs', [])):
            raise ContractError(f'{ref}: physical-cell edge attachment identity/direction invalid')
        fp_rel, drawing_rel, fp_hash, drawing_hash, pose, lib_item = _EDGE_PARTS[ref]
        footprint_path = _EDGE_PROJECT_ROOT / '03_src/lib' / fp_rel
        drawing_path = _EDGE_PROJECT_ROOT / '02_parts' / drawing_rel
        if (row['footprint_sha256'] != fp_hash or row['drawing_sha256'] != drawing_hash or
                digest(footprint_path) != fp_hash or digest(drawing_path) != drawing_hash):
            raise ContractError(f'{ref}: physical-cell footprint/drawing hash drift')
        fp = native.get(ref)
        if fp is None:
            raise ContractError(f'{ref}: physical-cell native footprint missing')
        actual_pose = (pcbnew.ToMM(fp.GetPosition().x), pcbnew.ToMM(fp.GetPosition().y),
                       fp.GetOrientationDegrees())
        if (row['pose_mm'] != list(pose) or actual_pose != pose or
                str(fp.GetFPID().GetLibItemName()) != lib_item):
            raise ContractError(f'{ref}: physical-cell fixed pose/footprint mismatch')
        courtyard = fp.GetCourtyard(pcbnew.F_CrtYd)
        if courtyard.OutlineCount() != 1 or courtyard.HasHoles():
            raise ContractError(f'{ref}: physical-cell courtyard has extra exterior lobe')
        court_box = box_mm(courtyard.BBox())
        outline_box = box_mm(outline.BBox())
        if (round(outline_box[1] - court_box[1], 6) != 0.045 or
                court_box[0] < outline_box[0] or court_box[2] > outline_box[2] or
                court_box[3] > outline_box[3]):
            raise ContractError(f'{ref}: physical-cell courtyard projection exceeds north limit')
        fab = [box_mm(item.GetBoundingBox()) for item in fp.GraphicalItems()
               if item.GetLayer() == pcbnew.F_Fab and item.GetClass() != 'PCB_TEXT']
        if not fab or any(not lane_inside_outline(outline, box) for box in fab):
            raise ContractError(f'{ref}: physical-cell F.Fab material leaves board')
        for pad in fp.Pads():
            if not lane_inside_outline(outline, box_mm(pad.GetBoundingBox())):
                raise ContractError(f'{ref}: physical-cell pad leaves board material')
            if pad.HasHole():
                # A circumscribed disk safely bounds circular and rotated slot drills.
                drill = pad.GetDrillSize()
                radius = math.hypot(pcbnew.ToMM(drill.x), pcbnew.ToMM(drill.y)) / 2
                center = pad.GetPosition()
                x, y = pcbnew.ToMM(center.x), pcbnew.ToMM(center.y)
                if not lane_inside_outline(outline, (x-radius, y-radius,
                                                     x+radius, y+radius)):
                    raise ContractError(f'{ref}: physical-cell drill/slot leaves board material')
        result[ref] = {'physical_cell_id': cell_id, 'courtyard_bbox': court_box}
    return result


def _physical_cells(source, interfaces, board, outline, regions, patterns,
                    board_sha256=None):
    """Bind disjoint physical regions to exact modular owners, never aliases."""
    rows = source.get('physical_cells')
    if rows is None:
        if 'physical_cell_edge_attachments' in source:
            raise ContractError('physical-cell edge attachment lacks physical cells')
        return {}
    if not isinstance(rows, list) or not rows or not isinstance(interfaces.get('blocks'), list):
        raise ContractError('physical cells require modular block ownership')
    blocks = {b.get('id'): set(b.get('refs', [])) for b in interfaces['blocks']}
    native = {fp.GetReference(): fp for fp in board.GetFootprints()}
    cells, assigned = {}, set()
    edge_attachments = _physical_cell_edge_attachments(source, board, outline,
                                                        board_sha256)
    used_edge = set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {'id', 'owner_block', 'refs', 'transit'}:
            raise ContractError('physical cell record malformed')
        ident, owner, refs = row['id'], row['owner_block'], row['refs']
        if (not isinstance(ident, str) or not ident or ident in cells or ident not in regions or
                not isinstance(owner, str) or owner not in blocks or owner == 'board_integration' or
                not isinstance(refs, list) or len(refs) != len(set(refs)) or
                not all(isinstance(ref, str) for ref in refs) or
                not isinstance(row['transit'], bool) or row['transit'] != (not refs)):
            raise ContractError('physical cell identity/owner/refs invalid')
        if not set(refs) <= blocks[owner] or any(ref in assigned or ref not in native for ref in refs):
            raise ContractError(f'{ident}: physical cell ref ownership/uniqueness mismatch')
        area = rectangle(regions[ident], f'{ident} physical cell')
        edge = next(((ref, edge_attachments[ref]) for ref in refs
                     if ref in edge_attachments), None)
        if edge is not None:
            ref, attachment = edge
            if (len(refs) != 1 or attachment['physical_cell_id'] != ident or
                    area != _physical_envelope(native[ref]) or
                    area[1] != attachment['courtyard_bbox'][1] or
                    area[0] < 20.0 or area[2] > 240.0 or area[3] > 140.0 or
                    not lane_inside_outline(outline, (area[0], 20.0,
                                                      area[2], area[3]))):
                raise ContractError(f'{ident}: edge cell must contain only exact fixed connector')
            used_edge.add(ref)
        elif not lane_inside_outline(outline, area):
            raise ContractError(f'{ident}: physical cell off board outline')
        for ref in refs:
            fp = native[ref]
            if not contains(area, _physical_envelope(fp)) or any(
                    not contains(area, box_mm(p.GetBoundingBox())) for p in fp.Pads()):
                raise ContractError(f'{ref}: native footprint/pad leaves physical cell {ident}')
            if any(pattern.get('region') not in (None, ident)
                   for pattern in patterns if ref in pattern['match']):
                raise ContractError(f'{ref}: floorplan pattern disagrees with physical cell {ident}')
        for ref, fp in native.items():
            if ref not in refs and (intersects(area, _physical_envelope(fp)) or any(
                    intersects(area, box_mm(p.GetBoundingBox())) for p in fp.Pads())):
                raise ContractError(f'{ident}: unassigned native footprint/pad {ref} enters physical cell')
        assigned.update(refs)
        cells[ident] = {'owner_block': owner, 'refs': set(refs),
                        'transit': row['transit'], 'bbox': area}
    for owner in {c['owner_block'] for c in cells.values()}:
        if assigned & blocks[owner] != blocks[owner]:
            raise ContractError(f'{owner}: physical cell ref denominator incomplete')
        if owner in regions and owner not in cells:
            raise ContractError(f'{owner}: primary physical cell missing')
        group = [c for c in cells.values() if c['owner_block'] == owner]
        reached = {id(c) for c in group if c['refs']}
        if not reached:
            raise ContractError(f'{owner}: physical cells have no occupied anchor')
        while True:
            expanded = reached | {id(c) for c in group if any(
                _positive_edge_contact(c['bbox'], peer['bbox'])
                for peer in group if id(peer) in reached)}
            if expanded == reached:
                break
            reached = expanded
        if len(reached) != len(group):
            raise ContractError(f'{owner}: physical transit cell disconnected')
    for ident, cell in cells.items():
        for other_id, value in regions.items():
            if other_id == ident:
                continue
            other = cells.get(other_id)
            if intersects(cell['bbox'], rectangle(value, f'{other_id} source region')):
                if other and other['owner_block'] == cell['owner_block']:
                    raise ContractError(f'{ident}: physical cells overlap {other_id}')
                raise ContractError(f'{ident}: physical cell overlaps foreign region {other_id}')
    if used_edge != set(edge_attachments):
        raise ContractError('physical-cell edge attachment lacks exact one-ref cell')
    return cells


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


def _independent_coarse_diagnostics(allocations, coverage, board, owned_pads, aliases,
                                    pads, outline, regions, fixed_refs, movable_refs,
                                    shared_ports, corridors, branches, physical_cells,
                                    zones, native_pitch, source, owner_pockets=None):
    """Report one local defect per item without relaxing the normal verdict.

    Cross-item endpoint denominators and overlap accounting remain the normal
    evaluator's responsibility. An invalid item must not hide its independent
    neighbors merely because the allocation loop is fail-fast.
    """
    findings = []
    for allocation in allocations:
        name = allocation['id']
        witnesses = allocation.get('boundary_witnesses', [])
        reservations = allocation.get('reservations', [])
        if not isinstance(witnesses, list) or not isinstance(reservations, list):
            continue
        reservation_map = {r.get('id'): r for r in reservations if isinstance(r, dict)}
        for index, witness in enumerate(witnesses):
            source_pad = witness.get('source') if isinstance(witness, dict) else None
            try:
                if not isinstance(witness, dict) or witness.get('net') not in coverage[name]:
                    raise ContractError(f'{name}: witness net outside allocation')
                verified = _coarse_witness(board, witness, witness['net'], owned_pads,
                                           aliases, pads, outline, regions, fixed_refs,
                                           shared_ports, corridors, branches, physical_cells,
                                           owner_pockets)
                target = reservation_map.get(witness.get('reservation_id'))
                if (target is None or verified['net'] not in target.get('nets', []) or
                        verified['layer'] != target.get('layer') or
                        (witness.get('kind') not in ({'fixed_connector_access_segmented'} |
                                                     UNRESOLVED_KINDS) and
                         not _witness_touches_reservation(verified, target))):
                    raise ContractError(f"{verified['source']}: block face does not contact assigned reservation")
                _virtual_region_clearance(witness, target, regions)
            except (ContractError, TypeError, KeyError, AttributeError, ValueError) as exc:
                findings.append({'allocation': name, 'kind': 'boundary_witness',
                                 'index': index, 'source': source_pad, 'reason': str(exc)})
        power_like_nets = set()
        if name == 'usb_device_pair':
            source_row = next((item for item in source['allocations'] if item.get('id') == name), {})
            if any(item.get('id') == 'usb_local_power' and item.get('status') == 'INCOMPLETE'
                   and 'VBUS_USB' in item.get('nets', []) for item in source_row.get('demands', [])):
                power_like_nets.add('VBUS_USB')
        for index, reservation in enumerate(reservations):
            ident = reservation.get('id') if isinstance(reservation, dict) else None
            try:
                if not isinstance(reservation, dict) or not set(reservation.get('nets', [])) <= coverage[name]:
                    raise ContractError(f'{name}: reservation net outside allocation')
                # Special reservations have source-bound cross-item semantics;
                # independently validate their rectangle here and leave their
                # full accounting to the unchanged evaluator below.
                if reservation.get('kind') in ('integration_corridor', 'fixed_connector_access',
                                               'fixed_connector_access_segmented',
                                               *UNRESOLVED_KINDS) or any(
                        p['reservation_id'] == ident for p in shared_ports.values()):
                    if reservation.get('kind') not in UNRESOLVED_KINDS:
                        rectangle(reservation.get('bbox'), f'{ident} reservation')
                else:
                    _coarse_reservation(board, reservation, outline, fixed_refs,
                                        movable_refs, zones, native_pitch,
                                        power_boundary=name == 'power_boundary_windows',
                                        power_like_nets=power_like_nets)
            except (ContractError, TypeError, KeyError, AttributeError, ValueError) as exc:
                findings.append({'allocation': name, 'kind': 'reservation',
                                 'index': index, 'id': ident, 'reason': str(exc)})
    return findings


def evaluate_coarse(board_path, contract_path, expected_contract_sha256=None, *,
                    source_path=None, interface_path=None, alias_path=None, floorplan_path=None,
                    expected_source_sha256=None, expected_interface_sha256=None,
                    expected_alias_sha256=None, expected_floorplan_sha256=None,
                    diagnose_all=False):
    errors, results, hashes = [], [], {}
    diagnostics = []
    shared_ports_configured = integration_configured = linked_configured = portal_configured = pocket_configured = False
    portals = []
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
            linked_configured = isinstance(source, dict) and 'linked_paths' in source
            portal_configured = isinstance(source, dict) and 'access_only_portals' in source
            pocket_configured = isinstance(source, dict) and 'branch_owner_pockets' in source
            branch_configured = isinstance(source, dict) and any(
                key in source for key in ('unresolved_multiterminal_branches',
                                         'unresolved_two_terminal_crossings'))
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
            physical_cells = _physical_cells(source, interfaces, board, outline,
                                             regions, patterns, hashes['board'])
            owner_pockets = _branch_owner_pockets(source, interfaces, board, outline,
                                                   regions, {'board': hashes['board'],
                                                             'floorplan': hashes['floorplan'],
                                                             'alias': hashes['aliases']}, patterns)
            portals = _access_only_portals(source, interfaces, board, outline,
                                           regions, list(board.Zones()), coverage,
                                           aliases, pads, contract.get('allocations'),
                                           physical_cells)
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
                                               zones, coverage, aliases, pads, shared_ports,
                                               physical_cells)
            branches = _unresolved_branches(source, interfaces, board, regions, coverage,
                                            aliases, pads, physical_cells, patterns, owner_pockets)
            used_port_endpoints = defaultdict(set)
            used_corridor_endpoints = defaultdict(set)
            used_branches = defaultdict(set)
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
            for branch in branches.values():
                matches = [(name,r) for name,r in reservations_seen
                           if branch['net'] in r.get('nets', [])]
                if len(matches) != 1 or matches[0][0] != branch['allocation_id'] or \
                        matches[0][1].get('id') != branch['reservation_id']:
                    raise ContractError(f"{branch['id']}: unresolved branch net has competing reservation")
            if {p['reservation_id'] for p in shared_ports.values()} & {c['reservation_id'] for c in corridors.values()}:
                raise ContractError('shared port/integration corridor reservation identity reused')
            special_ids = ([p['reservation_id'] for p in shared_ports.values()] +
                           [c['reservation_id'] for c in corridors.values()] +
                           [b['reservation_id'] for b in branches.values()])
            if len(special_ids) != len(set(special_ids)):
                raise ContractError('special source reservation identity reused')
            linked = _linked_paths(source, contract, interfaces, board, outline,
                                   regions, zones, coverage, aliases, pads,
                                   owned_pads, fixed_refs, movable_refs,
                                   shared_ports, physical_cells, native_pitch)
            if diagnose_all:
                diagnostics = _independent_coarse_diagnostics(
                    allocations, coverage, board, owned_pads, aliases, pads, outline,
                    regions, fixed_refs, movable_refs, shared_ports, corridors, branches,
                    physical_cells, zones, native_pitch, source, owner_pockets)
            for allocation in allocations:
                name = allocation['id']
                try:
                    linked_row = linked.get(name)
                    linked_nets = set(linked_row['nets']) if linked_row else set()
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
                    if (not isinstance(witnesses, list) or
                            (not witnesses and not linked_row) or
                            not isinstance(reservations, list) or
                            (not reservations and not linked_row)):
                        raise ContractError(f'{name}: witness/reservation denominator missing')
                    checked = []
                    for witness in witnesses:
                        if witness.get('net') not in coverage[name]:
                            raise ContractError(f'{name}: witness net outside allocation')
                        checked.append(_coarse_witness(board, witness, witness['net'], owned_pads,
                                                       aliases, pads, outline, regions, fixed_refs,
                                                       shared_ports, corridors, branches, physical_cells,
                                                       owner_pockets))
                    if {w['net'] for w in checked} | linked_nets != coverage[name]:
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
                                (witness.get('kind') not in ('fixed_connector_access_segmented',
                                    *UNRESOLVED_KINDS) and
                                 not _witness_touches_reservation(verified, target))):
                            raise ContractError(f"{verified['source']}: block face does not contact assigned reservation")
                        _virtual_region_clearance(witness, target, regions)
                        if witness.get('kind') in UNRESOLVED_KINDS:
                            branch = branches[witness['branch_id']]
                            if any('branch_owner_pocket_id' in e for e in branch['endpoints']) and (
                                    set(target) != {'id', 'kind', 'branch_id', 'layer', 'nets'}):
                                raise ContractError(f"{verified['source']}: pocketed branch reservation fields invalid")
                            if (branch['_kind'] == 'unresolved_two_terminal_crossing' and
                                    set(target) != {'id', 'kind', 'branch_id', 'layer', 'nets'}):
                                raise ContractError(f"{verified['source']}: two-terminal reservation fields invalid")
                            if (name != branch['allocation_id'] or
                                    target.get('kind') != branch['_kind'] or
                                    witness.get('kind') != branch['_kind'] or
                                    target.get('branch_id') != branch['id'] or
                                    target.get('id') != branch['reservation_id'] or
                                    target.get('nets') != [branch['net']] or
                                    target.get('layer') != branch['layer'] or
                                    any(key in target for key in
                                        ('bbox','segments','capacity_slots','demand_slots','slot_pitch_mm'))):
                                raise ContractError(f"{verified['source']}: unresolved branch cannot reserve geometry/capacity")
                            used_branches[branch['id']].add(verified['source'])
                        if witness.get('kind') == 'shared_transition_port':
                            port = shared_ports[witness['port_id']]
                            if (target.get('id') != port['reservation_id'] or
                                    target.get('layer') not in port['layers'] or
                                    set(target.get('nets', [])) != {e['net'] for e in port['affected']} or
                                    not contains(port['reservation_bbox'], rectangle(target.get('bbox'), 'shared reservation'))):
                                raise ContractError(f"{verified['source']}: reservation outside declared shared port scope")
                            used_port_endpoints[port['id']].add((verified['source'], verified['native'],
                                                                  verified['net'], verified['block'], verified['layer']))
                        if witness.get('kind') in ('integration_corridor_handoff', 'fixed_connector_access',
                                                   'fixed_connector_access_segmented'):
                            corridor = corridors[witness['corridor_id']]
                            if witness.get('kind') in ('fixed_connector_access', 'fixed_connector_access_segmented'):
                                access = rectangle(target.get('bbox'), 'fixed connector access')
                                segmented = witness['kind'] == 'fixed_connector_access_segmented'
                                selected = next(f for f in corridor['faces'] if f['block'] == verified['block'])
                                approach = {'north': 'south', 'south': 'north',
                                            'east': 'west', 'west': 'east'}[selected['region_face']]
                                if (name != corridor['allocation_id'] or
                                        target.get('kind') != witness['kind'] or
                                        target.get('corridor_id') != corridor['id'] or
                                        target.get('layer') != corridor['layer'] or
                                        target.get('nets') != [verified['net']] or
                                        not contains(rectangle(regions[verified['physical_cell_id'] or verified['block']], 'access source region'), access) or
                                        not intersects(access, selected['bbox']) or
                                        (not segmented and not _witness_touches_reservation(
                                            {'boundary_bbox': access, 'face': approach},
                                            {'bbox': corridor['bbox']}))):
                                    raise ContractError(f"{verified['source']}: fixed access does not join source face")
                                shapes = _fixed_access_shapes(target, verified, corridor['bbox'],
                                                               rectangle(regions[verified['physical_cell_id'] or verified['block']], 'access source region'))
                                if segmented and not intersects(shapes[-1], selected['bbox']):
                                    raise ContractError(f"{verified['source']}: segmented fixed access misses source face")
                                for other in reservations:
                                    if other is target or other.get('id') == corridor['reservation_id'] or \
                                            other.get('layer') != corridor['layer']:
                                        continue
                                    if _is_geometry_free_branch_reservation(other, branches):
                                        continue
                                    if other.get('kind') == 'fixed_connector_access_segmented':
                                        peers = [(peer_raw, peer_verified)
                                                 for peer_raw, peer_verified in zip(witnesses, checked)
                                                 if peer_raw.get('kind') == 'fixed_connector_access_segmented' and
                                                 peer_raw.get('reservation_id') == other.get('id')]
                                        if len(peers) != 1:
                                            raise ContractError(f"{verified['source']}: segmented peer access endpoint denominator invalid")
                                        peer_raw, peer_verified = peers[0]
                                        peer_corridor = corridors.get(peer_raw.get('corridor_id'))
                                        if peer_corridor is None:
                                            raise ContractError(f"{verified['source']}: segmented peer access corridor missing")
                                        other_shapes = _fixed_access_shapes(
                                            other, peer_verified, peer_corridor['bbox'],
                                            rectangle(regions[peer_verified['block']], 'peer access source region'))
                                    else:
                                        # A legacy rectangle has no narrower geometry to prove.
                                        other_shapes = [rectangle(other.get('bbox'), 'other reservation')]
                                    if any(intersects(shape, other_shape)
                                           for shape in shapes for other_shape in other_shapes):
                                        raise ContractError(f"{verified['source']}: fixed access overlaps other reservation")
                                # This reservation is intentionally exempt from rough-capacity
                                # measurement, but it still has to be an empty physical access
                                # envelope.  The source footprint's aggregate body bbox is
                                # exempt because it includes the named pad; its other pads are
                                # still rejected below.  A foreign body/courtyard, another pad,
                                # existing copper, or a rule area would make the declaration
                                # misleading.
                                for fp in board.GetFootprints():
                                    ref = fp.GetReference()
                                    side = fp.GetLayerName()
                                    if (ref != verified['native'].rsplit('.', 1)[0] and
                                            ((side == 'F.Cu' and corridor['layer'] == 'F.Cu') or
                                            (side == 'B.Cu' and corridor['layer'] == 'B.Cu'))):
                                        if any(intersects(shape, _physical_envelope(fp)) for shape in shapes):
                                            raise ContractError(f"{verified['source']}: fixed access intersects native body {ref}")
                                    for pad in fp.Pads():
                                        native_pad = f'{ref}.{pad.GetNumber()}'
                                        if (native_pad != verified['native'] and
                                                pad.IsOnLayer(board.GetLayerID(corridor['layer'])) and
                                                any(intersects(shape, box_mm(pad.GetBoundingBox()))
                                                    for shape in shapes)):
                                            raise ContractError(f"{verified['source']}: fixed access intersects native pad {native_pad}")
                                if any(item.IsOnLayer(board.GetLayerID(corridor['layer'])) and
                                       any(intersects(shape, box_mm(item.GetBoundingBox()))
                                           for shape in shapes)
                                       for item in board.GetTracks()):
                                    raise ContractError(f"{verified['source']}: fixed access intersects existing copper")
                                if any(not zone.GetIsRuleArea() and
                                       any(_filled_zone_intersects(zone, board.GetLayerID(corridor['layer']), shape)
                                           for shape in shapes)
                                       for zone in zones):
                                    raise ContractError(f"{verified['source']}: fixed access intersects existing copper")
                                if any(zone.GetIsRuleArea() and
                                       corridor['layer'] in {board.GetLayerName(i) for i in zone.GetLayerSet().Seq()} and
                                       any(intersects(shape, box_mm(zone.GetBoundingBox()))
                                           for shape in shapes)
                                       for zone in zones):
                                    raise ContractError(f"{verified['source']}: fixed access overlaps immutable native rule area")
                            elif (name != corridor['allocation_id'] or
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
                        branch = [b for b in branches.values() if b['reservation_id'] == reservation.get('id')]
                        if branch or reservation.get('kind') in UNRESOLVED_KINDS:
                            if len(branch) != 1 or sum(w.get('reservation_id') == reservation.get('id')
                                                        for w in witnesses) != 1:
                                raise ContractError(f'{name}: unresolved branch witness/reservation denominator mismatch')
                            measured.append({'id':reservation['id'],'status':'INCOMPLETE',
                                'nets':reservation['nets'],'capacity_slots':None,
                                'physical_blockers':branch[0]['physical_blockers'],
                                'p2_obligations':branch[0]['p2_obligations'],
                                'return_obligation':branch[0]['return_obligation'],
                                'tree_obligation':branch[0]['tree_obligation'],
                                'reason':('two-terminal source crossing, physical route and filled return unproved'
                                          if branch[0]['_kind'] == 'unresolved_two_terminal_crossing' else
                                          'five-terminal tree, source-region conflict, physical route and filled return unproved')})
                            continue
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
                        if reservation.get('kind') in ('fixed_connector_access', 'fixed_connector_access_segmented'):
                            if sum(w.get('kind') == reservation.get('kind') and
                                   w.get('reservation_id') == reservation.get('id')
                                   for w in witnesses) != 1:
                                raise ContractError(f'{name}: fixed connector access must serve exactly one endpoint')
                            measured.append({'id': reservation['id'], 'status': 'INCOMPLETE',
                                             'nets': reservation['nets'],
                                             'reason': 'fixed pad access, effective capacity and routing unproved'})
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
                    if {net for r in measured for net in r['nets']} | linked_nets != coverage[name]:
                        raise ContractError(f'{name}: missing per-net reservation')
                    row_result = {'id': name, 'status': 'FAIL' if any(r['status'] == 'FAIL' for r in measured) else 'INCOMPLETE',
                                    'witness_count': len(checked), 'reservation_count': len(measured),
                                    'p2_obligations': [w['p2_obligation'] for w in checked if w['p2_obligation']],
                                    'reservations': measured}
                    if linked_row:
                        row_result['linked_paths'] = [linked_row]
                    results.append(row_result)
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
                                                     or w.get('kind') in ('fixed_connector_access', 'fixed_connector_access_segmented',
                                                                          *UNRESOLVED_KINDS)
                                                     for w in (allocation.get('boundary_witnesses') or [])
                                                     if isinstance(w, dict)) or
                                                 any(r.get('kind') == 'integration_corridor'
                                                     for r in (allocation.get('reservations') or [])
                                                     if isinstance(r, dict)))
                    row_result = {'id': name,
                                  'status': 'FAIL' if definite_geometry_failure else 'INCOMPLETE',
                                  'reason': reason}
                    if linked_row:
                        row_result['linked_paths'] = [linked_row]
                    results.append(row_result)
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
                            not (reservation.get('kind') in ('fixed_connector_access', 'fixed_connector_access_segmented') and
                                 reservation.get('corridor_id') == ident) and
                            set(reservation.get('nets', [])) & set(corridor['nets'])):
                        errors.append(f'{ident}: integration net double reservation credit in {name}')
                    if (reservation.get('id') != corridor['reservation_id'] and
                            reservation.get('kind') not in UNRESOLVED_KINDS and
                            intersects(rectangle(reservation.get('bbox'), 'reservation'), corridor['bbox'])):
                        errors.append(f'{ident}: integration corridor overlaps reservation in {name}')
            for ident, branch in branches.items():
                if len(used_branches[ident]) != 1:
                    errors.append(f'{ident}: unresolved branch representative witness denominator mismatch')
                if sum(r.get('id') == branch['reservation_id'] for _,r in reservations_seen) != 1:
                    errors.append(f'{ident}: unresolved branch reservation denominator mismatch')
            for index, (left_name, left) in enumerate(reservations_seen):
                for right_name, right in reservations_seen[index + 1:]:
                    if (left.get('kind') not in UNRESOLVED_KINDS and
                            right.get('kind') not in UNRESOLVED_KINDS and
                            left_name != right_name and left.get('layer') == right.get('layer') and
                            intersects(rectangle(left.get('bbox'), 'reservation'), rectangle(right.get('bbox'), 'reservation'))):
                        errors.append(f'overlapping named allocations on one layer: {left_name}/{right_name}')
            if any('endpoint_pockets' in row or 'coverage_members' in row or 'through_lane' in row or
                   row.get('local_endpoint_completion') in ('PASS', 'P1_REQUIRED') for row in allocations):
                errors.append('coarse P1 contract attempts P2/P3 all-terminal proof')
        except (ContractError, ValueError, TypeError, AttributeError, RuntimeError, KeyError) as exc:
            errors.append(str(exc))
    status = 'FAIL' if (any(row['status'] == 'FAIL' for row in results) or
                        ((shared_ports_configured or integration_configured or
                          linked_configured or branch_configured or portal_configured or
                          pocket_configured) and errors) or
                        any('overlapping named allocations' in error or 'shared port' in error or
                            'shared transition port' in error or 'unowned overlap' in error or
                            'foreign footprint' in error for error in errors)) else 'INCOMPLETE'
    result = {'schema': 2, 'kind': 'p1-coarse-reservation-screen', 'status': status,
            'hashes': hashes, 'errors': errors, 'allocations': results,
            'allocation_denominator': len(results), 'routing_realized': False,
            'p1_accepted': False,
            'reason': 'independent filled-reference, effective-capacity and P1 review not supplied'}
    if diagnose_all:
        result['diagnostics'] = diagnostics
    if portal_configured:
        result['access_only_portals'] = portals
    return result


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
             expected_alias_sha256=None, expected_floorplan_sha256=None,
             diagnose_all=False):
    try:
        candidate = json.loads(contract_path.read_text())
        if isinstance(candidate, dict) and candidate.get('schema') == 2:
            return evaluate_coarse(board_path, contract_path, expected_contract_sha256,
                                   source_path=source_path, interface_path=interface_path,
                                   alias_path=alias_path, floorplan_path=floorplan_path,
                                   expected_source_sha256=expected_source_sha256,
                                   expected_interface_sha256=expected_interface_sha256,
                                   expected_alias_sha256=expected_alias_sha256,
                                   expected_floorplan_sha256=expected_floorplan_sha256,
                                   diagnose_all=diagnose_all)
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
    parser.add_argument('--diagnose-all', action='store_true',
                        help='schema-2 only: report independent per-item defects without changing the verdict')
    args = parser.parse_args()
    result = evaluate(args.board, args.contract, args.expected_contract_sha256,
                      source_path=args.source_requirements, interface_path=args.interfaces,
                      alias_path=args.aliases, floorplan_path=args.floorplan,
                      expected_source_sha256=args.expected_source_sha256,
                      expected_interface_sha256=args.expected_interface_sha256,
                      expected_alias_sha256=args.expected_alias_sha256,
                      expected_floorplan_sha256=args.expected_floorplan_sha256,
                      diagnose_all=args.diagnose_all)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
