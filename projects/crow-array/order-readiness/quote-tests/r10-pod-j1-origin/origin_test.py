"""Prepare a diagnostic CPL, not an accepted vendor-coordinate conversion."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ORDER = HERE.parents[1]
AB = HERE.parent / 'r10-pod-j1-180'
spec = importlib.util.spec_from_file_location('ab_test', AB / 'test_cpl.py')
ab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ab)
AUDIT = ORDER / 'r10-registration-review/native-audit.json'
CATALOG = ORDER / 'r10-orientation-images/catalog/C599441/jlc.pretty/RJ45-TH_RJHSE-5080.kicad_mod'
AUDIT_SHA = '8e1d84de40b6075c138971aec8decbb9632643fc0aafc27d187c3c375536a742'
CATALOG_SHA = 'ffd7f2a6381989e7a569e3ed018aee047d8964952351082be7318de1a83caf7d'
OUTPUT = 'pod-cpl-J1-180-Y9390-TEST-ONLY.csv'


def derive(native, vendor, native_pegs, vendor_pegs):
    """Fit translation at fixed 180 degrees; independently grade the pegs."""
    if set(native) != set(map(str, range(1, 9))) or set(vendor) != set(native):
        raise ValueError('Expected eight uniquely numbered terminals')
    if len(native_pegs) != 2 or len(vendor_pegs) != 2:
        raise ValueError('Expected two locator pegs')
    t = [sum(native[n][i] + vendor[n][i] for n in native) / 8 for i in (0, 1)]
    predicted = {n: [t[i] - vendor[n][i] for i in (0, 1)] for n in native}
    error = max(math.dist(predicted[n], native[n]) for n in native)
    pp = [[t[i] - p[i] for i in (0, 1)] for p in vendor_pegs]
    peg_error = max(math.dist(a, b) for a, b in zip(sorted(pp), sorted(native_pegs)))
    if not all(math.isfinite(x) for x in t + [error, peg_error]):
        raise ValueError('Non-finite geometry')
    if error > .03 or peg_error > .03:
        raise ValueError('Catalog geometry does not register to native witnesses')
    return {'conditional_catalog_insertion_native_mm': t,
            'predicted_pins_native_mm': predicted, 'predicted_pegs_native_mm': pp,
            'max_pin_error_mm': error, 'max_peg_error_mm': peg_error}


def geometry():
    for path, digest in ((AUDIT, AUDIT_SHA), (CATALOG, CATALOG_SHA)):
        if ab.sha(path.read_bytes()) != digest:
            raise ValueError('Changed geometry source: ' + str(path))
    audit = json.loads(AUDIT.read_text())
    witnesses = [r for r in audit['connector_witnesses'] if r['board'] == 'pod' and r['reference'] == 'J1']
    if len(witnesses) != 1:
        raise ValueError('Expected one pod J1 witness')
    source = ORDER / 'quote-draft/r10-2c8p-outward-power/native/pcb/pod/pod.kicad_pcb'
    if ab.sha(source.read_bytes()) != audit['sources'][str(source.relative_to(ORDER))]:
        raise ValueError('Native board no longer matches audit')
    entries = re.findall(r'\(pad (\d+|"") thru_hole circle \(at ([-\d.]+) ([-\d.]+)', CATALOG.read_text())
    pins = {n: [float(x), float(y)] for n, x, y in entries if n != '""'}
    pegs = [[float(x), float(y)] for n, x, y in entries if n == '""']
    if len(entries) != 10 or len(pins) != 8:
        raise ValueError('Unexpected catalog pad syntax or census')
    w = witnesses[0]
    result = derive(w['native_pads'], pins, w['native_locator_holes'], pegs)
    result['native_witnesses'] = w['native_pads']
    result['native_locator_holes'] = w['native_locator_holes']
    return result


def make_c(b, position):
    rows = ab.rows(b)
    j1 = next(r for r in rows if r['Designator'] == 'J1')
    if j1 != dict(zip(ab.HEADER, ['J1', '10.556000mm', '-8.373000mm', '180.000000', 'Top'])):
        raise ValueError('Expected exact B pose')
    if any(abs(a-b) > 1e-9 for a,b in zip(position, [10.556, 9.390])) or len(position) != 2:
        raise ValueError('Unexpected derived position; requires new review')
    old = b'J1,10.556000mm,-8.373000mm,180.000000,Top'
    new = b'J1,10.556000mm,-9.390000mm,180.000000,Top'
    lines = b.splitlines(keepends=True)
    indices = [i for i,line in enumerate(lines) if line.rstrip(b'\r\n') == old]
    if len(indices) != 1:
        raise ValueError('Expected exactly one B row')
    i = indices[0]
    lines[i] = new + lines[i][len(old):]
    return b''.join(lines)


def compare(b, c, position):
    if c != make_c(b, position):
        raise ValueError('Changes beyond the single J1 Y field')
    return [('J1', 'Mid Y', '-8.373000mm', '-9.390000mm')]


def expected():
    ab.run()  # B and A remain bound to the original board, CPL and generator.
    geo = geometry()
    b = (AB / ab.TRIAL).read_bytes()
    c = make_c(b, geo['conditional_catalog_insertion_native_mm'])
    compare(b, c, geo['conditional_catalog_insertion_native_mm'])
    manifest = {
        'status': 'QUOTE_ONLY_UNACCEPTED_ORIGIN_EXPERIMENT',
        'hypothesis': 'The JLC draft uses the retained catalog footprint origin without recentering; not established by public CAD alone.',
        'source_session_commit': 'a8e2cf84aad458ec2edd5894391503e943dde6e9',
        'source_hashes': {str(p.relative_to(ORDER)): ab.sha(p.read_bytes()) for p in (AUDIT, CATALOG, AB / ab.TRIAL, AB / 'test_cpl.py')},
        'generator_sha256': ab.sha(Path(__file__).read_bytes()),
        'geometry': geo,
        'references': 29,
        'change_from_B': {'reference': 'J1', 'field': 'Mid Y', 'before': '-8.373000mm', 'after': '-9.390000mm'},
        'file_sha256': ab.sha(c), 'file': OUTPUT,
        'browser_test_performed': False, 'alignment_verified': False, 'production_ready': False}
    return {OUTPUT: c, 'manifest.json': (json.dumps(manifest, indent=2)+'\n').encode()}


def run(build=False):
    outputs = expected()
    for name, data in outputs.items():
        path = HERE / name
        if path.exists() and path.read_bytes() != data:
            raise ValueError('Changed output: ' + name)
    for name, data in outputs.items():
        path = HERE / name
        if build and not path.exists():
            path.write_bytes(data)
        if path.read_bytes() != data:
            raise ValueError('Output mismatch: ' + name)
    return {'result': 'PASS_DIAGNOSTIC_CPL_INTEGRITY_ONLY', 'only_change_from_B': 'J1 Y -8.373 -> -9.390 mm', 'production_ready': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    print(json.dumps(run(parser.parse_args().command == 'build'), indent=2))
