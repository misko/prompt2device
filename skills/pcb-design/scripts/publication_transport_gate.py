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
import io
import subprocess
import sys
import tarfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


MIB = 1024 * 1024
DEFAULT_BLOB_LIMIT = 100 * MIB
DEFAULT_BATCH_LIMIT = 1536 * MIB
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1\n"
DEFAULT_ARCHIVE_DEPTH_LIMIT = 4
DEFAULT_ARCHIVE_MEMBER_LIMIT = 100_000
DEFAULT_ARCHIVE_EXPANDED_LIMIT = 4 * 1024 * MIB
DEFAULT_ARCHIVE_READ_LIMIT = 512 * MIB


@dataclass(frozen=True)
class Finding:
    code: str
    detail: str


@dataclass(frozen=True)
class ArchiveLimits:
    """Operational resource ceilings for archive inspection, not Git limits."""

    depth: int = DEFAULT_ARCHIVE_DEPTH_LIMIT
    members: int = DEFAULT_ARCHIVE_MEMBER_LIMIT
    expanded_bytes: int = DEFAULT_ARCHIVE_EXPANDED_LIMIT
    nested_read_bytes: int = DEFAULT_ARCHIVE_READ_LIMIT


def _archive_kind(name: str, header: bytes) -> str | None:
    lower = name.lower()
    if (lower.endswith(".zip") or
            header.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"))):
        return "zip"
    if (lower.endswith((".tar", ".tar.gz", ".tgz")) or
            header.startswith(b"\x1f\x8b") or
            (len(header) >= 262 and header[257:262] == b"ustar")):
        return "tar"
    return None


def inspect_archives(paths: list[Path], *, limits: ArchiveLimits = ArchiveLimits()
                     ) -> tuple[str, dict, list[str]]:
    """Inspect archive structure without extraction to the filesystem.

    The census is an operational bound on parser work and expanded evidence.
    It does not reinterpret inner members as Git blobs and does not emit
    ``T-BLOB`` or ``T-PACK`` findings.  Ordinary leaf archives such as Gerber
    ZIPs are valid.  Bounded archive members may themselves be archives.
    """
    census = {"archives": 0, "nested_archives": 0, "members": 0,
              "declared_expanded_bytes": 0, "streamed_bytes": 0,
              "max_depth": 0}
    errors: list[str] = []

    def account(name: str, size: int, depth: int) -> bool:
        census["members"] += 1
        census["declared_expanded_bytes"] += size
        census["max_depth"] = max(census["max_depth"], depth)
        if census["members"] > limits.members:
            errors.append(
                f"archive inspection member ceiling exceeded at {name}: "
                f"> {limits.members}")
        if census["declared_expanded_bytes"] > limits.expanded_bytes:
            errors.append(
                "archive inspection expanded-byte ceiling exceeded: "
                f"> {limits.expanded_bytes}")
        return not errors

    def consume_member(source: BinaryIO, name: str
                       ) -> tuple[str | None, bytes]:
        """Stream one member and retain it only when its bytes are an archive."""
        header = source.read(512)
        census["streamed_bytes"] += len(header)
        if census["streamed_bytes"] > limits.expanded_bytes:
            errors.append(
                "archive inspection streamed-byte ceiling exceeded: "
                f"> {limits.expanded_bytes}")
            return None, b""
        nested = _archive_kind(name, header)
        chunks = [header] if nested else []
        retained = len(header) if nested else 0
        if nested and retained > limits.nested_read_bytes:
            errors.append(
                "archive inspection nested-read ceiling exceeded at "
                f"{name}: > {limits.nested_read_bytes}")
            return nested, b""
        while True:
            block = source.read(1024 * 1024)
            if not block:
                break
            census["streamed_bytes"] += len(block)
            if census["streamed_bytes"] > limits.expanded_bytes:
                errors.append(
                    "archive inspection streamed-byte ceiling exceeded: "
                    f"> {limits.expanded_bytes}")
                break
            if nested:
                retained += len(block)
                if retained > limits.nested_read_bytes:
                    errors.append(
                        "archive inspection nested-read ceiling exceeded at "
                        f"{name}: > {limits.nested_read_bytes}")
                    break
                chunks.append(block)
        return nested, b"".join(chunks)

    def inspect(stream: BinaryIO, name: str, kind: str, depth: int) -> None:
        if errors:
            return
        if depth > limits.depth:
            errors.append(
                f"archive inspection depth ceiling exceeded at {name}: "
                f"> {limits.depth}")
            return
        census["archives"] += 1
        if depth > 1:
            census["nested_archives"] += 1
        census["max_depth"] = max(census["max_depth"], depth)
        try:
            if kind == "zip":
                with zipfile.ZipFile(stream) as archive:
                    for member in archive.infolist():
                        if member.is_dir():
                            continue
                        if not account(f"{name}!{member.filename}",
                                       member.file_size, depth):
                            return
                        with archive.open(member) as source:
                            nested, data = consume_member(
                                source, f"{name}!{member.filename}")
                        if errors:
                            return
                        if nested:
                            inspect(io.BytesIO(data), f"{name}!{member.filename}",
                                    nested, depth + 1)
            else:
                with tarfile.open(fileobj=stream, mode="r:*") as archive:
                    for member in archive:
                        if not member.isfile():
                            continue
                        if not account(f"{name}!{member.name}", member.size, depth):
                            return
                        source = archive.extractfile(member)
                        if source is None:
                            errors.append(
                                f"cannot inspect archive member {name}!{member.name}")
                            return
                        nested, data = consume_member(
                            source, f"{name}!{member.name}")
                        if errors:
                            return
                        if nested:
                            inspect(io.BytesIO(data), f"{name}!{member.name}",
                                    nested, depth + 1)
        except (OSError, EOFError, tarfile.TarError, zipfile.BadZipFile,
                RuntimeError) as exc:
            errors.append(f"cannot inspect archive {name}: {exc}")

    for path in sorted(paths):
        if errors:
            break
        try:
            with path.open("rb") as source:
                header = source.read(512)
                source.seek(0)
                kind = _archive_kind(path.name, header)
                if kind:
                    inspect(source, str(path), kind, 1)
        except OSError as exc:
            errors.append(f"cannot read archive candidate {path}: {exc}")
    return ("INCOMPLETE" if errors else "PASS"), census, errors


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
