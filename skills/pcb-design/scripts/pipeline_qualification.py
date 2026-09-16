"""Compose bounded compatibility probes and separately observed reviewer availability.

Cache only successful native probes on exact tool/library/probe identities.
Repository audits run separately, so their source freshness never rides on that
cache. A cached compatibility result never asserts current reviewer availability.
"""
from __future__ import annotations
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import uuid
from pipeline_execution import TaskEnvelope
from pipeline_identity import TypedIdentityInput, subject_identity
from pipeline_runtime import execute_attempt, _file_sha256, run_stage

REPO = Path(__file__).resolve().parents[3]
PROBE = REPO / "skills/kicad-pcb/scripts/qualification_probe.py"


def fingerprint(files, configuration):
    """Hash actual covered files, including shared objects; no mtime shortcut."""
    records = {str(Path(p).resolve(strict=True)): _file_sha256(Path(p)) for p in files}
    payload = {"files": records, "configuration": configuration}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    return digest, payload


def cached_native(path, digest):
    try:
        receipt = json.loads(Path(path).read_text())
        if receipt["fingerprint"] != digest or receipt["status"] != "PASS":
            return None
        for name, sha in receipt["evidence"].items():
            if _file_sha256(Path(name)) != sha:
                return None
        if not receipt["evidence"]:
            return None
        return receipt
    except (OSError, ValueError, KeyError, TypeError):
        return None


def qualify(root: Path, *, python="/usr/bin/python3", cli="kicad-cli", timeout_s=120,
            audits=True):
    """Run stable qualification in build scratch; no domain stage is admitted."""
    import math
    if not math.isfinite(timeout_s) or timeout_s <= 0:
        raise ValueError("qualification timeout must be positive and finite")
    root = root.resolve(strict=True)
    started = datetime.now(timezone.utc)
    deadline = (started + timedelta(seconds=timeout_s)).isoformat().replace("+00:00", "Z")
    run_id = "qualify-" + uuid.uuid4().hex
    output = root / "06_build/task_runs" / run_id
    output.mkdir(parents=True, exist_ok=False)
    receipt = {"schema": 1, "scope": "native and repository compatibility", "status": "INCOMPLETE", "started_at": started.isoformat(),
               "native": {"status": "INCOMPLETE"}, "repository": {"status": "INCOMPLETE"},
               "reviewer": {"status": "UNKNOWN", "detail": "fresh host launch is separately required"},
               "failures": [], "attempts": []}
    try:
        actual_python = shutil.which(python)
        actual_cli = shutil.which(cli)
        if not actual_python or not actual_cli:
            raise ValueError(f"missing tool: python={actual_python}, kicad-cli={actual_cli}")
        sources = [PROBE, Path(__file__), *Path(__file__).parent.glob("pipeline_*.py"),
                   REPO / "skills/kicad-pcb/scripts/process_runner.py"]
        seed, _ = fingerprint(sources, {"python": actual_python, "cli": actual_cli})
        subject = subject_identity("qualification", 1,
            [TypedIdentityInput("probe", "mapping", {"sha256": seed}, seed.encode())])
        def probe(mode, outputs, check):
            envelope = TaskEnvelope(task_id=f"{run_id}-{mode}", stage_id="PCB-COMMISSION",
                run_id=run_id, subject=subject, executor="subprocess", execution_class="local",
                recommended_agent_role=None, agent_role=None, role_escalation_reason=None,
                context_mode="NOT_APPLICABLE", input_handoff_id=None, input_packet=[],
                deadline_at=deadline, max_nonimproving_attempts=1, replacement_limit=0,
                writer_scope={"mode": "READ_ONLY", "paths": []},
                output_path=f"06_build/task_runs/{run_id}-{mode}/attempt.json", schema=2,
                completion={"outputs": sorted(outputs), "checks": [check]})
            attempt = execute_attempt(envelope, [actual_python, str(PROBE), mode], cwd=root,
                env={"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8",
                     "HOME": os.environ.get("HOME", ""),
                     "KICAD_CONFIG_HOME": str(root / Path(envelope.output_path).parent / "scratch/kicad-config"),
                     "PCB_QUALIFY_KICAD_CLI": actual_cli}, console=None)
            path = root / envelope.output_path
            receipt["attempts"].append(str(path))
            if attempt.status != "PASS":
                raise ValueError(f"{mode} probe {attempt.status}: {path}; {attempt.unresolved}")
            return path.parent
        identified = probe("identify", ["identity.json"], "identity")
        identity = json.loads((identified / "outputs/identity.json").read_text())
        digest, dependencies = fingerprint([actual_python, actual_cli, *sources, *identity["files"]],
            {"versions": {k: v for k, v in identity.items() if k != "files"},
             "config": "isolated per attempt", "LANG": "C.UTF-8"})
        receipt["fingerprint"] = digest
        receipt["dependencies"] = dependencies
        cache = root / "06_build/cache/native-qualification.json"
        hit = cached_native(cache, digest)
        if hit:
            receipt["native"] = {"status": "PASS", "cached": True, "evidence": hit["evidence"]}
        else:
            native = probe("native", ["clean.json", "hostile.json", "native.json"], "native-compatibility")
            if fingerprint(dependencies["files"], dependencies["configuration"])[0] != digest:
                raise ValueError("qualification dependencies changed during native probe")
            evidence = {str(p): _file_sha256(p) for p in native.rglob("*") if p.is_file()}
            hit = {"fingerprint": digest, "status": "PASS", "evidence": evidence,
                   "fetched_at": datetime.now(timezone.utc).isoformat()}
            cache.parent.mkdir(parents=True, exist_ok=True)
            temporary = cache.with_name(f".{run_id}.tmp")
            temporary.write_text(json.dumps(hit, sort_keys=True) + "\n")
            os.replace(temporary, cache)
            receipt["native"] = {"status": "PASS", "cached": False, "evidence": evidence}
        if audits:
            audit_results = []
            for name, script in (("contracts", REPO / "scripts/contracts_audit.py"),
                                 ("authority", Path(__file__).parent / "skill_authority_check.py")):
                remaining = (datetime.fromisoformat(deadline.replace("Z", "+00:00")) -
                             datetime.now(timezone.utc)).total_seconds()
                if remaining <= 0:
                    raise ValueError("qualification deadline elapsed before repository audit")
                result = run_stage({"id": "PCB-COMMISSION", "work_class": "local", "timeout_s": remaining},
                    [actual_python, str(script)], cwd=REPO,
                    env={"PATH": os.environ.get("PATH", ""), "LANG": "C.UTF-8"},
                    log_path=output / f"{name}.log", console=None)
                audit_results.append(result.to_mapping())
                if result.status != "PASS":
                    raise ValueError(f"repository {name} audit {result.status}: {result.log_path}")
            receipt["repository"] = {"status": "PASS", "audits": audit_results}
        else:
            receipt["repository"] = {"status": "NOT_RUN", "detail": "native-only API test"}
        if fingerprint(dependencies["files"], dependencies["configuration"])[0] != digest:
            raise ValueError("qualification dependencies changed during qualification")
        receipt["status"] = "PASS" if audits else "INCOMPLETE"
    except Exception as exc:
        receipt["failures"].append(str(exc))
    receipt["coverage"] = {
        "graded": (2 if receipt["native"]["status"] == "PASS" else 0) +
                  sum(r["status"] == "PASS" for r in receipt["repository"].get("audits", [])),
        "total": 4 if audits else 2}
    receipt["finished_at"] = datetime.now(timezone.utc).isoformat()
    target = output / "qualification.json"
    target.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(f"qualification {receipt['status']} input: {root}; "
          f"coverage={receipt['coverage']['graded']}/{receipt['coverage']['total']}; receipt={target}")
    return receipt, target
