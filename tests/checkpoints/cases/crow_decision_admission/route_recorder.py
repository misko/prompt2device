#!/usr/bin/env python3
"""Disposable command recorder: runs only after exact native admission PASS."""
import json
import sys
from pathlib import Path

output, report_path = map(Path, sys.argv[1:3])
report = json.loads(report_path.read_text())
if report.get("status") != "PASS" or report.get("phase") != "native":
    raise SystemExit("route recorder refuses a nonpassing native admission")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({
    "schema": 1,
    "command": "disposable-route-recorder",
    "admission_sha256": __import__("hashlib").sha256(
        report_path.read_bytes()).hexdigest(),
    "production_complete": False,
}, indent=2, sort_keys=True) + "\n")
