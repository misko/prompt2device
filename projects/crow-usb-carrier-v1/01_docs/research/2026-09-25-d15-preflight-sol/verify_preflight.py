#!/usr/bin/env python3
"""Read-only, hash-bound D15 copied-source preflight; never builds a board."""

import difflib
import hashlib
import json
from pathlib import Path
import subprocess

import pcbnew
import yaml


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
WORKTREE = PROJECT.parents[1]
MANIFEST = json.loads((HERE / "preflight_manifest.json").read_text())


def require(condition, message):
    if not condition:
        raise SystemExit("PREFLIGHT_FAIL: " + message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_files(base, entries, label):
    for relative, expected in entries.items():
        path = base / relative
        require(path.is_file(), f"{label} missing {relative}")
        require(digest(path) == expected, f"{label} hash drift {relative}")


def file_map(base):
    return {str(p.relative_to(base)): digest(p) for p in base.rglob("*") if p.is_file()}


def tree_digest(base):
    # Matches the project's native parity probe: path + NUL + raw SHA-256 bytes.
    h = hashlib.sha256()
    for relative, sha in sorted(file_map(base).items()):
        h.update(relative.encode() + b"\0")
        h.update(bytes.fromhex(sha))
    return h.hexdigest()


reference = PROJECT / MANIFEST["reference"]
prepared = PROJECT / MANIFEST["prepared"]
require(MANIFEST["status"] == "PREFLIGHT_ONLY_NO_GENERATION", "status")
for field in ("generation_executed", "route_executed", "stage_credit", "independent_preflight_signed"):
    require(MANIFEST[field] is False, field)
check_files(reference, MANIFEST["reference_files_sha256"], "reference")
check_files(prepared, MANIFEST["prepared_files_sha256"], "prepared")
check_files(PROJECT, MANIFEST["authority_sha256"], "authority")
for relative, expected in MANIFEST["generators_sha256"].items():
    path = (PROJECT if relative.startswith("03_src/") else WORKTREE) / relative
    require(path.is_file() and digest(path) == expected, f"generator drift {relative}")
require(digest(HERE / "source_diff.patch") == MANIFEST["source_diff_sha256"], "diff receipt drift")
for name in ("lib", "parts"):
    rel = "03_src/lib" if name == "lib" else "02_parts"
    for label, base in (("reference", reference), ("prepared", prepared)):
        require(tree_digest(base / rel) == MANIFEST[f"{label}_{name}_tree_sha256"], f"{label} {name} tree drift")

before = file_map(reference / "03_src")
after = file_map(prepared / "03_src")
require(before.keys() == after.keys(), "03_src file set drift")
changed = sorted("03_src/" + p for p in before if before[p] != after[p])
require(changed == MANIFEST["changed_source_files"], f"source changes {changed}")
require(file_map(reference / "04_kicad") == file_map(prepared / "04_kicad"), "native output changed before generation")
version = subprocess.run(["kicad-cli", "version"], capture_output=True, text=True, check=True).stdout.strip()
require(version == MANIFEST["kicad_cli_version"], f"KiCad version {version}")
board = pcbnew.LoadBoard(str(reference / "04_kicad/crow_carrier.kicad_pcb"))
xu = [fp for fp in board.GetFootprints() if fp.GetReference() == "U_XU"]
require(len(xu) == 1, "native U_XU identity")
for number, expected in MANIFEST["native_xu_pad_bbox_mm"].items():
    pads = [pad for pad in xu[0].Pads() if pad.GetNumber() == number]
    require(len(pads) == 1, f"native U_XU.{number} identity")
    box = pads[0].GetBoundingBox()
    observed = [round(pcbnew.ToMM(v), 6) for v in (box.GetX(), box.GetY(), box.GetRight(), box.GetBottom())]
    require(observed == expected, f"native U_XU.{number} box {observed}")

diff = []
for rel in changed:
    a = (reference / rel).read_text().splitlines(keepends=True)
    b = (prepared / rel).read_text().splitlines(keepends=True)
    diff.extend(difflib.unified_diff(a, b, fromfile="frozen/" + rel, tofile="prepared/" + rel))
require("".join(diff).encode() == (HERE / "source_diff.patch").read_bytes(), "source diff mismatch")

floor = yaml.safe_load((prepared / "03_src/floorplan.yaml").read_text())
oldfloor = yaml.safe_load((reference / "03_src/floorplan.yaml").read_text())
stack = floor["board"]["stackup"]
require(floor["board"]["outline"] == oldfloor["board"]["outline"], "outline changed")
require(stack["nominal_thickness_mm"] == 1.58 and stack["thickness_tolerance_mm"] == 0.158, "thickness")
require(stack["copper_thickness_mm"] == oldfloor["board"]["stackup"]["copper_thickness_mm"], "copper")
require([d["thickness_mm"] for d in stack["dielectrics"]] == [0.2064, 1.065, 0.2064], "dielectric thickness")
require([d["epsilon_r"] for d in stack["dielectrics"]] == [4.1, 4.38, 4.1], "dielectric Er")
areas = floor.get("keepouts", [])
require(len(areas) == len(oldfloor.get("keepouts", [])) + 1, "area count")
area = [a for a in areas if a.get("name") == "usb_pair_xu_launch"]
require(len(area) == 1 and area[0] == {"name": "usb_pair_xu_launch", "layers": ["F.Cu"], "deny": [], "rect": MANIFEST["allowed_area_bbox_mm"]}, "exact launch area")

nets = yaml.safe_load((prepared / "03_src/rules/nets.yaml").read_text())
usb = nets["classes"]["USB_HS"]
require(usb["nets"] == ["USB_DP", "USB_DN"], "USB nets")
require(usb["min_width"] == "0.180mm" and usb["clearance"] == "0.150mm", "USB widths/foreign clearance")
require(usb["diff_pair"] == {"width": "0.180mm", "gap": "0.100mm"}, "USB pair geometry")
scoped = nets["scoped_clearances"]
require(len(scoped) == 1, "scoped clearance count")
require({k: scoped[0][k] for k in ("zone", "nets_a", "nets_b", "clearance")} == {"zone": "usb_pair_xu_launch", "nets_a": ["USB_DP"], "nets_b": ["USB_DN"], "clearance": "0.100mm"}, "scoped pair clearance")

rf = yaml.safe_load((prepared / "03_src/rules/rf.yaml").read_text())
rf_text = (prepared / "03_src/rules/rf.yaml").read_text()
require("PRIVATE_UNROUTED_SCREEN" in rf_text and "JLC04161H-3313A" in rf_text, "RF hypothesis")
require("89.611" not in rf_text and "selected JLC stack" not in rf_text, "stale performance claim")
require("89.9172598796" in rf_text and "no named-stack" in rf_text, "numeric qualification")
require(rf is not None, "RF parse")

print("PREFLIGHT_CONTENT_CHECK_PASS")
print("Source files changed:", ", ".join(changed))
print("Generator not run; independent preflight signature still required.")
