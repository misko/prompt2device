"""Deterministic quote-only derivative, not a production/admission adapter."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
RELEASE = ROOT.parent / 'releases/crow-prototype-v3-first-run-5c10p-public-v1'
ASSEMBLY = RELEASE / 'fab/assembly'
DEFAULT = ROOT / 'quote-draft/r1-20261031'
BOM = ['Comment', 'Designator', 'Footprint', 'JLCPCB Part #', 'Manufacturer',
       'MPN', 'Quantity', 'Assembly route', 'Supply route']
COUNTS = {'carrier': 5, 'pod': 10}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path):
    with path.open(newline='') as stream:
        return list(csv.DictReader(stream))


def csv_bytes(rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fields, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def source_files():
    files = [Path(__file__).resolve(), ROOT / 'procurement-proposal-20261030.csv',
             ROOT / 'JLC-BROWSER-20261030.json', ROOT / 'JLC-PRICING-20261030.json',
             ROOT / 'SOURCING-DRAFT-20261030.md', RELEASE / 'README.md',
             RELEASE / 'historical/ORDER-INSTRUCTIONS.md']
    files += [ASSEMBLY / name for name in ('population.csv', 'population.json', 'positions.csv', 'demand.csv')]
    for board in COUNTS:
        files += [ASSEMBLY / f'{board}-consigned-{kind}.csv' for kind in ('bom', 'cpl')]
        files += [RELEASE / f'native/source/{board}/{board}.kicad_pcb',
                  RELEASE / f'fab/{board}/{board}-gerbers.zip']
    return files


def payloads():
    """All derivative identities originate in the sealed population, not catalog text."""
    population = read_csv(ASSEMBLY / 'population.csv')
    positions = {(r['board'], r['reference']): r for r in read_csv(ASSEMBLY / 'positions.csv')}
    proposals = read_csv(ROOT / 'procurement-proposal-20261030.csv')
    identities = {(r['manufacturer'], r['mpn']): r for r in proposals}
    need(len(identities) == len(proposals) == 38, 'duplicate/missing proposal identities')
    need(len({(r['board'], r['reference']) for r in population}) == len(population), 'duplicate reference')
    output, scope, manual, users = {}, [], [], []
    consumed = Counter()
    for board, quantity in COUNTS.items():
        selected = [r for r in population if r['board'] == board]
        groups = defaultdict(list)
        for r in selected:
            ref = r['reference']
            need(int(r['board_quantity']) == quantity, 'board count differs')
            if r['mode'] == 'mechanical':
                scope.append(dict(board=board, reference=ref, manufacturer='', mpn='',
                    owner='mechanical', installed_batch=0, catalog_code='', supply_route='',
                    matching_note='non-electrical mounting feature'))
                continue
            need(r['mode'] in ('consigned', 'manual'), 'unexpected population mode')
            p = identities[(r['manufacturer'], r['mpn'])]
            need(ref in p[board + '_refs'].split(';'), 'proposal reference differs: ' + ref)
            need(int(r['demand']) == quantity and r['native_dnp'] == 'False', 'DNP/demand differs')
            owner = p['assembly_owner']
            need(owner in ('user', 'JLC_manual_requested', 'JLC_SMT_requested'), 'unknown owner')
            need((r['mode'] == 'consigned') == (owner == 'JLC_SMT_requested'), 'assembly mode differs')
            code = p['catalog_code']
            global_part = p['proposed_supply_route'] == 'JLC_Global_Sourcing'
            note = ('Select exact Global Sourcing offer; public C-code is a locator, not owned inventory'
                    if global_part else 'Catalog candidate; final vendor matching required')
            if r['mpn'] in ('ERJ-3EKF68R0V', 'PJ-102AH'):
                note += '; explicit OR7 naming reconciliation required'
            if ref == 'X1':
                note += '; compatible SMD installation required despite manual catalog label'
            consumed[(r['manufacturer'], r['mpn'])] += quantity
            scope.append(dict(board=board, reference=ref, manufacturer=r['manufacturer'], mpn=r['mpn'],
                owner=owner, installed_batch=quantity, catalog_code=code,
                supply_route=p['proposed_supply_route'], matching_note=note if owner != 'user' else 'User supplied/installed; exclude from JLC'))
            if owner != 'user':
                # A public code must not masquerade as a usable private/global inventory ID.
                key = (r['value'], r['footprint'], r['manufacturer'], r['mpn'],
                       '' if global_part else code, owner, p['proposed_supply_route'])
                need(bool(code), 'missing catalog locator')
                groups[key].append(ref)
            if owner != 'JLC_SMT_requested':
                pos = positions[(board, ref)]
                entry = dict(board=board, reference=ref, manufacturer=r['manufacturer'], mpn=r['mpn'],
                    footprint=r['footprint'], owner=owner, quantity_per_board=1,
                    board_quantity=quantity, installed_batch=quantity, catalog_code=code,
                    supply_route=p['proposed_supply_route'], native_x_mm=pos['x_mm'],
                    native_y_mm=pos['y_mm'], native_angle_deg=pos['kicad_angle_deg'],
                    note='Native anchor only, NOT vendor centroid/CPL; manual installation scope')
                (users if owner == 'user' else manual).append(entry)
        bom = []
        for (value, footprint, maker, mpn, code, owner, route), refs in sorted(groups.items()):
            bom.append(dict(zip(BOM, [value, ','.join(sorted(refs)), footprint, code,
                                     maker, mpn, len(refs), owner, route])))
        smt = [r for r in bom if r['Assembly route'] == 'JLC_SMT_requested']
        output[f'{board}-bom.csv'] = csv_bytes(bom, BOM)
        output[f'{board}-smt-bom.csv'] = csv_bytes(smt, BOM)
        cpl_path = ASSEMBLY / f'{board}-consigned-cpl.csv'
        cpl = read_csv(cpl_path)
        smt_refs = {ref for r in smt for ref in r['Designator'].split(',')}
        need(len(cpl) == len(smt_refs) and {r['Designator'] for r in cpl} == smt_refs,
             'SMT BOM/CPL coverage mismatch')
        old_bom = read_csv(ASSEMBLY / f'{board}-consigned-bom.csv')
        old = {ref: (r['Manufacturer'], r['MPN'], r['Footprint'], r['Comment'])
               for r in old_bom for ref in r['Designator'].split(',')}
        new = {ref: (r['Manufacturer'], r['MPN'], r['Footprint'], r['Comment'])
               for r in smt for ref in r['Designator'].split(',')}
        need(old == new, 'released BOM identity changed')
        output[f'{board}-cpl.csv'] = cpl_path.read_bytes()
        output[f'{board}-gerbers.zip'] = (RELEASE / f'fab/{board}/{board}-gerbers.zip').read_bytes()
    need(consumed == Counter({key: int(p['installed_need']) for key, p in identities.items()}),
         'whole-batch identity/quantity mismatch')
    need(sum(consumed.values()) == 1000, 'incomplete total population')
    for name, rows in [('scope.csv', scope), ('manual-assembly.csv', manual), ('user-installation.csv', users)]:
        output[name] = csv_bytes(rows, list(rows[0]))
    need(sum(r['installed_batch'] for r in manual) == 60, 'manual scope differs')
    need(sum(r['installed_batch'] for r in users) == 25, 'user scope differs')
    return output


def manifest(outputs):
    return dict(schema=1, purpose='QUOTE_ONLY_NOT_ORDER_APPROVAL', board_quantities=COUNTS,
        sources={str(p.relative_to(REPO)): digest(p) for p in source_files()},
        files={n: hashlib.sha256(b).hexdigest() for n, b in sorted(outputs.items())},
        coordinates='Retained absolute native datum; CPL mm +X right/+Y up; exact retained vendor angles; no panel replication',
        quantity_basis='BOM/CPL per one board; set portal quantity carrier=5 pod=10; not purchase/attrition quantities',
        global_codes='Blank in BOM; scope.csv public codes are locators only; exact private offer selection pending',
        exclusions='Manual/user/mechanical references excluded from SMT CPL; 60 JLC manual operations separate',
        pending=['JLC ingestion and exact matching', 'vendor rotation/polarity preview',
                 'manual/THT handling', 'stock/allocation/attrition', 'exact-job process agreement',
                 'full quote and user approval'])


def build(output):
    need(not output.exists(), 'refusing to overwrite existing draft')
    data = payloads()
    output.mkdir(parents=True)
    for name, content in data.items():
        (output / name).write_bytes(content)
    (output / 'manifest.json').write_text(json.dumps(manifest(data), indent=2, sort_keys=True) + '\n')


def verify(output):
    expected = payloads()
    for name, content in expected.items():
        need((output / name).read_bytes() == content, 'changed draft: ' + name)
    need(json.loads((output / 'manifest.json').read_text()) == manifest(expected), 'stale manifest/source')
    allowed = set(expected) | {'manifest.json', 'README.md', 'native-audit.json'}
    need({p.name for p in output.iterdir()} <= allowed, 'unexpected draft file')
    audit = output / 'native-audit.json'
    if audit.exists():
        record = json.loads(audit.read_text())
        need(record['result'] == 'PASS' and record['manifest_sha256'] == digest(output / 'manifest.json'),
             'stale native audit')
    return dict(result='PASS', scope='source binding / exact exports, not vendor approval',
                installed=1000, JLC_SMT=915, JLC_manual=60, user=25)


def native_audit(output):
    """Reopen native boards independently; never save/regenerate them."""
    import pcbnew as pcb
    verify(output)
    population = read_csv(ASSEMBLY / 'population.csv')
    positions = {(r['board'], r['reference']): r for r in read_csv(ASSEMBLY / 'positions.csv')}
    observations = []
    for name in COUNTS:
        board = pcb.LoadBoard(str(RELEASE / f'native/source/{name}/{name}.kicad_pcb'))
        fps = {f.GetReference(): f for f in board.GetFootprints()}
        rows = [r for r in population if r['board'] == name]
        need(set(fps) == {r['reference'] for r in rows} and len(fps) == len(list(board.GetFootprints())), 'native coverage')
        cpl = {r['Designator']: r for r in read_csv(output / f'{name}-cpl.csv')}
        angle_offsets = []
        for r in rows:
            ref = r['reference']; fp = fps[ref]
            need(fp.GetFPIDAsString() == r['footprint'] and fp.GetValue() == r['value'], 'native identity: ' + ref)
            for method, field in [('IsDNP', 'native_dnp'), ('IsExcludedFromBOM', 'native_exclude_bom'),
                                  ('IsExcludedFromPosFiles', 'native_exclude_positions')]:
                need(str(getattr(fp, method)()) == r[field], 'native exclusion: ' + ref)
            if r['mode'] == 'mechanical':
                need(all(p.GetAttribute() == pcb.PAD_ATTRIB_NPTH and not p.GetNetname() for p in fp.Pads()), 'mechanical pads')
                continue
            for field, expected in json.loads(r['fields_json']).items():
                need(fp.GetFieldText(field) == expected, 'native field: ' + ref + '/' + field)
            pos = positions[(name, ref)]
            x, y, angle = fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6, fp.GetOrientationDegrees()
            need(abs(x-float(pos['x_mm'])) < 1e-6 and abs(y-float(pos['y_mm'])) < 1e-6 and
                 abs(angle-float(pos['kicad_angle_deg'])) < 1e-6, 'native pose: ' + ref)
            need(pos['side'] == ('bottom' if fp.IsFlipped() else 'top'), 'native side: ' + ref)
            if ref in cpl:
                c = cpl[ref]
                need(abs(float(c['Mid X'].removesuffix('mm'))-x) < 1e-6 and
                     abs(float(c['Mid Y'].removesuffix('mm'))+y) < 1e-6, 'CPL centroid: ' + ref)
                need(c['Layer'].lower() == pos['side'], 'CPL side')
                delta = (float(c['Rotation']) - angle) % 360
                if delta:
                    angle_offsets.append(dict(reference=ref, native_angle=angle,
                                              retained_CPL_angle=float(c['Rotation']), offset_mod360=delta))
        observations.append(dict(board=name, footprints=len(rows), smt=len(cpl),
                                 inherited_angle_offsets=angle_offsets))
    return dict(result='PASS', scope='native identity/pose/exclusion audit; inherited vendor angles preserved, not requalified',
                tool=pcb.Version(), manifest_sha256=digest(output / 'manifest.json'), boards=observations)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify', 'native-audit'])
    parser.add_argument('--output', type=Path, default=DEFAULT)
    args = parser.parse_args()
    if args.action == 'build':
        build(args.output)
    elif args.action == 'native-audit':
        record = native_audit(args.output)
        path = args.output / 'native-audit.json'
        with path.open('x') as stream:
            json.dump(record, stream, indent=2, sort_keys=True)
            stream.write('\n')
        print(json.dumps(record, indent=2))
    else:
        print(json.dumps(verify(args.output), indent=2))
