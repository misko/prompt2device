"""Legacy-tool measurements and explicit-CPL replay. Diagnostic, never approval."""
import argparse
import ast
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import sys

import pcbnew

HERE = Path(__file__).resolve().parent
ORDER = HERE.parents[1]
ROOT = ORDER.parents[2]
LEGACY = ROOT / 'skills/jlcpcb-fab/scripts'
sys.path.insert(0, str(LEGACY))
import jlc_rotation_measure as measure

BASE = ORDER / 'quote-draft/r10-2c8p-outward-power'
CAT = ORDER / 'r10-orientation-images/catalog'
FROZEN = {
    'carrier-cpl.csv': 'ea748566517886a3dee50eaaa176c173f5fde86f45fc48a42e24c97d68e5855d',
    'pod-cpl.csv': '6d1884eae3369d239da8d7f6214e27d8296df49d61daed141d9a126b4b2df9ae',
    'native/pcb/carrier/carrier.kicad_pcb': '1fc774524ef57efdd3a644de338328837e42ba648d3a4dd6bb78bad44e8852a1',
    'native/pcb/pod/pod.kicad_pcb': 'd67134d2361f32f25a1f8841134f21f84791d3d36ede1acb74b383d5b007ceb9',
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def need(ok, why):
    if not ok:
        raise ValueError(why)


def points(fp):
    pins, pegs = {}, []
    for pad in fp.Pads():
        xy = [pad.GetPosition().x / 1e6, pad.GetPosition().y / 1e6]
        n = pad.GetNumber()
        if n:
            need(n not in pins, 'duplicate terminal')
            pins[n] = xy
        else:
            pegs.append(xy)
    return pins, pegs


def replay(pins, pegs, row):
    """No fitting: use the actual CSV pose and the raw catalog origin."""
    need(row['Layer'] == 'Top', 'unsupported side')
    x, y = float(row['Mid X'].removesuffix('mm')), -float(row['Mid Y'].removesuffix('mm'))
    a = math.radians(float(row['Rotation']))
    need(all(math.isfinite(v) for v in (x, y, a)), 'nonfinite pose')
    def move(p):
        return [x + p[0]*math.cos(a) + p[1]*math.sin(a),
                y - p[0]*math.sin(a) + p[1]*math.cos(a)]
    return {n: move(p) for n, p in pins.items()}, [move(p) for p in pegs]


def errors(expected, pegs, actual, actual_pegs):
    need(set(expected) == set(actual) and len(pegs) == len(actual_pegs), 'feature census')
    return dict(max_pin_mm=max(math.dist(expected[n], actual[n]) for n in expected),
                max_peg_mm=max((math.dist(a, b) for a, b in zip(sorted(pegs), sorted(actual_pegs))), default=0))


def revise(blob, replacements):
    lines = blob.decode().splitlines(keepends=True)
    header = next(csv.reader([lines[0]]))
    seen = set()
    for i, line in enumerate(lines[1:], 1):
        values = next(csv.reader([line]))
        row = dict(zip(header, values))
        ref = row['Designator']
        need(ref not in seen, 'duplicate CPL reference')
        seen.add(ref)
        if ref in replacements:
            out = io.StringIO(newline='')
            csv.writer(out, lineterminator='\r\n' if line.endswith('\r\n') else '\n').writerow(
                [replacements[ref][k] for k in header])
            lines[i] = out.getvalue()
    need(set(replacements) <= seen, 'missing replacement reference')
    return ''.join(lines).encode()


def expected():
    for name, digest in FROZEN.items():
        need(sha(BASE/name) == digest, 'changed r10 input: '+name)
    # Reuse the actual legacy datum function without executing its exporter.
    exporter = LEGACY/'export_jlc_package.py'
    fn = next(n for n in ast.parse(exporter.read_text()).body
              if isinstance(n, ast.FunctionDef) and n.name == 'placement_datum')
    namespace = {'pcbnew': pcbnew}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(exporter), 'exec'), namespace)
    sources = [HERE/'mapping.py', exporter, LEGACY/'jlc_rotation_measure.py',
               ORDER/'r10-orientation-images/sources/rjhsex080.pdf',
               ORDER/'power-jack-r10-review/source-evidence/2-P028-manufacturer.pdf']
    sources += [BASE/n for n in FROZEN]
    results, outputs = [], {}
    for board_name in ('pod', 'carrier'):
        board = pcbnew.LoadBoard(str(BASE/f'native/pcb/{board_name}/{board_name}.kicad_pcb'))
        blob = (BASE/f'{board_name}-cpl.csv').read_bytes()
        rows = {r['Designator']: r for r in csv.DictReader(io.StringIO(blob.decode()))}
        inspection = ORDER/f'render-review-r10/{board_name}-inspection.json'
        sources.append(inspection)
        facts = json.loads(inspection.read_text())['connectors']
        refs = ['J1'] if board_name == 'pod' else ['J1'] + ['J'+str(n) for n in range(101,109)]
        changes = {}
        for ref in refs:
            fp = board.FindFootprintByReference(ref)
            power = board_name == 'carrier' and ref == 'J1'
            code, mpn = ('C3096093','PJ-102AH') if power else ('C599441','RJHSE-5080')
            need(fp and not fp.IsFlipped() and fp.GetFieldText('MPN') == mpn, 'native identity/side')
            mod = next((CAT/code/'jlc.pretty').glob('*.kicad_mod'))
            sources.append(mod)
            vendor = pcbnew.FootprintLoad(str(mod.parent), mod.stem)
            native, native_pegs = points(fp)
            vp, vpegs = points(vendor)
            need(len(native) == (3 if power else 8) and len(native_pegs) == (0 if power else 2), 'native census')
            # Reviewed manufacturer facts are in footprint-local native coordinates.
            fact = facts[ref]
            need(fact['mpn'] == mpn and set(fact['expected_pads']) == set(native), 'manufacturer identity')
            for n, p in fact['expected_pads'].items():
                q = measure.rot(*p, fp.GetOrientationDegrees())
                q = [q[0]+fp.GetPosition().x/1e6, q[1]+fp.GetPosition().y/1e6]
                need(math.dist(q, native[n]) <= fact['tolerance_mm'], 'manufacturer terminal disagreement')
            # Legacy numbered fit, independently cross-checked against complete peg geometry below.
            op = [p for p in measure.our_pads(fp) if p['num']]
            jp, _ = measure.parse_mod(mod)
            fits, common = measure.fit_by_number(op, jp)
            ranked = sorted(fits, key=lambda a: fits[a][0])
            angle = ranked[0]
            need(set(common) == set(native) and fits[angle][0] < .03 and fits[ranked[1]][0] > 1,
                 'ambiguous/poor numbered fit')
            absolute = (fp.GetOrientationDegrees()+angle) % 360
            rotated = {n: measure.rot(*vp[n], absolute) for n in native}
            translation = [sum(native[n][i]-rotated[n][i] for n in native)/len(native) for i in (0,1)]
            candidate = dict(rows[ref], **{'Mid X':f'{translation[0]:.6f}mm',
                'Mid Y':f'{-translation[1]:.6f}mm', 'Rotation':f'{absolute:.6f}'})
            old_error = errors(native, native_pegs, *replay(vp, vpegs, rows[ref]))
            new_error = errors(native, native_pegs, *replay(vp, vpegs, candidate))
            need(max(new_error.values()) < .03, 'candidate does not register all terminals/pegs')
            datum = namespace['placement_datum'](fp)
            vendor_datum = namespace['placement_datum'](vendor)
            result = dict(board=board_name, reference=ref, code=code, mpn=mpn,
                local_rotation_fits=fits, local_correction_deg=angle,
                native_rotation_deg=fp.GetOrientationDegrees(), before=rows[ref], candidate=candidate,
                native_pins=native, native_pegs=native_pegs, catalog_pins=vp, catalog_pegs=vpegs,
                legacy_native_datum_mm=[datum.x/1e6,datum.y/1e6],
                legacy_catalog_datum_mm=[vendor_datum.x/1e6,vendor_datum.y/1e6],
                baseline_raw_origin_replay=old_error, candidate_raw_origin_replay=new_error,
                candidate_mouth_direction_native=fact['intended_direction'],
                mouth_basis='Inherited manufacturer-bound native inspection; no live JLC model proof')
            results.append(result)
            changes[ref] = candidate
        outputs[f'{board_name}-ALL-CONNECTORS-RAW-ORIGIN-TEST-ONLY.csv'] = revise(blob, changes)
        if board_name == 'carrier':
            for ref in ('J1','J101'):
                outputs[f'carrier-{ref}-ONLY-RAW-ORIGIN-TEST-ONLY.csv'] = revise(blob, {ref:changes[ref]})
    need(len(results) == 10, 'connector denominator')
    report = dict(status='CATALOG_REGISTRATION_DIAGNOSTIC_ONLY', production_ready=False,
        live_vendor_verified=False, independent_acceptance=False,
        convention='CPL XY is raw retained catalog origin; NOT established for live JLC draft',
        sources={str(p.relative_to(ROOT)):sha(p) for p in sorted(set(sources))}, connectors=results)
    outputs['measurements.json'] = (json.dumps(report,indent=2,sort_keys=True)+'\n').encode()
    return outputs


def run(build=False):
    out = HERE/'generated'
    payload = expected()
    if build:
        out.mkdir(exist_ok=True)
    for name, content in payload.items():
        target = out/name
        if build and not target.exists():
            target.write_bytes(content)
        need(target.read_bytes() == content, 'changed output: '+name)
    need({p.name for p in out.iterdir()} == set(payload), 'unexpected output membership')
    return {'result':'PASS_CONDITIONAL_CATALOG_REPLAY_ONLY','connectors':10,'production_ready':False}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build','verify'])
    print(json.dumps(run(parser.parse_args().action == 'build')))
