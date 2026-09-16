"""Positive, hostile and declared physical-vacuity tests for source screens."""
from pathlib import Path
import sys
import unittest
import contextlib
import io
import json
from unittest import mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_power_source import (screen,capacitance_inventory,validate_power,
                                validate_legacy_power,POWER_PINS,POWER_VALUES,divider)
from source_inventory import inventory
from check_power_source import cold_start_screen
import check_power_source as power_checker
class PowerSourceTests(unittest.TestCase):
    def test_adr0021_limits_solve_and_straddle_actual_scalar_budget(self):
        for name in ('leakage_uA','loop_nH','part_nH','pcb_nH',
                     'feed_current_A','feed_resistance_ohm','bleed_resistance_ohm'):
            with self.subTest(name=name):
                limit=power_checker.adr0021_bound(name)
                self.assertAlmostEqual(power_checker.adr0021_bound(name,limit),1.)
                lower_is_safe=name not in ('feed_resistance_ohm','bleed_resistance_ohm')
                inside=limit*(.99 if lower_is_safe else 1.01)
                outside=limit*(1.01 if lower_is_safe else .99)
                self.assertLess(power_checker.adr0021_bound(name,inside),1.)
                self.assertGreater(power_checker.adr0021_bound(name,outside),1.)

    def test_adr0021_rejects_invalid_values_and_unsafe_historical_candidates(self):
        for value in (0,-1,float('nan'),float('inf')):
            with self.subTest(value=value), self.assertRaises(ValueError):
                power_checker.adr0021_bound('loop_nH',value)
        with self.assertRaises(ValueError):
            power_checker.adr0021_bound('silent_accept')
        for name,value in [('loop_nH',100),('feed_current_A',4.1),
                           ('feed_resistance_ohm',.01),('bleed_resistance_ohm',300),
                           ('leakage_uA',10)]:
            with self.subTest(name=name):
                self.assertGreater(power_checker.adr0021_bound(name,value),1.)
        self.assertFalse(cold_start_screen()['feed_current_budget_is_vendor_guarantee'])

    def test_adr0021_current_limit_matches_independent_power_equation(self):
        limit=power_checker.adr0021_bound('feed_current_A')
        self.assertAlmostEqual(limit**2*.05*1.05,.85)
        original=power_checker.cold_start_screen
        def weaker_rating(*args,**kwargs):
            row=original(*args,**kwargs)
            row['feed_85C_power_rating_W']*=.5
            return row
        with mock.patch.object(power_checker,'cold_start_screen',side_effect=weaker_rating):
            self.assertLess(power_checker.adr0021_bound('feed_current_A'),limit)
            self.assertGreater(power_checker.adr0021_bound('feed_current_A',4),1.)

    def test_nr_linear_charge_is_not_reported_as_full_settling(self):
        # 2026-09-09: SBVS318B p14/p19 specifies a final RC phase.
        # Run RED against the actual 86ca72ee checker before fixing it.
        got=screen()
        self.assertNotIn('NR_full_ramp_screen_ms',got)
        self.assertAlmostEqual(got['NR_linear_charge_equivalent_ms'][0],3.9174124)
        self.assertAlmostEqual(got['NR_linear_charge_equivalent_ms'][1],9.9986061)
        for rise,charge in zip(got['NR_ramp_10_to_90_screen_ms'],
                               got['NR_linear_charge_equivalent_ms']):
            self.assertAlmostEqual(rise,charge*.8)
        self.assertTrue(got['checks']['NR_ramp_screen'])

    def test_nr_settling_tail_matches_independent_time_integration(self):
        # Independently integrate only the final RC phase; do not call the
        # producer's logarithm. This is typical-model arithmetic, not silicon.
        got=power_checker.nr_settling_estimate()
        v=.97*.8
        dt=1e-7
        steps=0
        while v<.99*.8:
            v+=(.8-v)/(280000*47e-9)*dt
            steps+=1
            self.assertLess(steps,200000)
        self.assertAlmostEqual(got['tail_ms'],steps*dt*1000,delta=.0002)
        self.assertGreater(got['total_ms'],19.)
        self.assertLess(got['total_ms'],21.)
        self.assertAlmostEqual(got['total_ms'],got['linear_to_transition_ms']+got['tail_ms'])
        self.assertEqual(screen()['NR_settling_typical_estimate'],got)

    def test_nr_settling_requires_a_defined_tail_target(self):
        for fraction in (.97,1.,float('nan')):
            with self.subTest(fraction=fraction), self.assertRaises(ValueError):
                power_checker.nr_settling_estimate(settled_fraction=fraction)
        for capacitance in (0.,-47e-9,float('inf')):
            with self.subTest(capacitance=capacitance), self.assertRaises(ValueError):
                power_checker.nr_settling_estimate(cap_F=capacitance)
        normal=power_checker.nr_settling_estimate()
        doubled=power_checker.nr_settling_estimate(cap_F=94e-9)
        self.assertAlmostEqual(doubled['total_ms'],2*normal['total_ms'])

    def test_nr_typical_model_cannot_close_restart_or_maximum_time(self):
        got=screen()['NR_settling_typical_estimate']
        self.assertFalse(got['is_guaranteed_bound'])
        self.assertIsNone(got['guaranteed_settling_max_ms'])
        self.assertIsNone(got['guaranteed_NR_reset_max_ms'])
        self.assertTrue(any('NR reset' in x for x in screen()['qualification_owed']))

    def test_failed_current_child_changes_both_exit_and_reported_status(self):
        # Exercise the actual current source entry, not a TPS fixture selected
        # by a stale native output. Failed child and public status must agree.
        output=io.StringIO()
        with mock.patch('check_protection_architecture.calculate',
                        return_value={'checks':{'injected_bad':False}}), \
             contextlib.redirect_stdout(output):
            rc=power_checker.main(source_only=True)
        self.assertEqual(rc,1)
        report=json.loads(output.getvalue())
        self.assertFalse(report['checks']['injected_bad'])
        self.assertEqual(report['status'],'FAIL_ELECTRICAL_SOURCE')

    def test_stale_native_converter_cannot_select_a_retired_model(self):
        with mock.patch.object(power_checker,'parse_native_netlist',
                               return_value=(POWER_PINS,POWER_VALUES)):
            with self.assertRaisesRegex(ValueError,'U_LDO.*stale/retired'):
                power_checker.main()
    def test_complete_cold_start_screen(self):
        self.assertTrue(all(cold_start_screen()['checks'].values()))
        self.assertLess(cold_start_screen()['positive_input_current_bound_A'],.0012)
    def test_feed_stress_budget_is_not_minimum_buck_limit(self):
        result=cold_start_screen()
        self.assertEqual(result['buck_HS_peak_limit_min_max_A'],[2.5,3.1])
        self.assertEqual(result['buck_LS_valley_limit_min_max_A'],[2.5,3.9])
        self.assertEqual(result['feed_current_engineering_budget_A'],4.)
        self.assertFalse(result['feed_current_budget_is_vendor_guarantee'])
        self.assertAlmostEqual(result['feed_budget_power_W'],.84)
        self.assertNotIn('feed_max_2p5A_power_W',result)
        self.assertFalse(cold_start_screen(feed_current_budget_A=4.1)['checks']['feed_power'])
    def test_old_resistor_only_rail_still_fails(self):
        self.assertFalse(cold_start_screen(series_ohm=4700,bleed_ohm=4700)['checks']['all_rails_barrier'])
    def test_omitted_extra_cap_fails_shutdown(self):
        self.assertFalse(screen(opa_extra_uF=0)['checks']['OPA_before_isolation'])
    def test_unbounded_feed_inductance_fails(self):
        self.assertFalse(cold_start_screen(feed_L_H=100e-9)['checks']['feed_overdamped'])
    def test_all_new_source_power_connections(self):
        comps,pins,_=inventory()
        validate_power(*power_checker.source_power_maps(comps,pins))
    def test_source_adapter_rejects_wired_or_absent_intended_nc(self):
        comps,pins,_=inventory()
        for mutation in ('wired','absent'):
            bad=dict(pins)
            if mutation=='wired':bad[('U_DUMP','1')]='GND'
            else:del bad[('U_DUMP','1')]
            with self.assertRaisesRegex(ValueError,'U_DUMP'):
                validate_power(*power_checker.source_power_maps(comps,bad))
    def test_connected_cold_start_has_all_sixteen_input_limiters(self):
        # CS-01: RED measured on0885305f's actual JSX before correction.
        comps,pins,_=inventory()
        for n in range(1,9):
            for leg,pin in [('P','3'),('N','5')]:
                ref=f'R_IN{n}{leg}'
                self.assertIn(ref,comps)
                self.assertEqual(comps[ref][1],'10k')
                self.assertEqual(pins[(ref,'1')],f'BIAS_{leg}{n}')
                self.assertEqual(pins[(ref,'2')],f'AIN_{leg}{n}')
                self.assertEqual(pins[(f'U_AFE{n}',pin)],f'AIN_{leg}{n}')
    def test_thermal_with_fixed150mA85C(self):
        got=screen()
        self.assertTrue(got["thermal_screen_pass"])
        self.assertAlmostEqual(got["dissipation_mW"],308.6)
        self.assertLess(got["reference_board_tj_C"],103)
    def test_thermal_old_package_rejected(self):
        self.assertFalse(screen(theta_ja=167.8)["thermal_screen_pass"])
    def test_all_declared_conditional_screens(self):
        self.assertTrue(all(screen()["checks"].values()),screen()["checks"])
    def test_faster_buck_not_silently_qualified(self):
        self.assertFalse(screen(buck_ramp_ms=3.5)["checks"]["buck_typical_4ms_start"])
    def test_precharge_correct_linear_ramp_not_step_formula(self):
        got=screen()
        self.assertGreater(got["raw_buck_startup_peak_A"],2.38)
        self.assertLess(got["raw_buck_startup_peak_A"],2.5)
    def test_precharge_residual_includes_static_controls_and_leakage(self):
        got=screen()
        self.assertGreater(got['precharge_residual_max_V'],.044)
        self.assertGreater(got['precharge_static_load_A'],.002)
        self.assertNotIn('precharge_settled',got['checks'])
        self.assertLess(got['precharge_bypass_equalization_budget_A'],.5)
        self.assertFalse(got['precharge_bypass_is_coupled_network_proof'])
        self.assertFalse(screen(held_control_A=.020)['checks']['precharge_bypass_conditional_current'])
    def test_old250mA_allocation_fails_audio_demand(self):
        self.assertFalse(screen(local_allocation_A=.25)["checks"]["steady_local"])
    def test_excessive_upstream_allocation_rejected(self):
        self.assertFalse(screen(local_allocation_A=.4)["checks"]["upstream"])
    def test_large_bank_can_fail_current_screen(self):
        self.assertFalse(screen(cap_inventory_uF=1500)["checks"]["buck_ldo_charge"])
    def test_historical_power_fixture_is_explicitly_not_live_admission(self):
        self.assertGreater(validate_legacy_power(POWER_PINS,POWER_VALUES)["power_pin_maps"],10)
        with self.assertRaisesRegex(ValueError,'U_LDO.*stale/retired'):
            validate_power(POWER_PINS,POWER_VALUES)
    def test_reversed_hold_diode(self):
        pins={r:dict(p) for r,p in POWER_PINS.items()}
        pins["D_HOLD"]={"1":"5V_BUCK","2":"5V_LDO_FEED"}
        with self.assertRaisesRegex(ValueError,"D_HOLD"): validate_legacy_power(pins,POWER_VALUES)
    def test_no_precharge_bypass_around_hold(self):
        pins={r:dict(p) for r,p in POWER_PINS.items()}
        pins["Q_PRE"]["2"]="5V_BUCK"
        with self.assertRaisesRegex(ValueError,"Q_PRE"): validate_legacy_power(pins,POWER_VALUES)
    def test_programmer_cannot_change_silently(self):
        values=dict(POWER_VALUES); values["R_PRE"]="1"
        with self.assertRaisesRegex(ValueError,"R_PRE"): validate_legacy_power(POWER_PINS,values)
    def test_missing_nr_cap_rejected(self):
        values=dict(POWER_VALUES); del values["C_LDO_NR4"]
        with self.assertRaisesRegex(ValueError,"C_LDO_NR4"): validate_legacy_power(POWER_PINS,values)
    def test_rated_life_drift_is_not_prototype_allowance(self):
        # Primary test maxima0.5%life+0.5%reflow, plus initial/TCR.
        lo,_=divider(.8,3570,1150,.01,resistor_tol=.012625)
        _,audiohi=divider(1.15,17400,10000,.01,resistor_tol=.012625)
        self.assertGreater(audiohi*1.00825,lo)
        self.assertTrue(any("POWER-DRIFT" in x for x in screen()["qualification_owed"]))
    def test_physical_vacuity_is_declared(self):
        # Same source with an unsoldered EP still passes this numeric model.
        self.assertTrue(screen()["thermal_screen_pass"])
        self.assertTrue(any("EP solder" in x for x in screen()["qualification_owed"]))
        self.assertFalse(screen(theta_ja=167.8)["thermal_screen_pass"])
    def test_capacitance_inventory_keeps_internal_path_separate(self):
        pins={"C_FILT1_470U":{"1":"FILT1P","2":"GND"},
              "C_LDO_D":{"1":"LDO_D_FILT","2":"GND"},
              "C_NEW":{"1":"3V3_ADC","2":"GND"},
              "C_OPA":{"1":"5V_OPA","2":"GND"}}
        values={"C_FILT1_470U":"470uF","C_LDO_D":"4.7uF","C_NEW":"100nF","C_OPA":"47uF"}
        got=capacitance_inventory(pins,values)
        self.assertAlmostEqual(got["conservative_charge_inventory_nominal_uF"],474.8)
        self.assertEqual(len(got["components"]),3)
    def test_inventory_rejects_crossdomain(self):
        with self.assertRaises(ValueError):
            capacitance_inventory({"C_BAD":{"1":"FILT1P","2":"VMID1_EXT"}},{"C_BAD":"1uF"})
    def test_inventory_rejects_unparsed(self):
        with self.assertRaises(ValueError):
            capacitance_inventory({"C_BAD":{"1":"3V3_ADC","2":"GND"}},{"C_BAD":"TBD"})
if __name__=="__main__": unittest.main()
