"""Non-RF flat-board schematic receipt; requires explicit project adoption.

Reuses upstream admission and assembly/native replay. A reviewed project contract
01_docs/schematic-contract.json declares version=1, manifest, expected, rf=false.
The independent review uses upstream schema1, stage KICAD-SCHEMATIC, and CHECKS
below. This tool cannot authenticate people or judge electrical/readability prose.
It issues only an evidence receipt; it never edits status or advances placement.
"""
import argparse
import json
from pathlib import Path
import sys

if __package__:
    from . import admission as upstream, schematic_assembly as assembly
else:
    import admission as upstream
    import schematic_assembly as assembly

CHECKS = {'completeness', 'electrical', 'readability', 'sourcing',
          'signal_integrity', 'applicability'}
CONTRACT = '01_docs/schematic-contract.json'
CAPABILITY = '01_docs/capability-profile.json'
PARTS = '06_build/checkpoints/parts_locked.json'
RECEIPT = '06_build/checkpoints/schematic_reviewed.json'


def require(condition, message):
    if not condition:
        raise upstream.AdmissionError(message)


def review_data(project, name):
    require(name.startswith('08_reviews/') and upstream.DATE.fullmatch(Path(name).name),
            'schematic review must be dated under 08_reviews')
    raw = upstream.nonempty(project, name)
    blocks = upstream.FENCE.findall(raw.decode('utf-8'))
    require(len(blocks) == 1, 'review needs one JSON block')
    obj = upstream.exact_keys(upstream.parse_json(blocks[0].encode(), 'review'),
        {'schema', 'stage', 'author', 'reviewer', 'verdict', 'subjects', 'checks'}, 'review')
    require(type(obj['schema']) is int and obj['schema'] == 1
            and obj['stage'] == 'KICAD-SCHEMATIC', 'unsupported schematic review')
    require(all(isinstance(obj[k], str) and obj[k].strip() for k in ('author', 'reviewer')),
            'review identities required')
    require(obj['author'].strip().casefold() != obj['reviewer'].strip().casefold(),
            'author and reviewer must differ')
    require(obj['verdict'] == 'PASS', 'review verdict is not PASS')
    subjects = obj['subjects']
    require(isinstance(subjects, dict) and subjects, 'nonempty subjects required')
    for path, sha in subjects.items():
        resolved = upstream.safe_file(project, path).resolve().relative_to(project.resolve()).as_posix()
        require(not any(p.startswith(('03_src/drafts/', '06_build/drafts/'))
                        for p in (path, resolved)), 'draft evidence cannot admit a schematic')
        require(isinstance(sha, str) and upstream.SHA.fullmatch(sha), 'invalid subject hash')
        require(upstream.digest(upstream.nonempty(project, path)) == sha, f'stale subject: {path}')
    upstream.exact_keys(obj['checks'], CHECKS, 'schematic checks')
    for key, check in obj['checks'].items():
        upstream.exact_keys(check, {'verdict', 'evidence', 'rationale'}, key)
        require(check['verdict'] == 'PASS' and isinstance(check['rationale'], str)
                and check['rationale'].strip(), f'failed or empty check: {key}')
        require(isinstance(check['evidence'], list) and check['evidence']
                and all(isinstance(p, str) and p in subjects for p in check['evidence']),
                f'unbound check evidence: {key}')
    return obj, raw


def source_contract(project):
    return upstream.source_contract(project)


def prerequisites(project, root):
    """Shared dispatch/acceptance guard, so direct issue cannot bypass adoption."""
    prior = upstream.validate_certificate(project, PARTS, root)
    require(prior['role'] == 'parts_locked', 'parts_locked prerequisite required')
    review, _ = upstream.review_data(project, prior['review'])
    return prior, upstream.sourcing_contract(project, review)


def certificate(project, review, root):
    project, root = project.resolve(), root.resolve()
    obj, raw = review_data(project, review)
    prior, contract = prerequisites(project, root)
    graph = upstream.parse_json((root/'skills/pcb-design/workflow/graph.json').read_bytes(), 'graph')
    specs = [s['spec'] for s in graph['stages'] if s['spec']['id'] == 'KICAD-SCHEMATIC']
    require(len(specs) == 1 and specs[0]['produces'] == ['schematic_reviewed']
            and specs[0]['requires'] == ['parts_locked', 'rf_source_clearance'],
            'schematic graph roles differ from this contract')
    manifest = assembly.read(assembly.local(project, contract['manifest']))
    assembly.local(project, contract['expected'])
    require(isinstance(manifest.get('instances'), dict), 'instance mapping required')
    require(len(manifest['instances']) <= 1 or manifest.get('version') == 2,
            'multiple board instances require declared harness verification')
    groups = {
        'applicability': {CONTRACT, CAPABILITY, 'contracts.md'},
        'completeness': {CONTRACT, contract['manifest'], contract['expected']},
        'electrical': {CONTRACT}, 'readability': set(),
        'sourcing': {PARTS}, 'signal_integrity': {CAPABILITY},
    }
    require(isinstance(manifest.get('boards'), dict) and manifest['boards'], 'boards required')
    for paths in manifest['boards'].values():
        kind=assembly.producer(paths)
        require(kind in contract.get('producers',['native']),
                'producer not adopted by reviewed schematic contract')
        out = assembly.local(project, paths['output'], directory=True)
        artifact = {key: path.relative_to(project).as_posix()
                    for key, path in assembly.board_artifacts(project,paths).items()}
        groups['completeness'].update((paths['source'], paths['membership'],
                                      f"{paths['output']}/receipt.json", artifact['source']))
        groups['electrical'].update((paths['source'], artifact['source'], artifact['netlist'],
                                    artifact['erc'], artifact['erc_all']))
        groups['readability'].update((artifact['schematic'], artifact['pdf']))
        groups['signal_integrity'].update((paths['source'],artifact['source']))
        groups['sourcing'].update((paths['source'],artifact['source']))
        if kind=='imported':
            groups['completeness'].update(p.relative_to(project).as_posix()
                for p in assembly.imported.subjects(project,assembly.local(project,paths['source']),out))
    for key, required in groups.items():
        require(required <= set(obj['checks'][key]['evidence']),
                f'{key} lacks required exact subject coverage')
    checked = assembly.verify(project, contract['manifest'], contract['expected'])
    identities = upstream.identities(root)
    for path in ('tools/schematic_admission.py', 'tools/schematic_assembly.py',
                 'tools/native_schematic.py', 'tools/native_import.py', 'skills/pcb-design/workflow/stages/schematic.md',
                 'skills/pcb-design/procedures/schematic/native-tooling.md',
                 'skills/pcb-design/procedures/schematic/imported-tooling.md'):
        identities[path] = upstream.digest((root/path).read_bytes())
    return {'schema': 1, 'stage': 'KICAD-SCHEMATIC', 'role': 'schematic_reviewed',
            'review': review, 'review_sha256': upstream.digest(raw),
            'subjects': obj['subjects'], 'identities': identities,
            'prerequisites': {PARTS: upstream.digest(upstream.nonempty(project, PARTS))},
            'assembly': checked}


def validate(project, root):
    stored = upstream.parse_json(upstream.nonempty(project, RECEIPT), 'schematic receipt')
    require(isinstance(stored, dict) and isinstance(stored.get('review'), str), 'invalid receipt')
    require(stored == certificate(project, stored['review'], root), 'stale or altered schematic receipt')
    return stored


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    sub = parser.add_subparsers(dest='action', required=True)
    issue = sub.add_parser('issue')
    issue.add_argument('--review', required=True)
    sub.add_parser('check')
    args = parser.parse_args(argv)
    project, root = args.project.resolve(), Path(__file__).resolve().parents[1]
    try:
        if args.action == 'check':
            validate(project, root)
        else:
            result = certificate(project, args.review, root)
            target = project/RECEIPT
            require(not any(p.is_symlink() for p in (project/'06_build', target.parent, target))
                    and not target.exists() and target.resolve().is_relative_to(project),
                    'refusing overwrite, symlink or escaping receipt')
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('x', encoding='utf-8') as stream:
                stream.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
        print('Schematic evidence current; engineering verdict remains reviewer-owned. Stop before placement.')
        return 0
    except (ValueError, OSError, UnicodeError, TypeError, KeyError, assembly.native.ET.ParseError) as exc:
        print(f'schematic admission refused: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
