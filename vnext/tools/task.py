#!/usr/bin/env python3
"""Emit a read-only, locally bound vNext PCB task packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


AUTHORITY = "TASK_PACKET_ONLY"
STAGE = "PCB-COMMISSION"
SHARED_INSTRUCTIONS = (
    "skills/pcb-design/SKILL.md",
    "skills/workflow-orchestrator/SKILL.md",
    "skills/workflow-orchestrator/references/task-interface.md",
    "skills/pcb-design/workflow/stages/commission.md",
    "skills/pcb-design/procedures/part-recheck.md",
)
PROJECT_BINDING = "skills/pcb-design/bindings/project.md"
TASK_INSTRUCTIONS = {
    "channel-margin": (
        *SHARED_INSTRUCTIONS,
        "skills/pcb-design/procedures/commission/channel-margin.md",
        PROJECT_BINDING,
    ),
}
TASK_INSTRUCTIONS["channel-design"] = (
    *TASK_INSTRUCTIONS["channel-margin"],
    "skills/pcb-design/procedures/commission/channel-design.md",
)
TASK_INSTRUCTIONS["power-design"] = (
    *SHARED_INSTRUCTIONS,
    "skills/pcb-design/procedures/commission/power-design.md",
    PROJECT_BINDING,
)
TASK_INSTRUCTIONS["integration-design"] = (
    *SHARED_INSTRUCTIONS,
    "skills/pcb-design/procedures/commission/integration-design.md",
    PROJECT_BINDING,
)
TASK_INSTRUCTIONS["schematic-draft"] = (
    *SHARED_INSTRUCTIONS,
    "skills/pcb-design/procedures/schematic/draft.md",
    "skills/pcb-design/procedures/schematic/native-tooling.md",
    PROJECT_BINDING,
)
TASK_INSTRUCTIONS["schematic-design"] = (
    *(p for p in SHARED_INSTRUCTIONS if p != "skills/pcb-design/workflow/stages/commission.md"),
    "skills/pcb-design/workflow/stages/schematic.md",
    "skills/pcb-design/procedures/commission/admission.md",
    PROJECT_BINDING,
)
SCHEMATIC_TOOLS = (
    "tools/task.py", "tools/admission.py", "tools/source_snapshot.py",
    "tools/schematic_admission.py", "tools/schematic_assembly.py",
    "tools/native_schematic.py", "tools/native_import.py",
)


def schematic_instructions(contract):
    """Load only adopted producer manuals; tool hashes are provenance, not reading tasks."""
    return TASK_INSTRUCTIONS['schematic-design'] + tuple(
        f'skills/pcb-design/procedures/schematic/{producer}-tooling.md'
        for producer in sorted(contract.get('producers', ['native'])))

REQUIRED_INPUTS = (
    "01_docs/BRIEF.md",
    "01_docs/STATUS.md",
    "01_docs/COMMISSIONING-HOLD.md",
    "01_docs/journal/commission.md",
    "01_docs/capability-profile.json",
    "contracts.md",
    "01_docs/contracts.md",
    "01_docs/reports/contracts.md",
    "01_docs/journal/contracts.md",
)
STATUS_KEYS = ("stage", "step", "measure", "state", "next", "op_pid", "updated")
STATUS_MARKER = "<!-- reader parses from here down -->"
GRAPH_PATH = "skills/pcb-design/workflow/graph.json"


class PacketError(ValueError):
    """Invalid task request, project state, or local binding."""


def _relative_file(base: Path, name: str) -> Path:
    """Resolve one existing file without permitting a lexical or symlink escape."""
    raw = PurePosixPath(name)
    if (not name or raw.is_absolute() or ".." in raw.parts or "." in raw.parts
            or "\\" in name or str(raw) != name):
        raise PacketError(f"invalid relative path: {name!r}")
    path = (base / name).resolve()
    if not path.is_relative_to(base.resolve()):
        raise PacketError(f"path escapes root: {name}")
    if not path.is_file():
        raise PacketError(f"missing file: {name}")
    return path


def _hash_files(base: Path, names: tuple[str, ...]) -> dict[str, str]:
    return {name: hashlib.sha256(_relative_file(base, name).read_bytes()).hexdigest()
            for name in names}


def _status_fields(status: str) -> dict[str, str]:
    if STATUS_MARKER in status:
        status = status.split(STATUS_MARKER, 1)[1]
    fields: dict[str, str] = {}
    for line in status.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(.*?)\s*", line)
        if not match or match.group(1) not in STATUS_KEYS:
            raise PacketError("STATUS has an unsupported field or format")
        key, value = match.groups()
        if key in fields or (not value and key != "op_pid"):
            raise PacketError(f"STATUS has a duplicate or empty {key} field")
        fields[key] = value
    if set(fields) != set(STATUS_KEYS):
        raise PacketError("STATUS must contain exactly the seven required fields")
    if fields["stage"] not in {"commission", "architecture", "schematic"}:
        raise PacketError("project is not at commission, architecture or schematic stage")
    if fields["state"] not in {"working", "blocked", "checkpoint"}:
        raise PacketError("task state must be working, blocked or checkpoint")
    return fields


def build_packet(root: Path, project: Path, inputs: tuple[str, ...] | list[str],
                 task: str) -> dict[str, object]:
    """Bind a supported task to local instructions and explicit project inputs.

    This function reads files only. Engineering sufficiency and gate decisions
    belong to the task agent and coordinator, respectively.
    """
    if task not in TASK_INSTRUCTIONS:
        raise PacketError(f"unsupported task: {task}")
    root = Path(root).resolve()
    project = Path(project)
    if not project.is_absolute() or not project.is_dir():
        raise PacketError("project must be an existing absolute directory")
    project = project.resolve()
    additional = tuple(inputs)
    all_inputs = tuple(dict.fromkeys((*REQUIRED_INPUTS, *additional)))
    # Resolve every input before reading STATUS, including user-supplied paths.
    input_hashes = _hash_files(project, all_inputs)
    fields = _status_fields(_relative_file(project, "01_docs/STATUS.md").read_text())
    if fields['state'] == 'checkpoint':
        raise PacketError('project is at a user checkpoint; explicit coordinator resume required')
    selected = TASK_INSTRUCTIONS[task]
    stage = STAGE
    prerequisites = {}
    if (fields['stage'] == 'schematic') != (task == 'schematic-design'):
        raise PacketError('project is not at commission/architecture for research or schematic for schematic-design')
    if task == 'schematic-design':
        for name in ('tools/admission.py', 'tools/schematic_admission.py'):
            _relative_file(root, name)
        try:
            import admission
            import schematic_admission as schematic
            receipt = schematic.PARTS
            # The source/output declaration is an independently reviewed assembly
            # input, not a new unreviewed escape hatch after sourcing acceptance.
            prior, contract = schematic.prerequisites(project, root)
            selected = schematic_instructions(contract)
            pending, seen = [receipt], set()
            while pending:
                name = pending.pop()
                if name in seen:
                    continue
                seen.add(name)
                cert = admission.validate_certificate(project, name, root)
                input_hashes.update(_hash_files(project, (name, cert['review'], *cert['subjects'])))
                pending.extend(cert['prerequisites'])
            prerequisites = _hash_files(project, (receipt,))
            stage = 'KICAD-SCHEMATIC'
        except (ImportError, OSError, ValueError, KeyError, TypeError) as exc:
            raise PacketError(f'schematic prerequisite invalid: {exc}') from exc
    if fields['stage'] == 'architecture':
        if task == 'schematic-draft':
            raise PacketError('commission-only draft cannot run as architecture production')
        # Lazy import preserves the isolated commission-only packet route.
        _relative_file(root, 'tools/admission.py')
        try:
            from admission import AdmissionError, validate_certificate
        except ImportError as exc:
            raise PacketError(f'local admission verifier unavailable: {exc}') from exc
        receipt = '06_build/checkpoints/commissioned_brief.json'
        try:
            prior = validate_certificate(project, receipt, root)
            if prior['role'] != 'commissioned_brief':
                raise AdmissionError('wrong prerequisite role')
        except (AdmissionError, OSError, ValueError, KeyError, TypeError) as exc:
            raise PacketError(f'architecture prerequisite invalid: {exc}') from exc
        prerequisites = _hash_files(project, (receipt,))
        input_hashes.update(_hash_files(project, tuple(dict.fromkeys(
            (receipt, prior['review'], *prior['subjects'])))))
        selected = tuple('skills/pcb-design/workflow/stages/architecture.md'
                         if p == 'skills/pcb-design/workflow/stages/commission.md' else p
                         for p in selected) + ('skills/pcb-design/procedures/commission/admission.md',)
        stage = 'PCB-ARCHITECTURE'
    instruction_hashes = _hash_files(root, selected)
    graph_hash = _hash_files(root, (GRAPH_PATH,))[GRAPH_PATH]
    return {
        "schema_version": 1,
        "authority": AUTHORITY,
        "stage": stage,
        "task": task,
        "project": str(project),
        "status": fields,
        "instruction_root": str(root),
        "instructions": instruction_hashes,
        "tool_bindings": _hash_files(root, SCHEMATIC_TOOLS) if task == 'schematic-design' else {},
        "workflow_graph": {"path": GRAPH_PATH, "sha256": graph_hash},
        "inputs": input_hashes,
        "prerequisites": prerequisites,
        "missing_engineering_inputs": {
            "owner": "task_agent",
            "status": "not_evaluated_by_packet_tool",
        },
        "output_guidance": {
            "task_agent": (["01_docs/reports/*.md", "03_src/drafts/*.json", "06_build/drafts/*/"]
                           if task == "schematic-draft" else
                           ["source/output authoring under reviewed project contract; declaration fixes manifest/expected locations; no placement"]
                           if task == "schematic-design" else
                           ["01_docs/reports/*.md", "01_docs/ARCHITECTURE.md", "01_docs/DETAIL_DESIGN.md", "03_src/rules/*.yaml"]
                           if stage == 'PCB-ARCHITECTURE' else ["01_docs/reports/*.md"]),
            "coordinator_only": ["01_docs/STATUS.md", "01_docs/journal/commission.md"],
            "note": "Descriptive scope only; this packet does not enforce writes or accept gates.",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path,
                        help="absolute project directory")
    parser.add_argument("--task", required=True, help="supported task name")
    parser.add_argument("--input", action="append", default=[], dest="inputs",
                        help="additional project-relative input file; repeatable")
    args = parser.parse_args(argv)
    try:
        packet = build_packet(Path(__file__).resolve().parents[1], args.project,
                              args.inputs, args.task)
    except (PacketError, OSError, UnicodeError) as exc:
        print(f"task packet error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(packet, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
