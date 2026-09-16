#!/usr/bin/env python3
"""Record/verify the complete immutable input census for crow JLC prelayout.

The ordinary stage checkpoint pins generated artifacts and the exact JLC
request.  This companion pins the *set and bytes* of authored inputs that can
change their meaning: rules/layout, part dossiers and local authority files,
tscircuit source/tool locks, decision/source records, and any consumed foreign
hardware fact directory.  Verification rejects additions and deletions as well
as content drift.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import yaml


KIND = "crow-prelayout-input-checkpoint-v2"
IGNORED_NAMES = {"__pycache__", ".DS_Store"}
TS_GENERATED_DIRS = {
    ".tscircuit", "build", "dist", "kicad", "node_modules", "tsx_build",
    "verification",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def repo_path(path: Path, repo: Path) -> str:
    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"input escapes repository root: {path}") from exc
    return f"repo:{relative.as_posix()}"


def reject_symlink_components(path: Path, repo: Path) -> None:
    """Reject a symlink leaf or parent anywhere below the resolved repo."""
    absolute = Path(os.path.abspath(path))
    try:
        relative = absolute.relative_to(repo)
    except ValueError as exc:
        raise ValueError(f"input escapes repository root: {path}") from exc
    current = repo
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ValueError(
                f"symlink is forbidden in checkpoint scope: {current}")


def add_file(files: dict[str, dict[str, object]], path: Path, repo: Path) -> None:
    reject_symlink_components(path, repo)
    if not path.is_file():
        raise ValueError(f"input is missing or not a regular file: {path}")
    key = repo_path(path, repo)
    if key in files:
        return
    files[key] = {"sha256": sha256(path), "size": path.stat().st_size}


def add_tree(files: dict[str, dict[str, object]], root: Path, repo: Path,
             *, skip_top: set[str] | None = None) -> None:
    reject_symlink_components(root, repo)
    if not root.exists():
        return
    if not root.is_dir():
        raise ValueError(f"checkpoint root is not a directory: {root}")
    skip_top = skip_top or set()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if not relative.parts or relative.parts[0] in skip_top:
            continue
        if any(part in IGNORED_NAMES for part in relative.parts):
            continue
        if path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError(f"symlink is forbidden in checkpoint scope: {path}")
        if path.is_file():
            add_file(files, path, repo)
        elif not path.is_dir():
            raise ValueError(f"special file is forbidden in checkpoint scope: {path}")


def authored_census(project: Path, repo: Path,
                    explicit: list[Path]) -> dict[str, dict[str, object]]:
    files: dict[str, dict[str, object]] = {}

    # Electrical/layout/gate source and every exact dossier authority file.
    add_tree(files, project / "02_parts", repo)
    add_tree(files, project / "03_src", repo, skip_top={"tests"})
    add_tree(files, project / "03_tscircuit", repo,
             skip_top=TS_GENERATED_DIRS)

    # Only documentation that is itself consumed as design/source authority.
    for relative in ("BRIEF.md", "capability-profile.json",
                     "ARCHITECTURE.md", "DETAIL_DESIGN.md"):
        candidate = project / "01_docs" / relative
        # is_file() is false for a broken symlink.  Still pass one to
        # add_file() so every symlink substitution is rejected explicitly.
        if candidate.exists() or candidate.is_symlink():
            add_file(files, candidate, repo)
    for relative in ("decisions", "evidence", "sourcing"):
        add_tree(files, project / "01_docs" / relative, repo)

    # Both child copies are compared against the parent array contract. Bind
    # that upstream authority and the comparator that enforces fleet equality.
    parent_src = repo / "projects/crow-roof-array-v1/03_src"
    for relative in ("rules/spoke_interface.yaml", "check_spoke_interface.py"):
        add_file(files, parent_src / relative, repo)

    # Foreign fact locks are inputs whenever mates.yaml selects a device.
    mates = project / "03_src/rules/mates.yaml"
    if mates.is_file():
        payload = yaml.safe_load(mates.read_text(encoding="utf-8-sig")) or {}
        device = str(payload.get("device") or "").strip()
        if not device or "/" in device or device in {".", ".."}:
            raise ValueError("mates.yaml device is missing or unsafe")
        foreign = repo / "external_hardware" / device
        if not foreign.is_dir():
            raise ValueError(f"selected external hardware facts are missing: {foreign}")
        add_tree(files, foreign, repo)

    # Resume safety depends on these verifier implementations as well as their
    # inputs. A method update deliberately reopens the checkpoint.
    method_authorities = (
        Path(__file__),
        repo / "projects/crow-roof-array-v1/03_src/prelayout_resume_gate.py",
        repo / "skills/jlcpcb-fab/scripts/jlc_pcba_availability.py",
        repo / "skills/jlcpcb-fab/scripts/manufacturing_readiness.py",
        repo / "skills/kicad-pcb/scripts/stage_checkpoint.py",
        repo / "skills/kicad-pcb/scripts/build_provenance.py",
    )
    for authority in method_authorities:
        add_file(files, authority, repo)
    # manufacturing_readiness imports helpers across all three PCB skill
    # script trees and executes bom_source_check as a subprocess.  Census the
    # complete local method closure, including additions, instead of keeping a
    # brittle hand-maintained list of today's transitive imports.
    for scripts in (
        repo / "skills/jlcpcb-fab/scripts",
        repo / "skills/kicad-pcb/scripts",
        repo / "skills/pcb-design/scripts",
    ):
        add_tree(files, scripts, repo)
    for path in explicit:
        add_file(files, path, repo)
    return dict(sorted(files.items()))


def resolve_explicit(project: Path, raw_paths: list[str]) -> list[Path]:
    result = []
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = project / path
        result.append(Path(os.path.abspath(path)))
    return result


def atomic_write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n",
                         encoding="utf-8")
    os.replace(temporary, path)


def cmd_record(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    repo = args.repo_root.resolve()
    # Do not resolve the leaf: resolving first would turn an operator-supplied
    # symlink into its target and defeat the explicit no-symlink rule.
    output = Path(os.path.abspath(args.out))
    try:
        reject_symlink_components(output, repo)
        if output.exists() or output.is_symlink():
            raise ValueError(f"refusing to overwrite checkpoint: {output}")
        explicit = resolve_explicit(project, args.input)
        files = authored_census(project, repo, explicit)
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"PRELAYOUT-INPUT FAIL (record): {exc}")
        return 1
    if not files:
        print("PRELAYOUT-INPUT FAIL (record): empty input census")
        return 1
    payload = {
        "schema": 2,
        "kind": KIND,
        "project": project.name,
        # Keys below are rooted at the caller-supplied checkout, so binding the
        # checkout directory's basename would make identical committed bytes
        # unverifiable after an ordinary clone/worktree relocation.
        "path_model": "repo-relative-v1",
        "explicit": [repo_path(path, repo) for path in explicit],
        "files": files,
    }
    atomic_write(output, payload)
    print(f"PRELAYOUT-INPUT PASS (record): {len(files)}/{len(files)} file(s) "
          f"pinned in {output}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    project = args.project.resolve()
    repo = args.repo_root.resolve()
    # As in record mode, retain the raw leaf identity so a checkpoint symlink
    # cannot be silently followed.
    record = Path(os.path.abspath(args.record))
    try:
        reject_symlink_components(record, repo)
        if not record.is_file():
            raise ValueError(f"checkpoint record is missing or not regular: {record}")
        payload = json.loads(record.read_text(encoding="utf-8-sig"))
        if (payload.get("schema") != 2 or payload.get("kind") != KIND or
                payload.get("project") != project.name or
                payload.get("path_model") != "repo-relative-v1" or
                not isinstance(payload.get("files"), dict) or
                not payload.get("files") or
                not isinstance(payload.get("explicit"), list)):
            raise ValueError("checkpoint schema/kind/project/files are invalid")
        explicit = []
        for key in payload["explicit"]:
            if not isinstance(key, str) or not key.startswith("repo:"):
                raise ValueError("checkpoint explicit path is invalid")
            explicit.append(Path(os.path.abspath(
                repo / key.removeprefix("repo:"))))
        current = authored_census(project, repo, explicit)
    except (OSError, ValueError, json.JSONDecodeError, yaml.YAMLError) as exc:
        print(f"PRELAYOUT-INPUT FAIL (verify): {exc}")
        return 1

    saved = payload["files"]
    failures = []
    for key in sorted(set(saved) | set(current)):
        if key not in saved:
            failures.append(f"new input appeared: {key}")
        elif key not in current:
            failures.append(f"recorded input is missing: {key}")
        elif saved[key] != current[key]:
            failures.append(f"recorded input changed: {key}")
    if failures:
        for failure in failures[:30]:
            print(f"  FAIL {failure}")
        if len(failures) > 30:
            print(f"  ... {len(failures) - 30} more finding(s)")
        print(f"PRELAYOUT-INPUT FAIL (verify): {len(failures)} finding(s) over "
              f"{len(saved)} recorded file(s)")
        return 1
    print(f"PRELAYOUT-INPUT PASS (verify): {len(saved)}/{len(saved)} authored, "
          "generated and foreign-authority input(s) are byte-identical")
    return 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    record = commands.add_parser("record")
    record.add_argument("project", type=Path)
    record.add_argument("--repo-root", type=Path, required=True)
    record.add_argument("--out", type=Path, required=True)
    record.add_argument("--input", action="append", default=[])
    record.set_defaults(function=cmd_record)
    verify = commands.add_parser("verify")
    verify.add_argument("project", type=Path)
    verify.add_argument("--repo-root", type=Path, required=True)
    verify.add_argument("--record", type=Path, required=True)
    verify.set_defaults(function=cmd_verify)
    return root


def main() -> int:
    args = parser().parse_args()
    return args.function(args)


if __name__ == "__main__":
    sys.exit(main())
