#!/usr/bin/env python3
"""Package escape feasibility vs fab tier — the D-ESC gate's math (v2:
the ESCAPE-BUDGET model with CONDITIONAL verdicts).

Predicts, from package geometry and the fab capability model
(references/fab_tiers.yaml), the cheapest tier a package can escape at.
This is a PREDICTION from datasheet geometry; DRC/KRT later discover the
same wall empirically — checker and checked share no method (canon M1).

The physics, per package style:
- leaded / connector / passive: pads escape OUTWARD (gull-wing rows, edge
  pins); no via fanout ring is forced. BUT a DENSE leaded side hits the
  hole-to-hole wall: when pitch - min_via_drill < min_hole_to_hole, NO via
  fits between adjacent pins, so every escape must clear the row on the
  surface layer first. With >= DENSE_LEADED_ESCAPES escapes on one side
  the fan-out band saturates — the cheap tier is then CONDITIONAL on a
  reserved escape corridor at placement (floorplan `escape_corridors:`).
  Incident: LM5116 HTSSOP-20 @ 0.65mm, 8 escapes on the right side —
  0.65 - 0.3 drill = 0.35 < 0.5 hole-to-hole at jlc_4layer_standard =
  the v3 clean-room stall (usb-pwr-hub-3s ADR-0008, 2026-07-21).
- qfn / dfn (bottom-terminated, exposed pad): inner-facing nets need a
  dogbone via ring just outside the pads. The ring exists iff
      min_via_diameter + min_space <= pitch
  (adjacent dogbone vias at pad pitch), OR the tier allows via-in-pad.
  Incident: SY8368 QFN-10 @ 0.45-0.5mm pitch — 0.45 + 0.127 = 0.577 > 0.5
  at jlc_4layer_standard = the clean-room 3S stall (2026-07-20).
  CALIBRATION AGAINST SHIPPED GROUND TRUTH (a4ff7ed, 2026-07-21): the
  same SY8368 SHIPPED x2 at STANDARD tier on xt60-usb-supply-rerun with
  outward-only escapes — one surface track per fine pad, zero vias
  between pads, every escape net terminating in an adjacent passive.
  So for a SMALL dual-row-class QFN (npins <= OUTWARD_MAX_PINS) with a
  declared escape budget (escapes_worst_side <= OUTWARD_MAX_ESCAPES) the
  ring-infeasible tier is CONDITIONALLY feasible: condition
  `outward-only-local` (outward-only escape + all fine-pad nets local to
  adjacent passives, D-ADJ). A four-sided VQFN (LM5145, 20 pins — 3
  boards shipped ADVANCED) or a QFN-48 (IP6559-C) can NOT do outward-only
  and stays unconditional-advanced.
- bga: the generic model needs a dogbone ring AND an inter-ball routing
  lane (min_track + 2*min_space <= pitch - ball land, land ~= pitch/2).
  A separately declared 3x3 topology can instead use eight outward surface
  launches and one center filled/capped via, conditional on exact coupon and
  native-footprint SHA bindings, JLC BGA geometry and advanced via-in-pad.
  The Crow TMUX4827 coupon is the first named consumer. The condition proves
  source-stage geometric feasibility only; production CAM/process remains owed.

CONDITIONS VOCABULARY (emitted in the escape block, verified by P-ESC):
  outward-only-local  every fine-pad net terminates in an adjacent local
                      passive; escapes go outward only, no crossings, no
                      layer drops (the shipped SY8368 configuration)
  escape-corridor     a reserved routing lane at placement for the dense
                      side's fan-out (floorplan `escape_corridors:` key)
  center-via-perimeter-outward-coupon  reviewed 3x3 native coupon, exact
                      footprint and dimension-derived advanced via-in-pad;
                      vendor process acceptance remains a separate hold
A part.yaml claiming a CONDITIONAL tier must record the SAME conditions
in its escape block, or P-ESC fails it — a conditional verdict must be
EARNED per board, never inherited by copy.

usage:
  escape_check.py <part.yaml> [...]      # grade part.yaml escape blocks
  escape_check.py --style qfn --pitch 0.5 [--escapes-worst-side N] [--pins N]
  escape_check.py --board B.kicad_pcb    # P-LAND: finite declared-width witness per pad
Prints per-tier verdicts + the minimum tier; exits 1 on any infeasible-
everywhere part or any part.yaml whose declared block contradicts the math.

P-LAND — finite declared-width native launch witnesses (canon M-ENTRY).

The library land_witness.py admits the entire board/project/rules context,
then searches positive declared widths up to 2 mm, native-admitted adaptive
starts, 48 directions and 1 mm reach on enabled copper layers. A witness
records actual Track geometry, width rule and limiting Track–Pad pair.
NO_VALIDATED_WITNESS describes that finite policy, not a width maximum,
deficit, routing diagnosis or impossibility. Native DRC and connectivity
remain separate downstream gates. Actual incident tracks are inventoried at
their native geometry outside this finite policy. Nominal pour and native
via-on-land buckets are explicit inventory scope, not connectivity proof.

VACUITY: (canon G-VACUOUS. Fixtured by `t1_escape_tier.py`
`t_vacuity_P_LAND_passes_a_pad_whose_class_declares_no_width_floor`.)
A pad whose class declares no width floor is counted outside this model.
Thus an undeclared electrical width requirement cannot make this gate fail.
The maintained QSPI-only contrast preserves 13 graded pads and more than
250 floorless pads, then restores the eleven CAL findings with their
explicit floors. Board default widths do not invent declared requirements.
A zero graded denominator and unsupported/unreadable inputs block.
"""
import argparse
import hashlib
import math
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

TIERS_PATH = Path(__file__).resolve().parent.parent / "references" / "fab_tiers.yaml"

OUTWARD_STYLES = {"leaded", "connector", "passive", "module",
                  "through_hole"}
RING_STYLES = {"qfn", "dfn"}

# Calibration constants — each number is PAID-FOR ground truth, not tuning:
#   OUTWARD_MAX_ESCAPES = 6: the SY8368 shipped with ~6 outward escapes on
#     its fine side (measured on the sealed xt60-usb-supply-rerun board).
#   OUTWARD_MAX_PINS = 12: the dual-row 3x3-class QFN family the proof
#     covers; the LM5145 (VQFN-20, 4 sides, 3 boards shipped ADVANCED)
#     must NOT qualify for the outward-only rescue.
#   DENSE_LEADED_ESCAPES = 6: leaded sides with < 6 escapes closed at the
#     cheapest tier on many boards; 8 escapes hit the ADR-0008 wall (v3).
OUTWARD_MAX_ESCAPES = 6
OUTWARD_MAX_PINS = 12
DENSE_LEADED_ESCAPES = 6
COND_OUTWARD = "outward-only-local"
COND_CORRIDOR = "escape-corridor"
COND_CENTER_VIA = "center-via-perimeter-outward-coupon"
KNOWN_CONDITIONS = {COND_OUTWARD, COND_CORRIDOR, COND_CENTER_VIA}

# JLCPCB 4-layer BGA design guidance (reviewed 2026-09-23): 0.25-mm
# minimum ball land, 0.35-mm recommended filled-via copper, 0.10-mm
# via-to-ball copper spacing. Geometry at these floors remains conditional
# on exact-board DRC, selective Type VII processing and vendor acceptance.
BGA_LAND_MIN = 0.25
BGA_FILLED_VIA_MIN = 0.35
BGA_VIA_PAD_GAP_MIN = 0.10
TMUX4827_COUPON_SHA256 = "6f39a73aad46444e6b2256ced0b64a1dea5b9792801c3f705f8b691727ce83b6"
TMUX4827_BALL_FUNCTIONS = {
    "A1": "S1A_UNUSED", "A2": "SEL", "A3": "S2A_UNUSED",
    "B1": "D1", "B2": "GND", "B3": "D2",
    "C1": "S1B", "C2": "VDD", "C3": "S2B",
}


def center_via_geometry_ok(pitch, tier, t):
    """Special topology: only one inner ball; all perimeter balls exit outward."""
    try:
        if any(type(t[key]) is not int for key in
               ("rows", "cols", "perimeter_outward_launches")):
            return False
        rows, cols = t["rows"], t["cols"]
        land = float(t["land_diameter_mm"])
        via = float(t["center_via_diameter_mm"])
        drill = float(t["center_via_drill_mm"])
        opening = float(t["center_mask_opening_mm"])
        outward = t["perimeter_outward_launches"]
    except (KeyError, TypeError, ValueError):
        return False
    if not all(math.isfinite(x) for x in (pitch, land, via, drill, opening)):
        return False
    if rows != 3 or cols != 3 or outward != rows * cols - 1:
        return False
    if land + 1e-6 < BGA_LAND_MIN or via + 1e-6 < BGA_FILLED_VIA_MIN:
        return False
    if not (0 < drill < via and 0 < opening <= via):
        return False
    # Reviewed coupon has one 0.35/0.20 center via; 0.075-mm annulus is
    # diagnostic geometry, with fabrication acceptance still outstanding.
    if abs(drill - 0.20) > 1e-6 or (via - drill) / 2 + 1e-6 < 0.075:
        return False
    if pitch - (land + via) / 2 + 1e-6 < BGA_VIA_PAD_GAP_MIN:
        return False
    # Parallel outward launches are separated by one pitch. No lane between
    # balls is claimed; the only layer transition is the filled center via.
    if pitch - tier["min_track"] + 1e-6 < tier["min_space"]:
        return False
    return (tier.get("via_in_pad", False)
            and tier["min_via_diameter"] <= via + 1e-6
            and tier["min_via_drill"] <= drill + 1e-6
            and tier["min_space"] <= BGA_VIA_PAD_GAP_MIN + 1e-6)


def check_center_via_evidence(part_yaml, y, t):
    """Bind the dimension claim to retained exact native footprint and coupon."""
    mpn = y.get("mpn", Path(part_yaml).parent.name)
    probs = []
    if not isinstance(t, dict):
        return [f"{mpn}: center-via topology must be a mapping"]
    pins = y.get("pins") or {}
    expected_map = {f"{row}{col}": str(index) for index, (row, col) in
                    enumerate(((row, col) for row in "ABC" for col in "123"), 1)}
    expected = set(expected_map)
    mapping = t.get("ball_to_pad")
    if not isinstance(mapping, dict) or mapping != expected_map:
        probs.append(f"{mpn}: center-via topology requires exact TI A1..C3 to numeric pad mapping")
        return probs
    if set(map(str, pins)) != set(mapping.values()) or str(pins.get(mapping["B2"], "")).upper() != "GND":
        probs.append(f"{mpn}: center-via topology requires exact numeric pads and B2 GND")
    if mpn != "TMUX4827YBHR" or any(
            pins.get(mapping[ball]) != function
            for ball, function in TMUX4827_BALL_FUNCTIONS.items()):
        probs.append(f"{mpn}: center-via topology requires exact TI TMUX4827 ball functions")
    for field in ("coupon", "native_footprint"):
        record = t.get(field)
        if not isinstance(record, dict) or not record.get("local") or not record.get("sha256"):
            probs.append(f"{mpn}: missing {field} local path and SHA-256")
            continue
        if field == "coupon" and record["sha256"] != TMUX4827_COUPON_SHA256:
            probs.append(f"{mpn}: coupon differs from independently reviewed exact diagnostic board")
        path = (Path(part_yaml).parent / str(record["local"])).resolve()
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]:
            probs.append(f"{mpn}: {field} missing or SHA-256 mismatch: {path}")
            continue
        if field == "native_footprint":
            raw = path.read_text()
            all_names = re.findall(r'\(pad "([^"]+)" smd', raw)
            if len(all_names) != 9 or set(all_names) != set(mapping.values()):
                probs.append(f"{mpn}: native footprint must contain only mapped numeric pads")
            found = {}
            for pin, x, yy, diameter in re.findall(
                    r'\(pad "([1-9])" smd circle\s*\(at ([-\d.]+) ([-\d.]+)\)\s*\(size ([-\d.]+) \4\)', raw):
                found[pin] = (float(x), float(yy), float(diameter))
            try:
                pitch = float((y.get("escape") or {})["pitch"])
                land = float(t["land_diameter_mm"])
                via = float(t["center_via_diameter_mm"])
                for row, yy in zip("ABC", (-pitch, 0, pitch)):
                    for col, x in zip("123", (-pitch, 0, pitch)):
                        want = (x, yy, via if row + col == "B2" else land)
                        got = found.get(mapping[row + col])
                        if got is None or any(abs(a - b) > 0.0015 for a, b in zip(got, want)):
                            probs.append(f"{mpn}: native footprint ball {row+col} geometry differs from topology")
                margin = (float(t["center_mask_opening_mm"]) - via) / 2
                b2 = re.search(r'\(pad "' + re.escape(mapping["B2"]) + r'" smd circle[^\n]*', raw)
                if (not b2 or f'(solder_mask_margin {margin:g})' not in b2.group()
                        or f'(solder_paste_margin {margin:g})' not in b2.group()):
                    probs.append(f"{mpn}: native B2 mask/paste opening differs from topology")
            except (KeyError, TypeError, ValueError):
                probs.append(f"{mpn}: incomplete center-via topology dimensions")
    return probs


def load_tiers(path=TIERS_PATH):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8-sig"))["tiers"]


def grade_tier(style, pitch, tier, escapes_worst_side=None, npins=None,
               topology=None):
    """One tier's verdict: ('ok'|'conditional'|'no', [conditions]).

    'ok' = unconditionally feasible geometry. 'conditional' = feasible only
    under the returned conditions (which the part.yaml must record and the
    board must honour). 'no' = infeasible at this tier.
    """
    pitch = float(pitch)
    if style in OUTWARD_STYLES:
        # Dense-leaded wall (ADR-0008): applies to gull-wing rows only —
        # connectors/passives/modules never carry an 8-escape 0.65mm side
        # in this fleet, so the corridor condition stays evidence-scoped.
        if style == "leaded" and escapes_worst_side is not None \
                and int(escapes_worst_side) >= DENSE_LEADED_ESCAPES:
            wall = pitch - tier["min_via_drill"] < tier["min_hole_to_hole"]
            if wall and not tier.get("via_in_pad", False):
                return "conditional", [COND_CORRIDOR]
        return "ok", []
    if style in RING_STYLES:
        ring = (tier["min_via_diameter"] + tier["min_space"] <= pitch
                or tier.get("via_in_pad", False))
        if ring:
            return "ok", []
        # outward-only rescue: proven ONLY for the small dual-row class
        # with a declared, small escape budget (see module docstring)
        if (escapes_worst_side is not None
                and int(escapes_worst_side) <= OUTWARD_MAX_ESCAPES
                and (npins is None or int(npins) <= OUTWARD_MAX_PINS)):
            return "conditional", [COND_OUTWARD]
        return "no", []
    if style == "bga":
        if topology is not None:
            if center_via_geometry_ok(pitch, tier, topology):
                return "conditional", [COND_CENTER_VIA]
            return "no", []
        ring = (tier["min_via_diameter"] + tier["min_space"] <= pitch
                or tier.get("via_in_pad", False))
        lane = tier["min_track"] + 2 * tier["min_space"] <= pitch - pitch / 2
        return ("ok", []) if ring and lane else ("no", [])
    raise ValueError(f"unknown escape style '{style}' "
                     f"(known: {sorted(OUTWARD_STYLES | RING_STYLES | {'bga'})})")


def feasible(style, pitch, tier):
    """Back-compat: unconditional geometric feasibility (no budget facts)."""
    return grade_tier(style, pitch, tier)[0] == "ok"


def tier_required(style, pitch, tiers, escapes_worst_side=None, npins=None,
                  topology=None):
    """Name of the cheapest UNCONDITIONALLY feasible tier, or None."""
    ranked = sorted(tiers.items(), key=lambda kv: kv[1]["rank"])
    for name, t in ranked:
        if grade_tier(style, pitch, t, escapes_worst_side, npins, topology)[0] == "ok":
            return name
    return None


def tier_conditional(style, pitch, tiers, escapes_worst_side=None, npins=None,
                     topology=None):
    """Cheapest tier feasible AT ALL -> (name, [conditions]) or (None, [])."""
    ranked = sorted(tiers.items(), key=lambda kv: kv[1]["rank"])
    for name, t in ranked:
        v, conds = grade_tier(style, pitch, t, escapes_worst_side, npins, topology)
        if v in ("ok", "conditional"):
            return name, conds
    return None, []


# package/footprint-string sanity: catches an escape block whose declared
# inputs contradict the part's own footprint name (the tamper/copy hole)
STYLE_TOKENS = [
    (r"\bW?LCSP|\bBGA", "bga"),
    (r"\bU?[TVWX]?QFN|\bDFN|\bSON\b", "qfn"),
    (r"\bH?T?SS?OP|\bSOIC|\bSOT|\bSOP|\bTO-|\bQFP|\bDPAK|\bPAK", "leaded"),
]


def infer_from_strings(*strings):
    """(style_guess, pitch_guess) from package/footprint text; None if unknown."""
    blob = " ".join(s for s in strings if s)
    style = None
    for pat, st in STYLE_TOKENS:
        if re.search(pat, blob, re.I):
            style = st
            break
    m = re.search(r"P(\d+\.\d+)(?:mm)?", blob)
    pitch = float(m.group(1)) if m else None
    return style, pitch


def check_part(part_yaml, tiers):
    """-> list of problem strings (empty = part's escape block agrees)."""
    y = yaml.safe_load(Path(part_yaml).read_text(encoding="utf-8-sig")) or {}
    npins = len(y.get("pins") or {})
    mpn = y.get("mpn", Path(part_yaml).parent.name)
    probs = []
    # `mates:` is a connector PART FACT (plug|receptacle) — the male-plug
    # incident (usb-hub-3s ADR-0006, 2026-07-21): a USB-A MALE PLUG served
    # weeks as a receptacle because gender lives only in the drawing title
    # block. The fact is recorded here; role-vs-gender remains a HUMAN
    # check (pin review) — see t4_regressions.
    mates = y.get("mates")
    if mates is not None and mates not in ("plug", "receptacle"):
        probs.append(f"{mpn}: mates: '{mates}' is not plug|receptacle")
    # Harness housings, loose contacts, and other explicitly off-board parts
    # can legitimately expose several numbered circuits without owning any
    # PCB copper.  Requiring a fabricated-board escape tier for those parts
    # would force a false footprint/land claim.  Their cavity/service geometry
    # remains governed by the connector-assembly and pin-review contracts.
    if y.get("footprint") == "none_off_board":
        return probs
    if npins <= 2:
        return probs
    esc = y.get("escape")
    if not esc:
        return probs + [f"{mpn}: multi-pin part has NO escape block "
                        f"(D-ESC: declare style+pitch, run escape_check)"]
    style, pitch = esc.get("style"), esc.get("pitch")
    if not style or not pitch:
        return probs + [f"{mpn}: escape block missing style/pitch"]
    known_styles = OUTWARD_STYLES | RING_STYLES | {"bga"}
    if style not in known_styles:
        return probs + [f"{mpn}: unknown escape style '{style}' "
                        f"(known: {sorted(known_styles)})"]
    g_style, g_pitch = infer_from_strings(y.get("package", ""),
                                          y.get("footprint", ""))
    # Package strings normalize DFN/SON and QFN to one bottom-terminated
    # ring family. Both declared spellings use the identical grade_tier
    # operator; that normalization is not a package contradiction. Pitch,
    # escape budget, conditions and the computed tier still grade below.
    same_family = g_style in RING_STYLES and style in RING_STYLES
    if g_style and g_style != style and not same_family and not (
            g_style == "leaded" and style in ("connector", "module")):
        probs.append(f"{mpn}: declared style '{style}' contradicts "
                     f"package/footprint text ('{g_style}')")
    if g_pitch and abs(g_pitch - float(pitch)) > 0.051:
        probs.append(f"{mpn}: declared pitch {pitch} contradicts "
                     f"footprint text (P{g_pitch}mm)")

    ews = esc.get("escapes_worst_side")
    if ews is not None and (not isinstance(ews, int) or ews < 0):
        probs.append(f"{mpn}: escapes_worst_side '{ews}' is not a "
                     f"non-negative integer")
        ews = None
    conds_declared = esc.get("conditions") or []
    unknown_conds = sorted(set(conds_declared) - KNOWN_CONDITIONS)
    if unknown_conds:
        probs.append(f"{mpn}: unknown escape condition(s) {unknown_conds} "
                     f"(known: {sorted(KNOWN_CONDITIONS)})")
        return probs

    topology = esc.get("center_via_topology")
    if topology is not None:
        if style != "bga":
            probs.append(f"{mpn}: center-via topology requires bga style")
        probs.extend(check_center_via_evidence(part_yaml, y, topology))
    want = tier_required(style, float(pitch), tiers, ews, npins, topology)
    conditional_want, conditional_need = tier_conditional(
        style, float(pitch), tiers, ews, npins, topology)
    got = esc.get("tier_required")
    if want is None:
        if conditional_want is None:
            probs.append(f"{mpn}: {style} @ {pitch}mm escapes at NO known tier "
                         f"— package problem, re-select the part")
        elif got != conditional_want or sorted(set(conds_declared)) != sorted(set(conditional_need)):
            probs.append(f"{mpn}: conditional escape requires tier {conditional_want} "
                         f"and conditions {conditional_need}; got {got} / {conds_declared}")
    elif got == want:
        if conds_declared:
            probs.append(f"{mpn}: conditions {conds_declared} declared but "
                         f"tier_required '{got}' is UNCONDITIONAL for this "
                         f"geometry — stale/copied conditions")
    elif got not in tiers:
        probs.append(f"{mpn}: declared tier_required '{got}' is not a tier "
                     f"in fab_tiers.yaml")
    else:
        v, need = grade_tier(style, float(pitch), tiers[got], ews, npins, topology)
        if v == "conditional":
            if sorted(set(conds_declared)) == sorted(set(need)):
                pass  # conditional verdict, EARNED: conditions recorded
            elif not conds_declared:
                probs.append(
                    f"{mpn}: tier_required '{got}' is CONDITIONAL on "
                    f"{need} but the block records no conditions — record "
                    f"conditions: {need} (and honour them on the board) or "
                    f"raise the tier to '{want}'")
            else:
                probs.append(
                    f"{mpn}: recorded conditions {sorted(conds_declared)} "
                    f"do not match the math's {sorted(need)} for tier "
                    f"'{got}'")
        else:
            probs.append(f"{mpn}: declared tier_required '{got}' but the "
                         f"math says '{want}' ({style} @ {pitch}mm"
                         + (f", {ews} escapes worst side" if ews is not None
                            else "")
                         + ") — stale/copied block")
    return probs


# P-LAND's policy is fixed; caller-selected weaker limits are rejected.
REACH_MM = 1.0
DIRS = 48

LAND_FIX_ORDER = (
    "P-LAND FIX ORDER (measured on pluto-rx2-8way, 2026-07-30 — a launch "
    "that will not route is THREE questions):\n"
    "  1. ROUTER GRID, and it is free. At KRT `grid_step: 0.1` NOTHING "
    "routed that board's five boxed RF pads at ANY width (0.30/0.25/0.20 "
    "all fail): the land centres sit at odd multiples of 0.05 mm. At "
    "`grid_step: 0.05` + `clearance: 0.14` the same wave routes 11/11 at "
    "the FULL 0.36 mm.\n"
    "  2. A LAUNCH-LOCAL SCOPED CLEARANCE (a rule area over the land "
    "field). This gate reads `constraint clearance` rule-area relaxations "
    "if they exist.\n"
    "  3. WIDTH — a `scoped_floors:` taper bounded by a rule area, with "
    "the impedance/ampacity argument as its `why:` (pluto-cal-switch "
    "bounds its necks to lambda_g/61).\n"
    "  NOT A REMEDY: router NECK-DOWN. Measured `--neckdown-length 0.3` "
    "routes 11/11 and delivers 149.832 mm of RF copper at 0.25 mm and "
    "0.000 mm at 0.36 — the re-widen pass only restores width where the "
    "narrow-planned path has wide clearance, which leaving a QFN it never "
    "has.\n"
    "  AND THIS GATE DOES NOT CLAIM WIDTH IS WHY A BOARD FAILED TO ROUTE. "
    "The prescribed finite search did not validate a declared-width witness.")


def check_board(board_path, pro_path=None, dru_path=None, dirs=48, reach=1.0, verbose=False):
    """Public census with one explicit eligibility bucket for every copper pad."""
    import json
    from land_witness import BoardContext, Unsupported
    if dirs != 48 or reach != 1.0:
        raise Unsupported('P-LAND requires the fixed 48 directions / 1.0 mm policy')
    c = BoardContext(board_path, pro_path, dru_path)
    stats = dict(copper_pads=len(c.pads)+len(c.unreadable), physical_pads=c.physical,
                 noncopper_pads=c.noncopper, graded=0, failed=0, unreached=len(c.unreadable),
                 no_net=0, no_floor=0, relaxed=0, scoped_clearance=0, pour_fed=0,
                 via_on_pad=0, xcheck=0, xcheck_over=0)
    lines = []; results = {}
    name = c.path.stem
    for p in c.unreadable:
        lines.append(f"UNREACHED {name} {p['ref']}.{p['num']} net={p['net'] or '-'}: {p['why']}")
    for p in c.pads:
        if not p['net']:
            stats['no_net'] += 1; continue
        if not c.declared(p):
            stats['no_floor'] += 1; continue
        center = p['native'].GetPosition()
        if any(net == p['net'] and bool(layers & p['layers']) and poly.Contains(center) for net, layers, poly in c.pours):
            stats['pour_fed'] += 1; continue
        if any(v.GetNetname() == p['net'] and any(layer in set(v.GetLayerSet().CuStack()) and p['shapes'][layer].Collide(v.GetPosition(), 0) for layer in p['layers']) for v in c.vias):
            stats['via_on_pad'] += 1; continue
        stats['graded'] += 1
        # Inventory actual same-net incident tracks at native geometry. They
        # remain outside the finite policy; no inferred maximum comparison.
        incident = [t for t in c.tracks if t.GetNetname() == p['net'] and t.GetLayer() in p['layers'] and (p['shapes'][t.GetLayer()].Collide(t.GetStart(), 0) or p['shapes'][t.GetLayer()].Collide(t.GetEnd(), 0))]
        stats['xcheck'] += bool(incident)
        try:
            result = c.search(p)
        except Unsupported as e:
            result = {'valid': False, 'status': 'UNSUPPORTED', 'reason': str(e)}
        result['incident_tracks_outside_policy'] = [{'uuid': t.m_Uuid.AsString(), 'start_iu': [t.GetStart().x,t.GetStart().y], 'end_iu': [t.GetEnd().x,t.GetEnd().y], 'width_iu': t.GetWidth(), 'layer': c.board.GetLayerName(t.GetLayer())} for t in incident]
        key = p['ref']+'.'+p['num']; results[key] = result
        layer = min(p['layers'])
        diagnostic = c.track(p, (center.x,center.y), (center.x+1000000,center.y), 200000, layer)
        floor, rule = c.resolve('track_width', diagnostic, None, layer)
        if result['valid']:
            floor = result['floor_iu']; rule = result['width_rule']
        stats['relaxed'] += bool(rule and rule.startswith('scoped_'))
        pair = result.get('limiting_pair') or (result.get('last_rejection') or {}).get('limiting_pair') or {}
        stats['scoped_clearance'] += bool(pair.get('rule') and pair['rule'] not in ('native effective classes / board', 'local override'))
        detail = f"{name} {key} net={p['net']} class={p['cls']} floor={floor/1e6:.3f}" if floor is not None else f"{name} {key} net={p['net']} class={p['cls']} floor=candidate-dependent"
        if result['valid']:
            if verbose: lines.append('ok   P-LAND ' + detail + ' ' + json.dumps(result, sort_keys=True))
        else:
            stats['failed'] += 1
            lines.append('FAIL P-LAND ' + detail + ' ' + json.dumps(result, sort_keys=True))
    for note in c.outside: lines.append('scope: ' + note)
    return lines, stats, {'pro': c.pro, 'dru': c.dru, 'rules': len(c.rules), 'results': results, 'native_config': c.native_config, 'epsilon_iu': c.epsilon}


def run_land(args):
    total_bad = 0
    graded_boards = 0
    for bp in args.board:
        if not Path(bp).exists():
            print(f"FAIL P-LAND {bp}: no such board — a board that cannot "
                  f"be read is not a board that passed")
            total_bad += 1
            continue
        try:
            lines, st, inp = check_board(bp, args.project, args.dru,
                                         args.dirs, args.reach, args.verbose)
        except (ValueError, OSError, RuntimeError) as e:
            print(f"FAIL P-LAND UNSUPPORTED {bp}: {e}")
            total_bad += 1
            continue
        graded_boards += 1
        for L in lines:
            print(L)
        # G-INPUT: name every input the verdict depends on.
        print(f"input: board = {Path(bp).resolve()}")
        print(f"input: floors+relaxations = {Path(inp['dru']).resolve()} "
              f"({inp['rules']} width/clearance rule(s))")
        print(f"input: clearances = {Path(inp['pro']).resolve()}")
        print(f"input: native configuration = {inp['native_config']} (DRC epsilon {inp['epsilon_iu']} IU)")
        print("input: model = finite declared widths <=2 mm; adaptive bbox starts "
              "(0.03 mm requested scale, five intervals per axis, <=37 proposals, "
              "1 IU edge inset and native admission); 48 directions; 1 mm reach; "
              "all other-net/no-net pads on enabled copper layers; native clearance tolerance")
        print(f"P-LAND physical census: {st['physical_pads']} physical / "
              f"{st['copper_pads']} copper / {st['noncopper_pads']} noncopper")
        # M-COVER: the denominator, every bucket named.
        print(f"P-LAND denominator {Path(bp).stem}: {st['graded']} graded / "
              f"{st['copper_pads']} copper pads "
              f"({st['no_floor']} no declared width floor, "
              f"{st['pour_fed']} nominal same-net POUR, "
              f"{st['via_on_pad']} native VIA ON THE LAND, "
              f"{st['no_net']} no net, {st['unreached']} UNREACHED); "
              f"{st['relaxed']} graded against a SCOPED floor, "
              f"{st['scoped_clearance']} against a scoped clearance; "
              f"{st['failed']} failing")
        print(f"routed inventory {Path(bp).stem}: {st['xcheck']} graded pad(s) "
              "already carry a same-net track; actual geometry/width inventoried "
              "outside finite witness policy; nominal pours establish no connectivity")
        bad = st["failed"] + st["unreached"]
        if st["graded"] == 0:
            print(f"FAIL P-LAND {Path(bp).stem}: 0 pads graded — no pad on "
                  f"this board resolves a declared track_width floor. A "
                  f"zero denominator is a FAIL, never a pass (canon "
                  f"M-COVER); netclass floors are generated BEFORE routing "
                  f"(canon R1), so 0 means generate_rules has not run.")
            bad += 1
        total_bad += bad
    if total_bad:
        print(LAND_FIX_ORDER)
    verdict = "FAIL" if total_bad else "PASS"
    print(f"P-LAND {verdict}: {graded_boards}/{len(args.board)} board(s) "
          f"graded, {total_bad} problem(s)")
    sys.exit(1 if total_bad else 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="*", help="part.yaml paths")
    ap.add_argument("--board", action="append", default=[],
                    help="P-LAND: validate finite launch witnesses on a "
                         ".kicad_pcb (repeatable)")
    ap.add_argument("--project", help="P-LAND: .kicad_pro (default: the "
                                      "board's own stem)")
    ap.add_argument("--dru", help="P-LAND: .kicad_dru (default: the board's "
                                  "own stem)")
    ap.add_argument("--dirs", type=int, default=DIRS,
                    help=f"P-LAND: launch directions sampled (default {DIRS})")
    ap.add_argument("--reach", type=float, default=REACH_MM,
                    help=f"P-LAND: launch length mm (default {REACH_MM})")
    ap.add_argument("--verbose", action="store_true",
                    help="P-LAND: print the passing pads too")
    ap.add_argument("--style", help="ad-hoc: package style")
    ap.add_argument("--pitch", type=float, help="ad-hoc: pad pitch mm")
    ap.add_argument("--escapes-worst-side", type=int, default=None,
                    help="ad-hoc: escape count on the worst single side "
                         "(enables the conditional-verdict model)")
    ap.add_argument("--pins", type=int, default=None,
                    help="ad-hoc: total pin count (bounds the outward-only "
                         "rescue to the small dual-row QFN class)")
    ap.add_argument("--tiers", default=str(TIERS_PATH))
    args = ap.parse_args()
    if args.board:
        return run_land(args)
    tiers = load_tiers(args.tiers)
    bad = 0

    if args.style and args.pitch:
        ews, npins = args.escapes_worst_side, args.pins
        for name, t in sorted(tiers.items(), key=lambda kv: kv[1]["rank"]):
            v, conds = grade_tier(args.style, args.pitch, t, ews, npins)
            lab = {"ok": "ok",
                   "conditional": "CONDITIONAL on " + ",".join(conds),
                   "no": "INFEASIBLE"}[v]
            print(f"  {name:24s} {lab}")
        req = tier_required(args.style, args.pitch, tiers, ews, npins)
        creq, cconds = tier_conditional(args.style, args.pitch, tiers,
                                        ews, npins)
        print(f"tier_required: {req or 'NONE — re-select the part'}")
        if creq and req and creq != req:
            print(f"tier_conditional: {creq} (conditions: "
                  f"[{', '.join(cconds)}])")
        if req:
            extra = (f", escapes_worst_side: {ews}" if ews is not None else "")
            print(f'escape: {{style: {args.style}, pitch: {args.pitch}'
                  f'{extra}, tier_required: {req}, checked: escape_check}}')
            if creq and creq != req:
                print(f'# cheaper CONDITIONAL form (earn it on the board):\n'
                      f'# escape: {{style: {args.style}, pitch: {args.pitch}'
                      f'{extra}, tier_required: {creq}, conditions: '
                      f'[{", ".join(cconds)}], checked: escape_check}}')
        sys.exit(0 if req else 1)

    # G-COVER: `escape_check.py` with no part arguments printed NOTHING and
    # exited 0 — a green run over zero parts, which is the whole M-COVER
    # class. A shell glob that matched nothing (a renamed 02_parts dir, a
    # wrong cwd) reached exactly this line and read as success.
    if not args.parts:
        print("P-ESC FAIL: 0/0 parts graded — no part.yaml paths were given "
              "(a glob that matched nothing lands here). A zero denominator "
              "is a FAIL, never a pass (canon M-COVER). Pass part.yaml paths, "
              "or use --style/--pitch for the ad-hoc tier table.")
        sys.exit(1)

    graded = 0
    for p in args.parts:
        if not Path(p).exists():
            # G-COVER: a path that does not exist is UNGRADED, and must not be
            # silently absent from the denominator.
            print(f"FAIL {p}: no such part.yaml — a part that cannot be read "
                  f"is not a part that passed")
            bad += 1
            continue
        probs = check_part(p, tiers)
        graded += 1
        for pr in probs:
            print(f"FAIL {pr}")
        bad += len(probs)
        if not probs:
            print(f"ok   {Path(p).parent.name}")
    # G-INPUT: name the tier table too — the verdict depends on it entirely.
    print(f"input: tiers = {Path(args.tiers).resolve()} "
          f"({len(tiers)} tier(s))")
    verdict = "FAIL" if bad else "PASS"
    print(f"P-ESC {verdict}: {graded}/{len(args.parts)} part.yaml graded, "
          f"{bad} problem(s)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
