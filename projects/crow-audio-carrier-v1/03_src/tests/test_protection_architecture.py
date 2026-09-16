"""ADR0025 fixed-source positive/hostile contracts; no transient sweep."""
from copy import deepcopy
import math
import re
import subprocess
from pathlib import Path
import sys
import unittest
import yaml
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check_protection_architecture import calculate,validate,source_receipt,PROJECT
from check_power_source import source_power_maps
from source_inventory import inventory

class SharedRailProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        comps,flat,_=inventory()
        cls.pins,cls.values=source_power_maps(comps,flat)

    def test_actual_source_and_exact_primary_hashes(self):
        row=source_receipt(self.pins,self.values)
        self.assertTrue(all(row['checks'].values()))
        self.assertEqual(row['coverage']['amplifiers'],8)
        self.assertFalse(row['generation_admitted'])
        self.assertFalse(row['physical_qualified'])
        self.assertFalse(row['investigation_launched'])

    def test_all_eight_rails_individually_reject_split_supply(self):
        for n in range(1,9):
            p=deepcopy(self.pins);p[f'U_AFE{n}']['8']='5V_OPA'
            with self.subTest(n=n),self.assertRaises(ValueError):validate(p,self.values)

    def test_all_sixteen_bleeds_reject_old_100k(self):
        for n in range(1,9):
            for leg in ('P','N'):
                v=dict(self.values);v[f'R_ADC_PD{n}{leg}']='100k'
                with self.subTest(n=n,leg=leg),self.assertRaises(ValueError):validate(self.pins,v)

    def test_ldo_input_output_swap_and_grounded_nc_rejected(self):
        for pin,net in [('1','3V3_ADC'),('14','5V_LDO_HOLD'),('4','GND'),('15','3V3_ADC')]:
            p=deepcopy(self.pins);p['U_LDO'][pin]=net
            with self.subTest(pin=pin),self.assertRaises(ValueError):validate(p,self.values)

    def test_removed_reference_buffer_cannot_return(self):
        v=dict(self.values);v['U_AFE9']='OPA2320AIDR'
        with self.assertRaises(ValueError):validate(self.pins,v)

    def test_dump_resistor_cannot_bypass_discharge_bound(self):
        v=dict(self.values);v['R_DUMP']='0.01'
        with self.assertRaises(ValueError):validate(self.pins,v)

    def test_reversed_buck_isolation_diode_rejected(self):
        p=deepcopy(self.pins);p['D_BUCK_IN']={'1':'12V_PROTECTED','2':'12V_BUCK_IN'}
        with self.assertRaises(ValueError):validate(p,self.values)

    def test_adc_on_other_rail_rejected(self):
        p=deepcopy(self.pins);p['U_ADC']['5']=p['U_ADC']['9']='OTHER_SUPPLY'
        with self.assertRaises(ValueError):validate(p,self.values)

    def test_output_tracking_is_explicit_and_falsifiable(self):
        self.assertEqual(calculate()['amplifier_output_tracking_engineering_budget_V'],.05)
        self.assertFalse(calculate(output_tracking_error_V=.2)['checks']['combined_relative_pin_error_below_0p3V'])

    def test_no_cross_leg_capacitor_can_return(self):
        for n in range(1,9):
            for leg in 'PN':
                p=deepcopy(self.pins);p[f'C_FILTER{n}{leg}1']['2']=f'FILTER{n}{"N" if leg=="P" else "P"}'
                with self.subTest(n=n,leg=leg),self.assertRaises(ValueError):validate(p,self.values)

    def test_old_bridge_has_a_passive_counterexample_new_shunts_do_not(self):
        # Algebraic counterexample to an insufficient assumption, NOT evidence
        # that real silicon reaches simultaneous zero-output collapse.
        t=70e-9;common=1.65;leg=1.2/math.sqrt(2)
        old_negative=common*math.exp(-t/(10*1e-9))-leg*math.exp(-t/(10*31e-9))
        self.assertLess(old_negative,-.3)
        # Independent positive RC legs cannot transfer the other leg's charge.
        new_low=(common-leg)*math.exp(-t/(10*31e-9))
        self.assertGreater(new_low,0)

    def test_reference_divider_and_set_changes_rejected(self):
        for ref in ['R_VMID1_TOP','R_VMID2_BOT','R_LDO_SET']:
            v=dict(self.values);v[ref]='10k'
            with self.subTest(ref=ref),self.assertRaises(ValueError):validate(self.pins,v)

    def test_old_500ohm_rail_bleed_fails_all16_injection(self):
        self.assertFalse(calculate(bleed_ohm=500)['checks']['all16_rail_barrier'])

    def test_old_100k_node_bleed_fails_rail_relative_bound(self):
        self.assertFalse(calculate(adc_bleed_ohm=100000)['checks']['off_ADC_inward_barrier_derivative'])

    def test_one_missing_output_cap_invalidates_fast_discharge(self):
        self.assertFalse(calculate(direct_min_uF=8)['checks']['combined_relative_pin_error_below_0p3V'])

    def test_excess_reverse_sink_fails_off_barrier(self):
        self.assertFalse(calculate(falling_load_A=2)['checks']['off_ADC_inward_barrier_derivative'])

    def test_charge_injection_budget_is_not_a_guaranteed_typical(self):
        row=calculate()
        self.assertGreater(row['switch_charge_engineering_budget_C'],5e-12)
        self.assertFalse(calculate(switch_charge_C=300e-12)['checks']['combined_relative_pin_error_below_0p3V'])

    def test_extra_load_or_capacitance_fails_startup_budget(self):
        self.assertFalse(calculate(startup_available_A=.4)['checks']['startup_charge_budget_10ms'])
        self.assertFalse(calculate(cap_nominal_uF=4000)['checks']['startup_charge_budget_10ms'])

    def test_invalid_numbers_rejected(self):
        for value in [0,-1,float('nan'),float('inf')]:
            with self.subTest(value=value),self.assertRaises(ValueError):calculate(bleed_ohm=value)

    def test_audio_and_header_constraints_preserved(self):
        row=calculate()
        self.assertGreater(row['normal_leg_signal_window_V'][0],.7)
        self.assertLess(row['normal_leg_signal_window_V'][1],2.6)
        self.assertGreater(row['added_shunt_gain_lower'],.99996)
        self.assertLess(row['local_5V_steady_A'],.30)
        self.assertLess(row['upstream_trunk_budget_A'],1.)
        self.assertGreaterEqual(row['header_floor_V'],10.8)

    def test_current_seeds_bind_current_pin_nets_not_retired_regulator(self):
        route=yaml.safe_load((PROJECT/'03_src/route.yaml').read_text())
        self.assertEqual(route['route']['import_source'],'promoted')
        self.assertIsInstance(route['prep']['waves'],dict)
        stubs=route['prep']['seed_stubs']['stubs']
        self.assertTrue(stubs)
        for stub in stubs:
            ref, pin=stub['pin'].rsplit('.',1)
            self.assertIn(ref,self.pins,stub['pin'])
            self.assertEqual(stub['net'],self.pins[ref][pin],stub['pin'])
        ldo={s['pin']:s['net'] for s in stubs if s['pin'].startswith('U_LDO.')}
        self.assertEqual(ldo,{f'U_LDO.{p}':self.pins['U_LDO'][str(p)]
                             for p in (1,2,3,5,7,8,9,10,11,12,13,14)})
        # The old TPS assignments (OUT1/2, IN9/10, EP11) cannot pass the
        # current electrical map. Geometry, widths and Kelvin separation are
        # independently screened by the native-footprint regulator suite.

    def test_changed_rule_files_are_well_formed(self):
        for rel in ['floorplan.yaml','route.yaml','rules/nets.yaml','rules/power_tree.yaml','rules/electrical_invariants.yaml','rules/first_article.yaml']:
            with self.subTest(rel=rel):self.assertIsInstance(yaml.safe_load((PROJECT/'03_src'/rel).read_text()),dict)

    def test_conductors_enforce_current_protection_before_downstream_work(self):
        # RED against the pre-integration drivers: neither invoked this checker.
        for name,modes in [('rebuild_all.sh',[' --source-only','']),
                           ('rebuild_reuse.sh',[''])]:
            source=(PROJECT/'03_src'/name).read_text()
            for mode in modes:
                with self.subTest(driver=name,mode=mode):
                    pattern=r'^\$PY -B 03_src/check_power_source\.py'+mode+r' \\\n    \|\| \{[^\n]+\}\n'
                    blocks=re.findall(pattern,source,re.M)
                    self.assertEqual(len(blocks),1)
                    block=blocks[0]
                    downstream=('run_stage tscircuit_build ' if mode else
                                '$PY "$S/pre_route_review_check.py" . --phase schematic')
                    self.assertLess(source.index(block),source.index(downstream))
                    # Exercise the real shell guard in isolation, not a grep
                    # claiming that the named command's failure stops a build.
                    for code in (0,23):
                        probe=f'fake_python() {{ return {code}; }}\nPY=fake_python\n'+block+"printf 'DOWNSTREAM_REACHED\\n'\n"
                        result=subprocess.run(['bash','-c',probe],capture_output=True,text=True,timeout=5)
                        self.assertEqual(result.returncode,0 if code==0 else 1)
                        self.assertEqual('DOWNSTREAM_REACHED' in result.stdout,code==0)

if __name__=='__main__':unittest.main()
