"""Sparse, native-netlist controls for prototype schematic adoption."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import adopt_prototype_schematic as adoption


def write(path: Path, data: str | bytes):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data.encode() if isinstance(data, str) else data)


def prototype_selection(*_):
    return {"status": "PROTOTYPE_ONLY", "prototype_refs": ["U_USB_ESD"]}


def netlist() -> str:
    refs = ["U_USB_ESD"] + [f"R{i:03d}" for i in range(568)]
    nets = ["USB_DP", "USB_DN", "GND"] + [f"N{i}" for i in range(425)]
    components = []
    assigned = {net: [] for net in nets}
    index = 0
    for ref in refs:
        fpid = "Package_TO_SOT_SMD:Texas_DRT-3" if ref == "U_USB_ESD" else "Resistor_SMD:R_0402"
        value = "TPD2EUSB30ADRTR" if ref == "U_USB_ESD" else "1k"
        components.append(f'(comp (ref "{ref}") (value "{value}") (footprint "{fpid}"))')
        for pad in range(1, 5 if ref != "U_USB_ESD" and int(ref[1:]) < 80 else 4):
            if ref == "U_USB_ESD":
                net = {1: "USB_DP", 2: "USB_DN", 3: "GND"}[pad]
            else:
                net = nets[index % len(nets)]
                index += 1
            assigned[net].append(f'(node (ref "{ref}") (pin "{pad}"))')
    rows = [f'(net (code "{i+1}") (name "{net}") {" ".join(nodes)})'
            for i, (net, nodes) in enumerate(assigned.items())]
    return f'(export (components {" ".join(components)}) (libparts) (nets {" ".join(rows)}))\n'


def fixture(root: Path):
    project = root / "crow-usb-carrier-v1"
    selection = project / "03_src/rules/critical_part_selection.yaml"
    write(selection, yaml.safe_dump({"selections": [{"ref": "U_USB_ESD",
        "mpn": "TPD2EUSB30ADRTR", "suitability": {"status": "prototype_only"}}]}))
    write(project / "03_tscircuit/src/crow_carrier.tsx", "// governed source\n")
    for name in adoption.EXTRA_INPUTS:
        if name != "03_src/rules/critical_part_selection.yaml":
            write(project / name, "source fact\n")
    adoption_pause = sys.modules[adoption.verify_pause.__module__]
    adoption_pause.record(project, "prototype", "03_src/rules/critical_part_selection.yaml",
                          "not released", "continue private review", [])
    bundle = project / "06_build/prototype_only/test-bundle"
    refs = ["U_USB_ESD"] + [f"R{i:03d}" for i in range(568)]
    circuit = [{"type": "source_component", "name": ref,
                "manufacturer_part_number": "TPD2EUSB30ADRTR" if ref == "U_USB_ESD" else "R"}
               for ref in refs]
    write(bundle / "circuit.json", json.dumps(circuit))
    write(bundle / "crow_carrier.kicad_sch", "(kicad_sch synthetic)\n")
    write(bundle / "crow_carrier.net", netlist())
    write(bundle / "schematic.pdf", b"%PDF-1.7\nsynthetic")
    receipt = {"schema": 1, "status": "PROTOTYPE_ONLY",
               "selection_gate": "skills/pcb-design/scripts/critical_part_selection_admission.py --require-prototype",
               "inputs": {name: adoption.sha(path)
                          for name, path in adoption.exact_input_paths(project).items()},
               "artifacts": {name: adoption.sha(bundle / name) for name in adoption.DESTINATIONS}}
    write(bundle / "receipt.json", json.dumps(receipt))
    for relative in adoption.DESTINATIONS.values():
        write(project / relative, b"old canonical artifact")
    write(root / ".gitignore", "**/06_build/netlists/*.net\n")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "fixture@example.invalid"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "Fixture"], cwd=root, check=True)
    subprocess.run(["git", "add", ".gitignore", "crow-usb-carrier-v1/03_tscircuit/build/circuit.json",
                    "crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_sch",
                    "crow-usb-carrier-v1/03_tscircuit/build/schematic.pdf"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "baseline"], cwd=root, check=True)
    return project, bundle


def synthetic_export(schematic: Path):
    return adoption.parse_netlist(schematic.parent / "crow_carrier.net")


class AdoptionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="crow-adoption-fixture-")
        self.project, self.bundle = fixture(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def run_adopt(self, **options):
        return adoption.adopt(self.project, self.bundle,
            selection_check=options.pop("selection_check", prototype_selection),
            export_netlist=synthetic_export,
            gate_check=options.pop("gate_check", lambda *_: {
                "E-FAULT": "passed", "P-PREC": "passed", "ERC": "passed"}), **options)

    def test_guarded_adoption_stages_all_four_and_receipts_prototype_only(self):
        plan = self.run_adopt(expected=None, backup_dir=None, plan=True)
        backup = self.project / "06_build/prototype_only/backups/one"
        result = self.run_adopt(expected=plan, backup_dir=backup)
        self.assertEqual(result["status"], "PROTOTYPE_ONLY")
        self.assertEqual(result["stage"], "SCHEMATIC_ONLY")
        self.assertTrue(Path(result["receipt_path"]).is_file())
        for source, relative in adoption.DESTINATIONS.items():
            self.assertEqual(adoption.sha(self.project / relative), adoption.sha(self.bundle / source))
            self.assertEqual((backup / relative).read_bytes(), b"old canonical artifact")
        self.assertFalse((self.project / "04_kicad/crow_carrier.kicad_pcb").exists())
        self.assertFalse((self.project / "06_build/checkpoints/schematic.json").exists())

    def test_stale_bundle_input_fails_before_destination_write(self):
        write(self.project / "03_tscircuit/src/crow_carrier.tsx", "changed source\n")
        with self.assertRaisesRegex(adoption.AdoptionError, "incomplete or stale"):
            self.run_adopt(expected=None, backup_dir=None, plan=True)
        self.assertEqual((self.project / next(iter(adoption.DESTINATIONS.values()))).read_bytes(),
                         b"old canonical artifact")

    def test_partial_input_or_artifact_receipt_fails(self):
        path = self.bundle / "receipt.json"
        receipt = json.loads(path.read_text())
        receipt["inputs"].pop("03_tscircuit/package.json")
        write(path, json.dumps(receipt))
        with self.assertRaisesRegex(adoption.AdoptionError, "incomplete or stale"):
            self.run_adopt(expected=None, backup_dir=None, plan=True)
        receipt["inputs"]["03_tscircuit/package.json"] = adoption.sha(
            self.project / "03_tscircuit/package.json")
        receipt["artifacts"].pop("schematic.pdf")
        write(path, json.dumps(receipt))
        with self.assertRaisesRegex(adoption.AdoptionError, "partial"):
            self.run_adopt(expected=None, backup_dir=None, plan=True)

    def test_wrong_esd_even_with_rehashed_bundle_fails(self):
        path = self.bundle / "circuit.json"
        circuit = json.loads(path.read_text())
        circuit[0]["manufacturer_part_number"] = "PESD2USB5UX-TR"
        write(path, json.dumps(circuit))
        receipt_path = self.bundle / "receipt.json"
        receipt = json.loads(receipt_path.read_text())
        receipt["artifacts"]["circuit.json"] = adoption.sha(path)
        write(receipt_path, json.dumps(receipt))
        with self.assertRaisesRegex(adoption.AdoptionError, "wrong USB ESD MPN"):
            self.run_adopt(expected=None, backup_dir=None, plan=True)

    def test_ordinary_pass_selection_is_rejected(self):
        with self.assertRaisesRegex(adoption.AdoptionError, "PROTOTYPE_ONLY"):
            self.run_adopt(expected=None, backup_dir=None, plan=True,
                selection_check=lambda *_: {"status": "PASS", "prototype_refs": []})

    def test_dirty_overwrite_requires_exact_guard_and_backup(self):
        with self.assertRaisesRegex(adoption.AdoptionError, "guard and new backup"):
            self.run_adopt(expected=None, backup_dir=None)
        plan = self.run_adopt(expected=None, backup_dir=None, plan=True)
        guard = dict(plan)
        guard["expected_current"] = dict(plan["expected_current"])
        guard["expected_current"]["04_kicad/crow_carrier.kicad_sch"] = "0" * 64
        with self.assertRaisesRegex(adoption.AdoptionError, "guard and new backup"):
            self.run_adopt(expected=guard,
                backup_dir=self.project / "06_build/prototype_only/backups/wrong")
        self.assertEqual((self.project / "04_kicad/crow_carrier.kicad_sch").read_bytes(),
                         b"old canonical artifact")

    def test_dirty_tracked_destination_rejected_before_plan_even_with_guard(self):
        plan = self.run_adopt(expected=None, backup_dir=None, plan=True)
        write(self.project / "04_kicad/crow_carrier.kicad_sch", "another workstream's edit")
        with self.assertRaisesRegex(adoption.AdoptionError, "dirty tracked destination"):
            self.run_adopt(expected=None, backup_dir=None, plan=True)
        with self.assertRaisesRegex(adoption.AdoptionError, "dirty tracked destination"):
            self.run_adopt(expected=plan,
                backup_dir=self.project / "06_build/prototype_only/backups/dirty")

    def test_untracked_unignored_destination_rejected(self):
        subprocess.run(["git", "rm", "-q", "--cached",
                        "crow-usb-carrier-v1/04_kicad/crow_carrier.kicad_sch"],
                       cwd=self.project.parent, check=True)
        with self.assertRaisesRegex(adoption.AdoptionError, "untracked canonical destination"):
            self.run_adopt(expected=None, backup_dir=None, plan=True)

    def test_staged_gate_failure_prevents_adoption(self):
        with self.assertRaisesRegex(adoption.AdoptionError, "staged ERC failed"):
            self.run_adopt(expected=None, backup_dir=None, plan=True,
                gate_check=lambda *_: (_ for _ in ()).throw(
                    adoption.AdoptionError("staged ERC failed")))

    def test_precommit_recheck_catches_other_workstream_edit(self):
        plan = self.run_adopt(expected=None, backup_dir=None, plan=True)

        def late_edit(*_):
            write(self.project / "04_kicad/crow_carrier.kicad_sch", "late workstream edit")
            return {"E-FAULT": "passed", "P-PREC": "passed", "ERC": "passed"}

        with self.assertRaisesRegex(adoption.AdoptionError, "dirty tracked destination"):
            self.run_adopt(expected=plan,
                backup_dir=self.project / "06_build/prototype_only/backups/late",
                gate_check=late_edit)
        self.assertEqual((self.project / "04_kicad/crow_carrier.kicad_sch").read_text(),
                         "late workstream edit")

    def test_gate_view_is_private_copy_and_runs_three_required_checks(self):
        files = {name: self.bundle / name for name in adoption.DESTINATIONS}
        commands = []

        def fake_run(command, **_):
            commands.append(command)
            if "--fault-envelope" in command:
                view = Path(command[2])
                write(view / "03_src/rules/critical_part_selection.yaml", "gate-side edit")
            return subprocess.CompletedProcess(command, 0, "PASS", "")

        with patch.object(adoption.subprocess, "run", side_effect=fake_run):
            result = adoption.check_staged_gates(self.project, files)
        self.assertEqual(set(result), {"E-FAULT", "P-PREC", "ERC"})
        self.assertEqual(len(commands), 3)
        self.assertIn("--require-semantic-review", commands[1])
        self.assertIn("--exit-code-violations", commands[2])
        self.assertIn("TPD2EUSB30ADRTR",
                      (self.project / "03_src/rules/critical_part_selection.yaml").read_text())


if __name__ == "__main__":
    unittest.main()
