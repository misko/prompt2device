from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_spoke_implementation.py"
SPEC = importlib.util.spec_from_file_location("pod_spoke_checker", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


class FakeFPID:
    def __init__(self, value: str) -> None:
        self.value = value

    def GetUniStringLibId(self) -> str:
        return self.value


class FakePad:
    def __init__(self, number: str, net: str) -> None:
        self.number = number
        self.net = net

    def GetNumber(self) -> str:
        return self.number

    def GetNetname(self) -> str:
        return self.net


class FakeFootprint:
    def __init__(
        self,
        ref: str,
        value: str,
        footprint: str,
        pads: dict[str, str] | None = None,
    ) -> None:
        self.ref = ref
        self.value = value
        self.footprint = footprint
        self.pads = pads or {}

    def GetReference(self) -> str:
        return self.ref

    def GetValue(self) -> str:
        return self.value

    def GetFPID(self) -> FakeFPID:
        return FakeFPID(self.footprint)

    def Pads(self) -> list[FakePad]:
        return [FakePad(number, net) for number, net in self.pads.items()]


class FakeBoard:
    def __init__(self, footprints: list[FakeFootprint]) -> None:
        self.footprints = footprints

    def GetFootprints(self) -> list[FakeFootprint]:
        return self.footprints


def j1() -> FakeFootprint:
    return FakeFootprint(
        checker.EXPECTED_REF,
        checker.EXPECTED_MPN,
        checker.EXPECTED_FOOTPRINT,
        dict(checker.EXPECTED_PADS),
    )


def netlist_text(*, extra_connector: bool = False, swap_power_ground: bool = False) -> str:
    pads = dict(checker.EXPECTED_PADS)
    if swap_power_ground:
        pads["1"], pads["2"] = pads["2"], pads["1"]
    extra = ""
    if extra_connector:
        extra = '(comp (ref "J2") (value "GENERIC") (footprint "Connector_Generic:Conn_01x02"))'
    nets = "".join(
        f'(net (code "{index}") (name "{name}") (node (ref "J1") (pin "{pin}")))'
        for index, (pin, name) in enumerate(pads.items(), 1)
    )
    return (
        "(export (version \"E\") (components "
        f'(comp (ref "J1") (value "{checker.EXPECTED_MPN}") '
        f'(footprint "{checker.EXPECTED_FOOTPRINT}")){extra}) '
        f"(nets {nets}))"
    )


class SpokeCheckerHostiles(unittest.TestCase):
    def test_live_project_contract_and_generated_artifacts_pass(self) -> None:
        project = MODULE_PATH.parents[1]
        receipt = checker.audit(project)
        self.assertEqual(receipt["contract_sha256"], checker.CONTRACT_SHA256)
        self.assertEqual(receipt["denominator"], {"expected": 1, "realized": 1})
        self.assertEqual(receipt["kind"], checker.KIND)

    def test_receipt_declares_closed_connector_denominator(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            contract = root / "03_src/rules/spoke_interface.yaml"
            board = root / checker.BOARD_REL
            schematic = root / checker.SCHEMATIC_REL
            contract.parent.mkdir(parents=True)
            board.parent.mkdir(parents=True)
            contract.write_bytes(b"test contract\n")
            board.write_bytes(b"test board\n")
            schematic.write_bytes(b"test schematic\n")
            digest = hashlib.sha256(contract.read_bytes()).hexdigest()
            exact = (
                checker.EXPECTED_MPN,
                checker.EXPECTED_FOOTPRINT,
                dict(checker.EXPECTED_PADS),
            )
            with mock.patch.object(checker, "CONTRACT_SHA256", digest), \
                    mock.patch.object(checker, "_board_connector", return_value=exact), \
                    mock.patch.object(checker, "_schematic_connector", return_value=exact):
                receipt = checker.audit(root)
        self.assertEqual(receipt["denominator"], {"expected": 1, "realized": 1})
        self.assertEqual(len(receipt["connectors"]), receipt["denominator"]["realized"])

    def test_board_accepts_exact_single_j1(self) -> None:
        fake = types.SimpleNamespace(LoadBoard=lambda _path: FakeBoard([j1()]))
        with mock.patch.dict(sys.modules, {"pcbnew": fake}):
            self.assertEqual(
                checker._board_connector(Path("unused.kicad_pcb")),
                (checker.EXPECTED_MPN, checker.EXPECTED_FOOTPRINT, checker.EXPECTED_PADS),
            )

    def test_board_rejects_extra_generic_j2(self) -> None:
        j2 = FakeFootprint("J2", "GENERIC", "Connector_Generic:Conn_01x02")
        fake = types.SimpleNamespace(LoadBoard=lambda _path: FakeBoard([j1(), j2]))
        with mock.patch.dict(sys.modules, {"pcbnew": fake}):
            with self.assertRaisesRegex(checker.AuditError, "connector census"):
                checker._board_connector(Path("unused.kicad_pcb"))

    def test_schematic_rejects_extra_generic_j2(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pod.net"
            path.write_text(netlist_text(extra_connector=True), encoding="utf-8")
            with self.assertRaisesRegex(checker.AuditError, "connector census"):
                checker._schematic_connector_from_netlist(path)

    def test_schematic_accepts_native_kicad10_netlist(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pod.net"
            path.write_text(netlist_text(), encoding="utf-8")
            self.assertEqual(
                checker._schematic_connector_from_netlist(path),
                (checker.EXPECTED_MPN, checker.EXPECTED_FOOTPRINT, checker.EXPECTED_PADS),
            )

    def test_power_ground_pin_swap_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "pod.net"
            path.write_text(netlist_text(swap_power_ground=True), encoding="utf-8")
            value, footprint, pads = checker._schematic_connector_from_netlist(path)
            with self.assertRaisesRegex(checker.AuditError, "pad map"):
                checker._validate_connector("schematic", value, footprint, pads)

    def test_audio_4_5_swap_is_rejected(self) -> None:
        pads = dict(checker.EXPECTED_PADS)
        pads["4"], pads["5"] = pads["5"], pads["4"]
        with self.assertRaisesRegex(checker.AuditError, "pad map"):
            checker._validate_connector(
                "fixture", checker.EXPECTED_MPN, checker.EXPECTED_FOOTPRINT, pads
            )

    def test_each_shell_pad_rejects_signal_ground(self) -> None:
        for number in ("9", "10"):
            pads = dict(checker.EXPECTED_PADS)
            pads[number] = "GND"
            with self.subTest(number=number), self.assertRaisesRegex(
                checker.AuditError, "pad map"
            ):
                checker._validate_connector(
                    "fixture", checker.EXPECTED_MPN, checker.EXPECTED_FOOTPRINT, pads
                )

    def test_wrong_part_is_rejected(self) -> None:
        with self.assertRaisesRegex(checker.AuditError, "MPN"):
            checker._validate_connector(
                "fixture", "43650-0400", checker.EXPECTED_FOOTPRINT,
                dict(checker.EXPECTED_PADS)
            )

    def test_kicad_cli_export_timeout_is_bounded_and_rejected(self) -> None:
        expired = subprocess.TimeoutExpired(cmd=["kicad-cli"], timeout=checker.KICAD_CLI_TIMEOUT_S)
        with mock.patch.object(checker.subprocess, "run", side_effect=expired) as run:
            with self.assertRaisesRegex(checker.AuditError, "exceeded 30s"):
                checker._schematic_connector(Path("pod.kicad_sch"))
        self.assertEqual(run.call_args.kwargs["timeout"], checker.KICAD_CLI_TIMEOUT_S)
        self.assertIn("kicadsexpr", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
