#!/usr/bin/env python3
"""Audit the generated pod connector against the frozen spoke contract.

This checker deliberately reads the generated KiCad board and exports a netlist
from the generated KiCad schematic.  TSX/YAML declarations cannot satisfy it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import re


SCHEMA = 1
KIND = "crow-spoke-implementation-v1"
ROLE = "pod"
CONTRACT_SHA256 = "eacc850df2f2c1375e182d921745c74a7fb9def3133109e7c2dda105f7f453e7"
BOARD_REL = Path("04_kicad/crow_mic_pod_v3.kicad_pcb")
SCHEMATIC_REL = Path("04_kicad/crow_mic_pod_v3.kicad_sch")
EXPECTED_REF = "J1"
EXPECTED_MPN = "43650-0400"
EXPECTED_FOOTPRINT = (
    "crow_mic_pod_v3:"
    "Molex_Micro-Fit_3.0_43650-0400_1x04_P3.00mm_Horizontal"
)
EXPECTED_PADS = {"1": "12V_POD", "2": "GND", "3": "AUDIO_P", "4": "AUDIO_N"}
KICAD_CLI_TIMEOUT_S = 30


class AuditError(RuntimeError):
    """A generated-artifact implementation mismatch."""


_CONNECTOR_TOKEN = re.compile(r"connector|micro[-_ ]?fit|molex", re.IGNORECASE)


def _is_connector(ref: str, value: str, footprint: str) -> bool:
    """Conservative inverse census used in both generated domains.

    J1 is not allowed to hide beside a differently valued J2. Conversely, a
    connector whose author changed the refdes away from J* is still counted
    when its exact value/footprint identifies it as connector hardware.
    """

    return bool(re.fullmatch(r"J[A-Z0-9_-]*\d+[A-Z0-9_-]*", ref)) or bool(
        _CONNECTOR_TOKEN.search(f"{value} {footprint}")
    )


def _require_exact_connector_census(
    domain: str, identities: list[tuple[str, str, str]]
) -> None:
    refs = {ref for ref, value, footprint in identities if _is_connector(ref, value, footprint)}
    if refs != {EXPECTED_REF}:
        raise AuditError(
            f"{domain} connector census is {sorted(refs)!r}, "
            f"expected exactly [{EXPECTED_REF!r}]"
        )


def _validate_connector(
    domain: str, value: str, footprint: str, pads: dict[str, str]
) -> None:
    if value != EXPECTED_MPN:
        raise AuditError(
            f"{domain} {EXPECTED_REF} MPN/value {value!r}, expected {EXPECTED_MPN!r}"
        )
    if footprint != EXPECTED_FOOTPRINT:
        raise AuditError(
            f"{domain} {EXPECTED_REF} footprint {footprint!r}, "
            f"expected {EXPECTED_FOOTPRINT!r}"
        )
    if pads != EXPECTED_PADS:
        raise AuditError(
            f"{domain} {EXPECTED_REF} pad map {pads!r}, expected {EXPECTED_PADS!r}"
        )


def _record(project_root: Path, path: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": path.relative_to(project_root).as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "size": len(data),
    }


def _board_connector(path: Path) -> tuple[str, str, dict[str, str]]:
    try:
        import pcbnew  # type: ignore
    except ImportError as exc:  # pragma: no cover - environment failure
        raise AuditError("pcbnew is required to audit the generated board") from exc

    board = pcbnew.LoadBoard(str(path))
    footprints = list(board.GetFootprints())
    identities = [
        (
            str(fp.GetReference()),
            str(fp.GetValue()),
            str(fp.GetFPID().GetUniStringLibId()),
        )
        for fp in footprints
    ]
    _require_exact_connector_census("board", identities)
    candidates = [fp for fp in footprints if fp.GetReference() == EXPECTED_REF]
    if len(candidates) != 1:
        raise AuditError(
            f"board connector denominator is {len(candidates)}/1 for {EXPECTED_REF}"
        )
    identity_refs = {
        str(candidate.GetReference())
        for candidate in footprints
        if candidate.GetValue() == EXPECTED_MPN
        or candidate.GetFPID().GetUniStringLibId() == EXPECTED_FOOTPRINT
    }
    if identity_refs != {EXPECTED_REF}:
        raise AuditError(
            "board inverse connector census is "
            f"{sorted(identity_refs)!r}, expected [{EXPECTED_REF!r}]"
        )
    fp = candidates[0]
    fpid = fp.GetFPID().GetUniStringLibId()
    value = fp.GetValue()
    pads: dict[str, str] = {}
    for pad in fp.Pads():
        number = str(pad.GetNumber())
        if not number:
            continue
        if number in pads:
            raise AuditError(f"board {EXPECTED_REF} duplicate numbered pad {number}")
        pads[number] = str(pad.GetNetname())
    return value, fpid, pads


def _parse_sexpr(text: str) -> list:
    """Parse the emitted KiCad netlist grammar without an XML fallback.

    KiCad 10's default `sch export netlist` format is `kicadsexpr`. Keeping
    this small parser in the hash-bound checker makes its immutable receipt
    independent of an unbound helper module while still grading the native
    artifact used by the rest of the PCB pipeline.
    """

    tokens: list[object] = []
    index = 0
    while index < len(text):
        char = text[index]
        if char in "()":
            tokens.append(char)
            index += 1
        elif char.isspace():
            index += 1
        elif char == '"':
            index += 1
            value: list[str] = []
            while index < len(text) and text[index] != '"':
                if text[index] == "\\" and index + 1 < len(text):
                    value.append(text[index + 1])
                    index += 2
                else:
                    value.append(text[index])
                    index += 1
            if index >= len(text):
                raise AuditError("unterminated quoted string in KiCad netlist")
            tokens.append(("atom", "".join(value)))
            index += 1
        else:
            end = index
            while end < len(text) and not text[end].isspace() and text[end] not in "()":
                end += 1
            tokens.append(("atom", text[index:end]))
            index = end

    position = 0

    def parse_list() -> list:
        nonlocal position
        if position >= len(tokens) or tokens[position] != "(":
            raise AuditError("invalid KiCad netlist list boundary")
        position += 1
        node: list = []
        while position < len(tokens) and tokens[position] != ")":
            if tokens[position] == "(":
                node.append(parse_list())
            else:
                atom = tokens[position]
                if not isinstance(atom, tuple) or len(atom) != 2:
                    raise AuditError("invalid KiCad netlist atom")
                node.append(atom[1])
                position += 1
        if position >= len(tokens):
            raise AuditError("unterminated list in KiCad netlist")
        position += 1
        return node

    roots: list = []
    while position < len(tokens):
        if tokens[position] != "(":
            raise AuditError("unexpected top-level token in KiCad netlist")
        roots.append(parse_list())
    return roots


def _head(node: object) -> str | None:
    return node[0] if isinstance(node, list) and node and isinstance(node[0], str) else None


def _child_atom(node: list, key: str) -> str:
    for child in node[1:]:
        if isinstance(child, list) and _head(child) == key and len(child) >= 2:
            if isinstance(child[1], str):
                return child[1]
    return ""


def _walk(node: object):
    if not isinstance(node, list):
        return
    yield node
    for child in node:
        if isinstance(child, list):
            yield from _walk(child)


def _schematic_connector_from_netlist(
    netlist: Path,
) -> tuple[str, str, dict[str, str]]:
    roots = _parse_sexpr(netlist.read_text(encoding="utf-8-sig"))
    nodes = [node for root in roots for node in _walk(root)]
    all_components = [node for node in nodes if _head(node) == "comp"]
    identities = [
        (
            _child_atom(comp, "ref"),
            _child_atom(comp, "value"),
            _child_atom(comp, "footprint"),
        )
        for comp in all_components
    ]
    _require_exact_connector_census("schematic", identities)
    components = [comp for comp in all_components if _child_atom(comp, "ref") == EXPECTED_REF]
    if len(components) != 1:
        raise AuditError(
            f"schematic connector denominator is {len(components)}/1 for {EXPECTED_REF}"
        )
    identity_refs = {
        _child_atom(candidate, "ref")
        for candidate in all_components
        if _child_atom(candidate, "value") == EXPECTED_MPN
        or _child_atom(candidate, "footprint") == EXPECTED_FOOTPRINT
    }
    if identity_refs != {EXPECTED_REF}:
        raise AuditError(
            "schematic inverse connector census is "
            f"{sorted(identity_refs)!r}, expected [{EXPECTED_REF!r}]"
    )
    comp = components[0]
    value = _child_atom(comp, "value")
    footprint = _child_atom(comp, "footprint")
    pads: dict[str, str] = {}
    for net in (node for node in nodes if _head(node) == "net"):
        name = _child_atom(net, "name")
        for node in net[1:]:
            if not isinstance(node, list) or _head(node) != "node":
                continue
            if _child_atom(node, "ref") != EXPECTED_REF:
                continue
            pin = _child_atom(node, "pin")
            if pin in pads:
                raise AuditError(f"schematic {EXPECTED_REF} pin {pin} appears in two nets")
            pads[pin] = name
    return value, footprint, pads


def _schematic_connector(path: Path) -> tuple[str, str, dict[str, str]]:
    with tempfile.TemporaryDirectory(prefix="crow-spoke-audit-") as td:
        netlist = Path(td) / "pod.net"
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
        return _schematic_connector_from_netlist(netlist)


def audit(project_root: Path) -> dict:
    """Return a closed 1/1 pod implementation receipt or raise AuditError."""

    project_root = Path(project_root).resolve()
    contract = project_root / "03_src/rules/spoke_interface.yaml"
    board = project_root / BOARD_REL
    schematic = project_root / SCHEMATIC_REL
    for needed in (contract, board, schematic):
        if not needed.is_file():
            raise AuditError(f"required generated/input artifact missing: {needed}")

    got_contract_sha = hashlib.sha256(contract.read_bytes()).hexdigest()
    if got_contract_sha != CONTRACT_SHA256:
        raise AuditError(
            f"spoke contract drift: {got_contract_sha}, expected {CONTRACT_SHA256}"
        )

    b_value, b_fpid, b_pads = _board_connector(board)
    s_value, s_fpid, s_pads = _schematic_connector(schematic)
    for domain, value, fpid, pads in (
        ("board", b_value, b_fpid, b_pads),
        ("schematic", s_value, s_fpid, s_pads),
    ):
        _validate_connector(domain, value, fpid, pads)
    if (b_value, b_fpid, b_pads) != (s_value, s_fpid, s_pads):
        raise AuditError("generated board and schematic disagree for J1")

    return {
        "schema": SCHEMA,
        "kind": KIND,
        "role": ROLE,
        "contract_sha256": CONTRACT_SHA256,
        "denominator": {"expected": 1, "realized": 1},
        "board": _record(project_root, board),
        "schematic": _record(project_root, schematic),
        "connectors": [
            {
                "ref": EXPECTED_REF,
                "mpn": EXPECTED_MPN,
                "footprint": EXPECTED_FOOTPRINT,
                "pads": [
                    {"number": int(number), "net": EXPECTED_PADS[number]}
                    for number in ("1", "2", "3", "4")
                ],
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", nargs="?", default=".")
    parser.add_argument("--json", action="store_true", help="emit the receipt as JSON")
    parser.add_argument("--output", type=Path, help="also write the JSON receipt here")
    args = parser.parse_args()
    try:
        receipt = audit(Path(args.project_root))
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL crow-spoke-implementation-v1: {exc}")
        return 1
    payload = json.dumps(receipt, indent=2, sort_keys=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    if args.json:
        print(payload, end="")
    else:
        print("PASS crow-spoke-implementation-v1: 1/1 generated pod connector closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
