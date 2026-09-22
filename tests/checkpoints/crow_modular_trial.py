#!/usr/bin/env python3
"""Prepare/verify the isolated Crow modular-process trial input tree.

This is deliberately a current-parts reconstruction, not a historical checkout.
It copies only selected design authority and removes learned PCB geometry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import yaml


BASELINE = "d7c3ac4416b1ee3c233b98de869ad410e2e61788"
PROJECT_REL = Path("projects/crow-audio-carrier-v1")
DEFAULT_DEST = Path(
    "/home/mouse9911/gits/circuits-trials/crow-modular-20260921/"
    "crow-audio-carrier-v1"
)

DOC_FILES = (
    "README.md", "contracts.md", ".gitignore",
    "01_docs/BRIEF.md", "01_docs/ARCHITECTURE.md",
    "01_docs/DETAIL_DESIGN.md",
    "01_docs/FIRST_ARTICLE_TEST_PLAN.md",
    "01_docs/evidence/connector-physical-closure-request.md",
    "01_docs/evidence/cs530x-effective-capacitance-source.md",
    "01_docs/evidence/mchstreamer-user-manual-record.md",
    "01_docs/sourcing/contracts.md",
    "01_docs/sourcing/manual_quotes.yaml",
    "01_docs/sourcing/parts-selection-2026-09-09.md",
    "01_docs/sourcing/procurement-policy.yaml",
    "01_docs/sourcing/public-distributor-policy.yaml",
)
DECISIONS = tuple(
    f"01_docs/decisions/{name}"
    for name in (
        "0001-single-cs5308p-tdm8.md",
        "0002-hardware-reset-pulse.md",
        "0003-power-and-spoke-boundary.md",
        "0004-cirrus-input-buffer.md",
        "0005-mch-power-domain-boundary.md",
        "0006-public-catalog-prelayout-only.md",
        "0007-prototype-before-physical-qualification.md",
        "0008-external-vmid-and-reference-returns.md",
        "0009-held-power-and-analog-isolation.md",
        "0021-connected-start-input-current-limits.md",
        "0022-buck-input-reverse-isolation.md",
        "0023-opa2320-reference-protection.md",
        "0024-precision-reference-dividers.md",
        "0025-shared-rail-protection-architecture.md",
        "0026-exact-distributor-design-only.md",
        "0027-fixed-north-adc-channel-map.md",
        "0028-rj45-factory-spokes.md",
        "0029-top-only-smd-assembly.md",
        "0031-authorized-public-stock-surplus.md",
        "0032-first-article-order-profile.md",
        "0033-jlc-all-smd-placement.md",
        "contracts.md",
    )
)
TSCIRCUIT_FILES = (
    "03_tscircuit/bun.lock", "03_tscircuit/contracts.md",
    "03_tscircuit/manifest.yaml", "03_tscircuit/net_aliases.txt",
    "03_tscircuit/package.json", "03_tscircuit/parity_padmap.txt",
    "03_tscircuit/src/crow_audio_carrier_v1.tsx",
    "03_tscircuit/src/schematic_presentation.tsx",
)
SOURCE_FILES = (
    "03_src/adc_channel_map.json", "03_src/contracts.md",
    "03_src/check_analog_filter_topology.py",
    "03_src/check_clock_defaults.py", "03_src/check_power_source.py",
    "03_src/check_protection_architecture.py",
    "03_src/check_spoke_implementation.py",
)
RULE_FILES = tuple(
    f"03_src/rules/{name}"
    for name in (
        "assembly.yaml", "connector_assemblies.yaml",
        "connector_assembly_phases.yaml", "contracts.md",
        "critical_paths.yaml", "electrical_invariants.yaml",
        "first_article.yaml", "integration.yaml", "mates.yaml", "nets.yaml",
        "power_stages.yaml", "power_tree.yaml", "protection_paths.yaml",
        "requirements.yaml", "rf.yaml", "spoke_interface.yaml",
        "stackup.yaml",
    )
)


def run(repo: Path, *args: str) -> bytes:
    return subprocess.check_output(args, cwd=repo)


def file_sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def selected_files(source: Path) -> list[Path]:
    files = [Path(p) for p in (*DOC_FILES, *DECISIONS, *TSCIRCUIT_FILES,
                                *SOURCE_FILES, *RULE_FILES)]
    files.extend(p.relative_to(source) for p in (source / "02_parts").rglob("*")
                 if p.is_file())
    files.extend(p.relative_to(source) for p in (source / "03_src/lib").rglob("*")
                 if p.is_file())
    return sorted(set(files), key=lambda p: p.as_posix())


def source_state(repo: Path, files: list[Path]) -> dict[str, object]:
    project = repo / PROJECT_REL
    return {
        "git_status": run(
            repo, "git", "status", "--porcelain=v1", "--untracked-files=all",
            "--", str(PROJECT_REL),
        ).decode(),
        "selected_sha256": {
            p.as_posix(): file_sha(project / p) for p in files
        },
    }


def require_baseline(repo: Path) -> None:
    subprocess.run(
        ["git", "cat-file", "-e", f"{BASELINE}^{{commit}}"], cwd=repo,
        check=True,
    )
    subprocess.run(
        ["git", "diff", "--quiet", BASELINE, "--", str(PROJECT_REL)],
        cwd=repo, check=True,
    )


def require_clean_source_state(state: dict[str, object]) -> None:
    if state["git_status"]:
        raise SystemExit("source Crow project is dirty; refusing reconstruction")


def validate_floorplan_transform(
        original: dict[str, object], result: dict[str, object]) -> None:
    """Reject envelope drift and surviving solved physical geometry."""
    if result["board"]["outline"] != original["board"]["outline"]:
        raise ValueError("sanitized outline differs from pinned baseline")
    if result["board"]["mounting_holes"] != original["board"]["mounting_holes"]:
        raise ValueError("sanitized mounting holes differ from pinned baseline")
    allowed_top = {
        "project", "board", "libraries", "placement", "design_rules", "asserts",
    }
    if set(result) != allowed_top:
        raise ValueError("sanitized floorplan retained an unexpected top-level scope")
    if set(result["board"]) != {
            "outline", "edge_width", "layers", "stackup", "mounting_holes"}:
        raise ValueError("sanitized board retained solution-derived geometry")
    if set(result["placement"]) != {"sides", "require_anchor", "anchors"}:
        raise ValueError("sanitized placement retained solution-derived geometry")
    if result["placement"]["anchors"]:
        raise ValueError("sanitized placement retained component anchors")
    if set(result["asserts"]) != {"pad_net", "edge_faces"}:
        raise ValueError("sanitized assertions retained solution-derived geometry")


def sanitized_floorplan(source: Path) -> dict[str, object]:
    original = yaml.safe_load((source / "03_src/floorplan.yaml").read_text())
    board = original["board"]
    # Preserve the pinned baseline envelope as inherited trial input. It is not
    # promoted to a hard requirement: ADR-0030 is proposed, and later placement
    # work must establish or replace the physical boundary through its owner.
    # Component anchors, repeat cells, regions, keepouts, zones, captions,
    # fiducials, thermal-via sites, legalization, and route seeds are omitted.
    result = {
        "project": original["project"],
        "board": {
            "outline": board["outline"],
            "edge_width": board["edge_width"],
            "layers": board["layers"],
            "stackup": board["stackup"],
            "mounting_holes": board["mounting_holes"],
        },
        "libraries": original["libraries"],
        "placement": {
            "sides": {},
            "require_anchor": True,
            "anchors": {},
        },
        "design_rules": original["design_rules"],
        "asserts": {
            "pad_net": original["asserts"]["pad_net"],
            "edge_faces": original["asserts"]["edge_faces"],
        },
    }
    validate_floorplan_transform(original, result)
    return result


def boundary_text() -> str:
    return f"""# Crow modular trial input boundary

Baseline: `{BASELINE}`.

This directory is an **honestly reconstructed current-parts replay input**. Git
history contains no clean revision with the current selected parts after part
selection and before placement. It is not a historical post-selection snapshot
and it is not a fresh design result.

Inherited authority: BRIEF/architecture/detail design; selected part dossiers,
datasheets, exact footprints and pin mappings; accepted electrical, interface,
assembly, first-article and stackup rules; TSX connectivity and schematic
presentation intent. The TSX schematic is inherited intent and must be freshly
generated, checked and independently reviewed in this trial.

Inherited physical inputs retained for a reproducible start: the pinned
baseline board outline and mounting-hole values, connector edge-facing
requirements, stackup, fabrication minima and top-side assembly policy. The
outline and hole values are trial inputs, not newly established hard
requirements; placement must verify or replace them through the owning design
boundary. Connector component coordinates are intentionally absent because
their old positions were implementation results, not fixed input.

Excluded: every generated CAD/build/netlist/PDF, release, review, journal and
archived evidence artifact; the solved PCB, component anchors/repeat cells,
regions, fiducials, placement keepouts/zones/captions, route.yaml, promoted/final
route chains, route seeds, model-registration poses, assembly locator and
solution-specific DRC waivers. None may be consulted as a trial result.

The first valid output is a fresh schematic generation and review. Placement,
routing, whole-board DRC/parity, fabrication output and release remain owed.
Set `CIRCUITS_ROOT` to the source checkout when invoking shared tools.
"""


def tree_manifest(dest: Path) -> dict[str, object]:
    members = []
    digest = hashlib.sha256()
    for path in sorted((p for p in dest.rglob("*") if p.is_file()),
                       key=lambda p: p.relative_to(dest).as_posix()):
        rel = path.relative_to(dest).as_posix()
        sha = file_sha(path)
        size = path.stat().st_size
        members.append({"path": rel, "size": size, "sha256": sha})
        digest.update(f"{sha}  {rel}\n".encode())
    return {
        "schema": 1,
        "baseline": BASELINE,
        "classification": "reconstructed-current-parts-replay-input",
        "destination": str(dest),
        "member_count": len(members),
        "tree_sha256": digest.hexdigest(),
        "members": members,
    }


def prepare(repo: Path, dest: Path) -> dict[str, object]:
    require_baseline(repo)
    source = repo / PROJECT_REL
    files = selected_files(source)
    before = source_state(repo, files)
    require_clean_source_state(before)
    if dest.exists():
        raise SystemExit(f"destination already exists: {dest}")
    dest.mkdir(parents=True)
    for rel in files:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / rel, target)
    (dest / "03_src/floorplan.yaml").write_text(
        yaml.safe_dump(sanitized_floorplan(source), sort_keys=False),
        encoding="utf-8",
    )
    (dest / "INPUT_BOUNDARY.md").write_text(boundary_text(), encoding="utf-8")
    after = source_state(repo, files)
    if after != before:
        raise SystemExit("source project changed while preparing trial")
    require_baseline(repo)
    manifest = tree_manifest(dest)
    (dest / "INPUT_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def verify(dest: Path) -> dict[str, object]:
    manifest_path = dest / "INPUT_MANIFEST.json"
    expected = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual = tree_manifest(dest)
    # The manifest cannot hash itself; compare after excluding it.
    actual_members = [m for m in actual["members"]
                      if m["path"] != "INPUT_MANIFEST.json"]
    digest = hashlib.sha256()
    for member in actual_members:
        digest.update(f"{member['sha256']}  {member['path']}\n".encode())
    if actual_members != expected["members"] or digest.hexdigest() != expected["tree_sha256"]:
        raise SystemExit("trial input differs from INPUT_MANIFEST.json")
    forbidden = (
        "04_kicad", "06_build", "07_releases", "08_reviews",
        "01_docs/journal", "01_docs/research", "01_docs/reports",
        "03_src/route.yaml", "03_src/route", "03_src/assembly_locator.yaml",
        "03_tscircuit/build", "03_tscircuit/kicad",
    )
    found = [name for name in forbidden if (dest / name).exists()]
    if found:
        raise SystemExit(f"forbidden solved/generated inputs present: {found}")
    floorplan = yaml.safe_load((dest / "03_src/floorplan.yaml").read_text())
    if floorplan["placement"]["anchors"] or "zones" in floorplan or "keepouts" in floorplan:
        raise SystemExit("solution-derived placement geometry survived sanitization")
    return expected


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("prepare", "verify"))
    parser.add_argument("--repo", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--destination", type=Path, default=DEFAULT_DEST)
    args = parser.parse_args()
    if args.command == "prepare":
        result = prepare(args.repo.resolve(), args.destination.resolve())
    else:
        result = verify(args.destination.resolve())
    print(json.dumps({k: result[k] for k in
                      ("baseline", "classification", "destination",
                       "member_count", "tree_sha256")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
