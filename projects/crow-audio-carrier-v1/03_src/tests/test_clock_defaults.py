"""Known-good and hostile bias-network regression tests; no hardware claims."""
import copy
import re
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_clock_defaults import EXPECTED, PROJECT, screen, tdm_screen, validate_source, validate_netlist
from check_analog_filter_topology import parse_native_netlist


class ClockDefaultsTests(unittest.TestCase):
    def test_exact_additive_tdm_geometry_and_digital_path_census(self):
        import subprocess, yaml
        from test_route_source_contract import load_source
        floor,route,nets,*_=load_source()
        root=PROJECT.parents[1]
        def old(name, revision='a17ede026cceabb821738884857e99b6823e056f'):
            return yaml.safe_load(subprocess.check_output(['git','show',revision+':projects/crow-audio-carrier-v1/03_src/'+name],cwd=root,timeout=15))
        added={'U_TDM_SCH':[147.5,52,0],'R_TDM_PD':[144.7,52,90],'C_TDM_SCH':[150.75,51.05,0]}
        self.assertEqual({r:floor['placement']['anchors'][r] for r in added},added)
        accepted_route=old('route.yaml','1b725986')
        self.assertEqual(route['prep']['waves']['groups']['clocks'],
                         ['TDM_BUFFERED','TDM_CLEAN','ADC_TDM'])
        complete=set(nets['classes']['ADC_CLOCK']['nets'])-set(route['prep']['waves']['groups']['clocks'])
        for net in complete:
            self.assertIn(net,route['prep']['waves']['exclude'])
            self.assertEqual(route['route']['ownership']['nets'][net]['owner'],'prep.seed_stubs')
        current=next(w for w in route['route']['waves'] if w['name']=='clocks')
        self.assertEqual(current['layers'],['F.Cu'])
        self.assertEqual(current['clearance'],.25)
        self.assertEqual(dict(zip(current['power_nets'],current['power_nets_widths'])),
                         dict.fromkeys(nets['classes']['ADC_CLOCK']['nets'],.36))
        self.assertEqual(current['realized_width'],dict(nominal=.36,minimum=.18,
                         max_subnominal_length_per_net=3.,max_subnominal_segments_per_net=3))
        self.assertEqual((current['ordering'],current['keepout_layer']),('mps','User.2'))
        before_nets=old('rules/nets.yaml')
        names=('MCH_INPUT_SECTIONS','BUFFERED_DIGITAL_SECTIONS')
        def segments(spec):
            return [(s['net'],s['from'],s['to']) for name in names for paths in spec['length_match'][name]['paths'].values() for p in paths for s in p['segments']]
        oldrows,newrows=segments(before_nets),segments(nets)
        self.assertEqual((len(oldrows),len(newrows)),(15,17))
        self.assertEqual(set(oldrows)-set(newrows),{('TDM_RAW','U_ADC.25','U_TDM.2')})
        self.assertEqual(set(newrows)-set(oldrows),{('TDM_RAW','U_ADC.25','U_TDM_SCH.2'),('TDM_CLEAN','U_TDM_SCH.4','U_TDM.2'),('TDM_RAW','U_TDM_SCH.2','R_TDM_PD.1')})
        self.assertEqual((len(before_nets['classes']['ADC_CLOCK']['nets']),len(nets['classes']['ADC_CLOCK']['nets'])),(12,13))
        for name in names:
            self.assertEqual(nets['length_match'][name]['max_spread_mm'],'report')
            self.assertTrue(nets['length_match'][name]['no_vias'])
        accepted_nets=old('rules/nets.yaml','1b725986')
        for name in names:
            for key in ('topology','max_spread_mm','members','paths'):
                self.assertEqual(nets['length_match'][name][key],
                                 accepted_nets['length_match'][name][key])
        for key in ('nets','current','min_width','clearance'):
            self.assertEqual(nets['classes']['ADC_CLOCK'][key],accepted_nets['classes']['ADC_CLOCK'][key])
        self.assertEqual(nets['reference_plane_checks']['ADC_DIGITAL_RETURN'],
                         accepted_nets['reference_plane_checks']['ADC_DIGITAL_RETURN'])

    def test_new_bypass_is_charged_by_live_power_inventory(self):
        from check_power_source import capacitance_inventory
        pins,values=parse_native_netlist(PROJECT/'06_build/netlists/crow_audio_carrier_v1.net')
        new=capacitance_inventory(pins,values)
        oldpins=copy.deepcopy(pins);oldpins.pop('C_TDM_SCH')
        old=capacitance_inventory(oldpins,values)
        row=next(r for r in new['components'] if r['ref']=='C_TDM_SCH')
        self.assertEqual(row['group'],'direct_3V3_ADC');self.assertAlmostEqual(row['nominal_uF'],.1)
        self.assertAlmostEqual(new['conservative_charge_inventory_nominal_uF']-old['conservative_charge_inventory_nominal_uF'],.1)

    def test_tdm_allocation_corners_and_nonvacuous_hostiles(self):
        good = tdm_screen()
        self.assertEqual(good['guarantee'], 'NOT_ESTABLISHED')
        self.assertTrue(good['open'])
        self.assertEqual(len(good['checks']), 7)
        self.assertTrue(all(good['checks'].values()))
        self.assertAlmostEqual(good['measurements']['released_raw_V'], .2163)
        self.assertGreater(good['measurements']['release_to_0p4V_ns'], 500)
        for args, failed in [({'r_ohm':1e6},'released_low'),
                             ({'r_ohm':1000},'adc_load'),
                             ({'adc_board_leak_uA':50},'released_low'),
                             ({'raw_cap_pF':51},'raw_cap'),
                             ({'clean_load_uA':101},'clean_load'),
                             ({'path_allowance_ns':15},'timing_margin'),
                             ({'bclk_hz':24_576_000},'timing_margin')]:
            with self.subTest(args=args):
                self.assertFalse(tdm_screen(**args)['checks'][failed])

    def test_tdm_wrong_conditioning_identity_net_bias_and_bypass_rejected(self):
        source = (PROJECT / '03_tscircuit/src/crow_audio_carrier_v1.tsx').read_text()
        for old,new in [('74LVC1G17GV,125','74LVC1G14GV,125'),
                        ('jlc="C6076"','jlc="C131093"'),
                        ('pin2: N("TDM_CLEAN")','pin2: N("TDM_RAW")'),
                        ('name="C_TDM_SCH"','name="C_MISSING"'),
                        ('name="R_TDM_PD" value="10k"','name="R_TDM_PD" value="1M"'),
                        ('a="TDM_RAW" b="GND"','a="TDM_RAW" b="3V3_ADC"')]:
            self.assertIn(old,source)
            with self.subTest(old=old), self.assertRaises(ValueError):
                validate_source(source.replace(old,new),PROJECT)
    def test_tdm_raw_has_bias_and_true_noninverting_conditioner(self):
        source = (PROJECT / "03_tscircuit/src/crow_audio_carrier_v1.tsx").read_text()
        self.assertIn('<R2 name="R_TDM_PD" value="10k" a="TDM_RAW" b="GND"', source)
        self.assertIn('<Chip name="U_TDM_SCH" manufacturerPartNumber="74LVC1G17GV,125" jlc="C6076"', source)

    def test_missing_tdm_bias_is_rejected_by_production_checker(self):
        source = (PROJECT / "03_tscircuit/src/crow_audio_carrier_v1.tsx").read_text()
        bad = re.sub(r'<R2 name="R_TDM_PD"[^>]*/>', '', source)
        with self.assertRaises(ValueError):
            validate_source(bad, PROJECT)

    def test_generated_tdm_bias_and_conditioning_endpoints(self):
        pins, _ = parse_native_netlist(PROJECT / "06_build/netlists/crow_audio_carrier_v1.net")
        self.assertEqual(pins.get('R_TDM_PD'), {'1':'TDM_RAW', '2':'GND'})
        self.assertEqual(pins.get('U_TDM_SCH'), {'1':'', '2':'TDM_RAW', '3':'GND', '4':'TDM_CLEAN', '5':'3V3_ADC'})
        self.assertEqual(pins['U_TDM']['2'], 'TDM_CLEAN')

    def test_live_source_and_exact_dossiers(self):
        validate_source((PROJECT / "03_tscircuit/src/crow_audio_carrier_v1.tsx").read_text(), PROJECT)

    def test_good_screen(self):
        result = screen()
        self.assertEqual(len(result["checks"]), 9)
        self.assertTrue(all(result["checks"].values()))
        self.assertAlmostEqual(result["measurements"]["clock_allocated_low_V"], 0.2575)
        self.assertAlmostEqual(result["measurements"]["oe_disabled_V"], 2.9)

    def test_old_clock_pulls_fail(self):
        self.assertFalse(screen(clock_r=1_000_000)["checks"]["receiver_low"])

    def test_overstrong_clock_load_fails(self):
        self.assertFalse(screen(clock_r=1_000)["checks"]["clock_load"])

    def test_old_sense_divider_fails(self):
        checks = screen(gate_r=1_000_000, sense_r=100_000)["checks"]
        self.assertFalse(checks["gate_absent"])
        self.assertFalse(checks["gate_present"])

    def test_overloaded_push_pull_oe_fails(self):
        self.assertFalse(screen(oe_load_uA=101)["checks"]["oe_output_load"])

    def test_legacy_rc_oe_and_adc_cs_ground_fail(self):
        source = (PROJECT / "03_tscircuit/src/crow_audio_carrier_v1.tsx").read_text()
        for bad in (source + '<R2 name="R_TDM_OE_PU" />',
                    source + '<Chip name="Q_TDM_EN" />',
                    source.replace('pin38: N("3V3_ADC")', 'pin38: N("GND")'),
                    source.replace('manufacturerPartNumber="74LVC1G14GV,125"',
                                   'manufacturerPartNumber="SN74LVC1G125DBVR"'),
                    source.replace('<C2 name="C_OE"', '<C2 name="C_MISSING"')):
            with self.subTest(bad=bad[-60:]), self.assertRaises(ValueError):
                validate_source(bad, PROJECT)

    def test_missing_source_wrong_value_code_or_polarity_fail(self):
        source = (PROJECT / "03_tscircuit/src/crow_audio_carrier_v1.tsx").read_text()
        marker = '<R2 name="R_MCH_MCLK_PD" value="10k" a="MCH_MCLK" b="GND" jlc="C60490"'
        self.assertIn(marker, source)
        for bad in ("", marker.replace('value="10k"', 'value="1M"'),
                    marker.replace('jlc="C60490"', 'jlc="C138033"'),
                    marker.replace('b="GND"', 'b="3V3_ADC"')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                validate_source(source.replace(marker, bad, 1), PROJECT)

    def test_exact_generated_pins_and_values(self):
        pins = {ref: {"1": a, "2": b} for ref, (_, a, b, _, _) in EXPECTED.items()}
        pins.update({
            "U_ADC": {"25": "TDM_RAW"},
            "U_CLK": {"1": "MCH_MCLK", "2": "FSYNC_BUF", "3": "MCH_BCLK", "4": "GND",
                      "5": "BCLK_BUF", "6": "MCH_FSYNC", "7": "MCLK_BUF", "8": "3V3_ADC"},
            "U_TDM": {"1": "TDM_OE_N", "2": "TDM_CLEAN", "3": "GND", "4": "TDM_BUFFERED", "5": "3V3_ADC"},
            "U_TDM_SCH": {"1": "", "2": "TDM_RAW", "3": "GND", "4": "TDM_CLEAN", "5": "3V3_ADC"},
            "C_TDM_SCH": {"1": "3V3_ADC", "2": "GND"},
            "U_OE": {"1": "", "2": "TDM_SENSE_G", "3": "GND", "4": "TDM_OE_N", "5": "3V3_ADC"},
            "C_OE": {"1": "3V3_ADC", "2": "GND"},
        })
        values = {ref: value + "Ω" for ref, (value, *_rest) in EXPECTED.items()}
        validate_netlist(pins, values)
        for ref in EXPECTED:
            bad = dict(values, **{ref: "1MΩ"})
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                validate_netlist(pins, bad)
        badpins = copy.deepcopy(pins)
        badpins["U_CLK"]["1"] = "3V3_ADC"
        with self.assertRaises(ValueError):
            validate_netlist(badpins, values)
        badpins = copy.deepcopy(pins)
        badpins["U_OE"]["1"] = "GND"
        with self.assertRaises(ValueError):
            validate_netlist(badpins, values)
        for ref in ('U_TDM_SCH','R_TDM_PD','C_TDM_SCH'):
            badpins = copy.deepcopy(pins)
            del badpins[ref]
            with self.subTest(ref=ref), self.assertRaises(ValueError):
                validate_netlist(badpins,values)
        badpins = copy.deepcopy(pins)
        badpins['C_EXTRA'] = {'1':'TDM_RAW','2':'GND'}
        with self.assertRaises(ValueError):
            validate_netlist(badpins,values)


if __name__ == "__main__":
    unittest.main()
