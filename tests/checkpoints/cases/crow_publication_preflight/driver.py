#!/usr/bin/env python3
"""Prepare and independently grade the Crow publication-preflight coupon."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
CANDIDATE = Path("06_build/candidates/crow-publication-v0.1")
REVIEW = Path("08_reviews/release-review")
RECEIPT = REVIEW / "packet-receipt.json"
COMMISSION = REVIEW / "commission.json"
ENVELOPE = REVIEW / "envelope.json"
DEFERRED = (
    "verification/pin_review.md",
    "verification/redteam_layout.md",
    "verification/redteam_topology.md",
    "verification/render_review.md",
)
EVIDENCE_PAYLOAD = b"bounded synthetic review evidence\n"


def emit(outcome, findings=(), evidence=None, rc=None):
    payload = {
        "schema": 1,
        "outcome": outcome,
        "findings": [{"code": code, "message": message}
                     for code, message in findings],
    }
    if evidence is not None:
        payload["evidence"] = evidence
    print(json.dumps(payload, sort_keys=True))
    return rc if rc is not None else (0 if outcome == "PASS" else 1)


def run(workspace, *args, check=True):
    return subprocess.run(args, cwd=workspace, text=True, capture_output=True,
                          check=check)


def git(workspace, *args):
    return run(workspace, "git", *args).stdout.strip()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_manifest(workspace):
    release = workspace / CANDIDATE
    records = []
    for path in sorted(release.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.txt":
            records.append((path.relative_to(release).as_posix(), sha(path)))
    text = [
        "MANIFEST — synthetic Crow publication preflight candidate v0.1",
        "", "board:        crow_publication_coupon", "version:      v0.1",
        "status:       REVIEW PENDING", "ordered:      false", "", "sha256:",
    ]
    text.extend(f"  {name}  {digest}" for name, digest in records)
    (release / "MANIFEST.txt").write_text("\n".join(text) + "\n")


def nested_zip(path, depth):
    data = EVIDENCE_PAYLOAD
    name = "leaf.txt"
    for index in range(depth):
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(name, data)
        data = stream.getvalue()
        name = f"level-{depth - index - 1}.zip"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def logical_evidence_preserved(path):
    """Reopen logical content while allowing any deterministic repack bytes."""
    try:
        data = path.read_bytes()
        while data.startswith(b"PK\x03\x04"):
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                members = [row for row in archive.infolist() if not row.is_dir()]
                if len(members) != 1:
                    return False
                data = archive.read(members[0])
        return data == EVIDENCE_PAYLOAD
    except (OSError, RuntimeError, zipfile.BadZipFile):
        return False


def load_modules(repo):
    design = repo / "skills/pcb-design/scripts"
    kicad = repo / "skills/kicad-pcb/scripts"
    for source in (design, kicad):
        if str(source) not in sys.path:
            sys.path.insert(0, str(source))
    import release_review_preflight as pre
    import pcb_flow
    from pipeline_execution import TaskEnvelope
    return pre, pcb_flow, TaskEnvelope


def live_paths(pcb_flow, workspace):
    ctx = pcb_flow.resolve_context(workspace)
    return [ctx.board, *pcb_flow.build_source_files(ctx)]


def packet_item(project, name, path):
    data = path.read_bytes()
    return {"name": name, "path": path.relative_to(project).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}


def write_assertions(repo, workspace):
    pre, pcb_flow, _ = load_modules(repo)
    receipt_path = workspace / RECEIPT
    commission_path = workspace / COMMISSION
    envelope_path = workspace / ENVELOPE
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    source_commit = git(workspace, "rev-parse", "HEAD")
    receipt = pre.build_packet_receipt(
        workspace, workspace, workspace / CANDIDATE,
        source_commit=source_commit, live_paths=live_paths(pcb_flow, workspace))
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
    now = datetime.now(timezone.utc)
    stamp = lambda value: value.isoformat(timespec="seconds").replace("+00:00", "Z")
    commission = {
        "schema": 1, "commission_id": "R-RELEASE-1",
        "project": workspace.name, "source_commit": source_commit,
        "subject": receipt["subject"], "lens": "release_packet",
        "checklist": ["candidate_identity"], "exclusions": [],
        "artifacts": [{"path": row["path"], "sha256": row["sha256"]}
                      for row in receipt["artifacts"]],
        "output_path": "08_reviews/release_packet.json",
        "issued_at": stamp(now), "deadline_at": stamp(now + timedelta(hours=6)),
    }
    commission_path.write_text(json.dumps(commission, sort_keys=True) + "\n")
    packet = [packet_item(workspace, f"artifact_{index:04d}",
                          workspace / row["path"])
              for index, row in enumerate(receipt["artifacts"])]
    packet.extend((packet_item(workspace, "commission", commission_path),
                   packet_item(workspace, "packet_receipt", receipt_path)))
    envelope = {
        "schema": 2, "task_id": "release-review", "stage_id": "PCB-RELEASE-REVIEW",
        "run_id": "run-1", "subject": receipt["subject"], "executor": "reviewer",
        "execution_class": "review_wait", "recommended_agent_role": "judgment",
        "agent_role": "judgment", "role_escalation_reason": None,
        "context_mode": "FRESH", "input_handoff_id": "release-packet",
        "input_packet": sorted(packet, key=lambda row: row["name"]),
        "deadline_at": stamp(now + timedelta(hours=6)),
        "max_nonimproving_attempts": 1, "replacement_limit": 0,
        "writer_scope": {"mode": "READ_ONLY", "paths": []},
        "output_path": "06_build/task_runs/placeholder/attempt.json",
        "completion": {"outputs": ["answer.txt"],
                       "checks": ["candidate_identity"]},
        "repair": None,
    }
    envelope_path.write_text(json.dumps(envelope, sort_keys=True) + "\n")


def prepare(repo, workspace):
    nested_zip(workspace / CANDIDATE / "verification/evidence.zip", 5)
    write_manifest(workspace)
    git(workspace, "init", "-q")
    git(workspace, "config", "user.name", "Checkpoint Fixture")
    git(workspace, "config", "user.email", "fixture@example.invalid")
    (workspace / ".transport-base").write_text("isolated fixture base\n")
    git(workspace, "add", ".transport-base")
    git(workspace, "commit", "-q", "-m", "fixture transport base")
    base = git(workspace, "rev-parse", "HEAD")
    (workspace / REVIEW / "transport-base.txt").write_text(base + "\n")
    staged = [
        "02_parts", "03_src", "03_tscircuit", "04_kicad", "07_releases", "HANDOFF.md",
        str(CANDIDATE / "MANIFEST.txt"), str(CANDIDATE / "fab/board.gbr"),
        str(CANDIDATE / "source/board.kicad_pcb"),
        str(CANDIDATE / "verification/pre_review_gate.json"),
        str(CANDIDATE / "verification/evidence.zip"),
    ]
    git(workspace, "add", *staged)
    git(workspace, "commit", "-q", "-m", "stale review packet")
    write_assertions(repo, workspace)
    board = workspace / "04_kicad/crow_publication_coupon.kicad_pcb"
    board.write_text(board.read_text() + "; current producer edit after saved review context\n")
    return emit("PASS", evidence={
        "git_fixture": "isolated", "transport_base": base,
        "required_untracked": str(CANDIDATE / "fab/board-PTH.drl"),
        "archive_depth": 5,
    })


def apply_reference(repo, workspace):
    nested_zip(workspace / CANDIDATE / "verification/evidence.zip", 1)
    shutil.copy2(workspace / "04_kicad/crow_publication_coupon.kicad_pcb",
                 workspace / CANDIDATE / "source/board.kicad_pcb")
    write_manifest(workspace)
    git(workspace, "add", "04_kicad", str(CANDIDATE))
    git(workspace, "commit", "-q", "-m", "coherent bounded review packet")
    write_assertions(repo, workspace)
    (workspace / "HANDOFF.md").write_text(
        "Production release-review preflight is READY for the exact current "
        "candidate and bounded recipient-visible Git population. Reviewer output, "
        "seal, publication, remote verification and ordering remain deferred.\n")
    return emit("PASS", evidence={"reference_repair": "applied"})


def apply_bypass(repo, workspace):
    apply_reference(repo, workspace)
    required = workspace / CANDIDATE / "verification/pre_review_gate.json"
    required.unlink()
    write_manifest(workspace)
    git(workspace, "add", "-A", str(CANDIDATE))
    git(workspace, "commit", "-q", "-m", "invalid evidence-dropping shortcut")
    write_assertions(repo, workspace)
    (workspace / "HANDOFF.md").write_text(
        "Deleted required evidence and refreshed self-consistent prose and hashes; "
        "the independent required-artifact check must refuse this shortcut.\n")
    return emit("PASS", evidence={"invalid_shortcut": "dropped required evidence"})


def admission(repo, workspace):
    pre, pcb_flow, TaskEnvelope = load_modules(repo)
    envelope = TaskEnvelope.from_json((workspace / ENVELOPE).read_text())
    base = (workspace / REVIEW / "transport-base.txt").read_text().strip()
    result = pre.assess(
        workspace, workspace, workspace / CANDIDATE, envelope,
        workspace / COMMISSION, workspace / RECEIPT,
        live_paths=live_paths(pcb_flow, workspace), transport_base=base,
        transport_head="HEAD")
    return result, envelope, pcb_flow, base


def open_boundary(workspace, envelope, pcb_flow, base):
    calls = []

    def fake_opener(actual, *, cwd):
        calls.append((actual, Path(cwd)))
        parent = Path(cwd) / Path(actual.output_path).parent
        return {"attempt": str(parent / "attempt.json"),
                "envelope_sha256": "fixture-recorder",
                "output_dir": str(parent / "outputs"),
                "scratch_dir": str(parent / "scratch"),
                "deadline_at": actual.deadline_at}

    argv = [
        "agent-open", str(workspace), "--envelope", str(workspace / ENVELOPE),
        "--review-commission", str(workspace / COMMISSION),
        "--review-packet-receipt", str(workspace / RECEIPT),
        "--review-release", str(CANDIDATE), "--transport-base", base,
    ]
    output = io.StringIO()
    with patch("pipeline_runtime.open_agent_attempt", fake_opener), \
            contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        rc = pcb_flow.main(argv)
    return rc, len(calls), output.getvalue()


def grade(repo, workspace):
    try:
        result, envelope, pcb_flow, base = admission(repo, workspace)
        rc, opened, flow_output = open_boundary(workspace, envelope, pcb_flow, base)
    except Exception as exc:
        return emit("ERROR", [("GRADER-OPERATION", str(exc))], rc=2)
    findings = []
    seen = set()
    for row in result.findings:
        if row.code not in seen:
            findings.append((row.code, row.detail)); seen.add(row.code)
    if result.status != "READY":
        if opened:
            findings.append(("REVIEW-ALLOCATED-AFTER-REFUSAL",
                             "actual pcb_flow agent-open reached its opener"))
        else:
            findings.append(("REVIEW-NOT-ALLOCATED",
                             "preflight refused before attempt allocation"))
    elif rc != 0 or opened != 1:
        findings.append(("REVIEW-ALLOCATION-BOUNDARY",
                         f"READY boundary rc={rc}, opener calls={opened}"))
    release = workspace / CANDIDATE
    premature = [path for path in DEFERRED if (release / path).exists()]
    if premature or (workspace / "07_releases/sealed").exists():
        findings.append(("FINAL-GATE-BYPASS",
                         f"preflight materialized later outputs: {premature}"))
    if not logical_evidence_preserved(
            release / "verification/evidence.zip"):
        findings.append(("EVIDENCE-CONTENT",
                         "required logical review evidence was dropped or changed"))
    if findings:
        return emit("FAIL", findings, {
            "preflight": result.to_mapping(), "opener_calls": opened,
            "pcb_flow_exit": rc, "pcb_flow_tail": flow_output[-2000:],
            "host_reviewer_called": False,
        })
    if tuple(result.deferred_review_outputs) != DEFERRED:
        return emit("FAIL", [("DEFERRED-OUTPUT-CENSUS",
                              "READY did not defer exactly four review outputs")])
    return emit("PASS", evidence={
        "preflight": result.to_mapping(), "opener_calls": opened,
        "host_reviewer_called": False, "production_complete": False,
        "later_gates": ["review verdict", "release rehearsal", "release seal",
                        "publication", "remote verification"],
    })


def main():
    mode, repo, workspace = sys.argv[1:4]
    repo, workspace = Path(repo).resolve(), Path(workspace).resolve()
    if mode == "prepare":
        return prepare(repo, workspace)
    if mode == "reference":
        return apply_reference(repo, workspace)
    if mode == "bypass":
        return apply_bypass(repo, workspace)
    if mode == "grade":
        return grade(repo, workspace)
    return emit("ERROR", [("MODE", f"unknown mode {mode}")], rc=2)


if __name__ == "__main__":
    raise SystemExit(main())
