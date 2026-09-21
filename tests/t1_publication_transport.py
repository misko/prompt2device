#!/usr/bin/env python3
"""T1: publication transport rejects oversized and over-aggregate pushes."""
import subprocess
import sys
import io
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import check, main, test, tmpdir  # noqa: E402

SCRIPT = Path(__file__).resolve().parents[1] / "skills/pcb-design/scripts/publication_transport_gate.py"
sys.path.insert(0, str(SCRIPT.parent))
import publication_transport_gate as gate  # noqa: E402


def fixture():
    root = tmpdir("publication_transport_")
    for args in (["git", "init", "-q"],
                 ["git", "config", "user.email", "tests@example.invalid"],
                 ["git", "config", "user.name", "Transport Tests"]):
        subprocess.run(args, cwd=root, check=True)
    (root / "base.txt").write_text("base")
    subprocess.run(["git", "add", "."], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=root, check=True)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root,
                                   text=True).strip()
    return root, base


def commit(root, name):
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-q", "-m", name], cwd=root, check=True)


@test("bounded ordinary Git publication batch passes")
def t_bounded_batch():
    root, base = fixture()
    (root / "small.bin").write_bytes(b"x" * 8)
    commit(root, "small")
    findings, census = gate.grade(root, "HEAD", [base], blob_limit=32,
                                   batch_limit=64)
    check(not findings and census["raw_blob_bytes"] == 8,
          f"bounded batch rejected: {findings}, {census}")


@test("oversized individual Git blob is rejected", kind="known_bad")
def t_oversized_blob():
    root, base = fixture()
    (root / "large.bin").write_bytes(b"x" * 32)
    commit(root, "large")
    findings, _ = gate.grade(root, "HEAD", [base], blob_limit=32,
                              batch_limit=128)
    check(any(row.code == "T-BLOB" for row in findings),
          f"oversized blob escaped: {findings}")


@test("aggregate outgoing population is rejected", kind="known_bad")
def t_aggregate_batch():
    root, base = fixture()
    (root / "one.bin").write_bytes(b"1" * 20)
    (root / "two.bin").write_bytes(b"2" * 20)
    commit(root, "aggregate")
    findings, _ = gate.grade(root, "HEAD", [base], blob_limit=32,
                              batch_limit=40)
    check(any(row.code == "T-PACK" for row in findings),
          f"aggregate batch escaped: {findings}")


@test("LFS pointer is counted as transport metadata")
def t_lfs_pointer():
    root, base = fixture()
    (root / "large.bin").write_text(
        "version https://git-lfs.github.com/spec/v1\n"
        "oid sha256:" + "a" * 64 + "\nsize 493288311\n")
    commit(root, "pointer")
    findings, census = gate.grade(root, "HEAD", [base], blob_limit=256,
                                   batch_limit=512)
    check(not findings and census["lfs_pointers"] == 1,
          f"valid pointer metadata rejected: {findings}, {census}")


def zip_bytes(name="board.gbr", payload=b"G04 gerber*"):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name, payload)
    return stream.getvalue()


@test("bounded Gerber ZIP and bounded nested evidence are inspectable")
def t_archive_inspection_bounded():
    root = tmpdir("publication_archives_")
    gerber = root / "board_gerbers.zip"
    gerber.write_bytes(zip_bytes())
    nested = root / "evidence.zip"
    nested.write_bytes(zip_bytes("prior.zip", zip_bytes("report.txt", b"ok")))
    status, census, errors = gate.inspect_archives(
        [gerber, nested], limits=gate.ArchiveLimits(
            depth=4, members=20, expanded_bytes=4096,
            nested_read_bytes=2048))
    check(status == "PASS" and not errors,
          f"bounded archives rejected: {census}, {errors}")
    check(census["nested_archives"] == 1 and census["streamed_bytes"] > 0,
          f"nested/streamed census missing: {census}")


@test("archive inspection resource exhaustion is INCOMPLETE, not Git oversize",
      kind="known_bad")
def t_archive_inspection_limits():
    root = tmpdir("publication_archive_limit_")
    path = root / "evidence.zip"
    path.write_bytes(zip_bytes("report.txt", b"x" * 32))
    status, census, errors = gate.inspect_archives(
        [path], limits=gate.ArchiveLimits(
            depth=4, members=20, expanded_bytes=16,
            nested_read_bytes=16))
    check(status == "INCOMPLETE" and errors,
          f"inspection budget was treated as pass: {census}")
    check(all("T-BLOB" not in row and "T-PACK" not in row for row in errors),
          f"inspection resource limit mislabeled as Git transport: {errors}")


@test("nested archives are detected from bytes despite opaque member names",
      kind="known_bad")
def t_archive_opaque_nested_depth():
    root = tmpdir("publication_archive_opaque_")
    payload = zip_bytes("leaf.txt", b"ok")
    for _ in range(4):
        payload = zip_bytes("opaque.bin", payload)
    path = root / "evidence.zip"
    path.write_bytes(payload)
    status, census, errors = gate.inspect_archives(
        [path], limits=gate.ArchiveLimits(
            depth=4, members=20, expanded_bytes=16384,
            nested_read_bytes=8192))
    check(status == "INCOMPLETE" and any("depth ceiling" in row for row in errors),
          f"opaque nested archive bypassed depth bound: {census}, {errors}")


@test("malformed recognized archive is operationally incomplete",
      kind="known_bad")
def t_archive_inspection_malformed():
    root = tmpdir("publication_archive_bad_")
    path = root / "evidence.tar.gz"
    path.write_bytes(b"not an archive")
    status, _, errors = gate.inspect_archives([path])
    check(status == "INCOMPLETE" and errors,
          "malformed archive was treated as inspectable")


if __name__ == "__main__":
    sys.exit(main())
