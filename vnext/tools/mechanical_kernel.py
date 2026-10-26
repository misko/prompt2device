"""Real-solid operations for mechanical evidence, not engineering acceptance.

World coordinates are right-handed mm, PCB top Z=0. Source/model identities,
population, feature-specific mating policy and independent review belong to the
owning adapters. This module never invents those policies or issues acceptance.
"""
import math
from pathlib import Path

import cadquery as cq


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vector(values):
    require(isinstance(values, (list, tuple)) and len(values) == 3,
            'three finite coordinates required')
    require(all(isinstance(x, (int, float)) and not isinstance(x, bool)
                and math.isfinite(x) for x in values), 'nonfinite coordinate')
    return tuple(float(x) for x in values)


def solid_check(shape):
    require(shape.isValid(), 'invalid B-rep')
    solids = shape.Solids()
    require(solids and all(s.Volume() > 1e-12 for s in solids), 'nonzero solids required')
    # A file with an incidental solid must not smuggle unaccounted free shells,
    # faces or wire-only geometry into a claim about a solid assembly.
    covered = cq.Compound.makeCompound(solids)
    require(len(covered.Faces()) == len(shape.Faces()) and
            len(covered.Edges()) == len(shape.Edges()) and
            len(covered.Vertices()) == len(shape.Vertices()), 'non-solid geometry present')
    return shape


def load_step(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'local regular STEP required')
    require(path.suffix.lower() in {'.step', '.stp'}, 'STEP extension required')
    # CadQuery/OCCT respects STEP-declared units; output is normalized to mm.
    return solid_check(cq.importers.importStep(str(path)).val())


def pose(shape, translation=(0, 0, 0), rotation=(0, 0, 0)):
    """Extrinsic X, then Y, then Z rotations in degrees, then translation.

    No scale or reflection path exists. Bottom-side installation must be an
    explicit proper 3D rotation and translation, not a left-handed 2D mirror.
    """
    translation, rotation = vector(translation), vector(rotation)
    for axis, angle in zip(((1, 0, 0), (0, 1, 0), (0, 0, 1)), rotation):
        shape = shape.rotate((0, 0, 0), axis, angle)
    return shape.translate(translation)


def point_pose(point, translation=(0, 0, 0), rotation=(0, 0, 0)):
    vertex = cq.Vertex.makeVertex(*vector(point))
    return pose(vertex, translation, rotation).Center().toTuple()


def registration(local, expected, translation, rotation, tolerance_mm):
    require(isinstance(tolerance_mm, (int, float)) and not isinstance(tolerance_mm, bool)
            and math.isfinite(tolerance_mm) and tolerance_mm >= 0, 'invalid registration tolerance')
    require(len(local) == len(expected) and len(local) >= 3,
            'at least three paired registration landmarks required')
    local = [vector(x) for x in local]
    expected = [vector(x) for x in expected]
    for points in (local, expected):
        a = cq.Vector(*points[0])
        require(any((cq.Vector(*b)-a).cross(cq.Vector(*c)-a).Length > 1e-9
                    for b in points[1:] for c in points[1:]),
                'degenerate registration landmarks')
    actual = [point_pose(x, translation, rotation) for x in local]
    errors = [math.dist(a, b) for a, b in zip(actual, expected)]
    return {'actual': actual, 'expected': expected, 'errors_mm': errors,
            'tolerance_mm': tolerance_mm,
            'verdict': 'PASS' if max(errors) <= tolerance_mm+1e-9 else 'FAIL'}


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def measure_pair(a, b, clearance_mm=0.0, volume_tolerance_mm3=1e-9):
    for x in (clearance_mm, volume_tolerance_mm3):
        require(isinstance(x, (int, float)) and not isinstance(x, bool)
                and math.isfinite(x) and x >= 0, 'invalid clearance/tolerance')
    solid_check(a); solid_check(b)
    distance = a.distance(b)
    intersection = a.intersect(b)
    overlap = sum(s.Volume() for s in intersection.Solids())
    return {'distance_mm': distance, 'intersection_mm3': overlap,
            'required_clearance_mm': clearance_mm,
            'verdict': 'FAIL' if overlap > volume_tolerance_mm3 or
                       distance+1e-9 < clearance_mm else 'PASS'}


def compare_solids(a, b, length_tolerance_mm=1e-6, volume_tolerance_mm3=1e-6):
    """Geometry comparison, not a text checksum or volume-only proxy."""
    for value in (length_tolerance_mm, volume_tolerance_mm3):
        require(isinstance(value, (int, float)) and not isinstance(value, bool)
                and math.isfinite(value) and value >= 0, 'invalid comparison tolerance')
    solid_check(a); solid_check(b)
    bound_error = max(abs(x-y) for x, y in zip(bounds(a), bounds(b)))
    # Two equal-volume, equal-bounds solids can have entirely different holes.
    removed = sum(s.Volume() for s in a.cut(b).Solids())
    added = sum(s.Volume() for s in b.cut(a).Solids())
    return {'solids_before': len(a.Solids()), 'solids_after': len(b.Solids()),
            'bounds_error_mm': bound_error, 'removed_mm3': removed, 'added_mm3': added,
            'verdict': 'PASS' if len(a.Solids()) == len(b.Solids()) and
                       bound_error <= length_tolerance_mm and
                       max(removed, added) <= volume_tolerance_mm3 else 'FAIL'}


def export_step(parts, target):
    """Named, unfused solid assembly; reopen the exported bytes before returning."""
    require(parts and all(isinstance(n, str) and n.strip() for n in parts),
            'nonempty named population required')
    target = Path(target)
    require(not target.exists() and not target.is_symlink(), 'refusing existing STEP')
    assembly = cq.Assembly(name='verified_scene')
    for name, shape in sorted(parts.items()):
        assembly.add(solid_check(shape), name=name)
    assembly.export(str(target), exportType='STEP', mode='default')
    return check_step(parts, target)


def check_step(parts, target):
    """Compare saved STEP against the supplied scene, including named members."""
    require(parts, 'nonempty named population required')
    expected = cq.Compound.makeCompound(list(parts.values()))
    observed = load_step(target)
    result = compare_solids(expected, observed)
    require(result['verdict'] == 'PASS', 'STEP round-trip geometry differs')
    reopened = cq.Assembly.load(str(target))
    observed_parts = {}
    for shape, name, location, color in reopened:
        leaf = name.removeprefix(reopened.name+'/')
        require(leaf not in observed_parts, 'duplicate exported part name')
        observed_parts[leaf] = shape.moved(location)
    require(set(observed_parts) == set(parts), 'STEP named population differs')
    result['parts'] = {name: compare_solids(shape, observed_parts[name]) for name, shape in parts.items()}
    require(all(row['verdict'] == 'PASS' for row in result['parts'].values()),
            'STEP per-reference geometry differs')
    return result


def camera_frame(box, direction, up, width, height):
    """Same frame supplied to populated and bare render; never auto-fit each."""
    require(len(box) == 6 and all(math.isfinite(x) for x in box), 'finite scene bounds required')
    require(all(box[i] < box[i+3] for i in range(3)), 'nonempty scene bounds required')
    require(isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0,
            'positive image dimensions required')
    d, u = cq.Vector(*vector(direction)), cq.Vector(*vector(up))
    require(d.Length > 0 and u.Length > 0 and d.cross(u).Length > 1e-9,
            'degenerate camera basis')
    d = d.normalized(); right = u.cross(d).normalized(); u = d.cross(right).normalized()
    center = tuple((box[i]+box[i+3])/2 for i in range(3))
    corners = [cq.Vector(x-center[0], y-center[1], z-center[2])
               for x in (box[0], box[3]) for y in (box[1], box[4]) for z in (box[2], box[5])]
    vertical = max(abs(v.dot(u)) for v in corners)
    horizontal = max(abs(v.dot(right)) for v in corners)
    radius = max(v.Length for v in corners)
    return {'projection': 'orthographic', 'width': width, 'height': height,
            'focal_point': center, 'position': (cq.Vector(*center)+d*(radius*4+1)).toTuple(),
            'up': u.toTuple(), 'parallel_scale': max(vertical, horizontal*height/width)*1.1,
            'clip': [0.01, radius*8+10]}


def render_png(parts, target, frame, label=None):
    """Tessellated solid visualization; no fit verdict is inferred from pixels."""
    import vtk
    target = Path(target)
    require(parts and not target.exists() and not target.is_symlink(), 'new populated render target required')
    require(frame['projection'] == 'orthographic', 'unsupported projection')
    renderer = vtk.vtkRenderer(); renderer.SetBackground(1, 1, 1)
    if label is not None:
        require(isinstance(label, str) and label.strip(), 'nonempty render label required')
        title = vtk.vtkTextActor(); title.SetInput(label); title.SetPosition(16, 16)
        title.GetTextProperty().SetFontSize(16); title.GetTextProperty().SetColor(.1, .1, .1)
    window = vtk.vtkRenderWindow(); window.SetOffScreenRendering(1)
    window.SetMultiSamples(0); window.SetSize(frame['width'], frame['height']); window.AddRenderer(renderer)
    for name, shape in sorted(parts.items()):
        solid_check(shape)
        vertices, triangles = shape.tessellate(0.03, 0.1)
        points = vtk.vtkPoints()
        for v in vertices: points.InsertNextPoint(v.x, v.y, v.z)
        cells = vtk.vtkCellArray()
        for tri in triangles:
            cells.InsertNextCell(3)
            for i in tri: cells.InsertCellPoint(i)
        mesh = vtk.vtkPolyData(); mesh.SetPoints(points); mesh.SetPolys(cells)
        mapper = vtk.vtkPolyDataMapper(); mapper.SetInputData(mesh)
        actor = vtk.vtkActor(); actor.SetMapper(mapper)
        actor.GetProperty().SetColor((0.12, 0.38, 0.24) if name == 'board' else (0.56, 0.60, 0.66))
        renderer.AddActor(actor)
    camera = renderer.GetActiveCamera(); camera.ParallelProjectionOn()
    camera.SetPosition(*frame['position']); camera.SetFocalPoint(*frame['focal_point'])
    camera.SetViewUp(*frame['up']); camera.SetParallelScale(frame['parallel_scale'])
    camera.SetClippingRange(*frame['clip'])
    window.Render()
    capture = vtk.vtkWindowToImageFilter(); capture.SetInput(window)
    capture.SetInputBufferTypeToRGB(); capture.ReadFrontBufferOff(); capture.Update()
    # A text label must not make an otherwise empty camera look like geometry.
    require(capture.GetOutput().GetPointData().GetScalars().GetRange()[0] < 255,
            'blank geometry camera')
    if label is not None:
        renderer.AddActor2D(title); window.Render(); capture.Modified(); capture.Update()
    writer = vtk.vtkPNGWriter(); writer.SetFileName(str(target)); writer.SetInputConnection(capture.GetOutputPort())
    writer.Write(); window.Finalize()
    require(target.is_file() and target.stat().st_size > 0, 'missing rendered image')
    from PIL import Image
    with Image.open(target) as pixels:
        require(pixels.size == (frame['width'], frame['height']) and
                any(low != high for low, high in pixels.convert('RGB').getextrema()),
                'blank or incorrectly sized rendered image')
