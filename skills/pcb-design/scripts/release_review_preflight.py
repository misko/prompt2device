#!/usr/bin/env python3
"""Admit an exact staged release packet before expensive independent review.

This module proves packet identity and transport readiness only.  It neither
launches a reviewer nor requires review outputs which the launch will produce.
Final rehearsal, seal, and publication gates remain independently authoritative.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
KICAD_SCRIPTS = REPO / "skills/kicad-pcb/scripts"
for source in (HERE, KICAD_SCRIPTS):
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))

from pipeline_execution import TaskEnvelope, verify_input_packet  # noqa: E402
from pipeline_identity import TypedIdentityInput, subject_identity  # noqa: E402
from pipeline_review import ReviewCommission  # noqa: E402
from pcb_publication_gate import manifest_integrity_errors  # noqa: E402
from publication_transport_gate import (  # noqa: E402
    ArchiveLimits, grade as transport_grade, inspect_archives,
)
from release_required_check import (  # noqa: E402
    RELEASE_REVIEW_OUTPUTS, check_release_review_inputs,
)


RECIPE = "release-review-packet"
RECIPE_VERSION = 1
IGNORED_SOURCE_PARTS = frozenset({
    ".git", ".tscircuit", "__pycache__", "node_modules", "dist", "build",
})


@dataclass(frozen=True)
class Finding:
    code: str
    detail: str

    def to_mapping(self) -> dict[str, str]:
        return {"code": self.code, "detail": self.detail}


@dataclass(frozen=True)
class Admission:
    status: str
    findings: tuple[Finding, ...]
    census: dict[str, Any]
    deferred_review_outputs: tuple[str, ...]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "schema": 1,
            "kind": "release-review-preflight-v1",
            "status": self.status,
            "findings": [row.to_mapping() for row in self.findings],
            "census": self.census,
            "deferred_review_outputs": list(self.deferred_review_outputs),
        }


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(path: Path, parent: Path, label: str) -> Path:
    value = path.resolve()
    try:
        value.relative_to(parent.resolve())
    except ValueError as exc:
        raise ValueError(f"{label} escapes {parent}: {path}") from exc
    return value


def _record(path: Path, base: Path) -> dict[str, Any]:
    path = _inside(path, base, "packet input")
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"packet input is not one regular file: {path}")
    info = path.stat()
    return {"path": path.relative_to(base).as_posix(),
            "sha256": _sha(path), "size": info.st_size}


def _candidate_paths(project: Path, release: Path) -> list[Path]:
    deferred = set(RELEASE_REVIEW_OUTPUTS)
    result = []
    for path in release.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"release packet contains symlink: {path}")
        if path.is_file() and path.relative_to(release).as_posix() not in deferred:
            result.append(path)
    return sorted(result)


def _deferred_output_findings(release: Path) -> list[Finding]:
    present = [name for name in RELEASE_REVIEW_OUTPUTS
               if (release / name).exists()]
    if not present:
        return []
    return [Finding(
        "RP-REQUIRED", "future review outputs must be absent before their "
        "commissioned reviews run: " + ", ".join(present))]


def _source_paths(project: Path, live_paths: Iterable[str | Path]) -> list[Path]:
    result = []
    for value in live_paths:
        path = Path(value)
        path = path if path.is_absolute() else project / path
        path = _inside(path, project, "live source input")
        if set(path.relative_to(project).parts) & IGNORED_SOURCE_PARTS:
            raise ValueError(f"generated/dependency path entered live source census: {path}")
        if path.name.endswith((".pyc", ".failed")):
            raise ValueError(f"generated cache entered live source census: {path}")
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"live source input is missing or unsafe: {path}")
        result.append(path)
    unique = sorted(set(result))
    if not unique:
        raise ValueError("live source census is empty")
    return unique


def build_packet_receipt(repo_root: str | Path, project: str | Path,
                         release: str | Path, *, source_commit: str,
                         live_paths: Iterable[str | Path]) -> dict[str, Any]:
    """Build the producer-owned exact packet identity from current authority."""
    repo = Path(repo_root).resolve()
    project_path = _inside(Path(project), repo, "project")
    release_path = _inside(Path(release), project_path, "release")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("source_commit must be a full lowercase Git SHA")
    candidates = [_record(path, project_path)
                  for path in _candidate_paths(project_path, release_path)]
    live = [_record(path, project_path)
            for path in _source_paths(project_path, live_paths)]
    if not candidates:
        raise ValueError("release packet candidate census is empty")
    inputs = [
        TypedIdentityInput("candidate_inventory", "sequence", candidates,
                           _json_bytes(candidates), {"scope": "exact-files"}),
        TypedIdentityInput("live_source_inventory", "sequence", live,
                           _json_bytes(live), {"scope": "exact-files"}),
        TypedIdentityInput("source_commit", "scalar", source_commit,
                           source_commit.encode("ascii"),
                           {"meaning": "source-origin"}),
    ]
    subject = subject_identity(RECIPE, RECIPE_VERSION, inputs)
    return {
        "schema": 1,
        "kind": "release-review-packet-v1",
        "recipe": {"name": RECIPE, "version": RECIPE_VERSION,
                   "claim": "exact-byte-identity-only"},
        "project": project_path.relative_to(repo).as_posix(),
        "release": release_path.relative_to(project_path).as_posix(),
        "source_commit": source_commit,
        "subject": subject.to_mapping(),
        "artifacts": candidates,
        "live_inputs": live,
    }


def _git(repo: Path, *args: str, binary: bool = False):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True,
                          text=not binary, timeout=30, check=False)


def _source_provenance(repo: Path, project: Path, receipt: dict[str, Any],
                       head: str) -> list[Finding]:
    findings: list[Finding] = []
    commit = receipt["source_commit"]
    exists = _git(repo, "cat-file", "-e", f"{commit}^{{commit}}")
    if exists.returncode:
        return [Finding("RP-SOURCE", f"source commit does not exist: {commit}")]
    if _git(repo, "merge-base", "--is-ancestor", commit, head).returncode:
        findings.append(Finding(
            "RP-SOURCE", f"source commit {commit} is not an ancestor of {head}"))
    for record in receipt["live_inputs"]:
        current = project / record["path"]
        repo_rel = current.relative_to(repo).as_posix()
        prior = _git(repo, "show", f"{commit}:{repo_rel}", binary=True)
        if prior.returncode or prior.stdout != current.read_bytes():
            findings.append(Finding(
                "RP-SOURCE", f"current authoritative input differs from "
                f"source commit: {record['path']}"))
    project_rel = project.relative_to(repo).as_posix()
    roots = [f"{project_rel}/02_parts", f"{project_rel}/03_src",
             f"{project_rel}/03_tscircuit", f"{project_rel}/04_kicad"]
    changed = _git(repo, "diff", "--name-only", "--no-renames", commit, head,
                   "--", *roots)
    if changed.returncode:
        raise RuntimeError(changed.stderr.strip() or "cannot compare source commit")
    material_changes = []
    for name in changed.stdout.splitlines():
        path = Path(name)
        if not (set(path.parts) & IGNORED_SOURCE_PARTS or
                path.name.endswith((".pyc", ".failed"))):
            material_changes.append(name)
    dirty = _git(repo, "status", "--porcelain=v1", "--untracked-files=all",
                 "--", *roots)
    if dirty.returncode:
        raise RuntimeError(dirty.stderr.strip() or "cannot inspect source worktree")
    dirty_material = []
    for line in dirty.stdout.splitlines():
        name = line[3:].split(" -> ")[-1]
        path = Path(name)
        if not (set(path.parts) & IGNORED_SOURCE_PARTS or
                path.name.endswith((".pyc", ".failed"))):
            dirty_material.append(name)
    changed_all = sorted(set(material_changes + dirty_material))
    if changed_all:
        findings.append(Finding(
            "RP-SOURCE", "material source population changed after source_commit: "
            + ", ".join(changed_all[:8])))
    return findings


def _packet_records(envelope: TaskEnvelope) -> dict[str, tuple[str, int]]:
    return {row.path: (row.sha256, row.size) for row in envelope.input_packet}


def _staged_board_findings(project: Path, release: Path,
                           live_paths: Iterable[str | Path],
                           authoritative_board: str | Path | None) -> list[Finding]:
    if authoritative_board is None:
        authoritative = [path for path in _source_paths(project, live_paths)
                         if path.suffix == ".kicad_pcb"]
    else:
        value = Path(authoritative_board)
        value = value if value.is_absolute() else project / value
        authoritative = [_inside(value, project, "authoritative board")]
        if (authoritative[0].is_symlink() or
                not authoritative[0].is_file() or
                authoritative[0].suffix != ".kicad_pcb"):
            raise ValueError(
                f"authoritative board is missing or unsafe: {authoritative[0]}")
        live = set(_source_paths(project, live_paths))
        if authoritative[0] not in live:
            raise ValueError("authoritative board is outside the live source census")
    staged = sorted((release / "source").glob("*.kicad_pcb"))
    named = ([path for path in staged if path.name == authoritative[0].name]
             if len(authoritative) == 1 else [])
    selected = named if named else staged if len(staged) == 1 else []
    if len(authoritative) != 1 or len(selected) != 1:
        return [Finding(
            "RP-SOURCE", "release admission requires one authoritative live "
            "board and one unambiguous staged source board selected by basename "
            f"or sole membership; found live={len(authoritative)}, "
            f"staged={len(staged)}, selected={len(selected)}")]
    if _sha(authoritative[0]) != _sha(selected[0]):
        return [Finding(
            "RP-SOURCE", "staged source board differs from the current "
            f"authoritative live board: {selected[0].relative_to(release)}")]
    return []


def _git_candidate_findings(repo: Path, project: Path, head: str,
                            artifacts: list[dict[str, Any]]) -> list[Finding]:
    findings = []
    for record in artifacts:
        repo_rel = (project / record["path"]).relative_to(repo).as_posix()
        blob = _git(repo, "show", f"{head}:{repo_rel}", binary=True)
        if blob.returncode:
            findings.append(Finding(
                "RP-GIT", f"candidate artifact absent from {head}: {record['path']}"))
        elif (len(blob.stdout) != record["size"] or
              hashlib.sha256(blob.stdout).hexdigest() != record["sha256"]):
            findings.append(Finding(
                "RP-GIT", f"candidate artifact differs from {head}: {record['path']}"))
    return findings


def assess(repo_root: str | Path, project: str | Path, release: str | Path,
           envelope: TaskEnvelope, commission_path: str | Path,
           packet_receipt_path: str | Path, *, live_paths: Iterable[str | Path],
           authoritative_board: str | Path | None = None,
           transport_base: str, transport_head: str = "HEAD",
           archive_limits: ArchiveLimits = ArchiveLimits()) -> Admission:
    """Return launch readiness without launching or grading a review verdict."""
    deferred = tuple(RELEASE_REVIEW_OUTPUTS)
    findings: list[Finding] = []
    census: dict[str, Any] = {}
    try:
        repo = Path(repo_root).resolve()
        project_path = _inside(Path(project), repo, "project")
        release_path = _inside(Path(release), project_path, "release")
        commission_file = _inside(
            Path(commission_path) if Path(commission_path).is_absolute()
            else project_path / commission_path, project_path, "commission")
        receipt_file = _inside(
            Path(packet_receipt_path) if Path(packet_receipt_path).is_absolute()
            else project_path / packet_receipt_path, project_path, "packet receipt")
        commission = ReviewCommission.from_json(
            commission_file.read_text(encoding="utf-8-sig"))
        receipt = json.loads(receipt_file.read_text(encoding="utf-8-sig"))
        if (receipt.get("schema") != 1 or
                receipt.get("kind") != "release-review-packet-v1"):
            raise ValueError("unsupported release review packet receipt")
        live_paths = tuple(live_paths)
        current = build_packet_receipt(
            repo, project_path, release_path,
            source_commit=str(receipt.get("source_commit") or ""),
            live_paths=live_paths)
        census["candidate_artifacts"] = len(current["artifacts"])
        census["live_inputs"] = len(current["live_inputs"])
        if receipt != current:
            findings.append(Finding(
                "RP-SUBJECT", "producer packet receipt does not match current "
                "candidate and authoritative source bytes"))
        subjects = [current["subject"], receipt.get("subject"),
                    commission.subject.to_mapping(), envelope.subject.to_mapping()]
        if any(value != subjects[0] for value in subjects[1:]):
            findings.append(Finding(
                "RP-SUBJECT", "recomputed packet, receipt, commission, and "
                "envelope subjects differ"))
        if commission.project != project_path.name:
            findings.append(Finding(
                "RP-SUBJECT", f"commission project {commission.project!r} does "
                f"not match {project_path.name!r}"))
        if commission.source_commit != current["source_commit"]:
            findings.append(Finding(
                "RP-SOURCE", "commission source_commit differs from packet origin"))
        if (envelope.stage_id != "PCB-RELEASE-REVIEW" or
                envelope.executor != "reviewer"):
            findings.append(Finding(
                "RP-COMMISSION", "release-review admission requires an exact "
                "PCB-RELEASE-REVIEW reviewer envelope"))

        expected_artifacts = {
            row["path"]: row["sha256"] for row in current["artifacts"]}
        commissioned = {row.path: row.sha256 for row in commission.artifacts}
        if commissioned != expected_artifacts:
            findings.append(Finding(
                "RP-ARTIFACT", "commission artifact denominator differs from "
                "complete candidate packet"))
        packet = _packet_records(envelope)
        expected_packet = {
            row["path"]: (row["sha256"], row["size"])
            for row in current["artifacts"]}
        for authority in (commission_file, receipt_file):
            record = _record(authority, project_path)
            expected_packet[record["path"]] = (record["sha256"], record["size"])
        if packet != expected_packet or len(envelope.input_packet) != len(packet):
            missing = sorted(set(expected_packet) - set(packet))
            extra = sorted(set(packet) - set(expected_packet))
            misbound = sorted(path for path in set(packet) & set(expected_packet)
                              if packet[path] != expected_packet[path])
            findings.append(Finding(
                "RP-ARTIFACT", "envelope packet denominator differs from exact "
                f"candidate and authority set: missing={missing[:8]}, "
                f"extra={extra[:8]}, misbound={misbound[:8]}"))
        valid_packet, packet_failures = verify_input_packet(envelope, project_path)
        if not valid_packet:
            findings.append(Finding(
                "RP-ARTIFACT", "input packet reopening failed: "
                + "; ".join(packet_failures[:8])))

        required = check_release_review_inputs(
            release_path, project_path / "07_releases/contracts.md")
        deferred = tuple(required["deferred_review_outputs"])
        census["required_present"] = len(required["present"])
        if required["missing"] or required["unparsed"]:
            findings.append(Finding(
                "RP-REQUIRED", "required non-review release inputs are absent "
                f"or unparsed: missing={required['missing']}, "
                f"unparsed={required['unparsed']}"))
        findings.extend(_deferred_output_findings(release_path))
        manifest = release_path / "MANIFEST.txt"
        if not manifest.is_file():
            findings.append(Finding("RP-MANIFEST", "MANIFEST.txt is missing"))
        else:
            errors = manifest_integrity_errors(
                release_path, manifest.read_text(encoding="utf-8-sig",
                                                 errors="replace"))
            findings.extend(Finding("RP-MANIFEST", error) for error in errors)

        findings.extend(_source_provenance(
            repo, project_path, current, transport_head))
        findings.extend(_staged_board_findings(
            project_path, release_path, live_paths, authoritative_board))
        findings.extend(_git_candidate_findings(
            repo, project_path, transport_head, current["artifacts"]))
        transport_findings, transport_census = transport_grade(
            repo, transport_head, [transport_base])
        census["transport"] = transport_census
        findings.extend(Finding("RP-TRANSPORT", f"{row.code}: {row.detail}")
                        for row in transport_findings)
        archive_status, archive_census, archive_errors = inspect_archives(
            [project_path / row["path"] for row in current["artifacts"]],
            limits=archive_limits)
        census["archive_inspection"] = archive_census
        if archive_status != "PASS":
            return Admission(
                "INCOMPLETE",
                tuple(findings + [Finding("RP-OPERATION", detail)
                                  for detail in archive_errors]),
                census, deferred)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError,
            subprocess.SubprocessError, RuntimeError) as exc:
        return Admission("INCOMPLETE", (Finding("RP-OPERATION", str(exc)),),
                         census, deferred)
    return Admission("REFUSED" if findings else "READY", tuple(findings),
                     census, deferred)


__all__ = [
    "Admission", "Finding", "assess", "build_packet_receipt",
]
