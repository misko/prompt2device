#!/usr/bin/env /usr/bin/python3
"""Consume the signed D19 one-shot attempt and generate only an unrouted board."""
from __future__ import annotations

import hashlib
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
ROOT = HERE.parents[4]
SCRATCH = PROJECT / "06_build/prototype_board_diagnostic/d19-integrated-source-preflight-r3-20260925"
OUTPUT = PROJECT / "06_build/prototype_board_diagnostic/d19-integrated-native-candidate-20260925"
REVIEW = HERE / "independent-preflight-terra.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tree_sha(path: Path) -> str:
    h = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(item.relative_to(path).as_posix().encode() + b"\0")
        h.update(bytes.fromhex(sha(item)))
    return h.hexdigest()


def require(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("D19_GENERATION_REFUSED: " + message)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--preflight-only", action="store_true", help="verify exact packet without reserving or generating")
    args = ap.parse_args()
    manifest_path = SCRATCH / "preflight.json"
    require(manifest_path.is_file(), "missing author packet")
    manifest_sha = sha(manifest_path)
    m = json.loads(manifest_path.read_text())
    require(m["attempt"] == "D19-INTEGRATED-UNROUTED-ONE" and
            m["status"] == "AUTHOR_SOURCE_PREFLIGHT_ONLY" and not m["board_generated"], "attempt/status")
    require(m["generation_recipe_sha256"] == sha(Path(__file__)), "recipe drift")
    require(m["postgen_checker_sha256"] == sha(HERE / "postgen_check.py"), "postgen checker drift")
    require(subprocess.run(["kicad-cli", "version"], check=True, capture_output=True, text=True).stdout.strip() == m["kicad_cli_version"], "KiCad CLI drift")
    import pcbnew
    require(pcbnew.Version() == m["pcbnew_version"], "pcbnew drift")
    require(m["scratch_source_tree_sha256"] == tree_sha(SCRATCH / "03_src"), "scratch source drift")
    require(m["copied_parts_tree_sha256"] == tree_sha(SCRATCH / "02_parts"), "parts drift")
    for key, rel in (("pro", "04_kicad/crow_carrier.kicad_pro"),
                     ("dru", "04_kicad/crow_carrier.kicad_dru"),
                     ("fp_lib_table", "04_kicad/fp-lib-table")):
        require(sha(SCRATCH / rel) == m["copied_sidecar_sha256"][key], "sidecar drift " + key)
    require(sha(SCRATCH / "04_kicad/fp-lib-table") == m["inputs_sha256"]["fp_lib_table"], "library table provenance drift")
    for name, rel in (("circuit", "03_tscircuit/build/circuit.json"),
                      ("netlist", "06_build/netlists/crow_carrier.net")):
        require(sha(SCRATCH / rel) == m["inputs_sha256"][name], "schematic drift " + name)
    require(sha(HERE.parent / "2026-09-25-unadopted-3313a-controlled-pair-sol/native-replay-full-sidecar-independent-terra.json") == m["inputs_sha256"]["pair_controls"], "independent pair controls drift")
    for key, expected in m["p1_packet_sha256"].items():
        require(sha(SCRATCH / "p1_packet" / key) == expected, "P1 packet drift " + key)
    for key, expected in m["generator_checker_sha256"].items():
        rel = {"board_generator": "skills/kicad-pcb/scripts/generate_board_generic.py",
               "rule_generator": "skills/kicad-pcb/scripts/generate_rules_generic.py",
               "pofv_generator": "skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py",
               "via_checker": "skills/jlcpcb-fab/scripts/via_process_check.py",
               "p1_checker": "skills/kicad-pcb/scripts/p1_corridor_capacity.py"}[key]
        require(sha(ROOT / rel) == expected, "tool drift " + key)
    require(not OUTPUT.exists(), "candidate output already exists; no retry")
    require(not (SCRATCH / "generation_claim.json").exists(), "attempt already reserved")
    if args.preflight_only:
        print(json.dumps({"status": "READY_FOR_INDEPENDENT_PREFLIGHT", "preflight_sha256": manifest_sha,
                          "review_signed": REVIEW.is_file() and "D19_PREFLIGHT_PASS" in REVIEW.read_text() and manifest_sha in REVIEW.read_text()}, sort_keys=True))
        return
    require(REVIEW.is_file(), "missing independent preflight review")
    review = REVIEW.read_text()
    require("D19_PREFLIGHT_PASS" in review and manifest_sha in review, "independent review does not sign exact packet")
    claim = SCRATCH / "generation_claim.json"
    fd = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, "w") as handle:
        json.dump({"attempt": m["attempt"], "preflight_sha256": manifest_sha,
                   "review_sha256": sha(REVIEW), "output": str(OUTPUT), "consumed": True}, handle,
                  indent=2, sort_keys=True)
        handle.write("\n")
    OUTPUT.mkdir()
    project = OUTPUT / "project"
    for rel in ("03_src", "02_parts", "03_tscircuit", "06_build/netlists", "04_kicad"):
        shutil.copytree(SCRATCH / rel, project / rel)
    board = project / "04_kicad/crow_carrier.kicad_pcb"
    log = OUTPUT / "generation_commands.jsonl"
    commands = [
        ["/usr/bin/python3", str(ROOT / "skills/kicad-pcb/scripts/generate_board_generic.py"),
         str(project / "03_src/floorplan.yaml"), "--netlist", str(project / "06_build/netlists/crow_carrier.net"),
         "-o", str(board)],
        ["/usr/bin/python3", str(ROOT / "skills/kicad-pcb/scripts/generate_rules_generic.py"), str(project)],
        ["/usr/bin/python3", str(ROOT / "skills/jlcpcb-fab/scripts/generate_tmux4827_pofv.py"),
         str(board), "--assembly", str(project / "03_src/rules/assembly.yaml")],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=project, capture_output=True, text=True)
        with log.open("a") as handle:
            handle.write(json.dumps({"argv": command, "returncode": proc.returncode,
                                     "stdout": proc.stdout, "stderr": proc.stderr}) + "\n")
        require(proc.returncode == 0, "generator failed; attempt consumed; see command log")
    receipt = {"attempt": m["attempt"], "status": "GENERATED_UNREVIEWED_UNROUTED",
               "preflight_sha256": manifest_sha, "review_sha256": sha(REVIEW),
               "board_sha256": sha(board),
               "pro_sha256": sha(board.with_suffix(".kicad_pro")),
               "dru_sha256": sha(board.with_suffix(".kicad_dru")),
               "command_log_sha256": sha(log), "p1_accepted": False, "p2_accepted": False,
               "routing_realized": False, "connector_full": False,
               "fabrication_admitted": False, "order_admitted": False}
    (OUTPUT / "generation_receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
