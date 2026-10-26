#!/usr/bin/env python3
"""Initialize a fresh commissioning project from explicit raw user inputs.

This creates records, not interpreted requirements or engineering acceptance.
It has no dependency on replay fixtures, legacy tools, or a particular board.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys


RAW_PROMPT = "01_docs/inputs/PROMPT.md"
RAW_DECISIONS = "01_docs/inputs/USER_DECISIONS.md"
CAPABILITY = "01_docs/capability-profile.json"


def initialize(project: Path, prompt: Path, decisions: Path,
               capability: Path) -> Path:
    """Create only in an absent or empty absolute directory; never overwrite.

    All inputs are read and validated before creating anything. Source bytes
    are copied unchanged, including whitespace and line endings. The caller
    supplies chronological decisions; this tool does not interpret their order.
    """
    project = Path(project)
    if not project.is_absolute():
        raise ValueError("project must be an absolute directory")
    if project.is_symlink() or (project.exists() and
            (not project.is_dir() or any(project.iterdir()))):
        raise ValueError("project destination must be absent or an empty directory, not a symlink")
    sources = {RAW_PROMPT: Path(prompt), RAW_DECISIONS: Path(decisions),
               CAPABILITY: Path(capability)}
    raw = {name: source.read_bytes() for name, source in sources.items()}
    for name, data in raw.items():
        data.decode("utf-8")
        if not data.strip():
            raise ValueError(f"input must not be empty: {name}")
    if not isinstance(json.loads(raw[CAPABILITY]), dict):
        raise ValueError("capability profile must be a JSON object")
    hashes = {name: hashlib.sha256(data).hexdigest() for name, data in raw.items()}
    provenance = "\n".join(
        f"- `{name}` — SHA-256 `{digest}`" for name, digest in hashes.items())
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    documents = {
        "01_docs/BRIEF.md": f"""# Commissioning brief

## Raw user inputs — authoritative, not yet interpreted

The original prompt, chronological decisions and capability profile are
preserved byte-for-byte at the following project-relative paths. Read them
before deriving requirements; the hashes identify this initial source snapshot.

{provenance}

Later decisions must explicitly identify what they supersede; preserve earlier
sources. Do not infer that every statement in a raw input is an accepted fact.

## Interpreted requirements and acceptance criteria

Not yet extracted or reviewed. No engineering acceptance is established by
initialization. Add each requirement with a source location (and decision ID
where present), separating user-confirmed facts from engineering interpretation.
Preserve the user's scope, model preferences, authorization and phase stops.

## Assumptions and unresolved questions

Not yet assessed. Record proposed assumptions separately from external unknowns;
give each open item a question, evidence owner and closure condition. Do not
invent component choices, numerical envelopes or acceptance criteria.
""",
        "01_docs/STATUS.md": f"""# Project status

<!-- reader parses from here down -->
stage: commission
step: intake
measure: raw inputs preserved; interpretation pending
state: working
next: read raw sources and reconcile requirements under commissioning hold
op_pid:
updated: {now}
""",
        "01_docs/COMMISSIONING-HOLD.md": """# Commissioning hold

ACTIVE. Raw inputs have been preserved, not accepted as an engineering design.
Requirements, applicability, feasibility and independent review remain pending.
Initialization and task packets do not admit any stage. Keep this hold in place;
follow the local commissioning contract before further bounded work. No stage
promotion or downstream production is authorized by this scaffold.
""",
        "01_docs/journal/commission.md": f"""# Commissioning journal

## {now} — project initialization

Actor: tools/bootstrap.py. Stage: commission. Result: raw inputs copied and
local project records created; interpretation and independent review pending.
No design/research attempt was dispatched or completed; no stage was accepted.
Initial source hashes are recorded in ../BRIEF.md. Next: reconcile the raw
prompt and chronological decisions, identify scope/stops and missing facts.
""",
        "contracts.md": """# Project contract

This is a local vNext commissioning project. Read 01_docs/BRIEF.md and its raw
sources, STATUS.md, COMMISSIONING-HOLD.md and journal/commission.md before work.
Raw source files are immutable snapshots; preserve subsequent decisions as new
evidence and explicitly reconcile supersession in BRIEF.md. Preserve user scope
and phase stops. No purchase, vendor message, hardware experiment or production
CAD is authorized by initialization. No stage is accepted by these records.
""",
        "01_docs/contracts.md": """# Document contract

BRIEF.md owns source provenance and the distinction between confirmed facts,
interpretations, assumptions and unknowns. The coordinator updates BRIEF.md,
STATUS.md and the commissioning journal; preserve raw inputs and prior evidence.
STATUS.md is the live view, with exactly the seven fields after its reader
marker: stage, step, measure, state, next, op_pid and updated. Keep commission
working or blocked under the hold until an implemented owning verifier and
authorized promotion consumer establish otherwise. Reports are not acceptance.
""",
        "01_docs/reports/contracts.md": """# Report contract

One author writes each dated report. Identify its bounded question, exact input
paths/hashes, primary sources, assumptions, calculations, findings, unknowns and
next discriminating action. Separate a candidate result from accepted evidence.
Independent review consumes the exact report bytes and primary sources, checks
critical reasoning, and records findings against the report hash in the journal.
A repair invalidates the prior review; preserve failed attempts and revisions.
Software checks do not establish physical assumptions or stage acceptance.
""",
        "01_docs/journal/contracts.md": """# Journal contract

commission.md is the append-only history and sole progress ledger. The
coordinator records stable run/task/attempt IDs, actual dispatch/completion
times, actor, stage, exact outputs and review results when work occurs. Record
backtracks with their cause, destination and affected evidence. Preserve spent
attempt budgets and failed outputs across handoffs. Queued work is not dispatched
work, and task completion is not stage acceptance. Do not create a second ledger.
""",
    }
    payloads = {**raw, **{name: text.encode("utf-8")
                         for name, text in documents.items()}}
    project.mkdir(parents=True, exist_ok=True)
    # Recheck after input reads; exclusive creates also refuse any colliding
    # file introduced after preflight. There is deliberately no overwrite mode.
    if project.is_symlink() or any(project.iterdir()):
        raise ValueError("project destination must still be empty")
    for name, data in payloads.items():
        path = project / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as stream:
            stream.write(data)
    return project.resolve()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path,
                        help="chronological user decisions (explicitly state if none)")
    parser.add_argument("--capability", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        project = initialize(args.project, args.prompt, args.decisions, args.capability)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"project initialization error: {exc}", file=sys.stderr)
        return 2
    print(f"Initialized {project}; commission working, hold active; no stage accepted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
