#!/usr/bin/env python3
"""Grade configured short paths and protection branch order on saved copper.

Usage: critical_path_check.py BOARD --config critical_paths.yaml --json REPORT
Promoted from the pod checker when a second board needed the same mechanism.
Nonempty schema-1 source fixes copper layers, stackup, endpoint paths and
clamp-dominance obligations. Zones, arcs and unsplit/width-only copper contacts
and unrepresented pad contacts on graded nets are refused rather than silently
omitted from the graph. Rounded-pad anchor ambiguity is conservatively refused.
This is not an ESD waveform or physical protection qualification.

VACUITY: Correctly declared copper paths cannot establish that a fitted clamp
actually limits voltage. A failed-open device with identical copper passes;
physical component and transient qualification remain separate.

Grade safety- and stability-critical realized copper.

Placement distance is not route distance. This checker reopens the exact saved
KiCad board, builds a layer-aware copper graph, and proves that the regulator
capacitors and exposed-line clamps are reached by their exact short, via-free
layer-specific paths.
It also proves downstream branches include the complete connector-to-clamp
prefix and that every physical prefix edge dominates each downstream target,
so a longer parallel pre-clamp bypass cannot be hidden by shortest-path choice.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


class AuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class PathResult:
    start: str
    end: str
    net: str
    length_mm: float
    physical_edges: frozenset[int]
    via_count: int
    layers: frozenset[str]
    pad_centre_mm: float = 0.0


def validate_config(data):
    import re
    if not isinstance(data, dict) or set(data) != {"schema", "layers", "stackup_mm", "short_paths", "prefixes"} or type(data["schema"]) is not int or data["schema"] != 1:
        raise AuditError("invalid critical-path schema/header")
    layers = data["layers"]
    if not isinstance(layers, list) or len(layers) < 2 or len(set(layers)) != len(layers) or layers[0] != "F.Cu" or layers[-1] != "B.Cu" or any(not isinstance(x, str) or not re.fullmatch(r"(?:F|B|In[1-9][0-9]*)\.Cu", x) for x in layers):
        raise AuditError("invalid declared copper layers")
    def positive(x):
        return type(x) in (int, float) and math.isfinite(x) and x > 0
    if not isinstance(data["stackup_mm"], list) or len(data["stackup_mm"]) != len(layers)-1 or not all(positive(x) for x in data["stackup_mm"]):
        raise AuditError("invalid declared layer spacing")
    def endpoint(x):
        return isinstance(x, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*\.[A-Za-z0-9_]+", x)
    short = data["short_paths"]
    if not isinstance(short, list) or not short:
        raise AuditError("short-path denominator is empty")
    pairs = set()
    for row in short:
        if not isinstance(row, dict) or set(row) != {"from", "to", "max_length_mm", "layer", "max_pad_centre_mm", "why"}:
            raise AuditError("invalid short-path keys")
        pair = (row["from"], row["to"])
        if not all(endpoint(x) for x in pair) or pair[0] == pair[1] or pair in pairs:
            raise AuditError("invalid/duplicate short-path endpoints")
        pairs.add(pair)
        if row["layer"] not in layers or not positive(row["max_length_mm"]) or (row["max_pad_centre_mm"] is not None and not positive(row["max_pad_centre_mm"])) or not isinstance(row["why"], str) or not row["why"].strip():
            raise AuditError("invalid short-path limit/layer/reason")
    if not isinstance(data["prefixes"], list):
        raise AuditError("prefixes must be a list")
    seen = set()
    for row in data["prefixes"]:
        if not isinstance(row, dict) or set(row) != {"from", "through", "targets", "why"}:
            raise AuditError("invalid prefix keys")
        pair = (row["from"], row["through"])
        targets = row["targets"]
        if pair not in pairs or pair in seen or not isinstance(targets, list) or not targets or not all(endpoint(x) for x in targets) or len(set(targets)) != len(targets) or any(x in pair for x in targets) or not isinstance(row["why"], str) or not row["why"].strip():
            raise AuditError("invalid/duplicate prefix or targets")
        seen.add(pair)
    return data


def load_config(path):
    import yaml
    class UniqueLoader(yaml.SafeLoader):
        pass
    def mapping(loader, node, deep=False):
        result = {}
        for key, value in node.value:
            key = loader.construct_object(key, deep=deep)
            if key in result:
                raise AuditError("duplicate critical-path YAML key")
            result[key] = loader.construct_object(value, deep=deep)
        return result
    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    try:
        return validate_config(yaml.load(Path(path).read_text(), Loader=UniqueLoader))
    except (yaml.YAMLError, TypeError) as exc:
        raise AuditError(str(exc)) from exc


def point_segment_distance(p, a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    norm = dx*dx+dy*dy
    if norm == 0:
        return math.dist(p,a)
    t = max(0., min(1., ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/norm))
    return math.dist(p,(a[0]+t*dx,a[1]+t*dy))


def segment_distance(a,b,c,d):
    def cross(p,q,r):
        return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    ab_c,ab_d,cd_a,cd_b = cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
    if ab_c*ab_d < 0 and cd_a*cd_b < 0:
        return 0.
    return min(point_segment_distance(a,c,d),point_segment_distance(b,c,d),
               point_segment_distance(c,a,b),point_segment_distance(d,a,b))


def pad_local(pad, point):
    angle = math.radians(pad['angle'])
    dx,dy = point[0]-pad['x'], point[1]-pad['y']
    return (dx*math.cos(angle)-dy*math.sin(angle),
            dx*math.sin(angle)+dy*math.cos(angle))


def pad_box_distance(pad, a, b):
    """Conservative contact screen against a rotated pad bounding rectangle.

    A near miss at a rounded corner may be refused. It can never be accepted
    as copper merely because the rectangle reaches farther than the land.
    """
    a,b = pad_local(pad,a),pad_local(pad,b)
    hx,hy = pad['sx']/2,pad['sy']/2
    if any(abs(x)<=hx and abs(y)<=hy for x,y in (a,b)):
        return 0.
    vertices=[(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]
    return min(segment_distance(a,b,c,d) for c,d in zip(vertices,vertices[1:]+vertices[:1]))


def verified_pad_hit(pad, point, copper):
    """Guarantee every graph anchor is within actual supported land geometry.

    The shared length reader's 2 um tolerance/roundrect rectangle is broader
    than this protection proof permits. Refuse ambiguous anchors; an inscribed
    ellipse is a conservative subset of a roundrect without guessing its radius.
    """
    graph_hit = copper._point_in_pad(pad,*point)
    if graph_hit:
        x,y = pad_local(pad,point);hx,hy=pad['sx']/2,pad['sy']/2
        if pad['shape'] in ('circle','oval','roundrect'):
            proven = (x/hx)**2+(y/hy)**2 <= 1.+1e-12
        else:
            proven = abs(x)<=hx+1e-12 and abs(y)<=hy+1e-12
        if not proven:
            raise AuditError(f"{pad['ref']}.{pad['pad']}: ambiguous pad boundary/rounded-corner graph anchor")
    return graph_hit


def expression_tags(text):
    """Read S-expression tags without mistaking quoted pin/net text for syntax."""
    import re
    quoted = escaped = False
    tags = set()
    for i, char in enumerate(text):
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == '(':
            match = re.match(r'([^\s()]+)', text[i+1:])
            if match:
                tags.add(match[1])
    return tags


def syntax_blocks(text):
    """Quote-aware, indentation-independent census of serialized objects."""
    import re
    head = re.compile(r'([^\s()]+)')
    stack = []
    quoted = escaped = False
    for i,char in enumerate(text):
        if quoted:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '"':
                quoted = False
        elif char == '"':
            quoted = True
        elif char == '(':
            match = head.match(text,i+1)
            if not match:
                raise AuditError('unsupported serialized object head')
            stack.append((match[1],i))
        elif char == ')':
            if not stack:
                raise AuditError('unbalanced serialized copper')
            tag,start=stack.pop()
            yield tag,text[start:i+1]
    if stack or quoted:
        raise AuditError('unclosed serialized copper')


def assert_graph_contacts(text, net, entry, pads, copper):
    """Refuse physical contacts the endpoint graph cannot represent faithfully."""
    import re
    # A native file can also carry copper in graphic primitives. Those have no
    # edge representation here, even when KiCad assigns an explicit net.
    # Refuse copper graphics anywhere; ordinary silk/fab/courtyard is allowed.
    census = {}
    for tag,body in syntax_blocks(text):
        census[tag] = census.get(tag,0)+1
        if tag.startswith(('gr_','fp_')):
            layer = re.search(r'\(layer\s+"([^"]+)"',body)
            if layer and layer[1].endswith('.Cu'):
                raise AuditError(f'{net}: unsupported copper graphics {tag}')
    for tag in ('footprint','segment','via','arc','zone'):
        if census.get(tag,0) != len(list(copper._blocks(text,tag))):
            raise AuditError(f'{net}: unsupported serialization hides {tag} from graph reader')
    footprints=list(copper._blocks(text,'footprint'))
    if census.get('pad',0) != sum(len(list(copper._subblocks(fp,'pad'))) for fp in footprints):
        raise AuditError(f'{net}: unsupported serialization hides pad from graph reader')
    if entry["zones"]:
        raise AuditError(f"{net}: zone copper is not represented by path graph")
    if any(copper._net(b) == net for b in copper._blocks(text, "arc")):
        raise AuditError(f"{net}: arc contacts require a supported graph adapter")
    # KiCad serializes chamfered lands as `roundrect` plus modifiers, and
    # copper offsets under `drill`, including on SMD pads. Shape name alone is
    # not a closed geometry schema. Refuse all unrepresented syntax instead
    # of allowing new pad features to silently invent connectivity.
    supported_pad_tags = {'pad','at','size','drill','layers','net','pinfunction',
        'pintype','uuid','tstamp','roundrect_rratio','solder_mask_margin',
        'solder_paste_margin','solder_paste_margin_ratio','clearance',
        'zone_connect','thermal_bridge_width','thermal_gap',
        'thermal_bridge_angle','property','locked','die_length','remove_unused_layers'}
    for footprint in copper._blocks(text, 'footprint'):
        for body in copper._subblocks(footprint, 'pad'):
            if copper._net(body) == net:
                unsupported = expression_tags(body) - supported_pad_tags
                if unsupported:
                    raise AuditError(f"{net}: unsupported pad geometry syntax {sorted(unsupported)}")
                if 'remove_unused_layers' in expression_tags(body) and not re.search(r'\(remove_unused_layers\s+no\)',body):
                    raise AuditError(f"{net}: unsupported pad geometry: layer removal")
    seen_pads = set()
    for pad in pads:
        ident = (pad['ref'],pad['pad'])
        if ident in seen_pads or pad['shape'] not in {'rect','roundrect','circle','oval'}:
            raise AuditError(f"{net}: duplicate or unsupported pad {ident}")
        if not all(math.isfinite(pad[k]) and pad[k]>0 for k in ('sx','sy')):
            raise AuditError(f"{net}: invalid pad dimensions")
        seen_pads.add(ident)
    segs = []
    quantized = {}
    def admit_node(layer,point,width):
        if point is None or not all(math.isfinite(x) for x in point):
            raise AuditError(f'{net}: invalid physical node')
        key=copper._path_node(point,layer)
        for other,other_width in quantized.get(key,[]):
            if math.dist(point,other) > (width+other_width)/2+1e-12:
                raise AuditError(f'{net}: quantization merges disconnected copper endpoints')
        quantized.setdefault(key,[]).append((point,width))
        rounded=copper._path_xy(key)
        for pad in pads:
            if copper._pad_has_layer(pad,layer):
                raw_hit=verified_pad_hit(pad,point,copper)
                rounded_hit=verified_pad_hit(pad,rounded,copper)
                if raw_hit != rounded_hit:
                    raise AuditError(f'{net}: quantization changes pad-anchor membership')
    for body in copper._blocks(text, "segment"):
        if copper._net(body) != net:
            continue
        width = re.search(r'\(width\s+([-\d.eE+]+)\)', body)
        if not width or not math.isfinite(float(width[1])) or float(width[1]) <= 0:
            raise AuditError(f"{net}: invalid track width")
        layer = re.search(r'\(layer\s+"([^"]+)"', body)[1]
        a, b = copper._pt(body, "start"), copper._pt(body, "end")
        admit_node(layer,a,float(width[1]));admit_node(layer,b,float(width[1]))
        segs.append((layer, a, b, float(width[1]), (a,b)))
    # A physical connection to a pad must be present as an endpoint anchor.
    # Otherwise pad-interior or track-width contact could create a bypass that
    # the endpoint-only graph incorrectly treats as disconnected copper.
    for la,a,b,w,line in segs:
        for pad in pads:
            if not copper._pad_has_layer(pad,la):
                continue
            hit = [verified_pad_hit(pad,pt,copper) for pt in (a,b)]
            if not any(hit) and pad_box_distance(pad,a,b) <= w/2+1e-7:
                raise AuditError(f"{net}: unrepresented pad-track contact at {pad['ref']}.{pad['pad']}")
    # Distinct touching lands are not joined by the endpoint graph. Refuse a
    # conservative bounding-box overlap even if native DRC may later clear it.
    for i,pad in enumerate(pads):
        for other in pads[i+1:]:
            if not any(copper._pad_has_layer(pad,l) and copper._pad_has_layer(other,l) for l in set(pad['layers']+other['layers']) if l.endswith('.Cu')):
                continue
            angle=math.radians(other['angle']);co,si=math.cos(angle),math.sin(angle)
            hx,hy=other['sx']/2,other['sy']/2
            corners=[(other['x']+x*co+y*si,other['y']-x*si+y*co) for x,y in [(-hx,-hy),(hx,-hy),(hx,hy),(-hx,hy)]]
            if pad_box_distance(pad,(other['x'],other['y']),(other['x'],other['y'])) == 0. or pad_box_distance(other,(pad['x'],pad['y']),(pad['x'],pad['y'])) == 0. or any(pad_box_distance(pad,a,b)<=1e-7 for a,b in zip(corners,corners[1:]+corners[:1])):
                raise AuditError(f"{net}: potentially touching distinct pads {pad['ref']}.{pad['pad']} / {other['ref']}.{other['pad']}")
    for i, (la,a,b,wa,line) in enumerate(segs):
        for lb,c,d,wb,other in segs[i+1:]:
            if la != lb or segment_distance(*line,*other) > (wa+wb)/2 + 1e-7:
                continue
            # admit_node already proved that every vertex collapsed at this
            # precision physically touches. That shared graph vertex is a
            # represented join even when the serialized centers differ.
            if any(copper._path_node(x,la)==copper._path_node(y,la) for x in (a,b) for y in (c,d)):
                continue
            # Two tracks intentionally meeting within one ordinary land share
            # the same synthetic pad anchor even if their endpoints differ.
            if any(copper._pad_has_layer(p, la) and any(copper._point_in_pad(p,*x) for x in (a,b)) and any(copper._point_in_pad(p,*x) for x in (c,d)) for p in pads):
                continue
            raise AuditError(f"{net}: unsplit or width-only track contact; graph dominance unproven")
    vias = []
    for body in copper._blocks(text, "via"):
        if copper._net(body) != net:
            continue
        unsupported = expression_tags(body) - {'via','at','size','drill','layers','net','uuid','tstamp','locked','free','remove_unused_layers'}
        if unsupported or ('remove_unused_layers' in expression_tags(body) and not re.search(r'\(remove_unused_layers\s+no\)',body)):
            raise AuditError(f'{net}: unsupported via geometry syntax {sorted(unsupported)}')
        at = copper._pt(body, "at")
        size = re.search(r'\(size\s+([-\d.eE+]+)\)', body)
        span = re.search(r'\(layers\s+"([^"]+)"\s+"([^"]+)"', body)
        if not size or not span or not math.isfinite(float(size[1])) or float(size[1]) <= 0:
            raise AuditError(f"{net}: unpriced via contact")
        ends = span.groups()
        for layer in ends:
            admit_node(layer,at,float(size[1]))
        for other_at,other_size,_ends in vias:
            if at != other_at and math.dist(at,other_at) <= (float(size[1])+other_size)/2+1e-7:
                raise AuditError(f"{net}: unrepresented via-via annulus contact")
        vias.append((at,float(size[1]),ends))
        for pad in pads:
            # Through vias conservatively visit every declared copper layer;
            # unsupported blind-span precision must not hide a possible bond.
            hit = verified_pad_hit(pad,at,copper)
            if hit and not any(copper._pad_has_layer(pad,layer) for layer in ends):
                raise AuditError(f"{net}: unrepresented interior via-pad contact at {pad['ref']}.{pad['pad']}")
            if not hit and pad_box_distance(pad,at,at) <= float(size[1])/2+1e-7:
                raise AuditError(f"{net}: unrepresented pad-via contact at {pad['ref']}.{pad['pad']}")
        for la,a,b,w,line in segs:
            if la not in ends and point_segment_distance(at,*line) <= (float(size[1])+w)/2+1e-7:
                raise AuditError(f"{net}: unrepresented interior via-layer contact")
            if point_segment_distance(at,*line) <= (float(size[1])+w)/2 + 1e-7 and not any(copper._path_node(at,la)==copper._path_node(p,la) for p in (a,b)):
                if any(copper._pad_has_layer(p, la) and copper._point_in_pad(p,*at) and any(copper._point_in_pad(p,*x) for x in (a,b)) for p in pads):
                    continue
                raise AuditError(f"{net}: unsplit or width-only via contact; graph dominance unproven")

    for pad in pads:
        if pad['kind'] != 'thru_hole':
            continue
        served = {}
        for layer,a,b,w,line in segs:
            if copper._pad_has_layer(pad,layer):
                for point in (a,b):
                    if verified_pad_hit(pad,point,copper):
                        served.setdefault(layer,set()).add(point)
        for at,size,ends in vias:
            if verified_pad_hit(pad,at,copper):
                for layer in ends:
                    served.setdefault(layer,set()).add(at)
        center=(pad['x'],pad['y'])
        if len(served)>2 or (len(served)>1 and any(center not in points for points in served.values())):
            raise AuditError(f"{net}: unrepresented off-center/intermediate PTH layer transition at {pad['ref']}.{pad['pad']}")


def grade(oracle: Callable[[str, str], PathResult], config: dict) -> dict:
    config = validate_config(config)
    short_paths = config["short_paths"]
    prefixes = config["prefixes"]
    rows: list[dict] = []
    findings: list[str] = []
    cache: dict[tuple[str, str], PathResult] = {}

    def path(start: str, end: str) -> PathResult:
        key = (start, end)
        if key not in cache:
            cache[key] = oracle(start, end)
        return cache[key]

    dominance = getattr(oracle, "bypassed_prefix_edges", None)
    if not callable(dominance):
        raise AuditError("route oracle does not provide clamp-dominance proof")

    for decl in short_paths:
        start, end, maximum, required_layer, why = (decl[k] for k in ("from", "to", "max_length_mm", "layer", "why"))
        item = path(start, end)
        failures = []
        if (item.start != start or item.end != end or not item.net
                or not math.isfinite(item.length_mm) or item.length_mm < 0
                or not math.isfinite(item.pad_centre_mm) or item.pad_centre_mm < 0
                or not item.physical_edges):
            raise AuditError(f"{start}->{end}: invalid or empty measured path")
        if item.length_mm > maximum + 1e-9:
            failures.append(f"{item.length_mm:.6f} mm exceeds {maximum:.3f} mm")
        if item.via_count:
            failures.append(f"uses {item.via_count} via(s)")
        if item.layers != frozenset({required_layer}):
            failures.append(
                f"uses layers {sorted(item.layers)} instead of {required_layer} only"
            )
        if decl["max_pad_centre_mm"] is not None and item.pad_centre_mm > decl["max_pad_centre_mm"] + 1e-9:
            failures.append(
                f"pad-centre span {item.pad_centre_mm:.6f} mm exceeds {decl['max_pad_centre_mm']:.3f} mm"
            )
        verdict = "PASS" if not failures else "FAIL"
        rows.append({
            "kind": "short_path", "start": start, "end": end,
            "net": item.net, "length_mm": round(item.length_mm, 6),
            "maximum_mm": maximum, "required_layer": required_layer,
            "pad_centre_mm": round(item.pad_centre_mm, 6),
            "via_count": item.via_count,
            "layers": sorted(item.layers), "why": why, "verdict": verdict,
        })
        if failures:
            findings.append(f"{start}->{end}: " + "; ".join(failures))

    for decl in prefixes:
        start, clamp, targets, why = (decl[k] for k in ("from", "through", "targets", "why"))
        prefix = path(start, clamp)
        for target in targets:
            downstream = path(start, target)
            missing = sorted(prefix.physical_edges - downstream.physical_edges)
            bypassed = sorted(dominance(
                start, clamp, target, prefix.physical_edges
            ))
            verdict = "PASS" if not missing and not bypassed else "FAIL"
            rows.append({
                "kind": "branch_after_clamp", "start": start,
                "clamp": clamp, "target": target, "net": prefix.net,
                "prefix_edge_count": len(prefix.physical_edges),
                "missing_prefix_edge_count": len(missing),
                "bypassed_prefix_edge_count": len(bypassed),
                "why": why, "verdict": verdict,
            })
            if missing:
                findings.append(
                    f"{start}->{target} branches before {clamp}; "
                    f"{len(missing)} clamp-prefix edge(s) are bypassed"
                )
            if bypassed:
                findings.append(
                    f"{start}->{target} has parallel copper bypassing "
                    f"{clamp}; {len(bypassed)} prefix edge(s) are not cuts"
                )

    return {
        "schema": 1,
        "kind": "critical-path-audit-v1",
        "verdict": "PASS" if not findings else "FAIL",
        "graded": len(rows),
        "rows": rows,
        "findings": findings,
    }


def canonical_board_text(text):
    """Parse once and give every inherited geometry reader identical syntax.

    This is an analysis representation only. All original bytes remain bound
    by audit(); nothing is written back to the native board. Unsupported
    field arity, duplicate geometry fields and ambiguous identities fail here.
    """
    from land_witness import Atom, Unsupported, sexpressions
    try:
        forms=sexpressions(text,allow_escaped_strings=True)
    except Unsupported as exc:
        raise AuditError(f'board syntax: {exc}') from exc
    def tag(form):
        if not isinstance(form,list) or not form or not isinstance(form[0],Atom) or form[0].quoted:
            raise AuditError('invalid serialized object head')
        return form[0].text
    if len(forms)!=1 or tag(forms[0])!='kicad_pcb':
        raise AuditError('expected one complete native board expression')
    def walk(form):
        yield form
        for child in form[1:]:
            if isinstance(child,list):yield from walk(child)
    def atoms(form):
        if any(not isinstance(x,Atom) for x in form[1:]):
            raise AuditError(f'{tag(form)}: expected scalar fields')
        return form[1:]
    def name(value):
        if not isinstance(value,Atom) or any(c in value.text for c in ('"','\\')) or any(ord(c)<32 or ord(c)==127 for c in value.text):
            raise AuditError('unsupported escaped geometry identity')
        # Inspect original spelling, not only decoded text: identities never
        # admit an escape even when a metadata decoder could normalize it.
        if value.quoted and text[value.offset:value.offset+1]=='"':
            _,end=json.JSONDecoder().raw_decode(text,value.offset)
            if '\\' in text[value.offset:end]:
                raise AuditError('unsupported escaped geometry identity token')
        return value.text
    def quoted(value):return Atom(name(value),True,value.offset)
    def scalar_fields(form):
        result={}
        for child in form[1:]:
            if isinstance(child,list):
                key=tag(child)
                if key in {'at','size','layers','layer','net','start','end','mid','width','drill','roundrect_rratio'}:
                    if key in result:raise AuditError(f'{tag(form)}: duplicate geometry field {key}')
                    result[key]=child
        return result
    net_names={0:''}
    for form in walk(forms[0]):
        if tag(form)=='net' and len(form)==3:
            a,b=atoms(form)
            if a.quoted or not a.text.isdigit():raise AuditError('invalid numeric/name net declaration')
            ident=int(a.text);value=name(b)
            if ident in net_names and net_names[ident]!=value:raise AuditError('conflicting numeric net identity')
            net_names[ident]=value
    def normalized(form, parent=None):
        key=tag(form)
        geometry=key in {'footprint','pad','segment','arc','via','zone'} or key.startswith(('gr_','fp_'))
        fields=scalar_fields(form) if geometry else {}
        if key in ('footprint','pad'):
            required={'at','layer'} if key=='footprint' else {'at','size','layers'}
            if not required <= fields.keys():raise AuditError(f'{key}: missing geometry fields {sorted(required-fields.keys())}')
        if key=='net':
            values=atoms(form)
            if len(values)==2:value=values[1]
            elif len(values)==1:
                value=values[0]
                if not value.quoted and value.text.isdigit():
                    ident=int(value.text)
                    if ident not in net_names:raise AuditError('unresolved numeric net identity')
                    value=Atom(net_names[ident],True,value.offset)
            else:raise AuditError('invalid net field arity')
            return [form[0],quoted(value)]
        if key in ('layer','net_name') and parent!='stackup':
            values=atoms(form)
            if len(values)!=1:raise AuditError(f'{key}: invalid arity')
            return [form[0],quoted(values[0])]
        if key=='layers' and all(isinstance(x,Atom) for x in form[1:]):
            if len(form)<2:raise AuditError('empty copper layer set')
            return [form[0],*[quoted(x) for x in form[1:]]]
        # Geometry numbers are not repaired or guessed. Require the dialect
        # the downstream geometry reader actually represents.
        for field in fields.values():
            ftag=tag(field)
            if ftag in {'at','size','start','end','mid','width','roundrect_rratio'} and key in {'footprint','pad','segment','arc','via'}:
                values=atoms(field)
                allowed=(2,3) if ftag=='at' else ((2,) if ftag in {'start','end','mid'} or (ftag=='size' and key!='via') else (1,))
                if len(values) not in allowed or any(x.quoted for x in values):raise AuditError(f'{key}.{ftag}: unsupported numeric arity/dialect')
                try:
                    if not all(math.isfinite(float(x.text)) for x in values):raise ValueError('nonfinite')
                except ValueError as exc:raise AuditError(f'{key}.{ftag}: invalid number') from exc
        result=[form[0]]
        for i,value in enumerate(form[1:],1):
            if isinstance(value,list):result.append(normalized(value,key))
            elif key in ('footprint','pad') and i==1:
                result.append(quoted(value))
            elif key=='fp_text' and len(form)>1 and isinstance(form[1],Atom) and form[1].text=='reference' and i==2:
                result.append(quoted(value))
            elif key=='property' and i in (1,2):
                if i==1:name(value)  # dispatch keys must not acquire a new identity
                result.append(Atom(value.text,True,value.offset))
            else:result.append(value)
        if key=='footprint':
            refs=[x for x in result[1:] if isinstance(x,list) and tag(x)=='property' and len(x)>2 and isinstance(x[1],Atom) and x[1].text=='Reference']
            old_refs=[x for x in result[1:] if isinstance(x,list) and tag(x)=='fp_text' and len(x)>2 and isinstance(x[1],Atom) and x[1].text=='reference']
            if len(refs)+len(old_refs)!=1:raise AuditError('footprint requires one unambiguous reference')
            for row in refs+old_refs:name(row[2])
        return result
    tree=normalized(forms[0])
    def emit(form,depth):
        key=tag(form)
        head=[x for x in form if isinstance(x,Atom)]
        children=[x for x in form if isinstance(x,list)]
        # The legacy pad reader scans the first at expression; make that the
        # actual direct footprint/pad position, never a text/property offset.
        if key in ('footprint','pad'):
            children.sort(key=lambda x:0 if tag(x)=='at' else 1)
        prefix='\t'*depth+'('+' '.join(json.dumps(x.text,ensure_ascii=False) if x.quoted else x.text for x in head)
        if not children:return prefix+')'
        return prefix+'\n'+'\n'.join(emit(x,depth+1) for x in children)+'\n'+'\t'*depth+')'
    return emit(tree,0)+'\n'


def board_oracle(board_path: Path, config: dict) -> Callable[[str, str], PathResult]:
    config = validate_config(config)
    board_path = board_path.resolve()
    if not board_path.is_file() or board_path.is_symlink():
        raise AuditError(f"board is missing or not a regular file: {board_path}")
    import copper_length_audit as copper
    text=canonical_board_text(board_path.read_text(encoding='utf-8-sig'))
    nets, layers, text = copper.read_copper_text(text,board_path)
    pads = copper.read_pad_shapes(text)
    plated = copper.read_plated_pads(text)
    if layers != config["layers"]:
        raise AuditError(f"declared copper layers differ, got {layers}")

    pad_to_net: dict[str, str] = {}
    pad_centres: dict[str, tuple[float, float]] = {}
    for net, net_pads in pads.items():
        for pad in net_pads:
            ident = f"{pad['ref']}.{pad['pad']}"
            if ident in pad_to_net and pad_to_net[ident] != net:
                raise AuditError(f"ambiguous pad identity {ident}")
            pad_to_net[ident] = net
            pad_centres[ident] = (float(pad["x"]), float(pad["y"]))

    graphs: dict[str, tuple[dict, dict]] = {}

    def graph_for(net: str):
        if net not in graphs:
            if net not in nets:
                raise AuditError(f"net {net!r} has no routed copper")
            assert_graph_contacts(text, net, nets[net], pads.get(net, []), copper)
            graph, error = copper._path_graph(
                nets[net], layers, config["stackup_mm"], pads.get(net, []), plated.get(net, [])
            )
            if error or graph is None:
                raise AuditError(f"cannot build {net} copper graph: {error}")
            graphs[net] = (graph, nets[net])
        return graphs[net]

    def oracle(start: str, end: str) -> PathResult:
        start_net = pad_to_net.get(start)
        end_net = pad_to_net.get(end)
        if not start_net or not end_net:
            raise AuditError(f"missing exact pad endpoint {start} or {end}")
        if start_net != end_net:
            raise AuditError(f"{start} is {start_net}, but {end} is {end_net}")
        graph, entry = graph_for(start_net)
        length, used, error = copper._shortest_declared_path(graph, start, end)
        if error or length is None:
            raise AuditError(error or f"no path from {start} to {end}")
        segment_count = len(entry["segs"])
        via_count = sum(
            1 for edge in used
            if segment_count <= edge < segment_count + len(entry["vias"])
        )
        layers_used = frozenset(
            entry["segs"][edge][0]
            for edge in used if 0 <= edge < segment_count
        )
        return PathResult(
            start=start, end=end, net=start_net, length_mm=float(length),
            physical_edges=frozenset(used), via_count=via_count,
            layers=layers_used,
            pad_centre_mm=math.dist(pad_centres[start], pad_centres[end]),
        )

    def bypassed_prefix_edges(start: str, clamp: str, target: str,
                              prefix_edges: frozenset[int]) -> frozenset[int]:
        """Return prefix edges that are not start-to-target graph cuts."""
        start_net = pad_to_net.get(start)
        clamp_net = pad_to_net.get(clamp)
        target_net = pad_to_net.get(target)
        if not start_net or start_net != clamp_net or start_net != target_net:
            raise AuditError(
                f"dominance endpoints disagree: {start}, {clamp}, {target}"
            )
        graph, _entry = graph_for(start_net)
        starts = graph["anchors"].get(start) or []
        ends = set(graph["anchors"].get(target) or [])
        if not starts or not ends:
            raise AuditError(
                f"dominance endpoint lacks copper: {start} or {target}"
            )

        bypassed: set[int] = set()
        for blocked in prefix_edges:
            seen = set(starts)
            stack = list(starts)
            while stack and not (seen & ends):
                node = stack.pop()
                for nxt, _weight, edge_id in graph["adj"].get(node, []):
                    if edge_id == blocked or nxt in seen:
                        continue
                    seen.add(nxt)
                    stack.append(nxt)
            if seen & ends:
                bypassed.add(blocked)
        return frozenset(bypassed)

    setattr(oracle, "bypassed_prefix_edges", bypassed_prefix_edges)

    return oracle


def audit(board_path: Path, config: dict) -> dict:
    before = board_path.read_bytes()
    receipt = grade(board_oracle(board_path, config), config)
    if board_path.read_bytes() != before:
        raise AuditError("board changed during audit")
    receipt["board"] = str(board_path.resolve())
    receipt["board_sha256"] = hashlib.sha256(before).hexdigest()
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    try:
        raw = args.config.read_bytes()
        config = load_config(args.config)
        receipt = audit(args.board, config)
        if args.config.read_bytes() != raw:
            raise AuditError("config changed during audit")
        receipt["config_sha256"] = hashlib.sha256(raw).hexdigest()
    except (AuditError, ValueError, OSError) as exc:
        print(f"FAIL R-CRITICAL-PATH: {exc}")
        return 1
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    for row in receipt["rows"]:
        if row["kind"] == "short_path":
            print(f"{row['verdict']} {row['start']}->{row['end']} "
                  f"{row['length_mm']:.6f}mm vias={row['via_count']} "
                  f"layers={','.join(row['layers'])}")
        else:
            print(f"{row['verdict']} {row['start']}->{row['clamp']} "
                  f"before {row['target']}")
    for finding in receipt["findings"]:
        print("FAIL " + finding)
    print(f"R-CRITICAL-PATH {receipt['verdict']}: {receipt['graded']} graded, "
          f"{len(receipt['findings'])} findings")
    return 0 if receipt["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
