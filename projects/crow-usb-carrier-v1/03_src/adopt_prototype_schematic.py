#!/usr/bin/env python3
"""Guarded Crow prototype-only schematic adoption; never produces a PCB."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

import yaml

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/pcb-design/scripts"))
sys.path.insert(0, str(ROOT / "skills/kicad-pcb/scripts"))
from critical_part_selection_admission import evaluate as evaluate_selection
from generate_board_generic import parse_netlist
from pause_state import verify as verify_pause

DESTINATIONS = {
    "circuit.json": "03_tscircuit/build/circuit.json",
    "crow_carrier.kicad_sch": "04_kicad/crow_carrier.kicad_sch",
    "crow_carrier.net": "06_build/netlists/crow_carrier.net",
    "schematic.pdf": "03_tscircuit/build/schematic.pdf",
}
EXTRA_INPUTS = (
    "03_tscircuit/package.json", "03_tscircuit/bun.lock",
    "03_tscircuit/net_aliases.txt", "03_src/rules/critical_part_selection.yaml",
    "03_src/rules/assembly.yaml", "01_docs/findings.yaml",
    "02_parts/TPD2EUSB30ADRTR/part.yaml",
    "01_docs/research/2026-09-24-public-stock-569/public-stock.json",
    "01_docs/research/2026-09-25-ti-usb-esd-prototype-test-plan.md",
    "08_reviews/2026-09-25_ti-usb-esd-prototype-only_terra.md",
)


class AdoptionError(ValueError):
    pass


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inside(path: Path, parent: Path) -> bool:
    return path == parent or parent in path.parents


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)


def check_destination_authority(project: Path) -> None:
    """Protect other workstreams' edits before even offering a hash guard."""
    if git("rev-parse", "--show-toplevel", cwd=project).returncode:
        raise AdoptionError("canonical project must be inside a Git checkout")
    ignored_net = "06_build/netlists/crow_carrier.net"
    for relative in DESTINATIONS.values():
        tracked = git("ls-files", "--error-unmatch", "--", relative, cwd=project)
        if tracked.returncode == 0:
            dirty = git("status", "--porcelain", "--untracked-files=all", "--", relative,
                        cwd=project)
            if dirty.returncode or dirty.stdout.strip():
                raise AdoptionError(f"dirty tracked destination: {relative}")
        elif relative == ignored_net and git("check-ignore", "-q", "--", relative,
                                              cwd=project).returncode == 0:
            # The fixed native netlist is intentionally ignored. Its exact
            # bytes are still guarded in the plan and preserved in backup.
            continue
        else:
            raise AdoptionError(f"untracked canonical destination: {relative}")


def exact_input_paths(project: Path) -> dict[str, Path]:
    sources = sorted((project / "03_tscircuit/src").rglob("*.tsx"))
    if not sources:
        raise AdoptionError("no governed TSX source files")
    paths = sources + [project / name for name in EXTRA_INPUTS]
    result = {}
    for path in paths:
        resolved = path.resolve()
        if not inside(resolved, project) or not resolved.is_file():
            raise AdoptionError(f"missing or escaping producer input: {path}")
        result[path.relative_to(project).as_posix()] = path
    return result


def check_staged_gates(project: Path, files: dict[str, Path]) -> dict[str, str]:
    """Run source-bound gates against a disposable, private TI subject."""
    with tempfile.TemporaryDirectory(prefix="crow-ti-adoption-gates-") as tmp:
        view = Path(tmp) / "project"
        view.mkdir()
        for dirname in ("01_docs", "02_parts", "03_src", "08_reviews"):
            shutil.copytree(project / dirname, view / dirname, copy_function=shutil.copy2)
        for name, relative in DESTINATIONS.items():
            target = view / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(files[name], target)
        commands = {
            "E-FAULT": [sys.executable, str(ROOT / "skills/kicad-pcb/scripts/early_design_check.py"),
                        str(view), "--fault-envelope"],
            "P-PREC": [sys.executable, str(ROOT / "skills/kicad-pcb/scripts/ic_reference_check.py"),
                       str(view), "--require-semantic-review"],
            "ERC": ["kicad-cli", "sch", "erc", "--severity-error", "--exit-code-violations",
                    "-o", str(Path(tmp) / "erc.txt"),
                    str(view / DESTINATIONS["crow_carrier.kicad_sch"])],
        }
        evidence = {}
        for gate, command in commands.items():
            run = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            if run.returncode:
                detail = (run.stdout + "\n" + run.stderr).strip()[-2000:]
                raise AdoptionError(f"staged {gate} failed (rc={run.returncode}): {detail}")
            evidence[gate] = hashlib.sha256(
                (run.stdout + "\n" + run.stderr).encode()).hexdigest()
        return evidence


def check_bundle(project: Path, bundle: Path, selection_check=evaluate_selection,
                 export_netlist=None, gate_check=check_staged_gates) -> tuple[dict, dict[str, Path], dict]:
    project, bundle = project.resolve(), bundle.resolve()
    if not inside(bundle, project / "06_build/prototype_only") or not bundle.is_dir():
        raise AdoptionError("bundle must be under this project's private prototype tree")
    if bundle.name.endswith("pin-index-layout"):
        raise AdoptionError("renderer-only candidate is not a complete producer bundle")
    manifest_path = project / "03_src/rules/critical_part_selection.yaml"
    report = selection_check(project, manifest_path)
    if report.get("status") != "PROTOTYPE_ONLY" or report.get("prototype_refs") != ["U_USB_ESD"]:
        raise AdoptionError("exact U_USB_ESD PROTOTYPE_ONLY selection required")
    selected = yaml.safe_load(manifest_path.read_text())
    rows = selected.get("selections") if isinstance(selected, dict) else None
    if not isinstance(rows, list) or len(rows) != 1 or rows[0].get("ref") != "U_USB_ESD" \
            or rows[0].get("mpn") != "TPD2EUSB30ADRTR" \
            or (rows[0].get("suitability") or {}).get("status") != "prototype_only":
        raise AdoptionError("selection manifest does not name exact TI prototype-only device")
    paused, findings = verify_pause(project)
    if not paused:
        raise AdoptionError(f"pause state invalid: {findings}")
    pause = json.loads((project / "01_docs/pause_state.json").read_text())
    if pause.get("checkpoint", {}).get("path") != "03_src/rules/critical_part_selection.yaml" \
            or pause["checkpoint"].get("sha256") != sha(manifest_path):
        raise AdoptionError("pause checkpoint does not bind selected TI device")

    receipt_path = bundle / "receipt.json"
    if not receipt_path.is_file():
        raise AdoptionError("private producer receipt missing")
    receipt = json.loads(receipt_path.read_text())
    if receipt.get("schema") != 1 or receipt.get("status") != "PROTOTYPE_ONLY" \
            or receipt.get("selection_gate") != (
                "skills/pcb-design/scripts/critical_part_selection_admission.py --require-prototype"):
        raise AdoptionError("bundle is not an admitted prototype-only producer receipt")
    inputs = exact_input_paths(project)
    expected_inputs = {name: sha(path) for name, path in inputs.items()}
    if receipt.get("inputs") != expected_inputs:
        raise AdoptionError("bundle inputs are incomplete or stale")
    artifacts = receipt.get("artifacts")
    if not isinstance(artifacts, dict) or set(artifacts) != set(DESTINATIONS):
        raise AdoptionError("bundle artifact set is partial or has extras")
    files = {name: bundle / name for name in DESTINATIONS}
    if any(not path.is_file() or path.is_symlink() for path in files.values()) \
            or {name: sha(path) for name, path in files.items()} != artifacts:
        raise AdoptionError("bundle artifacts are missing, stale, or linked")

    circuit = json.loads(files["circuit.json"].read_text())
    if not isinstance(circuit, list) or any(
            isinstance(row, dict) and row.get("type", "").endswith("_error")
            for row in circuit):
        raise AdoptionError("circuit has malformed or hard-error diagnostics")
    components = [row for row in circuit if isinstance(row, dict)
                  and row.get("type") == "source_component"]
    names = [row.get("name") for row in components]
    if len(components) != 569 or len(set(names)) != 569:
        raise AdoptionError("source circuit must contain 569 unique components")
    esd = next((row for row in components if row.get("name") == "U_USB_ESD"), None)
    if not esd or esd.get("manufacturer_part_number") != "TPD2EUSB30ADRTR":
        raise AdoptionError("source circuit has wrong USB ESD MPN")
    comps, pads, nets = parse_netlist(files["crow_carrier.net"])
    if set(comps) != set(names) or len(pads) != 1787 or len(nets) != 428:
        raise AdoptionError("native netlist census differs from governed 569/1787/428")
    if comps["U_USB_ESD"] != ("Package_TO_SOT_SMD:Texas_DRT-3", "TPD2EUSB30ADRTR") \
            or {pad: net for (ref, pad), net in pads.items() if ref == "U_USB_ESD"} != {
                "1": "USB_DP", "2": "USB_DN", "3": "GND"}:
        raise AdoptionError("native USB ESD FPID/value/pad map is not exact TI DRT")
    if not files["schematic.pdf"].read_bytes().startswith(b"%PDF-"):
        raise AdoptionError("bundle schematic is not a PDF")

    # The netlist is checked against a second export from the exact bundle
    # schematic. This is read-only and never touches the canonical schematic.
    if export_netlist is None:
        with tempfile.TemporaryDirectory(prefix="crow-adopt-export-") as tmp:
            exported = Path(tmp) / "from_schematic.net"
            subprocess.run(["kicad-cli", "sch", "export", "netlist", "--output",
                            str(exported), str(files["crow_carrier.kicad_sch"])],
                           check=True, capture_output=True, text=True)
            generated = parse_netlist(exported)
    else:
        generated = export_netlist(files["crow_carrier.kicad_sch"])
    if generated != (comps, pads, nets):
        raise AdoptionError("bundle netlist differs from native schematic export")
    gates = gate_check(project, files)
    if set(gates) != {"E-FAULT", "P-PREC", "ERC"}:
        raise AdoptionError("staged gate evidence is incomplete")
    return receipt, files, gates


def current_hashes(project: Path) -> dict[str, str | None]:
    result = {}
    for relative in DESTINATIONS.values():
        path = project / relative
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise AdoptionError(f"canonical destination is not a regular file: {relative}")
        result[relative] = sha(path) if path.is_file() else None
    return result


def adopt(project: Path, bundle: Path, *, expected: dict[str, str | None] | None,
          backup_dir: Path | None, selection_check=evaluate_selection,
          export_netlist=None, gate_check=check_staged_gates, plan=False) -> dict:
    project = project.resolve()
    check_destination_authority(project)
    receipt, files, gates = check_bundle(project, bundle, selection_check,
                                        export_netlist, gate_check)
    check_destination_authority(project)
    observed = current_hashes(project)
    bundle_digest = sha(bundle / "receipt.json")
    if plan:
        return {"status": "PLAN_ONLY", "expected_current": observed,
                "bundle_sha256": bundle_digest, "staged_gates": gates}
    if expected is None or expected.get("status") != "PLAN_ONLY" \
            or expected.get("expected_current") != observed \
            or expected.get("bundle_sha256") != bundle_digest or backup_dir is None:
        raise AdoptionError("exact current-hash guard and new backup directory required")
    backup_dir = backup_dir.resolve(strict=False)
    if backup_dir.exists() or backup_dir.is_symlink() or not inside(
            backup_dir, project / "06_build/prototype_only"):
        raise AdoptionError("backup must be a new path under private prototype tree")
    marker = project / "06_build/prototype_only/adoption_pending.json"
    if marker.exists():
        raise AdoptionError("prior incomplete adoption requires manual recovery")
    after = {relative: receipt["artifacts"][name]
             for name, relative in DESTINATIONS.items()}
    if observed == after:
        raise AdoptionError("canonical artifacts already equal this bundle")
    staged = {}
    backup_dir.mkdir(parents=True)
    try:
        for name, relative in DESTINATIONS.items():
            target = project / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            tmp = target.parent / f".{target.name}.prototype-stage-{os.getpid()}"
            if tmp.exists():
                raise AdoptionError(f"staging path already exists: {tmp}")
            shutil.copyfile(files[name], tmp)
            if sha(tmp) != after[relative]:
                raise AdoptionError(f"staging hash mismatch: {relative}")
            staged[relative] = tmp
            if observed[relative] is not None:
                old = backup_dir / relative
                old.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(target, old)
                if sha(old) != observed[relative]:
                    raise AdoptionError(f"backup hash mismatch: {relative}")
        check_destination_authority(project)
        if current_hashes(project) != observed:
            raise AdoptionError("canonical destinations changed during staging")
        marker.write_text(json.dumps({"status": "INCOMPLETE", "before": observed,
                                      "after": after}, sort_keys=True) + "\n")
        replaced = []
        output = receipt_stage = None
        try:
            for relative, tmp in staged.items():
                os.replace(tmp, project / relative)
                replaced.append(relative)
            if current_hashes(project) != after:
                raise AdoptionError("post-promotion hash mismatch")
            result = {"schema": 1, "status": "PROTOTYPE_ONLY",
                      "stage": "SCHEMATIC_ONLY", "admitted_at": datetime.now(timezone.utc).isoformat(),
                      "scope": "source/schematic adoption only; no PCB, route, release, order, or electrical qualification",
                      "bundle_receipt_sha256": bundle_digest,
                      "staged_gates": gates,
                      "selection_sha256": sha(project / "03_src/rules/critical_part_selection.yaml"),
                      "pause_state_sha256": sha(project / "01_docs/pause_state.json"),
                      "before": observed, "after": after,
                      "backup": backup_dir.relative_to(project).as_posix(),
                      "ordinary_checkpoint": "NOT_REFRESHED",
                      "pinned_reuse_schematic": "NOT_PROMOTED"}
            receipt_dir = project / "06_build/prototype_only/adoptions"
            receipt_dir.mkdir(parents=True, exist_ok=True)
            output = receipt_dir / f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{os.getpid()}.json"
            if output.exists():
                raise AdoptionError("adoption receipt path already exists")
            receipt_stage = output.with_suffix(".stage")
            if receipt_stage.exists():
                raise AdoptionError("adoption receipt staging path already exists")
            receipt_stage.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
            os.replace(receipt_stage, output)
            marker.unlink()
            result["receipt_path"] = str(output)
            return result
        except Exception:
            if output is not None:
                output.unlink(missing_ok=True)
            if receipt_stage is not None:
                receipt_stage.unlink(missing_ok=True)
            for relative in reversed(replaced):
                target = project / relative
                if observed[relative] is None:
                    target.unlink(missing_ok=True)
                else:
                    shutil.copyfile(backup_dir / relative, target)
            if current_hashes(project) == observed:
                marker.unlink(missing_ok=True)
            raise
    finally:
        for tmp in staged.values():
            tmp.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("project", type=Path)
    ap.add_argument("bundle", type=Path)
    ap.add_argument("--plan", action="store_true", help="validate and print current-hash guard only")
    ap.add_argument("--expect-current", type=Path, help="unmodified JSON output from --plan")
    ap.add_argument("--backup-dir", type=Path, help="new directory under 06_build/prototype_only")
    args = ap.parse_args()
    try:
        expected = json.loads(args.expect_current.read_text()) if args.expect_current else None
        result = adopt(args.project, args.bundle, expected=expected,
                       backup_dir=args.backup_dir, plan=args.plan)
    except (AdoptionError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"PROTOTYPE-ADOPTION FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
