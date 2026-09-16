from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml


MODULE_PATH = Path(__file__).resolve().parents[1] / "check_analog_filter_topology.py"
SPEC = importlib.util.spec_from_file_location("carrier_analog_filter", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)


def valid_fixture() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    return (
        {**{ref: dict(pins) for ref, pins in checker.EXPECTED_PINS.items()},
         "U_ADC": dict(checker.ADC_REFERENCE_PINS)},
        dict(checker.EXPECTED_VALUES),
    )


class AnalogFilterTopologyHostiles(unittest.TestCase):
    def test_accepts_exact_vendor_topology(self) -> None:
        receipt = checker.validate(*valid_fixture())
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual(receipt["same_leg_feedback_resistors"], 16)

    def test_accepts_kicad_native_ohm_glyph_without_weakening_value(self) -> None:
        pins, values = valid_fixture()
        values["R_X1P"] = "300Ω"
        values["R_VMID1_TOP"] = "1k ohm"
        self.assertEqual(checker.validate(pins, values)["status"], "PASS")

        values["R_X1P"] = "301Ω"
        with self.assertRaisesRegex(checker.TopologyError, "R_X1P value"):
            checker.validate(pins, values)

    def test_rejects_crossed_feedback_leg(self) -> None:
        pins, values = valid_fixture()
        pins["R_X1P"]["2"] = "ADC1N"
        with self.assertRaisesRegex(checker.TopologyError, "R_X1P pin map"):
            checker.validate(pins, values)

    def test_rejects_missing_passive_vmid_divider_resistor(self) -> None:
        pins, values = valid_fixture()
        del pins["R_VMID2_BOT"]
        with self.assertRaises(checker.TopologyError):
            checker.validate(pins, values)

    def test_rejects_direct_vmid_feedback_tie(self) -> None:
        pins, values = valid_fixture()
        pins["U_AFE1"]["2"] = "VMID1_EXT"
        with self.assertRaises(checker.TopologyError):
            checker.validate(pins, values)

    def test_rejects_wrong_c0g_network_value(self) -> None:
        pins, values = valid_fixture()
        values["C_FILTER8N2"] = "10nF"
        with self.assertRaisesRegex(checker.TopologyError, "C_FILTER8N2 value"):
            checker.validate(pins, values)

    def test_rejects_reversed_adc_filter_bulk_cap(self) -> None:
        pins, values = valid_fixture()
        pins["C_FILT1_470U"] = {"1": "FILT1N", "2": "FILT1P"}
        with self.assertRaisesRegex(checker.TopologyError, "C_FILT1_470U pin map"):
            checker.validate(pins, values)

    def test_rejects_extra_feedback_channel(self) -> None:
        pins, values = valid_fixture()
        pins["R_X9P"] = {"1": "FB_P9", "2": "ADC9P"}
        with self.assertRaisesRegex(checker.TopologyError, "R_X census"):
            checker.validate(pins, values)

    def test_rejects_hardware_mode_internal_vmid_follower(self) -> None:
        for pin, net in (("3", "VMID1"), ("5", "VMID2")):
            pins, values = valid_fixture()
            pins["U_AFE1"][pin] = net
            with self.assertRaises(checker.TopologyError):
                checker.validate(pins, values)

    def test_rejects_indirect_adc_vmid_loading(self) -> None:
        pins, values = valid_fixture()
        pins["R_EXTRA"] = {"1": "VMID1", "2": "VMID1_EXT"}
        with self.assertRaisesRegex(checker.TopologyError, "decouplers only"):
            checker.validate(pins, values)

    def test_rejects_wrong_divider_supply_ratio_and_missing_bypass(self) -> None:
        for kind in ("supply", "ratio", "bypass"):
            pins, values = valid_fixture()
            if kind == "supply":
                pins["R_VMID1_TOP"]["1"] = "5V_OPA"
            elif kind == "ratio":
                values["R_VMID2_BOT"] = "100k"
            else:
                del pins["C_VMID1_EXT_10U"]
            with self.assertRaises(checker.TopologyError):
                checker.validate(pins, values)

    def test_rejects_resistive_negative_returns_on_pin_or_cap(self) -> None:
        for ref, pin, net in (("U_ADC", "17", "FILT2N"),
                              ("U_ADC", "44", "FILT1N"),
                              ("C_FILT1_10U", "2", "FILT1N")):
            pins, values = valid_fixture()
            pins[ref][pin] = net
            with self.assertRaises(checker.TopologyError):
                checker.validate(pins, values)

    def test_rejects_resurrected_ground_leg_resistor(self) -> None:
        pins, values = valid_fixture()
        pins["R_FILT1N"] = {"1": "FILT1N", "2": "GND"}
        values["R_FILT1N"] = "1"
        with self.assertRaisesRegex(checker.TopologyError, "forbidden"):
            checker.validate(pins, values)

    def test_rejects_lost_raw_adc_vmid_bypass(self) -> None:
        pins, values = valid_fixture()
        del pins["C_VMID2_470N"]
        with self.assertRaises(checker.TopologyError):
            checker.validate(pins, values)

    def test_rejects_cross_leg_bridge_even_when_renamed(self) -> None:
        for ref in ('C_DIFF1', 'C_EXTRA'):
            pins, values = valid_fixture()
            pins[ref] = {'1':'FILTER1P', '2':'FILTER1N'}
            values[ref] = '15nF'
            with self.assertRaisesRegex(checker.TopologyError, 'forbidden'):
                checker.validate(pins, values)

    def test_rejects_missing_or_extra_independent_shunt(self) -> None:
        for extra in (False, True):
            pins, values = valid_fixture()
            if extra:
                pins['C_FILTER9P1'] = {'1':'FILTER1P','2':'GND'}
            else:
                del pins['C_FILTER1P1']
            with self.assertRaisesRegex(checker.TopologyError, 'C_FILTER census'):
                checker.validate(pins, values)


class NativeIdentityTests(unittest.TestCase):
    """Exercise native input, not an expected-value map fed back to validate.

    The fresh-native regression was run RED before the adapter: U_AFE1
    remained C2863402 even though the dossier and producer named OPA2320AIDR.
    The small fixtures below independently supply code/MPN/package authority.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.parts = self.root / 'parts'
        self.parts.mkdir()
        self.netlist = self.root / 'native.net'
        self.authority('amplifier', 'OPA2320AIDR', 'C2863402', 'Pkg:SOIC8')
        self.authority('LT3041ADE-TRPBF', 'LT3041ADE#TRPBF', 'C7452883', 'Pkg:DFN14')

    def authority(self, directory, mpn, code, footprint, **extra):
        target = self.parts / directory
        target.mkdir(exist_ok=True)
        record = dict(mpn=mpn, manufacturer='fixture manufacturer',
                      footprint=footprint, sourcing={'lcsc': code}, **extra)
        (target / 'part.yaml').write_text(yaml.safe_dump(record))

    def read(self, value='C2863402', footprint='Pkg:SOIC8', extra=''):
        self.netlist.write_text(f'''(export (version "E")
          (components (comp (ref "U_AFE1") (value "{value}")
            (footprint "{footprint}")) {extra})
          (nets (net (code "1") (name "GND")
            (node (ref "U_AFE1") (pin "4")))))''')
        return checker.parse_native_netlist(self.netlist, parts=self.parts)

    def test_fresh_native_reaches_exact_analog_and_power_predicates(self):
        project = MODULE_PATH.parents[1]
        pins, values = checker.parse_native_netlist(
            project / '06_build/netlists/crow_audio_carrier_v1.net')
        self.assertEqual('OPA2320AIDR', values['U_AFE1'])
        self.assertEqual('LT3041ADE#TRPBF', values['U_LDO'])
        self.assertEqual('PASS', checker.validate(pins, values)['status'])
        from check_power_source import validate_power
        self.assertEqual(8, validate_power(pins, values)['channels'])

    def test_exact_code_and_direct_mpn_resolve_without_changing_pins(self):
        for token in ('C2863402', 'OPA2320AIDR'):
            pins, values = self.read(token)
            self.assertEqual({'U_AFE1': {'4': 'GND'}}, pins)
            self.assertEqual({'U_AFE1': 'OPA2320AIDR'}, values)

    def test_dossier_field_not_directory_name_is_mpn(self):
        _, values = self.read('C7452883', 'Pkg:DFN14')
        self.assertEqual('LT3041ADE#TRPBF', values['U_AFE1'])

    def test_known_wrong_code_is_not_replaced_by_refdes_expectation(self):
        self.authority('other', 'WRONG_AMPLIFIER', 'C999', 'Pkg:SOIC8')
        _, actual = self.read('C999')
        pins, values = valid_fixture()
        values.update(actual)
        with self.assertRaisesRegex(checker.TopologyError, 'U_AFE1 value'):
            checker.validate(pins, values)

    def test_unknown_code_fails_closed(self):
        with self.assertRaisesRegex(checker.TopologyError, 'unresolved.*C999'):
            self.read('C999')

    def test_missing_and_wrong_package_fail_for_code_and_mpn(self):
        for value in ('C2863402', 'OPA2320AIDR'):
            for footprint in ('', 'Pkg:TSSOP8'):
                with self.subTest(value=value, footprint=footprint):
                    with self.assertRaisesRegex(checker.TopologyError, 'footprint'):
                        self.read(value, footprint)

    def test_ambiguous_code_fails_even_when_one_package_matches(self):
        self.authority('conflict', 'OTHER_MPN', 'C2863402', 'Pkg:TSSOP8')
        with self.assertRaisesRegex(checker.TopologyError, 'ambiguous.*C2863402'):
            self.read()

    def test_incomplete_identity_authority_fails(self):
        self.authority('amplifier', '', 'C2863402', 'Pkg:SOIC8')
        with self.assertRaisesRegex(checker.TopologyError, 'incomplete.*identity'):
            self.read()

    def test_duplicate_native_component_fails_instead_of_last_wins(self):
        extra = '(comp (ref "U_AFE1") (value "C2863402") (footprint "Pkg:SOIC8"))'
        with self.assertRaisesRegex(checker.TopologyError, 'duplicate.*U_AFE1'):
            self.read(extra=extra)

    def test_passive_display_is_normalized_but_never_replaced_from_dossier(self):
        self.authority('resistor', 'RESISTOR_MPN', 'C123', 'Pkg:R', value='300')
        for displayed, normalized in (('300Ω', '300'), ('301Ω', '301'),
                                      ('1k ohm', '1k'), ('15nF', '15nF')):
            extra = f'(comp (ref "R_X1P") (value "{displayed}") (footprint "Pkg:R"))'
            _, values = self.read(extra=extra)
            self.assertEqual(normalized, values['R_X1P'])
        pins, values = valid_fixture()
        values['R_X1P'] = self.read(extra=
            '(comp (ref "R_X1P") (value "301Ω") (footprint "Pkg:R"))')[1]['R_X1P']
        with self.assertRaisesRegex(checker.TopologyError, 'R_X1P value'):
            checker.validate(pins, values)


if __name__ == "__main__":
    unittest.main()
