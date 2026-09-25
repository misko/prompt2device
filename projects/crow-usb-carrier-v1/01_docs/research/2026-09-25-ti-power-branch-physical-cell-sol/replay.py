#!/usr/bin/env python3
"""Reproduce remote-XU-cell power branch accounting without P1 credit."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT/'projects/crow-usb-carrier-v1'
TERRA = PROJECT/'01_docs/research/2026-09-25-unified-power-boundary-replay-terra'
CHECKER = ROOT/'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
EXPECTED_BOARD = 'd0c065dc16de081a5410b7a22e474f0a99c6fdeb0b7dd1f6c37422ace4a9fcf7'
EXPECTED_CHECKER = 'b4ece816b23bcc1f213a6e66253d4aa2dfe1a1358a5a74aaaea40fd8a36bab95'
EXPECTED_TERRA_BUILDER = '62ae4e1af284b8ab68f89d4e4e505fdd252fe7bb65009ce0a3c513cb8b3dc246'
EXPECTED_TERRA_BASE = 'cafefe406881f8a80e3de22997fdc49ef680f827a264983698889869e57cb363'
REMOTE = {'C_XU_VDDIO_35.1', 'C_XU_VDDIO_56.1', 'C_XU_USB33.1'}
NETS = ('N1V8', 'N3V3X', 'N3V3_ADC', 'N5V_BUCK')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sys.path.insert(0, str(TERRA))
    import build_one_pad_shared_port_overlay as base
    import build_power_unresolved_branch_overlay as terra
    if (sha(terra.BOARD) != EXPECTED_BOARD or sha(CHECKER) != EXPECTED_CHECKER or
            sha(TERRA/'build_power_unresolved_branch_overlay.py') != EXPECTED_TERRA_BUILDER or
            sha(TERRA/'build_one_pad_shared_port_overlay.py') != EXPECTED_TERRA_BASE):
        raise SystemExit('native board/checker/builder SHA drift')
    base.EXPECTED['checker'] = EXPECTED_CHECKER
    spec = importlib.util.spec_from_file_location('cell_power_checker', CHECKER)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    with tempfile.TemporaryDirectory(prefix='crow-power-cell-') as tmp:
        output = Path(tmp)/'overlay'
        old_argv = sys.argv
        sys.argv = ['build_power_unresolved_branch_overlay.py', '--output', str(output)]
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                terra.main()
        finally:
            sys.argv = old_argv
        req_path, floor_path = output/'p1_requirements.yaml', output/'floorplan.yaml'
        iface_path, contract_path = output/'modular_plan.json', output/'coarse.json'
        source = yaml.safe_load(req_path.read_text())
        floor = yaml.safe_load(floor_path.read_text())
        interfaces = json.loads(iface_path.read_text())
        contract = json.loads(contract_path.read_text())
        board = pcbnew.LoadBoard(str(terra.BOARD))
        _, pads = checker.graph.board_index(board)
        regions = floor['placement']['regions']
        patterns = floor['placement']['patterns']
        outline = pcbnew.SHAPE_POLY_SET()
        if not board.GetBoardPolygonOutlines(outline, False):
            raise SystemExit('native outline unavailable')
        cells = checker._physical_cells(source, interfaces, board, outline, regions, patterns)
        if cells['xmos_core_east']['owner_block'] != 'xmos_core':
            raise SystemExit('remote XU physical owner drift')
        power = [row for row in source['unresolved_multiterminal_branches']
                 if row['allocation_id'] == 'power_boundary_windows']
        if tuple(row['net'] for row in power) != NETS or sum(row['terminal_count'] for row in power) != 171:
            raise SystemExit('exact 171-terminal power denominator drift')
        tagged = []
        for row in power:
            for entry in row['endpoints']:
                native = entry['native_pad']
                if native in REMOTE:
                    if entry['block'] != 'xmos_core':
                        raise SystemExit(f'{native}: modular owner drift')
                    entry['physical_cell_id'] = 'xmos_core_east'
                    tagged.append(native)
            # A same-owner physical cell is not a foreign electrical owner.
            row['physical_blockers'] = [
                {**blocker, 'foreign_regions': [name for name in blocker['foreign_regions']
                    if name not in cells or cells[name]['owner_block'] != blocker['block']]}
                for blocker in row['physical_blockers']]
            row['physical_blockers'] = [b for b in row['physical_blockers']
                                        if b['foreign_regions']]
        if set(tagged) != REMOTE or len(tagged) != 3:
            raise SystemExit('remote physical-cell endpoint denominator drift')
        aliases = checker.graph.alias_inventory(yaml.safe_load(terra.ALIASES.read_text()))
        coverage, _ = checker.graph.source_inventory(source, interfaces)
        isolated = {}
        for row in power:
            one = {'unresolved_multiterminal_branches':[row]}
            try:
                checker._unresolved_branches(one, interfaces, board, regions, coverage,
                                             aliases, pads, cells, patterns)
            except checker.ContractError as exc:
                isolated[row['net']] = {'accepted':False, 'reason':str(exc)}
            else:
                isolated[row['net']] = {'accepted':True, 'reason':None}
        if (not isolated['N1V8']['accepted'] or not isolated['N3V3X']['accepted'] or
                isolated['N3V3_ADC']['accepted'] or isolated['N5V_BUCK']['accepted']):
            raise SystemExit('isolated power branch classification drift')
        req_path.write_text(yaml.safe_dump(source, sort_keys=False))
        contract.update(board_sha256=sha(terra.BOARD), source_sha256=sha(req_path),
                        floorplan_sha256=sha(floor_path),
                        interfaces_sha256=sha(iface_path), aliases_sha256=sha(terra.ALIASES))
        contract_path.write_text(json.dumps(contract, indent=2)+'\n')
        result = checker.evaluate_coarse(
            terra.BOARD, contract_path, sha(contract_path), source_path=req_path,
            interface_path=iface_path, alias_path=terra.ALIASES,
            floorplan_path=floor_path, expected_source_sha256=sha(req_path),
            expected_interface_sha256=sha(iface_path),
            expected_alias_sha256=sha(terra.ALIASES),
            expected_floorplan_sha256=sha(floor_path), diagnose_all=True)
        if (result['p1_accepted'] or result['routing_realized'] or result['status'] != 'FAIL'
                or not any('branch pad outside source owner region' in x
                           for x in result['errors'])):
            raise SystemExit('unexpected full checker outcome')
        receipt = {'status':result['status'], 'p1_accepted':False,
                   'routing_realized':False, 'board_sha256':sha(terra.BOARD),
                   'base_source_sha256':base.EXPECTED['requirements'],
                   'base_contract_sha256':base.EXPECTED['contract'],
                   'checker_sha256':sha(CHECKER), 'overlay_source_sha256':sha(req_path),
                   'overlay_contract_sha256':sha(contract_path),
                   'tagged_remote_pads':sorted(tagged),
                   'power_terminal_count':171, 'isolated':isolated,
                   'first_full_error':result['errors'][0],
                   'global_error_count':len(result['errors'])}
        (HERE/'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
        print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
