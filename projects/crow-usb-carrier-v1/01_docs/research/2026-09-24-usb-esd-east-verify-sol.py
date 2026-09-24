#!/usr/bin/env python3
"""Fail-closed check of the pinned USB ESD east-move replay.

Arguments: baseline project, trial project, absolute generator script, P1
requirements YAML. Each project has 03_src/floorplan.yaml, the netlist,
04_kicad/crow_carrier.kicad_pcb; the trial has drc_baseline.json and
drc_variant.json from the paired diagnostic DRC command in the research note.
"""

import collections
import hashlib
import json
import sys
from pathlib import Path

import pcbnew
import yaml


EXPECTED = {
    "generator": "8a5fa1d48d80138458601a097ab6260565841510a498e44cb9c5773652215b3c",
    "baseline_floorplan": "cd52893214a87432b99bab41827a64680bd8a2f970342f126260157948b50925",
    "trial_floorplan": "9fa1bd656eac8e8f71a12a01677464ecef729dd169cf0ed3d8c9520c1a888b55",
    "netlist": "e7ef7dbd752b9431ade0933ca77ee998963bfe3871c3caf65cddc56442f1371d",
    "project_rules": "3d1cb7206c4101b1be96ee85e994a5e694ef871a47f6356a70bdfa1576641cf1",
    "fp_lib_table": "5601fde400e769f779b9b51b9ed00508c53182a188e75c031549ce14bf4098b0",
    "parts_manifest": "a9489b919a577046abaac033837dfd0105a678592b548d395ad77b291a1c6da4",
    "lib_manifest": "0a2c611f6eefcfedd17461d13bfb41ad1ecc29c9f36bd01ffd42fe4b0bf881d5",
    "baseline_board": "fbfb3bda95f1ddc98e7d3d229550644d136dc7d6349ba19a4023eb13b07e7e27",
    "trial_board": "048272d20c8af90b3ce37a2b9950708b08d6e2d3cbf35ce845738911a097dab2",
}
USB_SUPPORT = (
    "C_USB_VBUS", "R_USB_CC1", "R_USB_CC2", "R_USB_VBUS_BLEED",
    "U_USB_CC_ESD", "U_USB_ESD", "U_USB_VBUS_ESD",
)


def require_hash(key, path):
    got = hashlib.sha256(path.read_bytes()).hexdigest()
    if got != EXPECTED[key]:
        raise SystemExit(f"{key} SHA-256 mismatch: {got} ({path})")


def require_tree(key, project, subtree):
    files = sorted(p for p in (project / subtree).rglob("*") if p.is_file())
    manifest = "".join(p.relative_to(project).as_posix() + " " +
                       hashlib.sha256(p.read_bytes()).hexdigest() + "\n"
                       for p in files).encode()
    got = hashlib.sha256(manifest).hexdigest()
    if got != EXPECTED[key]:
        raise SystemExit(f"{key} manifest mismatch: {got} ({project / subtree})")


def check(condition, message):
    if not condition:
        raise SystemExit(message)


def bbox_mm(box):
    return tuple(round(x / 1_000_000, 6) for x in
                 (box.GetX(), box.GetY(), box.GetRight(), box.GetBottom()))


def overlaps(a, b):
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def contains(a, b):
    return a[0] <= b[0] and a[1] <= b[1] and b[2] <= a[2] and b[3] <= a[3]


def pose(fp):
    return (fp.GetPosition().x, fp.GetPosition().y, fp.GetOrientationDegrees())


def pad_identity(fp):
    return sorted((p.GetNumber(), p.GetNetname()) for p in fp.Pads())


def models(fp):
    return [(m.m_Filename, str(m.m_Offset), str(m.m_Rotation),
             str(m.m_Scale), m.m_Show) for m in fp.Models()]


def courtyard(fp):
    return bbox_mm(fp.GetCourtyard(pcbnew.F_CrtYd).BBox(0))


def main(base, trial, generator, requirements):
    require_hash("generator", generator)
    require_hash("baseline_floorplan", base / "03_src/floorplan.yaml")
    require_hash("trial_floorplan", trial / "03_src/floorplan.yaml")
    for project in (base, trial):
        require_hash("netlist", project / "06_build/netlists/crow_carrier.net")
        require_hash("project_rules", project / "04_kicad/crow_carrier.kicad_pro")
        require_hash("fp_lib_table", project / "04_kicad/fp-lib-table")
        require_tree("parts_manifest", project, "02_parts")
        require_tree("lib_manifest", project, "03_src/lib")
    require_hash("baseline_board", base / "04_kicad/crow_carrier.kicad_pcb")
    require_hash("trial_board", trial / "04_kicad/crow_carrier.kicad_pcb")
    a = {f.GetReference(): f for f in pcbnew.LoadBoard(str(base / "04_kicad/crow_carrier.kicad_pcb")).GetFootprints()}
    b = {f.GetReference(): f for f in pcbnew.LoadBoard(str(trial / "04_kicad/crow_carrier.kicad_pcb")).GetFootprints()}
    check(len(a) == len(b) == 569 and set(a) == set(b), "footprint ref set changed")
    changed = {ref: (pose(a[ref]), pose(b[ref])) for ref in a if pose(a[ref]) != pose(b[ref])}
    check(changed == {"U_USB_ESD": ((217000000, 36000000, 0.0), (217300000, 36000000, 0.0))}, "unexpected pose delta")
    check(all(pad_identity(a[ref]) == pad_identity(b[ref]) and models(a[ref]) == models(b[ref]) for ref in a), "pad/net or model identity changed")
    check(sum(len(f.Pads()) for f in b.values()) == 1872, "pad denominator changed")
    fixed = yaml.safe_load(requirements.read_text())["p1_fixed_refs"]
    check(len(fixed) == 27 and all(pose(a[ref]) == pose(b[ref]) for ref in fixed), "fixed-ref pose changed")
    regions = yaml.safe_load((trial / "03_src/floorplan.yaml").read_text())["placement"]["regions"]
    usb, debug = regions["usb_frontend"], regions["debug_connector"]
    check(usb == [216.3, 29.2, 238.5, 40] and debug == [221, 40, 238, 65], "region geometry changed")
    check(all(contains(usb, courtyard(b[ref])) for ref in USB_SUPPORT), "USB support courtyard outside region")
    check(not contains(usb, courtyard(b["J_USB"])) and contains(debug, courtyard(b["J_JTAG"])), "connector ownership finding changed")
    check(all(not overlaps(candidate, region) for name, candidate in
               (("usb_frontend", usb), ("debug_connector", debug))
               for other, region in regions.items() if other != name), "source regions overlap")
    strip = (221, 65, 226, 84)
    check(all(not overlaps(strip, region) for region in regions.values()), "JTAG strip crosses source region")
    for fp in b.values():
        shapes = [bbox_mm(fp.GetBoundingBox(False, False)), courtyard(fp)]
        shapes.extend(bbox_mm(pad.GetBoundingBox()) for pad in fp.Pads())
        check(not any(overlaps(strip, shape) for shape in shapes), f"JTAG strip meets {fp.GetReference()}")
    drc = [json.loads((trial / f"drc_{name}.json").read_text()) for name in ("baseline", "variant")]
    check(len(drc[0]["violations"]) == len(drc[1]["violations"]) == 263, "DRC violation count changed")
    check(collections.Counter(json.dumps(v, sort_keys=True) for v in drc[0]["violations"]) == collections.Counter(json.dumps(v, sort_keys=True) for v in drc[1]["violations"]), "DRC violations differ")
    check(len(drc[0]["unconnected_items"]) == len(drc[1]["unconnected_items"]) == 499, "unconnected denominator changed")
    check(not drc[0]["schematic_parity"] and not drc[1]["schematic_parity"], "schematic parity issue")
    print("PASS pinned generator/source/board; one pose; 27 fixed; 1872 pads/models; seven USB supports; clear JTAG strip; identical 263 DRC violations")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("usage: verify.py BASE_PROJECT TRIAL_PROJECT GENERATOR_PY P1_REQUIREMENTS_YAML")
    main(*(Path(x) for x in sys.argv[1:]))
