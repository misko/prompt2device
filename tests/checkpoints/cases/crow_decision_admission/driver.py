#!/usr/bin/env python3
"""Prepare, control, and independently grade Crow decision admission."""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml


HERE = Path(__file__).resolve().parent


def emit(outcome, findings=(), evidence=None, rc=None):
    obj = {"schema": 1, "outcome": outcome,
           "findings": [{"code": code, "message": message}
                        for code, message in findings]}
    if evidence is not None:
        obj["evidence"] = evidence
    print(json.dumps(obj, sort_keys=True))
    return rc if rc is not None else (0 if outcome == "PASS" else 1)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def generate_circuit(workspace):
    return subprocess.run([sys.executable, str(workspace / "build_circuit.py")],
                          cwd=workspace, text=True, capture_output=True)


def admission(repo, workspace):
    report = workspace / "06_build/decision_admission.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "/usr/bin/python3",
        str(repo / "skills/pcb-design/scripts/design_decision_admission.py"),
        str(workspace), "--phase", "native",
        "--board", "04_kicad/crow_decision_coupon.kicad_pcb",
        "--locked-route", "03_src/reviews/accepted-route.yaml",
        "--require-locked-route",
        "--locked-nets", "03_src/reviews/accepted-nets.yaml",
        "--require-locked-nets", "--json", str(report),
    ]
    return subprocess.run(command, cwd=workspace, text=True, capture_output=True), report


def apply_reference(workspace):
    source = workspace / "03_tscircuit/src/components.json"
    rows = json.loads(source.read_text())
    next(row for row in rows if row["ref"] == "U1")["jlc"] = "C200"
    source.write_text(json.dumps(rows, indent=2) + "\n")
    floorplan = workspace / "03_src/floorplan.yaml"
    floorplan.write_text(floorplan.read_text().replace('pad: "9"', 'pad: "1"'))
    nets_path = workspace / "03_src/rules/nets.yaml"
    nets = yaml.safe_load(nets_path.read_text())
    nets["length_match"]["MCH_INPUT_SECTIONS"]["no_vias"] = True
    nets_path.write_text(yaml.safe_dump(nets, sort_keys=False))
    generated = generate_circuit(workspace)
    if generated.returncode:
        raise RuntimeError(generated.stdout + generated.stderr)
    (workspace / "HANDOFF.md").write_text(
        "Reconciled component ownership, current connector anchor, and the "
        "reviewed MCH_INPUT_SECTIONS no-via contract.\n\n"
        "Run native D-DESIGN-ADMISSION before routing.\n")


def apply_bypass(workspace):
    apply_reference(workspace)
    nets_path = workspace / "03_src/rules/nets.yaml"
    nets = yaml.safe_load(nets_path.read_text())
    del nets["length_match"]["MCH_INPUT_SECTIONS"]
    nets_path.write_text(yaml.safe_dump(nets, sort_keys=False))
    (workspace / "HANDOFF.md").write_text(
        "Deleted the protected group to make the current file appear unconstrained; "
        "the independent lock must reject this shortcut.\n")


def fix_floor_and_nets(workspace):
    floorplan = workspace / "03_src/floorplan.yaml"
    floorplan.write_text(floorplan.read_text().replace('pad: "9"', 'pad: "1"'))
    nets_path = workspace / "03_src/rules/nets.yaml"
    nets = yaml.safe_load(nets_path.read_text())
    nets["length_match"]["MCH_INPUT_SECTIONS"]["no_vias"] = True
    nets_path.write_text(yaml.safe_dump(nets, sort_keys=False))


def apply_generated_bypass(workspace):
    fix_floor_and_nets(workspace)
    circuit_path = workspace / "03_tscircuit/build/circuit.json"
    circuit = json.loads(circuit_path.read_text())
    next(row for row in circuit
         if row.get("type") == "source_component" and row.get("name") == "U1")[
             "supplier_part_numbers"] = {"jlcpcb": ["C200"]}
    circuit_path.write_text(json.dumps(circuit, indent=2, sort_keys=True) + "\n")
    (workspace / "HANDOFF.md").write_text(
        "Edited generated Circuit JSON without repairing its source; must fail.\n")


def apply_manual_bypass(workspace):
    fix_floor_and_nets(workspace)
    assembly = workspace / "03_src/rules/assembly.yaml"
    assembly.write_text(
        "schema: 1\nservice: JLCPCB_PCBA\nsides: [top]\nfiducials: none\n"
        "build_quantity: 5\nnot_assembled:\n"
        "  - refs: [U1]\n"
        "    reason: user_supplied\n"
        "    evidence: '2026-09-20 reduced case manual shortcut'\n"
        "    disposition: 'Hand fit instead of required machine placement'\n"
        "consigned: []\n")
    generated = generate_circuit(workspace)
    if generated.returncode:
        raise RuntimeError(generated.stdout + generated.stderr)
    (workspace / "HANDOFF.md").write_text(
        "Changed required U1 machine placement to manual; must fail case policy.\n")


def apply_side_bypass(workspace):
    apply_reference(workspace)
    assembly_path = workspace / "03_src/rules/assembly.yaml"
    assembly = yaml.safe_load(assembly_path.read_text())
    assembly["sides"] = ["top", "bottom"]
    assembly_path.write_text(yaml.safe_dump(assembly, sort_keys=False))
    (workspace / "HANDOFF.md").write_text(
        "Broadened the historical top-only assembly decision; must fail.\n")


def circuit_matches_source(workspace):
    """Generate in isolation with the trusted case producer; do not overwrite."""
    with tempfile.TemporaryDirectory(prefix="crow-decision-circuit-") as raw:
        isolated = Path(raw)
        source = isolated / "03_tscircuit/src/components.json"
        source.parent.mkdir(parents=True)
        shutil.copy2(workspace / "03_tscircuit/src/components.json", source)
        producer = isolated / "build_circuit.py"
        shutil.copy2(HERE / "snapshot/build_circuit.py", producer)
        completed = subprocess.run([sys.executable, str(producer)], cwd=isolated,
                                   text=True, capture_output=True)
        if completed.returncode:
            return False, completed.stdout + completed.stderr
        try:
            expected = json.loads(
                (isolated / "03_tscircuit/build/circuit.json").read_text())
            actual = json.loads(
                (workspace / "03_tscircuit/build/circuit.json").read_text())
        except Exception as exc:
            return False, str(exc)
        return expected == actual, "generated Circuit JSON differs from component source"


def grade(repo, workspace):
    findings = []
    for relative in ("03_src/reviews/accepted-route.yaml",
                     "03_src/reviews/accepted-nets.yaml"):
        expected = HERE / "snapshot" / relative
        actual = workspace / relative
        if not actual.is_file() or sha(actual) != sha(expected):
            findings.append(("PROTECTED-REVIEW-CHANGED",
                             f"independent reviewed input changed: {relative}"))
    try:
        components = json.loads(
            (workspace / "03_tscircuit/src/components.json").read_text())
        u1_source = next(row for row in components if row.get("ref") == "U1")
        assembly = yaml.safe_load(
            (workspace / "03_src/rules/assembly.yaml").read_text()) or {}
        consigned = {str(ref) for row in assembly.get("consigned") or []
                     for ref in row.get("refs") or []}
        if u1_source.get("jlc") != "C200" and "U1" not in consigned:
            findings.append(("U1-MACHINE-ASSEMBLY-REQUIRED",
                             "Crow reduction requires exact U1 machine placement"))
        if assembly.get("sides") != ["top"]:
            findings.append(("CROW-TOP-ONLY-REQUIRED",
                             "Crow reduction requires fitted SMD on top only"))
    except Exception as exc:
        findings.append(("CROW-ASSEMBLY-POLICY-INVALID", str(exc)))
    matches, detail = circuit_matches_source(workspace)
    if not matches:
        findings.append(("CIRCUIT-NOT-REGENERATED", detail))
    completed, report_path = admission(repo, workspace)
    report = None
    if report_path.is_file():
        try:
            report = json.loads(report_path.read_text())
        except Exception as exc:
            findings.append(("ADMISSION-REPORT-INVALID", str(exc)))
    else:
        findings.append(("ADMISSION-REPORT-MISSING", "native gate wrote no report"))
    if report:
        findings.extend((str(row.get("code") or "ADMISSION-FAIL"),
                         str(row.get("message") or row.get("code") or "failure"))
                        for row in report.get("findings") or [])
        if report.get("phase") != "native":
            findings.append(("NATIVE-PHASE-BYPASSED", "native admission did not run"))
    if completed.returncode != 0:
        findings.append(("ADMISSION-COMMAND-FAILED",
                         f"native admission command exited {completed.returncode}"))
    route_marker = workspace / "06_build/route-command.json"
    if completed.returncode == 0 and report and report.get("status") == "PASS" and not findings:
        recorder = subprocess.run(
            [sys.executable, str(HERE / "route_recorder.py"),
             str(route_marker), str(report_path)],
            cwd=workspace, text=True, capture_output=True)
        if recorder.returncode:
            findings.append(("ROUTE-RECORDER-FAILED",
                             recorder.stdout + recorder.stderr))
    else:
        if route_marker.exists():
            findings.append(("ROUTE-RAN-AFTER-REFUSAL",
                             "route recorder exists although admission failed"))
        else:
            findings.append(("ROUTE-NOT-INVOKED",
                             "admission refused before the disposable route command"))
    if findings:
        return emit("FAIL", findings, {
            "admission_exit": completed.returncode,
            "admission_tail": (completed.stdout + completed.stderr)[-3000:],
            "route_invoked": route_marker.is_file(),
        })
    return emit("PASS", evidence={
        "admission": "native PASS",
        "route_recorder": str(route_marker.relative_to(workspace)),
        "production_complete": False,
    })


def main():
    mode, repo, workspace = sys.argv[1:4]
    repo, workspace = Path(repo).resolve(), Path(workspace).resolve()
    if mode == "prepare":
        shutil.copytree(HERE / "snapshot", workspace, dirs_exist_ok=True)
        circuit = generate_circuit(workspace)
        native = subprocess.run(
            ["/usr/bin/python3", str(workspace / "build_native.py"), str(workspace)],
            cwd=workspace, text=True, capture_output=True)
        if circuit.returncode or native.returncode:
            return emit("ERROR", [("PREPARE-FAILED",
                                    circuit.stdout + circuit.stderr +
                                    native.stdout + native.stderr)], rc=2)
        return emit("PASS", evidence={"prepared": "synthetic native Crow coupon"})
    if mode == "reference":
        apply_reference(workspace)
        return emit("PASS", evidence={"reference_repair": "applied"})
    if mode == "bypass":
        apply_bypass(workspace)
        return emit("PASS", evidence={"invalid_shortcut": "applied"})
    if mode == "generated-bypass":
        apply_generated_bypass(workspace)
        return emit("PASS", evidence={"generated_only_shortcut": "applied"})
    if mode == "manual-bypass":
        apply_manual_bypass(workspace)
        return emit("PASS", evidence={"manual_owner_shortcut": "applied"})
    if mode == "side-bypass":
        apply_side_bypass(workspace)
        return emit("PASS", evidence={"side_policy_shortcut": "applied"})
    if mode == "grade":
        return grade(repo, workspace)
    return emit("ERROR", [("MODE", f"unknown mode {mode}")], rc=2)


if __name__ == "__main__":
    sys.exit(main())
