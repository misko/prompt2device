"""Focused source-stage tests for Crow's conditional fuse/source E-FAULT branch."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/kicad-pcb/scripts"))
from early_design_check import ContractError, check_fault_envelopes, circuit_semantic_sha256  # noqa: E402

PROJECT = ROOT / "projects/crow-usb-carrier-v1"


def fixture_circuit():
    """Small source-JSON graph of the actual protected input and eight spokes."""
    parts = {"J_PWR": ("43650-0200", {}), "F_IN": ("0451004.MRL", {}),
             "Q_IN": ("DMP6023LFG-13", {}),
             "R_QIN_G": ("RC0402FR-07100KL", {"resistance": 100000}),
             "D_QIN_GS": ("BZT52C12-13-F", {}), "D_IN": ("SMBJ15A", {}),
             "U_BUCK": ("TPSM63603RDHR", {})}
    pins = {("J_PWR", 1): "N12V_IN", ("F_IN", 1): "N12V_IN",
            ("F_IN", 2): "N12V_FUSED", ("Q_IN", 5): "N12V_FUSED",
            ("Q_IN", 1): "N12V_PROTECTED", ("Q_IN", 2): "N12V_PROTECTED",
            ("Q_IN", 3): "N12V_PROTECTED", ("Q_IN", 4): "Q_IN_GATE",
            ("R_QIN_G", 1): "Q_IN_GATE", ("R_QIN_G", 2): "GND",
            ("D_QIN_GS", 1): "N12V_PROTECTED", ("D_QIN_GS", 2): "Q_IN_GATE",
            ("D_IN", 1): "N12V_PROTECTED", ("D_IN", 2): "GND",
            ("U_BUCK", 3): "N12V_PROTECTED"}
    for i in range(1, 4):
        parts[f"C_IN{i}"] = ("12105C106K4Z2A", {"capacitance": 1e-5})
        pins[(f"C_IN{i}", 1)] = "N12V_PROTECTED"
        pins[(f"C_IN{i}", 2)] = "GND"
    for i in range(1, 9):
        parts[f"J{i}"] = ("615008160221", {})
        parts[f"U_SPOKE{i}"] = ("TPS26625DRCR", {})
        parts[f"R_SPOKE_ILIM{i}"] = ("RT0603BRD0744K2L", {"resistance": 44200})
        parts[f"C_SPOKE_DVDT{i}"] = ("CL05B103KB5NNNC", {"capacitance": 1e-8})
        pins[(f"U_SPOKE{i}", 1)] = "N12V_PROTECTED"
        pins[(f"U_SPOKE{i}", 7)] = f"SPOKE_ILIM{i}"
        pins[(f"U_SPOKE{i}", 8)] = f"SPOKE_DVDT{i}"
        pins[(f"U_SPOKE{i}", 5)] = f"SPOKE_RTN{i}"
        pins[(f"U_SPOKE{i}", 11)] = f"SPOKE_RTN{i}"
        pins[(f"U_SPOKE{i}", 6)] = "GND"
        pins[(f"U_SPOKE{i}", 10)] = f"N12V_POD{i}"
        for pin in (1, 3, 7):
            pins[(f"J{i}", pin)] = f"N12V_POD{i}"
        for pin in (2, 6, 8):
            pins[(f"J{i}", pin)] = "GND"
        pins[(f"R_SPOKE_ILIM{i}", 1)] = f"SPOKE_ILIM{i}"
        pins[(f"R_SPOKE_ILIM{i}", 2)] = f"SPOKE_RTN{i}"
        pins[(f"C_SPOKE_DVDT{i}", 1)] = f"SPOKE_DVDT{i}"
        pins[(f"C_SPOKE_DVDT{i}", 2)] = f"SPOKE_RTN{i}"
    circuit = [{"type": "source_project_metadata", "source_filesystem_md5_hash": "0" * 32}]
    for ref, (mpn, value) in parts.items():
        circuit.append({"type": "source_component", "source_component_id": ref,
                        "name": ref, "manufacturer_part_number": mpn, **value})
    for net in set(pins.values()):
        circuit.append({"type": "source_net", "source_net_id": net, "name": net})
    for (ref, pin), net in pins.items():
        port_id = f"{ref}.{pin}"
        circuit.extend((
            {"type": "source_port", "source_port_id": port_id,
             "source_component_id": ref, "pin_number": pin},
            {"type": "source_trace", "connected_source_port_ids": [port_id],
             "connected_source_net_ids": [net]},
        ))
    return circuit


class ExternalSourceFaultTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)
        rules = self.project / "03_src/rules"
        rules.mkdir(parents=True)
        for name in ("power_tree.yaml", "protection_paths.yaml", "electrical_invariants.yaml"):
            shutil.copy2(PROJECT / "03_src/rules" / name, rules / name)
        self.circuit = fixture_circuit()
        self.power = yaml.safe_load((rules / "power_tree.yaml").read_text())
        self.protection = yaml.safe_load((rules / "protection_paths.yaml").read_text())
        self.invariants = yaml.safe_load((rules / "electrical_invariants.yaml").read_text())

    def check(self, error=None):
        path = self.project / "03_tscircuit/build/circuit.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(self.circuit, sort_keys=True).encode()
        path.write_bytes(raw)
        self.power["external_source_fuse"]["circuit_semantic_sha256"] = circuit_semantic_sha256(self.circuit)
        rules = self.project / "03_src/rules"
        (rules / "power_tree.yaml").write_text(yaml.safe_dump(self.power))
        (rules / "protection_paths.yaml").write_text(yaml.safe_dump(self.protection))
        (rules / "electrical_invariants.yaml").write_text(yaml.safe_dump(self.invariants))
        if error is None:
            result = check_fault_envelopes(self.project)
            self.assertIn("CONDITIONAL external source/fuse", " ".join(result))
        else:
            with self.assertRaisesRegex(ContractError, error):
                check_fault_envelopes(self.project)

    def episode(self):
        return self.power["external_source_fuse"]["source"]

    def sync_episode(self):
        self.protection["paths"][0]["series_overcurrent"]["aggregate_source_episode"] = dict(self.episode())

    def test_conditional_pass(self):
        self.check()

    def test_digest_mismatch_rejects_stale_circuit(self):
        self.check()
        path = self.project / "03_tscircuit/build/circuit.json"
        circuit = json.loads(path.read_text())
        next(row for row in circuit if row.get("type") == "source_component" and row.get("name") == "R_QIN_G")["resistance"] = 99000
        path.write_text(json.dumps(circuit))
        with self.assertRaisesRegex(ContractError, "digest mismatch"):
            check_fault_envelopes(self.project)

    def test_path_fingerprint_and_json_format_do_not_stale_electrical_source(self):
        self.check()
        path = self.project / "03_tscircuit/build/circuit.json"
        circuit = json.loads(path.read_text())
        circuit[0]["source_filesystem_md5_hash"] = "a" * 32
        path.write_text(json.dumps(circuit, indent=2))
        self.assertIn("CONDITIONAL external source/fuse", " ".join(check_fault_envelopes(self.project)))

    def test_missing_or_expanded_path_fingerprint_fails_closed(self):
        self.check()
        path = self.project / "03_tscircuit/build/circuit.json"
        circuit = json.loads(path.read_text())
        circuit[0]["electrical_override"] = "unreviewed"
        path.write_text(json.dumps(circuit))
        with self.assertRaisesRegex(ContractError, "metadata must be one path fingerprint only"):
            check_fault_envelopes(self.project)

    def test_legacy_raw_hash_cannot_bypass_semantic_binding(self):
        self.power["external_source_fuse"]["circuit_sha256"] = "0" * 64
        self.check("legacy raw circuit_sha256")

    def test_rebound_digest_still_rejects_real_bound_net_change(self):
        self.circuit = fixture_circuit()
        trace = next(row for row in self.circuit if row.get("type") == "source_trace"
                     and row.get("connected_source_port_ids") == ["F_IN.2"])
        trace["connected_source_net_ids"] = ["GND"]
        self.check("F_IN.2 must connect to N12V_FUSED")

    def test_prebuild_validates_contract_without_circuit_then_full_requires_it(self):
        # A cold-start conductor has no generated circuit yet. A prebuild pass
        # must disclose that circuit binding is still owed.
        self.check()
        (self.project / "03_tscircuit/build/circuit.json").unlink()
        notes = check_fault_envelopes(self.project, prebuild=True)
        self.assertIn("PREBUILD CONTRACT ONLY; CIRCUIT OWED", " ".join(notes))
        with self.assertRaisesRegex(ContractError, "needs fresh source circuit.json"):
            check_fault_envelopes(self.project)

    def test_prebuild_does_not_admit_stale_generated_bytes(self):
        self.check()
        path = self.project / "03_tscircuit/build/circuit.json"
        circuit = json.loads(path.read_text())
        next(row for row in circuit if row.get("type") == "source_component" and row.get("name") == "R_QIN_G")["resistance"] = 99000
        path.write_text(json.dumps(circuit))
        self.assertIn("CIRCUIT OWED", " ".join(check_fault_envelopes(self.project, prebuild=True)))
        with self.assertRaisesRegex(ContractError, "digest mismatch"):
            check_fault_envelopes(self.project)

    def test_prebuild_still_rejects_authored_envelope_contradiction(self):
        self.check()
        self.protection["paths"][0]["series_overcurrent"]["one_fault_screen_A"] = 2.1
        rules = self.project / "03_src/rules"
        (rules / "protection_paths.yaml").write_text(yaml.safe_dump(self.protection))
        with self.assertRaisesRegex(ContractError, "one_fault_screen_A contradicts"):
            check_fault_envelopes(self.project, prebuild=True)

    def test_exclusive_from_legacy_and_no_requirements(self):
        self.power["fault_envelopes"] = [{}]
        self.check("exclusive")
        del self.power["fault_envelopes"]
        self.power["no_fault_envelope_requirements"] = "not applicable"
        self.check("exclusive")

    def test_protection_path_scalar_contradiction(self):
        self.protection["paths"][0]["series_overcurrent"]["one_fault_screen_A"] = 2.1
        self.check("one_fault_screen_A contradicts")

    def test_spoke_output_and_return_must_be_connected(self):
        for pin, pattern in (("U_SPOKE1.10", "U_SPOKE1.10 must connect"),
                             ("U_SPOKE1.5", "U_SPOKE1.5 must connect"),
                             ("C_IN1.2", "C_IN1.2 must connect")):
            self.circuit = fixture_circuit()
            trace = next(c for c in self.circuit if c.get("type") == "source_trace"
                         and c.get("connected_source_port_ids") == [pin])
            trace["connected_source_net_ids"] = ["GND"] if pin != "C_IN1.2" else ["N12V_PROTECTED"]
            self.check(pattern)

    def test_missing_bound_ref(self):
        self.power["external_source_fuse"]["bound_refs"].remove("U_SPOKE8")
        self.check("bound_refs")

    def test_malformed_bound_ref(self):
        self.power["external_source_fuse"]["bound_refs"][0] = ["J_PWR"]
        self.check("bound_refs must be nonempty strings")

    def test_wrong_source_part(self):
        next(c for c in self.circuit if c.get("name") == "F_IN")["manufacturer_part_number"] = "WRONG_FUSE"
        self.check("F_IN source identity")

    def test_wrong_fitted_value(self):
        next(c for c in self.circuit if c.get("name") == "R_SPOKE_ILIM3")["resistance"] = 47000
        self.check("R_SPOKE_ILIM3 fitted source value mismatch")

    def test_uncapped_retry(self):
        self.episode()["retry_rearm"] = "auto_retry_every_512ms"
        self.sync_episode()
        self.check("uncapped excess-current retries")

    def test_nonfinite_or_boolean_peak(self):
        for bad in (True, float("nan"), float("inf")):
            self.episode()["fault_instantaneous_peak_A"] = bad
            self.sync_episode()
            self.check("must be numeric|must be finite")

    def test_peak_and_voltage_relationship(self):
        self.episode()["fault_instantaneous_peak_A"] = 2.1
        self.sync_episode()
        self.check("contradictory")
        self.episode()["fault_instantaneous_peak_A"] = 3.4
        self.episode()["delivery_voltage_min_V"] = 13.3
        self.sync_episode()
        self.check("reviewed floor|contradictory")

    def test_nominal_i2t_cannot_claim_nonopening(self):
        self.power["external_source_fuse"]["nominal_fuse_i2t_role"] = "guaranteed_nonopening"
        self.check("not a nonopening guarantee")

    def test_unsafe_thermal_and_current(self):
        self.power["external_source_fuse"]["pfet"]["hot_resistance_allocation_ohm"] = 0.08
        self.check("thermal screen exceeds")
        self.power["external_source_fuse"]["pfet"]["hot_resistance_allocation_ohm"] = 0.05
        self.episode()["fault_instantaneous_peak_A"] = 4
        self.sync_episode()
        self.check("reviewed ceiling")

    def test_removed_source_mode_returns_failure(self):
        self.protection["paths"][0]["series_overcurrent"]["allowed_source_fault_modes"] = ["fuse_clearing"]
        self.check("unqualified fuse-clearing mode")

    def test_extra_branch_rejected(self):
        self.circuit.append({"type": "source_component", "source_component_id": "U_SPOKE9",
                             "name": "U_SPOKE9", "manufacturer_part_number": "TPS26625DRCR"})
        self.check("extra or missing shared-path")

    def test_ambiguous_port_net_rejected(self):
        self.circuit.append({"type": "source_trace", "connected_source_port_ids": ["F_IN.1"],
                             "connected_source_net_ids": ["N12V_FUSED"]})
        self.check("ambiguous source net")


if __name__ == "__main__":
    unittest.main()
