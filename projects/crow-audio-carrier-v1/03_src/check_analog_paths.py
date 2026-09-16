#!/usr/bin/env python3
"""Carrier analog path contract and conditional saved-copper resistance screen.

Backend gap (M8): shared R-LEN grades endpoint lengths, not width-weighted
trace/barrel resistance. A future shared nets.yaml trace_resistance schema
should replace this one-board adapter; a second board must not copy it.

The independent text reader, not pcbnew/KRT, measures saved copper. All copper
on each of the three post-buffer nets is charged in series, including branches,
so extra inventory cannot hide resistance. The 2x design reserve is not a
fabrication tolerance: nominal foil and average hole plating do not establish
local minima. Pad spreading, solder, intentional resistors and switch Ron are
not priced. Physical end-to-end DCR remains UNVERIFIED even when this screen
passes. See ADR0019 for scope and primary sources.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys

import yaml

PROJECT = Path(__file__).resolve().parent.parent
REPO = PROJECT.parents[1]
sys.path.insert(0, str(REPO / 'skills/kicad-pcb/scripts'))
import copper_length_audit as length
import critical_path_check as critical
from generate_board_generic import parse_netlist

# Physical pin table remains vendor identity; logical association is source.
PHYSICAL_ADC_PINS = {'P': [40, 42, 46, 48, 14, 16, 20, 22],
                     'N': [39, 41, 45, 47, 13, 15, 19, 21]}


def validate_channel_map(data):
    if (not isinstance(data, dict) or set(data) != {'schema', 'id', 'pod_to_adc', 'capture_requirements'}
            or type(data['schema']) is not int or data['schema'] != 1
            or not isinstance(data['id'], str) or not data['id'].strip()):
        raise ValueError('invalid ADC channel-map header')
    order = data['pod_to_adc']
    if (not isinstance(order, list) or len(order) != 8
            or any(type(ch) is not int for ch in order)
            or set(order) != set(range(1, 9))
            or set(order[:4]) != {1, 2, 3, 4}
            or order[4:] != [5, 6, 7, 8]):
        raise ValueError('ADC map must bijectively preserve reference domains and south order')
    required = {'record_fields': ['map_id', 'map_sha256', 'slot_to_pod',
                'pod_serials', 'cable_serials', 'surveyed_pod_coordinates',
                'stream_epoch', 'impulse_evidence'],
                'impulse_channel_count': 8,
                'reject': ['missing', 'duplicate', 'swapped', 'inverted', 'unstable']}
    if data['capture_requirements'] != required:
        raise ValueError('capture identity requires complete 8/8 impulse and record obligations')
    return order


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate ADC channel-map JSON key: '+key)
        result[key] = value
    return result


CHANNEL_MAP_BYTES = (PROJECT / '03_src/adc_channel_map.json').read_bytes()
CHANNEL_MAP_SHA256 = hashlib.sha256(CHANNEL_MAP_BYTES).hexdigest()
CHANNEL_MAP = json.loads(CHANNEL_MAP_BYTES, object_pairs_hook=_unique_json_object)
POD_TO_ADC = validate_channel_map(CHANNEL_MAP)
ADC_PINS = {leg: [physical[ch-1] for ch in POD_TO_ADC]
            for leg, physical in PHYSICAL_ADC_PINS.items()}
RHO_85_OHM_M = 2.1643958e-8  # retained ADR0015 nominal copper model
HOLE_PLATING_MODEL_MM = .018  # JLC public AVERAGE, never a guaranteed minimum
RESISTANCE_LIMIT_OHM = .5     # Cirrus signal-track guidance, not R_OUT/Ron
DESIGN_RESERVE_FACTOR = 2.0   # project engineering margin, not vendor tolerance


class PathError(RuntimeError):
    pass


def expected_sections():
    rows = {}
    for n in range(1, 9):
        for stage in ('OUTPUT', 'FILTER', 'ADC'):
            members = {}
            for leg in ('P', 'N'):
                positive = leg == 'P'
                if stage == 'OUTPUT':
                    net, start = f'OPA_{leg}{n}', f'U_AFE{n}.{1 if positive else 7}'
                    ends = {'main': f'R_OUT{n}{leg}.1', 'feedback': f'C_FB{n}{leg}.2'}
                elif stage == 'FILTER':
                    net, start = f'FILTER{n}{leg}', f'R_OUT{n}{leg}.2'
                    ends = {'main': f'U_ISO{n}.{1 if positive else 5}',
                            'feedback': f'R_X{n}{leg}.2',
                            'shunt1': f'C_FILTER{n}{leg}1.1',
                            'shunt2': f'C_FILTER{n}{leg}2.1'}
                else:
                    net, start = f'ADC{n}{leg}', f'U_ISO{n}.{2 if positive else 6}'
                    ends = {'main': f'U_ADC.{ADC_PINS[leg][n-1]}',
                            'common_mode': f'C_ADC_CM{n}{leg}.1', 'bias': f'R_ADC_PD{n}{leg}.1'}
                members[leg] = dict(net=net, start=start, ends=ends)
            rows[f'ANALOG_CH{n}_{stage}'] = members
    return rows


def validate_source(groups, route, pins):
    expected = expected_sections()
    selected = {k: v for k, v in groups.items() if k.startswith('ANALOG_CH')}
    if set(selected) != set(expected):
        raise PathError('analog group census must be exactly 24')
    actual_pairs = []
    endpoints, path_count = set(), 0
    for name, members in expected.items():
        decl = selected[name]
        if (decl.get('members') != {leg: [m['net']] for leg, m in members.items()}
                or decl.get('topology') != 'tree' or decl.get('congruent_pads') is not False
                or decl.get('no_vias') is not False or decl.get('max_spread_mm') != 1.0
                or decl.get('router_moves') != 'octilinear' or decl.get('elongation') != 'meander'
                or decl.get('stackup_mm') != [.2104, 1.065, .2104]):
            raise PathError(f'{name}: changed analog matching/stack/via contract')
        for leg, member in members.items():
            net, start, ends = member['net'], member['start'], member['ends']
            paths = [{'id': key, 'segments': [{'net': net, 'from': start, 'to': end}]}
                     for key, end in ends.items()]
            if decl.get('paths', {}).get(leg) != paths:
                raise PathError(f'{name}.{leg}: main/shunt/feedback endpoint paths differ')
            if decl.get('octilinear_endpoints', {}).get(leg) != [start, ends['main']]:
                raise PathError(f'{name}.{leg}: wrong octilinear main endpoints')
            intended = {start, *ends.values()}
            actual = {f'{ref}.{pin}' for (ref, pin), pin_net in pins.items() if pin_net == net}
            if intended != actual:
                raise PathError(f'{name}.{leg}: native pad census/identity differs')
            endpoints.update(intended)
            path_count += len(paths)
        actual_pairs.append([members[leg]['net'] for leg in ('P', 'N')])
    recipe = route.get('stitch', {}).get('endpoint_length_matching', {})
    passes = route.get('stitch', {}).get('passes', [])
    if (recipe != {
            'mechanism': 'canonicalize_chains',
            'groups': sorted(expected),
            'verification': 'copper_length_audit',
            }
            or 'canonicalize_chains' not in passes
            or 'prune_declared_path_offcuts' not in passes
            or passes.index('canonicalize_chains') > passes.index('prune_declared_path_offcuts')):
        raise PathError('analog router matching recipes do not cover exact 24 pairs')
    return dict(status='PASS', groups=24, nets=48, endpoints=len(endpoints), paths=path_count,
                channel_map_id=CHANNEL_MAP['id'], channel_map_sha256=CHANNEL_MAP_SHA256,
                channel_map_source='03_src/adc_channel_map.json', pod_to_adc=POD_TO_ADC,
                capture_requirements=CHANNEL_MAP['capture_requirements'],
                capture_identity_status='OWED',
                slot_to_pod=[POD_TO_ADC.index(ch)+1 for ch in range(1,9)],
                per_section_tolerance_mm=1.0, summed_three_section_main_spread_ceiling_mm=3.0,
                routed_length_status='NOT_GRADED', physical_dcr_status='UNVERIFIED')


def validate_entry_paths(config, route, pins):
    critical.validate_config(config)
    if config['layers'] != ['F.Cu','In1.Cu','In2.Cu','B.Cu'] or config['stackup_mm'] != [.2104,1.065,.2104]:
        raise PathError('entry path copper stack differs from carrier authority')
    expected = {}
    for n in range(1,9):
        for leg, jp, up in [('P',5,3),('N',4,5)]:
            start, clamp, target = f'J{n}.{jp}', f'U_ESD{n}.{up}', f'C_A{n}{leg}.1'
            net = f'AUDIO_{leg}{n}'
            actual = {f'{ref}.{pin}' for (ref,pin), name in pins.items() if name == net}
            if actual != {start, clamp, target}:
                raise PathError(f'{net}: entry/clamp/coupling endpoint census differs')
            expected[(start,clamp)] = (target,net)
    admitted_nets={net for target,net in expected.values()}
    audio_seeds=[x for x in route['prep']['seed_stubs']['stubs']
                 if re.fullmatch(r'AUDIO_[PN][1-8]', x.get('net',''))]
    unknown_audio=[x['net'] for x in route['prep']['seed_stubs']['stubs']
                   if x.get('net','').startswith('AUDIO_')
                   and x['net'] not in admitted_nets|{'AUDIO_EN','AUDIO_CT'}]
    if unknown_audio or len(audio_seeds)!=32 or {x['net'] for x in audio_seeds}!=admitted_nets:
        raise PathError('entry source requires exactly the two named prefix/post banks for sixteen AUDIO nets')
    if route['prep']['seed_stubs']['via'] != {'size':.50,'drill':.20}:
        raise PathError('entry launch via family differs from admitted0.50/0.20mm')
    short = {(x['from'],x['to']):x for x in config['short_paths']}
    prefixes = {(x['from'],x['through']):x for x in config['prefixes']}
    if set(short) != set(expected) or set(prefixes) != set(expected):
        raise PathError('entry protection requires exact 16 prefixes and branch obligations')
    for pair,(target,net) in expected.items():
        row = short[pair]
        positive = net.startswith('AUDIO_P')
        routed, centre = (9.0,8.6) if positive else (7.5,5.7)
        if row['max_length_mm'] != routed or row['max_pad_centre_mm'] != centre or row['layer'] != 'F.Cu' or prefixes[pair]['targets'] != [target]:
            raise PathError(f'{net}: changed protection path limit/layer/target')
        seeds = [x for x in route['prep']['seed_stubs']['stubs'] if x['net'] == net]
        entries = [x for x in seeds if x.get('pin') == pair[0]]
        launches = [x for x in seeds if x.get('pin') == pair[1]]
        if len(seeds) != 2 or len(entries) != 1 or len(launches) != 1:
            raise PathError(f'{net}: missing/duplicate/changed connector prefix or clamp launch seed')
        entry, launch = entries[0], launches[0]
        if entry.get('vias') or entry.get('arcs') or set(entry) != {'net','pin','segments'} or len(entry.get('segments',[])) != 1:
            raise PathError(f'{net}: changed connector prefix seed geometry')
        if set(launch) != {'net','pin','segments','vias'} or len(launch.get('segments',[])) != 1 or len(launch.get('vias',[])) != 1:
            raise PathError(f'{net}: changed post-clamp launch inventory')
        if any(x['layer'] != 'F.Cu' or x['width'] != .20 for seed in seeds for x in seed['segments']):
            raise PathError(f'{net}: connector prefix seed layer/width differs from admitted0.20mm')
        # The exact admitted cell coordinates bind source pad contact; the saved
        # copper checker remains the independent dominance/contact authority.
        n = int(net[7:]); sg = 1 if n < 5 else -1
        jx,jy = (38.+32*(n-1),25.86) if n < 5 else (43.+32*(n-5),114.14)
        def point(q): return [round(jx+sg*q[0],4),round(jy+sg*q[1],4)]
        local = [[4.08,0],[4.08,5.64],[3.2125,6.5075],[3.2125,8.39]] if positive else [[3.06,4],[3.06,4.84],[.9,7],[.9,9.04],[1.25,9.39],[1.7875,9.39]]
        post = [[3.2125,8.39],[4.1,8.39]] if positive else [[1.7875,9.39],[1.7875,10.39]]
        if entry['segments'][0]['pts'] != [point(q) for q in local] or launch['segments'][0]['pts'] != [point(q) for q in post] or launch['vias'] != [point(post[-1])]:
            raise PathError(f'{net}: changed/off-pad connector prefix or post-clamp launch')
    chassis = {f'{ref}.{pin}' for (ref,pin),name in pins.items() if name == 'CHASSIS'}
    if chassis != {f'J{n}.{p}' for n in range(1,9) for p in (9,10)}:
        raise PathError('carrier shell net must contain exactly sixteen RJ45 shield lands')
    pod_power = route['prep']['waves']['groups'].get('pod_power', [])
    if (pod_power.count('CHASSIS') != 1
            or not any(x.get('group') == 'pod_power' and x.get('track_width') == .60
                       for x in route['route']['waves'])):
        raise PathError('CHASSIS lacks its declared outer-layer route owner')
    return {'status':'PASS','prefixes':16,'downstream_paths':16,'shield_pads':16,'realized_copper':'NOT_GRADED'}


def _positive(value, label):
    if not math.isfinite(value) or value <= 0:
        raise PathError(f'{label}: missing/nonpositive/nonfinite geometry')
    return value


def _source_via_geometries(route):
    """Exact final geometry derived from seeds and enabled typed relocations."""
    if route is None:
        return {}
    seed = route['prep']['seed_stubs']
    default = seed['via']
    allowed = {}
    for stub in seed['stubs']:
        geometry = stub.get('via', default)
        for at in stub.get('vias', []):
            key = (stub['net'], int(round(float(at[0])*1000)),
                   int(round(float(at[1])*1000)))
            if key in allowed and allowed[key] != geometry:
                raise PathError(f'{stub["net"]}: conflicting source via geometry at {at}')
            allowed[key] = geometry
    stitch = route.get('stitch') or {}
    def declared(net, spec):
        if not isinstance(spec, dict) or set(spec) != {'at','size','drill','layers'} or spec['layers'] != ['F.Cu','B.Cu']:
            raise PathError('invalid exact source via geometry')
        try:
            values = list(spec['at']) + [spec['size'],spec['drill']]
            if len(values) != 4 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in values):
                raise ValueError()
            x,y,size,drill = values
            if not 0 < drill < size: raise ValueError()
        except (ValueError,TypeError):
            raise PathError('nonfinite or invalid exact source via geometry')
        return (net,round(x*1000),round(y*1000)),dict(size=size,drill=drill)
    if 'relocate_exact_vias' in (stitch.get('passes') or []):
        recipe = stitch.get('relocate_exact_vias')
        if not isinstance(recipe, dict) or set(recipe) != {'edits'} or not isinstance(recipe['edits'], list) or not recipe['edits']:
            raise PathError('invalid exact source via relocation recipe')
        claimed, targets = set(), set()
        for row in recipe['edits']:
            if not isinstance(row,dict) or set(row) != {'net','reason','from','to'} or any(not isinstance(row[k],str) or not row[k].strip() for k in ('net','reason')):
                raise PathError('invalid exact source via relocation row')
            old,old_geometry = declared(row['net'],row['from'])
            new,new_geometry = declared(row['net'],row['to'])
            if old in claimed or new in targets or new in claimed or old in targets:
                raise PathError('overlapping exact source via relocations')
            claimed.add(old);targets.add(new)
            if old == new and old_geometry == new_geometry:
                raise PathError('vacuous exact source via relocation')
            if old not in allowed and old_geometry != dict(size=.5,drill=.2):
                raise PathError('nonordinary relocated via lacks exact source seed geometry')
            if old in allowed and allowed[old] != old_geometry:
                raise PathError('relocated via conflicts with exact source seed geometry')
            if new in allowed and new != old:
                raise PathError('relocated source via target occupied')
            allowed.pop(old,None)
            allowed[new] = new_geometry
    if 'restore_exact_geometry' in (stitch.get('passes') or []):
        recipe = stitch.get('restore_exact_geometry')
        rows = recipe.get('transactions') if isinstance(recipe, dict) else None
        if set(recipe or {}) != {'transactions'} or not isinstance(rows, list) or not rows:
            raise PathError('invalid exact geometry restoration recipe')
        seen = set()
        for row in rows:
            if (not isinstance(row, dict)
                    or set(row) != {'net','reason','via','remove_segments','add_segments'}
                    or not isinstance(row['net'], str) or not row['net'].strip()
                    or not isinstance(row['reason'], str) or not row['reason'].strip()
                    or not isinstance(row['via'], dict)
                    or set(row['via']) != {'from','to'}
                    or not isinstance(row['remove_segments'], list) or not row['remove_segments']
                    or not isinstance(row['add_segments'], list) or not row['add_segments']):
                raise PathError('invalid exact geometry restoration row')
            old,old_geometry = declared(row['net'],row['via']['from'])
            new,new_geometry = declared(row['net'],row['via']['to'])
            if old == new or old in seen or new in seen:
                raise PathError('overlapping exact geometry restoration vias')
            seen.update((old,new))
            # Restoration may consume a compact via synthesized by a late
            # stitch pass, but its final target must already be an exact
            # source-owned seed with identical geometry. It cannot authorize
            # a new fine-via site or silently change barrel dimensions.
            if new not in allowed or allowed[new] != new_geometry:
                raise PathError('exact geometry restoration target is not a matching source seed')
            if old in allowed:
                raise PathError('exact geometry restoration source overlaps a declared source seed')
    return allowed


def inventory_model(text, copper_mm, board_mm, route=None):
    """Conditional track+barrel inventory model; no connectivity/PASS claim."""
    wanted = {m['net'] for pair in expected_sections().values() for m in pair.values()}
    rows = {n: dict(track_ohm=0., via_ohm=0., track_mm=0., segments=0, vias=0) for n in wanted}
    source_vias = _source_via_geometries(route)
    if set(copper_mm) != {'F.Cu', 'B.Cu'}:
        raise PathError('expected explicit outer-copper thicknesses')
    for layer, thickness in copper_mm.items():
        _positive(thickness, layer + ' copper')
    _positive(board_mm, 'board thickness')
    for tag in ('segment', 'arc', 'via', 'zone'):
        for body in length._blocks(text, tag):
            net = length._net(body)
            # Current KiCad 10 named-net dialect is required: no numeric-net
            # fallback that could silently omit the selected signal copper.
            if net and net.startswith('#'):
                raise PathError('numeric-net board dialect is not supported by this adapter')
            if net not in wanted:
                continue
            if tag == 'zone':
                raise PathError(f'{net}: analog pour cannot be priced as a track')
            row = rows[net]
            if tag == 'via':
                drill = re.search(r'\(drill\s+([-\d.eE+]+)\)', body)
                size = re.search(r'\(size\s+([-\d.eE+]+)\)', body)
                layers = re.search(r'\(layers\s+"([^"]+)"\s+"([^"]+)"', body)
                if not drill or not size or not layers or set(layers.groups()) != {'F.Cu', 'B.Cu'}:
                    raise PathError(f'{net}: unpriced via geometry/layers')
                d, diameter = _positive(float(drill[1]), 'drill'), _positive(float(size[1]), 'via size')
                at = length._pt(body, 'at')
                # KiCad may serialize a source coordinate one nanometre below
                # its decimal spelling. Bind identity on the same 1 um graph
                # lattice used by the independent endpoint-path audit.
                source = source_vias.get((net, int(round(at[0]*1000)),
                                          int(round(at[1]*1000)))) if at else None
                ordinary = abs(d-.2) <= 1e-9 and abs(diameter-.5) <= 1e-9
                exact_seed = (source is not None
                              and abs(d-float(source['drill'])) <= 1e-9
                              and abs(diameter-float(source['size'])) <= 1e-9)
                if not (ordinary or exact_seed):
                    raise PathError(f'{net}: via differs from ordinary 0.50/0.20 mm and exact source seed geometry')
                # Thin-wall approximation pi*d*t is smaller than exact annulus
                # area, hence charges slightly more at the SAME assumed t.
                row['via_ohm'] += RHO_85_OHM_M * board_mm * 1000 / (math.pi*d*HOLE_PLATING_MODEL_MM)
                row['vias'] += 1
                continue
            width = re.search(r'\(width\s+([-\d.eE+]+)\)', body)
            layer = re.search(r'\(layer\s+"([^"]+)"', body)
            a, b = length._pt(body, 'start'), length._pt(body, 'end')
            if not width or not layer or layer[1] not in copper_mm or a is None or b is None:
                raise PathError(f'{net}: unpriced track geometry/layer')
            w = _positive(float(width[1]), 'track width')
            # The two exact ADC pin-field rule areas deliberately admit the
            # advanced-prototype 0.15 mm floor. Native DRC owns containment:
            # the same width outside those bounded areas still violates the
            # global 0.20 mm ANALOG_AUDIO rule. Price the actual narrower
            # copper here rather than pretending every analog segment is
            # 0.20 mm, while retaining 0.20 mm for OPA/FILTER copper.
            floor = .15 if re.fullmatch(r'ADC[1-8][PN]', net) else .2
            if w < floor-1e-9:
                raise PathError(f'{net}: analog track below {floor:.2f} mm')
            if tag == 'arc':
                mid = length._pt(body, 'mid')
                if mid is None:
                    raise PathError(f'{net}: missing arc midpoint')
                ln = length.arc_len(a, mid, b)
            else:
                ln = math.dist(a, b)
            _positive(ln, net + ' track length')
            row['track_ohm'] += RHO_85_OHM_M * ln * 1000 / (w*copper_mm[layer[1]])
            row['track_mm'] += ln
            row['segments'] += 1
    missing = sorted(n for n, row in rows.items() if row['segments'] == 0)
    if missing:
        raise PathError('unmeasured analog nets: ' + ', '.join(missing))
    legs = []
    for n in range(1, 9):
        for leg in ('P', 'N'):
            chain = [f'OPA_{leg}{n}', f'FILTER{n}{leg}', f'ADC{n}{leg}']
            r = sum(rows[net]['track_ohm'] + rows[net]['via_ohm'] for net in chain)
            legs.append(dict(channel=n, leg=leg, nets=chain, inventory_model_ohm=r,
                             reserve_charged_ohm=r*DESIGN_RESERVE_FACTOR,
                             within_design_screen=r*DESIGN_RESERVE_FACTOR < RESISTANCE_LIMIT_OHM))
    return dict(nets=rows, legs=legs, copper_mm=copper_mm, barrel_height_model_mm=board_mm,
                rho_ohm_m_at85C=RHO_85_OHM_M, hole_plating_model_mm=HOLE_PLATING_MODEL_MM,
                hole_plating_basis='public average, not minimum', reserve_factor=DESIGN_RESERVE_FACTOR,
                signal_track_limit_ohm=RESISTANCE_LIMIT_OHM, physical_dcr_status='UNVERIFIED',
                excluded=['pad spreading', 'solder joints', '10 ohm series resistors', 'switch Ron'],
                model_status='PASS' if all(r['within_design_screen'] for r in legs) else 'FAIL')


def emit_report(report, output):
    """Persist full evidence while keeping bounded-runner stdout compact."""
    rendered = json.dumps(report, indent=2) + '\n'
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered)
        summary = [f"ANALOG-PATHS {report.get('status', 'INCOMPLETE')}"]
        board_sha = report.get('board_sha256')
        if board_sha:
            summary.append(f"board_sha256={board_sha}")
        measured = (report.get('length') or {}).get('n_electrical_measured')
        declared = (report.get('length') or {}).get('n_electrical_declared')
        if measured is not None and declared is not None:
            summary.append(f"paths={measured}/{declared}")
        if report.get('error'):
            summary.append(f"error={report['error']}")
        summary.append(f"receipt={output}")
        print(' '.join(summary))
    else:
        print(rendered, end='')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--source-only', action='store_true')
    mode.add_argument('--board', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = dict(status='INCOMPLETE', physical_dcr_status='UNVERIFIED')
    rc = 2
    try:
        floor = yaml.safe_load((PROJECT/'03_src/floorplan.yaml').read_text())
        route = yaml.safe_load((PROJECT/'03_src/route.yaml').read_text())
        groups, _ = length.load_groups(PROJECT)
        _, pins, _ = parse_netlist(PROJECT/floor['project']['netlist'])
        report['source'] = validate_source(groups, route, pins)
        entry_config = critical.load_config(PROJECT/'03_src/rules/critical_paths.yaml')
        report['entry_source'] = validate_entry_paths(entry_config, route, pins)
        report['input_sha256'] = {p: hashlib.sha256((PROJECT/p).read_bytes()).hexdigest()
                                  for p in ['03_src/floorplan.yaml', '03_src/route.yaml', '03_src/rules/nets.yaml', '03_src/check_analog_paths.py', '03_src/rules/critical_paths.yaml', floor['project']['netlist']]}
        report['critical_path_checker_sha256'] = hashlib.sha256(Path(critical.__file__).read_bytes()).hexdigest()
        if args.source_only:
            report.update(status='PASS', scope='source contract only; no saved copper measured')
            rc = 0
        else:
            board_bytes = args.board.read_bytes()
            report['board_sha256'] = hashlib.sha256(board_bytes).hexdigest()
            report['entry_copper'] = critical.audit(args.board, entry_config)
            if report['entry_copper']['verdict'] != 'PASS':
                raise PathError('saved entry-clamp path or branch dominance failed')
            result = length.grade(PROJECT, args.board)
            report['length'] = result
            if result['fails'] or result['unreached'] or result['n_electrical_measured'] != result['n_electrical_declared']:
                raise PathError('saved endpoint-path length/connectivity acceptance not reached')
            stack = floor['board']['stackup']
            foil = stack['copper_thickness_mm']
            if len(foil) != floor['board']['layers']:
                raise PathError('source copper layer count differs from stack')
            copper = {'F.Cu': foil[0], 'B.Cu': foil[-1]}
            report['resistance'] = inventory_model(board_bytes.decode('utf-8-sig'), copper, stack['nominal_thickness_mm'], route)
            if args.board.read_bytes() != board_bytes:
                raise PathError('board changed during the read-only audit')
            report.update(status=report['resistance']['model_status'], scope='saved path matching and conditional copper model; not physical DCR')
            rc = 0 if report['status'] == 'PASS' else 1
    except (PathError, critical.AuditError, length.AuditError, OSError, KeyError, ValueError) as exc:
        report.update(status='INCOMPLETE', error=str(exc))
    emit_report(report, args.output)
    return rc


if __name__ == '__main__':
    raise SystemExit(main())
