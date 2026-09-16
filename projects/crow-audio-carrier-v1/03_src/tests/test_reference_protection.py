"""Current OPA2320/passive-bias adoption and hostile protection regressions.

Native isolated source geometry and explicit engineering DC envelopes only;
not installed transient, hot/lifetime or generated-board acceptance. Historical
reference_protection_screen tests below retain old-model arithmetic explicitly,
but that model cannot select the current production validation path.
"""
import copy
from pathlib import Path
import sys
import unittest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check_analog_filter_topology as topology
import check_power_source as power
from source_inventory import inventory, source_rows


def fixture():
    return ({**copy.deepcopy(topology.EXPECTED_PINS),
             'U_ADC': dict(topology.ADC_REFERENCE_PINS)},
            dict(topology.EXPECTED_VALUES))


def validate_opa_dossier(text):
    """Exact source identity only; no native or electrical acceptance.

    Ordinary YAML loaders silently keep the last duplicate mapping key. The
    source-author regression must reject that ambiguity before comparing the
    effective catalog identity with the already-adopted ADR0023 identity.
    """
    node = yaml.compose(text)
    keys = [key.value for key, _ in node.value]
    if len(keys) != len(set(keys)):
        raise ValueError('duplicate top-level dossier key')
    part = yaml.safe_load(text)
    if part['mpn'] != 'OPA2320AIDR' or part['sourcing']['lcsc'] != 'C2863402':
        raise ValueError('OPA2320 exact sourcing identity mismatch')
    refs = part['layout_refs']
    if not any(row['tier'] == 1 and row['reached'] and
               'SBOS513F' in row['artifact'] for row in refs):
        raise ValueError('OPA2320 primary layout authority absent')
    if any('OPA1656' in str(row) or 'SBOS901C' in str(row) for row in refs):
        raise ValueError('superseded amplifier layout authority')
    return part


class ReferenceProtectionTests(unittest.TestCase):
    def test_exact_dossier_has_one_effective_sourcing_identity(self):
        text = (power.PROJECT/'02_parts/OPA2320AIDR/part.yaml').read_text()
        part = validate_opa_dossier(text)
        self.assertEqual(part['sourcing']['lcsc'], 'C2863402')
        self.assertEqual(yaml.safe_load(text)['sourcing'], part['sourcing'])

    def test_exact_dossier_layout_refs_match_selected_primary(self):
        part = yaml.safe_load((power.PROJECT/'02_parts/OPA2320AIDR/part.yaml').read_text())
        self.assertTrue(any('SBOS513F' in row['artifact'] and row['reached']
                            for row in part['layout_refs']))
        self.assertNotIn('OPA1656', str(part['layout_refs']))
        self.assertNotIn('SBOS901C', str(part['layout_refs']))

    def test_rejects_inherited_duplicate_sourcing_override(self):
        text = (power.PROJECT/'02_parts/OPA2320AIDR/part.yaml').read_text()
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            validate_opa_dossier(text + '\nsourcing: {lcsc: C1849431, alternates: []}\n')

    def test_rejects_unique_but_wrong_catalog_identity(self):
        part = yaml.safe_load((power.PROJECT/'02_parts/OPA2320AIDR/part.yaml').read_text())
        part['sourcing']['lcsc'] = 'C1849431'
        with self.assertRaisesRegex(ValueError, 'sourcing identity'):
            validate_opa_dossier(yaml.safe_dump(part))

    def test_rejects_superseded_layout_reference(self):
        part = yaml.safe_load((power.PROJECT/'02_parts/OPA2320AIDR/part.yaml').read_text())
        part['sourcing']['lcsc'] = 'C2863402'
        part['layout_refs'].append({'tier': 1, 'reached': True,
                                   'artifact': 'TI SBOS901C OPA1656 layout'})
        with self.assertRaisesRegex(ValueError, 'layout authority'):
            validate_opa_dossier(yaml.safe_dump(part))

    def test_exact_precision_reference_dividers(self):
        rows = {r['name']: r for r in source_rows()}
        for n in (1, 2):
            for leg in ('TOP', 'BOT'):
                row = rows[f'R_VMID{n}_{leg}']
                with self.subTest(ref=row['name']):
                    self.assertEqual(row['manufacturerPartNumber'], 'RT0603BRD071KL')
                    self.assertEqual(row['supplierPartNumbers'], {'jlcpcb': ['C110776']})
                    self.assertEqual(row['footprint'], '0603')
                    self.assertEqual(row['resistance'], '1k')

    def test_initial_passive_reference_dc_screen_preserves_acceptance_window(self):
        # Independent passive nodal bound, with adopted +/-1uA per leg
        # engineering leakage, not a manufacturer lifetime guarantee.
        rows={r['name']:r for r in source_rows()}
        for n in (1,2):
            part=yaml.safe_load((power.PROJECT/'02_parts/RT0603BRD071KL/part.yaml').read_text())
            tol=float(part['limits']['tolerance'].removesuffix('pct'))/100
            for leg in ('TOP','BOT'):
                self.assertEqual(rows[f'R_VMID{n}_{leg}']['resistance'],'1k')
            rhi,rlo=1000*(1+tol),1000*(1-tol)
            low=(3.23/rhi-8e-6)/(1/rhi+1/rlo+1/10e6+1/100e6)
            high=(3.34/rlo+8e-6)/(1/rlo+1/rhi)
            with self.subTest(bank=n):
                self.assertGreaterEqual(low,1.60)
                self.assertLessEqual(high,1.70)
        # The old10k dividers do not meet that SAME adopted leakage envelope.
        old_low=(3.23/(10000*1.001)-8e-6)/(1/(10000*1.001)+1/(10000*.999))
        self.assertLess(old_low,1.60)

    def test_precision_dividers_clear_all_source_native_library_parts(self):
        from test_route_source_contract import load_source
        from test_digital_launch_source import native_geometry
        from test_startup_source import clearances
        floor, *_ = load_source()
        targets = {f'R_VMID{n}_{leg}' for n in (1, 2) for leg in ('TOP', 'BOT')}
        failures, counts = clearances(native_geometry(floor), targets)
        self.assertEqual(failures, [])
        self.assertTrue(all(n > 0 for n in counts.values()))

    def test_eight_exact_amplifiers_on_shared_adc_rail(self):
        comps,pins,_=inventory()
        refs={r for r in comps if r.startswith('U_AFE')}
        self.assertEqual(refs,{f'U_AFE{n}' for n in range(1,9)})
        for ref in refs:
            self.assertEqual(comps[ref][1],'OPA2320AIDR')
            self.assertEqual(pins[(ref,'8')],'3V3_ADC')
            self.assertEqual(pins[(ref,'4')],'GND')

    def test_rejects_old_amplifier_identity(self):
        pins, values = fixture()
        values['U_AFE1'] = 'OPA1656IDR'
        with self.assertRaises(topology.TopologyError):
            topology.validate(pins, values)

    def test_actual_source_topology_and_dossier_identity(self):
        comps, pins, _ = inventory()
        receipt = topology.validate(*power.source_power_maps(comps, pins))
        self.assertEqual(receipt['exact_amplifiers'], 8)
        self.assertEqual(receipt['reference_input_current_limit_resistors'], 0)

    def test_adopted_exact_orderable_identities(self):
        rows={r['name']:r for r in source_rows()}
        for n in range(1,9):
            self.assertEqual(rows[f'U_AFE{n}']['manufacturerPartNumber'],'OPA2320AIDR')
            self.assertEqual(rows[f'U_AFE{n}']['supplierPartNumbers'],{'jlcpcb':['C2863402']})
        for n in (1,2):
            for leg in ('TOP','BOT'):
                self.assertEqual(rows[f'R_VMID{n}_{leg}']['manufacturerPartNumber'],'RT0603BRD071KL')
                self.assertEqual(rows[f'R_VMID{n}_{leg}']['supplierPartNumbers'],{'jlcpcb':['C110776']})
            self.assertNotIn(f'R_VMID{n}_IN',rows)
            self.assertNotIn(f'R_VMID{n}_ISO',rows)
        self.assertNotIn('U_AFE9',rows)

    def test_passive_reference_parts_clear_all_native_parts_and_exact_adjacencies(self):
        from test_route_source_contract import load_source
        from test_digital_launch_source import native_geometry
        from test_startup_source import clearances,copper_gap
        floor,*_=load_source();geometry=native_geometry(floor)
        targets={f'R_VMID{n}_{leg}' for n in (1,2) for leg in ('TOP','BOT')}
        targets|={f'C_VMID{n}_EXT_{cap}' for n in (1,2) for cap in ('1U','10U')}
        failures,counts=clearances(geometry,targets)
        self.assertEqual(failures,[]);self.assertEqual(counts['courtyard'],8*332)
        pads={p['id']:p for p in geometry['pads']}
        part=yaml.safe_load((power.PROJECT/'02_parts/RT0603BRD071KL/part.yaml').read_text())
        rows=part['layout']['adjacency'];self.assertEqual(len(rows),6)
        for row in rows:
            a,b=row['refdes']
            gap=min(copper_gap(pa['shape'],pb['shape'])
                for pa in pads.values() if pa['id'].startswith(a+'.') and pa['net'] in row['nets']
                for pb in pads.values() if pb['id'].startswith(b+'.') and pb['net']==pa['net'])
            self.assertLessEqual(gap,row['max_mm'],row)

    def test_reference_screen_rejects_invalid_domain(self):
        for kwargs in ({'input_ohm':0}, {'output_ohm':-1}, {'retained_V':float('nan')},
                       {'resistance_reserve':1}, {'resistance_reserve':-.01}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                power.reference_protection_screen(**kwargs)

    def test_rejects_direct_reference_to_amplifier_input(self):
        for n,pin in ((1,'3'),(5,'5')):
            pins,values=fixture()
            pins[f'U_AFE{n}'][pin]=f'VMID{1 if n<=4 else 2}_EXT'
            with self.subTest(channel=n),self.assertRaises(topology.TopologyError):
                topology.validate(pins,values)

    def test_rejects_missing_signal_input_limiter(self):
        pins,values=fixture();pins.pop('R_IN2P');values.pop('R_IN2P')
        with self.assertRaises(topology.TopologyError):topology.validate(pins,values)

    def test_rejects_parallel_reference_input_bypass(self):
        pins, values = fixture()
        pins['R_BYPASS'] = {'1': 'VMID1_EXT', '2': 'VMID1_IN'}
        values['R_BYPASS'] = '0'
        with self.assertRaises(topology.TopologyError):
            topology.validate(pins, values)

    def test_rejects_old_buffered_reference_arrangement(self):
        for n in (1,2):
            pins,values=fixture()
            pins['U_AFE9']={'1':f'VMID{n}_BUF','8':'3V3_ADC'}
            values['U_AFE9']='OPA2320AIDR'
            with self.subTest(bank=n),self.assertRaises(topology.TopologyError):
                topology.validate(pins,values)

    def test_signal_feedback_cannot_be_reassigned_to_passive_reference(self):
        pins,values=fixture();pins['U_AFE1']['2']='VMID1_EXT'
        with self.assertRaises(topology.TopologyError):topology.validate(pins,values)

    def test_reference_current_screen_has_margin_and_explicit_scope(self):
        result = power.reference_protection_screen()
        self.assertTrue(all(result['checks'].values()))
        self.assertLess(result['positive_input_current_A'], .00057)
        self.assertLess(result['combined_output_feedback_current_A'], .0057)
        self.assertFalse(result['proves_node_voltage_envelope'])
        self.assertFalse(result['proves_output_pin_overdrive_rating'])
        self.assertAlmostEqual(result['output_RC_nominal_ms'], 4.7)

    def test_reference_screen_rejects_old_output_resistor(self):
        result = power.reference_protection_screen(output_ohm=100)
        self.assertFalse(result['checks']['feedback_input_current'])

    def test_reference_screen_rejects_undersized_input_resistor(self):
        result = power.reference_protection_screen(input_ohm=100)
        self.assertFalse(result['checks']['positive_input_current'])


if __name__ == '__main__':
    unittest.main()
