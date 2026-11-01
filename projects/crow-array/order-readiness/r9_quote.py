"""Quote-only assembly split: user installs TI X1; no design or order changes."""
import argparse
import json
from pathlib import Path
import shutil
import r8_quote as r

q = r.q
ROOT = r.ROOT
BASE = r.OUT
OUT = ROOT / 'quote-draft/r9-2c8p-home-clock'
CHANGED = {'carrier-bom.csv', 'carrier-cpl.csv', 'scope.csv',
           'procurement-plan.csv', 'home-install-parts.csv', 'README.md'}
LEAD = 'https://www.digikey.com/en/products/detail/texas-instruments/LMK6CE012288CDLFR/22107194'


def tables():
    result = {n: q.read_csv(BASE/n) for n in CHANGED if n.endswith('.csv')}
    for name in ('carrier-bom.csv', 'carrier-cpl.csv'):
        rows = result[name]
        q.need(sum(x['Designator'] == 'X1' for x in rows) == 1, 'Expected single X1 row')
        result[name] = [x for x in rows if x['Designator'] != 'X1']
    for row in result['scope.csv']:
        if (row['board'], row['reference']) == ('carrier', 'X1'):
            row['owner'] = 'HOME'
    clocks = [x for x in result['procurement-plan.csv'] if x['mpn'] == r.MPN]
    q.need(len(clocks) == 1, 'Expected exact TI procurement identity')
    clocks[0].update(owner='HOME', proposed_route='external_to_home', external_lead=LEAD,
                     purchase_quantity='', evidence_status='User authorized home SMT installation Nov 1; DigiKey browser observed 2884, MOQ1, USD3.34 each; not allocation; delivery/spares unconfirmed')
    result['home-install-parts.csv'].append(dict(clocks[0]))
    return result


def population(output):
    scope = q.read_csv(output/'scope.csv')
    q.need(len({(x['board'], x['reference']) for x in scope}) == len(scope), 'Duplicate scope reference')
    totals = {owner: sum(int(x['installed_batch']) for x in scope if x['owner'] == owner)
              for owner in ('JLC_SMT', 'JLC_THT', 'HOME')}
    q.need(totals == {'JLC_SMT':476, 'JLC_THT':28, 'HOME':20}, 'Wrong installed split')
    for board in ('carrier', 'pod'):
        factory = {x['reference'] for x in scope if x['board'] == board and x['owner'].startswith('JLC_')}
        bom = [ref.strip() for x in q.read_csv(output/f'{board}-bom.csv') for ref in x['Designator'].split(',')]
        cpl = [x['Designator'] for x in q.read_csv(output/f'{board}-cpl.csv')]
        q.need(len(bom) == len(set(bom)) and len(cpl) == len(set(cpl)), 'Duplicate factory reference')
        q.need(set(bom) == set(cpl) == factory, 'Factory reference coverage mismatch')
        home = {ref for x in q.read_csv(output/'home-install-parts.csv') for ref in x[f'{board}_refs'].split(';') if ref}
        q.need(home == {x['reference'] for x in scope if x['board'] == board and x['owner'] == 'HOME'}, 'Home coverage mismatch')
    return totals


def build(output):
    r.verify(BASE)
    q.need(not output.exists(), 'Refusing existing output')
    shutil.copytree(BASE, output)
    for name, rows in tables().items():
        (output/name).write_bytes(q.csv_bytes(rows))
    shutil.copyfile(ROOT/'R9-INSTRUCTIONS.md', output/'README.md')
    # X1 coordinates retained for home work, deliberately excluded from factory CPL.
    clock = [x for x in q.read_csv(BASE/'carrier-cpl.csv') if x['Designator'] == 'X1']
    (output/'home-clock-placement.csv').write_bytes(q.csv_bytes(clock))
    shutil.copyfile(BASE/'README.md', output/'engineering/R8-HISTORICAL-INSTRUCTIONS.md')
    totals = population(output)
    protected = {str(p.relative_to(BASE)):q.sha(p) for p in BASE.rglob('*')
                 if p.is_file() and str(p.relative_to(BASE)) not in CHANGED | {'manifest.json'}}
    m = dict(status='QUOTE_ONLY_HOME_CLOCK_SPLIT_VERIFIED', production_ready=False,
             purchase_authorized=False, submitted=False, stage_acceptance_issued=False,
             inherited_release_acceptance=False, independent_r9_assembly_acceptance=False,
             fabricated={'carrier':5,'pod':10}, assembled={'carrier':2,'pod':8},
             installed={**totals,'total':sum(totals.values())}, oscillator_installed=2,
             oscillator_owner='HOME', oscillator_delivery_date=None,
             base_manifest_sha256=q.sha(BASE/'manifest.json'), tool_sha256=q.sha(Path(__file__)),
             protected=protected)
    m['files'] = {str(p.relative_to(output)):q.sha(p) for p in output.rglob('*')
                  if p.is_file() and p.name != 'manifest.json'}
    (output/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    return verify(output)


def verify(output):
    m = json.loads((output/'manifest.json').read_text())
    q.need(m['base_manifest_sha256'] == q.sha(BASE/'manifest.json'), 'Changed r8 manifest')
    base = json.loads((BASE/'manifest.json').read_text())
    actual_base = {str(p.relative_to(BASE)):q.sha(p) for p in BASE.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    q.need(actual_base == base['files'], 'Changed r8 payload')
    q.need(m['tool_sha256'] == q.sha(Path(__file__)), 'Changed producer')
    actual = {str(p.relative_to(output)):q.sha(p) for p in output.rglob('*') if p.is_file() and p.name != 'manifest.json'}
    q.need(actual == m['files'], 'Changed/missing/extra payload')
    expected_protected = {k:v for k,v in base['files'].items() if k not in CHANGED}
    q.need(m['protected'] == expected_protected, 'Incorrect preservation policy')
    for name, digest in expected_protected.items():
        q.need(q.sha(output/name) == digest, 'Changed protected payload: '+name)
    for name, rows in tables().items():
        q.need((output/name).read_bytes() == q.csv_bytes(rows), 'Wrong derived table: '+name)
    q.need((output/'README.md').read_bytes() == (ROOT/'R9-INSTRUCTIONS.md').read_bytes(), 'Changed instructions')
    clock = [x for x in q.read_csv(BASE/'carrier-cpl.csv') if x['Designator'] == 'X1']
    q.need((output/'home-clock-placement.csv').read_bytes() == q.csv_bytes(clock), 'Wrong manual coordinates')
    q.need((output/'engineering/R8-HISTORICAL-INSTRUCTIONS.md').read_bytes() == (BASE/'README.md').read_bytes(), 'Changed historical instructions')
    totals = population(output)
    q.need(m['installed'] == {**totals,'total':524}, 'Manifest totals mismatch')
    q.need(m['fabricated'] == {'carrier':5,'pod':10} and m['assembled'] == {'carrier':2,'pod':8}, 'Wrong job quantities')
    q.need(m['oscillator_owner'] == 'HOME' and m['oscillator_installed'] == 2, 'Wrong clock ownership')
    q.need(all(m[k] is False for k in ('production_ready','purchase_authorized','submitted',
        'stage_acceptance_issued','inherited_release_acceptance','independent_r9_assembly_acceptance')), 'Invalid authority claim')
    return dict(result='PASS', files=len(actual), preserved_r8_files=len(expected_protected), installed=m['installed'], production_ready=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build','verify'])
    parser.add_argument('--output', type=Path, default=OUT)
    args = parser.parse_args()
    print(json.dumps((build if args.action == 'build' else verify)(args.output),indent=2))
