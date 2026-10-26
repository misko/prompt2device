#!/usr/bin/env python3
"""Render the vNext workflow catalog and a project's reported current stage.

This view is read-only. Neither a STATUS beacon nor a graph edge is evidence
that a stage or its engineering gate has been accepted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import subprocess

from task import STAGE, TASK_INSTRUCTIONS


ROOT = Path(__file__).resolve().parents[1]
GRAPH = ROOT / "skills/pcb-design/workflow/graph.json"
STATUS = "01_docs/STATUS.md"
STATUS_MARKER = "<!-- reader parses from here down -->"


class WorkflowError(ValueError):
    """Malformed graph or ambiguous project beacon."""


def _selection(selects: dict) -> str | None:
    if selects == {"always": True}:
        return None
    if not isinstance(selects, dict) or not selects:
        raise WorkflowError("stage has invalid selection condition")
    clauses = []
    for key, values in selects.items():
        if not isinstance(key, str) or not isinstance(values, list) or not values:
            raise WorkflowError("stage has invalid selection condition")
        clauses.append(f"{key}=" + ",".join(str(v).lower() if isinstance(v, bool) else str(v)
                                           for v in values))
    return "; ".join(clauses)


def _graph(path: Path) -> tuple[list[dict], list[tuple[int, int, str, str | None]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != 1 or not isinstance(data.get("stages"), list):
        raise WorkflowError("unsupported workflow graph schema")
    stages = data["stages"]
    producers: dict[str, tuple[int, str | None]] = {}
    selections: list[str | None] = []
    ids: set[str] = set()
    for index, stage in enumerate(stages):
        spec = stage.get("spec", {})
        stage_id = spec.get("id")
        if (spec.get("schema") != 1 or not isinstance(stage_id, str)
                or not stage_id or stage_id in ids
                or not isinstance(spec.get("produces"), list)
                or not isinstance(spec.get("requires"), list)):
            raise WorkflowError("invalid or duplicate stage spec")
        ids.add(stage_id)
        condition = _selection(stage.get("selects"))
        selections.append(condition)
        for artifact in spec["produces"]:
            if not isinstance(artifact, str) or not artifact or artifact in producers:
                raise WorkflowError(f"invalid or duplicate produced artifact: {artifact!r}")
            producers[artifact] = (index, condition)
    edges = []
    for target, stage in enumerate(stages):
        for artifact in stage["spec"]["requires"]:
            if artifact not in producers:
                raise WorkflowError(f"no producer for required artifact: {artifact}")
            source, producer_condition = producers[artifact]
            consumer_condition = selections[target]
            if producer_condition == consumer_condition:
                condition = producer_condition
            elif producer_condition and consumer_condition:
                condition = f"producer: {producer_condition}; consumer: {consumer_condition}"
            else:
                condition = producer_condition or consumer_condition
            edges.append((source, target, artifact, condition))
    return stages, edges


def _reported_stage(project: Path) -> tuple[str | None, str, str]:
    status_path = project / STATUS
    if not status_path.is_file():
        return None, f"STATUS unavailable: `{STATUS}` is missing.", "STATUS source: missing."
    status_bytes = status_path.read_bytes()
    content = status_bytes.decode("utf-8")
    if STATUS_MARKER not in content:
        raise WorkflowError("STATUS is missing its reader marker")
    fields: dict[str, str] = {}
    for line in content.split(STATUS_MARKER, 1)[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"([a-z_]+):\s*(.*?)\s*", line)
        if not match:
            raise WorkflowError("STATUS has an unsupported field format")
        key, value = match.groups()
        if key in fields:
            raise WorkflowError(f"STATUS has a duplicate {key} field")
        fields[key] = value
    stage = fields.get("stage")
    source = (f"STATUS source: `{STATUS}`; updated: "
              f"`{fields.get('updated') or 'unreported'}`; "
              f"SHA-256: `{hashlib.sha256(status_bytes).hexdigest()}`.")
    if not stage:
        return None, "STATUS unavailable: `stage` is missing or empty.", source
    entry_nodes = {"commission": "PCB-COMMISSION", "architecture": "PCB-ARCHITECTURE",
                   "sourcing": "PCB-SOURCING", "schematic": "KICAD-SCHEMATIC",
                   "placement": "KICAD-PLACEMENT", "mating_clearance": "KICAD-MATING-IMPORT",
                   "routing": "KICAD-ROUTING", "layout_seal": "KICAD-LAYOUT-SEAL",
                   "fabrication": "JLC-FABRICATION", "assembly_verify": "JLC-ASSEMBLY-VERIFY",
                   "release_review": "PCB-RELEASE-REVIEW", "release_seal": "PCB-RELEASE-SEAL",
                   "publication": "PCB-PUBLICATION", "first_article": "PCB-FIRST-ARTICLE",
                   "production": "PCB-PRODUCTION"}
    if stage not in entry_nodes:
        return None, (f"STATUS reports `{stage}`, but mapping that beacon stage to a graph node "
                      "is unsupported. No node is marked current."), source
    return entry_nodes[stage], (f"STATUS reports `{stage}` (" +
                              (f"state `{fields['state']}`" if fields.get("state") else "state unreported") +
                              "). This is reported progress, not stage acceptance."), source


def _mermaid_label(value: str) -> str:
    return value.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def _exploration_view(project: Path, catalog: dict) -> list[str]:
    route = catalog.get("exploration")
    if not route:
        return []
    lines = ["", "## Exploration before acceptance", "",
             "Draft, comparison and repair are not accepted engineering stages.",
             f"Domain: `{route['contract']}`. Control: `{route['controller']}`.",
             "", "```mermaid", "flowchart LR"]
    nodes = list(dict.fromkeys(n for edge in route["edges"] for n in edge))
    for i, node in enumerate(nodes):
        lines.append(f'    e{i}["{_mermaid_label(node)}"]')
    for source, target in route["edges"]:
        lines.append(f"    e{nodes.index(source)} --> e{nodes.index(target)}")
    lines.extend(["```", ""])
    journal = project / "run.json"
    if journal.is_file():
        state = json.loads(journal.read_text())
        if state.get("version") != 1 or "tasks" not in state:
            raise WorkflowError("unsupported exploration journal")
        lines.append(f"Journal reports round {state['round']}/{state['max_rounds']}, "
                     f"phase `{state['phase']}`, selected `{state['selected']}`, "
                     f"paused `{state['paused']}`; charged {state['charged_s']:.1f}/"
                     f"{state['budget_s']} worker-seconds. No acceptance inferred.")
        lines.append("Journal source: `run.json`; SHA-256: "
                     f"`{hashlib.sha256(journal.read_bytes()).hexdigest()}`.")
        live = [(key, task) for key, task in state['tasks'].items() if task['status'] == 'running']
        for key, task in live:
            lines.append(f"Live task `{key}` ({task['kind']}), owner `{task['actor']}`, "
                         f"handle `{task.get('handle')}`, deadline Unix `{task['deadline']}`.")
        if not live:
            lines.append("No live journal tasks.")
    else:
        lines.append("No exploration journal in this directory; graph is catalog-only.")
    return lines


OWNERS = {
    'KICAD-PLACEMENT': ('placement_reviewed', ['placement.py', 'check']),
    'KICAD-MATING-IMPORT': ('mating_clearance', ['routing.py', 'check', '--kind', 'mating']),
    'KICAD-ROUTING': ('routed_board', ['routing.py', 'check', '--kind', 'routing']),
    'KICAD-LAYOUT-SEAL': ('layout_sealed', ['layout_seal.py', 'check']),
    'JLC-FABRICATION': ('fabrication_staged', ['fabrication.py', 'check']),
}


def owning_check(project: Path, command: list[str]) -> None:
    result = subprocess.run(['/usr/bin/python3', str(ROOT/'tools'/command[0]),
                             *command[1:], '--project', str(project)],
                            capture_output=True, text=True)
    if result.returncode:
        raise WorkflowError((result.stderr or result.stdout).strip()[-800:])


def stage_rows(project, stages, current, verify_acceptance=False, checker=owning_check):
    coverage_path = ROOT/'skills/pcb-design/workflow/coverage.json'
    coverage = {v['stage_id']: v for v in json.loads(coverage_path.read_text())['stages']}
    lines = ['', '## Capability, reported progress and verified acceptance', '',
             '| Stage | Local capability | Reported current | Acceptance now |',
             '|---|---|---|---|']
    for stage in stages:
        sid = stage['spec']['id']; local = stage.get('local_execution')
        capability = ('definition only; execution unavailable' if stage.get('local_definition') else
                      ('local pilot: '+local['scope']) if local else (
            'local procedure' if coverage.get(sid, {}).get('backing') == 'local_procedure'
            else 'catalog/reference only'))
        acceptance = 'not checked by this view'
        if sid in OWNERS:
            role, command = OWNERS[sid]
            command=list(command)
            receipt=project/f'06_build/checkpoints/{role}.json'
            try:
                binding=project/'01_docs/routing-contract.json'
                if sid in {'KICAD-PLACEMENT','KICAD-MATING-IMPORT'} and binding.is_file():
                    contract=json.loads(binding.read_text())
                    selected=('placement' if sid=='KICAD-PLACEMENT' and contract.get('version') in (2,3)
                              else 'mating' if sid=='KICAD-MATING-IMPORT' and contract.get('version')==3 else None)
                    if selected:
                        name=contract.get(selected+'_receipt')
                        if (not isinstance(name,str) or not name or Path(name).is_absolute()
                                or '..' in Path(name).parts or str(Path(name))!=name
                                or not (project/name).resolve().is_relative_to(project.resolve())):
                            raise WorkflowError('invalid versioned '+selected+' receipt path')
                        receipt=project/name
                        if selected=='placement' and receipt.is_file() and hashlib.sha256(receipt.read_bytes()).hexdigest()!=contract.get('placement_receipt_sha256'):
                            raise WorkflowError('selected placement receipt hash differs from routing binding')
                        if selected=='placement':command.extend(['--receipt',name])
                if not receipt.is_file():
                    acceptance = 'no receipt'
                elif not verify_acceptance:
                    acceptance = 'receipt present; NOT verified'
                else:
                    checker(project, command); acceptance = 'owning check PASS'
            except (ValueError, OSError) as exc:
                acceptance = 'owning check FAILED: '+str(exc).replace('|', '/').replace('\n', ' ')
        lines.append(f"| {sid} | {capability} | {'yes (STATUS only)' if sid == current else '—'} | {acceptance} |")
    return lines


def render(project: Path, graph_path: Path = GRAPH, verify_acceptance=False, checker=owning_check) -> str:
    project = Path(project)
    if not project.is_absolute() or not project.is_dir():
        raise WorkflowError("project must be an existing absolute directory")
    stages, edges = _graph(graph_path)
    catalog = json.loads(graph_path.read_text(encoding="utf-8"))
    if (project / "run.json").is_file() and catalog.get("exploration"):
        return "\n".join(["# PCB exploration view", "", f"Project: `{project}`.",
                          *_exploration_view(project, catalog), "",
                          "Acceptance contracts remain in `graph.json`; no stage pass is inferred.", ""])
    current, status_note, status_source = _reported_stage(project)
    graph_hash = hashlib.sha256(graph_path.read_bytes()).hexdigest()
    lines = ["# PCB workflow view", "",
             "Catalog dependencies come from vNext `graph.json` stage artifacts. "
             "This is not an acceptance ledger; no completed or accepted stages are inferred.",
             "", f"Project: `{project.resolve()}`.",
             f"Graph source: `skills/pcb-design/workflow/graph.json`; SHA-256: `{graph_hash}`.",
             status_source, "", status_note, "",
             f"Supported standalone task bindings: `{STAGE}` / "
             + ", ".join(f"`{task}`" for task in TASK_INSTRUCTIONS if task != 'schematic-design')
             + ". Non-draft research tasks also support `PCB-ARCHITECTURE` after "
             "current commissioning receipt validation. `KICAD-SCHEMATIC` / `schematic-design` "
             "runs at STATUS schematic for explicitly migrated non-RF flat projects with current reviewed parts/source contract. "
             "These packets are not stage admission. "
             "Admission is a separate reviewed route where the project-bound skill supports it; "
             "The table below distinguishes local execution support from reported progress and acceptance.",
             "", "```mermaid", "flowchart LR"]
    for index, stage in enumerate(stages):
        stage_id = stage["spec"]["id"]
        label = _mermaid_label(stage_id + (" — CURRENT (reported)" if stage_id == current else ""))
        lines.append(f'    n{index}["{label}"]')
        if stage_id == current:
            lines.append(f"    class n{index} reportedCurrent")
    for source, target, artifact, condition in edges:
        label = artifact + (f" [if {condition}]" if condition else "")
        lines.append(f'    n{source} -->|"{_mermaid_label(label)}"| n{target}')
    lines.extend(["    classDef reportedCurrent fill:#fff2b2,stroke:#9b6a00,stroke-width:3px",
                  "```", "",
                  "Conditional edge labels describe the producing and/or consuming stage's "
                  "selection rule; they do not establish whether it applies to this project."])
    lines.extend(stage_rows(project, stages, current, verify_acceptance, checker))
    lines.extend(_exploration_view(project, catalog))
    guards = catalog.get("guards", [])
    if guards:
        lines.extend(["", "## Cross-stage guards", "",
                      "Procedural routing only; no automatic detection, backtracking or promotion."])
    for guard in guards:
        lines.extend(["", f"`{guard['id']}` — owner `{guard['owner']}`. "
                      f"Trigger: {guard['applies']}. Before: {guard['before']}.",
                      f"Instructions: `{guard['procedure']}`.",
                      "States: " + " → ".join(f"`{state}`" for state in guard["states"]) + ".",
                      "Recovery: " + "; ".join(f"{cause}: {action}" for cause, action
                                                in guard["recovery"].items()) + "."])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path, help="absolute project directory")
    parser.add_argument("--verify-acceptance", action="store_true", help="rerun supported owning checks; can take minutes")
    args = parser.parse_args(argv)
    try:
        print(render(args.project, verify_acceptance=args.verify_acceptance), end="")
    except (WorkflowError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"workflow view error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
