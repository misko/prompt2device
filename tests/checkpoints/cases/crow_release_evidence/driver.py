#!/usr/bin/env python3
"""Prepare and independently grade the reduced Crow release evidence repair."""
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def emit(outcome, findings=(), evidence=None):
    obj = {"schema": 1, "outcome": outcome,
           "findings": [{"code": c, "message": c} for c in findings]}
    if evidence is not None:
        obj["evidence"] = evidence
    print(json.dumps(obj, sort_keys=True))
    return 0 if outcome == "PASS" else 1


def gate(repo, cand):
    return subprocess.run([sys.executable,
                           str(Path(repo) / "skills/jlcpcb-fab/scripts/release_freshness_check.py"),
                           str(cand)], text=True, capture_output=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    mode, repo, workspace = sys.argv[1:4]
    repo, workspace = Path(repo), Path(workspace)
    if mode == "prepare":
        shutil.copytree(Path(__file__).parent / "snapshot", workspace, dirs_exist_ok=True)
        return emit("PASS", evidence={"prepared": "mutable 06_build candidate"})
    cand = workspace / "06_build/candidates/crow-recorder-v1.0"
    if mode == "reference":
        audit = cand / "verification/policy_audit.md"
        erc = json.loads((cand / "verification/erc.json").read_text())
        warnings = sum(v.get("severity") == "warning"
                       for sheet in erc.get("sheets", [])
                       for v in sheet.get("violations", []))
        with (cand / "fab/bom.csv").open(newline="") as f:
            bom_count = sum(1 for row in csv.reader(f)
                            if any(c.strip() for c in row)) - 1
        audit.write_text(re.sub(r"(S-ERC[^\n]*\()(\d+)( warnings\))",
                                rf"\g<1>{warnings}\g<3>", audit.read_text()))
        manifest = cand / "MANIFEST.txt"
        manifest.write_text(re.sub(r"(ERC 0 errors \()(\d+)( baselined warnings\))",
                                   rf"\g<1>{warnings}\g<3>", manifest.read_text()))
        manifest.write_text(re.sub(r"(bom_source_check PASS \()(\d+)( lines)",
                                   rf"\g<1>{bom_count}\g<3>", manifest.read_text()))
        (cand / "verification/bom_source_check.txt").write_text(
            f"PASS: bom_source_check PASS ({bom_count} lines, every LCSC == source)\n")
        (workspace / "HANDOFF.md").write_text(
            "Ran python3 skills/jlcpcb-fab/scripts/release_freshness_check.py on the mutable candidate.\n\nFRESHNESS: PASS\n")
        return emit("PASS", evidence={"reference_repair": "applied"})
    findings = []
    try:
        if sha(cand / "verification/erc.json") != "4a4b2fa4738a1f4365639d368e264035124248bce259599fc97fc487e3574d21":
            findings.append("ERC-MEASUREMENT-CHANGED")
        if sha(cand / "fab/bom.csv") != "50682b4090f6fb8dbffb3df0e1a20e099bf54010a2ee9f4de30339c43f581ad7":
            findings.append("BOM-MEASUREMENT-CHANGED")
        manifest = (cand / "MANIFEST.txt").read_text()
        audit = (cand / "verification/policy_audit.md").read_text()
        erc = json.loads((cand / "verification/erc.json").read_text())
        warnings = sum(v.get("severity") == "warning"
                       for sheet in erc.get("sheets", [])
                       for v in sheet.get("violations", []))
        bom_file = cand / "fab/bom.csv"
        with bom_file.open(newline="") as f:
            bom_count = sum(1 for row in csv.reader(f) if any(c.strip() for c in row)) - 1
        audit_m = re.search(r"S-ERC[^\n]*\((\d+) warnings\)", audit)
        manifest_m = re.search(r"ERC 0 errors \((\d+) baselined warnings\)", manifest)
        bom_m = re.search(r"bom_source_check PASS \((\d+) lines", manifest)
        if not audit_m or int(audit_m.group(1)) != warnings:
            findings.append("ERC-AUDIT-STALE")
        if not manifest_m or int(manifest_m.group(1)) != warnings:
            findings.append("ERC-MANIFEST-STALE")
        if not bom_m or int(bom_m.group(1)) != bom_count:
            findings.append("BOM-MANIFEST-STALE")
        bom_evidence = (cand / "verification/bom_source_check.txt").read_text()
        if str(bom_count) not in bom_evidence:
            findings.append("BOM-CHECK-STALE")
        report = cand / "verification/freshness_report.txt"
    except Exception:
        findings.append("CANDIDATE-INPUT-INVALID")
        report = cand / "verification/freshness_report.txt"
    checked = gate(repo, cand)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(checked.stdout + checked.stderr)
    if checked.returncode != 0 or "FRESHNESS: PASS" not in checked.stdout:
        findings.append("RELEASE-FRESHNESS-FAIL")
    if findings:
        return emit("FAIL", findings, {"checker_rc": checked.returncode,
                                        "checker_output": checked.stdout[-2000:]})
    return emit("PASS", evidence={"checker": "FRESHNESS: PASS",
                                   "report": str(report.relative_to(workspace))})


if __name__ == "__main__":
    sys.exit(main())
