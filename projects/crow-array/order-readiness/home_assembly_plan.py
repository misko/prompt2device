"""Rebase batch demand/ownership without changing released boards or r1 exports."""
import argparse
from collections import Counter
import json
from pathlib import Path
import quote_files as q

ROOT = q.ROOT
DEFAULT = ROOT / 'quote-draft/r3-1c8p-home'
SHORT = {'CB3LV-3I-12M288000', '1206L010/30WR', 'GRM21BR71A105KA01L',
         'C2012X7R1V225K125AE', 'C3216X7R1V106K160AC', 'PCM1864DBT'}
HOME = {'RJHSE-5080', 'PJ-102AH', 'R-78E5.0-0.5', 'SC0915', 'CMA-4544PF-W', 'CPE-203'}
SCENARIOS = {
    'A_target_1c8p': {'carrier_assembled': 1, 'pod_assembled': 8,
                    'carrier_bare_candidate': 5, 'pod_bare_candidate': 10,
                    'status': 'Desired target; one carrier not supported by observed JLC controls'},
    'B_observed_5c8p': {'carrier_assembled': 5, 'pod_assembled': 8,
                      'carrier_bare_candidate': 5, 'pod_bare_candidate': 10,
                      'status': 'Observed portal scenario; not an adopted build or proven minimum'},
}


def sources():
    return [Path(__file__).resolve(), ROOT/'quote_files.py', q.DEFAULT/'manifest.json',
            q.DEFAULT/'native-audit.json', ROOT/'procurement-proposal-20261030.csv',
            ROOT/'procurement-map-20261026-v3.csv', ROOT/'PCBA-SESSION-20261031.md',
            ROOT/'JLC-PRICING-20261030.json', q.ASSEMBLY/'population.csv']


def payloads():
    q.verify(q.DEFAULT)
    population = q.read_csv(q.ASSEMBLY/'population.csv')
    old = q.read_csv(ROOT/'procurement-proposal-20261030.csv')
    leads = {r['mpn']: r for r in q.read_csv(ROOT/'procurement-map-20261026-v3.csv')}
    per_board = Counter((r['board'], r['manufacturer'], r['mpn']) for r in population
                        if r['mode'] != 'mechanical')
    output, demand, home = {}, [], []
    for p in old:
        maker, mpn = p['manufacturer'], p['mpn']
        c, pod = per_board['carrier', maker, mpn], per_board['pod', maker, mpn]
        owner = 'HOME' if mpn in HOME else 'JLC_SMT'
        route = ('external_to_home' if owner == 'HOME' else
                 'JLC_Global_Sourcing_candidate' if mpn == 'PCM1864DBT' else
                 'JLC_replenishment_candidate' if mpn in SHORT else 'JLC_catalog_candidate')
        row = dict(manufacturer=maker, mpn=mpn, carrier_refs=p['carrier_refs'], pod_refs=p['pod_refs'],
                   per_carrier=c, per_pod=pod, installed_A_1c8p=c+8*pod,
                   installed_B_5c8p=5*c+8*pod, owner=owner, proposed_route=route,
                   catalog_locator=p['catalog_code'], shortage_in_session=mpn in SHORT,
                   purchase_quantity='', price='', usable_arrival='',
                   evidence_status='New batch provisional; retained observations not allocation',
                   external_lead=leads[mpn]['fallback_url'])
        demand.append(row)
        if owner == 'HOME':
            home.append(row)
    q.need(len(demand) == 38 and len(home) == 6, 'identity coverage')
    scope = []
    for r in population:
        owner = 'MECHANICAL' if r['mode'] == 'mechanical' else 'HOME' if r['mpn'] in HOME else 'JLC_SMT'
        q.need((r['mode'] == 'consigned') == (owner == 'JLC_SMT'), 'SMT partition mismatch')
        scope.append(dict(board=r['board'], reference=r['reference'], manufacturer=r['manufacturer'],
                          mpn=r['mpn'], footprint=r['footprint'], owner=owner,
                          installed_A_1c8p=0 if owner == 'MECHANICAL' else 1 if r['board'] == 'carrier' else 8,
                          installed_B_5c8p=0 if owner == 'MECHANICAL' else 5 if r['board'] == 'carrier' else 8))
    for board in ('carrier', 'pod'):
        for filename, source in [(f'{board}-bom.csv', f'{board}-smt-bom.csv'),
                                 (f'{board}-cpl.csv', f'{board}-cpl.csv'),
                                 (f'{board}-gerbers.zip', f'{board}-gerbers.zip')]:
            output[filename] = (q.DEFAULT/source).read_bytes()
        refs = {ref for row in q.read_csv(q.DEFAULT/f'{board}-smt-bom.csv')
                for ref in row['Designator'].split(',')}
        q.need(refs == {r['reference'] for r in scope if r['board'] == board and r['owner'] == 'JLC_SMT'},
               'BOM not exact SMT scope')
    for name, rows in [('procurement-plan.csv', demand), ('home-install-parts.csv', home),
                       ('shortage-parts.csv', [r for r in demand if r['mpn'] in SHORT]), ('scope.csv', scope)]:
        output[name] = q.csv_bytes(rows, list(rows[0]))
    output['scenarios.json'] = (json.dumps(SCENARIOS, indent=2, sort_keys=True)+'\n').encode()
    return output


def manifest(data):
    import hashlib
    return dict(schema=1, status='SUBMISSION_DRAFT_NOT_PRODUCTION_APPROVAL',
                sources={str(p.relative_to(q.REPO)): q.digest(p) for p in sources()},
                files={n: hashlib.sha256(b).hexdigest() for n, b in sorted(data.items())},
                source_native_audit='quote-draft/r1-20261031/native-audit.json; inherited unchanged geometry',
                scenarios=SCENARIOS, installed={'A': {'JLC_SMT': 351, 'HOME': 35, 'total': 386},
                                               'B': {'JLC_SMT': 859, 'HOME': 79, 'total': 938}},
                basis='Per-board upload files; scenario totals are installed, NOT purchase/attrition/minima',
                holds=['scenario/quantity selection', 'exact stock/attrition/allocation',
                       'vendor matches/placement preview', 'stack/stencil/mechanical/process acceptance',
                       'complete quote and purchase authority'],
                permitted_external_actions='NONE by this local preparation')


def build(output):
    q.need(not output.exists(), 'refusing existing revision')
    data = payloads()
    output.mkdir(parents=True)
    for name, content in data.items():
        (output/name).write_bytes(content)
    (output/'manifest.json').write_text(json.dumps(manifest(data), indent=2, sort_keys=True)+'\n')


def verify(output):
    data = payloads()
    for name, expected in data.items():
        q.need((output/name).read_bytes() == expected, 'changed scenario artifact: '+name)
    q.need(json.loads((output/'manifest.json').read_text()) == manifest(data), 'stale scenario manifest')
    q.need({p.name for p in output.iterdir()} <= set(data) | {'manifest.json', 'README.md', 'JLC-SUBMISSION-NOTES.md'},
           'unexpected scenario artifact')
    return dict(result='PASS', status='DRAFT_NOT_ORDER_APPROVED', scenarios=manifest(data)['installed'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify'])
    parser.add_argument('--output', type=Path, default=DEFAULT)
    args = parser.parse_args()
    if args.action == 'build':
        build(args.output)
    else:
        print(json.dumps(verify(args.output), indent=2))
