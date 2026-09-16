#!/usr/bin/env python3
"""Audit J1-J8 in generated KiCad bytes against the shared spoke contract.

The expected set and pad maps are hand-authored constants.  Generated
schematic/board content cannot choose its own denominator.  ``audit(Path)`` is
the pure public API: it either returns a closed 8/8 receipt or raises
``AuditError``.  KiCad CLI work is bounded so a producer hang fails closed.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import tempfile


SCHEMA = 1
KIND = "crow-spoke-implementation-v1"
ROLE = "carrier"
CONTRACT_SHA256 = "88872f0d3fd41ac5235ca9c3927ae70cacb89c79e03793889e419d2c50761dc0"
BOARD_REL = Path("04_kicad/crow_audio_carrier_v1.kicad_pcb")
SCHEMATIC_REL = Path("04_kicad/crow_audio_carrier_v1.kicad_sch")
EXPECTED_REFS = tuple(f"J{index}" for index in range(1, 9))
EXPECTED_MPN = "615008160221"
EXPECTED_FOOTPRINT = "crow_audio_carrier:Wurth_615008160221_RJ45"
KICAD_CLI_TIMEOUT_S = 30
SHARED_NETLIST_PARSER_REL = Path("skills/kicad-pcb/scripts/kicad_sch_parity.py")


class AuditError(RuntimeError):
    """A generated-artifact implementation mismatch."""


def expected_pads(ref: str) -> dict[str, str]:
    if ref not in EXPECTED_REFS:
        raise AuditError(f"no authored spoke pad map for {ref!r}")
    index = int(ref[1:])
    return {"1": f"12V_POD{index}", "2": "GND", "3": f"12V_POD{index}",
            "4": f"AUDIO_N{index}", "5": f"AUDIO_P{index}", "6": "GND",
            "7": f"12V_POD{index}", "8": "GND", "9": "CHASSIS", "10": "CHASSIS"}


def _validate_realizations(domain: str, rows: list[dict]) -> list[dict]:
    """Pure implementation check used by both real parsers and hostiles.

    ``rows`` may include other carrier components and connector families.  The
    inverse census is deliberately keyed by either the exact spoke MPN or exact
    footprint: an added J12 using either identity, or a renamed exact connector,
    is counted and rejected.
    """

    by_ref: dict[str, dict] = {}
    for row in rows:
        ref = str(row.get("ref", ""))
        if not ref:
            raise AuditError(f"{domain} realization has empty refdes")
        if ref in by_ref:
            raise AuditError(f"{domain} duplicate realization for {ref}")
        by_ref[ref] = {
            "ref": ref,
            "value": str(row.get("value", "")),
            "footprint": str(row.get("footprint", "")),
            "pads": {str(k): str(v) for k, v in dict(row.get("pads", {})).items()},
        }

    identity_refs = {
        ref for ref, row in by_ref.items()
        if row["value"] == EXPECTED_MPN
        or row["footprint"] == EXPECTED_FOOTPRINT
    }
    expected = set(EXPECTED_REFS)
    if identity_refs != expected:
        raise AuditError(
            f"{domain} inverse spoke connector census is {sorted(identity_refs)!r}, "
            f"expected exactly {list(EXPECTED_REFS)!r}"
        )
    missing = expected - set(by_ref)
    if missing:
        raise AuditError(f"{domain} missing authored refs {sorted(missing)!r}")

    closed: list[dict] = []
    for ref in EXPECTED_REFS:
        row = by_ref[ref]
        if row["value"] != EXPECTED_MPN:
            raise AuditError(
                f"{domain} {ref} MPN/value {row['value']!r}, expected {EXPECTED_MPN!r}"
            )
        if row["footprint"] != EXPECTED_FOOTPRINT:
            raise AuditError(
                f"{domain} {ref} footprint {row['footprint']!r}, "
                f"expected {EXPECTED_FOOTPRINT!r}"
            )
        pads = expected_pads(ref)
        if row["pads"] != pads:
            raise AuditError(
                f"{domain} {ref} pad map {row['pads']!r}, expected {pads!r}"
            )
        closed.append(row)
    return closed


def _record(project_root: Path, path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": path.relative_to(project_root).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
    }


def _board_rows(path: Path) -> list[dict]:
    try:
        import pcbnew  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment failure
        raise AuditError("pcbnew is required to audit the generated board") from exc
    try:
        board = pcbnew.LoadBoard(str(path))
    except Exception as exc:  # pragma: no cover - pcbnew exception type varies
        raise AuditError(f"cannot load generated board {path}: {exc}") from exc
    rows: list[dict] = []
    for footprint in board.GetFootprints():
        pads: dict[str, str] = {}
        for pad in footprint.Pads():
            number = str(pad.GetNumber())
            if not number:
                continue
            if number in pads:
                raise AuditError(
                    f"board {footprint.GetReference()} duplicate numbered pad {number}"
                )
            pads[number] = str(pad.GetNetname())
        rows.append({
            "ref": str(footprint.GetReference()),
            "value": str(footprint.GetValue()),
            "footprint": str(footprint.GetFPID().GetUniStringLibId()),
            "pads": pads,
        })
    return rows


def _shared_netlist_parser():
    """Load the repository's KiCad-native netlist parser by ordinary path.

    The implementation checker intentionally shares the parser used by the
    schematic-parity gate.  That prevents this gate from quietly retaining an
    XML-only interpretation while KiCad 10's default/export authority is the
    native ``kicadsexpr`` format.
    """

    repository_root = Path(__file__).resolve().parents[3]
    parser_path = repository_root / SHARED_NETLIST_PARSER_REL
    if not parser_path.is_file() or parser_path.is_symlink():
        raise AuditError(f"shared KiCad netlist parser missing: {parser_path}")
    spec = importlib.util.spec_from_file_location(
        "crow_carrier_shared_kicad_netlist_parser", parser_path
    )
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load shared KiCad netlist parser: {parser_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "parse_netlist", None)):
        raise AuditError(f"shared parser has no parse_netlist API: {parser_path}")
    return module.parse_netlist


def _named_sexpr_forms(text: str, name: str) -> list[str]:
    """Return balanced ``(name ...)`` forms while respecting quoted strings."""

    starts = list(re.finditer(r"\(\s*" + re.escape(name) + r"\b", text))
    forms: list[str] = []
    for match in starts:
        start = match.start()
        depth = 0
        quoted = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
                continue
            if char == '"':
                quoted = True
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    forms.append(text[start:index + 1])
                    break
                if depth < 0:
                    raise AuditError(f"malformed KiCad netlist near {name!r} form")
        else:
            raise AuditError(f"unterminated KiCad netlist {name!r} form")
    return forms


def _sexpr_quoted_field(form: str, field: str) -> str:
    match = re.search(
        r"\(\s*" + re.escape(field) + r'\s+"((?:[^"\\]|\\.)*)"\s*\)',
        form,
    )
    if not match:
        return ""
    # KiCad's quoted atoms use backslash escaping.  Only the two escapes that
    # can affect identity comparisons need decoding here.
    return match.group(1).replace(r'\"', '"').replace(r"\\", "\\")


def _schematic_rows_from_netlist(netlist: Path) -> list[dict]:
    text = netlist.read_text(encoding="utf-8")
    if not text.lstrip().startswith("(export"):
        raise AuditError("schematic netlist is not KiCad native kicadsexpr")
    if not _named_sexpr_forms(text, "components"):
        raise AuditError("KiCad native netlist has no components form")
    if not _named_sexpr_forms(text, "nets"):
        raise AuditError("KiCad native netlist has no nets form")

    parse_netlist = _shared_netlist_parser()
    net_to_nodes, no_connects = parse_netlist(netlist, {}, {})
    if not net_to_nodes and not no_connects:
        raise AuditError("shared parser found zero schematic nodes")
    pads_by_ref: dict[str, dict[str, str]] = {}
    for name, nodes in net_to_nodes.items():
        for ref, pin in nodes:
            pads = pads_by_ref.setdefault(ref, {})
            if pin in pads:
                raise AuditError(
                    f"schematic {ref} pin {pin} appears in both {pads[pin]!r} and {name!r}"
                )
            pads[pin] = name
    rows: list[dict] = []
    for component in _named_sexpr_forms(text, "comp"):
        ref = _sexpr_quoted_field(component, "ref")
        rows.append({
            "ref": ref,
            "value": _sexpr_quoted_field(component, "value"),
            "footprint": _sexpr_quoted_field(component, "footprint"),
            "pads": pads_by_ref.get(ref, {}),
        })
    if not rows:
        raise AuditError("KiCad native netlist has zero component realizations")
    return rows


def _schematic_rows(path: Path) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="crow-carrier-spoke-audit-") as td:
        netlist = Path(td) / "carrier.net"
        try:
            completed = subprocess.run(
                [
                    "kicad-cli", "sch", "export", "netlist",
                    "--format", "kicadsexpr", "--output", str(netlist), str(path),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
                timeout=KICAD_CLI_TIMEOUT_S,
            )
        except subprocess.TimeoutExpired as exc:
            raise AuditError(
                f"generated schematic netlist export exceeded {KICAD_CLI_TIMEOUT_S}s"
            ) from exc
        if completed.returncode != 0 or not netlist.is_file():
            raise AuditError(
                "cannot export generated schematic netlist: " + completed.stdout[-2000:]
            )
        return _schematic_rows_from_netlist(netlist)


def audit(project_root: Path) -> dict:
    """Return a closed 8/8 carrier implementation receipt or raise."""

    project_root = Path(project_root).resolve()
    contract = project_root / "03_src/rules/spoke_interface.yaml"
    board = project_root / BOARD_REL
    schematic = project_root / SCHEMATIC_REL
    for needed in (contract, board, schematic):
        if not needed.is_file() or needed.is_symlink():
            raise AuditError(f"required ordinary generated/input artifact missing: {needed}")
    got_contract_sha = hashlib.sha256(contract.read_bytes()).hexdigest()
    if got_contract_sha != CONTRACT_SHA256:
        raise AuditError(
            f"spoke contract drift: {got_contract_sha}, expected {CONTRACT_SHA256}"
        )

    board_closed = _validate_realizations("board", _board_rows(board))
    schematic_closed = _validate_realizations(
        "schematic", _schematic_rows(schematic)
    )
    for b_row, s_row in zip(board_closed, schematic_closed):
        if b_row != s_row:
            raise AuditError(
                f"generated board and schematic disagree for {b_row['ref']}: "
                f"board={b_row!r} schematic={s_row!r}"
            )

    return {
        "schema": SCHEMA,
        "kind": KIND,
        "role": ROLE,
        "contract_sha256": CONTRACT_SHA256,
        "denominator": {"expected": 8, "realized": 8},
        "board": _record(project_root, board),
        "schematic": _record(project_root, schematic),
        "connectors": [
            {
                "ref": ref,
                "mpn": EXPECTED_MPN,
                "footprint": EXPECTED_FOOTPRINT,
                "pads": [
                    {"number": int(number), "net": expected_pads(ref)[number]}
                    for number in ("1", "2", "3", "4", "5", "6", "7", "8", "9", "10")
                ],
            }
            for ref in EXPECTED_REFS
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        receipt = audit(Path(args.project_root))
    except (AuditError, OSError) as exc:
        print(f"FAIL {KIND}: {exc}")
        return 1
    payload = json.dumps(receipt, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    if args.json:
        print(payload, end="")
    else:
        print(f"PASS {KIND}: 8/8 generated carrier spoke connectors closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
