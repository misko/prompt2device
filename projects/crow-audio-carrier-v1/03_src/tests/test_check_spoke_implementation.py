from __future__ import annotations

import importlib.util
import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_spoke_implementation.py"
FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures/kicad10_native_excerpt.net"
SPEC = importlib.util.spec_from_file_location("carrier_spoke_checker", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def row(ref: str, *, value: str | None = None, footprint: str | None = None,
        pads: dict[str, str] | None = None) -> dict:
    return {
        "ref": ref,
        "value": checker.EXPECTED_MPN if value is None else value,
        "footprint": checker.EXPECTED_FOOTPRINT if footprint is None else footprint,
        "pads": checker.expected_pads(ref) if pads is None and ref in checker.EXPECTED_REFS else (pads or {}),
    }


def valid_rows() -> list[dict]:
    return [row(ref) for ref in checker.EXPECTED_REFS]


class CarrierSpokeCheckerHostiles(unittest.TestCase):
    def test_contract_digest_is_current_authored_authority(self) -> None:
        contract = MODULE_PATH.parents[1] / "03_src/rules/spoke_interface.yaml"
        self.assertEqual(
            hashlib.sha256(contract.read_bytes()).hexdigest(),
            checker.CONTRACT_SHA256,
        )

    def test_accepts_exact_eight(self) -> None:
        self.assertEqual(
            len(checker._validate_realizations("fixture", valid_rows())), 8
        )

    def test_rejects_missing_j8(self) -> None:
        with self.assertRaisesRegex(checker.AuditError, "census"):
            checker._validate_realizations("fixture", valid_rows()[:-1])

    def test_rejects_extra_exact_connector(self) -> None:
        hostile = valid_rows() + [row("J12", pads={"1": "X"})]
        with self.assertRaisesRegex(checker.AuditError, "census"):
            checker._validate_realizations("fixture", hostile)

    def test_rejects_power_ground_swap(self) -> None:
        hostile = valid_rows()
        swapped = checker.expected_pads("J4")
        swapped["1"], swapped["2"] = swapped["2"], swapped["1"]
        hostile[3] = row("J4", pads=swapped)
        with self.assertRaisesRegex(checker.AuditError, "pad map"):
            checker._validate_realizations("fixture", hostile)

    def test_rejects_wrong_footprint_even_with_exact_mpn(self) -> None:
        hostile = valid_rows()
        hostile[2] = row("J3", footprint="Connector_Generic:Conn_01x04")
        with self.assertRaisesRegex(checker.AuditError, "footprint"):
            checker._validate_realizations("fixture", hostile)

    def test_parses_representative_kicad_10_native_netlist(self) -> None:
        rows = checker._schematic_rows_from_netlist(FIXTURE_PATH)
        j1 = next(item for item in rows if item["ref"] == "J1")
        self.assertEqual(j1["value"], "43650-0400")
        self.assertEqual(
            j1["footprint"],
            "crow_mic_pod_v3:Molex_Micro-Fit_3.0_43650-0400_1x04_P3.00mm_Horizontal",
        )
        self.assertEqual(
            j1["pads"],
            {"1": "12V_POD", "2": "GND", "3": "AUDIO_P", "4": "AUDIO_N"},
        )

    def test_native_netlist_parser_rejects_duplicate_pin(self) -> None:
        hostile = FIXTURE_PATH.read_text(encoding="utf-8").replace(
            '(ref "J1") (pin "4")', '(ref "J1") (pin "1")', 1
        )
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "hostile.net"
            path.write_text(hostile, encoding="utf-8")
            with self.assertRaisesRegex(checker.AuditError, "appears in both"):
                checker._schematic_rows_from_netlist(path)

    def test_rejects_legacy_xml_netlist(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legacy.net"
            path.write_text("<export><components/><nets/></export>", encoding="utf-8")
            with self.assertRaisesRegex(checker.AuditError, "not KiCad native"):
                checker._schematic_rows_from_netlist(path)

    def test_kicad_cli_timeout_is_bounded(self) -> None:
        expired = subprocess.TimeoutExpired(
            cmd=["kicad-cli"], timeout=checker.KICAD_CLI_TIMEOUT_S
        )
        with mock.patch.object(checker.subprocess, "run", side_effect=expired) as run:
            with self.assertRaisesRegex(checker.AuditError, "exceeded 30s"):
                checker._schematic_rows(Path("carrier.kicad_sch"))
        self.assertEqual(run.call_args.kwargs["timeout"], 30)


    def test_rj45_map_has_all_contacts_and_isolated_shells(self):
        self.assertEqual(checker.expected_pads("J1"), {
            "1": "12V_POD1", "2": "GND", "3": "12V_POD1", "4": "AUDIO_N1",
            "5": "AUDIO_P1", "6": "GND", "7": "12V_POD1", "8": "GND",
            "9": "CHASSIS", "10": "CHASSIS"})

    def test_rj45_missing_contact_audio_swap_and_grounded_shell_rejected(self):
        for mutation in ("missing", "swap", "shield"):
            hostile = valid_rows()
            pads = checker.expected_pads("J1")
            if mutation == "missing": pads.pop("7")
            elif mutation == "swap": pads["4"], pads["5"] = pads["5"], pads["4"]
            else: pads["9"] = "GND"
            hostile[0] = row("J1", pads=pads)
            with self.assertRaises(checker.AuditError):
                checker._validate_realizations("fixture", hostile)


if __name__ == "__main__":
    unittest.main()
