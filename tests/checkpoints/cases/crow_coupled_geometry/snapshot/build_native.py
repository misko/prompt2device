#!/usr/bin/env python3
"""Regenerate the synthetic coupled boards for local iteration only.

The checkpoint grader uses its own protected producer and regenerates again;
these local artifacts carry no acceptance authority.
"""
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
root = Path(__file__).resolve().parent
start = (root / ".checkpoint_context/START.md").read_text()
match = re.search(r"Trusted repository \(read-only reference/tools\): `([^`]+)`", start)
if match is None:
    raise SystemExit("checkpoint START.md has no trusted repository path")
case = Path(match.group(1)) / "tests/checkpoints/cases/crow_coupled_geometry"
sys.path.insert(0, str(case))
from native_fixture import build_from_source  # noqa: E402

build_from_source(root, root / "06_build/coupled")
print("wrote 06_build/coupled/prepared.kicad_pcb and witness.kicad_pcb")
