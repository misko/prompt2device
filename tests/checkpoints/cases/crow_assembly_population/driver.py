#!/usr/bin/env python3
"""Prepare and independently grade the reduced Crow A-POP candidate."""
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def emit(outcome, findings=(), evidence=None, rc=None):
    obj = {"schema": 1, "outcome": outcome,
           "findings": [{"code": c, "message": c} for c in findings]}
    if evidence is not None:
        obj["evidence"] = evidence
    print(json.dumps(obj, sort_keys=True))
    return rc if rc is not None else (0 if outcome == "PASS" else 1)


def run(repo, workspace):
    root = Path(workspace)
    cand = root / "06_build/candidates/crow-assembly-v1.3"
    src = root / "03_src/rules/assembly.yaml"
    args = [sys.executable, str(Path(repo) / "skills/jlcpcb-fab/scripts/assembly_coverage.py"),
            str(cand), "--assembly", str(src),
            "--board", str(cand / "source/crow_recorder_central_v2.kicad_pcb"),
            "--cpl", str(cand / "fab/cpl.csv"), "--bom", str(cand / "fab/bom.csv"),
            "--manifest", str(cand / "MANIFEST.txt")]
    return subprocess.run(args, text=True, capture_output=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    mode, repo, workspace = sys.argv[1:4]
    repo, workspace = Path(repo), Path(workspace)
    if mode == "prepare":
        shutil.copytree(Path(__file__).parent / "snapshot", workspace, dirs_exist_ok=True)
        return emit("PASS", evidence={"prepared": "mutable 06_build candidate"})
    if mode == "reference":
        (workspace / "03_src/rules/assembly.yaml").write_text(
            "service: standard\nsides: [top]\nfiducials: none\n"
            "consigned:\n  - refs: [U1]\n"
            '    evidence: "Crow v1.3 U1 is XU316 C6938291 supplied on consignment; archived 2026-07-24"\n'
            '    disposition: "Supply U1 to JLC for automated placement"\n')
        (workspace / "06_build/candidates/crow-assembly-v1.3/MANIFEST.txt").write_text(
            "board: crow_recorder_central_v2\nversion: v1.3\nnot_assembled:\n")
        (workspace / "HANDOFF.md").write_text(
            "Ran python3 skills/jlcpcb-fab/scripts/assembly_coverage.py on the mutable candidate.\n\nA-POP: PASS\n")
        return emit("PASS", evidence={"reference_repair": "applied"})
    p = workspace / "06_build/candidates/crow-assembly-v1.3"
    findings = []
    try:
        pinned = {
            "source/crow_recorder_central_v2.kicad_pcb": "4cb5d9da4dfe4efa1c789b588ee745bc958cebb0d495e1cdc884192a5dafa135",
            "fab/cpl.csv": "1bc9082de88339b3eeee6af72fc700d90281835c0e93816cf26769ea5c375ebd",
            "fab/bom.csv": "1ab5cfbd7f40349fe938a3c60ea51c0333d0cb57c47bea522b0c4c788245ee1f",
        }
        if any(sha(p / rel) != digest for rel, digest in pinned.items()):
            findings.append("POPULATION-PREMISES-CHANGED")
        if not re.search(r'\(property\s+"Reference"\s+"U1"',
                         (p / "source/crow_recorder_central_v2.kicad_pcb").read_text()):
            findings.append("U1-BOARD-FOOTPRINT-MISSING")
        import yaml
        policy = yaml.safe_load((workspace / "03_src/rules/assembly.yaml").read_text()) or {}
        consigned = {r for e in policy.get("consigned", []) for r in e.get("refs", [])}
        unpop = {r for e in policy.get("not_assembled", []) for r in e.get("refs", [])}
        with (p / "fab/cpl.csv").open(newline="") as f:
            placed = {r.strip() for row in csv.DictReader(f)
                      for r in row.get("Designator", "").split(",") if r.strip()}
        with (p / "fab/bom.csv").open(newline="") as f:
            bom_refs = {r.strip() for row in csv.DictReader(f)
                        for r in row.get("Designator", "").split(",") if r.strip()}
        if "U1" not in consigned or "U1" not in placed or "U1" not in bom_refs:
            findings.append("U1-POPULATION-SOURCE")
        if "U1" in unpop:
            findings.append("U1-MISDECLARED-UNPOPULATED")
        if any(len(str(e.get("evidence", ""))) < 20 or not e.get("disposition")
               for e in policy.get("consigned", []) if "U1" in e.get("refs", [])):
            findings.append("U1-CONSIGN-EVIDENCE")
        line = next((x.split(":",1)[1].strip() for x in (p / "MANIFEST.txt").read_text().splitlines()
                     if x.lstrip().startswith("not_assembled:")), None)
        if line not in ("", None):
            findings.append("MANIFEST-POPULATION-DRIFT")
    except Exception:
        findings.append("CANDIDATE-INPUT-INVALID")
    check = run(repo, workspace)
    report = p / "verification/assembly_coverage.txt"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(check.stdout + check.stderr)
    if check.returncode != 0:
        findings.append("A-POP-CHECK-FAIL")
    if findings:
        return emit("FAIL", findings, {"checker_rc": check.returncode,
                                        "checker_output": check.stdout[-2000:]})
    return emit("PASS", evidence={"checker": "A-POP PASS", "report": str(report.relative_to(workspace))})


if __name__ == "__main__":
    sys.exit(main())
