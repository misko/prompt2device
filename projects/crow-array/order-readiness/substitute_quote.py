"""Reproducible metadata-only substitution derivative; never an order approval.

Consumes reviewed changes, preserves r5 and the published release, and proves
native edits touch only the specified MPN/manufacturer/value property strings.
No footprint, connectivity, copper, CPL or fabrication changes are supported.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'quote-draft/r5-2c8p-complete'
RELEASE = ROOT.parent / 'releases/crow-prototype-v3-first-run-5c10p-public-v1'
TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    return list(csv.DictReader(io.StringIO(path.read_text())))


def csv_bytes(rows):
    stream = io.StringIO()
    writer = csv.DictWriter(stream, list(rows[0]), lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def forms(text):
    """Return nodes with token offsets, preserving every untouched source byte."""
    stack, nodes = [], []
    for token in TOKENS.finditer(text):
        s = token.group()
        if s == '(':
            node = []
            if stack:
                stack[-1].append(node)
            stack.append(node)
        elif s == ')':
            need(stack, 'Unbalanced source')
            nodes.append(stack.pop())
        else:
            need(stack, 'Token outside native expression')
            stack[-1].append(token)
    need(not stack, 'Incomplete source')
    return nodes


def atom(node, index=0):
    return node[index].group() if len(node) > index and not isinstance(node[index], list) else ''


def rewrite(text, board, changes):
    edits, seen = [], []
    for node in forms(text):
        if atom(node) not in ('symbol', 'footprint'):
            continue
        props = {json.loads(atom(c, 1)): c[2] for c in node if isinstance(c, list)
                 and atom(c) == 'property' and len(c) >= 3}
        if 'MPN' not in props:
            continue
        old = json.loads(props['MPN'].group())
        spec = next((r for r in changes if r['old_mpn'] == old), None)
        if spec is None:
            continue
        ref = json.loads(props['Reference'].group())
        if ref not in spec['refs'].get(board, []):
            ref = json.loads(atom(node, 1)).split(':')[-1]
        need(ref in spec['refs'].get(board, []), 'Unexpected changed component: ' + ref)
        need(json.loads(props['Manufacturer'].group()) == spec['old_manufacturer'], 'Maker mismatch')
        fields = {'MPN': spec['mpn'], 'Manufacturer': spec['manufacturer']}
        value = json.loads(props['Value'].group())
        fields['Value'] = spec['values'].get(value, value)
        for key, value in fields.items():
            token = props[key]
            edits.append((token.start(), token.end(), json.dumps(value), token.group()))
        seen.append(ref)
    result = text
    for start, end, value, old in sorted(edits, reverse=True):
        need(text[start:end] == old, 'Property span mismatch')
        result = result[:start] + value + result[end:]
    # Reconstruct baseline by reversing only these exact replacements.
    shift, inverse = 0, []
    for start, end, value, old in sorted(edits):
        inverse.append((start + shift, start + shift + len(value), old))
        shift += len(value) - (end - start)
    restored = result
    for start, end, old in reversed(inverse):
        restored = restored[:start] + old + restored[end:]
    need(restored == text, 'Unintended source change')
    return result, sorted(seen)


def spec_check(spec):
    need(spec['assembled'] == {'carrier': 2, 'pod': 8}, 'Wrong build quantity')
    need(sha(BASE / 'manifest.json') == spec['base_quote_manifest_sha256'], 'Changed r5 baseline')
    need(sha(RELEASE / 'publication.json') == spec['release_publication_sha256'], 'Changed release baseline')
    for name, digest in json.loads((BASE / 'manifest.json').read_text())['files'].items():
        need(sha(BASE / name) == digest, 'Changed r5 input: ' + name)
    release_files = json.loads((RELEASE / 'publication.json').read_text())['files']
    need({str(p.relative_to(RELEASE)) for p in RELEASE.rglob('*') if p.is_file()} ==
         set(release_files) | {'publication.json'}, 'Extra or missing release input')
    for name, entry in release_files.items():
        need(sha(RELEASE / name) == entry['sha256'], 'Changed release input: ' + name)
    rows = spec['replacements']
    need(len({r['old_mpn'] for r in rows}) == len(rows), 'Duplicate original')
    need(len({r['mpn'] for r in rows}) == len(rows), 'Duplicate target')
    for r in rows:
        need(r['engineering'] == 'PASS', 'Unreviewed replacement')
        need(r['mpn'] != r['old_mpn'] and r['code'], 'Invalid candidate')
        need(r['review'] in spec['evidence'], 'Replacement review is not bound')
        need(r['installed_need'] == sum(len(refs) * spec['assembled'][b]
                                       for b, refs in r['refs'].items()), 'Wrong part quantity')
    for path, expected in spec['evidence'].items():
        source = ROOT / path
        need(source.resolve().is_relative_to(ROOT), 'Evidence path escape')
        need(sha(source) == expected, 'Missing/stale evidence: ' + path)


def generated_tables(spec):
    changes = spec['replacements']
    result = {}
    for board in spec['assembled']:
        rows = read_csv(BASE / f'{board}-bom.csv')
        seen = set()
        for row in rows:
            retained = next((s for s in spec.get('retained_sources', []) if s['mpn'] == row['MPN']), None)
            if retained:
                need(row['Manufacturer'] == retained['manufacturer'], 'Retained-source maker mismatch')
                row['Supply route'] = 'JLC_Global_Sourcing_or_consignment_candidate'
                row['JLCPCB Part #'] = ''  # Private IDs are not known; public locators remain in the plan.
            r = next((s for s in changes if s['old_mpn'] == row['MPN']), None)
            if r is None:
                continue
            refs = set(row['Designator'].split(','))
            need(refs <= set(r['refs'].get(board, [])), 'BOM reference mismatch')
            need(row['Manufacturer'] == r['old_manufacturer'], 'BOM maker mismatch')
            need(row['Footprint'] == r['footprint'], 'BOM footprint mismatch')
            row.update({'MPN': r['mpn'], 'Manufacturer': r['manufacturer'],
                        'JLCPCB Part #': r['code'], 'Supply route': 'JLC_catalog_candidate',
                        'Comment': r['values'].get(row['Comment'], row['Comment'])})
            seen.update(refs)
        need(seen == {ref for r in changes for ref in r['refs'].get(board, [])}, 'Missing changed refs')
        result[f'{board}-bom.csv'] = csv_bytes(rows)
    for name in ('scope.csv', 'procurement-plan.csv'):
        rows = read_csv(BASE / name)
        for row in rows:
            r = next((s for s in changes if s['old_mpn'] == row['mpn']), None)
            if r:
                need(row['manufacturer'] == r['old_manufacturer'], 'Table maker mismatch')
                row.update(mpn=r['mpn'], manufacturer=r['manufacturer'])
                if name == 'procurement-plan.csv':
                    row.update(catalog_locator=r['code'], external_lead='',
                               proposed_route='JLC_catalog_candidate',
                               evidence_status='Reviewed substitute; public availability only; job allocation pending')
            retained = next((s for s in spec.get('retained_sources', []) if s['mpn'] == row['mpn']), None)
            if retained and name == 'procurement-plan.csv':
                need(row['manufacturer'] == retained['manufacturer'], 'Source plan maker mismatch')
                row.update(external_lead=retained['url'],
                           proposed_route='JLC_Global_Sourcing_or_consignment_candidate',
                           evidence_status='Exact distributor public stock adequate; factory eligibility, gross demand, allocation and fees pending')
        result[name] = csv_bytes(rows)
    return result


def build(spec_path, output):
    need(not output.exists(), 'Refusing existing output')
    spec = json.loads(spec_path.read_text())
    spec_check(spec)
    tables = generated_tables(spec)
    output.mkdir(parents=True)
    for name, data in tables.items():
        (output / name).write_bytes(data)
    unchanged = ['home-install-parts.csv', 'jlc-tht-parts.csv', 'tht-placement-verification.csv']
    unchanged += [f'{b}-{s}' for b in spec['assembled'] for s in ('cpl.csv', 'gerbers.zip')]
    for name in unchanged:
        shutil.copyfile(BASE / name, output / name)
    for name in ('LICENSE', 'KiCad-LICENSE.md', 'THIRD-PARTY-NOTICES.md'):
        shutil.copyfile(RELEASE / name, output / name)
    need(spec['instructions'] in spec['evidence'], 'Instructions must be hash-bound')
    shutil.copyfile(ROOT / spec['instructions'], output / 'README.md')
    shutil.copytree(RELEASE / 'native/source', output / 'native/pcb')
    schematic = RELEASE / 'native/design/03_src/recovery/first-run-r3-source'
    shutil.copytree(schematic, output / 'native/schematic')
    audit = []
    for board in spec['assembled']:
        paths = [(output / f'native/pcb/{board}/{board}.kicad_pcb',
                  RELEASE / f'native/source/{board}/{board}.kicad_pcb', 1),
                 (output / f'native/schematic/crow-{board}.kicad_sch', schematic / f'crow-{board}.kicad_sch', 2),
                 (output / f'native/schematic/Crow{board.title()}.kicad_sym', schematic / f'Crow{board.title()}.kicad_sym', 1)]
        expected = sorted(ref for r in spec['replacements'] for ref in r['refs'].get(board, []))
        for path, original, repeats in paths:
            text = original.read_text()
            updated, seen = rewrite(text, board, spec['replacements'])
            need(seen == sorted(expected * repeats), 'Native reference coverage: ' + str(path))
            path.write_text(updated)
            audit.append(dict(path=str(path.relative_to(output)), source=str(original.relative_to(ROOT.parent)),
                              source_sha256=sha(original), sha256=sha(path), refs=seen,
                              proof='Byte-exact inverse of only MPN/Manufacturer/Value property strings'))
    manifest = dict(status='REVIEWED_SUBSTITUTION_QUOTE_DERIVATIVE', production_ready=False,
                    purchase_authorized=False, submitted=False, vendor_preview_approved=False,
                    assembled=spec['assembled'], fabricated={'carrier': 5, 'pod': 10},
                    spec_sha256=sha(spec_path), tool_sha256=sha(Path(__file__)), native_changes=audit,
                    unchanged={name: sha(BASE / name) for name in unchanged},
                    inherited_release_acceptance=False,
                    installed={'JLC_SMT': 478, 'JLC_THT': 28, 'HOME': 18, 'total': 524})
    manifest['files'] = {str(p.relative_to(output)): sha(p) for p in sorted(output.rglob('*')) if p.is_file()}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    return manifest


def verify(spec_path, output):
    import tempfile
    with tempfile.TemporaryDirectory(prefix='crow-substitution-verify-') as tmp:
        expected = Path(tmp) / 'expected'
        build(spec_path, expected)
        wanted = {str(p.relative_to(expected)): sha(p) for p in expected.rglob('*') if p.is_file()}
        actual = {str(p.relative_to(output)): sha(p) for p in output.rglob('*') if p.is_file()}
        need(actual == wanted, 'Derivative differs from deterministic replay')
    return {'result': 'PASS', 'files': len(actual), 'production_ready': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify'])
    parser.add_argument('spec', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = globals()[args.action](args.spec, args.output)
    print(json.dumps({'status': result.get('status', result.get('result')), 'production_ready': False}))
