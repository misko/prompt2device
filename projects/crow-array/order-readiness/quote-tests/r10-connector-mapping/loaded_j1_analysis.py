"""Source-bound pod J1 diagnostic. No board, CPL or browser changes."""
import argparse
import json
import math
from pathlib import Path

import mapping

HERE = Path(__file__).resolve().parent
CAPTURE = HERE / 'macbook-j1-cache-20261102/C599441-loaded-footprint.json'
CAPTURE_SHA = 'c09dbe4e2bc3b4396109e23740f67b03758ca5ac515747f3ad82d108e2d0c8be'
MODEL_UUID = '7d3d1c9e95104606a19576559311bb67'
MODEL_SHA = '7e16867569831cd98a298dcf3dc5d4692343d067e36dc1aed26f7216d8ff39da'
MODEL_URL = 'https://modules.lceda.cn/3dmodel/' + MODEL_UUID


def bounds(points):
    mapping.need(bool(points), 'empty geometry')
    return ([min(p[i] for p in points) for i in range(len(points[0]))],
            [max(p[i] for p in points) for i in range(len(points[0]))])


def centre(points):
    lo, hi = bounds(points)
    return [(a+b)/2 for a, b in zip(lo, hi)]


def footprint():
    mapping.need(mapping.sha(CAPTURE) == CAPTURE_SHA, 'captured footprint changed')
    record = json.loads(CAPTURE.read_text())
    mapping.need(record['uuid'] == '4305e070e23841dcbc23b07ddde0edab', 'package UUID')
    data = record['dataStr']
    origin = list(map(float, data['canvas'].split('~')[16:18]))
    pins, pegs, nodes = {}, [], []
    def xy(x, y):
        # Ld: canvas-relative 10-mil coordinates; report in native Y-down mm.
        return [(float(x)-origin[0])*.254, (float(y)-origin[1])*.254]
    for shape in data['shape']:
        fields = shape.split('~')
        if fields[0] == 'PAD':
            mapping.need(fields[8] not in pins, 'duplicate pin')
            pins[fields[8]] = xy(fields[2], fields[3])
        elif fields[0] == 'HOLE':
            pegs.append(xy(fields[1], fields[2]))
        elif fields[0] == 'SVGNODE':
            nodes.append(json.loads(shape.split('~', 1)[1]))
    mapping.need(set(pins) == set('12345678') and len(pegs) == 2 and len(nodes) == 1,
                 'captured feature census')
    node = nodes[0]
    attrs = node['attrs']
    mapping.need(attrs['uuid'] == MODEL_UUID and not attrs.get('transformV2'), 'model path changed')
    mapping.need(attrs['c_rotation'] == '0,0,0', 'unsupported model rotation')
    model_origin = list(map(float, attrs['c_origin'].split(',')))
    outline = []
    for child in node['childNodes']:
        values = list(map(float, child['attrs']['points'].split()))
        outline += list(zip(values[::2], values[1::2]))
    delta_mil = [abs(a-b)*10 for a, b in zip(centre(outline), model_origin)]
    # Ld overrides c_origin only if a child-outline centre differs by >0.1 mil.
    mapping.need(max(delta_mil) <= .1, 'viewer outline-centre override requires review')
    transform = dict(offset_native_mm=xy(*model_origin), z_mm=float(attrs['z'])*.254,
                     target_span_mm=[float(attrs[k])*.254 for k in ('c_width', 'c_height')],
                     child_centre_delta_mil=delta_mil)
    return pins, pegs, transform, data['head']['uuid_3d']


def model_features(path, transform):
    """Fixed-asset terminal-tip/peg-bottom profile measurements, NOT hole-fit proof."""
    mapping.need(mapping.sha(path) == MODEL_SHA, 'public OBJ changed; review before reuse')
    vertices = [tuple(map(float, line.split()[1:4])) for line in path.read_text().splitlines()
                if line.startswith('v ')]
    mapping.need(len(vertices) == 7002, 'model vertex census')
    lo, hi = bounds(vertices)
    scale = min(transform['target_span_mm'][i]/(hi[i]-lo[i]) for i in (0, 1))
    mid = [(lo[i]+hi[i])/2 for i in (0, 1)]
    def local(p):
        # N$: XY bbox recenter, uniform scale, then model origin. Native Y is down.
        return [(p[0]-mid[0])*scale+transform['offset_native_mm'][0],
                -(p[1]-mid[1])*scale+transform['offset_native_mm'][1]]
    inner = [p for p in vertices if abs(p[0]) < 4]
    z = min(p[2] for p in inner)
    remaining = {p[:2] for p in inner if abs(p[2]-z) < 1e-7}
    groups = []
    while remaining:
        group = {min(remaining)}
        remaining -= group
        while True:
            additions = {p for p in remaining if any(math.dist(p, q) < .65 for q in group)}
            if not additions:
                break
            remaining -= additions
            group |= additions
        groups.append(group)
    mapping.need(len(groups) == 8 and all(len(g) == 4 for g in groups), 'terminal-tip census')
    # Pin labels follow captured numbered footprint/maker staggering, not nearest-hole fitting.
    tips = sorted((centre(list(g)) for g in groups), reverse=True)
    pins = {str(i+1): local(p) for i, p in enumerate(tips)}
    bottom = [p for p in vertices if abs(p[2]-lo[2]) < 1e-7]
    pegs = [local(centre([p[:2] for p in bottom if sign*p[0] > 4])) for sign in (-1, 1)]
    return pins, pegs, dict(sha256=MODEL_SHA, url=MODEL_URL, bytes=path.stat().st_size,
        vertices=len(vertices), uniform_scale=scale, bbox_min=lo, bbox_max=hi,
        observation='Fresh public download; cached browser OBJ byte equality NOT established',
        measurement='Terminal-tip and forked peg-bottom profile bbox centres; nominal CAD only')


def analyze(model_path=None):
    generated = json.loads(mapping.expected()['measurements.json'])
    native = next(r for r in generated['connectors'] if r['board'] == 'pod')
    pins, pegs, transform, header_uuid = footprint()
    rows = {'A': native['before'], 'B': dict(native['before'], Rotation='180'),
            'C': native['candidate']}
    result = dict(status='POD_TEST_C_SUPPORTED_BY_CAPTURED_GEOMETRY', production_ready=False,
        live_C_verified=False, captured_footprint_sha256=CAPTURE_SHA,
        active_model_uuid=MODEL_UUID, unused_header_model_uuid=header_uuid,
        model_transform=transform, footprint_local_native_mm=dict(pins=pins, pegs=pegs), trials={})
    mp = model_features(model_path, transform) if model_path else None
    for label, row in rows.items():
        replay = mapping.replay(pins, pegs, row)
        trial = dict(cpl=row, captured_footprint=mapping.errors(
            native['native_pins'], native['native_pegs'], *replay))
        if mp:
            actual = mapping.replay(mp[0], mp[1], row)
            trial['public_model_features'] = mapping.errors(native['native_pins'], native['native_pegs'], *actual)
            trial['model_feature_positions_native_mm'] = dict(pins=actual[0], pegs=actual[1])
        result['trials'][label] = trial
    if mp:
        result['public_model'] = mp[2]
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path)
    parser.add_argument('--output', type=Path, help='Create a new report, or verify identical existing bytes')
    args = parser.parse_args()
    report = analyze(args.model)
    payload = json.dumps(report, sort_keys=True, indent=2)+'\n'
    if args.output:
        if args.output.exists():
            mapping.need(args.output.read_text() == payload, 'existing report differs')
        else:
            args.output.write_text(payload)
    print(payload)
