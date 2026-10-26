"""Small native smoke/negative suite; no Crow acceptance or full regression claim.

Run from the isolated vNext root: python3 tools/test_native_schematic.py
Requires real KiCad 10.0.4 and Poppler; missing tools fail rather than skip.
All producer outputs and intentional corruptions are confined to a temporary dir.
"""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import native_schematic as native

FIXTURE = Path(__file__).parent / 'test-fixtures' / 'native-smoke.json'


class NativeSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='vnext-native-smoke-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.out = cls.root / 'good'
        cls.source = json.loads(FIXTURE.read_text())
        native.build(FIXTURE, cls.out)

    def test_real_native_roundtrip(self):
        self.assertTrue(native.verify(FIXTURE, self.out))
        receipt = json.loads((self.out / 'receipt.json').read_text())
        self.assertEqual(receipt['tool_version'], '10.0.4')
        self.assertIn('erc_all_severity_counts', receipt)

    def test_empty_circuit_rejected(self):
        value = copy.deepcopy(self.source)
        value.update(nets=[], components=[], wire_paths=[])
        with self.assertRaises(ValueError):
            native.check(value)

    def test_off_grid_rejected_without_snapping(self):
        value = copy.deepcopy(self.source)
        value['components'][0]['at'][0] += 0.1
        with self.assertRaisesRegex(ValueError, 'off-grid'):
            native.check(value)

    def test_native_tampering_rejected(self):
        out = self.root / 'tampered-native'
        shutil.copytree(self.out, out)
        path = native.artifacts(out)['schematic']
        path.write_text(path.read_text() + '\n; intentional test corruption\n')
        with self.assertRaisesRegex(ValueError, 'differs from source'):
            native.verify(FIXTURE, out)

    def test_stale_source_rejected(self):
        path = self.root / 'changed-source.json'
        value = copy.deepcopy(self.source)
        value['components'][0]['value'] = '10k'
        path.write_text(json.dumps(value))
        with self.assertRaisesRegex(ValueError, 'source snapshot is stale'):
            native.verify(path, self.out)

    def test_missing_export_rejected(self):
        out = self.root / 'missing-export'
        shutil.copytree(self.out, out)
        native.artifacts(out)['netlist'].unlink()
        with self.assertRaisesRegex(ValueError, 'missing/empty'):
            native.verify(FIXTURE, out)

    def test_real_erc_rejects_output_conflict(self):
        value = copy.deepcopy(self.source)
        for component in value['components']:
            component['pins'][0]['type'] = 'output'
        path = self.root / 'electrical-conflict.json'
        path.write_text(json.dumps(value))
        out = self.root / 'electrical-conflict'
        with self.assertRaisesRegex(ValueError, 'kicad-cli failed|ERC'):
            native.build(path, out)
        report = json.loads(native.artifacts(out)['erc_all'].read_text())
        conflicts = [v for sheet in report['sheets'] for v in sheet['violations']
                     if v.get('type') == 'pin_to_pin' and
                     v.get('severity') == 'error']
        self.assertTrue(conflicts, 'must fail for a real native pin conflict')
        self.assertFalse((out / 'receipt.json').exists())


if __name__ == '__main__':
    unittest.main()
