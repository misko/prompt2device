#!/usr/bin/env python3
"""Exact no-credit four-crossing timing replay on the unified TI board."""
from __future__ import annotations

import hashlib
import importlib.util
import json
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
BASE = PROJECT/'01_docs/research/2026-09-25-ti-unified-p1-diagnostic-sol'
BOARD = PROJECT/'01_docs/research/2026-09-25-ti-vmid-coupled-ch8-sol/candidate.kicad_pcb'
ALIASES = PROJECT/'02_parts/USB4215-03-A/part.yaml'
CHECKER = ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
NETS = ('AUDIO_MCLK_1V8', 'TDM_BCLK_1V8', 'TDM_DATA_1V8', 'TDM_FSYNC_1V8')
EXPECTED = {
    'board':'d0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7',
    'source':'f6f132891712bfcb1cec4d1df6714748337040ba5c42ae3fecd14fb9c35d1222',
    'contract':'18936dc3f3dd6e01637182b2dab57cb472a31bfa2eb345a20bd4f7867708777f',
    'floorplan':'7d95376bbfa3bc9dd0bf59bc7e91d02d86c31235f6145f4d09b49a31f81769d0',
    'interfaces':'02be5ad6ea879ac04d5dfd9e2e09d5226f85c85fa83d72628aa40cf93de6b4d8',
    'aliases':'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    inputs = {'board':BOARD, 'source':BASE/'p1_requirements.yaml',
              'contract':BASE/'coarse.json', 'floorplan':BASE/'floorplan.yaml',
              'interfaces':BASE/'modular_plan.json', 'aliases':ALIASES}
    for name, path in inputs.items():
        if sha(path) != EXPECTED[name]:
            raise SystemExit(f'{name}: exact unified input SHA drift')
    spec = importlib.util.spec_from_file_location('two_terminal_p1_checker', CHECKER)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    source = yaml.safe_load(inputs['source'].read_text())
    contract = json.loads(inputs['contract'].read_text())
    floor = yaml.safe_load(inputs['floorplan'].read_text())
    interfaces = json.loads(inputs['interfaces'].read_text())
    aliases = helper.graph.alias_inventory(yaml.safe_load(ALIASES.read_text()))
    board = pcbnew.LoadBoard(str(BOARD))
    _, pads = helper.graph.board_index(board)
    allocation = next(row for row in contract['allocations']
                      if row['id'] == 'adc_timing_xmos_bundle')
    if (len(allocation['boundary_witnesses']) != 9 or
            len(allocation['reservations']) != 9 or
            source.get('unresolved_two_terminal_crossings') is not None):
        raise SystemExit('base timing allocation/source schema drift')
    by_net = {row['net']:row for row in interfaces['interfaces']}
    src_alloc = next(row for row in source['allocations']
                     if row['id'] == 'adc_timing_xmos_bundle')
    source['unresolved_two_terminal_crossings'] = []
    for net in NETS:
        owner_pads = by_net[net]['endpoints']
        if src_alloc['endpoints'][net] != owner_pads:
            raise SystemExit(f'{net}: source/modular denominator drift')
        entries = sorted([{'source_pad':source_pad,
                           'native_pad':helper.graph.native_identity(source_pad, aliases),
                           'net':net, 'block':block}
                          for block, names in owner_pads.items() for source_pad in names],
                         key=lambda e:e['source_pad'])
        if len(entries) != 2 or {e['block'] for e in entries} != {
                'audio_clock_tdm','xmos_core'}:
            raise SystemExit(f'{net}: two-owner terminal denominator drift')
        native_on_net = [fp.GetReference()+'.'+pad.GetNumber()
                         for fp in board.GetFootprints() for pad in fp.Pads()
                         if pad.GetNetname() == net]
        if len(native_on_net) != 2 or set(native_on_net) != {e['native_pad'] for e in entries}:
            raise SystemExit(f'{net}: exact native terminal census drift')
        for entry in entries:
            native = pads.get(entry['native_pad'], [])
            if len(native) != 1 or not native[0].IsOnLayer(pcbnew.F_Cu):
                raise SystemExit(f"{entry['native_pad']}: exact native F.Cu identity drift")
        ident, reserve = f'timing_{net.lower()}_unplaced_connection', f'timing_{net.lower()}_connection'
        duties = [{'status':'P2_REQUIRED', **entry, 'branch_id':ident,
                   'layer':'F.Cu', 'proof':'native_pad_to_unplaced_tree'}
                  for entry in entries]
        row = {'id':ident, 'owner':'board_integration',
               'allocation_id':'adc_timing_xmos_bundle', 'net':net,
               'layer':'F.Cu', 'reference_layer':'In1.Cu', 'reservation_id':reserve,
               'endpoints':entries, 'terminal_count':2, 'minimum_tree_edges':1,
               'physical_blockers':[], 'capacity_slots':None,
               'p2_obligations':duties,
               'tree_obligation':{'status':'P3_REQUIRED','net':net,
                                  'terminal_count':2,'minimum_tree_edges':1,
                                  'proof':'one_connected_native_net_without_unrelated_branches'},
               'return_obligation':{'status':'P2_REQUIRED','net':'GND',
                                    'branch_id':ident,'reference_layer':'In1.Cu',
                                    'proof':'continuous_filled_reference_under_actual_tree'}}
        source['unresolved_two_terminal_crossings'].append(row)
        rep = entries[0]
        box = helper.box_mm(pads[rep['native_pad']][0].GetBoundingBox())
        allocation['boundary_witnesses'].append({
            'kind':'unresolved_two_terminal_crossing', 'branch_id':ident,
            'source':rep['source_pad'], 'native':rep['native_pad'],
            'net':net, 'block':rep['block'], 'layer':'F.Cu', 'face':'north',
            'boundary_bbox':list(box), 'reservation_id':reserve,
            'p2_obligation':duties[0]})
        allocation['reservations'].append({
            'id':reserve, 'kind':'unresolved_two_terminal_crossing',
            'branch_id':ident, 'layer':'F.Cu', 'nets':[net]})
    req, floor_path, iface_path, coarse = (HERE/'p1_requirements.yaml',
        HERE/'floorplan.yaml', HERE/'modular_plan.json', HERE/'coarse.json')
    req.write_text(yaml.safe_dump(source, sort_keys=False))
    floor_path.write_bytes(inputs['floorplan'].read_bytes())
    iface_path.write_bytes(inputs['interfaces'].read_bytes())
    contract.update(board_sha256=sha(BOARD), source_sha256=sha(req),
                    floorplan_sha256=sha(floor_path))
    coarse.write_text(json.dumps(contract, indent=2)+'\n')
    coverage, _ = helper.graph.source_inventory(source, interfaces)
    declared = helper._unresolved_branches(source, interfaces, board,
        floor['placement']['regions'], coverage, aliases, pads)
    if not all(row['id'] in declared and declared[row['id']]['_kind'] ==
               'unresolved_two_terminal_crossing'
               for row in source['unresolved_two_terminal_crossings']):
        raise SystemExit('exact two-terminal source validation drift')
    result = helper.evaluate_coarse(BOARD, coarse, sha(coarse), source_path=req,
        interface_path=iface_path, alias_path=ALIASES, floorplan_path=floor_path,
        expected_source_sha256=sha(req), expected_interface_sha256=sha(iface_path),
        expected_alias_sha256=sha(ALIASES), expected_floorplan_sha256=sha(floor_path),
        diagnose_all=True)
    (HERE/'result.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    timing = next(row for row in result['allocations']
                  if row['id'] == 'adc_timing_xmos_bundle')
    if (result['status'] != 'FAIL' or result['p1_accepted'] or result['routing_realized'] or
            timing['status'] != 'FAIL' or
            timing.get('reason') != 'adc_timing_xmos_bundle: missing per-net boundary witness' or
            len(result['errors']) != 13 or
            any('unresolved branch representative witness denominator mismatch' not in e
                for e in result['errors'])):
        raise SystemExit('expected remaining AUDIO_EN fail-closed outcome drift')
    print(json.dumps({'status':result['status'], 'p1_accepted':False,
                      'two_terminal_nets':list(NETS), 'timing_reason':timing['reason'],
                      'global_errors':len(result['errors']),
                      'source_sha256':sha(req), 'contract_sha256':sha(coarse)}, indent=2))


if __name__ == '__main__':
    main()
