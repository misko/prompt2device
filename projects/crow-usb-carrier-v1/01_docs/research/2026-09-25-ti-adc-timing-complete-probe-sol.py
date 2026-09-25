#!/usr/bin/env python3
"""Research-only exact TI ADC timing endpoint census and negative lane screen."""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / 'projects/crow-usb-carrier-v1'
PACKET = PROJECT / '06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project'
BOARD = PACKET / '04_kicad/crow_carrier.kicad_pcb'
SOURCE = PACKET / '03_src/rules/p1_corridor_requirements.yaml'
INTERFACES = PACKET / '03_src/modular_plan.json'
EXPECTED_BOARD_SHA = '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10'
EXPECTED_SOURCE_SHA = '191e5580a6ddf56bc9670aff3593c9e9a02d91e75c0c79998b500955050e82a3'
EXPECTED_INTERFACES_SHA = '75c3a517cea50dd6b5745fae96b051d334debd48aac143becaca3d5fe3fc35dc'
NETS = (
    'ADC_BCLK', 'ADC_FSYNC', 'ADC_DOUT1', 'AUDIO_MCLK_1V8',
    'TDM_BCLK_1V8', 'TDM_DATA_1V8', 'TDM_FSYNC_1V8', 'ADC_I2C_SCL',
    'ADC_I2C_SDA', 'ADC_READY', 'AUDIO_EN', 'XU_I2C_SCL_1V8',
    'XU_I2C_SDA_1V8', 'ADC_DIGITAL_BAD',
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authoritative_members(allocation, interfaces):
    """Fail on one missing/extra owner or terminal, including ADC B branches."""
    if allocation.get('coverage_nets') != list(NETS):
        raise ValueError('14-net allocation coverage/order differs from source authority')
    rows = {row['net']: row['endpoints'] for row in interfaces['interfaces']
            if row.get('net') in NETS}
    if set(rows) != set(NETS) or set(allocation.get('endpoints', {})) != set(NETS):
        raise ValueError('14-net interface denominator mismatch')
    for net in NETS:
        owners = allocation['endpoints'][net]
        if owners != rows[net]:
            raise ValueError(f'{net}: source endpoints differ from modular interface')
    count = sum(len(members) for net in NETS
                for members in rows[net].values())
    if count != 54:
        raise ValueError(f'ADC timing endpoint denominator {count} != 54')
    return rows


def native_terminals(board, rows):
    fps = {fp.GetReference(): fp for fp in board.GetFootprints()}
    if len(fps) != len(list(board.GetFootprints())):
        raise ValueError('duplicate native footprint reference')
    result = []
    for net in NETS:
        for owner, members in rows[net].items():
            for member in members:
                ref, number = member.rsplit('.', 1)
                fp = fps.get(ref)
                pads = [] if fp is None else [p for p in fp.Pads() if p.GetNumber() == number]
                if len(pads) != 1 or pads[0].GetNetname() != net or not pads[0].IsOnLayer(pcbnew.F_Cu):
                    raise ValueError(f'{member}: missing, ambiguous, wrong net, or absent from F.Cu')
                pad = pads[0]
                pos = pad.GetPosition()
                result.append({'net': net, 'owner': owner, 'source': member,
                               'native': member, 'layer': 'F.Cu',
                               'center_mm': [round(pcbnew.ToMM(pos.x), 6),
                                             round(pcbnew.ToMM(pos.y), 6)]})
    if len({r['native'] for r in result}) != 54:
        raise ValueError('ADC timing native endpoint identities are not unique')
    return result


def screen_lanes(board):
    path = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
    spec = importlib.util.spec_from_file_location('p1_capacity', path)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    tests = [
        ('adc_to_tdm_broad', [140.0, 92.5, 174.35, 111.0], 3),
        ('tdm_to_xu_west', [182.475, 94.0, 199.825, 100.0], 4),
    ]
    output = []
    obstacles = checker.layer_obstacles(board, 'F.Cu', set())
    for name, bbox, demand in tests:
        # Include every physical body/pad, including named endpoint components.
        measured = checker.connected_capacity(bbox, obstacles, 'horizontal', 0.45)
        minimum = min(measured['cross_sections'],
                      key=lambda section: section['reachable_width_mm'])
        x = minimum['at_mm']
        blockers = [(ref, box) for ref, box in obstacles
                    if box[0] < x < box[2] and checker.intersects(bbox, box)]
        free = checker.free_intervals(bbox[1], bbox[3],
                                      [(box[1], box[3]) for _, box in blockers])
        output.append({'id': name, 'bbox_mm': bbox, 'demand_slots': demand,
                       'raw_connected_width_mm': measured['connected_width_mm'],
                       'raw_capacity_slots': measured['capacity_slots'],
                       'status': 'FAIL' if measured['capacity_slots'] < demand else 'INCOMPLETE',
                       'foreign_obstacles': measured['foreign_obstacles'],
                       'minimum_cross_section': {
                           'x_mm': x,
                           'reachable_width_mm': minimum['reachable_width_mm'],
                           'blockers': [{'ref': ref, 'bbox_mm': box} for ref, box in blockers],
                           'free_y_intervals_mm': free}})
    return output, digest(path)


def main():
    if digest(BOARD) != EXPECTED_BOARD_SHA:
        raise SystemExit('exact TI diagnostic board SHA mismatch')
    if digest(SOURCE) != EXPECTED_SOURCE_SHA or digest(INTERFACES) != EXPECTED_INTERFACES_SHA:
        raise SystemExit('exact TI source packet SHA mismatch')
    source = yaml.safe_load(SOURCE.read_text())
    allocation = next(row for row in source['allocations']
                      if row['id'] == 'adc_timing_xmos_bundle')
    interfaces = json.loads(INTERFACES.read_text())
    rows = authoritative_members(allocation, interfaces)
    # Red self-check: dropping the second ADC's BCLK source terminal must fail.
    damaged = copy.deepcopy(allocation)
    damaged['endpoints']['ADC_BCLK']['adc_reference'].remove('U_ADC_B.22')
    try:
        authoritative_members(damaged, interfaces)
    except ValueError:
        red_missing_adc_b_rejected = True
    else:
        raise SystemExit('missing ADC B endpoint was accepted')
    board = pcbnew.LoadBoard(str(BOARD))
    terminals = native_terminals(board, rows)
    zones = [{'net': z.GetNetname(), 'filled': z.IsFilled(),
              'rule_area': z.GetIsRuleArea(),
              'layers': [board.GetLayerName(i) for i in z.GetLayerSet().Seq()]}
             for z in board.Zones()]
    lanes, checker_sha = screen_lanes(board)
    report = {'schema': 1, 'kind': 'ti-adc-timing-complete-endpoint-research',
              'status': 'INCOMPLETE', 'routing_realized': False, 'p1_accepted': False,
              'hashes': {'board': digest(BOARD), 'source': digest(SOURCE),
                         'modular_plan': digest(INTERFACES),
                         'capacity_checker': checker_sha},
              'coverage_nets': list(NETS), 'net_count': len(NETS),
              'endpoint_count': len(terminals), 'terminals': terminals,
              'red_missing_adc_b_rejected': red_missing_adc_b_rejected,
              'lane_screens': lanes, 'zones': zones,
              'reason': '54/54 native endpoints verified, but no complete 14-net physical reservation/branch graph or GND return proof'}
    output = Path(sys.argv[1]) if len(sys.argv) == 2 else None
    encoded = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if output:
        output.write_text(encoded)
    else:
        print(encoded, end='')


if __name__ == '__main__':
    main()
