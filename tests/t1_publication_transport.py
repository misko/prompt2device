#!/usr/bin/env python3
"""T1: publication transport rejects oversized and over-aggregate pushes."""
import subprocess
import sys
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


if __name__ == "__main__":
    sys.exit(main())
