#!/usr/bin/env python3
"""Fail-closed continuation gate for every crow PCB post-JLC path."""

from __future__ import annotations

import argparse
import csv
import filecmp
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


PYTHON = "/usr/bin/python3"


def invoke(command: list[object], cwd: Path, label: str) -> int:
    completed = subprocess.run(
        [str(value) for value in command], cwd=cwd, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.returncode:
        print(f"GATE FAILED [{label}]: exit {completed.returncode}")
    return completed.returncode


def regular(path: Path, label: str, root: Path) -> bool:
    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(root)
    except ValueError:
        print(f"GATE FAILED [{label}]: evidence escapes project: {path}")
        return False
    current = root
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            print(f"GATE FAILED [{label}]: symlink evidence component is forbidden: {current}")
            return False
    if not path.is_file():
        print(f"GATE INCOMPLETE [{label}]: missing regular file: {path}")
        return False
    return True


def blank_response_matches_request(response: Path, request: Path,
                                   label: str) -> bool:
    """Keep public-catalog continuation distinct from operator JLC evidence."""
    try:
        request_data = json.loads(request.read_text(encoding="utf-8-sig"))
        with response.open(newline="", encoding="utf-8-sig") as stream:
            rows = list(csv.DictReader(stream))
    except (OSError, ValueError, csv.Error) as exc:
        print(f"GATE FAILED [{label}]: blank response is unreadable: {exc}")
        return False
    expected = [str(row.get("requested_lcsc") or "")
                for row in request_data.get("rows") or []]
    observed = [str(row.get("Requested LCSC") or "") for row in rows]
    populated = [
        f"{row.get('Requested LCSC')}: {field}"
        for row in rows for field, value in row.items()
        if field != "Requested LCSC" and str(value or "").strip()
    ]
    if observed != expected:
        print(f"GATE FAILED [{label}]: blank response rows do not match the exact request")
        return False
    if populated:
        print(f"GATE FAILED [{label}]: public-catalog mode cannot consume operator fields: {populated[:5]}")
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--context", required=True)
    parser.add_argument("--continuation", required=True)
    parser.add_argument("--require-schematic", action="store_true")
    parser.add_argument("--pinned-schematic", type=Path)
    parser.add_argument("--generated-schematic", type=Path)
    parser.add_argument(
        "--allow-public-catalog", action="store_true",
        help="accept fresh public catalog evidence for pre-layout design work only")
    parser.add_argument(
        "--allow-blocked-sourcing", action="store_true",
        help="continue design with fresh exact evidence but a loud sourcing/order hold")
    args = parser.parse_args()

    project = args.project.resolve()
    repo = args.repo_root.resolve()
    context = args.context
    kicad = repo / "skills/kicad-pcb/scripts"
    fab = repo / "skills/jlcpcb-fab/scripts"
    input_gate = repo / "projects/crow-roof-array-v1/03_src/prelayout_input_checkpoint.py"
    circuit = project / "03_tscircuit/build/circuit.json"
    request = project / "06_build/sourcing/prelayout_request.json"
    response = project / "06_build/sourcing/prelayout_response.csv"
    receipt = project / "06_build/sourcing/prelayout_receipt.json"
    catalog_evidence = project / "06_build/sourcing/public_catalog_stock.json"
    catalog_decision = project / "01_docs/decisions/0006-public-catalog-prelayout-only.md"
    input_record = project / "06_build/checkpoints/prelayout-inputs.json"
    prelayout_record = project / "06_build/checkpoints/prelayout.json"
    schematic_record = project / "06_build/checkpoints/schematic.json"
    assembly = project / "03_src/rules/assembly.yaml"
    procurement = project / "01_docs/sourcing/procurement-policy.yaml"

    # All checks before manufacturing_readiness are read-only. This ordering is
    # what lets reuse drivers call the gate before their first generated write.
    rc = invoke([PYTHON, kicad / "build_provenance.py", "audit", "."],
                project, f"{context}:M-FRESH")
    if rc:
        return rc

    checkpoint_records = ((prelayout_record, "PRELAYOUT-CHECKPOINT"),
                          (input_record, "INPUT-CHECKPOINT"))
    if args.require_schematic:
        checkpoint_records += ((schematic_record, "SCHEMATIC-CHECKPOINT"),)
    for path, label in checkpoint_records:
        if not regular(path, f"{context}:{label}", project):
            return 2

    commands = [
        ([PYTHON, kicad / "stage_checkpoint.py", "verify", ".", "prelayout"],
         f"{context}:CHECKPOINT"),
        ([PYTHON, input_gate, "verify", ".", "--repo-root", repo,
          "--record", input_record], f"{context}:INPUT-CHECKPOINT"),
    ]
    if args.require_schematic:
        commands.append((
            [PYTHON, kicad / "stage_checkpoint.py", "verify", ".", "schematic"],
            f"{context}:SCHEMATIC-CHECKPOINT"))
    for command, label in commands:
        rc = invoke(command, project, label)
        if rc:
            return rc

    if bool(args.pinned_schematic) != bool(args.generated_schematic):
        print(f"GATE FAILED [{context}:M-PIN]: both pinned/generated schematic paths are required together")
        return 2
    if args.pinned_schematic:
        pinned = args.pinned_schematic
        generated = args.generated_schematic
        if not pinned.is_absolute():
            pinned = project / pinned
        if not generated.is_absolute():
            generated = project / generated
        if not regular(pinned, f"{context}:M-PIN", project) or not regular(
                generated, f"{context}:M-PIN", project):
            return 2
        if not filecmp.cmp(pinned, generated, shallow=False):
            print(f"GATE FAILED [{context}:M-PIN]: deterministic input schematic differs from the checkpointed generated schematic")
            return 1

    for path, label in ((circuit, "circuit"), (request, "request"),
                        (response, "response"),
                        (assembly, "assembly"), (procurement, "procurement")):
        if not regular(path, f"{context}:J-PCBA-{label.upper()}", project):
            return 2

    try:
        assembly_data = yaml.safe_load(
            assembly.read_text(encoding="utf-8-sig")) or {}
        build_quantity = int(assembly_data.get("build_quantity"))
        if build_quantity <= 0:
            raise ValueError
    except (OSError, TypeError, ValueError, yaml.YAMLError):
        print(f"GATE INCOMPLETE [{context}:J-PCBA]: assembly build_quantity is not a positive integer")
        return 2

    # Reproduce the immutable request from the current circuit and policy
    # before even opening the operator receipt.  The receipt verifier then
    # reopens the exact request/response hashes and the current circuit hash.
    rc = invoke([
        PYTHON, fab / "jlc_pcba_availability.py", "verify-request", request,
        "--bom", circuit, "--assembly", assembly,
        "--procurement-policy", procurement,
        "--build-quantity", build_quantity, "--phase", "prelayout",
    ], project, f"{context}:J-PCBA-REQUEST")
    if rc:
        return rc

    if receipt.is_file() and not receipt.is_symlink():
        rc = invoke([
            PYTHON, fab / "jlc_pcba_availability.py", "verify", receipt,
            "--bom", circuit, "--phase", "prelayout",
        ], project, f"{context}:J-PCBA-RECEIPT")
        if rc:
            return rc
        readiness_authority = ["--pcba-receipt", receipt]
        authority_description = "authenticated JLCPCB receipt"
    elif args.allow_public_catalog:
        if not blank_response_matches_request(
                response, request, f"{context}:J-PCBA-PUBLIC"):
            return 1
        for path, label in ((catalog_evidence, "CATALOG-EVIDENCE"),
                            (catalog_decision, "CATALOG-DECISION")):
            if not regular(path, f"{context}:J-PCBA-{label}", project):
                return 2
        readiness_authority = [
            "--catalog-request", request,
            "--catalog-evidence", catalog_evidence,
            "--catalog-decision", catalog_decision,
        ]
        authority_description = "fresh public-catalog negative filter"
        distributor_policy = project / "01_docs/sourcing/public-distributor-policy.yaml"
        if distributor_policy.exists() or distributor_policy.is_symlink():
            distributor_quotes = project / "01_docs/sourcing/manual_quotes.yaml"
            for path, label in ((distributor_policy, 'DISTRIBUTOR-POLICY'),
                                (distributor_quotes, 'DISTRIBUTOR-QUOTES')):
                if not regular(path, f'{context}:{label}', project):
                    return 2
            readiness_authority += ['--distributor-policy', distributor_policy,
                                    '--distributor-quotes', distributor_quotes]
            authority_description = 'public stock with explicit exact-part distributor design policy'
    else:
        regular(receipt, f"{context}:J-PCBA-RECEIPT", project)
        print("  Grade the preserved response, then run:")
        print(f"  {args.continuation}")
        print("  Or refresh the public catalog evidence and use the explicit public-prelayout continuation.")
        return 2

    pipeline = project / "06_build/verification/pipeline"
    rc = invoke([
        PYTHON, fab / "manufacturing_readiness.py", "grade", ".",
        "--phase", "prelayout", *readiness_authority,
        *(["--allow-blocked-sourcing"] if args.allow_blocked_sourcing else []),
        "--json", project / "06_build/verification/manufacturing_readiness_prelayout.json",
        "--stage-bundle", pipeline / "bundles/part_freeze",
        "--stage-result", pipeline / "S-PART-FREEZE.stage.json",
    ], project, f"{context}:J-PCBA-READINESS")
    if rc:
        return rc
    print(f"PRELAYOUT-RESUME PASS [{context}]: checkpoint, complete input census, exact request, {authority_description}, and readiness reverified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
