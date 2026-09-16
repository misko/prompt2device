"""ADR0022: actual source must separate shared spokes from the buck VIN bank.

This checks the architectural remedy, not unspecified AP63205 silicon timing.
The conditional removal experiment and exact primary limits are retained in
the reverse-port packet. Historical direct-VIN source is an intentional RED.
"""
import unittest
import copy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from source_inventory import inventory
from check_power_source import screen, validate_power, source_power_maps


def validate_reverse_port(comps, pins):
    expected = {('D_BUCK_IN','1'):'12V_BUCK_IN', ('D_BUCK_IN','2'):'12V_PROTECTED',
                ('U_BUCK','2'):'12V_BUCK_IN', ('U_BUCK','3'):'12V_BUCK_IN',
                **{(r,'1'):'12V_BUCK_IN' for r in ('C_BUCK_IN','C_BUCK_IN2','C_BUCK_IN3')}}
    for key, net in expected.items():
        if pins.get(key) != net:
            raise ValueError(f'{key}: reverse-port isolation requires {net}')
    if comps['D_BUCK_IN'] != ('Diode_SMD:D_SMA','US1B-13-F'):
        raise ValueError('D_BUCK_IN exact low-leakage ultrafast part required')
    owners={r for (r,p),n in pins.items() if n=='12V_BUCK_IN'}
    if owners != {'D_BUCK_IN','U_BUCK','C_BUCK_IN','C_BUCK_IN2','C_BUCK_IN3'}:
        raise ValueError('Unexpected local VIN owner')


class ReversePortTests(unittest.TestCase):
    def test_live_buck_input_and_all_three_ceramics_are_reverse_isolated(self):
        comps,pins,_=inventory()
        validate_reverse_port(comps,pins)

    def test_direct_vin_reversed_diode_and_stranded_cap_are_rejected(self):
        comps,pins,_=inventory()
        for key in [('U_BUCK','3'),('U_BUCK','2'),('C_BUCK_IN','1'),
                    ('C_BUCK_IN2','1'),('C_BUCK_IN3','1'),('D_BUCK_IN','1')]:
            with self.subTest(key=key):
                bad=dict(pins); bad[key]='12V_PROTECTED'
                with self.assertRaises(ValueError): validate_reverse_port(comps,bad)

    def test_actual_reversal_extra_owner_and_production_validator(self):
        comps,pins,_=inventory()
        validate_reverse_port(comps,pins)
        validate_power(*source_power_maps(comps,pins))
        bad=dict(pins)
        bad[('D_BUCK_IN','1')],bad[('D_BUCK_IN','2')]=bad[('D_BUCK_IN','2')],bad[('D_BUCK_IN','1')]
        with self.assertRaises(ValueError): validate_reverse_port(comps,bad)
        with self.assertRaises(ValueError): validate_power(*source_power_maps(comps,bad))
        bad=dict(pins);bad[('F1','1')]='12V_BUCK_IN'
        with self.assertRaises(ValueError): validate_reverse_port(comps,bad)
        with self.assertRaises(ValueError): validate_power(*source_power_maps(comps,bad))

    def test_new_native_diode_clears_all_foreign_instances(self):
        from test_power_landing_source import load_source, native_geometry, copper_groups, entry_screen
        from test_startup_source import clearances, copper_gap
        floor,route,nets,*_=load_source()
        geometry=native_geometry(floor)
        failures,checks=clearances(geometry,{'D_BUCK_IN'})
        self.assertEqual(failures,[])
        self.assertEqual(checks['courtyard'],332)
        pads={p['id']:p for p in geometry['pads']}
        self.assertLess(copper_gap(pads['D_BUCK_IN.1']['shape'],pads['C_BUCK_IN2.1']['shape']),12.)
        groups=copper_groups('12V_BUCK_IN',geometry,route)
        self.assertEqual(len(groups),6)
        for group in groups:
            self.assertIsNotNone(entry_screen('12V_BUCK_IN',group,geometry,route,floor)['witness'])
        bad=copy.deepcopy(floor);bad['placement']['anchors']['D_BUCK_IN']=[28,58,180]
        self.assertTrue(clearances(native_geometry(bad),{'D_BUCK_IN'})[0])

    def test_conditional_leakage_recovery_and_drop_have_hostile_controls(self):
        good=screen()
        self.assertTrue(good['checks']['OPA_before_isolation'])
        self.assertLess(good['raw_OPA_hold_screen_V'],4.502764)
        self.assertFalse(good['input_diode_recovery_is_vendor_guarantee'])
        self.assertFalse(screen(input_diode_leakage_A=.020)['checks']['OPA_before_isolation'])
        self.assertFalse(screen(input_diode_recovery_budget_C=2e-6)['checks']['OPA_before_isolation'])
        self.assertFalse(screen(input_diode_drop_V=2.1)['checks']['upstream'])


if __name__=='__main__': unittest.main()
