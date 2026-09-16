#!/usr/bin/env python3
"""Reject an outgoing Git object set that cannot be transported safely.

Publication correctness and transportability are separate properties.  This
gate examines every object reachable from ``--head`` but not from the supplied
``--base`` revisions.  It rejects ordinary Git blobs at or above GitHub's
100 MiB limit and an aggregate raw-blob set above a conservative batch limit.
Git LFS pointers remain small Git blobs and are reported explicitly.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


MIB = 1024 * 1024
DEFAULT_BLOB_LIMIT = 100 * MIB
DEFAULT_BATCH_LIMIT = 1536 * MIB
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"


@dataclass(frozen=True)
class Finding:
    code: str
    detail: str


def _git(root: Path, *args: str, input_text: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=root, input=input_text, text=True,
        capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout


def outgoing_objects(root: Path, head: str, bases: list[str]) -> list[tuple[str, str]]:
    args = ["rev-list", "--objects", head]
    if bases:
        args += ["--not", *bases]
    rows = []
    for line in _git(root, *args).splitlines():
        oid, _, path = line.partition(" ")
        rows.append((oid, path))
    return rows


def grade(root: Path, head: str, bases: list[str], *,
          blob_limit: int = DEFAULT_BLOB_LIMIT,
          batch_limit: int = DEFAULT_BATCH_LIMIT) -> tuple[list[Finding], dict]:
    objects = outgoing_objects(root, head, bases)
    if not objects:
        return [], {"objects": 0, "blobs": 0, "raw_blob_bytes": 0,
                    "lfs_pointers": 0, "largest_blob_bytes": 0}
    metadata = _git(
        root, "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)",
        input_text="".join(f"{oid}\n" for oid, _ in objects))
    by_oid = {}
    for line in metadata.splitlines():
        oid, kind, size = line.split()
        by_oid[oid] = (kind, int(size))
    findings = []
    blob_rows = []
    lfs_count = 0
    for oid, path in objects:
        kind, size = by_oid[oid]
        if kind != "blob":
            continue
        blob_rows.append((oid, path, size))
        if size <= 1024:
            content = subprocess.check_output(["git", "cat-file", "blob", oid], cwd=root)
            if content.startswith(LFS_HEADER):
                lfs_count += 1
        if size >= blob_limit:
            findings.append(Finding(
                "T-BLOB", f"ordinary Git blob {size} bytes >= {blob_limit}: "
                f"{path or oid}"))
    raw = sum(row[2] for row in blob_rows)
    if raw >= batch_limit:
        findings.append(Finding(
            "T-PACK", f"outgoing raw blob population {raw} bytes >= conservative "
            f"batch limit {batch_limit}; seed bounded reviewed commits first"))
    return findings, {
        "objects": len(objects), "blobs": len(blob_rows),
        "raw_blob_bytes": raw, "lfs_pointers": lfs_count,
        "largest_blob_bytes": max((row[2] for row in blob_rows), default=0),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--base", action="append", default=[])
    parser.add_argument("--blob-limit-bytes", type=int, default=DEFAULT_BLOB_LIMIT)
    parser.add_argument("--batch-limit-bytes", type=int, default=DEFAULT_BATCH_LIMIT)
    args = parser.parse_args(argv)
    try:
        findings, census = grade(args.root.resolve(), args.head, args.base,
                                  blob_limit=args.blob_limit_bytes,
                                  batch_limit=args.batch_limit_bytes)
    except Exception as exc:
        print(f"T-PUBLISH INCOMPLETE: {exc}")
        return 2
    print("T-PUBLISH census: " + ", ".join(f"{k}={v}" for k, v in census.items()))
    for finding in findings:
        print(f"  FAIL {finding.code}: {finding.detail}")
    print(f"T-PUBLISH {'FAIL' if findings else 'PASS'}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
