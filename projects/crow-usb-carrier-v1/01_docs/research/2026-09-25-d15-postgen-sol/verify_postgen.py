#!/usr/bin/env python3
"""Read-only verification of the stopped D15 post-generation research receipt."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
PRIVATE = PROJECT / "06_build/prototype_board_diagnostic/current-ti-4l-3313a-preflight-20260925"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(ok, message):
    if not ok:
        raise SystemExit("D15_POSTGEN_FAIL: " + message)


receipt = json.loads((HERE / "receipt.json").read_text())
stored = json.loads((HERE / "object_diff.json").read_text())
probe = subprocess.run([sys.executable, str(HERE / "audit.py")], capture_output=True, text=True)
check(probe.returncode == 0, "native object audit: " + probe.stderr[-300:])
check(json.loads(probe.stdout) == stored, "object diff drift")
check(sha(HERE / "object_diff.json") == receipt["object_diff_sha256"], "object receipt hash")
check(sha(PROJECT / "01_docs/research/2026-09-25-d15-preflight-sol/preflight_manifest.json") == receipt["preflight_manifest_sha256"], "preflight manifest")
check(sha(PROJECT / "01_docs/research/2026-09-25-d15-independent-preflight-review-terra.md") == receipt["independent_preflight_review_sha256"], "independent preflight")
for name, key in (("crow_carrier.kicad_pcb", "saved_board_sha256"),
                  ("crow_carrier.kicad_pro", "saved_pro_sha256"),
                  ("crow_carrier.kicad_dru", "saved_dru_sha256")):
    check(sha(PRIVATE / "04_kicad" / name) == receipt[key], "native output " + name)
via_path = PRIVATE / "via_process.json"
drc_path = PRIVATE / "drc_disposable_refill.json"
via = json.loads(via_path.read_text())
drc = json.loads(drc_path.read_text())
check(sha(via_path) == receipt["v_process"]["sha256"], "V-PROCESS hash")
check(via["fails"] == ["TMUX-DRU: foreign clearance/via/hole constraint"], "V-PROCESS result")
check(sha(drc_path) == receipt["native_drc_disposable_refill"]["sha256"], "DRC hash")
check({k: len(drc[k]) for k in ("violations", "unconnected_items", "schematic_parity")} ==
      {"violations": 0, "unconnected_items": 499, "schematic_parity": 0}, "native DRC counts")
check(receipt["status"] == "FAILED_RESEARCH" and receipt["no_retry"] and
      all(receipt[key] is False for key in receipt if key.endswith("_credit")), "no-credit status")
print("D15_POSTGEN_FAILED_RESEARCH_RECEIPT_VERIFIED")
print("Objects unchanged except launch area; native DRC/parity clean; V-PROCESS gate failed.")
