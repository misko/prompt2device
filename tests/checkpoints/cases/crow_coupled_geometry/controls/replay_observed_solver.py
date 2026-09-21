#!/usr/bin/env python3
"""Replay the preserved Sol repair through the documented native gate command."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path


EXPECTED_SOURCE = "8fc61169c623af04b3bd2db3fdc820b6f0667c1385f958c0b525cfdf1b0e906f"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: replay_observed_solver.py REPO WORKSPACE", file=sys.stderr)
        return 2
    repo, workspace = Path(argv[1]).resolve(), Path(argv[2]).resolve()
    here = Path(__file__).resolve().parent
    source = here / "observed_sol_repair.yaml"
    if sha(source) != EXPECTED_SOURCE:
        raise RuntimeError("preserved observed source repair identity changed")
    shutil.copy2(source, workspace / "03_src/route_geometry.yaml")
    shutil.copy2(here / "observed_sol_HANDOFF.md", workspace / "HANDOFF.md")
    build = subprocess.run(["/usr/bin/python3", str(workspace / "build_native.py")],
                           cwd=workspace, text=True, capture_output=True,
                           timeout=60, check=False)
    if build.returncode:
        print(build.stdout + build.stderr, file=sys.stderr)
        return build.returncode
    receipt = workspace / "06_build/coupled/coupled-receipt.json"
    command = [
        "/usr/bin/python3",
        str(repo / "skills/kicad-pcb/scripts/coupled_geometry_preflight.py"),
        "grade", ".", "--prepared",
        "06_build/coupled/prepared.kicad_pcb", "--witness",
        "06_build/coupled/witness.kicad_pcb", "--workspace",
        "06_build/coupled/gate/repair-1", "--json",
        "06_build/coupled/coupled-receipt.json",
    ]
    gate = subprocess.run(command, cwd=workspace, text=True, capture_output=True,
                          timeout=150, check=False)
    if gate.returncode:
        print(gate.stdout + gate.stderr, file=sys.stderr)
        return gate.returncode
    payload = json.loads(receipt.read_text())
    if payload.get("status") != "PASS":
        print("documented solver gate wrote no passing receipt", file=sys.stderr)
        return 1
    print(gate.stdout, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
