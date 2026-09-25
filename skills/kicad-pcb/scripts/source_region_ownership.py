#!/usr/bin/env python3
"""Census native occupants of explicitly exclusive source physical cells.

Only ``physical_cells`` in the P1 source opts a region into exclusive
ownership. Ordinary floorplan planning regions are never treated as cells.
This pre-routing check grants no P1, placement, outline, or connector credit.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import yaml

try:
    import pcbnew
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew

from p1_corridor_capacity import _physical_envelope, box_mm, contains, intersects, rectangle


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _occupancy(cell: str, area: tuple, refs: set[str], native: dict) -> list[dict]:
    findings = []
    for ref in sorted(refs):
        if ref not in native:
            findings.append({'cell': cell, 'kind': 'owned_missing', 'ref': ref})
            continue
        fp = native[ref]
        envelope = _physical_envelope(fp)
        pads = [box_mm(p.GetBoundingBox()) for p in fp.Pads()]
        if not contains(area, envelope) or any(not contains(area, box) for box in pads):
            findings.append({'cell': cell, 'kind': 'owned_outside', 'ref': ref,
                             'envelope': envelope,
                             'outside_pads': [box for box in pads if not contains(area, box)]})
    for ref, fp in sorted(native.items()):
        if ref in refs:
            continue
        envelope_hit = intersects(area, _physical_envelope(fp))
        pad_hits = [box_mm(p.GetBoundingBox()) for p in fp.Pads()
                    if intersects(area, box_mm(p.GetBoundingBox()))]
        if envelope_hit or pad_hits:
            findings.append({'cell': cell, 'kind': 'foreign_inside', 'ref': ref,
                             'envelope_hit': envelope_hit, 'pad_hits': pad_hits})
    return findings


def evaluate(board_path: Path, floorplan_path: Path, modular_path: Path,
             source_path: Path, expected: dict[str, str]) -> dict:
    paths = {'board': board_path, 'floorplan': floorplan_path,
             'modular': modular_path, 'source': source_path}
    hashes, errors, findings, rows, planning = {}, [], [], [], []
    cells = None
    for label, path in paths.items():
        try:
            hashes[label] = digest(path)
        except OSError as exc:
            hashes[label] = None
            errors.append(f'{label} unavailable: {exc}')
        if hashes[label] != expected.get(label):
            errors.append(f'{label} not bound to independent expected digest')
    if errors:
        return {'status': 'FAIL', 'hashes': hashes, 'errors': errors,
                'cells': rows, 'findings': findings,
                'planning_observations': planning, 'p1_accepted': False}
    try:
        source = yaml.safe_load(source_path.read_text())
        floorplan = yaml.safe_load(floorplan_path.read_text())
        modular = json.loads(modular_path.read_text())
        cells = source.get('physical_cells') if isinstance(source, dict) else None
        if not isinstance(source, dict):
            raise ValueError('source requirements malformed')
        if cells is not None and (not isinstance(cells, list) or not cells):
            raise ValueError('physical_cells opt-in must be a nonempty list')
        regions = floorplan['placement']['regions']
        blocks = {b['id']: set(b['refs']) for b in modular['blocks']}
        if not isinstance(regions, dict) or not blocks:
            raise ValueError('floorplan regions or modular blocks missing')
        if len(blocks) != len(modular['blocks']):
            raise ValueError('duplicate modular block id')
        all_owned_refs = [ref for refs in blocks.values() for ref in refs]
        if len(all_owned_refs) != len(set(all_owned_refs)):
            raise ValueError('duplicate modular footprint owner')
        board = pcbnew.LoadBoard(str(board_path))
        if board is None:
            raise ValueError('native board unavailable')
        native = {fp.GetReference(): fp for fp in board.GetFootprints()}
        if len(native) != len(list(board.GetFootprints())):
            raise ValueError('duplicate native footprint reference')
        assigned: dict[str, str] = {}
        declared: set[str] = set()
        for index, cell in enumerate(cells or []):
            if not isinstance(cell, dict) or set(cell) != {'id', 'owner_block', 'refs', 'transit'}:
                errors.append(f'cell {index}: malformed physical cell record')
                continue
            ident, owner, refs = cell['id'], cell['owner_block'], cell['refs']
            if (not isinstance(ident, str) or not ident or ident in declared or
                    not isinstance(owner, str) or owner not in blocks or
                    not isinstance(refs, list) or not all(isinstance(r, str) for r in refs) or
                    len(refs) != len(set(refs)) or not isinstance(cell['transit'], bool) or
                    cell['transit'] != (not refs)):
                errors.append(f'cell {index}: invalid identity/owner/refs/transit')
                continue
            declared.add(ident)
            if ident not in regions:
                errors.append(f'{ident}: floorplan region missing')
                continue
            try:
                area = rectangle(regions[ident], f'{ident} region')
            except (ValueError, TypeError) as exc:
                errors.append(str(exc))
                continue
            for ref in refs:
                if ref not in blocks[owner]:
                    errors.append(f'{ident}: {ref} not owned by {owner} in modular plan')
                if ref in assigned:
                    errors.append(f'{ref}: duplicate physical cell {assigned[ref]}/{ident}')
                assigned[ref] = ident
            own = set(refs)
            findings.extend(_occupancy(ident, area, own, native))
            rows.append({'id': ident, 'owner_block': owner, 'region': area,
                         'owned_refs': sorted(own)})
        for owner in {row['owner_block'] for row in rows}:
            missing = sorted(blocks[owner] - set(assigned))
            if missing:
                errors.append(f'{owner}: physical cell ref denominator incomplete: {missing}')
        # Functional block regions are planning envelopes, not exclusive cells.
        # Preserve their useful occupancy census without changing gate status.
        for owner, refs in sorted(blocks.items()):
            if owner in regions and owner not in declared:
                area = rectangle(regions[owner], f'{owner} planning region')
                planning.extend(_occupancy(owner, area, refs, native))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, yaml.YAMLError) as exc:
        errors.append(str(exc))
    status = ('FAIL' if errors or findings else
              'NOT_APPLICABLE' if cells is None else 'PASS')
    return {'status': status, 'hashes': hashes,
            'errors': errors, 'cells': rows, 'findings': findings,
            'planning_observations': planning,
            'p1_accepted': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('board', 'floorplan', 'modular', 'source', 'output'):
        parser.add_argument(name, type=Path)
    for name in ('board', 'floorplan', 'modular', 'source'):
        parser.add_argument(f'--expected-{name}-sha256', required=True)
    args = parser.parse_args()
    expected = {name: getattr(args, f'expected_{name}_sha256')
                for name in ('board', 'floorplan', 'modular', 'source')}
    result = evaluate(args.board, args.floorplan, args.modular, args.source, expected)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    return 0 if result['status'] in ('PASS', 'NOT_APPLICABLE') else 1


if __name__ == '__main__':
    raise SystemExit(main())
