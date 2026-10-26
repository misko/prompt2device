#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Explicit public derivative of one pinned seal; never engineering acceptance."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import zipfile

IDENTITY = 'crow-prototype-v3-first-run-5c10p-public-v1'
SEAL = 'c2b89fdaf364b7538cd58bf0e52a150c8bde3b9cd1f2b52f2010adfafc398a50'
ARCHIVE = '97d98924da353325c3297f1886abdf5d305ede273d3100a5ce056f19ea15df56'
NATIVE = 'source/project/06_build/recovery/first-run-d3-staging/fabrication1/native/'
BOARDS = {'carrier': {'quantity': 5, 'version': 'rev-a-first-run-r3-d3'},
          'pod': {'quantity': 10, 'version': 'rev-a-first-run'}}
ROOT = Path(__file__).resolve().parent
DEFAULT = ROOT / 'releases' / IDENTITY
POST_SEAL = {
    '08_reviews/2026-10-23-first-run-seal.md': ('evidence/post-seal-review.md',
        '7babb5bd84b559dc82d4205fda1f5687b2cc4971f5abfbed61848453e5690a8d'),
    '06_build/checkpoints/sealed_release.json': ('evidence/sealed-release-receipt.json',
        'f0e1fdf90dd6b6c181fac99741bdfbca32aa86ff250f4a020e3092f691ae5b0e'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe(root, name):
    p = PurePosixPath(name)
    require(not p.is_absolute() and '..' not in p.parts and str(p) == name,
            f'unsafe path: {name}')
    target = root / name
    require(target.resolve().is_relative_to(root.resolve()), f'escaping path: {name}')
    require(not any(x.is_symlink() for x in [target, *target.parents]), f'symlink: {name}')
    return target


def load(root, name):
    return json.loads(safe(root, name).read_text())


def selection(archive):
    """Map public paths to archive paths; never glob vendor documentation."""
    selected = {}
    for board, info in archive['recipient']['native'].items():
        require(board in BOARDS, 'unexpected native board')
        for origin in [*info['roles'].values(), *info['resources']]:
            require(origin.startswith(NATIVE), 'unexpected native root')
            selected['native/' + origin.removeprefix(NATIVE)] = origin
    for origin in archive['files']:
        if origin.startswith(('fab/', 'pdf/', 'verification/')):
            selected[origin] = origin
    for name in ('HANDOFF.md', 'ORDER-INSTRUCTIONS.md'):
        selected['historical/' + name] = name
    # Original authored instructions, not vendor PDFs/HTML or model binaries.
    for origin in archive['files']:
        if origin.startswith('documentation/') and origin.endswith('.md'):
            selected['historical/' + origin] = origin
    return dict(sorted(selected.items()))


def roles(archive):
    return {b: {role: 'native/' + p.removeprefix(NATIVE)
                for role, p in value['roles'].items()}
            for b, value in archive['recipient']['native'].items()}


def copied_license(origin):
    return 'CC-BY-SA-4.0 WITH KiCad-design-exception' if '/libraries/' in origin else 'MIT'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def build(sealed, output, post_seal):
    require(not output.exists(), 'output must be absent')
    require(digest(sealed/'release/seal.json') == SEAL, 'wrong seal')
    require(digest(sealed/'release/archive/release.json') == ARCHIVE, 'wrong archive')
    seal = load(sealed, 'release/seal.json')
    archive = load(sealed, 'release/archive/release.json')
    output.mkdir(parents=True)
    inventory = {}

    def copy(origin, target, expected, license_name='MIT', source_root=None):
        src = safe(source_root or sealed, origin)
        require(digest(src) == expected, f'upstream mismatch: {origin}')
        dst = safe(output, target)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        inventory[target] = dict(sha256=expected,
                                origin=('post-seal/' if source_root else '')+origin,
                                license=license_name)

    for target, origin in selection(archive).items():
        copy('release/archive/' + origin, target, archive['files'][origin], copied_license(origin))
    copy('release/seal.json', 'evidence/seal.json', SEAL)
    copy('release/archive/release.json', 'evidence/archive-manifest.json', ARCHIVE)
    for origin in ('CURRENT-STATUS.json', 'CURRENT-STATUS.md',
                   'verification/release-review.md', 'verification/release_reviewed.json'):
        copy('release/' + origin, 'evidence/' + origin, seal['files'][origin])
    for origin, (target, sha) in POST_SEAL.items():
        copy(origin, target, sha, source_root=post_seal)

    status = load(output, 'evidence/CURRENT-STATUS.json')
    omitted = []
    # Stable upstream pointers/checksums for vendor sources, not redistributed bytes.
    for path in sorted((sealed/'source/project/02_parts').rglob('*')):
        if path.is_file() and path.suffix.lower() in ('.pdf', '.html', '.step', '.stp'):
            urls = set()
            for peer in list(path.parent.glob('*.yaml')) + list(path.parent.glob('*.md')):
                urls.update(re.findall(r'https?://[^\s<>"\)]+', peer.read_text(errors='replace')))
            omitted.append(dict(origin=path.relative_to(sealed).as_posix(), sha256=digest(path),
                                source_urls=sorted(urls),
                                note='Related dossier URLs; identical bytes are not guaranteed available upstream.'))
    write_json(output/'EXTERNAL-DEPENDENCIES.json', {
        'not_complete_offline_replay': True, 'vendor_sources': omitted,
        'excluded_families': ['vendor PDFs and HTML', 'runtime binaries',
                              'populated 3D assemblies and model assets',
                              'full authoring/replay source and engineering evidence closure'],
        'optional_native_3d': {'variable': 'KICAD10_3DMODEL_DIR',
                             'upstream': 'https://gitlab.com/kicad/libraries/kicad-packages3D',
                             'note': 'Native optional library previews are not the reviewed registered assembly.'}})
    shutil.copyfile(ROOT/'licenses/KiCad-LICENSE.md', output/'KiCad-LICENSE.md')
    shutil.copyfile(ROOT.parents[1]/'LICENSE', output/'LICENSE')
    (output/'THIRD-PARTY-NOTICES.md').write_text(
        '# Third-party notices\n\n'
        'Original project designs, custom Crow symbols/footprints, reports and generated '
        'outputs are covered by LICENSE. KiCad-derived designs use the library design exception.\n\n'
        'All native/**/libraries/** footprint collections are attributed to the KiCad '
        'library contributors and retain CC-BY-SA 4.0 plus the design exception; see '
        '[KiCad-LICENSE.md](KiCad-LICENSE.md). Snapshot: the selected libraries retained '
        'by the KiCad 10.0.4 Crow toolchain, with exact per-file hashes and original paths '
        'in publication.json. Project-modified snapshots are not asserted identical to an '
        'upstream tag. Upstream: https://gitlab.com/kicad/libraries/kicad-footprints ; '
        'license: https://www.kicad.org/libraries/license/ .\n\n'
        'No vendor PDF, HTML, model library or compiled runtime is included. '
        '[EXTERNAL-DEPENDENCIES.json](EXTERNAL-DEPENDENCIES.json) records excluded '
        'source hashes and related upstream links. Historical paths in retained review '
        'records may refer to this omitted evidence. They are not claims of local availability.\n')
    native = roles(archive)
    lines = ['# Crow v3 — public design package', '', '**DO-NOT-ORDER.** Public derivative; '
             'not the original sealed archive and not a complete offline replay.', '',
             'Scope: 5 carriers and 10 pods, not five complete eight-pod arrays. '
             'Original seal records SOUND design acceptance; physical qualification, firmware, '
             'current stock and exact-job approval are not established here.', '',
             '## Designs and exports', '',
             '| Board | Native schematic | Native PCB | Schematic PDF | PCB PDF | Gerbers |',
             '|---|---|---|---|---|---|']
    for board in BOARDS:
        lines.append(f'| {board} | [schematic]({native[board]["schematic"]}) | '
                     f'[PCB]({native[board]["pcb"]}) | [PDF](pdf/{board}/schematic.pdf) | '
                     f'[PDF](pdf/{board}/pcb.pdf) | [ZIP](fab/{board}/{board}-gerbers.zip) |')
    lines += ['', 'BOM, CPL and population policies: [fab/assembly](fab/assembly). '
              'Factory and consigned files describe distinct proposed routes; do not combine '
              'or submit them as an approved turnkey order.', '',
              'Open with KiCad 10.0.4. Local symbol/footprint tables and native settings are '
              'included. Keep the native directory structure. Optional standard KiCad 3D '
              'models are external; the registered populated assembly is deliberately excluded.', '',
              '## Active ordering holds', '']
    for hold in status['holds']:
        lines.append(f'- **{hold["id"]}** — {hold["reason"]} Closure: {hold["closure"]}')
    lines += ['', 'The user authorized this separate public derivative on 2026-10-25. '
              'Historical statements denying publication authority describe the earlier seal; '
              'they do not grant or remove purchasing authority.', '',
              '## Evidence and limits', '',
              '- [Exact original current status](evidence/CURRENT-STATUS.json).',
              '- [Independent post-seal review](evidence/post-seal-review.md) and '
              '[final seal receipt](evidence/sealed-release-receipt.json), retained separately '
              'from the original seal to avoid a circular hash claim.',
              '- [Historical release review](evidence/verification/release-review.md) and '
              '[receipt](evidence/verification/release_reviewed.json).',
              '- [Original seal record](evidence/seal.json) and '
              '[archive inventory](evidence/archive-manifest.json). These inventory omitted '
              'files too; neither is a manifest of this public subset.',
              '- [Historical handoff](historical/HANDOFF.md) and '
              '[order instructions](historical/ORDER-INSTRUCTIONS.md). Their full-replay '
              'commands require the original archive and must not be run as subset instructions.',
              '- [External dependencies](EXTERNAL-DEPENDENCIES.json), '
              '[licenses](THIRD-PARTY-NOTICES.md), and [public inventory](publication.json).', '',
              'All copied payload bytes match their pinned upstream identities. Verification '
              'of this subset checks preservation, inventory, native local dependencies and '
              'Gerber ZIP/plot consistency, not independent engineering acceptance. No new '
              'seal, live sourcing result or complete-replay claim is made.', '',
              'From the repository root: `python3 -B projects/crow-array/publication.py verify`.']
    (output/'README.md').write_text('\n'.join(lines)+'\n')
    for name in ('README.md', 'LICENSE', 'KiCad-LICENSE.md', 'THIRD-PARTY-NOTICES.md',
                 'EXTERNAL-DEPENDENCIES.json'):
        inventory[name] = dict(sha256=digest(output/name), origin=None,
                               license='CC-BY-SA-4.0 WITH KiCad-design-exception' if name=='KiCad-LICENSE.md' else 'MIT')
    write_json(output/'publication.json', dict(schema=1, package_id=IDENTITY,
        kind='public-derivative-not-sealed-replay', boards=BOARDS,
        original_design_verdict='SOUND', order_verdict='DO-NOT-ORDER',
        seal_sha256=SEAL, archive_sha256=ARCHIVE, native=native, files=inventory))
    return verify(output)


def verify(root):
    p = load(root, 'publication.json')
    require(p['schema']==1 and p['package_id']==IDENTITY and
            p['kind']=='public-derivative-not-sealed-replay', 'wrong package identity')
    require(p['boards']==BOARDS and p['order_verdict']=='DO-NOT-ORDER' and
            p['original_design_verdict']=='SOUND', 'scope/status changed')
    require(p['seal_sha256']==SEAL and p['archive_sha256']==ARCHIVE, 'pin changed')
    for file in root.rglob('*'):
        require(not file.is_symlink(), 'symlink in public package')
    actual = {f.relative_to(root).as_posix() for f in root.rglob('*') if f.is_file()}
    require(actual == set(p['files']) | {'publication.json'}, 'extra or missing file')
    for name, meta in p['files'].items():
        require(digest(safe(root, name))==meta['sha256'], f'changed file: {name}')
        license_name = ('CC-BY-SA-4.0 WITH KiCad-design-exception' if name=='KiCad-LICENSE.md'
                        else copied_license(meta['origin'] or ''))
        require(meta['license']==license_name, f'license changed: {name}')
    require(digest(root/'evidence/seal.json')==SEAL, 'changed original seal')
    require(digest(root/'evidence/archive-manifest.json')==ARCHIVE, 'changed original archive')
    seal = load(root, 'evidence/seal.json')
    archive = load(root, 'evidence/archive-manifest.json')
    status = load(root, 'evidence/CURRENT-STATUS.json')
    expected = {'evidence/seal.json': ('release/seal.json', SEAL),
                'evidence/archive-manifest.json': ('release/archive/release.json', ARCHIVE)}
    for origin, (target, sha) in POST_SEAL.items():
        expected[target] = ('post-seal/'+origin, sha)
    for name in ('CURRENT-STATUS.json', 'CURRENT-STATUS.md',
                 'verification/release-review.md', 'verification/release_reviewed.json'):
        expected['evidence/'+name] = ('release/'+name, seal['files'][name])
    for name, origin in selection(archive).items():
        expected[name] = ('release/archive/'+origin, archive['files'][origin])
    require({n for n,m in p['files'].items() if m['origin'] is not None}==set(expected),
            'copied selection changed')
    generated = {'README.md','LICENSE','KiCad-LICENSE.md','THIRD-PARTY-NOTICES.md',
                 'EXTERNAL-DEPENDENCIES.json'}
    require(set(p['files'])==set(expected)|generated, 'unapproved file selection')
    policy = load(ROOT, 'publication-policy.json')
    require(set(policy)==generated, 'incomplete publication policy')
    for name, sha in policy.items():
        require(digest(safe(root,name))==sha, f'publication policy mismatch: {name}')
    for name,(origin,sha) in expected.items():
        require(p['files'][name]['origin']==origin and p['files'][name]['sha256']==sha,
                f'origin binding changed: {name}')
        if '/libraries/' in origin:
            require(p['files'][name]['license']=='CC-BY-SA-4.0 WITH KiCad-design-exception',
                    'library license changed')
    require(p['native']==roles(archive), 'native role mismatch')
    require(status['boards']==BOARDS and status['design_verdict']=='SOUND' and
            status['order_verdict']=='DO-NOT-ORDER' and len(status['holds'])==9, 'upstream status mismatch')
    readme = (root/'README.md').read_text()
    for hold in status['holds']:
        require(hold['id'] in readme and hold['closure'] in readme, 'hidden hold')
    for target in re.findall(r'\]\(([^)]+)\)', readme):
        require(safe(root,target).exists(), f'broken index link: {target}')
    for table in (root/'native').rglob('*-lib-table'):
        for uri in re.findall(r'\(uri "([^"]+)"\)', table.read_text()):
            require(uri.startswith('${KIPRJMOD}/'), 'external local library')
            require(safe(table.parent,uri.removeprefix('${KIPRJMOD}/')).exists(), 'missing native library')
    for board in BOARDS:
        with zipfile.ZipFile(root/f'fab/{board}/{board}-gerbers.zip') as z:
            require(z.testzip() is None and len(z.namelist())==13, 'bad Gerber ZIP')
            for name in z.namelist():
                require(PurePosixPath(name).name==name, 'nested Gerber member')
                require(z.read(name)==safe(root,f'fab/{board}/plots/{name}').read_bytes(), 'ZIP/plot mismatch')
    return dict(package_id=IDENTITY, files=len(p['files']), boards=list(BOARDS),
                preservation='PASS', engineering_acceptance='NOT_REASSESSED', order='DO-NOT-ORDER')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build','verify'])
    parser.add_argument('--sealed', type=Path)
    parser.add_argument('--post-seal-project', type=Path)
    parser.add_argument('--package', type=Path, default=DEFAULT)
    args = parser.parse_args()
    try:
        if args.command=='build':
            require(args.sealed is not None and args.post_seal_project is not None,
                    '--sealed and --post-seal-project required')
            result=build(args.sealed.resolve(), args.package.resolve(), args.post_seal_project.resolve())
        else:
            result=verify(args.package.resolve())
        print(json.dumps(result,indent=2))
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        parser.exit(1, f'PUBLICATION FAIL: {exc}\n')
