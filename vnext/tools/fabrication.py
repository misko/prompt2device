"""Joined fabrication staging and independent admission; never order authority."""
import argparse
from datetime import date
import json
from pathlib import Path
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
import fab_replay as replay
import fab_population as population
import part_recheck

seal = replay.s
p = seal.p
CONTRACT = '01_docs/fabrication-contract.json'
RECEIPT = '06_build/checkpoints/fabrication_staged.json'
STAGE = 'skills/pcb-design/workflow/stages/fabrication.md'
MANUAL = 'skills/pcb-design/procedures/fabrication/tooling.md'
TOOLS = (*replay.TOOL_NAMES, 'fab_population.py', 'part_recheck.py', 'fabrication.py')
CRITERIA = {'source', 'population', 'sourcing', 'process', 'mechanical', 'instructions', 'handoff'}
HOLDS = ['assembly verification', 'vendor matching/orientation and allocation',
         'actual uploader process confirmation', 'release review and seal']


def order_holds(manifest, pop):
    modes = {r['mode'] for board in pop['boards'].values() for r in board['population'].values()}
    handling = [mode+' handling/execution and inspection confirmation'
                for mode in ('manual', 'consigned') if mode in modes]
    return HOLDS+handling+manifest['order_holds']


def evidence(root, names, subjects):
    p.need(isinstance(names, list) and names and all(isinstance(n, str) for n in names),
           'retained evidence list required')
    for n in names:
        subjects[n] = p.sha(p.local(root, n))


def stock(root, name, rows, subjects):
    """Grade supplied observations against summed mixed-board demand, not allocation."""
    facts = p.read(p.local(root, name)); subjects[name] = p.sha(p.local(root, name))
    p.need(facts.get('version') == 1 and isinstance(facts.get('parts'), list), 'sourcing facts required')
    as_of = date.fromisoformat(facts['as_of'])
    p.need(as_of <= date.today(), 'sourcing as-of date is in the future')
    demand = {}
    for row in rows:
        if not row['demand']: continue
        key = (row['manufacturer'], row['mpn'])
        item = demand.setdefault(key, {'quantity': 0, 'contributors': []})
        item['quantity'] += row['demand']
        item['contributors'].append({'board': row['board'], 'reference': row['reference']})
    indexed = {}
    for item in facts['parts']:
        key = (item['manufacturer'], item['mpn'])
        p.need(key not in indexed, 'duplicate sourcing identity')
        indexed[key] = item
    p.need(set(indexed) == set(demand), 'sourcing identity coverage differs')
    result = []
    for key, needed in sorted(demand.items()):
        item = indexed[key]
        p.need(isinstance(item.get('package'), str) and item['package'].strip(), 'exact stock package required')
        p.need(type(item.get('quantity')) is int and item['quantity'] == needed['quantity'],
               'whole-system sourcing quantity differs')
        sort = lambda values: sorted(values, key=lambda v: (v['board'], v['reference']))
        p.need(sort(item['contributors']) == sort(needed['contributors']), 'stock contributors differ')
        evidence(root, item['jlc_evidence'], subjects)
        offers = item.get('offers')
        p.need(isinstance(offers, list) and offers, 'exact offers required')
        adequate = []
        for offer in offers:
            evidence(root, offer['evidence'], subjects)
            observed = date.fromisoformat(offer['checked_on'])
            p.need(observed <= as_of, 'offer postdates sourcing as-of date')
            if 'availability_verified' in offer:
                p.need(type(offer['availability_verified']) is bool, 'availability_verified must be boolean')
            if 'lookup_state' in offer:
                p.need(offer['lookup_state'] in {
                    'verified', 'exact_matches', 'exact_identity_observed', 'lookup_failed',
                    'stale', 'no_exact_match', 'no_exact_evidence', 'inventory_unverified', 'unverified'},
                    'unknown stock lookup state')
                # Discovery/identity alone is not inventory verification. Retain
                # these observations but do not let them qualify a stocked part.
                if offer['lookup_state'] != 'verified': continue
            for field in ('source_kind', 'evidence_kind'):
                if field in offer:
                    p.need(offer[field] in {'supplier_page', 'exact_supplier_page', 'aggregate_snapshot',
                                          'search_snippet'}, 'unknown stock evidence kind')
            if part_recheck.adequate_offer(offer, item, needed['quantity']): adequate.append(offer['supplier_url'])
        p.need(adequate, 'no adequate exact offer: '+key[1])
        result.append(dict(manufacturer=key[0], mpn=key[1], **needed, adequate_offers=adequate))
    return {'as_of': facts['as_of'], 'demand': result, 'scope': 'supplied observations; not allocation or live stock'}


def policy(root, manifest):
    p.need(set(manifest) == {'version', 'population', 'sourcing', 'boards', 'handoff', 'order_holds'}
           and manifest['version'] == 1, 'unsupported fabrication manifest')
    pop_name = manifest['population']; pop = p.read(p.local(root, pop_name))
    p.need('assembly' in pop, 'explicit factory/consigned assembly mapping required')
    result = population.data(root, pop)
    population.assembly_files(root, pop, result)
    subjects = dict(result['subjects']); subjects[pop_name] = p.sha(p.local(root, pop_name))
    p.need(set(manifest['boards']) == set(pop['boards']), 'fabrication policy board coverage differs')
    for key, row in manifest['boards'].items():
        p.need(set(row) == {'source_sha256', 'process', 'mechanical_views', 'instructions'},
               'unsupported board fabrication policy')
        native = p.local(root, pop['boards'][key]['source'])
        p.need(row['source_sha256'] == p.sha(native), 'stale mechanical/process source: '+key)
        board = p.pcb.LoadBoard(str(native)); process = row['process']
        p.need(set(process) == {'copper_layers', 'thickness_mm', 'selections', 'evidence'},
               'explicit process selections required')
        p.need(type(process['copper_layers']) is int and process['copper_layers'] == board.GetCopperLayerCount(),
               'process copper layer count differs')
        p.need(abs(p.number(process['thickness_mm']) - board.GetDesignSettings().GetBoardThickness()/1e6) < 1e-6,
               'process thickness differs')
        p.need(isinstance(process['selections'], dict) and process['selections'] and
               all(isinstance(k, str) and k.strip() and isinstance(v, str) and v.strip()
                   for k, v in process['selections'].items()), 'nonempty process selections required')
        for names in (process['evidence'], row['mechanical_views'], row['instructions']):
            evidence(root, names, subjects)
    evidence(root, manifest['handoff'], subjects)
    p.need(isinstance(manifest['order_holds'], list), 'explicit order holds required')
    ids = set()
    for hold in manifest['order_holds']:
        p.need(set(hold) == {'id', 'reason', 'evidence'} and isinstance(hold['id'], str) and
               hold['id'].strip() and hold['id'] not in ids and isinstance(hold['reason'], str)
               and hold['reason'].strip(), 'invalid/duplicate order hold')
        ids.add(hold['id']); evidence(root, hold['evidence'], subjects)
    sourcing = stock(root, manifest['sourcing'], result['population'], subjects)
    return pop, subjects, sourcing


def inventory(root):
    # Unlike the inner native bundle, retain every nested bundle.json as a subject.
    p.need(root.is_dir() and not root.is_symlink(), 'missing/linked fabrication package')
    found = {}
    for file in sorted(root.rglob('*')):
        p.need(not file.is_symlink(), 'linked fabrication package member')
        name = file.relative_to(root).as_posix()
        if file.is_file() and name != 'fabrication.json': found[name] = p.sha(file)
    return found


def parity(package, pop):
    bundle = p.read(package/'native/bundle.json')
    p.need(bundle.get('schematics') is not None, 'complete schematic replay required')
    p.need(set(bundle['boards']) == set(pop['boards']), 'native/population board coverage differs')
    design = package/'native/design'
    manifest, _ = replay.design_sources(design, bundle['schematics'], bundle['boards'])
    for key, row in pop['boards'].items():
        native = p.local(package/'native', bundle['boards'][key]['native'])
        decl = replay.imported.declaration(design, p.local(design, manifest['boards'][key]['source']))
        p.need(p.sha(native) == p.sha(p.local(package/'inputs', row['source'])),
               'population/native source differs: '+key)
        p.need(p.sha(p.local(design, decl['intent'])) == p.sha(p.local(package/'inputs', row['intent'])),
               'population/schematic intent differs: '+key)


def produce(project, boards, schematics, manifest_name, output, context=None):
    """Internal isolated fixture seam, never upstream acceptance or a stage receipt."""
    manifest = p.read(p.local(project, manifest_name))
    pop, subjects, sourcing = policy(project, manifest)
    subjects[manifest_name] = p.sha(p.local(project, manifest_name))
    if context is not None:
        for n, digest in context.items():
            p.need(p.sha(p.local(project, n)) == digest, 'stale adoption evidence: '+n)
        subjects.update(context)
    p.need(not output.exists(), 'refusing existing fabrication output')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='vnext-fabrication-', dir=output.parent) as tmp:
        stage = Path(tmp)/'package'; stage.mkdir()
        replay.produce(project, boards, stage/'native', context, schematics)
        for n in subjects:
            dest = p.local(stage/'inputs', n, exists=False); dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(p.local(project, n), dest)
        parity(stage, pop)
        population.produce(stage/'inputs', pop, stage/'assembly')
        dest = stage/'tools'; dest.mkdir()
        for name in TOOLS: shutil.copyfile(Path(__file__).parent/name, dest/name)
        record = dict(version=1, manifest=manifest_name, context=context, input_subjects=subjects,
                      sourcing=sourcing, order_holds=order_holds(manifest, pop),
                      accepted=False, order_status='DO-NOT-ORDER', files=inventory(stage))
        (stage/'fabrication.json').write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
        stage.rename(output)
    return record


def verify_package(package):
    record = p.read(p.local(package, 'fabrication.json'))
    p.need(record.get('version') == 1 and record.get('accepted') is False and
           record.get('order_status') == 'DO-NOT-ORDER', 'unsupported fabrication record')
    p.need(inventory(package) == record['files'], 'fabrication inventory/hash differs')
    p.need({f.name for f in package.iterdir()} == {'native', 'inputs', 'assembly', 'tools', 'fabrication.json'},
           'fabrication root census differs')
    tool_dir = package/'tools'
    p.need(tool_dir.is_dir() and {f.name for f in tool_dir.iterdir()} == set(TOOLS), 'fabrication tool census differs')
    for name in TOOLS:
        p.need(p.sha(tool_dir/name) == p.sha(Path(__file__).parent/name), 'fabrication tool identity differs: '+name)
    inputs = package/'inputs'; manifest = p.read(p.local(inputs, record['manifest']))
    pop, subjects, sourcing = policy(inputs, manifest)
    subjects[record['manifest']] = p.sha(p.local(inputs, record['manifest']))
    context = record['context']
    if context is not None:
        for n, digest in context.items():
            p.need(p.sha(p.local(inputs, n)) == digest, 'stale copied adoption evidence: '+n)
        subjects.update(context)
    actual = {f.relative_to(inputs).as_posix(): p.sha(f) for f in inputs.rglob('*') if f.is_file()}
    p.need(actual == subjects == record['input_subjects'], 'fabrication input census/hash differs')
    p.need(sourcing == record['sourcing'] and record['order_holds'] == order_holds(manifest, pop),
           'fabrication policy result differs')
    parity(package, pop)
    p.need(p.read(package/'native/bundle.json')['context'] == context, 'native adoption context differs')
    population.verify(inputs, pop, package/'assembly')
    replay.verify(package/'native')
    return {'boards': sorted(pop['boards']), 'sourcing': sourcing, 'accepted': False,
            'order_status': 'DO-NOT-ORDER'}


def upstream(project):
    contract = p.read(p.local(project, CONTRACT))
    p.need(set(contract) == {'version', 'authority', 'authority_sha256', 'layout_receipt_sha256',
                            'board_quantities'} and contract['version'] == 1, 'unsupported fabrication contract')
    p.need(p.sha(p.local(project, contract['authority'])) == contract['authority_sha256'],
           'fabrication authority changed')
    p.need(p.sha(p.local(project, seal.RECEIPT)) == contract['layout_receipt_sha256'],
           'layout receipt changed; explicit fabrication re-adoption required')
    receipt = seal.check(project)
    review = seal.r.review_json(project, receipt['review'])
    layout = p.read(p.local(project, review['manifest'])); boards = {}
    quantities = contract['board_quantities']
    p.need(set(quantities) == set(layout['boards']) and
           all(type(v) is int and v > 0 for v in quantities.values()), 'adopted board quantities required')
    for key, row in layout['boards'].items():
        base = review['output']+'/'+key+'/native/'
        boards[key] = dict(source=base+key+'.kicad_pcb', project=base+key+'.kicad_pro',
                           resources={n: base+n for n in row['resources']})
    schematic = p.read(p.local(project, '01_docs/schematic-contract.json'))
    spec = {n: schematic[n] for n in ('manifest', 'expected')}
    context = {n: p.sha(p.local(project, n)) for n in
               (CONTRACT, contract['authority'], seal.RECEIPT, receipt['review'])}
    return contract, boards, spec, context


def live_inputs(project, name):
    contract, boards, spec, context = upstream(project)
    manifest = p.read(p.local(project, name)); pop, subjects, _ = policy(project, manifest)
    subjects[name] = p.sha(p.local(project, name))
    subjects.update(context)
    p.need(set(pop['boards']) == set(boards), 'accepted board coverage differs')
    for key, row in pop['boards'].items():
        p.need(row['source'] == boards[key]['source'] and row['quantity'] == contract['board_quantities'][key],
               'population source or adopted quantity differs: '+key)
    return boards, spec, context, subjects


def build(project, name, output):
    boards, spec, context, _ = live_inputs(project, name)
    return produce(project, boards, spec, name, p.local(project, output, exists=False), context)


def verify(project, name, output):
    boards, spec, context, subjects = live_inputs(project, name)
    package = p.local(project, output, exists=False); record = p.read(package/'fabrication.json')
    p.need(record['manifest'] == name and record['context'] == context and
           record['input_subjects'] == subjects, 'stale fabrication inputs/adoption')
    bundle = p.read(package/'native/bundle.json')
    p.need(bundle['context'] == context and bundle['schematics'] == spec and
           set(bundle['boards']) == set(boards), 'stale native bundle context')
    # Check exact adopted native settings/resources, not just a self-consistent archive.
    for key, row in boards.items():
        entry = bundle['boards'][key]
        mapping = {entry['native']: row['source'], entry['project']: row['project']}
        mapping.update({'source/'+key+'/'+n: src for n, src in row['resources'].items()})
        for dest, source in mapping.items():
            p.need(p.sha(p.local(package/'native', dest)) == p.sha(p.local(project, source)),
                   'archive differs from accepted native input: '+key)
    _, names = replay.design_sources(project, spec, boards)
    for n in names:
        p.need(p.sha(p.local(project, n)) == p.sha(p.local(package/'native/design', n)),
               'archive differs from accepted circuit input: '+n)
    result = verify_package(package)
    subjects.update(context)
    subjects.update({output+'/'+n: digest for n, digest in inventory(package).items()})
    subjects[output+'/fabrication.json'] = p.sha(package/'fabrication.json')
    return {**result, 'subjects': subjects}


def validate_review(project, review, required, manifest):
    p.need(review.get('schema') == 1 and review.get('stage') == 'JLC-FABRICATION' and
           review.get('verdict') == 'PASS', 'fabrication review not PASS')
    a = review.get('author', '').strip(); b = review.get('reviewer', '').strip()
    p.need(a and b and a.casefold() != b.casefold(), 'independent reviewer required')
    p.need(required.items() <= review.get('subjects', {}).items(), 'missing fabrication review subjects')
    for n, digest in review['subjects'].items():
        p.need(p.sha(p.local(project, n)) == digest, 'stale fabrication review subject: '+n)
    p.need(set(review.get('checks', {})) == CRITERIA, 'fabrication review criteria differ')
    for row in review['checks'].values():
        p.need(row.get('verdict') == 'PASS' and isinstance(row.get('rationale'), str) and
               row['rationale'].strip() and isinstance(row.get('evidence'), list) and row['evidence'] and
               all(n in review['subjects'] for n in row['evidence']), 'incomplete independent fabrication disposition')
    for key, board in manifest['boards'].items():
        for criterion, names in (('process', board['process']['evidence']),
                                 ('mechanical', board['mechanical_views']), ('instructions', board['instructions'])):
            p.need(set(names) <= set(review['checks'][criterion]['evidence']),
                   'review omits '+key+' '+criterion+' evidence')
    p.need(manifest['sourcing'] in review['checks']['sourcing']['evidence'] and
           set(manifest['handoff']) <= set(review['checks']['handoff']['evidence']), 'review omits sourcing/handoff')


def certificate(project, name):
    stages = [s for s in p.read(p.ROOT/'skills/pcb-design/workflow/graph.json')['stages']
              if s['spec']['id'] == 'JLC-FABRICATION']
    p.need(len(stages) == 1, 'fabrication stage identity differs')
    stage = stages[0]
    p.need(stage['spec']['requires'] == ['layout_sealed'] and
           stage['spec']['produces'] == ['fabrication_staged'], 'fabrication graph contract differs')
    binding = stage.get('local_execution', {})
    p.need('local_definition' not in stage and binding.get('tool') == 'tools/fabrication.py' and
           binding.get('contract') == STAGE and binding.get('status') == 'pilot_under_validation',
           'fabrication stage has not adopted this local execution adapter')
    review = seal.r.review_json(project, name)
    result = verify(project, review['manifest'], review['output'])
    manifest = p.read(p.local(project, review['manifest']))
    validate_review(project, review, result['subjects'], manifest)
    # Require inspection of the actual derivative artifacts, not just input claims.
    output = review['output']; package = p.local(project, output, exists=False)
    bundle = p.read(package/'native/bundle.json')
    assembly, _ = replay.design_sources(package/'native/design', bundle['schematics'], bundle['boards'])
    required = {key: set() for key in CRITERIA}
    required['source'].update({output+'/fabrication.json', output+'/native/bundle.json'})
    for key, row in assembly['boards'].items():
        required['source'].add(output+'/native/design/'+row['output']+'/native.pdf')
        required['source'].add(output+'/native/design/'+row['output']+'/receipt.json')
        required['source'].add(output+'/native/fab/'+key+'/'+key+'-gerbers.zip')
        required['source'].update(output+'/native/fab/'+key+'/pdf/'+n for n in replay.PDF_NAMES)
    required['population'].update(output+'/assembly/'+f.name for f in (package/'assembly').iterdir()
                                  if f.suffix == '.csv')
    pop = p.read(p.local(project, manifest['population']))
    for board in pop['boards'].values():
        for entry in board['population'].values():
            required['population'].update(entry['evidence'])
            if entry['mode'] in {'manual', 'consigned', 'dnp'}:
                required['instructions'].update(entry['evidence'])
    for board in pop['assembly']['boards'].values():
        for entry in board['placements'].values(): required['population'].update(entry['evidence'])
    for part in p.read(p.local(project, manifest['sourcing']))['parts']:
        required['sourcing'].update(part['jlc_evidence'])
        for offer in part['offers']: required['sourcing'].update(offer['evidence'])
    for hold in manifest['order_holds']: required['handoff'].update(hold['evidence'])
    for key, names in required.items():
        p.need(names <= set(review['checks'][key]['evidence']), 'review omits actual '+key+' artifacts')
    return dict(schema=1, role='fabrication_staged', review=name, review_sha256=p.sha(p.local(project, name)),
                subjects=review['subjects'], stage_spec=stage['spec'],
                toolchain={n: p.sha(Path(__file__).parent/n) for n in TOOLS},
                stage_sha256=p.sha(p.ROOT/STAGE), manual_sha256=p.sha(p.ROOT/MANUAL),
                guidance={n: p.sha(p.ROOT/n) for n in (
                    'skills/pcb-design/procedures/fabrication/population.md',
                    'skills/pcb-design/procedures/fabrication/native-replay.md',
                    'skills/pcb-design/procedures/part-recheck.md',
                    'skills/pcb-design/procedures/schematic/imported-tooling.md')},
                order_status='DO-NOT-ORDER', next_owner='JLC-ASSEMBLY-VERIFY')


def check(project):
    old = p.read(p.local(project, RECEIPT))
    p.need(old == certificate(project, old['review']), 'stale fabrication receipt')
    return old


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=['build', 'verify', 'replay', 'issue', 'check'])
    ap.add_argument('--project', type=Path); ap.add_argument('--package', type=Path)
    for n in ('manifest', 'output', 'review'): ap.add_argument('--'+n)
    a = ap.parse_args()
    try:
        if a.action == 'replay':
            p.need(a.package, 'package required'); result = verify_package(a.package.absolute())
        else:
            p.need(a.project, 'project required'); root = a.project.resolve()
            if a.action in {'build', 'verify'}:
                p.need(a.manifest and a.output, 'manifest/output required')
                result = (build if a.action == 'build' else verify)(root, a.manifest, a.output)
            elif a.action == 'check': result = check(root)
            else:
                p.need(a.review, 'independent review required'); result = certificate(root, a.review)
                dest = p.local(root, RECEIPT, exists=False); dest.parent.mkdir(parents=True, exist_ok=True)
                with dest.open('x') as f: json.dump(result, f, indent=2, sort_keys=True)
        print(json.dumps(result, indent=2)); return 0
    except (ValueError, KeyError, TypeError, OSError, AttributeError) as exc:
        print('Fabrication refused: '+str(exc), file=sys.stderr); return 1


if __name__ == '__main__': sys.exit(main())
