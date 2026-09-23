"""Exact Crow TMUX4827 YBH B2 POFV profile; no generic via exceptions.

The rule area is only a native-DRC aid.  ``audit`` binds every protected
0.35/0.20 via to live pad identity and checks the process flags independently.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pcbnew as p
import yaml

ID = "TMUX4827_YBH_B2_POFV"
REFS = tuple(f"U_ISO{i}" for i in range(1, 9))
AREA_PREFIX = "tmux4827_b2_pofv_"
AREA_HALF_MM = 0.005
TOL_MM = 0.0015
GEOMETRY = {
    "pad_diameter_mm": .35, "via_diameter_mm": .35, "drill_mm": .20,
    "annulus_mm": .075, "mask_opening_mm": .25,
    "paste_opening_mm": .25, "bga_via_to_pad_gap_mm": .10,
    "perimeter_pad_gap_mm": .15,
}


def mm(i):
    return p.ToMM(i)


def near(a, b, tol=TOL_MM):
    return abs(a-b) <= tol


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contract(assembly: dict, assembly_path: Path):
    """Return (profile, part, project root), or raise on any widened identity."""
    vp = assembly.get("via_process", {})
    profiles = vp.get("named_profiles", []) if isinstance(vp, dict) else []
    if not profiles:
        return None
    if not isinstance(profiles, list) or len(profiles) != 1 or not isinstance(profiles[0], dict):
        raise ValueError("TMUX-PROFILE: exactly one named profile is supported")
    q = profiles[0]
    wanted = {"id": ID, "kind": "tmux4827_ybh_b2_pofv_v1",
              "tier": "jlc_4layer_advanced", "finish": "ENIG",
              "pad": "5", "net": "GND", "expected_count": 8,
              "process": "type_vii_filled_and_capped_pofv"}
    for key, value in wanted.items():
        if type(q.get(key)) is not type(value) or q[key] != value:
            raise ValueError(f"TMUX-PROFILE: {key} must be {value!r}")
    if set(q) != set(wanted) | {"refs", "geometry", "evidence"}:
        raise ValueError("TMUX-PROFILE: unknown or missing profile fields")
    if q.get("refs") != list(REFS):
        raise ValueError("TMUX-PROFILE: refs must be exact ordered U_ISO1..8")
    g = q.get("geometry")
    if not isinstance(g, dict) or set(g) != set(GEOMETRY) or any(
        type(g[k]) not in (int, float) or not near(float(g[k]), v, 1e-9)
        for k, v in GEOMETRY.items()
    ):
        raise ValueError("TMUX-PROFILE: geometry is not exact qualified B2 geometry")
    ev = q.get("evidence")
    if not isinstance(ev, dict) or set(ev) != {"part", "coupon_sha256"} or ev["part"] != "02_parts/TMUX4827YBHR/part.yaml":
        raise ValueError("TMUX-PROFILE: exact part evidence path required")
    root = assembly_path.resolve().parents[2]
    nets = yaml.safe_load((root / "03_src/rules/nets.yaml").read_text())
    if nets.get("fab_tier") != q["tier"]:
        raise ValueError("TMUX-PROFILE: selected board tier disagrees")
    floor = yaml.safe_load((root / "03_src/floorplan.yaml").read_text()).get("design_rules", {})
    if (not near(float(floor.get("via_min_size", -1)), .45, 1e-9)
        or not near(float(floor.get("via_min_annulus", -1)), .13, 1e-9)
        or not near(float(floor.get("min_clearance", -1)), .15, 1e-9)):
        raise ValueError("TMUX-PROFILE: authored ordinary via/clearance floors changed")
    part_path = root / ev["part"]
    part = yaml.safe_load(part_path.read_text())
    topo = part["escape"]["center_via_topology"]
    if part.get("mpn") != "TMUX4827YBHR" or part.get("manufacturer") != "Texas Instruments" or part.get("footprint") != "crow_usb_analog:TI_YBH0009_C02_TMUX4827":
        raise ValueError("TMUX-PROFILE: part MPN/manufacturer/footprint changed")
    if part.get("pins", {}).get("5") != "GND" or topo.get("ball_to_pad") != {
        "A1":"1", "A2":"2", "A3":"3", "B1":"4", "B2":"5",
        "B3":"6", "C1":"7", "C2":"8", "C3":"9"}:
        raise ValueError("TMUX-PROFILE: retained TI B2/5 map changed")
    for key, val in (("land_diameter_mm", .25), ("center_via_diameter_mm", .35),
                     ("center_via_drill_mm", .20), ("center_mask_opening_mm", .25)):
        if not near(float(topo.get(key, -1)), val, 1e-9):
            raise ValueError(f"TMUX-PROFILE: part topology {key} changed")
    if any(part.get("pins", {}).get(number) != function
           for number, function in (("7", "S1B"), ("8", "VDD"), ("9", "S2B"))):
        raise ValueError("TMUX-PROFILE: perimeter signal/supply functions changed")
    coupon = (part_path.parent / topo["coupon"]["local"]).resolve()
    native = (part_path.parent / topo["native_footprint"]["local"]).resolve()
    if (sha(coupon) != topo["coupon"]["sha256"] or
        sha(coupon) != ev["coupon_sha256"] or
        sha(native) != topo["native_footprint"]["sha256"]):
        raise ValueError("TMUX-PROFILE: coupon/native footprint hash changed")
    return q, part, root


def pad_position(pad):
    v = pad.GetPosition()
    return mm(v.x), mm(v.y)


def center_pads(board, part, failures):
    found = {}
    fps = list(board.GetFootprints())
    mapping = part["escape"]["center_via_topology"]["ball_to_pad"]
    for ref in REFS:
        matches = [f for f in fps if f.GetReference() == ref]
        if len(matches) != 1:
            failures.append(f"TMUX-ID {ref}: expected one footprint, found {len(matches)}")
            continue
        f = matches[0]
        if f.GetFPIDAsString() != part["footprint"] or f.GetValue() != part["mpn"]:
            failures.append(f"TMUX-ID {ref}: footprint or MPN differs from part.yaml")
        pads = list(f.Pads())
        if len(pads) != 9 or sorted(x.GetNumber() for x in pads) != [str(i) for i in range(1, 10)]:
            failures.append(f"TMUX-PAD {ref}: expected exact numeric nine-pad map")
            continue
        bynum = {x.GetNumber(): x for x in pads}
        for number, xoff, yoff in (("1",-.4,-.4),("2",0,-.4),("3",.4,-.4),
                                   ("4",-.4,0),("5",0,0),("6",.4,0),
                                   ("7",-.4,.4),("8",0,.4),("9",.4,.4)):
            land=bynum[number]
            local=land.GetFPRelativePosition()
            size=.35 if number=="5" else .25
            mask=-.05 if number=="5" else 0
            paste=land.GetSolderPasteMargin(p.F_Paste)
            if (not near(mm(local.x),xoff) or not near(mm(local.y),yoff)
                or not near(mm(land.GetSize().x),size) or not near(mm(land.GetSize().y),size)
                or land.GetShape()!=p.PAD_SHAPE_CIRCLE or land.GetAttribute()!=p.PAD_ATTRIB_SMD
                or land.GetDrillSize().x != 0 or not all(land.IsOnLayer(layer) for layer in (p.F_Cu,p.F_Mask,p.F_Paste))
                or land.IsOnLayer(p.B_Cu) or land.IsOnLayer(p.B_Mask) or land.IsOnLayer(p.B_Paste)
                or not near(mm(land.GetLocalSolderMaskMargin() or 0),mask)
                or not near(mm(land.GetLocalSolderPasteMargin() or 0),mask)
                or abs(land.GetLocalSolderPasteMarginRatio() or 0) > 1e-9
                or not near(mm(land.GetSolderMaskExpansion(p.F_Mask)),mask)
                or not near(mm(paste[0]),mask) or not near(mm(paste[1]),mask)):
                failures.append(f"TMUX-PAD {ref}.{number}: embedded footprint land differs from hashed native pad map")
        index = ref.removeprefix("U_ISO")
        for number, net in (("7", f"FILTER{index}P"), ("8", "N5V_LDO_HOLD"),
                            ("9", f"FILTER{index}N")):
            if bynum[number].GetNetname() != net:
                failures.append(f"TMUX-PERIMETER {ref}.{number}: expected exact net {net}")
        c = bynum["5"]
        if c.GetNetname() != "GND" or c.GetAttribute() != p.PAD_ATTRIB_SMD or c.GetShape() != p.PAD_SHAPE_CIRCLE or c.GetDrillSize().x != 0 or not c.IsOnLayer(p.F_Cu):
            failures.append(f"TMUX-PAD {ref}.5: B2 must be undrilled circular F.Cu SMD GND")
        dia = (mm(c.GetSize().x), mm(c.GetSize().y))
        if not all(near(v, .35) for v in dia):
            failures.append(f"TMUX-PAD {ref}.5: copper land must be diameter 0.35")
        if not c.IsOnLayer(p.F_Mask) or not c.IsOnLayer(p.F_Paste) or not near(.35 + 2*mm(c.GetLocalSolderMaskMargin()), .25) or not near(.35 + 2*mm(c.GetLocalSolderPasteMargin()), .25):
            failures.append(f"TMUX-PAD {ref}.5: mask/paste apertures must be diameter 0.25")
        cx, cy = pad_position(c)
        for ball in ("A2", "B1", "B3", "C2"):
            n = bynum[mapping[ball]]
            x, y = pad_position(n)
            if n.GetNetname() == "GND" or n.GetShape() != p.PAD_SHAPE_CIRCLE or not near(mm(n.GetSize().x), .25) or not near(mm(n.GetSize().y), .25) or not near(abs(x-cx)+abs(y-cy), .4) or not (near(x,cx) or near(y,cy)):
                failures.append(f"TMUX-PAD {ref}.{ball}: expected different-net orthogonal diameter 0.25 at pitch 0.40")
        found[ref] = c
    return found


def area_bounds(center):
    x,y = pad_position(center)
    h=AREA_HALF_MM
    return x-h,y-h,x+h,y+h


def audit(board, profile, part, require_areas=True, require_vias=True):
    failures = []
    if board.GetCopperLayerCount() != 4:
        failures.append("TMUX-TIER: B2 profile requires the selected four-layer board")
    centers = center_pads(board, part, failures)
    vias = [v for v in board.GetTracks() if v.GetClass() == "PCB_VIA"]
    accepted = set()
    for ref, pad in centers.items():
        cx,cy = pad_position(pad)
        hits = [v for v in vias if abs(mm(v.GetPosition().x)-cx) <= TOL_MM and abs(mm(v.GetPosition().y)-cy) <= TOL_MM]
        if require_vias and len(hits) != 1:
            failures.append(f"TMUX-VIA {ref}.5: expected exactly one centred via, found {len(hits)}")
        for v in hits:
            accepted.add(v.m_Uuid.AsString())
            diameter, drill = mm(v.GetWidth(p.F_Cu)), mm(v.GetDrill())
            if (v.GetNetname() != "GND" or not near(diameter,.35) or not near(drill,.20)
                or not near((diameter-drill)/2,.075) or v.TopLayer() != p.F_Cu or v.BottomLayer() != p.B_Cu
                or v.GetFillingMode() != p.FILLING_MODE_FILLED
                or v.GetCappingMode() != p.CAPPING_MODE_CAPPED):
                failures.append(f"TMUX-VIA {ref}.5: net, layers, geometry, fill or cap differs")
    for v in vias:
        if near(mm(v.GetWidth(p.F_Cu)), .35) and near(mm(v.GetDrill()), .20) and v.m_Uuid.AsString() not in accepted:
            failures.append("TMUX-VIA: 0.35/0.20 via outside exact B2 centres")
    if require_vias and len(accepted) != 8:
        failures.append(f"TMUX-VIA: expected eight B2 vias, found {len(accepted)}")
    zones = [z for z in board.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith(AREA_PREFIX)]
    if require_areas:
        expected = {AREA_PREFIX+ref for ref in REFS}
        names = [z.GetZoneName() for z in zones]
        if len(names) != 8 or set(names) != expected:
            failures.append("TMUX-AREA: missing, duplicate or foreign producer area")
        for z in zones:
            ref = z.GetZoneName()[len(AREA_PREFIX):]
            if ref not in centers:
                continue
            x0,y0,x1,y1=area_bounds(centers[ref]);bb=z.GetBoundingBox()
            if (not all(near(a,b) for a,b in ((mm(bb.GetLeft()),x0),(mm(bb.GetTop()),y0),(mm(bb.GetRight()),x1),(mm(bb.GetBottom()),y1)))
                or not z.IsOnLayer(p.F_Cu)):
                failures.append(f"TMUX-AREA {ref}: stale or widened area geometry")
            # KiCad insideArea matches overlap, so reject any other via whose
            # copper disc intersects the tiny rule area, including wrong-net vias.
            for v in vias:
                if v.m_Uuid.AsString() in accepted:
                    continue
                x,y=mm(v.GetPosition().x),mm(v.GetPosition().y)
                radius=mm(v.GetWidth(p.F_Cu))/2
                if x0-radius <= x <= x1+radius and y0-radius <= y <= y1+radius:
                    failures.append(f"TMUX-AREA {ref}: foreign via overlaps exemption")
    return failures


def dru_rules():
    rules = ['(rule "tmux_ordinary_via_floor"\n  (condition "A.Type == \'Via\'")\n  (constraint via_diameter (min 0.45mm))\n  (constraint annular_width (min 0.13mm)))']
    for ref in REFS:
        area=AREA_PREFIX+ref
        rules.append(f'''(rule "{area}_via"
  (condition "A.Type == 'Via' && A.NetName == 'GND' && A.insideArea('{area}')")
  (constraint via_diameter (min 0.35mm))
  (constraint annular_width (min 0.075mm))
  (constraint hole_size (min 0.20mm)))''')
        for n in ("2","4","6","8"):
            pair=(f"A.Type == 'Pad' && B.Type == 'Pad' && A.Reference == '{ref}' && B.Reference == '{ref}' && A.Pad_Number == '5' && B.Pad_Number == '{n}'")
            reverse=(f"A.Type == 'Pad' && B.Type == 'Pad' && A.Reference == '{ref}' && B.Reference == '{ref}' && A.Pad_Number == '{n}' && B.Pad_Number == '5'")
            rules.append(f'''(rule "{area}_pad_{n}"
  (condition "(({pair}) || ({reverse})) && A.NetName != B.NetName")
  (constraint clearance (min 0.10mm)))''')
            pair_v=(f"A.Type == 'Via' && A.NetName == 'GND' && A.insideArea('{area}') && B.Type == 'Pad' && B.Reference == '{ref}' && B.Pad_Number == '{n}'")
            reverse_v=(f"B.Type == 'Via' && B.NetName == 'GND' && B.insideArea('{area}') && A.Type == 'Pad' && A.Reference == '{ref}' && A.Pad_Number == '{n}'")
            rules.append(f'''(rule "{area}_via_pad_{n}"
  (condition "(({pair_v}) || ({reverse_v})) && A.NetName != B.NetName")
  (constraint clearance (min 0.10mm))
  (constraint hole_clearance (min 0.175mm)))''')
        index = ref.removeprefix("U_ISO")
        for number, signal in (("7", f"FILTER{index}P"), ("9", f"FILTER{index}N")):
            pair = (f"A.Type == 'Pad' && B.Type == 'Pad' && A.Reference == '{ref}' && "
                    f"B.Reference == '{ref}' && A.Pad_Number == '{number}' && B.Pad_Number == '8' && "
                    f"A.NetName == '{signal}' && B.NetName == 'N5V_LDO_HOLD'")
            reverse = (f"B.Type == 'Pad' && A.Type == 'Pad' && B.Reference == '{ref}' && "
                       f"A.Reference == '{ref}' && B.Pad_Number == '{number}' && A.Pad_Number == '8' && "
                       f"B.NetName == '{signal}' && A.NetName == 'N5V_LDO_HOLD'")
            rules.append(f'''(rule "tmux_perimeter_{ref}_{number}_8"
  (condition "({pair}) || ({reverse})")
  (constraint clearance (min 0.15mm)))''')
    return rules
