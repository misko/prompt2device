"""Source-bound solid scene and artifacts; never a mating/assembly receipt.

Reuses the assembly manifest and staged population. Drawing-derived envelopes
remain explicitly envelopes; an optional retained STEP replaces one model, not
the population or its contact checks. All checks and exports use the same solids.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.dont_write_bytecode = True
import assembly_verify as assembly
import mechanical_kernel as k

p = assembly.p
cq = k.cq
VIEWS = {'top': ([0, 0, 1], [0, 1, 0]),
         'bottom': ([0, 0, -1], [0, 1, 0]),
         'iso_nw': ([-1, 1, 1.2], [0, 0, 1]),
         'iso_se': ([1, -1, 1.2], [0, 0, 1]),
         'edge_west': ([-1, 0, 0], [0, 0, 1]),
         'edge_east': ([1, 0, 0], [0, 0, 1])}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+'\n')


def envelope(body):
    """Assembly-local (+Y down) declaration to right-handed solid coordinates."""
    low, high = body['z']
    if body['shape'] == 'box':
        left, top, right, bottom = body['bounds']
        return k.solid_check(cq.Solid.makeBox(right-left, bottom-top, high-low,
                                            cq.Vector(left, -bottom, low)))
    x, y = body['center']
    return k.solid_check(cq.Solid.makeCylinder(body['radius'], high-low,
                                             cq.Vector(x, -y, low)))


def noncoplanar(points):
    """A fourth out-of-plane witness prevents planar-only height ambiguity."""
    points = [cq.Vector(*k.vector(point)) for point in points]
    k.require(len(points) >= 4, 'four noncoplanar registration landmarks required')
    vectors = [q-points[0] for q in points[1:]]
    k.require(any(abs(a.dot(b.cross(c))) > 1e-8
                  for a in vectors for b in vectors for c in vectors),
              'coplanar 3D registration landmarks')


def step_model(project, row, subjects):
    k.require(set(row) == {'path', 'translation', 'rotation', 'local_landmarks',
                          'landmark_features', 'expected_landmarks', 'tolerance_mm', 'evidence', 'limitations'},
              'unsupported STEP registration declaration')
    path = assembly.local(project, row['path'])
    assembly.evidence(project, [row['path'], *row['evidence']], subjects)
    k.require(row['evidence'], 'independent registration evidence required')
    k.require(any(assembly.local(project, n) != path and sha(assembly.local(project, n)) != sha(path)
                  for n in row['evidence']), 'registration evidence cannot be only the STEP itself')
    k.require(isinstance(row['limitations'], list) and
              all(isinstance(x, str) and x.strip() for x in row['limitations']),
              'explicit STEP limitations list required')
    noncoplanar(row['local_landmarks']); noncoplanar(row['expected_landmarks'])
    raw = k.load_step(path)
    features = bind_features(raw, row['local_landmarks'], row['landmark_features'])
    registration = k.registration(row['local_landmarks'], row['expected_landmarks'],
                                  row['translation'], row['rotation'], row['tolerance_mm'])
    k.require(registration['verdict'] == 'PASS', 'STEP registration failed')
    shape = k.pose(raw, row['translation'], row['rotation'])
    return shape, dict(representation='retained_step', source=row['path'],
                       registration=registration, feature_binding=features, limitations=row['limitations'])


def bind_features(shape, points, features):
    """Locate witnesses on actual B-rep geometry, not caller coordinate arithmetic.

    10 nm is CAD correspondence tolerance, not manufacturing/registration slack.
    Circle centers can lie in holes, so require a matching circular edge radius.
    Surface witnesses measure to faces, not to solid interiors.
    """
    k.require(isinstance(features, list) and len(features) == len(points), 'landmark feature coverage differs')
    result = []
    for point, feature in zip(points, features):
        point = k.vector(point)
        k.require(isinstance(feature, dict), 'landmark feature declaration required')
        if feature == {'kind': 'surface'}:
            vertex = cq.Vertex.makeVertex(*point)
            error = min(face.distance(vertex) for face in shape.Faces())
        else:
            k.require(set(feature) == {'kind', 'radius_mm'} and feature['kind'] == 'circle_center',
                      'unsupported landmark feature')
            radius = feature['radius_mm']
            k.require(isinstance(radius, (int, float)) and not isinstance(radius, bool)
                      and math.isfinite(radius) and radius > 0, 'positive feature radius required')
            edges = [edge for edge in shape.Edges() if edge.geomType() == 'CIRCLE'
                     and abs(edge.radius()-radius) <= 1e-5]
            error = min((math.dist(edge.arcCenter().toTuple(), point) for edge in edges), default=math.inf)
        k.require(error <= 1e-5, 'registration landmark is not on declared STEP feature')
        result.append(dict(point=point, feature=feature, error_mm=error, cad_tolerance_mm=1e-5))
    return result


def box_distance(a, b):
    return math.sqrt(sum(max(0, a[i]-b[i+3], b[i]-a[i+3])**2 for i in range(3)))


def pair_checks(parts, minimum_clearance=0):
    """Every unordered pair counted; separated AABBs give a lower bound only.

    Overlapping/touching boxes always enter the solid kernel. A hollow connector
    may therefore pass despite overlapping bounds; a solid collision cannot.
    No whole-component pair is exempted. Intentional surface contact is zero
    volume, not permission for solid interpenetration.
    """
    k.require(math.isfinite(minimum_clearance) and minimum_clearance >= 0,
              'invalid scene clearance')
    names = sorted(parts); boxes = {n: k.bounds(s) for n, s in parts.items()}
    detailed = []; excluded = 0
    for i, name in enumerate(names):
        for other in names[i+1:]:
            lower = box_distance(boxes[name], boxes[other])
            if lower > minimum_clearance+1e-7:
                excluded += 1
                continue
            detailed.append(dict(a=name, b=other,
                                 **k.measure_pair(parts[name], parts[other], minimum_clearance)))
    failures = [r for r in detailed if r['verdict'] != 'PASS']
    return dict(total_pairs=len(names)*(len(names)-1)//2,
                separated_by_bounds_lower_limit=excluded, kernel_pairs=detailed,
                failures=failures, verdict='FAIL' if failures else 'PASS',
                scope='nominal body clearance only; not tolerance, engagement or solder-seat acceptance')


def access_checks(parts, declared):
    result = []
    for row in declared:
        access = envelope(dict(shape='box', bounds=row['bounds'], z=row['z']))
        measurements = []
        for ref, solid in parts.items():
            if box_distance(k.bounds(access), k.bounds(solid)) > 1e-7: continue
            measurements.append(dict(reference=ref, **k.measure_pair(access, solid)))
        result.append(dict(id=row['id'], owner=row['ref'], measurements=measurements,
                           verdict='FAIL' if any(m['verdict'] != 'PASS' for m in measurements) else 'PASS'))
    return result


def assemble_parts(bare, mounted):
    k.require(mounted and 'board' not in mounted, 'empty population or reserved board reference')
    return {'board': bare, **mounted}


def native_board(native, target):
    # KiCad STEP export can create editor preference files alongside its input.
    # Always copy the complete local native resources before invoking it.
    with tempfile.TemporaryDirectory(prefix='vnext-scene-native-') as tmp:
        isolated = Path(tmp)/'native'; shutil.copytree(native.parent, isolated)
        copied = isolated/native.name
        command = ['kicad-cli', 'pcb', 'export', 'step', '--no-components',
                   '--user-origin', '0x0mm', '--output', str(target), str(copied)]
        p.command(command)
        command[-1] = str(native)  # Logical source identity; physical copy is disposable.
    raw = k.load_step(target); bounds = k.bounds(raw)
    board = p.pcb.LoadBoard(str(native))
    declared = board.GetDesignSettings().GetBoardThickness()/1e6
    # Preserve exact native outline/drill/cutout section, but do NOT silently
    # equate KiCad's dielectric STEP height with nominal finished board thickness.
    finished = finished_board_envelope(raw, declared)
    result = dict(command=command, declared_thickness_mm=declared,
                  execution='logical command shown; source/resources copied to disposable directory before export',
                  exported_body_thickness_mm=bounds[5]-bounds[2],
                  representation='nominal finished-board envelope extruded from native top section',
                  frame='right-handed mm; nominal finished top Z=0; native X, negative native Y',
                  limitation='Board section preserves native outline and holes; thickness is nominal '
                             'finished thickness, not measured laminate. Local copper/mask/finish relief '
                             'and manufacturing tolerances are not represented.')
    # Stable logged command uses artifact-relative output, not a deleted temp path.
    result['command'] = [target.name if word == str(target) else word for word in command]
    return finished, result


def finished_board_envelope(raw, thickness):
    k.require(isinstance(thickness, (int, float)) and not isinstance(thickness, bool)
              and math.isfinite(thickness) and thickness > 0, 'positive finished board thickness required')
    box = k.bounds(raw); top = box[5]
    faces = [face for face in raw.Faces()
             if face.geomType() == 'PLANE' and abs(face.normalAt().z) > .999999
             and abs(face.BoundingBox().zmin-top) < 1e-6
             and abs(face.BoundingBox().zmax-top) < 1e-6]
    k.require(faces, 'native board top section missing')
    solids = [cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), cq.Vector(0, 0, -thickness))
              .translate((0, 0, -top)) for face in faces]
    result = k.solid_check(cq.Compound.makeCompound(solids))
    got = k.bounds(result)
    k.require(all(abs(got[i]-box[i]) < 1e-6 for i in (0, 1, 3, 4))
              and abs(got[2]+thickness) < 1e-6 and abs(got[5]) < 1e-6,
              'finished-board envelope bounds differ')
    k.require(abs(result.Volume()-sum(face.Area() for face in faces)*thickness) < 1e-5,
              'finished-board section extrusion differs')
    return result


def inputs(project, name):
    spec = p.read(assembly.local(project, name))
    k.require(set(spec) == {'version', 'assembly_manifest', 'step_models', 'unresolved'}
              and spec['version'] == 1, 'unsupported scene manifest')
    k.require(isinstance(spec['step_models'], dict), 'STEP model mapping required')
    k.require(isinstance(spec['unresolved'], list) and
              all(isinstance(x, str) and x.strip() for x in spec['unresolved']),
              'explicit unresolved claims required')
    source = p.read(assembly.local(project, spec['assembly_manifest']))
    _, geometry, subjects = assembly.payload(project, spec['assembly_manifest'], source['package'], {})
    assembly.evidence(project, [name], subjects)
    package = assembly.local(project, source['package'], False)
    assembly.evidence(project, [source['package']+'/native/bundle.json',
                               source['package']+'/assembly/population.csv',
                               source['package']+'/fabrication.json'], subjects)
    bundle = p.read(package/'native/bundle.json')
    k.require(set(spec['step_models']) <= set(source['models']), 'unknown STEP model key')
    models = {}; model_reports = {}
    for key, model in source['models'].items():
        if key in spec['step_models']:
            models[key], model_reports[key] = step_model(project, spec['step_models'][key], subjects)
        else:
            models[key] = cq.Compound.makeCompound([envelope(b) for b in model['bodies']])
            model_reports[key] = dict(representation='drawing_envelope', basis=model['basis'],
                                      evidence=model['evidence'],
                                      limitations=['No implied lead geometry, cavity or engagement proof.'])
    boards = {}
    for key, data in geometry['boards'].items():
        k.require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', key), 'unsafe scene board name')
        native = assembly.local(package/'native', bundle['boards'][key]['native'])
        subjects[native.relative_to(project).as_posix()] = sha(native)
        # Export behavior also depends on local settings and footprint resources.
        for path in native.parent.rglob('*'):
            k.require(not path.is_symlink(), 'linked native resource')
            if path.is_file(): subjects[path.relative_to(project).as_posix()] = sha(path)
        parts = {}
        for ref, row in data['references'].items():
            k.require(re.fullmatch(r'[A-Za-z0-9_.+-]+', ref), 'unsafe scene reference name')
            x, y, angle = row['position']
            parts[ref] = k.pose(models[row['model']], [x, -y, 0], [0, 0, angle])
        boards[key] = dict(native=native, parts=parts, geometry=data)
    return spec, subjects, model_reports, boards


def build(project, name, output):
    project = Path(project).resolve(); output = Path(output).absolute()
    k.require(not output.exists() and not output.is_symlink(), 'refusing existing scene output')
    spec, subjects, model_reports, boards = inputs(project, name)
    tools = {n: sha(Path(__file__).parent/n) for n in
             (*assembly.fab.TOOLS, 'assembly_verify.py', 'mechanical_scene.py', 'mechanical_kernel.py')}
    # A failed build remains diagnostic; atomic publication prevents partial
    # images from looking like a completed artifact set.
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.mechanical-scene-', dir=output.parent) as temp:
        stage = Path(temp)/'scene'; stage.mkdir(); reports = {}
        for key, board in sorted(boards.items()):
            dest = stage/key; dest.mkdir()
            bare, datum = native_board(board['native'], dest/'native-dielectric.step')
            datum['command'] = [board['native'].relative_to(project).as_posix()
                                if word == str(board['native']) else word for word in datum['command']]
            datum['bare_step_roundtrip'] = k.export_step({'board': bare}, dest/'board.step')
            parts = assemble_parts(bare, board['parts'])
            checks = pair_checks(parts)
            accesses = access_checks(parts, board['geometry']['access'])
            roundtrip = k.export_step(parts, dest/(key+'-populated.step'))
            world = k.bounds(cq.Compound.makeCompound(list(parts.values())))
            frames = {}
            for view, (direction, up) in VIEWS.items():
                frame = k.camera_frame(world, direction, up, 1200, 800); frames[view] = frame
                k.render_png(parts, dest/('twin_'+view+'.png'), frame,
                             key+' | '+view+' | 3D DIAGNOSTIC - NOT ACCEPTED')
                if view in ('top', 'bottom'):
                    k.render_png({'board': bare}, dest/('render_'+view+'_bare.png'), frame,
                                 key+' | '+view+' | BARE - SAME CAMERA')
            details = {}
            for ref, row in board['geometry']['references'].items():
                if row['model'] not in spec['step_models']: continue
                box = k.bounds(parts[ref])
                close_box = [v-1 if i < 3 else v+1 for i, v in enumerate(box)]
                close_box[2] = min(close_box[2], -datum['declared_thickness_mm']-1)
                for view in ('iso_nw', 'edge_west', 'edge_east'):
                    direction, up = VIEWS[view]
                    frame = k.camera_frame(close_box, direction, up, 1200, 800)
                    filename = 'detail_'+ref+'_'+view+'.png'
                    k.render_png({'board': bare, ref: parts[ref]}, dest/filename, frame,
                                 key+' '+ref+' | '+view+' | ISOLATED DETAIL - NEIGHBORS HIDDEN')
                    details[filename] = dict(reference=ref, frame=frame,
                                             visible_references=['board', ref], neighbors_hidden=True)
            reports[key] = dict(mounted_references=len(parts)-1,
                                references=board['geometry']['references'],
                                contact_failures=board['geometry']['failures'],
                                board_datum=datum, clearance=checks,
                                access=accesses,
                                step_roundtrip=roundtrip, frames=frames, details=details)
        # Reopen inputs after expensive geometry work: concurrent changes cannot
        # quietly bind old geometry to new input hashes.
        k.require(all(sha(assembly.local(project, n)) == digest for n, digest in subjects.items()),
                  'scene inputs changed during build')
        k.require(all(sha(Path(__file__).parent/n) == digest for n, digest in tools.items()),
                  'scene tools changed during build')
        failures = any(b['contact_failures'] or b['clearance']['failures'] or
                       any(a['verdict'] != 'PASS' for a in b['access']) for b in reports.values())
        report = dict(version=1, manifest=name, accepted=False,
                      status='FAIL' if failures else 'INCOMPLETE',
                      scope='source-bound 3D diagnostic; owning admission and independent review still required',
                      inputs=subjects, models=model_reports, boards=reports,
                      unresolved=spec['unresolved'],
                      tools=tools,
                      files={f.relative_to(stage).as_posix(): sha(f) for f in stage.rglob('*') if f.is_file()})
        write_json(stage/'scene.json', report); stage.rename(output)
    return report


def verify(project, name, output):
    """Reproduce source-bound scene, inspect STEP solids and compare image pixels.

    STEP writer timestamps are not geometry. Saved artifact hashes must match,
    then reopened geometry must match fresh production from unchanged inputs.
    Successful replay still returns accepted=False and the diagnostic status.
    """
    from PIL import Image, ImageChops
    project = Path(project).resolve(); output = Path(output).absolute()
    k.require(output.is_dir() and not output.is_symlink(), 'scene output directory required')
    for path in output.rglob('*'): k.require(not path.is_symlink(), 'linked scene artifact')
    old = p.read(output/'scene.json')
    observed = {f.relative_to(output).as_posix(): sha(f) for f in output.rglob('*')
                if f.is_file() and f != output/'scene.json'}
    k.require(observed == old.get('files'), 'scene artifact inventory/hash differs')
    k.require(old.get('manifest') == name and old.get('accepted') is False, 'scene declaration differs')
    # Reject stale source/tool evidence before invoking any expensive producer.
    for n, digest in old['inputs'].items():
        k.require(sha(assembly.local(project, n)) == digest, 'stale scene input: '+n)
    for n, digest in old['tools'].items():
        k.require(Path(n).name == n and sha(Path(__file__).parent/n) == digest, 'stale scene tool: '+n)
    with tempfile.TemporaryDirectory(prefix='vnext-scene-replay-') as tmp:
        fresh_dir = Path(tmp)/'scene'
        build(project, name, fresh_dir)
        # Compare durable JSON to durable JSON (tuples serialize as lists).
        fresh = p.read(fresh_dir/'scene.json')
        k.require({n: v for n, v in old.items() if n != 'files'} ==
                  {n: v for n, v in fresh.items() if n != 'files'}, 'scene evidence replay differs')
        k.require(set(old['files']) == set(fresh['files']), 'scene role census differs')
        for name in fresh['files']:
            a, b = output/name, fresh_dir/name
            if a.suffix == '.png':
                with Image.open(a) as stored, Image.open(b) as replayed:
                    k.require(stored.size == replayed.size and
                              ImageChops.difference(stored.convert('RGB'), replayed.convert('RGB')).getbbox() is None,
                              'scene render pixels differ: '+name)
            elif a.name == 'native-dielectric.step':
                k.require(k.compare_solids(k.load_step(a), k.load_step(b))['verdict'] == 'PASS',
                          'native STEP replay differs: '+name)
            else:
                loaded = cq.Assembly.load(str(b)); parts = {}
                for shape, member, location, color in loaded:
                    leaf = member.removeprefix(loaded.name+'/')
                    k.require(leaf not in parts, 'duplicate replay member')
                    parts[leaf] = shape.moved(location)
                k.check_step(parts, a)
    return dict(status=old['status'], accepted=False, replayed_boards=sorted(old['boards']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify'])
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.action == 'verify':
        print(json.dumps(verify(args.project, args.manifest, args.output), indent=2)); return
    report = build(args.project, args.manifest, args.output)
    print(json.dumps(dict(status=report['status'], accepted=False,
                         boards={key: dict(mounted=row['mounted_references'],
                                           failed_pairs=len(row['clearance']['failures']))
                                 for key, row in report['boards'].items()}), indent=2))


if __name__ == '__main__':
    main()
