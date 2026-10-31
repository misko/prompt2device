# SPDX-License-Identifier: MIT
"""Complete quote-upload CPLs; local physical pose is not JLC preview approval."""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path

import jlc_tht_quote as t

q = t.q
DEFAULT = q.ROOT / 'quote-draft/r5-2c8p-complete'
REVIEW = q.ROOT / 'THT-PLACEMENT-REVIEW-20261031.md'
FIELDS = ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer']
# Drawing-derived nominal body centers in the native top-side, pad-1 frame.
# RJ: primary inches; PJ and RECOM: primary mm. See REVIEW for derivations.
FACTS = {
    'RJHSE-5080': dict(center=(3.556, -0.127), size=(15.748, 14.986),
                      pads={str(i + 1): (1.016 * i, 1.778 * (i % 2)) for i in range(8)},
                      pegs=[(-2.794, -2.54), (9.906, -2.54)],
                      direction='Mouth toward native -Y / CPL +Y; pin 1 left of pin 8'),
    'PJ-102AH': dict(center=(0.0, 6.5), size=(9.0, 14.4),
                    pads={'1': (0, 0), '2': (0, 6), '3': (4.7, 3)}, pegs=[],
                    direction='Mouth toward native +Y / CPL -Y; pin 3 to right'),
    'R-78E5.0-0.5': dict(center=(2.59, -2.25), size=(11.6, 8.5),
                        pads={'1': (0, 0), '2': (2.54, 0), '3': (5.08, 0)}, pegs=[],
                        direction='Pins 1 VIN, 2 GND, 3 VOUT left to right; body toward native -Y'),
}


def rows(blob):
    return list(csv.DictReader(io.StringIO(blob.decode())))


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2) + '\n').encode()


def board_path(board):
    return q.RELEASE / f'native/source/{board}/{board}.kicad_pcb'


def sources():
    paths = [Path(__file__).resolve(), REVIEW, *t.sources(),
             t.DEFAULT / 'manifest.json', *[board_path(b) for b in t.COUNTS]]
    return {str(p.relative_to(q.REPO)): q.digest(p) for p in paths}


def placements():
    population = {(r['board'], r['reference']): r for r in q.read_csv(q.ASSEMBLY / 'population.csv')}
    positions = q.read_csv(q.ASSEMBLY / 'positions.csv')
    out = []
    for p in positions:
        r = population[p['board'], p['reference']]
        if r['mpn'] not in FACTS:
            continue
        q.need(float(p['kicad_angle_deg']) == 0 and p['side'] == 'top',
               'New THT pose requires a reviewed transform')
        dx, dy = FACTS[r['mpn']]['center']
        x, y = float(p['x_mm']), float(p['y_mm'])
        out.append(dict(board=p['board'], reference=p['reference'], mpn=r['mpn'],
                        anchor_x=x, anchor_y=y, body_center_x=round(x + dx, 6),
                        body_center_y=round(y + dy, 6),
                        cpl_x=round(x + dx, 6), cpl_y=round(-y - dy, 6),
                        rotation=0, layer='Top', orientation=FACTS[r['mpn']]['direction']))
    q.need(Counter(p['board'] for p in out) == Counter(carrier=10, pod=1), 'THT count')
    return sorted(out, key=lambda p: (p['board'], p['reference']))


def cpl_row(p):
    return dict(zip(FIELDS, [p['reference'], f"{p['cpl_x']:.6f}mm", f"{p['cpl_y']:.6f}mm",
                            '0.000000', 'Top']))


def check_cpl(board, cpl, bom, tht):
    refs = [r['Designator'] for r in cpl]
    wanted = [ref for row in bom for ref in row['Designator'].split(',')]
    q.need(len(set(refs)) == len(refs) and Counter(refs) == Counter(wanted), 'BOM/CPL reference coverage')
    expected = q.read_csv(q.DEFAULT / f'{board}-cpl.csv') + [cpl_row(p) for p in tht if p['board'] == board]
    q.need(cpl == expected, 'CPL coordinate/side/orientation or inherited SMT changed')


def payloads():
    t.verify(t.DEFAULT)
    old = t.payloads()
    keep = ['scope.csv', 'procurement-plan.csv', 'home-install-parts.csv', 'jlc-tht-parts.csv']
    data = {name: old[name] for name in keep}
    tht = placements()
    for board in t.COUNTS:
        for kind in ('bom.csv', 'gerbers.zip'):
            name = f'{board}-{kind}'
            data[name] = old[name]
        smt = old[f'{board}-cpl-SMT-ONLY-INCOMPLETE.csv']
        extra = q.csv_bytes([cpl_row(p) for p in tht if p['board'] == board], FIELDS).split(b'\n', 1)[1]
        q.need(smt.endswith(b'\n'), 'SMT CPL missing final newline')
        complete = smt + extra  # Preserve every inherited SMT byte, including angle offsets.
        check_cpl(board, rows(complete), rows(data[f'{board}-bom.csv']), tht)
        data[f'{board}-cpl.csv'] = complete
    data['tht-placement-verification.csv'] = q.csv_bytes(tht, list(tht[0]))
    data['README.md'] = REVIEW.read_bytes()
    return data


def check_geometry(mpn, pads, pegs):
    """Check labeled contacts, not just a symmetric bounding box; allow drawing rounding."""
    expected = FACTS[mpn]
    q.need(set(pads) == set(expected['pads']), 'THT pin set')
    for pin, point in expected['pads'].items():
        q.need(all(abs(a-b) <= 0.006 for a, b in zip(pads[pin], point)), 'THT pin pose: ' + pin)
    q.need(len(pegs) == len(expected['pegs']), 'THT peg count')
    for actual, target in zip(sorted(pegs), sorted(expected['pegs'])):
        q.need(all(abs(a-b) <= 0.006 for a, b in zip(actual, target)), 'THT peg pose')


def native_audit(data):
    import pcbnew as pcb
    # Reopen both native boards; independently check retained SMT identity and pose.
    smt_audit = q.native_audit(q.DEFAULT)
    population = {(r['board'], r['reference']): r for r in q.read_csv(q.ASSEMBLY / 'population.csv')}
    observations = []
    tht = placements()
    for board in t.COUNTS:
        native = pcb.LoadBoard(str(board_path(board)))
        fps = {f.GetReference(): f for f in native.GetFootprints()}
        actual_cpl = {r['Designator']: r for r in rows(data[f'{board}-cpl.csv'])}
        for p in [p for p in tht if p['board'] == board]:
            fp = fps[p['reference']]
            pop = population[board, p['reference']]
            q.need(fp.GetFPIDAsString() == pop['footprint'] and fp.GetValue() == pop['value'], 'THT identity')
            q.need(not fp.IsFlipped() and fp.GetOrientationDegrees() == 0, 'THT side/angle')
            x, y = fp.GetPosition().x / 1e6, fp.GetPosition().y / 1e6
            q.need(abs(x-p['anchor_x']) < 1e-6 and abs(y-p['anchor_y']) < 1e-6, 'THT origin')
            pads, pegs, nets = {}, [], {}
            for pad in fp.Pads():
                point = (pad.GetPosition().x / 1e6 - x, pad.GetPosition().y / 1e6 - y)
                pin = pad.GetNumber()
                if pin:
                    q.need(pin not in pads and pad.GetAttribute() == pcb.PAD_ATTRIB_PTH, 'Duplicate/non-PTH contact')
                    pads[pin], nets[pin] = point, pad.GetNetname()
                else:
                    q.need(pad.GetAttribute() == pcb.PAD_ATTRIB_NPTH and not pad.GetNetname(), 'Peg type/net')
                    pegs.append(point)
            check_geometry(p['mpn'], pads, pegs)
            q.need(actual_cpl[p['reference']] == cpl_row(p), 'Native-derived CPL pose')
            if p['mpn'] == 'R-78E5.0-0.5':
                q.need(nets == {'1': '/12V', '2': '/GND', '3': '/5V'}, 'RECOM pin functions')
            if p['mpn'] == 'PJ-102AH':
                q.need(nets['1'] == '/VIN12' and nets['2'] == '/GND' and
                       nets['3'].startswith('unconnected-'), 'Power jack pin functions')
            observations.append(dict(board=board, reference=p['reference'], mpn=p['mpn'],
                                     contacts=len(pads), pegs=len(pegs), nets=nets, cpl=actual_cpl[p['reference']]))
    return dict(result='PASS', tool=pcb.Version(), sources=sources(), tht=observations,
                smt=smt_audit, scope='Local source/pin/nominal-body-pose verification; not JLC catalog preview or new release acceptance')


def manifest(data):
    return dict(schema=1, status='COMPLETE_QUOTE_UPLOAD_FILES', quote_upload_ready=True,
                production_ready=False, vendor_preview_approved=False, submitted=False,
                purchase_authorized=False, assembled=t.COUNTS,
                bare_candidates={'carrier': 5, 'pod': 10},
                installed={'JLC_SMT': 478, 'JLC_THT': 28, 'HOME': 18, 'total': 524},
                per_board_jlc={'carrier': 137, 'pod': 29}, sources=sources(),
                files={n: hashlib.sha256(b).hexdigest() for n, b in sorted(data.items())},
                holds=['Exact JLC matching/private source IDs and job stock/gross demand',
                       'Selected-library orientation, component centers and all placements in JLC preview',
                       'Existing fabrication/stencil/mechanical/process controls and THT installation agreement',
                       'Complete quote, explicit purchase and production approval'])


def build(output):
    q.need(not output.exists(), 'Refusing to overwrite existing quote revision')
    data = payloads()
    data['native-audit.json'] = json_bytes(native_audit(data))
    output.mkdir(parents=True)
    for name, content in data.items():
        (output / name).write_bytes(content)
    (output / 'manifest.json').write_bytes(json_bytes(manifest(data)))


def verify(output, live_native=False):
    data = payloads()
    for name, content in data.items():
        q.need((output / name).read_bytes() == content, 'Changed quote artifact: ' + name)
    audit_bytes = (output / 'native-audit.json').read_bytes()
    audit = json.loads(audit_bytes)
    q.need(audit['result'] == 'PASS' and audit['sources'] == sources(), 'Missing/stale native audit')
    expected = {(p['board'], p['reference']): cpl_row(p) for p in placements()}
    q.need(len(audit['tht']) == 11 and
           {(p['board'], p['reference']): p['cpl'] for p in audit['tht']} == expected, 'Audit coverage/poses')
    if live_native:
        q.need(native_audit(data) == audit, 'Live native audit differs')
    data['native-audit.json'] = audit_bytes
    q.need(json.loads((output / 'manifest.json').read_bytes()) == manifest(data), 'Stale/tampered manifest')
    q.need({p.name for p in output.iterdir()} == set(data) | {'manifest.json'}, 'Unexpected/missing package file')
    return dict(result='PASS', quote_upload_ready=True, production_ready=False,
                per_board={'carrier': 137, 'pod': 29}, jlc_batch=506, home_batch=18,
                native_evidence='reexecuted' if live_native else 'retained hash-bound audit')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify'])
    parser.add_argument('--output', type=Path, default=DEFAULT)
    parser.add_argument('--live-native', action='store_true', help='Requires KiCad pcbnew Python')
    args = parser.parse_args()
    try:
        if args.action == 'build':
            build(args.output)
        else:
            print(json.dumps(verify(args.output, args.live_native), indent=2))
    except (ValueError, OSError, ImportError) as error:
        parser.exit(2, str(error) + '\n')
