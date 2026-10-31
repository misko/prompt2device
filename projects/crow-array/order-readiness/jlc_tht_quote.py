# SPDX-License-Identifier: MIT
"""Quote-only 2c8p JLC SMT/THT split; preserve release and expose missing THT CPL."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import quote_files as q
import home_assembly_plan as h

DEFAULT = q.ROOT / 'quote-draft/r4-2c8p-jlc-tht'
COUNTS = {'carrier': 2, 'pod': 8}
THT = {'RJHSE-5080', 'PJ-102AH', 'R-78E5.0-0.5'}
HOME = {'SC0915', 'CMA-4544PF-W', 'CPE-203'}
R2 = q.ROOT / 'quote-draft/r2-1c8p-manual-review'


def sources():
    return [Path(__file__).resolve(), Path(q.__file__).resolve(), Path(h.__file__).resolve(),
            q.ASSEMBLY / 'population.csv', q.ASSEMBLY / 'positions.csv',
            h.DEFAULT / 'procurement-plan.csv', h.DEFAULT / 'manifest.json',
            q.DEFAULT / 'manifest.json', q.DEFAULT / 'native-audit.json',
            R2 / 'manual-native-geometry.json',
            *[q.DEFAULT / f'{b}-{kind}' for b in COUNTS for kind in
              ('bom.csv', 'cpl.csv', 'gerbers.zip', 'smt-bom.csv')]]


def owner(row):
    if row['mode'] == 'mechanical':
        return 'MECHANICAL'
    if row['mpn'] in HOME:
        return 'HOME'
    if row['mpn'] in THT:
        return 'JLC_THT'
    q.need(row['mode'] == 'consigned', 'Unclassified electrical population')
    return 'JLC_SMT'


def payloads():
    h.verify(h.DEFAULT)
    pop = q.read_csv(q.ASSEMBLY / 'population.csv')
    poses = {(r['board'], r['reference']): r for r in q.read_csv(q.ASSEMBLY / 'positions.csv')}
    data, scope, manual = {}, [], []
    totals = Counter()
    for row in pop:
        who = owner(row)
        count = 0 if who == 'MECHANICAL' else COUNTS[row['board']]
        totals[who] += count
        scope.append(dict(board=row['board'], reference=row['reference'],
                          manufacturer=row['manufacturer'], mpn=row['mpn'],
                          footprint=row['footprint'], owner=who, installed_batch=count))
        if who == 'JLC_THT':
            pos = poses[row['board'], row['reference']]
            manual.append(dict(board=row['board'], reference=row['reference'],
                               manufacturer=row['manufacturer'], mpn=row['mpn'],
                               board_quantity=COUNTS[row['board']], installed_batch=count,
                               native_x_mm=pos['x_mm'], native_y_mm=pos['y_mm'],
                               native_angle_deg=pos['kicad_angle_deg'], side=pos['side'],
                               coordinate_status='NATIVE PAD-1 ANCHOR ONLY; NOT VERIFIED JLC CENTROID/ROTATION'))
    q.need(totals == Counter(JLC_SMT=478, JLC_THT=28, HOME=18), 'Incorrect ownership totals')
    q.need(len({(r['board'], r['reference']) for r in scope}) == len(pop), 'Duplicate references')
    for board in COUNTS:
        full = q.read_csv(q.DEFAULT / f'{board}-bom.csv')
        refs = {ref for r in full for ref in r['Designator'].split(',')}
        expected = {r['reference'] for r in scope if r['board'] == board and r['owner'].startswith('JLC_')}
        q.need(refs == expected, 'Combined BOM is not exact JLC scope')
        q.need(sum(int(r['Quantity']) for r in full) == len(refs), 'BOM duplicates/count mismatch')
        data[f'{board}-bom.csv'] = (q.DEFAULT / f'{board}-bom.csv').read_bytes()
        data[f'{board}-gerbers.zip'] = (q.DEFAULT / f'{board}-gerbers.zip').read_bytes()
        # Preserve proven SMT bytes, but do not mislabel them as complete mixed CPL.
        data[f'{board}-cpl-SMT-ONLY-INCOMPLETE.csv'] = (q.DEFAULT / f'{board}-cpl.csv').read_bytes()
        cpl = q.read_csv(q.DEFAULT / f'{board}-cpl.csv')
        smt_refs = {r['reference'] for r in scope if r['board'] == board and r['owner'] == 'JLC_SMT'}
        tht_refs = {r['reference'] for r in manual if r['board'] == board}
        q.need({r['Designator'] for r in cpl} == smt_refs, 'SMT CPL changed')
        q.need(smt_refs.isdisjoint(tht_refs) and smt_refs | tht_refs == expected, 'CPL coverage partition')
        template = [dict(Designator=r['reference'], **{'Mid X': '', 'Mid Y': '', 'Rotation': '',
                    'Layer': r['side'].title(), 'Status': 'NOT UPLOAD: verify centroid/datum/vendor orientation'})
                    for r in manual if r['board'] == board]
        data[f'{board}-cpl-THT-NOT-UPLOAD.csv'] = q.csv_bytes(template, list(template[0]))
    demand = []
    for old in q.read_csv(h.DEFAULT / 'procurement-plan.csv'):
        row = {k: old[k] for k in ('manufacturer', 'mpn', 'carrier_refs', 'pod_refs',
                                  'per_carrier', 'per_pod', 'catalog_locator', 'external_lead')}
        row['installed_2c8p'] = 2 * int(row['per_carrier']) + 8 * int(row['per_pod'])
        row['owner'] = 'HOME' if row['mpn'] in HOME else 'JLC_THT' if row['mpn'] in THT else 'JLC_SMT'
        row['proposed_route'] = ('external_to_home' if row['owner'] == 'HOME' else
                                'JLC_Global_Sourcing_or_consignment_candidate' if row['mpn'] in ('PCM1864DBT', 'R-78E5.0-0.5')
                                else 'JLC_catalog_or_replenishment_candidate')
        row['purchase_quantity'] = ''
        row['evidence_status'] = 'Not allocation; current exact-job gross demand, stock and fees pending'
        demand.append(row)
    q.need(len(demand) == 38 and sum(r['installed_2c8p'] for r in demand) == 524, 'Demand coverage')
    homes = [r for r in demand if r['owner'] == 'HOME']
    thts = [r for r in demand if r['owner'] == 'JLC_THT']
    for name, rows in [('scope.csv', scope), ('procurement-plan.csv', demand),
                       ('home-install-parts.csv', homes), ('jlc-tht-parts.csv', thts),
                       ('tht-native-anchors-NOT-CPL.csv', manual)]:
        data[name] = q.csv_bytes(rows, list(rows[0]))
    data['manual-native-geometry.json'] = (R2 / 'manual-native-geometry.json').read_bytes()
    return data


def manifest(data):
    return dict(schema=1, status='QUOTE_DRAFT_THT_PLACEMENT_REVIEW_REQUIRED',
                upload_ready=False, purchase_authorized=False, submitted=False,
                assembled=COUNTS, bare_candidates={'carrier': 5, 'pod': 10},
                installed={'JLC_SMT': 478, 'JLC_THT': 28, 'HOME': 18, 'total': 524},
                per_board={'carrier': {'JLC_SMT': 127, 'JLC_THT': 10, 'HOME': 1},
                           'pod': {'JLC_SMT': 28, 'JLC_THT': 1, 'HOME': 2}},
                sources={str(p.relative_to(q.REPO)): q.digest(p) for p in sources()},
                files={n: hashlib.sha256(b).hexdigest() for n, b in sorted(data.items())},
                authority='User requests JLC Ethernet/power jacks and RECOM; home Pico/microphone/buzzer; 2c8p; no purchases',
                holds=['11 per-board THT placements need verified centroid/datum/vendor rotation and complete CPL',
                       'Exact matching and final placement preview', 'JLC source allocation and gross quantities including RECOM',
                       'Existing stack/stencil/process/mechanical controls', 'Complete quote and explicit production/purchase authority'],
                note='BOMs per one board. No board replication or quantity multiplication inside vendor BOM/CPL. '
                     'Native anchors are evidence only. Mixed-assembly BOM with SMT-only CPL is incomplete, not an acceptable full quote.')


def build(output):
    q.need(not output.exists(), 'Refusing to overwrite existing quote revision')
    data = payloads()
    output.mkdir(parents=True)
    for name, content in data.items():
        (output / name).write_bytes(content)
    (output / 'manifest.json').write_text(json.dumps(manifest(data), indent=2, sort_keys=True) + '\n')


def verify(output, require_upload_ready=False):
    data = payloads()
    for name, content in data.items():
        q.need((output / name).read_bytes() == content, 'Changed quote artifact: ' + name)
    q.need(json.loads((output / 'manifest.json').read_text()) == manifest(data), 'Stale/tampered manifest')
    q.need({p.name for p in output.iterdir()} <= set(data) | {'manifest.json', 'README.md', 'JLC-SUBMISSION-NOTES.md'},
           'Unexpected quote file; complete CPL must not be silently invented')
    if require_upload_ready:
        q.need(False, 'NOT UPLOAD-READY: THT placement mapping / complete CPL remains unverified')
    return dict(result='PASS', scope='Data/ownership/source preservation, not placement or order approval',
                upload_ready=False, installed=manifest(data)['installed'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify'])
    parser.add_argument('--output', type=Path, default=DEFAULT)
    parser.add_argument('--require-upload-ready', action='store_true')
    args = parser.parse_args()
    try:
        if args.action == 'build':
            q.need(not args.require_upload_ready, 'Use require-upload-ready with verify')
            build(args.output)
        else:
            print(json.dumps(verify(args.output, args.require_upload_ready), indent=2))
    except (ValueError, OSError) as error:
        parser.exit(2, str(error) + '\n')
