"""Deterministic synthetic-source to native KiCad schematic tool.

Runtime dependencies: KiCad CLI 10.0.4 and Poppler's pdftoppm executable.

CLI: python3 tools/native_schematic.py build SOURCE.json OUTPUT_DIR
     python3 tools/native_schematic.py verify SOURCE.json OUTPUT_DIR
     python3 tools/native_schematic.py verify-complete SOURCE.json OUTPUT_DIR MEMBERSHIP.json

Source schema, version 1 (shown keys required; optional paper; unknown keys rejected):
{"version":1,"title":"Example","nets":["A","B"],
 "components":[{"ref":"R1","value":"1k","footprint":"Resistor_SMD:R_0603_1608Metric","expected_pins":["1","2"],
   "at":[50.8,50.8],"pins":[{"number":"1","name":"A","type":"passive",
   "at":[-5.08,0],"direction":180,"net":"A"}, ...]}],
 "wire_paths":[{"net":"A","points":[[45.72,50.8],[30.48,50.8]]}, ...]}

Paper defaults to A4; optional "paper" may select landscape A4, A3 or A2.
Coordinates are mm; pin offsets use schematic y-down; direction is the angle
in KiCad library coordinates (0 right, 90 up, 180 left, 270 down). A pin may
instead declare "nc":true (never both). Every connected pin must be an exact
wire-path endpoint. Paths are orthogonal and must connect all pins of their net
by endpoint intersections. No labels are used to conceal missing physical wires.
The receipt is provenance only, never an engineering acceptance decision.
Native schematic bytes and normalized BOM/connectivity are deterministic; PDF
metadata is tool-generated and may vary across runs/platforms, so PDF bytes
are hashed per build while replay compares rendered pages. Receipt hashes detect
staleness; they are not cryptographic proof of authenticity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

TOOLCHAIN = "10.0.4"
GRID = 1.27  # KiCad's 50 mil electrical connection grid; never snap source.
PAPERS = {"A4": (297, 210), "A3": (420, 297), "A2": (594, 420)}
PIN_TYPES = {"input", "output", "bidirectional", "tri_state", "passive", "free", "unspecified", "power_in", "power_out", "open_collector", "open_emitter", "no_connect"}
NS = uuid.UUID("2dbb030c-ec91-4ad4-9627-4f5b53fed97a")


def uid(name):
    return str(uuid.uuid5(NS, name))


def quoted(s):
    return json.dumps(s, ensure_ascii=False)


def fail(message):
    raise ValueError(message)


def keys(obj, required, optional=()):
    if not isinstance(obj, dict) or set(obj) - set(required) - set(optional) or set(required) - set(obj):
        fail(f"fields must be exactly {sorted(required)} with optional {sorted(optional)}: {obj!r}")


def paper_name(source):
    paper = source.get("paper", "A4")
    if not isinstance(paper, str) or paper not in PAPERS:
        fail("paper must be A4, A3 or A2")
    return paper


def point(p, offset=False, grid=False, paper="A4"):
    if not isinstance(p, list) or len(p) != 2 or any(type(v) not in (int, float) or not -594 <= v <= 594 for v in p):
        fail(f"invalid sheet coordinate: {p!r}")
    if not offset and any(not 0 <= v <= limit for v, limit in zip(p, PAPERS[paper])):
        fail(f"electrical geometry outside {paper} sheet: {p!r}")
    if grid and any(abs(float(v) / GRID - round(float(v) / GRID)) > 1e-7 for v in p):
        fail(f"off-grid electrical geometry: {p!r}; use {GRID} mm grid (no automatic snapping)")
    return tuple(round(float(v), 4) for v in p)


def on_segment(p, a, b):
    return (a[0] == b[0] == p[0] and min(a[1], b[1]) <= p[1] <= max(a[1], b[1])) or (a[1] == b[1] == p[1] and min(a[0], b[0]) <= p[0] <= max(a[0], b[0]))


def label_anchors(source):
    """Choose stable grid anchors, avoiding every foreign wire and pin/NC.

    A label at an otherwise unjoined wire crossing can join distinct nets in
    native KiCad. Reject ambiguous endpoints/overlaps instead of rerouting.
    """
    paper = paper_name(source)
    segments = [(w['net'], point(a, grid=True, paper=paper), point(b, grid=True, paper=paper)) for w in source['wire_paths'] for a, b in zip(w['points'], w['points'][1:])]
    pins = [(p.get('net'), (round(c['at'][0]+p['at'][0], 4), round(c['at'][1]+p['at'][1], 4))) for c in source['components'] for p in c['pins']]
    for i, (net, a, b) in enumerate(segments):
        for other, c, d in segments[i+1:]:
            if net != other and any(on_segment(p, x, y) for p, x, y in ((a,c,d), (b,c,d), (c,a,b), (d,a,b))):
                fail(f"ambiguous other-net wire endpoint/overlap: {net}, {other}")
        if any(other != net and on_segment(p, a, b) for other, p in pins):
            fail(f"other-net pin/NC lies on wire {net}")
    result = {}
    for net in source['nets']:
        own = sorted(((a,b) for n,a,b in segments if n == net), key=lambda ab: (-abs(ab[0][0]-ab[1][0])-abs(ab[0][1]-ab[1][1]), ab))
        for a, b in own:
            steps = round((abs(a[0]-b[0])+abs(a[1]-b[1])) / GRID)
            # Prefer the centre but use grid points only; ties go towards a.
            for k in sorted(range(steps+1), key=lambda k: (abs(2*k-steps), k)):
                p = (round(a[0]+(b[0]-a[0])*k/steps, 4), round(a[1]+(b[1]-a[1])*k/steps, 4))
                if not any(n != net and on_segment(p,c,d) for n,c,d in segments) and not any(n != net and p == q for n,q in pins):
                    result[net] = p
                    break
            if net in result:
                break
        if net not in result:
            fail(f"no collision-free grid label anchor for {net}; source geometry must be revised")
    return result


def num(v):
    return f"{v:.4f}".rstrip("0").rstrip(".") if v else "0"


def check(source):
    keys(source, {"version", "title", "nets", "components", "wire_paths"}, {"paper"})
    paper = paper_name(source)
    if source["version"] != 1 or not isinstance(source["title"], str) or not source["title"]:
        fail("version must be 1 and title nonempty")
    nets = source["nets"]
    comps = source["components"]
    if not isinstance(nets, list) or not nets or len(nets) != len(set(nets)) or any(not isinstance(n, str) or not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_+-]*", n) for n in nets):
        fail("nets must be nonempty, unique, safe names")
    if not isinstance(comps, list) or not comps:
        fail("empty circuit")
    refs = set()
    terminals = {n: set() for n in nets}
    for c in comps:
        keys(c, {"ref", "value", "footprint", "expected_pins", "at", "pins"})
        if not isinstance(c["ref"], str) or not re.fullmatch(r"[A-Z]+[1-9][0-9]*", c["ref"]) or c["ref"] in refs:
            fail("duplicate or invalid reference")
        refs.add(c["ref"])
        if any(not isinstance(c[k], str) or not c[k] for k in ("value", "footprint")):
            fail("value and footprint required")
        origin = point(c["at"], paper=paper)
        if not isinstance(c["pins"], list) or not c["pins"]:
            fail("component has no pins")
        numbers = set()
        for p in c["pins"]:
            keys(p, {"number", "name", "type", "at", "direction"}, {"net", "nc"})
            if not isinstance(p["number"], str) or not p["number"] or p["number"] in numbers:
                fail("duplicate or empty pin number")
            numbers.add(p["number"])
            if not isinstance(p["name"], str) or not p["name"] or p["type"] not in PIN_TYPES or p["direction"] not in (0, 90, 180, 270):
                fail("invalid pin function, type, or direction")
            offset = point(p["at"], offset=True)
            absolute = point([c['at'][0]+p['at'][0], c['at'][1]+p['at'][1]], grid=True, paper=paper)
            if ("net" in p) == ("nc" in p) or ("nc" in p and p["nc"] is not True):
                fail("pin needs exactly one net or true nc")
            if "net" in p:
                if p["net"] not in terminals:
                    fail("unknown net")
                terminals[p["net"]].add(absolute)
        expected_pins = c['expected_pins']
        if not isinstance(expected_pins, list) or not expected_pins or any(not isinstance(n, str) or not n for n in expected_pins) or len(expected_pins) != len(set(expected_pins)) or set(expected_pins) != numbers:
            fail(f"pin coverage mismatch for {c['ref']}")
    paths = source["wire_paths"]
    if not isinstance(paths, list):
        fail("wire_paths must be list")
    segments = {n: [] for n in nets}
    for path in paths:
        keys(path, {"net", "points"})
        if path["net"] not in segments or not isinstance(path["points"], list) or len(path["points"]) < 2:
            fail("invalid wire path")
        points = [point(p, grid=True, paper=paper) for p in path["points"]]
        for a, b in zip(points, points[1:]):
            if a == b or (a[0] != b[0] and a[1] != b[1]):
                fail("wire segments must be nonzero and orthogonal")
            segments[path["net"]].append((a, b))
    for net, pins in terminals.items():
        if not pins:
            fail(f"net {net} has no pins")
        edges = segments[net]
        if not edges:
            fail(f"net {net} has no wire path")
        vertices = set(sum(([a, b] for a, b in edges), []))
        if not pins <= vertices:
            fail(f"net {net} pin omitted from wire endpoints: {pins - vertices}")
        seen = {next(iter(pins))}
        while True:
            more = seen | {b for a, b in edges if a in seen} | {a for a, b in edges if b in seen}
            if more == seen:
                break
            seen = more
        if not pins <= seen:
            fail(f"net {net} has disconnected paths")
    label_anchors(source)
    return terminals


def render(source, project, notices=()):
    root = uid("root:" + project)
    lines = [f'(kicad_sch (version 20250114) (generator "eeschema") (uuid {root}) (paper {quoted(paper_name(source))}) (title_block (title {quoted(source["title"])}))', '(lib_symbols']
    for c in source["components"]:
        ref = c["ref"]
        lib = f"Native:{ref}"
        pins = c["pins"]
        xs = [p["at"][0] for p in pins]
        ys = [p["at"][1] for p in pins]
        left, right = min(-2.54, min(xs)+2.54), max(2.54, max(xs)-2.54)
        top, bottom = min(-2.54, min(ys)+2.54), max(2.54, max(ys)-2.54)
        lines.append(f'(symbol {quoted(lib)} (pin_names (offset 0.508)) (in_bom yes) (on_board yes)')
        for name, val in (("Reference", re.match(r"[A-Z]+", ref).group()), ("Value", c["value"]), ("Footprint", c["footprint"])):
            lines.append(f'(property {quoted(name)} {quoted(val)} (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
        lines.append(f'(symbol {quoted(ref+"_1_1")} (rectangle (start {num(left)} {num(-top)}) (end {num(right)} {num(-bottom)}) (stroke (width 0.254) (type default)) (fill (type background)))')
        for p in pins:
            x, y = p["at"]
            lines.append(f'(pin {p["type"]} line (at {num(x)} {num(-y)} {p["direction"]}) (length 2.54) (name {quoted(p["name"])} (effects (font (size 1.27 1.27)))) (number {quoted(p["number"])} (effects (font (size 1.27 1.27)))))')
        lines.append('))')
    lines.append(')')
    for c in source["components"]:
        ref, (x, y) = c["ref"], c["at"]
        lines.append(f'(symbol (lib_id {quoted("Native:"+ref)}) (at {num(x)} {num(y)} 0) (unit 1) (in_bom yes) (on_board yes) (dnp no) (uuid {uid("symbol:"+ref)})')
        top_pin = min(p['at'][1] for p in c['pins'])
        bottom_pin = max(p['at'][1] for p in c['pins'])
        for name, val, dy in (("Reference", ref, top_pin-5.08), ("Value", c["value"], bottom_pin+5.08), ("Footprint", c["footprint"], 0)):
            hide = ' hide' if name == 'Footprint' else ''
            lines.append(f'(property {quoted(name)} {quoted(val)} (at {num(x)} {num(y+dy)} 0) (effects (font (size 1.27 1.27)){hide}))')
        for p in c["pins"]:
            lines.append(f'(pin {quoted(p["number"])} (uuid {uid("pin:"+ref+":"+p["number"])}))')
        lines.append(f'(instances (project {quoted(project)} (path "/{root}" (reference {quoted(ref)}) (unit 1)))))')
        for p in c["pins"]:
            if p.get("nc"):
                px, py = x+p["at"][0], y+p["at"][1]
                lines.append(f'(no_connect (at {num(px)} {num(py)}) (uuid {uid("nc:"+ref+":"+p["number"])}))')
    for i, path in enumerate(source["wire_paths"]):
        for j, (a, b) in enumerate(zip(path["points"], path["points"][1:])):
            lines.append(f'(wire (pts (xy {num(a[0])} {num(a[1])}) (xy {num(b[0])} {num(b[1])})) (stroke (width 0) (type default)) (uuid {uid(f"wire:{i}:{j}")}))')
    for net, (x, y) in label_anchors(source).items():
        lines.append(f'(label {quoted(net)} (at {num(x)} {num(y)} 0) (effects (font (size 1.27 1.27)) (justify left bottom)) (uuid {uid("label:"+net)}))')
    for i, notice in enumerate(notices):
        lines.append(f'(text {quoted(notice)} (at 15 {15+i*5} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid {uid("notice:"+str(i))}))')
    lines.append(')')
    return '\n'.join(lines)+'\n'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        fail(f"{args[0]} failed ({result.returncode}): {result.stdout} {result.stderr}")
    return result


def raster_hashes(pdf, prefix):
    run(['pdftoppm', '-png', '-r', '72', str(pdf), str(prefix)])
    pages = sorted(prefix.parent.glob(prefix.name+'-*.png'))
    if not pages:
        fail('PDF has no rendered pages')
    return [digest(page) for page in pages]


def erc_clean(path):
    report = json.loads(path.read_text())
    if not isinstance(report, dict) or report.get('kicad_version') != TOOLCHAIN or 'error' not in report.get('included_severities', []) or not isinstance(report.get('sheets'), list) or not report['sheets']:
        fail('malformed ERC report')
    for sheet in report['sheets']:
        if not isinstance(sheet, dict) or not isinstance(sheet.get('violations'), list):
            fail('malformed ERC sheet')
        if sheet['violations']:
            fail(f"ERC findings: {sheet['violations']}")


def parity(source, netlist):
    tree = ET.parse(netlist)
    actual = {}
    for c in tree.findall('./components/comp'):
        if c.attrib['ref'] in actual:
            fail('duplicate exported component')
        actual[c.attrib['ref']] = (c.findtext('value'), c.findtext('footprint') or '')
    expected = {c['ref']: (c['value'], c['footprint']) for c in source['components']}
    if actual != expected:
        fail(f"component value/footprint mismatch: {actual} != {expected}")
    observed = {}
    for net in tree.findall('./nets/net'):
        name = net.attrib.get('name')
        if name and name.startswith('/'):
            name = name[1:]
        for node in net.findall('node'):
            pair = (node.attrib['ref'], node.attrib['pin'])
            if pair in observed:
                fail(f"duplicate exported pin {pair}")
            observed[pair] = name
    wanted = {(c['ref'], p['number']): p.get('net') for c in source['components'] for p in c['pins']}
    for pair, wanted_net in wanted.items():
        if wanted_net is None and pair in observed:
            expected_nc = rf'^unconnected-\({re.escape(pair[0])}-.*-Pad{re.escape(pair[1])}\)$'
            if re.fullmatch(expected_nc, observed[pair] or ''):
                observed[pair] = None
    if observed != wanted:
        fail(f"pin/net parity mismatch: exported {observed}; source {wanted}")
    return {'components': actual, 'pins': observed}


def artifacts(out):
    return {'source': out/'source.json', 'schematic': out/'native.kicad_sch', 'netlist': out/'native.xml', 'erc': out/'native-erc.json', 'erc_all': out/'native-erc-all.json', 'pdf': out/'native.pdf'}


def erc_summary(path):
    report = json.loads(path.read_text())
    if report.get('kicad_version') != TOOLCHAIN or not {'error', 'warning'} <= set(report.get('included_severities', [])) or not report.get('sheets'):
        fail('malformed all-severity ERC report')
    counts = {}
    for sheet in report['sheets']:
        for item in sheet['violations']:
            severity = item.get('severity', 'unknown')
            counts[severity] = counts.get(severity, 0) + 1
    return counts


def verify(source_path, out, require_receipt=True, notices=()):
    source = json.loads(source_path.read_text())
    check(source)
    version = run(['kicad-cli', 'version']).stdout.strip()
    if version != TOOLCHAIN:
        fail(f"requires KiCad CLI {TOOLCHAIN}; got {version}")
    paths = artifacts(out)
    for name, p in paths.items():
        if not p.is_file() or not p.stat().st_size:
            fail(f"missing/empty {name}")
    if paths['source'].read_bytes() != source_path.read_bytes():
        fail("output source snapshot is stale")
    if paths['schematic'].read_text() != render(source, 'native', notices):
        fail("native schematic differs from source rendering")
    erc_clean(paths['erc'])
    summary = erc_summary(paths['erc_all'])
    if require_receipt:
        receipt = json.loads((out/'receipt.json').read_text())
        if receipt['tool_version'] != TOOLCHAIN or receipt['builder_sha256'] != digest(Path(__file__)) or receipt['hashes'] != {k: digest(v) for k, v in paths.items()}:
            fail("stale/tampered output receipt")
        if receipt.get('erc_all_severity_counts') != summary:
            fail("receipt all-severity ERC counts differ from report")
    # Re-export from the exact native file, independently of stored artifacts.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        fresh = Path(tmp)
        run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(fresh/'native.xml'), str(paths['schematic'])])
        parity(source, fresh/'native.xml')
        if (fresh/'native.xml').read_bytes() != paths['netlist'].read_bytes():
            # Timestamps may differ; stored netlist must at least preserve all facts.
            parity(source, paths['netlist'])
        run(['kicad-cli', 'sch', 'erc', '--format', 'json', '--severity-error', '--exit-code-violations', '-o', str(fresh/'native-erc.json'), str(paths['schematic'])])
        erc_clean(fresh/'native-erc.json')
        run(['kicad-cli', 'sch', 'erc', '--format', 'json', '--severity-all', '-o', str(fresh/'native-erc-all.json'), str(paths['schematic'])])
        if erc_summary(fresh/'native-erc-all.json') != erc_summary(paths['erc_all']):
            fail('all-severity ERC summary differs from native replay')
        run(['kicad-cli', 'sch', 'export', 'pdf', '-o', str(fresh/'native.pdf'), str(paths['schematic'])])
        if raster_hashes(paths['pdf'], fresh/'stored-page') != raster_hashes(fresh/'native.pdf', fresh/'fresh-page'):
            fail('PDF rendered pages differ from native schematic export')
    return True


def build(source_path, out, notices=()):
    source = json.loads(source_path.read_text())
    check(source)
    version = run(['kicad-cli', 'version']).stdout.strip()
    if version != TOOLCHAIN:
        fail(f"requires KiCad CLI {TOOLCHAIN}; got {version}")
    out.mkdir(parents=True, exist_ok=True)
    paths = artifacts(out)
    # A failed rebuild must never leave a prior apparently valid review receipt.
    (out/'receipt.json').unlink(missing_ok=True)
    paths['source'].write_bytes(source_path.read_bytes())
    paths['schematic'].write_text(render(source, 'native', notices))
    run(['kicad-cli', 'sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(paths['netlist']), str(paths['schematic'])])
    parity(source, paths['netlist'])
    run(['kicad-cli', 'sch', 'erc', '--format', 'json', '--severity-all', '-o', str(paths['erc_all']), str(paths['schematic'])])
    summary = erc_summary(paths['erc_all'])
    run(['kicad-cli', 'sch', 'erc', '--format', 'json', '--severity-error', '--exit-code-violations', '-o', str(paths['erc']), str(paths['schematic'])])
    erc_clean(paths['erc'])
    run(['kicad-cli', 'sch', 'export', 'pdf', '-o', str(paths['pdf']), str(paths['schematic'])])
    receipt = {'tool_version': version, 'builder_sha256': digest(Path(__file__)), 'hashes': {k: digest(v) for k, v in paths.items()}, 'erc_all_severity_counts': summary, 'note': 'Export parity and absence of ERC errors only; all-severity findings retained, not waived. No engineering acceptance verdict.'}
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    verify(source_path, out, notices=notices)


def check_membership(source, membership):
    """Compare against separately reviewed design membership, not export counts.

    Membership schema: {version:1, components:{ref:{value,footprint,pins:[...] }},
    nets:[...]}. It must originate from complete architecture/parts evidence;
    copying it from a partial generated source cannot establish completeness.
    This checks flat-sheet membership, not hierarchy or engineering acceptance.
    """
    check(source)
    keys(membership, {'version', 'components', 'nets'})
    if type(membership['version']) is not int or membership['version'] != 1:
        fail('invalid membership version')
    expected = membership['components']
    if not isinstance(expected, dict) or not expected:
        fail('empty or invalid expected component membership')
    for ref, item in expected.items():
        if not isinstance(ref, str) or not re.fullmatch(r'[A-Z]+[1-9][0-9]*', ref):
            fail('invalid expected reference')
        keys(item, {'value', 'footprint', 'pins'})
        if any(not isinstance(item[k], str) or not item[k] for k in ('value', 'footprint')):
            fail('expected value and footprint required')
        pins = item['pins']
        if (not isinstance(pins, list) or not pins
                or any(not isinstance(p, str) or not p for p in pins)
                or len(set(pins)) != len(pins)):
            fail('invalid expected pin membership')
    nets = membership['nets']
    if (not isinstance(nets, list) or not nets
            or any(not isinstance(n, str) or not n for n in nets)
            or len(set(nets)) != len(nets)):
        fail('invalid expected net membership')
    actual = {c['ref']: {'value': c['value'], 'footprint': c['footprint'],
                         'pins': sorted(p['number'] for p in c['pins'])}
              for c in source['components']}
    normalized = {ref: dict(item, pins=sorted(item['pins'])) for ref, item in expected.items()}
    if actual != normalized or set(source['nets']) != set(nets):
        fail('source differs from complete design membership')
    return True


def verify_complete(source_path, out, membership_path):
    """Reopen membership plus real native/PDF/netlist/ERC; never admit a stage."""
    check_membership(json.loads(source_path.read_text()), json.loads(membership_path.read_text()))
    verify(source_path, out)
    return {'source_sha256': digest(source_path),
            'membership_sha256': digest(membership_path),
            'build_receipt_sha256': digest(out/'receipt.json'),
            'builder_sha256': digest(Path(__file__)),
            'note': 'Flat design membership and native replay only; no engineering acceptance.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('command', choices=('build', 'verify', 'verify-complete'))
    ap.add_argument('source', type=Path)
    ap.add_argument('output_dir', type=Path)
    ap.add_argument('membership', type=Path, nargs='?')
    args = ap.parse_args()
    if (args.command == 'verify-complete') != (args.membership is not None):
        ap.error('MEMBERSHIP is required only for verify-complete')
    try:
        if args.command == 'build':
            build(args.source, args.output_dir)
        elif args.command == 'verify':
            verify(args.source, args.output_dir)
        else:
            print(json.dumps(verify_complete(args.source, args.output_dir, args.membership), sort_keys=True))
    except (ValueError, OSError, ET.ParseError, json.JSONDecodeError) as exc:
        print(f'native schematic: {exc}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
