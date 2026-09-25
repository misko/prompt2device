#!/usr/bin/env python3
"""Regenerate and check the isolated ADC7 four-part source/silk candidate."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

try:
    import pcbnew as pcb
except ImportError:
    sys.path.append("/usr/lib/python3/dist-packages")
    import pcbnew as pcb

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
PROJECT = ROOT / "projects/crow-usb-carrier-v1"
PACKET = PROJECT / "06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project"
PREVIOUS = PROJECT / "01_docs/research/2026-09-25-ti-adc7-four-part-margin-sol/candidate.kicad_pcb"
PREVIOUS_SHA = "046019a13094764baef313d62611b137e0f0af971079734c71ab050dbf46b3a0"
SILK_REFS = {
    "C_ADC_CLOCK_OK", "C_ADC_CM7N", "C_ADC_I2C_A", "C_ADC_I2C_B",
    "C_AUDIO_OSC", "C_CORE_OK", "C_U_CORE_OUT_1", "R_1V8_FB_TOP",
    "R_3V3X_FB_BOTTOM", "R_TDM_OE_PU", "U_ADC_CLOCK_OK", "U_ADC_I2C_XLATE",
    "R_ADC_PD7N",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*argv: str, log: Path | None = None) -> None:
    proc = subprocess.run(argv, text=True, capture_output=True)
    if log:
        log.write_text(proc.stdout + proc.stderr)
    if proc.returncode:
        raise RuntimeError(f"{argv[0]} returned {proc.returncode}: {proc.stderr[-1000:]}")


def footprints(board):
    return {f.GetReference(): f for f in board.GetFootprints()}


def pose(f):
    q = f.GetPosition()
    return q.x, q.y, round(f.GetOrientationDegrees(), 6)


def pad_identity(f):
    return sorted((p.GetNumber(), p.GetNetname(), tuple(sorted(p.GetLayerSet().Seq()))) for p in f.Pads())


def main() -> None:
    if sha(PREVIOUS) != PREVIOUS_SHA:
        raise RuntimeError("four-part candidate SHA drift")
    overlay = json.loads((HERE / "source_overlay.json").read_text())
    fixed = yaml.safe_load((PACKET / "03_src/rules/p1_corridor_requirements.yaml").read_text())["p1_fixed_refs"]
    original = footprints(pcb.LoadBoard(str(PREVIOUS)))
    if len(fixed) != 27:
        raise RuntimeError("fixed-ref count drift")

    with tempfile.TemporaryDirectory(prefix="crow-adc7-source-silk-") as dirname:
        tmp = Path(dirname)
        shutil.copytree(PACKET / "03_src", tmp / "03_src")
        (tmp / "02_parts").symlink_to(PACKET / "02_parts", target_is_directory=True)
        native = tmp / "04_kicad"
        native.mkdir()
        for name in ("crow_carrier.kicad_pro", "crow_carrier.kicad_dru"):
            shutil.copy2(PACKET / "04_kicad" / name, native / name)

        floorpath = tmp / "03_src/floorplan.yaml"
        floor = yaml.safe_load(floorpath.read_text())
        floor["placement"]["post_anchors"].update(overlay["post_anchors"])
        priorities = floor["silk"]["refdes"]["priority_refs"]
        floor["silk"]["refdes"]["priority_refs"] = overlay["prepend_priority_refs"] + [
            ref for ref in priorities if ref not in overlay["prepend_priority_refs"]
        ]
        floorpath.write_text(yaml.safe_dump(floor, sort_keys=False))
        target = native / "crow_carrier.kicad_pcb"
        generation_log = tmp / "generator.log"
        run("/usr/bin/python3", str(ROOT / "skills/kicad-pcb/scripts/generate_board_generic.py"),
            str(floorpath), "--netlist", str(PACKET / "06_build/netlists/crow_carrier.net"),
            "-o", str(target), log=generation_log)
        run("/usr/bin/python3", str(ROOT / "skills/kicad-pcb/scripts/generate_rules_generic.py"),
            str(tmp))
        run("/usr/bin/python3", str(ROOT / "skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py"),
            str(target), "--assembly", str(tmp / "03_src/rules/assembly.yaml"))
        drcpath = tmp / "drc.json"
        run("kicad-cli", "pcb", "drc", "--severity-all", "--refill-zones", "--format", "json",
            "--output", str(drcpath), str(target))
        drc = json.loads(drcpath.read_text())
        if drc["violations"] or len(drc["unconnected_items"]) != 499:
            raise RuntimeError("native DRC or unconnected denominator changed")

        made = footprints(pcb.LoadBoard(str(target)))
        if set(made) != set(original):
            raise RuntimeError("reference-set drift")
        pose_changes = [ref for ref in made if pose(made[ref]) != pose(original[ref])]
        pad_changes = [ref for ref in made if pad_identity(made[ref]) != pad_identity(original[ref])]
        if pose_changes or pad_changes:
            raise RuntimeError(f"footprint/pad drift: poses={pose_changes[:5]}, pads={pad_changes[:5]}")
        if any(made[ref].Reference().GetLayer() != pcb.F_SilkS or not made[ref].Reference().IsVisible()
               for ref in SILK_REFS):
            raise RuntimeError("warning-involved refdes absent from F.SilkS")

        ownership = {}
        rx = re.compile(r"WARN silk ownership: refdes '([^']+)' for (\S+) lands (\d+\.\d+)mm "
                        r"from \S+ but (\d+\.\d+)mm from (\S+) \(lead (-?\d+\.\d+)mm\)")
        for line in generation_log.read_text().splitlines():
            match = rx.search(line)
            if match and match.group(2) in SILK_REFS:
                _, ref, own, other_distance, other, lead = match.groups()
                ownership[ref] = {"own_mm": float(own), "nearest_other_ref": other,
                                  "other_mm": float(other_distance), "lead_mm": float(lead)}
        shutil.copy2(target, HERE / "candidate.kicad_pcb")
        receipt = {
            "source_packet": str(PACKET.relative_to(ROOT)),
            "source_floorplan_sha256": sha(PACKET / "03_src/floorplan.yaml"),
            "source_netlist_sha256": sha(PACKET / "06_build/netlists/crow_carrier.net"),
            "four_part_input_sha256": PREVIOUS_SHA,
            "generated_board_sha256": sha(target),
            "footprint_count": len(made),
            "fixed_ref_count": len(fixed),
            "all_footprint_poses_identical_to_four_part": True,
            "all_pad_net_layer_identities_identical_to_four_part": True,
            "warning_involved_refdes_visible_on_f_silks": sorted(SILK_REFS),
            "native_drc_violations": len(drc["violations"]),
            "unconnected_items": len(drc["unconnected_items"]),
            "affected_refdes_with_ambiguous_ownership": ownership,
            "source_only_reproduction": True,
            "p2_placement_accepted": False,
        }
        (HERE / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
