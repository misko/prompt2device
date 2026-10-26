"""Isolated commission draft builder; never an admission or production command.

python3 tools/draft_schematic.py build|verify --project /absolute/project \
    --source 03_src/drafts/channel-a.json --out 06_build/drafts/channel-a-01
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from . import native_schematic as native, task
except ImportError:
    import native_schematic as native
    import task

ROOT = Path(__file__).resolve().parents[1]
STATUS = "DRAFT / NOT ACCEPTED / DO NOT ORDER"
CONTRACTS = ("03_src/contracts.md", "06_build/contracts.md")
DISPATCH_RECORDS = ("01_docs/STATUS.md", "01_docs/journal/commission.md")


def isolated(project, relative, prefix, file=False):
    if not isinstance(relative, str) or not re.fullmatch(re.escape(prefix) + r"/[a-z0-9][a-z0-9_-]*" + (r"\.json" if file else ""), relative):
        raise ValueError(f"expected isolated {prefix} path")
    path = project / relative
    # Reject aliases even when they point inside the project (e.g. to 04_kicad).
    if any(p.is_symlink() for p in (path, *path.parents) if p != project.parent):
        raise ValueError("symlink in draft path")
    if not path.resolve().is_relative_to(project):
        raise ValueError("draft path escapes project")
    if file and not path.is_file():
        raise ValueError("missing draft source")
    return path


def context(project, source_name, out_name):
    project = Path(project).resolve()
    source = isolated(project, source_name, "03_src/drafts", file=True)
    out = isolated(project, out_name, "06_build/drafts")
    envelope = json.loads(source.read_text())
    native.keys(envelope, {"schema", "status", "inputs", "components_evidence", "circuit"})
    if envelope["schema"] not in (1, 2) or envelope["status"] != STATUS:
        raise ValueError("draft schema/status required")
    schema = envelope["schema"]
    inputs = envelope["inputs"]
    required = set((*task.REQUIRED_INPUTS, *CONTRACTS))
    if schema == 2:
        required -= set(DISPATCH_RECORDS)
    if not isinstance(inputs, dict) or not required <= inputs.keys():
        raise ValueError("draft must bind project records and source/build contracts")
    if schema == 2 and set(DISPATCH_RECORDS) & inputs.keys():
        raise ValueError("schema 2 dispatch records belong in captured context, not semantic inputs")
    packet = task.build_packet(ROOT, project, list(inputs), "schematic-draft")
    current = {k: v for k, v in packet["inputs"].items() if schema == 1 or k not in DISPATCH_RECORDS}
    if inputs != current:
        raise ValueError("stale draft inputs")
    circuit = envelope["circuit"]
    native.check(circuit)
    evidence = envelope["components_evidence"]
    if not isinstance(evidence, dict) or set(evidence) != {c["ref"] for c in circuit["components"]}:
        raise ValueError("each draft component needs evidence grades")
    for grade in evidence.values():
        native.keys(grade, {"identity", "pinmap", "notes"})
        if any(grade[k] not in {"CITED", "CANDIDATE", "UNKNOWN"} for k in ("identity", "pinmap")) or not isinstance(grade["notes"], str) or not grade["notes"].strip():
            raise ValueError("invalid evidence grade or missing limitation")
    notices = (STATUS, "Draft source SHA256: " + native.digest(source),
               "UNQUALIFIED candidate identities, pin maps and footprints; see source grades. No engineering approval.")
    # Keep a clear top strip for the warning and hash on the single sheet.
    if any(c["at"][1] + min(p["at"][1] for p in c["pins"]) < 40 for c in circuit["components"]) or any(p[1] < 40 for w in circuit["wire_paths"] for p in w["points"]):
        raise ValueError("reserve top 40 mm for visible draft notices")
    binding = {"schema": schema, "status": STATUS, "stage": "PCB-COMMISSION",
               "task": "schematic-draft", "engineering_acceptance": False,
               "manufacturing_pass": False, "source": source_name,
               "source_sha256": native.digest(source), "inputs": inputs,
               "instructions": packet["instructions"],
               "workflow_graph": packet["workflow_graph"],
               "builder_sha256": native.digest(Path(__file__)),
               "components_evidence": evidence}
    if schema == 2:
        binding["task_tool_sha256"] = native.digest(ROOT / "tools/task.py")
    return source, out, circuit, notices, binding


def execute(command, project, source_name, out_name):
    source, out, circuit, notices, binding = context(project, source_name, out_name)
    expected = json.dumps(circuit, indent=2, sort_keys=True) + "\n"
    if command == "build":
        # Exclusive namespace: failed attempts stay inspectable; never overwrite.
        out.parent.mkdir(parents=True, exist_ok=True)
        out.mkdir(exist_ok=False)
        (out / "draft-source.json").write_bytes(source.read_bytes())
        if binding["schema"] == 2:
            # Immutable attempt evidence, never compared with today's log hashes.
            packet = task.build_packet(ROOT, Path(project).resolve(), list(binding["inputs"]), "schematic-draft")
            (out / "dispatch-context.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
        circuit_path = out / "circuit.json"
        circuit_path.write_text(expected)
        native.build(circuit_path, out, notices=notices)
        # Recheck every input after generation before issuing a provenance receipt.
        if context(project, source_name, out_name)[4] != binding:
            raise ValueError("inputs changed during draft build")
        if binding["schema"] == 2:
            binding["dispatch_context_sha256"] = native.digest(out / "dispatch-context.json")
        binding["native_receipt_sha256"] = native.digest(out / "receipt.json")
        binding["checks"] = "NATIVE_EXPORT_PARITY_ERC_PASS_ONLY" if binding["schema"] == 1 else "NATIVE_EXPORT_PARITY_MATCHED_ERC_ERRORS_ABSENT_ALL_SEVERITIES_REPORTED"
        (out / "draft-receipt.json").write_text(json.dumps(binding, indent=2, sort_keys=True) + "\n")
    elif command != "verify":
        raise ValueError("unsupported draft command")
    if (out / "draft-source.json").read_bytes() != source.read_bytes() or (out / "circuit.json").read_text() != expected:
        raise ValueError("stale draft source snapshot")
    binding["native_receipt_sha256"] = native.digest(out / "receipt.json")
    if binding["schema"] == 2:
        binding["dispatch_context_sha256"] = native.digest(out / "dispatch-context.json")
    binding["checks"] = "NATIVE_EXPORT_PARITY_ERC_PASS_ONLY" if binding["schema"] == 1 else "NATIVE_EXPORT_PARITY_MATCHED_ERC_ERRORS_ABSENT_ALL_SEVERITIES_REPORTED"
    if json.loads((out / "draft-receipt.json").read_text()) != binding:
        raise ValueError("stale draft receipt")
    native.verify(out / "circuit.json", out, notices=notices)
    return binding


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(execute(args.command, args.project, args.source, args.out), indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"draft refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
