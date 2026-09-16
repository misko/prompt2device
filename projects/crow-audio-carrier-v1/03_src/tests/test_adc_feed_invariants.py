"""ADR0015 netlist intent, complementary to native source-geometry tests.

Reads this project's live generated netlist deliberately: every regeneration
must retain the accepted west ADC supply and VMID return identities. This does
not establish copper length, nearest-ground routing, filled return or ampacity.
The 2026-09-08 full build exposed the absent ADR0015 invariant declarations.
"""
import sys
import unittest
from collections import defaultdict
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT.parents[1] / 'skills/kicad-pcb/scripts'))
from electrical_invariants import Netlist, adr_coverage, check_invariants, load_invariants

# Hand-transcribed electrical intent from ADR0015's two supply/return banks,
# not inferred from the TSX producer, route source, or invariants under test.
EXPECTED = {
    'U_ADC.5': '3V3_ADC', 'U_ADC.9': '3V3_ADC',
    'U_ADC.6': 'GND', 'U_ADC.8': 'GND',
    'C_VDDA1_4U7.1': '3V3_ADC', 'C_VDDA1_4U7.2': 'GND',
    'C_VDDA1_10N.1': '3V3_ADC', 'C_VDDA1_10N.2': 'GND',
    'C_VDDA2_4U7.1': '3V3_ADC', 'C_VDDA2_4U7.2': 'GND',
    'C_VDDA2_10N.1': '3V3_ADC', 'C_VDDA2_10N.2': 'GND',
    'U_ADC.1': 'VMID1', 'U_ADC.12': 'VMID2',
    'C_VMID1_470N.1': 'VMID1', 'C_VMID1_470N.2': 'GND',
    'C_VMID1_4U7.1': 'VMID1', 'C_VMID1_4U7.2': 'GND',
    'C_VMID2_470N.1': 'VMID2', 'C_VMID2_470N.2': 'GND',
    'C_VMID2_4U7.1': 'VMID2', 'C_VMID2_4U7.2': 'GND',
}


def fixture(mapping):
    """A parser-realistic netlist whose one-defect mutations remain valid."""
    nets = defaultdict(list)
    for pin, net in mapping.items():
        ref, number = pin.rsplit('.', 1)
        nets[net].append(f'(node (ref "{ref}") (pin "{number}"))')
    return Netlist('(export (nets ' + ' '.join(
        f'(net (code {i}) (name "{net}") {" ".join(nodes)})'
        for i, (net, nodes) in enumerate(nets.items(), 1)) + '))')


class AdcFeedInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [r for r in load_invariants(
            PROJECT / '03_src/rules/electrical_invariants.yaml')
            if r['_adr'] == '0015']

    def assert_complete(self):
        self.assertEqual(len(self.rows), len(EXPECTED))
        self.assertTrue(all(r['assert'] == 'pin_on_net' for r in self.rows))
        self.assertEqual({r['pin']: r['net'] for r in self.rows}, EXPECTED)

    def test_every_accepted_supply_and_return_pin_has_an_invariant(self):
        self.assert_complete()
        self.assertEqual(check_invariants(fixture(EXPECTED), self.rows), [])

    def test_replaced_regulator_is_owned_by_successor_not_old_pin_map(self):
        rows=load_invariants(PROJECT/'03_src/rules/electrical_invariants.yaml')
        ldo={r['pin']:r['net'] for r in rows if r['_adr']=='0025'
             and r['assert']=='pin_on_net' and r['pin'].startswith('U_LDO.')}
        self.assertEqual(ldo,{'U_LDO.1':'5V_LDO_HOLD','U_LDO.2':'5V_LDO_HOLD',
            'U_LDO.3':'5V_LDO_HOLD','U_LDO.5':'LDO_EN','U_LDO.7':'GND',
            'U_LDO.8':'5V_LDO_HOLD','U_LDO.9':'LDO_NR','U_LDO.10':'GND',
            'U_LDO.11':'GND','U_LDO.12':'3V3_ADC','U_LDO.13':'3V3_ADC',
            'U_LDO.14':'3V3_ADC','U_LDO.15':'GND'})

    def test_current_native_netlist_retains_electrical_intent(self):
        self.assert_complete()
        nl = Netlist((PROJECT / '06_build/netlists/crow_audio_carrier_v1.net').read_text())
        self.assertEqual(check_invariants(nl, self.rows), [])

    def test_each_wrong_supply_or_return_net_is_rejected(self):
        self.assert_complete()
        for pin, net in EXPECTED.items():
            with self.subTest(pin=pin):
                bad = dict(EXPECTED)
                bad[pin] = '3V3_ADC' if net == 'GND' else 'GND'
                findings = check_invariants(fixture(bad), self.rows)
                self.assertEqual(len(findings), 1, findings)
                self.assertIn(pin, findings[0])

    def test_each_missing_supply_or_return_pin_is_rejected(self):
        self.assert_complete()
        for pin in EXPECTED:
            with self.subTest(pin=pin):
                bad = dict(EXPECTED)
                del bad[pin]
                findings = check_invariants(fixture(bad), self.rows)
                self.assertEqual(len(findings), 1, findings)
                self.assertIn(pin, findings[0])

    def test_active_topology_decisions_remain_covered(self):
        findings, cited, total, _ = adr_coverage(PROJECT)
        self.assertGreater(total, 0)
        self.assertEqual(cited, total)
        self.assertEqual(findings, [])


if __name__ == '__main__':
    unittest.main()
