from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import substitute_quote as s


CHANGE = dict(old_mpn='OLD', old_manufacturer='Maker', mpn='NEW', manufacturer='Maker2',
              code='C123', refs={'carrier': ['U1']}, values={'OLD': 'NEW'},
              footprint='SO:30', installed_need=2, engineering='PASS', review='review.md')
SOURCE = '''(kicad_pcb (footprint "SO:30" (at 10 20)
 (property "Reference" "U1") (property "Value" "OLD")
 (property "Manufacturer" "Maker") (property "MPN" "OLD")
 (pad "1" smd rect (at 2 3) (net 1 "/A")))
 (segment (start 1 2) (end 3 4) (net 1)))'''


class SubstitutionTests(unittest.TestCase):
    def test_only_property_strings_change(self):
        out, refs = s.rewrite(SOURCE, 'carrier', [CHANGE])
        self.assertEqual(refs, ['U1'])
        expected = SOURCE.replace('"Value" "OLD"', '"Value" "NEW"').replace(
            '"Manufacturer" "Maker"', '"Manufacturer" "Maker2"').replace('"MPN" "OLD"', '"MPN" "NEW"')
        self.assertEqual(out, expected)

    def test_same_mpn_other_maker_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Maker mismatch'):
            s.rewrite(SOURCE.replace('"Maker"', '"Impostor"'), 'carrier', [CHANGE])

    def test_unexpected_reference_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unexpected changed component'):
            s.rewrite(SOURCE.replace('"U1"', '"U2"'), 'carrier', [CHANGE])

    def test_unrelated_part_unchanged(self):
        other = SOURCE.replace('"OLD"', '"OTHER"')
        self.assertEqual(s.rewrite(other, 'carrier', [CHANGE]), (other, []))

    def test_library_and_instance_fields(self):
        text = '''(kicad_sch (lib_symbols (symbol "Lib:U1"
        (property "Reference" "U") (property "Value" "OLD")
        (property "MPN" "OLD") (property "Manufacturer" "Maker")
        (symbol "U1_1_1" (pin input line (at 1 2 0)))))
        (symbol (lib_id "Lib:U1") (property "Reference" "U1")
        (property "Value" "OLD") (property "MPN" "OLD")
        (property "Manufacturer" "Maker")))'''
        out, refs = s.rewrite(text, 'carrier', [CHANGE])
        self.assertEqual(refs, ['U1', 'U1'])
        self.assertNotIn('"MPN" "OLD"', out)
        self.assertIn('(pin input line (at 1 2 0))', out)

    def test_escaped_quotes_do_not_break_parser(self):
        src = SOURCE.replace('(at 10 20)', '(at 10 20) (descr "keep \\"quoted\\" (text)")')
        out, _ = s.rewrite(src, 'carrier', [CHANGE])
        self.assertIn('(descr "keep \\"quoted\\" (text)")', out)

    def test_missing_closing_paren_rejected(self):
        with self.assertRaises(ValueError):
            s.rewrite(SOURCE[:-1], 'carrier', [CHANGE])

    def test_bom_cpl_geometry_field_not_changed(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(s, 'BASE', Path(tmp)):
            base = Path(tmp)
            row = {'MPN': 'OLD', 'Manufacturer': 'Maker', 'Designator': 'U1',
                   'Footprint': 'SO:30', 'Quantity': '1', 'Comment': 'OLD',
                   'JLCPCB Part #': '', 'Supply route': 'old', 'Assembly route': 'JLC_SMT_requested'}
            (base / 'carrier-bom.csv').write_bytes(s.csv_bytes([row]))
            (base / 'pod-bom.csv').write_bytes(s.csv_bytes([{**row, 'MPN': 'OTHER'}]))
            scope = [{'board': 'carrier', 'reference': 'U1', 'manufacturer': 'Maker', 'mpn': 'OLD', 'installed_batch': '2'}]
            (base / 'scope.csv').write_bytes(s.csv_bytes(scope))
            procurement = [{'manufacturer': 'Maker', 'mpn': 'OLD', 'catalog_locator': '',
                            'external_lead': '', 'proposed_route': '', 'evidence_status': '', 'installed_2c8p': '2'}]
            (base / 'procurement-plan.csv').write_bytes(s.csv_bytes(procurement))
            out = s.generated_tables({'assembled': {'carrier': 2, 'pod': 8}, 'replacements': [CHANGE]})
            self.assertIn(b'NEW,Maker2,U1,SO:30,1,NEW,C123', out['carrier-bom.csv'])
            self.assertEqual(out['pod-bom.csv'], (base / 'pod-bom.csv').read_bytes())
            self.assertEqual(set(out), {'carrier-bom.csv', 'pod-bom.csv', 'scope.csv', 'procurement-plan.csv'})
            retained = s.generated_tables({'assembled': {'carrier': 2, 'pod': 8}, 'replacements': [CHANGE],
                'retained_sources': [{'mpn': 'OTHER', 'manufacturer': 'Maker', 'url': 'https://supplier.example/exact'}]})
            self.assertIn(b'OTHER,Maker,U1,SO:30,1,OLD,,JLC_Global_Sourcing_or_consignment_candidate', retained['pod-bom.csv'])
            row['Footprint'] = 'wrong'
            (base / 'carrier-bom.csv').write_bytes(s.csv_bytes([row]))
            with self.assertRaisesRegex(ValueError, 'footprint mismatch'):
                s.generated_tables({'assembled': {'carrier': 2, 'pod': 8}, 'replacements': [CHANGE]})

    def test_real_package_replay_and_tamper(self):
        spec = s.ROOT / 'substitutions-20261101/adopted-changes.json'
        if not spec.exists():
            self.skipTest('Current substitution fixture not available')
        external = ('evidence/pcm1864.pdf', 'evidence/capacitor-primary-research.tar.gz')
        if not all((spec.parent / name).is_file() for name in external):
            self.skipTest('Full replay requires retained external manufacturer research; use public payload verifier')
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'candidate'
            manifest = s.build(spec, output)
            self.assertFalse(manifest['production_ready'])
            self.assertFalse(manifest['purchase_authorized'])
            self.assertEqual(s.verify(spec, output)['result'], 'PASS')
            with self.assertRaisesRegex(ValueError, 'existing output'):
                s.build(spec, output)
            bom = output / 'carrier-bom.csv'
            bom.write_text(bom.read_text().replace('PCM1864DBTR', 'PCM1865DBTR'))
            with self.assertRaisesRegex(ValueError, 'deterministic replay'):
                s.verify(spec, output)


if __name__ == '__main__':
    unittest.main()
