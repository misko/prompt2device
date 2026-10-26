"""Native layout finishing pilot: strict replay and independent seal, not fabrication."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

import routing as r

p = r.p
CONTRACT = '01_docs/layout-seal-contract.json'
RECEIPT = '06_build/checkpoints/layout_sealed.json'
STAGE = 'skills/pcb-design/workflow/stages/layout-seal.md'
MANUAL = 'skills/pcb-design/procedures/layout-seal/tooling.md'
CRITERIA = {'identity', 'physical', 'markings', 'engineering', 'reproducibility'}
DOCUMENT_LAYERS = {'"F.SilkS"', '"B.SilkS"', '"F.Fab"', '"B.Fab"', '"Dwgs.User"'}
LAYERS = ('F.Cu', 'B.Cu', 'F.SilkS', 'B.SilkS', 'F.Fab', 'B.Fab')


def parse(text):
    """Small lossless-token s-expression reader; quoted strings remain quoted."""
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+', text)
    stack = []; result = []
    for token in tokens:
        if token == '(':
            child = []
            (stack[-1] if stack else result).append(child); stack.append(child)
        elif token == ')':
            p.need(stack, 'unbalanced native expression'); stack.pop()
        else:
            p.need(stack, 'token outside native expression'); stack[-1].append(token)
    p.need(not stack and len(result) == 1, 'incomplete native expression')
    return result[0]


def layer(node):
    return next((v[1] for v in node if isinstance(v, list) and v[:1] == ['layer']), None)


def physical(node):
    tag = node[0]
    if tag in {'fp_text', 'fp_text_box', 'fp_line', 'fp_rect', 'fp_arc', 'fp_circle', 'fp_poly',
               'gr_text', 'gr_text_box', 'gr_line', 'gr_rect', 'gr_arc', 'gr_circle', 'gr_poly'}:
        if layer(node) in DOCUMENT_LAYERS:
            # Legacy reference/value text content remains part of identity.
            if tag == 'fp_text' and node[1] in {'reference', 'value'}:
                return node[:3]
            return None
    if tag == 'property' and node[1] in {'"Reference"', '"Value"'} and layer(node) in DOCUMENT_LAYERS:
        # Only presentation changes are allowed, never ref/value strings.
        return [*node[:3], *[v for v in node[3:] if not isinstance(v, list) or
                             v[0] not in {'at', 'layer', 'effects', 'unlocked', 'hide'}]]
    if tag == 'footprint':
        children = [physical(v) if isinstance(v, list) else v for v in node]
        return [v for v in children if v is not None]
    return node


def physical_identity(path):
    # Compare authored tokens. Load/save may repair net assignments, which must
    # never erase a source delta before this admission comparison.
    nodes = [physical(parse(f)) for f in r.forms(path.read_text())]
    return sorted(json.dumps(n, separators=(',', ':')) for n in nodes if n is not None)


def classify(base, candidate):
    if physical_identity(base) != physical_identity(candidate):
        return 'engineering_change'
    return 'unchanged' if r.normalized(base) == r.normalized(candidate) else 'document_only'


def upstream(project):
    c = p.read(p.local(project, CONTRACT))
    p.need(c.get('version') in (1, 2), 'unsupported layout-seal contract')
    p.need(p.sha(p.local(project, c['authority'])) == c['authority_sha256'], 'layout authority changed')
    p.need(p.sha(p.local(project, r.RECEIPT)) == c['routing_receipt_sha256'],
           'routing receipt changed; explicit layout re-adoption required')
    old = r.check(project, 'routing')  # Never trust a hash or STATUS instead of the owning check.
    review = r.review_json(project, old['review'])
    baseline = p.read(p.local(project, review['manifest']))
    obligations = c.get('obligations')
    p.need(isinstance(obligations, list) and obligations, 'explicit engineering obligations required')
    ids = [v['id'] for v in obligations]
    p.need(len(set(ids)) == len(ids) and all(ids), 'duplicate or empty obligation')
    for v in obligations:
        p.need(v.get('requirement') and v.get('source'), 'obligation needs requirement authority')
        p.local(project, v['source'])
    return c, baseline


def resources(project, mapping, source=None):
    p.need(isinstance(mapping, dict), 'resource map required')
    for dest, resource_source in mapping.items():
        p.local(project, dest, exists=False); p.local(project, resource_source)
        p.need(dest == 'fp-lib-table' or (Path(dest).suffix == '.kicad_mod' and
               any(part.endswith('.pretty') for part in Path(dest).parts)), 'unsupported resource: '+dest)
        if Path(dest).suffix == '.kicad_mod':
            module = parse(p.local(project, resource_source).read_text())
            p.need(module[0] == 'footprint', 'native footprint library required')
            # KiCad's parser tolerates a board-only footprint position in a
            # library, but FootprintSave drops it. Do not accept that unstable
            # encoding merely because the exact instance has clean DRC.
            p.need(not any(isinstance(v, list) and v[:1] == ['at'] for v in module[1:]),
                   'board-only footprint position is not valid library source: '+dest)
    libraries = {}
    if 'fp-lib-table' in mapping:
        table = parse(p.local(project, mapping['fp-lib-table']).read_text())
        p.need(table[0] == 'fp_lib_table', 'invalid library table')
        names = set()
        for entry in table[1:]:
            if entry[0] == 'version': continue
            p.need(entry[0] == 'lib', 'unsupported library table entry')
            fields = {x[0]: x[1] for x in entry[1:]}
            name = fields['name']; uri = json.loads(fields['uri'])
            p.need(name not in names and fields['type'] == '"KiCad"', 'duplicate/non-native library')
            names.add(name)
            p.need(uri.startswith('${KIPRJMOD}/'), 'library must be project-local')
            relative = uri[len('${KIPRJMOD}/'):]
            libraries[json.loads(name)] = relative
            p.local(project, relative, exists=False)
            p.need(relative.endswith('.pretty') and any(n.startswith(relative+'/') for n in mapping),
                   'unbound library directory')
            p.need(fields.get('options', '""') == '""', 'library options unsupported')
    if source is not None:
        for form in r.forms(source.read_text()):
            node = parse(form)
            if node[0] != 'footprint': continue
            ident = json.loads(node[1])
            if not ident:
                # Native board-only mechanical holes have no library lookup.
                pads = [v for v in node if isinstance(v, list) and v[:1] == ['pad']]
                p.need(pads and all(v[2] == 'np_thru_hole' and
                       not any(isinstance(x, list) and x[:1] == ['net'] for x in v) for v in pads),
                       'unqualified electrical footprint unsupported')
                continue
            p.need(':' in ident, 'library-qualified footprint required')
            nickname, name = ident.split(':', 1)
            p.need(nickname in libraries and libraries[nickname]+'/'+name+'.kicad_mod' in mapping,
                   'unbound footprint library resource: '+ident)


def closure_status(contract, data):
    closure = data.get('closure', {})
    p.need(set(closure) == {v['id'] for v in contract['obligations']}, 'obligation coverage differs')
    for row in closure.values():
        p.need(row.get('status') in {'open', 'closed', 'not_applicable'} and
               isinstance(row.get('rationale'), str) and row['rationale'].strip(),
               'invalid obligation disposition')
        p.need(isinstance(row.get('evidence'), list), 'obligation evidence list required')
        if row['status'] != 'open': p.need(row['evidence'], 'closed obligation needs evidence')
    return all(v['status'] != 'open' for v in closure.values())


def schematic_sources(project, board_keys):
    """Select native schematics from the upstream-checked flat producer, not user aliases."""
    import native_import as imported
    import schematic_assembly as assembly
    contract_name = '01_docs/schematic-contract.json'
    contract = p.read(p.local(project, contract_name))
    p.need(contract.get('version') == 2 and contract.get('rf') is False,
           'layout parity requires adopted flat imported schematics')
    manifest = p.read(p.local(project, contract['manifest']))
    p.need(set(manifest['boards']) == set(board_keys), 'schematic/PCB coverage differs')
    names = {contract_name, contract['manifest'], contract['expected']}
    result = {}
    for key, row in manifest['boards'].items():
        p.need(assembly.producer(row) == 'imported', 'layout parity producer unsupported')
        declaration = imported.declaration(project, p.local(project, row['source']))
        result[key] = declaration['schematic']
        names.update((row['source'], row['membership'], declaration['schematic'], declaration['intent']))
        names.update(declaration['producer']['inputs']); names.update(declaration['context'])
    for name in names: p.local(project, name)
    return result, names


def inputs(project, name):
    c, base = upstream(project); data = p.read(p.local(project, name))
    p.need(data.get('version') == 1 and set(data['boards']) == set(base['boards']), 'board coverage differs')
    closure_status(c, data)
    names = {CONTRACT, c['authority'], r.RECEIPT, name}
    names.update(v['source'] for v in c['obligations'])
    names.update(data.get('evidence', []))
    names.update(n for v in data['closure'].values() for n in v['evidence'])
    if c['version'] == 2:
        schematics, schematic_names = schematic_sources(project, data['boards'])
        p.need(data.get('schematics') == schematics, 'missing or wrong accepted native schematics')
        names.update(schematic_names)
    else:
        p.need('schematics' not in data, 'native parity requires explicit version2 adoption')
    for key, board in data['boards'].items():
        p.need(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', key), 'unsafe board key')
        p.need(set(board) == {'source', 'project', 'resources'}, 'unsupported board fields')
        source = p.local(project, board['source']); pro = p.local(project, board['project'])
        p.need(source.suffix == '.kicad_pcb' and pro.suffix == '.kicad_pro', 'native source/settings required')
        p.need(not source.with_suffix('.kicad_dru').exists() and not pro.with_suffix('.kicad_dru').exists(),
               'custom rules unsupported')
        p.need(classify(p.local(project, base['boards'][key]['source']), source) != 'engineering_change',
               'engineering change: reopen routing/placement/stack review for '+key)
        old = p.read(p.local(project, base['boards'][key]['project']))
        new = p.read(pro)
        p.need(new == old, 'project settings changed; explicit engineering re-adoption required')
        p.need(not new['board']['design_settings'].get('drc_exclusions'), 'DRC exclusions unsupported')
        resources(project, board['resources'], source)
        names.update([board['source'], board['project'], *board['resources'].values()])
    return c, data, {n: p.sha(p.local(project, n)) for n in sorted(names)}


def strict_summary(report):
    result = r.drc_summary(report)
    result['layout_clean'] = result['route_complete'] and not report['violations']
    return result


def produce(project, data, out):
    out.mkdir(parents=True, exist_ok=False); checks = {}
    for key, board in data['boards'].items():
        dest = out/key; dest.mkdir()
        # Match routing's native producer flags, not its permissive non-copper predicate.
        result_dir = dest/'native'
        # Resources need KIPRJMOD to be the board directory.
        result_dir.mkdir()
        for name, source in board['resources'].items():
            target = result_dir/name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p.local(project, source), target)
        native = result_dir/(key+'.kicad_pcb'); pro = native.with_suffix('.kicad_pro')
        shutil.copyfile(p.local(project, board['source']), native)
        settings = p.read(p.local(project, board['project']))
        rules = settings['board']['design_settings']
        rules['rule_severities'] = {k: 'error' for k in rules['rule_severities']}
        pro.write_text(json.dumps(settings, indent=2, sort_keys=True)+'\n')
        report = result_dir/(key+'-drc.json')
        command = ['kicad-cli', 'pcb', 'drc', '--format', 'json', '--units', 'mm', '--severity-all',
                   '--all-track-errors', '--refill-zones', '--save-board']
        if 'schematics' in data:
            schematic = p.local(project, data['schematics'][key])
            shutil.copyfile(schematic, native.with_suffix('.kicad_sch'))
            command += ['--schematic-parity', '--output', report.name, native.name]
            process = subprocess.run(command, cwd=result_dir, capture_output=True, text=True, timeout=90)
            p.need(process.returncode == 0, 'native layout DRC execution failed: '+process.stderr+process.stdout)
            execution = dict(version=1, command=command, exit_code=process.returncode,
                             native_source_sha256=p.sha(p.local(project, board['source'])),
                             schematic_sha256=p.sha(schematic))
            (result_dir/'drc-execution.json').write_text(json.dumps(execution, indent=2, sort_keys=True)+'\n')
        else:
            p.command(command + ['--output', str(report), str(native)])
        p.need(r.identity(native) == r.identity(p.local(project, board['source'])), 'refill changed identity')
        checks[key] = strict_summary(p.read(report))
        for layer_name in LAYERS:
            p.command(['kicad-cli', 'pcb', 'export', 'svg', '--mode-single', '--fit-page-to-board',
                       '--exclude-drawing-sheet', '--layers', layer_name+',Edge.Cuts',
                       '--output', str(result_dir/(layer_name+'.svg')), str(native)])
    (out/'checks.json').write_text(json.dumps(checks, indent=2, sort_keys=True)+'\n')
    return checks


def build(project, name, output):
    c, data, _ = inputs(project, name)
    checks = produce(project, data, p.local(project, output, exists=False))
    return {'boards': checks, 'engineering_closed': closure_status(c, data), 'accepted': False}


def verify(project, name, output):
    c, data, subjects = inputs(project, name)
    with tempfile.TemporaryDirectory(prefix='vnext-layout-replay-') as tmp:
        fresh = Path(tmp)/'out'; checks = produce(project, data, fresh)
        inventory = lambda root: {f.relative_to(root).as_posix() for f in root.rglob('*')
                                  if f.is_file() and f.suffix != '.kicad_prl'}
        actual_dir = p.local(project, output, exists=False)
        p.need(actual_dir.is_dir(), 'layout output directory missing')
        p.need(inventory(fresh) == inventory(actual_dir), 'layout output inventory differs')
        for file in fresh.rglob('*'):
            if not file.is_file() or file.suffix == '.kicad_prl': continue
            n = output+'/'+file.relative_to(fresh).as_posix(); actual = p.local(project, n)
            if file.suffix == '.kicad_pcb': equal = r.normalized(actual) == r.normalized(file)
            elif file.name.endswith('-drc.json'): equal = r.grade_drc(actual) == r.grade_drc(file)
            elif file.suffix == '.svg': equal = p.canonical_svg(actual) == p.canonical_svg(file)
            else: equal = actual.read_bytes() == file.read_bytes()
            p.need(equal, 'stale layout artifact: '+n); subjects[n] = p.sha(actual)
    return {'boards': checks, 'engineering_closed': closure_status(c, data), 'subjects': subjects,
            'scope': 'strict native replay and DRC, not independent engineering acceptance'}


def validate_review(project, review, required, obligation_ids):
    p.need(review.get('schema') == 1 and review.get('stage') == 'KICAD-LAYOUT-SEAL' and
           review.get('verdict') == 'PASS', 'layout review not PASS')
    a = review.get('author', '').strip(); b = review.get('reviewer', '').strip()
    p.need(a and b and a.casefold() != b.casefold(), 'independent reviewer required')
    p.need(required.items() <= review.get('subjects', {}).items(), 'missing review subjects')
    for n, digest in review['subjects'].items():
        p.need(p.sha(p.local(project, n)) == digest, 'stale review subject: '+n)
    p.need(set(review.get('checks', {})) == CRITERIA, 'layout review criteria differ')
    p.need(set(review.get('obligations', {})) == set(obligation_ids), 'review obligation coverage differs')
    for row in [*review['checks'].values(), *review['obligations'].values()]:
        p.need(row.get('verdict') == 'PASS' and isinstance(row.get('rationale'), str) and
               row['rationale'].strip() and row.get('evidence') and
               all(n in review['subjects'] for n in row['evidence']), 'incomplete independent disposition')


def certificate(project, name, historical=False):
    review = r.review_json(project, name)
    result = verify(project, review['manifest'], review['output'])
    p.need(all(v['layout_clean'] for v in result['boards'].values()), 'layout has unresolved DRC findings')
    p.need(result['engineering_closed'], 'engineering obligations remain open')
    c = p.read(p.local(project, CONTRACT))
    p.need(c.get('version') == 2 or historical, 'new layout acceptance requires version2 native parity')
    validate_review(project, review, result['subjects'], [v['id'] for v in c['obligations']])
    data = p.read(p.local(project, review['manifest']))
    for key, row in data['closure'].items():
        p.need(set(row['evidence']) <= set(review['obligations'][key]['evidence']),
               'review must disposition closure evidence: '+key)
    views = {review['output']+'/'+key+'/native/'+layer+'.svg'
             for key in data['boards'] for layer in ('F.SilkS','B.SilkS','F.Fab','B.Fab')}
    p.need(views <= set(review['checks']['markings']['evidence']), 'markings review missing board views')
    spec = next(s['spec'] for s in p.read(p.ROOT/'skills/pcb-design/workflow/graph.json')['stages']
                if s['spec']['id'] == 'KICAD-LAYOUT-SEAL')
    return {'schema': 1, 'role': 'layout_sealed', 'review': name, 'review_sha256': p.sha(p.local(project, name)),
            'subjects': review['subjects'], 'stage_spec': spec, 'tool_sha256': p.sha(Path(__file__)),
            'routing_tool_sha256': p.sha(Path(r.__file__)), 'placement_tool_sha256': p.sha(Path(p.__file__)),
            'stage_sha256': p.sha(p.ROOT/STAGE), 'manual_sha256': p.sha(p.ROOT/MANUAL),
            'kicad_version': p.pcb.Version()}


def check(project):
    old = p.read(p.local(project, RECEIPT))
    p.need(old == certificate(project, old['review'], historical=True), 'stale layout-seal receipt')
    return old


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify', 'issue', 'check'])
    parser.add_argument('--project', type=Path, required=True)
    for name in ('manifest', 'output', 'review'): parser.add_argument('--'+name)
    a = parser.parse_args(); project = a.project.resolve()
    try:
        if a.action in {'build', 'verify'}:
            p.need(a.manifest and a.output, 'manifest and output required')
            result = (build if a.action == 'build' else verify)(project, a.manifest, a.output)
        elif a.action == 'check': result = check(project)
        else:
            result = certificate(project, a.review)
            dest = p.local(project, RECEIPT, exists=False); dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open('x') as f: json.dump(result, f, indent=2, sort_keys=True)
        print(json.dumps(result, indent=2)); return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print('Layout seal refused: '+str(exc), file=sys.stderr); return 1


if __name__ == '__main__': sys.exit(main())
