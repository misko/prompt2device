"""Validate recorded native exports against the exact metadata-only derivative.

Run with KiCad's system Python after creating before/after XML and ERC/DRC
reports using the commands recorded in VALIDATION.md. Read-only except an
explicit new result file. Neither this check nor KiCad approves manufacturing.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import pcbnew

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import substitute_quote as q


def components(root):
    return {c.attrib['ref']: {'value': c.findtext('value'), 'footprint': c.findtext('footprint'),
                             'fields': {f.attrib['name']: f.text for f in c.findall('./fields/field')}}
            for c in root.findall('./components/comp')}


def nets(root):
    return sorted((n.attrib['name'], sorted((x.attrib['ref'], x.attrib['pin']) for x in n.findall('node')))
                  for n in root.findall('./nets/net'))


def validate():
    spec_path = HERE / 'adopted-changes.json'
    spec = json.loads(spec_path.read_text())
    package = HERE.parent / 'quote-draft/r6-2c8p-substitutions'
    q.verify(spec_path, package)
    observations, hashes = {}, {}
    for board in spec['assembled']:
        before = ET.parse(HERE / f'validation/{board}-before.xml').getroot()
        after = ET.parse(HERE / f'validation/{board}-after.xml').getroot()
        q.need(nets(before) == nets(after), board + ': connectivity changed')
        old, new = components(before), components(after)
        q.need(set(old) == set(new), board + ': schematic component coverage changed')
        expected = {r: change for change in spec['replacements'] for r in change['refs'].get(board, [])}
        for ref, value in old.items():
            if ref in expected:
                change = expected[ref]
                q.need(value['fields']['MPN'] == change['old_mpn'], 'Unexpected old MPN')
                value['fields'].update(MPN=change['mpn'], Manufacturer=change['manufacturer'])
                value['value'] = change['values'].get(value['value'], value['value'])
            q.need(value == new[ref], board + ': unexpected schematic component change: ' + ref)
        native = package / f'native/pcb/{board}/{board}.kicad_pcb'
        pcb = pcbnew.LoadBoard(str(native))
        footprints = {fp.GetReference(): fp for fp in pcb.GetFootprints()}
        for ref in new:
            # Some schematic power helpers are intentionally not placed.
            if ref not in footprints:
                continue
            fp = footprints[ref]
            q.need(fp.GetValue() == new[ref]['value'] and fp.GetFPIDAsString() == new[ref]['footprint'],
                   board + ': native identity mismatch: ' + ref)
            for key in ('MPN', 'Manufacturer'):
                q.need(fp.GetFieldText(key) == new[ref]['fields'][key], board + ': native property mismatch: ' + ref)
        bom = q.read_csv(package / f'{board}-bom.csv')
        bom_refs = [ref for row in bom for ref in row['Designator'].split(',')]
        cpl_refs = [row['Designator'] for row in q.read_csv(package / f'{board}-cpl.csv')]
        q.need(len(bom_refs) == len(set(bom_refs)) and Counter(bom_refs) == Counter(cpl_refs), 'BOM/CPL coverage')
        for row in bom:
            q.need(int(row['Quantity']) == len(row['Designator'].split(',')), 'BOM quantity mismatch')
            for ref in row['Designator'].split(','):
                c = new[ref]
                q.need((row['MPN'], row['Manufacturer'], row['Comment'], row['Footprint']) ==
                       (c['fields']['MPN'], c['fields']['Manufacturer'], c['value'], c['footprint']), 'BOM/source identity')
        erc = json.loads((HERE / f'validation/{board}-erc.json').read_text())
        drc = json.loads((HERE / f'validation/{board}-drc.json').read_text())
        q.need(not any(s.get('violations') for s in erc['sheets']), 'ERC violations')
        q.need(not drc['violations'] and not drc['unconnected_items'], 'DRC violations/unconnected')
        q.need(not drc.get('ignored_checks'), 'Ignored DRC checks')
        q.need(set(drc['included_severities']) == {'error', 'warning', 'exclusion'}, 'Incomplete DRC severity scope')
        for path in [native, package / f'native/schematic/crow-{board}.kicad_sch',
                     *sorted((HERE / 'validation').glob(f'{board}-*'))]:
            hashes[str(path.relative_to(HERE.parent))] = q.sha(path)
        observations[board] = dict(connectivity='UNCHANGED', changed_refs=sorted(expected),
                                   jlc_placements=len(bom_refs), erc_violations=0,
                                   erc_inherited_ignored_checks=erc.get('ignored_checks', []),
                                   drc_violations=0, unconnected_items=0)
    scope = q.read_csv(package / 'scope.csv')
    totals = Counter()
    for row in scope:
        totals[row['owner']] += int(row['installed_batch'])
    q.need(totals == Counter(JLC_SMT=478, JLC_THT=28, HOME=18), 'Batch population differs')
    plan = q.read_csv(package / 'procurement-plan.csv')
    q.need(len(plan) == 38 and sum(int(r['installed_2c8p']) for r in plan) == 524, 'Procurement quantity differs')
    return dict(result='PASS', kicad=pcbnew.Version(), boards=observations, population=dict(totals),
                package_manifest_sha256=q.sha(package / 'manifest.json'),
                validator_sha256=q.sha(Path(__file__)), inputs=hashes,
                scope='Metadata/source/BOM/connectivity preservation and recorded raw ERC/DRC; no production or physical acceptance')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    q.need(args.output is None or not args.output.exists(), 'Refusing existing result')
    result = validate()
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['boards'], indent=2))
