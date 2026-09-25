#!/usr/bin/env python3
"""Reproduce the hash-bound, research-only XU reset region audit."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ROOT = PROJECT.parents[1]
BOARD = Path('/tmp/crow-xu-qspi-gap-sol/project/04_kicad/crow_carrier.kicad_pcb')
FLOORPLAN = PROJECT / '01_docs/research/xu_service_variant/p1_qspi_packet/floorplan_qspi_gap.yaml'
SOURCE = PROJECT / '03_src/rules/p1_corridor_requirements.yaml'
INTERFACES = PROJECT / '03_src/modular_plan.json'
ALIASES = PROJECT / '02_parts/USB4215-03-A/part.yaml'
BASE_CONTRACT = PROJECT / '01_docs/research/xu_service_variant/p1_qspi_packet/coarse_contract.json'
CHECKER = ROOT / 'skills/kicad-pcb/scripts/p1_corridor_capacity.py'
PINNED = {
    BOARD: 'fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27',
    FLOORPLAN: 'cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925',
    SOURCE: '9ef85e5f4918dea0378203a97fa631ce2e73a690170235902a97a6c8e30527d8',
    INTERFACES: '7201aa55cffefca99f9f27e92711cbbcf28387432523a8c960b5cd71e973170e',
    ALIASES: 'a6baba8bd4e389c146250a2a2ef5f7e9b09f63526e71dbdd05be8bca9b7b2c2e',
}
PROPOSED_FLOORPLAN_SHA = '3b8383139c6f2ae8d8e4e37bf1c666ed89778c097b7c1c39e041544bb61feb20'
PROPOSED_CONTRACT_SHA = '1124f32bd78005ef0bc73ab51f62dfddd2395726207bf186456da9a1a109e370'


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_checker():
    spec = importlib.util.spec_from_file_location('p1_corridor_capacity', CHECKER)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    for path, expected in PINNED.items():
        if sha(path) != expected:
            raise SystemExit(f'pin drift: {path}')
    checker = load_checker()
    floorplan = yaml.safe_load(FLOORPLAN.read_text())
    regions = floorplan['placement']['regions']
    regions['audio_clock_tdm'] = [145.0, 72.0, 190.0, 99.84]
    regions['digital_power'] = [145.0, 99.84, 185.0, 134.0]
    source = yaml.safe_load(SOURCE.read_text())
    interfaces = json.loads(INTERFACES.read_text())
    with tempfile.TemporaryDirectory(prefix='crow-reset-region-') as temporary:
        work = Path(temporary)
        derived_floorplan = work / 'floorplan.yaml'
        derived_floorplan.write_text(yaml.safe_dump(floorplan, sort_keys=False))
        if sha(derived_floorplan) != PROPOSED_FLOORPLAN_SHA:
            raise SystemExit('derived floorplan hash drift')
        contract = json.loads(BASE_CONTRACT.read_text())
        for name, path in {'board': BOARD, 'source': SOURCE, 'interfaces': INTERFACES,
                           'aliases': ALIASES, 'floorplan': derived_floorplan}.items():
            contract[name + '_sha256'] = sha(path)
        derived_contract = work / 'contract.json'
        derived_contract.write_text(json.dumps(contract, indent=2) + '\n')
        if sha(derived_contract) != PROPOSED_CONTRACT_SHA:
            raise SystemExit('derived contract hash drift')
        board = checker.pcbnew.LoadBoard(str(BOARD))
        patterns = {row['region']: row['match'] for row in floorplan['placement']['patterns']
                    if row.get('region') in {'audio_clock_tdm', 'digital_power'}}
        escapes = {}
        for owner, refs in patterns.items():
            escaped = []
            for ref in refs:
                footprint = board.FindFootprintByReference(ref)
                shapes = [('envelope', checker._physical_envelope(footprint))]
                shapes += [(f'pad.{pad.GetNumber()}', checker.box_mm(pad.GetBoundingBox()))
                           for pad in footprint.Pads()]
                escaped += [{'ref': ref, 'geometry': kind, 'bbox': list(box)}
                            for kind, box in shapes
                            if not checker.contains(tuple(regions[owner]), box)]
            escapes[owner] = escaped
        reset_pads = []
        for footprint in board.GetFootprints():
            if footprint.GetReference() not in {'R_XU_RST_PU', 'U_CORE_OK', 'U_XU_3V3_OK'}:
                continue
            for pad in footprint.Pads():
                if pad.GetNetname() == 'XU_RESET_N':
                    box = checker.box_mm(pad.GetBoundingBox())
                    reset_pads.append({'native_pad': footprint.GetReference() + '.' + pad.GetNumber(),
                                       'bbox': [round(value, 3) for value in box],
                                       'inside_digital_power': checker.contains(tuple(regions['digital_power']), box),
                                       'intersects_audio_clock_tdm': checker.intersects(tuple(regions['audio_clock_tdm']), box)})
        coverage, terminals = checker.graph.source_inventory(source, interfaces)
        result = checker.evaluate_coarse(
            BOARD, derived_contract, sha(derived_contract), source_path=SOURCE,
            interface_path=INTERFACES, alias_path=ALIASES, floorplan_path=derived_floorplan,
            expected_source_sha256=sha(SOURCE), expected_interface_sha256=sha(INTERFACES),
            expected_alias_sha256=sha(ALIASES), expected_floorplan_sha256=sha(derived_floorplan))
    audit = {
        'status': 'PASS_RESEARCH_ONLY', 'p1_accepted': False, 'routing_realized': False,
        'board_sha256': sha(BOARD), 'floorplan_sha256': PROPOSED_FLOORPLAN_SHA,
        'coverage_net_count': len(terminals), 'coverage_denominator_preserved': len(terminals) == 59,
        'audio_digital_interior_overlap': checker.intersects(tuple(regions['audio_clock_tdm']), tuple(regions['digital_power'])),
        'owner_envelope_or_pad_escape': escapes, 'digital_xu_reset_pads': sorted(reset_pads, key=lambda row: row['native_pad']),
        'checker_status': result['status'], 'checker_errors': result['errors'],
        'xmos_service_escape': next(row for row in result['allocations'] if row['id'] == 'xmos_service_escape'),
    }
    assert not audit['audio_digital_interior_overlap'] and not any(escapes.values())
    assert all(row['inside_digital_power'] and not row['intersects_audio_clock_tdm'] for row in reset_pads)
    assert audit['coverage_denominator_preserved']
    assert audit['checker_status'] == 'FAIL' and audit['checker_errors'] == []
    print(json.dumps(audit, indent=2))


if __name__ == '__main__':
    main()
