#!/usr/bin/env python3
"""T1: exact release packets are admitted before costly review allocation."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import (KPY, ROOT, check, eq, main, must_pass, run, test,  # noqa: E402
                     tmpdir)

DESIGN = ROOT / "skills/pcb-design/scripts"
KICAD = ROOT / "skills/kicad-pcb/scripts"
for source in (DESIGN, KICAD):
    sys.path.insert(0, str(source))

import pipeline_runtime  # noqa: E402
import release_review_preflight as preflight  # noqa: E402
from pipeline_execution import TaskEnvelope  # noqa: E402


CONTRACT = """```
07_releases/
└── <version>-<date>/
    ├── MANIFEST.txt REQUIRED
    ├── ORDER_README.md required
    ├── fab/ REQUIRED
    │   └── <board>.drl drill
    └── verification/ REQUIRED
        ├── pin_review.md future
        ├── render_review.md future
        ├── redteam_topology.md future
        ├── redteam_layout.md future
        └── parity.md machine
```
"""


def git(root, *args):
    return must_pass(run(["git", *args], cwd=root), f"git {' '.join(args)}").out.strip()


def commit(root, message):
    git(root, "add", "-A")
    git(root, "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def record(project, path, name):
    data = path.read_bytes()
    return {"name": name, "path": path.relative_to(project).as_posix(),
            "sha256": hashlib.sha256(data).hexdigest(), "size": len(data)}


def load_flow():
    spec = importlib.util.spec_from_file_location(
        "release_review_flow_under_test", KICAD / "pcb_flow.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fixture():
    repo = tmpdir("release_review_")
    for args in (("init", "-q"), ("config", "user.email", "test@example.invalid"),
                 ("config", "user.name", "Release Review Test")):
        git(repo, *args)
    project = repo / "projects/demo"
    for rel in ("02_parts/X", "03_src/rules", "03_tscircuit/src", "04_kicad",
                "06_build/candidates/demo-v1/fab",
                "06_build/candidates/demo-v1/source",
                "06_build/candidates/demo-v1/verification", "07_releases"):
        (project / rel).mkdir(parents=True, exist_ok=True)
    route = {
        "project": {"name": "demo", "board": "04_kicad/demo.kicad_pcb",
                    "build_dir": "06_build/route"},
        "route": {"waves": [], "final": "03_src/route/r1.kicad_pcb"},
        "stitch": {"seed_stubs": {"stubs": []}},
        "flow": {"owner": {"stage": "routing", "files": ["03_src/route.yaml"]},
                 "copper": {"deterministic": [], "stochastic": []},
                 "budgets_s": {}, "inputs": {"include": ["03_src", "03_tscircuit"],
                                                "parts": ["02_parts/X"]}},
    }
    (project / "03_src/route.yaml").write_text(yaml.safe_dump(route, sort_keys=False))
    (project / "03_src/rebuild_all.sh").write_text("#!/bin/sh\nexit 0\n")
    (project / "03_src/rules/nets.yaml").write_text("schema: 1\n")
    (project / "03_tscircuit/src/demo.tsx").write_text("export const demo = 1\n")
    (project / "02_parts/X/part.yaml").write_text("mpn: X\n")
    for suffix in (".kicad_pcb", ".kicad_sch", ".kicad_pro", ".kicad_dru"):
        (project / f"04_kicad/demo{suffix}").write_text(f"demo {suffix}\n")
    (project / "07_releases/contracts.md").write_text(CONTRACT)
    source = commit(repo, "source")

    release = project / "06_build/candidates/demo-v1"
    (release / "ORDER_README.md").write_text("DRAFT DO-NOT-ORDER\n")
    (release / "fab/demo.drl").write_text("M48\n")
    (release / "source/demo.kicad_pcb").write_bytes(
        (project / "04_kicad/demo.kicad_pcb").read_bytes())
    (release / "verification/parity.md").write_text("PASS\n")
    payloads = [release / "ORDER_README.md", release / "fab/demo.drl",
                release / "source/demo.kicad_pcb",
                release / "verification/parity.md"]
    (release / "MANIFEST.txt").write_text(
        "git_sha: " + source + "\ngit_dirty: false\nsha256:\n" +
        "".join(f"  {path.relative_to(release).as_posix()}  "
                f"{hashlib.sha256(path.read_bytes()).hexdigest()}\n"
                for path in payloads))
    head = commit(repo, "candidate")

    flow = load_flow()
    ctx = flow.resolve_context(project)
    live = [ctx.board, *flow.build_source_files(ctx)]
    packet_dir = project / "06_build/release_review_packet"
    packet_dir.mkdir()
    receipt = preflight.build_packet_receipt(
        repo, project, release, source_commit=source, live_paths=live)
    receipt_path = packet_dir / "packet.json"
    receipt_path.write_text(json.dumps(receipt, sort_keys=True) + "\n")
    commission = {
        "schema": 1, "commission_id": "R-RELEASE-1", "project": project.name,
        "source_commit": source, "subject": receipt["subject"],
        "lens": "release_packet", "checklist": ["candidate_identity"],
        "exclusions": [],
        "artifacts": [{"path": row["path"], "sha256": row["sha256"]}
                      for row in receipt["artifacts"]],
        "output_path": "08_reviews/release_packet.json",
        "issued_at": "2026-09-20T12:00:00Z",
        "deadline_at": "2099-09-20T13:00:00Z",
    }
    commission_path = packet_dir / "commission.json"
    commission_path.write_text(json.dumps(commission, sort_keys=True) + "\n")
    items = [record(project, project / row["path"], f"artifact_{index:04d}")
             for index, row in enumerate(receipt["artifacts"])]
    items.extend((record(project, commission_path, "commission"),
                  record(project, receipt_path, "packet_receipt")))
    envelope_value = {
        "schema": 2, "task_id": "release-review",
        "stage_id": "PCB-RELEASE-REVIEW", "run_id": "run-1",
        "subject": receipt["subject"], "executor": "reviewer",
        "execution_class": "review_wait", "recommended_agent_role": "judgment",
        "agent_role": "judgment", "role_escalation_reason": None,
        "context_mode": "FRESH", "input_handoff_id": "release-packet",
        "input_packet": sorted(items, key=lambda row: row["name"]),
        "deadline_at": "2099-09-20T13:00:00Z",
        "max_nonimproving_attempts": 1, "replacement_limit": 0,
        "writer_scope": {"mode": "READ_ONLY", "paths": []},
        "output_path": "06_build/task_runs/placeholder/attempt.json",
        "completion": {"outputs": ["answer.txt"],
                       "checks": ["candidate_identity"]}, "repair": None,
    }
    envelope_path = packet_dir / "envelope.json"
    envelope_path.write_text(json.dumps(envelope_value, sort_keys=True) + "\n")
    return {"repo": repo, "project": project, "release": release,
            "source": source, "head": head, "live": live, "flow": flow,
            "receipt": receipt_path, "commission": commission_path,
            "envelope": envelope_path,
            "envelope_object": TaskEnvelope.from_mapping(envelope_value)}


def assess(f):
    return preflight.assess(
        f["repo"], f["project"], f["release"], f["envelope_object"],
        f["commission"], f["receipt"], live_paths=f["live"],
        authoritative_board=f["project"] / "04_kicad/demo.kicad_pcb",
        transport_base=f["source"], transport_head=f["head"])


@test("complete exact candidate is ready without completed review outputs")
def t_ready():
    result = assess(fixture())
    eq(result.status, "READY", f"clean packet refused: {result.to_mapping()}")
    eq(tuple(result.deferred_review_outputs),
       ("verification/pin_review.md", "verification/redteam_layout.md",
        "verification/redteam_topology.md", "verification/render_review.md"),
       "exact future review outputs")


@test("three mutually matching stale assertions cannot admit current source",
      kind="known_bad")
def t_stale_all_three():
    f = fixture()
    (f["project"] / "04_kicad/demo.kicad_pcb").write_text("changed current board\n")
    result = assess(f)
    eq(result.status, "REFUSED", "stale packet was not an engineering refusal")
    codes = {row.code for row in result.findings}
    check({"RP-SUBJECT", "RP-SOURCE"} <= codes,
          f"stale current authority was not diagnosed: {result.to_mapping()}")


@test("staged source board must equal the authoritative current board",
      kind="known_bad")
def t_staged_board_stale():
    f = fixture()
    (f["release"] / "source/route_chain_r3.kicad_pcb").write_bytes(
        (f["project"] / "04_kicad/demo.kicad_pcb").read_bytes())
    (f["release"] / "source/demo.kicad_pcb").write_text("stale staged board\n")
    result = assess(f)
    eq(result.status, "REFUSED", "stale staged source board was admitted")
    check(any(row.code == "RP-SOURCE" and "staged source board differs" in row.detail
              for row in result.findings),
          f"source-board relation was not diagnosed: {result.to_mapping()}")


@test("additional staged route boards remain covered candidate evidence")
def t_additional_staged_board_allowed():
    f = fixture()
    extra = f["release"] / "source/route_chain_r3.kicad_pcb"
    extra.write_text("preserved route evidence\n")
    payloads = [path for path in f["release"].rglob("*")
                if path.is_file() and path.name != "MANIFEST.txt"]
    (f["release"] / "MANIFEST.txt").write_text(
        "git_sha: " + f["source"] + "\ngit_dirty: false\nsha256:\n" +
        "".join(f"  {path.relative_to(f['release']).as_posix()}  "
                f"{hashlib.sha256(path.read_bytes()).hexdigest()}\n"
                for path in sorted(payloads)))
    f["head"] = commit(f["repo"], "preserve additional route board")
    receipt = preflight.build_packet_receipt(
        f["repo"], f["project"], f["release"], source_commit=f["source"],
        live_paths=f["live"])
    f["receipt"].write_text(json.dumps(receipt, sort_keys=True) + "\n")
    commission = json.loads(f["commission"].read_text())
    commission["subject"] = receipt["subject"]
    commission["artifacts"] = [
        {"path": row["path"], "sha256": row["sha256"]}
        for row in receipt["artifacts"]]
    f["commission"].write_text(json.dumps(commission, sort_keys=True) + "\n")
    envelope = json.loads(f["envelope"].read_text())
    envelope["subject"] = receipt["subject"]
    envelope["input_packet"] = [
        record(f["project"], f["project"] / row["path"], f"artifact_{index:04d}")
        for index, row in enumerate(receipt["artifacts"])]
    envelope["input_packet"].extend((
        record(f["project"], f["commission"], "commission"),
        record(f["project"], f["receipt"], "packet_receipt")))
    envelope["input_packet"].sort(key=lambda row: row["name"])
    f["envelope_object"] = TaskEnvelope.from_mapping(envelope)
    result = assess(f)
    eq(result.status, "READY",
       f"additional staged route evidence was rejected: {result.to_mapping()}")


@test("future review outputs must be absent before review", kind="known_bad")
def t_fake_future_review_output():
    f = fixture()
    (f["release"] / "verification/pin_review.md").write_text("SOUND\n")
    result = assess(f)
    eq(result.status, "REFUSED", "preexisting future review output was admitted")
    check(any(row.code == "RP-REQUIRED" and "must be absent" in row.detail
              for row in result.findings),
          f"preexisting future output not diagnosed: {result.to_mapping()}")


@test("envelope packet denominator rejects unrelated extras", kind="known_bad")
def t_packet_extra():
    f = fixture()
    value = json.loads(f["envelope"].read_text())
    value["input_packet"].append(record(
        f["project"], f["project"] / "04_kicad/demo.kicad_pcb", "unrelated"))
    value["input_packet"].sort(key=lambda row: row["name"])
    f["envelope_object"] = TaskEnvelope.from_mapping(value)
    result = assess(f)
    eq(result.status, "REFUSED", "extra packet scope was admitted")
    check(any(row.code == "RP-ARTIFACT" and "extra=" in row.detail
              for row in result.findings),
          f"extra packet member not diagnosed: {result.to_mapping()}")


@test("packet denominator cannot omit a candidate artifact", kind="known_bad")
def t_packet_member_missing():
    f = fixture()
    value = json.loads(f["envelope"].read_text())
    value["input_packet"] = [row for row in value["input_packet"]
                             if row["path"] != "06_build/candidates/demo-v1/fab/demo.drl"]
    f["envelope_object"] = TaskEnvelope.from_mapping(value)
    result = assess(f)
    eq(result.status, "REFUSED", "incomplete packet denominator passed")
    check(any(row.code == "RP-ARTIFACT" for row in result.findings),
          f"missing packet member not diagnosed: {result.to_mapping()}")


@test("missing release file is distinct from an omitted packet declaration",
      kind="known_bad")
def t_release_member_missing():
    f = fixture()
    (f["release"] / "fab/demo.drl").unlink()
    result = assess(f)
    eq(result.status, "REFUSED", "missing required release file passed")
    codes = {row.code for row in result.findings}
    check({"RP-REQUIRED", "RP-MANIFEST"} <= codes,
          f"release absence collapsed into packet omission: {result.to_mapping()}")


@test("candidate artifact absent from recipient Git tree is refused",
      kind="known_bad")
def t_recipient_git_member_missing():
    f = fixture()
    relative = "projects/demo/06_build/candidates/demo-v1/fab/demo.drl"
    git(f["repo"], "rm", "--cached", relative)
    git(f["repo"], "commit", "-qm", "omit candidate payload")
    f["head"] = git(f["repo"], "rev-parse", "HEAD")
    result = assess(f)
    eq(result.status, "REFUSED", "worktree-only candidate artifact passed")
    check(any(row.code == "RP-GIT" for row in result.findings),
          f"recipient-visible omission not diagnosed: {result.to_mapping()}")


@test("unrelated later documentation commit does not stale source origin")
def t_unrelated_commit_allowed():
    f = fixture()
    (f["repo"] / "README.md").write_text("unrelated publication note\n")
    f["head"] = commit(f["repo"], "unrelated docs")
    result = assess(f)
    eq(result.status, "READY",
       f"unrelated later commit invalidated scoped source: {result.to_mapping()}")


def agent_args(f):
    return ["agent-open", str(f["project"]), "--envelope", str(f["envelope"]),
            "--review-commission", str(f["commission"]),
            "--review-packet-receipt", str(f["receipt"]),
            "--review-release", "06_build/candidates/demo-v1",
            "--transport-base", f["source"], "--transport-head", f["head"]]


@test("agent-open refuses invalid release packet before opener allocation",
      kind="known_bad")
def t_agent_open_refuses_before_allocation():
    f = fixture()
    (f["project"] / "04_kicad/demo.kicad_pcb").write_text("stale\n")
    calls = []
    original = pipeline_runtime.open_agent_attempt
    pipeline_runtime.open_agent_attempt = lambda *args, **kwargs: calls.append(args) or {}
    try:
        rc = f["flow"].main(agent_args(f))
    finally:
        pipeline_runtime.open_agent_attempt = original
    eq(rc, 1, "invalid packet agent-open result")
    eq(calls, [], "invalid packet reached expensive reviewer allocation")


@test("agent-open allocates exactly once after valid release preflight")
def t_agent_open_valid_once():
    f = fixture()
    calls = []
    original = pipeline_runtime.open_agent_attempt
    pipeline_runtime.open_agent_attempt = lambda *args, **kwargs: calls.append(args) or {
        "attempt": "recorded", "envelope_sha256": "a" * 64,
        "output_dir": "recorded", "scratch_dir": "recorded",
        "deadline_at": "2099-09-20T13:00:00Z"}
    try:
        rc = f["flow"].main(agent_args(f))
    finally:
        pipeline_runtime.open_agent_attempt = original
    eq(rc, 0, "valid packet agent-open result")
    eq(len(calls), 1, "valid packet allocation count")


@test("release-review stage rejects a non-reviewer before allocation",
      kind="known_bad")
def t_agent_open_rejects_wrong_executor():
    f = fixture()
    value = json.loads(f["envelope"].read_text())
    value["executor"] = "agent"
    f["envelope"].write_text(json.dumps(value, sort_keys=True) + "\n")
    calls = []
    original = pipeline_runtime.open_agent_attempt
    pipeline_runtime.open_agent_attempt = lambda *args, **kwargs: calls.append(args) or {}
    try:
        rc = f["flow"].main(agent_args(f))
    finally:
        pipeline_runtime.open_agent_attempt = original
    eq(rc, 1, "wrong release-review executor result")
    eq(calls, [], "wrong executor reached reviewer allocation")


@test("immutable pre-fix agent-open allocates the same stale packet",
      kind="known_bad")
def t_prefixed_red_actual_old_agent_open():
    f = fixture()
    (f["project"] / "04_kicad/demo.kicad_pcb").write_text("stale\n")
    old = tmpdir("release_review_old_flow_")
    files = (
        "skills/kicad-pcb/scripts/pcb_flow.py",
        "skills/kicad-pcb/scripts/process_runner.py",
        "skills/pcb-design/scripts/pipeline_runtime.py",
        "skills/pcb-design/scripts/pipeline_execution.py",
        "skills/pcb-design/scripts/pipeline_identity.py",
    )
    for relative in files:
        target = old / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        content = subprocess.run(
            ["git", "show", f"6fdf970a:{relative}"], cwd=ROOT,
            capture_output=True, check=True).stdout
        target.write_bytes(content)
    result = run([KPY, old / "skills/kicad-pcb/scripts/pcb_flow.py",
                  "agent-open", f["project"], "--envelope", f["envelope"]])
    eq(result.rc, 0, f"immutable pre-fix did not reproduce admission: {result.out}")
    check(any((f["project"] / "06_build/task_runs").iterdir()),
          "immutable pre-fix did not allocate a stale reviewer packet")


if __name__ == "__main__":
    sys.exit(main())
