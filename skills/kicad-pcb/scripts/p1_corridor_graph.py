#!/usr/bin/env python3
"""Hash-bound P1 graph topology screen. Geometry and return remain incomplete.

Schema 2 deliberately cannot emit P1 PASS. It verifies source/native terminal
identity and the declared on-board graph, and records pads which still constrain
each segment. Capacity, filled reference, DRC, and mechanical fit require later
native evidence bound to the same saved board.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew


class ContractError(ValueError):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rect(value, name):
    if not isinstance(value, list) or len(value) != 4 or any(
        isinstance(v, bool) or not isinstance(v, (float, int)) or not math.isfinite(v)
        for v in value
    ):
        raise ContractError(f'{name}: expected four finite numbers')
    x0, y0, x1, y1 = map(float, value)
    if x0 >= x1 or y0 >= y1:
        raise ContractError(f'{name}: empty or reversed bbox')
    return x0, y0, x1, y1


def box_mm(box):
    return tuple(pcbnew.ToMM(v) for v in
                 (box.GetLeft(), box.GetTop(), box.GetRight(), box.GetBottom()))


def contains(outer, inner, tol=1e-6):
    return (outer[0] <= inner[0] + tol and outer[1] <= inner[1] + tol and
            outer[2] + tol >= inner[2] and outer[3] + tol >= inner[3])


def overlap(a, b, tol=1e-6):
    return min(a[2], b[2]) - max(a[0], b[0]) > tol and min(a[3], b[3]) - max(a[1], b[1]) > tol


def inside_outline(outline, bbox):
    polygon = pcbnew.SHAPE_POLY_SET()
    polygon.NewOutline()
    for x, y in ((bbox[0], bbox[1]), (bbox[2], bbox[1]),
                 (bbox[2], bbox[3]), (bbox[0], bbox[3])):
        polygon.Append(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
    area = polygon.Area()
    polygon.BooleanIntersection(outline)
    return abs(polygon.Area() - area) <= max(1.0, area * 1e-9)


def source_inventory(source, interfaces):
    """Return allocation coverage and exact schematic ref.pad sets."""
    if source.get('kind') != 'crow-p1-corridor-requirements':
        raise ContractError('wrong P1 source kind')
    rows = source.get('allocations')
    power = source.get('power_boundary_windows')
    if not isinstance(rows, list) or not isinstance(power, dict):
        raise ContractError('source allocation denominator missing')
    allocation_nets = {}
    for row in rows + [dict(power, id='power_boundary_windows')]:
        name, nets = row.get('id'), row.get('coverage_nets')
        if not name or name in allocation_nets or not isinstance(nets, list) or not nets or len(nets) != len(set(nets)):
            raise ContractError('invalid source allocation coverage')
        allocation_nets[name] = set(nets)
    all_nets = [net for nets in allocation_nets.values() for net in nets]
    if len(all_nets) != len(set(all_nets)):
        raise ContractError('source nets are not exact-once')
    if not isinstance(interfaces.get('interfaces'), list):
        raise ContractError('modular interfaces missing')
    terminals = {}
    for item in interfaces['interfaces']:
        net, owners = item.get('net'), item.get('endpoints')
        if net in terminals or not isinstance(owners, dict):
            raise ContractError('duplicate or malformed modular interface')
        pads = [pad for values in owners.values() for pad in values]
        if not pads or len(pads) != len(set(pads)):
            raise ContractError(f'{net}: duplicate or missing source endpoints')
        terminals[net] = set(pads)
    if set(terminals) != set(all_nets):
        raise ContractError('source/modular interface net coverage mismatch')
    for row in rows:
        for net in row['coverage_nets']:
            owners = row.get('endpoints', {}).get(net)
            if not isinstance(owners, dict) or {p for v in owners.values() for p in v} != terminals[net]:
                raise ContractError(f'{net}: source/modular endpoint mismatch')
    evidence = power.get('endpoint_evidence', {}).get('CHASSIS')
    if 'CHASSIS' in allocation_nets['power_boundary_windows']:
        if not isinstance(evidence, dict) or set(evidence.get('native_required_pads', [])) != terminals['CHASSIS']:
            raise ContractError('CHASSIS native shell denominator mismatch')
    return allocation_nets, terminals


def alias_inventory(part):
    rows = part.get('pin_aliases', {}) if part else {}
    result = {}
    for value in rows.values():
        source, native = value.get('schematic'), value.get('footprint')
        if not source or not native or source in result:
            raise ContractError('duplicate or malformed J_USB alias')
        result[str(source)] = str(native)
    return result


def native_identity(source_id, aliases):
    if '.' not in source_id:
        raise ContractError(f'malformed source pad {source_id}')
    ref, number = source_id.rsplit('.', 1)
    if ref == 'J_USB':
        if number not in aliases:
            raise ContractError(f'missing J_USB source alias {source_id}')
        number = aliases[number]
    return ref + '.' + number


def board_index(board):
    refs, pads = {}, defaultdict(list)
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        if ref in refs:
            raise ContractError(f'duplicate native reference {ref}')
        refs[ref] = fp
        for pad in fp.Pads():
            pads[ref + '.' + pad.GetNumber()].append(pad)
    return refs, pads


def edge_datum(pocket, fp, outline, pad_box):
    datum = pocket.get('edge_datum')
    if not isinstance(datum, dict) or not datum.get('footprint_id') or not datum.get('drawing_ref'):
        raise ContractError(f"{pocket['id']}: edge footprint identity/datum missing")
    native_fpid = fp.GetFPID()
    footprint_id = str(native_fpid.GetLibNickname()) + ':' + str(native_fpid.GetLibItemName())
    if footprint_id != datum['footprint_id']:
        raise ContractError(f"{pocket['id']}: edge footprint identity mismatch")
    points = datum.get('outline_edge')
    mouth = datum.get('mouth')
    mouth_local = datum.get('mouth_local')
    expected = datum.get('mouth_to_edge_mm')
    tolerance = datum.get('tolerance_mm')
    overhang = datum.get('max_overhang_mm')
    if (not isinstance(points, list) or len(points) != 2 or
            any(not isinstance(p, list) or len(p) != 2 for p in points) or
            not isinstance(mouth, list) or len(mouth) != 2 or
            not isinstance(mouth_local, list) or len(mouth_local) != 2 or
            any(not isinstance(v, (int, float)) or not math.isfinite(v) for p in points for v in p) or
            any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in mouth) or
            any(not isinstance(v, (int, float)) or not math.isfinite(v) for v in mouth_local) or
            any(not isinstance(v, (int, float)) or v < 0 or not math.isfinite(v)
                for v in (expected, tolerance, overhang))):
        raise ContractError(f"{pocket['id']}: invalid edge datum")
    (x0, y0), (x1, y1) = points
    if x0 != x1 and y0 != y1 or x0 == x1 and y0 == y1:
        raise ContractError(f"{pocket['id']}: edge must be one orthogonal segment")
    # The declared edge must coincide with a real Edge.Cuts segment, not just a bbox.
    board_edges = [shape for shape in fp.GetBoard().GetDrawings()
                   if shape.GetLayer() == pcbnew.Edge_Cuts and shape.GetShape() == pcbnew.SHAPE_T_SEGMENT]
    def mm_point(p):
        return (round(pcbnew.ToMM(p.x), 6), round(pcbnew.ToMM(p.y), 6))
    declared = {tuple(map(float, points[0])), tuple(map(float, points[1]))}
    if not any({mm_point(s.GetStart()), mm_point(s.GetEnd())} == declared for s in board_edges):
        raise ContractError(f"{pocket['id']}: edge datum does not match native Edge.Cuts")
    angle = math.radians(fp.GetOrientationDegrees())
    position = fp.GetPosition()
    actual_mouth = (pcbnew.ToMM(position.x) + mouth_local[0] * math.cos(angle) + mouth_local[1] * math.sin(angle),
                    pcbnew.ToMM(position.y) - mouth_local[0] * math.sin(angle) + mouth_local[1] * math.cos(angle))
    if math.dist(actual_mouth, mouth) > 1e-4:
        raise ContractError(f"{pocket['id']}: mouth datum does not follow native footprint transform")
    distance = abs(mouth[0] - x0) if x0 == x1 else abs(mouth[1] - y0)
    projection = mouth[1] if x0 == x1 else mouth[0]
    extent = (min(y0, y1), max(y0, y1)) if x0 == x1 else (min(x0, x1), max(x0, x1))
    if not extent[0] <= projection <= extent[1] or abs(distance - expected) > tolerance + 1e-6:
        raise ContractError(f"{pocket['id']}: mouth-to-edge registration mismatch")
    body = box_mm(fp.GetBoundingBox(False, False))
    # Only the side outside the board should be counted, using the target pad as on-board side witness.
    if x0 == x1:
        protrusion = max(0, x0 - body[0]) if pad_box[0] >= x0 else max(0, body[2] - x0)
    else:
        protrusion = max(0, y0 - body[1]) if pad_box[1] >= y0 else max(0, body[3] - y0)
    if protrusion > overhang + 1e-6 or not inside_outline(outline, pad_box):
        raise ContractError(f"{pocket['id']}: edge pad/overhang outside approved envelope")


def check_allocation(board, outline, row, expected_nets, source_terminals, aliases, refs, pads):
    name = row.get('id')
    if set(row.get('coverage_nets', [])) != expected_nets:
        raise ContractError(f'{name}: net coverage mismatch')
    expected_sources = {pad: net for net in expected_nets for pad in source_terminals[net]}
    terminals = row.get('terminals')
    if not isinstance(terminals, list) or len(terminals) != len(expected_sources):
        raise ContractError(f'{name}: terminal denominator mismatch')
    seen, mapped = set(), {}
    for terminal in terminals:
        source_id, native_id, net = terminal.get('source'), terminal.get('native'), terminal.get('net')
        if source_id in seen or source_id not in expected_sources or net != expected_sources[source_id]:
            raise ContractError(f'{name}: duplicate or wrong source terminal {source_id}')
        if native_id != native_identity(source_id, aliases):
            raise ContractError(f'{source_id}: source/native alias mismatch')
        found = pads.get(native_id, [])
        if not found or any(p.GetNetname() != net for p in found):
            raise ContractError(f'{native_id}: native pad/net absent or mismatch')
        seen.add(source_id)
        mapped[source_id] = (native_id, found)
    if seen != set(expected_sources):
        raise ContractError(f'{name}: source terminal set mismatch')
    if name == 'power_boundary_windows':
        return {'id': name, 'status': 'INCOMPLETE', 'terminal_count': len(terminals),
                'reason': 'power current/thermal and CHASSIS mechanical boundaries unmeasured'}
    segments, junctions, pockets = row.get('segments'), row.get('junctions'), row.get('pockets')
    if not isinstance(segments, list) or not segments or not isinstance(junctions, list) or not isinstance(pockets, list):
        raise ContractError(f'{name}: graph denominator missing')
    valid_layers = {board.GetLayerName(i) for i in board.GetEnabledLayers().Seq() if pcbnew.IsCopperLayer(i)}
    nodes, segment_map, pocket_map = {}, {}, {}
    for node in junctions:
        ident = node.get('id')
        if not ident or ident in nodes or node.get('layer') not in valid_layers:
            raise ContractError(f'{name}: invalid junction {ident}')
        bbox = rect(node.get('bbox'), f'{ident} junction')
        if not inside_outline(outline, bbox):
            raise ContractError(f'{ident}: junction off board')
        nodes[ident] = (node['layer'], bbox, set(node.get('nets', [])))
    pocket_sources = set()
    for pocket in pockets:
        ident, source_id = pocket.get('id'), pocket.get('source')
        if not ident or ident in nodes or source_id not in mapped or source_id in pocket_sources:
            raise ContractError(f'{name}: duplicate or unknown pocket {ident}')
        layer = pocket.get('layer')
        if layer not in valid_layers or pocket.get('net') != expected_sources[source_id]:
            raise ContractError(f'{ident}: pocket layer/net mismatch')
        native_id, native_pads = mapped[source_id]
        if not all(p.IsOnLayer(board.GetLayerID(layer)) for p in native_pads):
            raise ContractError(f'{ident}: target pad absent from pocket layer')
        bbox = rect(pocket.get('bbox'), f'{ident} pocket')
        if not inside_outline(outline, bbox):
            raise ContractError(f'{ident}: pocket off board')
        if not all(contains(bbox, box_mm(p.GetBoundingBox())) for p in native_pads):
            raise ContractError(f'{ident}: target pad outside pocket')
        ref = native_id.rsplit('.', 1)[0]
        body = box_mm(refs[ref].GetBoundingBox(False, False))
        if not inside_outline(outline, body):
            if pocket.get('kind') != 'edge_connector':
                raise ContractError(f'{ident}: ordinary endpoint body off board')
            edge_datum(pocket, refs[ref], outline, box_mm(native_pads[0].GetBoundingBox()))
        elif pocket.get('kind') == 'edge_connector':
            edge_datum(pocket, refs[ref], outline, box_mm(native_pads[0].GetBoundingBox()))
        nodes[ident] = (layer, bbox, {pocket['net']})
        pocket_sources.add(source_id)
        pocket_map[ident] = pocket
    if pocket_sources != set(expected_sources):
        raise ContractError(f'{name}: uncovered source terminal pockets')
    adjacency = {net: defaultdict(set) for net in expected_nets}
    segment_report = []
    for segment in segments:
        ident, layer, ports = segment.get('id'), segment.get('layer'), segment.get('ports')
        if not ident or ident in segment_map or layer not in valid_layers or not isinstance(ports, list) or len(ports) != 2 or ports[0] == ports[1]:
            raise ContractError(f'{name}: invalid segment {ident}')
        nets = segment.get('nets')
        if not isinstance(nets, list) or not nets or len(nets) != len(set(nets)) or not set(nets) <= expected_nets:
            raise ContractError(f'{ident}: invalid assigned nets')
        bbox = rect(segment.get('bbox'), f'{ident} segment')
        if not inside_outline(outline, bbox):
            raise ContractError(f'{ident}: segment off board')
        for port in ports:
            if port not in nodes or nodes[port][0] != layer or not overlap(bbox, nodes[port][1]):
                raise ContractError(f'{ident}: missing, layer-mismatched, or closed port {port}')
            if not set(nets) <= nodes[port][2]:
                raise ContractError(f'{ident}: port net mismatch {port}')
        obstacle_pads = []
        for native_id, native_rows in pads.items():
            for pad in native_rows:
                if not pad.IsOnLayer(board.GetLayerID(layer)) or not overlap(bbox, box_mm(pad.GetBoundingBox())):
                    continue
                # Exempt a target pad only inside its exact own pocket. Other pads on
                # that reference remain visible, including same-net fused lands.
                exempt = any(mapped[p['source']][0] == native_id and p['layer'] == layer and
                             p['net'] in nets and contains(nodes[pid][1], box_mm(pad.GetBoundingBox()))
                             for pid, p in pocket_map.items() if pid in ports)
                if not exempt:
                    obstacle_pads.append(native_id)
        segment_report.append({'id': ident, 'obstacle_pads': sorted(set(obstacle_pads)),
                               'capacity_status': 'INCOMPLETE'})
        for net in nets:
            adjacency[net][ports[0]].add(ports[1])
            adjacency[net][ports[1]].add(ports[0])
        segment_map[ident] = segment
    for net in expected_nets:
        terminals_for_net = [pid for pid, p in pocket_map.items() if p['net'] == net]
        if len(terminals_for_net) < 2:
            raise ContractError(f'{net}: fewer than two terminal pockets')
        reached, stack = set(), [terminals_for_net[0]]
        while stack:
            node = stack.pop()
            if node not in reached:
                reached.add(node)
                stack.extend(adjacency[net][node] - reached)
        if not set(terminals_for_net) <= reached:
            raise ContractError(f'{net}: graph does not reach every terminal')
    return {'id': name, 'status': 'INCOMPLETE', 'terminal_count': len(terminals),
            'segment_count': len(segments), 'junction_count': len(junctions),
            'graph_valid': True, 'segments': segment_report,
            'reason': 'topology checked; effective capacity, filled reference, DRC and pad access still unproved'}


def evaluate(board_path: Path, contract_path: Path, source_path: Path, interface_path: Path,
             alias_path: Path, expected_contract_sha256: str | None = None,
             expected_source_sha256: str | None = None,
             expected_interface_sha256: str | None = None,
             expected_alias_sha256: str | None = None):
    paths = {'board': board_path, 'contract': contract_path, 'source': source_path,
             'interfaces': interface_path, 'aliases': alias_path}
    hashes, errors, rows = {}, [], []
    for name, path in paths.items():
        try:
            hashes[name] = digest(path)
        except OSError as exc:
            errors.append(f'{name} unavailable: {exc}')
    if errors:
        return {'schema': 2, 'status': 'INCOMPLETE', 'errors': errors, 'allocations': [],
                'hashes': hashes, 'routing_realized': False, 'p1_accepted': False}
    expected = {'contract': expected_contract_sha256, 'source': expected_source_sha256,
                'interfaces': expected_interface_sha256, 'aliases': expected_alias_sha256}
    for name, value in expected.items():
        if value != hashes[name]:
            errors.append(f'{name} hash not bound to independent expected digest')
    try:
        contract = json.loads(contract_path.read_text())
        source = yaml.safe_load(source_path.read_text())
        interfaces = json.loads(interface_path.read_text())
        aliases = alias_inventory(yaml.safe_load(alias_path.read_text()))
        if contract.get('schema') != 2 or contract.get('kind') != 'p1-corridor-graph':
            raise ContractError('contract must be p1-corridor-graph schema 2')
        for name in ('board', 'source', 'interfaces', 'aliases'):
            if contract.get(name + '_sha256') != hashes[name]:
                errors.append(f'{name} hash drift in contract')
        coverage, terminals = source_inventory(source, interfaces)
        if contract.get('profile') == 'crow-p1' and (len(terminals) != 59 or len(coverage) != 5):
            raise ContractError('crow-p1 requires exactly 59 nets in five coverage groups')
        board = pcbnew.LoadBoard(str(board_path))
        outline = pcbnew.SHAPE_POLY_SET()
        if board is None or not board.GetBoardPolygonOutlines(outline, False) or outline.OutlineCount() != 1:
            raise ContractError('native board outline unavailable')
        refs, pads = board_index(board)
        allocations = contract.get('allocations')
        if not isinstance(allocations, list) or len(allocations) != len(coverage):
            raise ContractError('contract allocation denominator mismatch')
        names = [r.get('id') for r in allocations if isinstance(r, dict)]
        if len(names) != len(set(names)) or set(names) != set(coverage):
            raise ContractError('contract allocation identities mismatch')
        for row in allocations:
            try:
                rows.append(check_allocation(board, outline, row, coverage[row['id']],
                                             terminals, aliases, refs, pads))
            except (ContractError, TypeError, KeyError, AttributeError) as exc:
                rows.append({'id': row.get('id'), 'status': 'INCOMPLETE',
                             'graph_valid': False, 'reason': str(exc)})
    except (ContractError, ValueError, TypeError, AttributeError, RuntimeError, KeyError) as exc:
        errors.append(str(exc))
    return {'schema': 2, 'kind': 'p1-corridor-graph-screen', 'status': 'INCOMPLETE',
            'hashes': hashes, 'errors': errors, 'allocations': rows,
            'routing_realized': False, 'p1_accepted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('board', 'contract', 'source', 'interfaces', 'aliases', 'output'):
        parser.add_argument(name, type=Path)
    for name in ('contract', 'source', 'interface', 'alias'):
        parser.add_argument('--expected-' + name + '-sha256', required=True)
    args = parser.parse_args()
    result = evaluate(args.board, args.contract, args.source, args.interfaces, args.aliases,
                      args.expected_contract_sha256, args.expected_source_sha256,
                      args.expected_interface_sha256, args.expected_alias_sha256)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return 1  # No capacity/reference/DRC acceptance exists in this revision.


if __name__ == '__main__':
    raise SystemExit(main())
