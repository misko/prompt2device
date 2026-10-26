"""Check declared board instances and replay each unique flat native design.

Development-only verification, not electrical or stage acceptance.
Usage: schematic_assembly.py ROOT MANIFEST.json EXPECTED.json
Both JSON paths and every manifest path are relative to ROOT.

Manifest schema 1: {version:1, boards:{board_id:{source, membership, output}},
                   instances:{instance_id:board_id}}
Independent expectation: {version:1, instances:{instance_id:board_id}}
Version 2 adds a required nonempty ``harness`` to both documents: a list of
two-terminal wires, each represented by a two-item list. Each terminal is
{instance, ref, pin, net}; ``net`` is the expected local board net, not a global
net name. Wire and terminal ordering do not matter. Derive the expectation
independently from reviewed interfaces, never by copying the candidate.
Version 1 still checks membership only; it cannot certify harness coverage.
Per-board membership uses native_schematic.py's separately reviewed schema.
Boards may explicitly set producer="imported". Their source then names a
native_import.py declaration and membership uses that adapter's intent schema.
Omitted producer retains the original native builder; unknown producers fail.
Board names and instance counts come from the project manifest.
"""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys

if __package__:
    from . import native_schematic as native
    from . import native_import as imported
else:
    import native_schematic as native
    import native_import as imported


def unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(), object_pairs_hook=unique)


def local(root, name, directory=False):
    if not isinstance(name, str) or not name:
        raise ValueError('nonempty relative path required')
    relative = PurePosixPath(name)
    if (relative.is_absolute() or '..' in relative.parts or
            str(relative) != name or '\\' in name or name == '.'):
        raise ValueError(f'invalid relative path: {name}')
    path = (root / name).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'path escapes assembly root: {name}')
    if not (path.is_dir() if directory else path.is_file()):
        raise ValueError(f'missing assembly input: {name}')
    return path


def instances(value):
    if not isinstance(value, dict) or not value:
        raise ValueError('nonempty instance mapping required')
    for instance, board in value.items():
        if any(not isinstance(s, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', s)
               for s in (instance, board)):
            raise ValueError('invalid instance or board identity')
    return value


def producer(paths):
    native.keys(paths, {'source', 'membership', 'output'}, {'producer'})
    kind=paths.get('producer','native')
    if kind not in ('native','imported'):
        raise ValueError('unsupported schematic producer')
    return kind


def board_artifacts(root, paths):
    kind=producer(paths)
    out=local(root,paths['output'],directory=True)
    if kind=='native': return native.artifacts(out)
    d=imported.declaration(root,local(root,paths['source']))
    return imported.artifacts(root,d,out)


def harness(value, mapping, sources):
    """Resolve physical terminals to board-local nets and normalize wire edges.

    No electrical equivalence, pin ratings, cable pairing or physical assembly
    is inferred. In particular, equal local net names on different instances
    are not implicitly connected. Multiple wires may share a terminal (splice).
    """
    if not isinstance(value, list) or not value:
        raise ValueError('nonempty harness required for assembly version 2')
    edges = set()
    for wire in value:
        if not isinstance(wire, list) or len(wire) != 2:
            raise ValueError('harness wire needs exactly two terminals')
        terminals = []
        for terminal in wire:
            native.keys(terminal, {'instance', 'ref', 'pin', 'net'})
            if any(not isinstance(v, str) or not v for v in terminal.values()):
                raise ValueError('harness terminal fields must be nonempty strings')
            instance, ref, pin, net = (terminal[k] for k in ('instance', 'ref', 'pin', 'net'))
            if instance not in mapping:
                raise ValueError(f'unknown harness instance: {instance}')
            source = sources[mapping[instance]]
            component = next((c for c in source['components'] if c['ref'] == ref), None)
            terminal_pin = next((p for p in component['pins'] if p['number'] == pin), None) if component else None
            if terminal_pin is None or terminal_pin.get('net') != net:
                raise ValueError(f'harness terminal net/pin mismatch: {instance}/{ref}/{pin}')
            terminals.append((instance, ref, pin, net))
        if terminals[0][:3] == terminals[1][:3]:
            raise ValueError('harness wire cannot connect a terminal to itself')
        edge = tuple(sorted(terminals))
        if edge in edges:
            raise ValueError('duplicate harness wire')
        edges.add(edge)
    return edges


def verify(root, manifest_name, expected_name):
    root = root.resolve()
    manifest_path = local(root, manifest_name)
    expected_path = local(root, expected_name)
    manifest, expected = read(manifest_path), read(expected_path)
    native.keys(manifest, {'version', 'boards', 'instances'}, {'harness'})
    native.keys(expected, {'version', 'instances'}, {'harness'})
    if any(type(obj['version']) is not int or obj['version'] not in (1, 2)
           for obj in (manifest, expected)):
        raise ValueError('assembly version must be 1 or 2')
    if manifest['version'] != expected['version']:
        raise ValueError('assembly versions differ')
    check_harness = manifest['version'] == 2
    if any(('harness' in obj) != check_harness for obj in (manifest, expected)):
        raise ValueError('harness must be present exactly for assembly version 2')
    if instances(manifest['instances']) != instances(expected['instances']):
        raise ValueError('assembly instance membership differs from expectation')
    boards = manifest['boards']
    if not isinstance(boards, dict) or set(boards) != set(manifest['instances'].values()):
        raise ValueError('board definitions must match instantiated board identities')

    # Resolve every input before expensive native replay. Separate design outputs
    # cannot share/contain one another; identical copies remain distinct subjects.
    resolved = {}
    sources = {}
    used_outputs = []
    for board, paths in boards.items():
        kind=producer(paths)
        source = local(root, paths['source'])
        membership = local(root, paths['membership'])
        out = local(root, paths['output'], directory=True)
        if any(out.is_relative_to(other) or other.is_relative_to(out) for other in used_outputs):
            raise ValueError('board output directories overlap')
        used_outputs.append(out)
        # Keep artifact reads within ROOT, including symlinked individual files.
        for artifact in (*board_artifacts(root,paths).values(), out/'receipt.json'):
            if not artifact.resolve().is_relative_to(root):
                raise ValueError('board artifact escapes assembly root')
        if kind=='native':
            sources[board] = read(source)
            native.check_membership(sources[board], read(membership))
        else:
            d=imported.declaration(root,source)
            sources[board]=imported.check_intent(read(local(root,d['intent'])))
            imported.membership(sources[board],read(membership))
        resolved[board] = (kind,source,out,membership)

    wires = None
    if check_harness:
        wires = harness(manifest['harness'], manifest['instances'], sources)
        if wires != harness(expected['harness'], expected['instances'], sources):
            raise ValueError('harness wiring differs from independent expectation')
    results = {board: native.verify_complete(source,out,membership) if kind=='native'
               else imported.verify(root,source,out,membership)
               for board,(kind,source,out,membership) in sorted(resolved.items())}
    return {'schema': 1, 'manifest_sha256': native.digest(manifest_path),
            'expected_sha256': native.digest(expected_path),
            'verifier_sha256': native.digest(Path(__file__)),
            'instances': manifest['instances'], 'boards': results,
            'harness_checked': check_harness,
            'harness_wire_count': len(wires) if wires is not None else None,
            'note': 'Declared instance membership and per-board native replay; '
                    + ('declared harness terminals/wires checked against independent expectation. '
                       if check_harness else 'No harness verification. ')
                    + 'No cable ratings/pairing, electrical, readability or stage acceptance.'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('manifest')
    parser.add_argument('expected')
    args = parser.parse_args(argv)
    try:
        print(json.dumps(verify(args.root, args.manifest, args.expected), sort_keys=True))
    except (ValueError, OSError, native.ET.ParseError) as exc:
        print(f'schematic assembly: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
