"""Native-source routing build/check and exact-subject independent acceptance.

This is not an autorouter. Editable KiCad boards own copper; isolated KiCad
refill, DRC and plots own derived outputs. A successful build is not acceptance.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile

import placement as p

CONTRACT = '01_docs/routing-contract.json'
MATING = '06_build/checkpoints/mating_clearance.json'
RECEIPT = '06_build/checkpoints/routed_board.json'
MANUAL = 'skills/pcb-design/procedures/routing/tooling.md'
STAGES = {'mating': 'KICAD-MATING-IMPORT', 'routing': 'KICAD-ROUTING'}
CRITERIA = {'mating': {'applicability', 'geometry', 'interfaces'},
            'routing': {'completeness', 'physical', 'electrical', 'interfaces', 'reproducibility'}}
# These findings still need independent review; they cannot hide copper defects.
NON_COPPER = {'lib_footprint_issues', 'lib_footprint_mismatch', 'silk_overlap',
              'silk_over_copper', 'text_height', 'text_thickness',
              'footprint_filters_mismatch'}


def forms(text):
    depth = 0; quoted = False; escaped = False; start = None; result = []
    p.need(text.lstrip().startswith('(kicad_pcb'), 'not a native PCB')
    for i, char in enumerate(text):
        if quoted:
            if escaped: escaped = False
            elif char == '\\': escaped = True
            elif char == '"': quoted = False
            continue
        if char == '"': quoted = True
        elif char == '(':
            if depth == 1: start = i
            depth += 1
        elif char == ')':
            depth -= 1
            p.need(depth >= 0, 'unbalanced native PCB')
            if depth == 1 and start is not None:
                result.append(text[start:i+1]); start = None
    p.need(depth == 0 and not quoted, 'incomplete native PCB')
    return result


def tag(form):
    return re.match(r'\(\s*([^\s()]+)', form)[1]


def normalized(path):
    # Collection order is non-geometric. Preserve every token, including UUIDs.
    return sorted(forms(path.read_text()))


def identity(path):
    # Full serialized footprint includes every pad property, layer and drill;
    # no bounding-box-only equivalence. Cosmetic footprint edits also need review.
    # Read/resave both inputs through the same native serializer: KiCad can emit
    # an omitted default font thickness explicitly after the first round trip.
    # Do not delete fields or normalize away geometry to accommodate that.
    with tempfile.TemporaryDirectory(prefix='vnext-route-identity-') as tmp:
        fresh = Path(tmp)/'identity.kicad_pcb'
        p.pcb.SaveBoard(str(fresh), p.pcb.LoadBoard(str(path)))
        native = fresh.read_text()
    return sorted(f for f in forms(native) if
                  tag(f) in {'footprint', 'layers', 'net', 'embedded_fonts'} or
                  (tag(f)=='zone' and '(keepout' in f) or
                  tag(f)=='group' or
                  (tag(f).startswith('gr_') and '(layer "Edge.Cuts")' in f))


def placement_receipt_path(contract):
    version=contract.get('version')
    p.need(version in (1,2,3), 'unsupported routing contract')
    if version==1:
        p.need('placement_receipt' not in contract,'version1 cannot select another placement receipt')
        return p.RECEIPT
    p.need(isinstance(contract.get('placement_receipt'),str) and contract['placement_receipt'],
           'version2 requires an explicit placement receipt')
    return contract['placement_receipt']


def mating_receipt_path(contract):
    if contract.get('version')==3:
        p.need(isinstance(contract.get('mating_receipt'),str) and contract['mating_receipt'],
               'version3 requires an explicit mating receipt')
        return contract['mating_receipt']
    return MATING


def upstream(project):
    contract = p.read(p.local(project, CONTRACT))
    receipt_name=placement_receipt_path(contract)
    p.need(p.sha(p.local(project, contract['authority'])) == contract['authority_sha256'],
           'routing authority changed')
    old = p.read(p.local(project, receipt_name))
    p.need(p.sha(p.local(project, receipt_name)) == contract['placement_receipt_sha256'],
           'placement receipt changed; routing re-adoption required')
    p.need(p.certificate(project, old['review']) == old, 'stale placement acceptance')
    review = review_json(project, old['review'])
    plan = p.read(p.local(project, review['plan']))
    return contract, review, plan


def base_subjects(project, contract):
    names = {CONTRACT, contract['authority'], placement_receipt_path(contract)}
    if contract.get('version')==3:names.add(contract['mating_requirements'])
    return {n: p.sha(p.local(project, n)) for n in sorted(names)}


def review_json(project, name):
    p.need(re.fullmatch(r'08_reviews/\d{4}-\d{2}-\d{2}[^/]*\.md', name), 'dated review required')
    blocks = re.findall(r'```json\s*\n(.*?)\n```', p.local(project, name).read_text(), re.S)
    p.need(len(blocks) == 1, 'one review JSON block required')
    return json.loads(blocks[0], object_pairs_hook=p.pairs)


def validate_review(project, review, kind, required):
    p.need(review.get('schema') == 1 and review.get('stage') == STAGES[kind]
           and review.get('verdict') == 'PASS', 'independent review not PASS')
    a, b = review['author'].strip(), review['reviewer'].strip()
    p.need(a and b and a.casefold() != b.casefold(), 'independent reviewer required')
    p.need(required.items() <= review['subjects'].items(), 'missing required review subjects')
    for name, digest in review['subjects'].items():
        p.need(p.sha(p.local(project, name)) == digest, 'stale review subject: ' + name)
    p.need(set(review['checks']) == CRITERIA[kind], 'review criteria differ')
    for criterion in review['checks'].values():
        p.need(criterion.get('verdict') == 'PASS' and criterion.get('rationale', '').strip()
               and criterion.get('evidence') and
               all(n in review['subjects'] for n in criterion['evidence']), 'incomplete review criterion')


def receipt(project, name, kind, historical=False):
    contract, placement_review, _ = upstream(project)
    review = review_json(project, name)
    subjects = base_subjects(project, contract)
    if kind == 'mating':
        p.need(contract.get('version')==3 or historical,
               'new mating acceptance requires version3 registered 3D contract')
        p.need(review.get('applicability') in {'applicable', 'not_applicable'},
               'unknown mating applicability')
        p.need(review.get('scope_evidence') and
               all(n in review['subjects'] for n in review['scope_evidence']), 'missing mating scope evidence')
        if review['applicability'] == 'applicable':
            p.need(review.get('geometry_evidence') and
                   all(n in review['subjects'] for n in review['geometry_evidence']), 'missing mating geometry evidence')
        if contract.get('version')==3:
            import mating_admission
            mechanical=mating_admission.verify(project,contract['mating_requirements'],review,placement_review,subjects)
            subjects.update(mechanical['subjects'])
    else:
        result = verify(project, review['manifest'], review['output'])
        p.need(all(v['route_complete'] for v in result['boards'].values()), 'routing is incomplete or has physical faults')
        subjects.update(result['subjects'])
    validate_review(project, review, kind, subjects)
    stage = 'mating-clearance' if kind == 'mating' else 'routing'
    spec = next(s['spec'] for s in p.read(p.ROOT/'skills/pcb-design/workflow/graph.json')['stages']
                if s['spec']['id'] == STAGES[kind])
    result = {'schema': 1, 'role': 'mating_clearance' if kind == 'mating' else 'routed_board',
            'review': name, 'review_sha256': p.sha(p.local(project, name)),
            'subjects': review['subjects'], 'stage_spec': spec,
            'tool_sha256': p.sha(Path(__file__)), 'placement_tool_sha256': p.sha(Path(p.__file__)),
            'stage_sha256': p.sha(p.ROOT/f'skills/pcb-design/workflow/stages/{stage}.md'),
            'manual_sha256': p.sha(p.ROOT/MANUAL), 'kicad_version': p.pcb.Version()}
    if kind=='mating' and contract.get('version')==3:result['mechanical']=mechanical
    return result


def check(project, kind):
    contract=p.read(p.local(project,CONTRACT))
    old = p.read(p.local(project, mating_receipt_path(contract) if kind == 'mating' else RECEIPT))
    p.need(old == receipt(project, old['review'], kind, historical=True), 'stale ' + kind + ' receipt')
    return old


def inputs(project, name):
    contract, placement_review, plan = upstream(project)
    check(project, 'mating')
    data = p.read(p.local(project, name))
    p.need(data.get('version') == 1 and set(data['boards']) == set(plan['boards']), 'board coverage differs')
    subjects = base_subjects(project, contract)
    for n in (name, mating_receipt_path(contract), *data.get('evidence', [])):
        subjects[n] = p.sha(p.local(project, n))
    for key, board in data['boards'].items():
        p.need(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', key), 'unsafe board key')
        p.need(set(board) == {'source', 'project'}, 'unsupported board source fields')
        source = p.local(project, board['source']); rules = p.local(project, board['project'])
        p.need(source.suffix == '.kicad_pcb' and rules.suffix == '.kicad_pro', 'native PCB/project required')
        p.need(not source.with_suffix('.kicad_dru').exists() and not rules.with_suffix('.kicad_dru').exists(),
               'custom rules unsupported by this pilot')
        accepted = p.local(project, placement_review['output']+'/'+key+'.kicad_pcb')
        p.need(identity(source) == identity(accepted), 'changed placement/pads/nets/outline: ' + key)
        settings = p.read(rules)['board']['design_settings']
        p.need(not settings.get('drc_exclusions'), 'DRC exclusions unsupported')
        for n in board.values(): subjects[n] = p.sha(p.local(project, n))
    return data, subjects


def drc_summary(report):
    p.need(report.get('coordinate_units') == 'mm', 'unexpected DRC units')
    p.need(not report.get('ignored_checks'), 'DRC checks were ignored')
    faults = [v for v in report['violations'] if v['type'] not in NON_COPPER]
    return {'route_complete': not faults and not report['unconnected_items'] and not report['schematic_parity'],
            'unconnected': len(report['unconnected_items']), 'physical_faults': len(faults),
            'review_findings': len(report['violations'])-len(faults),
            'violations_by_type': {t: sum(v['type'] == t for v in report['violations'])
                                   for t in sorted({v['type'] for v in report['violations']})}}


def grade_drc(path):
    r = p.read(path)
    # Date and source basename vary by replay directory; findings remain exact.
    return {k: v for k, v in r.items() if k not in {'date', 'source'}}


def produce(project, data, out):
    out.mkdir(parents=True, exist_ok=False); checks = {}
    for key, board in data['boards'].items():
        native = out/(key+'.kicad_pcb'); pro = out/(key+'.kicad_pro')
        shutil.copyfile(p.local(project, board['source']), native)
        rules = p.read(p.local(project, board['project']))
        settings = rules['board']['design_settings']
        # Re-enable every listed check, regardless of author's saved severity.
        settings['rule_severities'] = {k: 'error' for k in settings['rule_severities']}
        pro.write_text(json.dumps(rules, indent=2, sort_keys=True)+'\n')
        drc = out/(key+'-drc.json')
        p.command(['kicad-cli', 'pcb', 'drc', '--format', 'json', '--units', 'mm',
                   '--severity-all', '--all-track-errors', '--refill-zones', '--save-board',
                   '--output', str(drc), str(native)])
        p.need(identity(native) == identity(p.local(project, board['source'])), 'KiCad refill changed placement identity')
        checks[key] = drc_summary(p.read(drc))
        p.command(['kicad-cli', 'pcb', 'export', 'svg', '--mode-single', '--fit-page-to-board',
                   '--exclude-drawing-sheet', '--layers', 'F.Cu,B.Cu,F.Fab,Edge.Cuts',
                   '--output', str(out/(key+'.svg')), str(native)])
    (out/'checks.json').write_text(json.dumps(checks, indent=2, sort_keys=True)+'\n')
    return checks


def build(project, manifest, output):
    data, _ = inputs(project, manifest)
    return produce(project, data, p.local(project, output, exists=False))


def verify(project, manifest, output):
    data, subjects = inputs(project, manifest)
    with tempfile.TemporaryDirectory(prefix='vnext-routing-replay-') as tmp:
        fresh = Path(tmp)/'out'; checks = produce(project, data, fresh)
        for key in data['boards']:
            for ext in ('.kicad_pcb', '.kicad_pro', '.svg', '-drc.json'):
                name = output+'/'+key+ext; actual = p.local(project, name); new = fresh/(key+ext)
                if ext == '.kicad_pcb': equal = normalized(actual) == normalized(new)
                elif ext == '.svg': equal = p.canonical_svg(actual) == p.canonical_svg(new)
                elif ext == '-drc.json': equal = grade_drc(actual) == grade_drc(new)
                else: equal = actual.read_bytes() == new.read_bytes()
                p.need(equal, 'stale routing artifact: '+name); subjects[name] = p.sha(actual)
        name = output+'/checks.json'
        p.need(p.read(p.local(project, name)) == checks, 'forged routing checks')
        subjects[name] = p.sha(p.local(project, name))
    return {'boards': checks, 'subjects': subjects, 'scope': 'native replay/DRC, not engineering acceptance'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify', 'issue', 'check'])
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--kind', choices=['routing', 'mating'], default='routing')
    for name in ('manifest', 'output', 'review'): parser.add_argument('--'+name)
    a = parser.parse_args(); project = a.project.resolve()
    try:
        if a.action in {'build', 'verify'}:
            p.need(a.kind == 'routing' and a.manifest and a.output, 'routing manifest/output required')
            result = (build if a.action == 'build' else verify)(project, a.manifest, a.output)
        elif a.action == 'check': result = check(project, a.kind)
        else:
            result = receipt(project, a.review, a.kind)
            contract=p.read(p.local(project,CONTRACT))
            target = p.local(project, mating_receipt_path(contract) if a.kind == 'mating' else RECEIPT, exists=False)
            p.need(not target.exists(), 'refusing existing receipt')
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
        print(json.dumps(result, indent=2, sort_keys=True)); return 0
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print('Routing refused: '+str(exc), file=sys.stderr); return 1


if __name__ == '__main__': sys.exit(main())
