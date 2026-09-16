#!/usr/bin/env python3
"""Compatibility entry point for the shared configured critical-path checker."""
from pathlib import Path
import os
import sys
PROJECT = Path(__file__).resolve().parents[1]
REPO = Path(os.environ.get("CIRCUITS_ROOT", PROJECT.parents[1]))
sys.path.insert(0, str(REPO / "skills/kicad-pcb/scripts"))
import critical_path_check as shared
AuditError = shared.AuditError
PathResult = shared.PathResult
CONFIG_PATH = PROJECT / "03_src/rules/critical_paths.yaml"
def grade(oracle):
    return shared.grade(oracle, shared.load_config(CONFIG_PATH))
def board_oracle(board_path):
    return shared.board_oracle(board_path, shared.load_config(CONFIG_PATH))
def audit(board_path):
    return shared.audit(board_path, shared.load_config(CONFIG_PATH))
if __name__ == "__main__":
    sys.argv.extend(["--config", str(CONFIG_PATH)])
    raise SystemExit(shared.main())
