"""ADR0027 source association, independently checked through native pad poses.

No BOARD or route is emitted. Monotone endpoint order and unchanged physical
population do not prove routed matching, clearance, or reference continuity.
"""
import copy
from collections import Counter
from fnmatch import fnmatchcase
import json
import os
import shutil
from pathlib import Path
import re
import subprocess
import unittest
import yaml
from test_digital_launch_source import native_geometry, load_source
from test_local_placement_source import source_builder
from source_inventory import inventory
import check_analog_paths as checker

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parents[1]
BASE = 'f2675b43'


def inversions(values):
    return sum(a > b for i, a in enumerate(values) for b in values[i+1:])


class ChannelMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, cls.nets, *_ = load_source()
        cls.geometry = native_geometry(cls.floor)
        cls.before = yaml.safe_load(subprocess.check_output(
            ['git', 'show', BASE+':projects/crow-audio-carrier-v1/03_src/floorplan.yaml'],
            cwd=REPO, timeout=15))

    def test_native_north_and_south_endpoints_are_monotone_for_both_legs(self):
        for channels in (range(1, 5), range(5, 9)):
            for leg, iso_pin in [('P', '2'), ('N', '6')]:
                targets = {f'ADC{n}{leg}' for n in channels}
                source = sorted((p['at'][0], p['net']) for p in self.geometry['pads']
                                if p['id'].startswith('U_ISO') and p['id'].endswith('.'+iso_pin)
                                and p['net'] in targets)
                dest = sorted((p['at'][0], p['net']) for p in self.geometry['pads']
                              if p['id'].startswith('U_ADC.') and p['net'] in targets)
                self.assertEqual(len(source), 4)
                self.assertEqual(len(dest), 4)
                ranks = {net: i for i, (_, net) in enumerate(source)}
                self.assertEqual(inversions([ranks[net] for _, net in dest]), 0)
        # Reconstruct the former association on the same native pad poses.
        # The very same spatial-order predicate must reject that input.
        bad = copy.deepcopy([{k:v for k,v in p.items() if k != 'shape'}
                             for p in self.geometry['pads']])
        for p in bad:
            if p['id'].startswith('U_ADC.') and re.fullmatch(r'ADC[1-4][PN]', p['net']):
                p['net'] = 'ADC'+str(5-int(p['net'][3]))+p['net'][4]
        for leg, iso_pin in [('P','2'),('N','6')]:
            targets = {f'ADC{n}{leg}' for n in range(1,5)}
            source = sorted((p['at'][0],p['net']) for p in bad
                            if p['id'].startswith('U_ISO') and p['id'].endswith('.'+iso_pin)
                            and p['net'] in targets)
            dest = sorted((p['at'][0],p['net']) for p in bad
                          if p['id'].startswith('U_ADC.') and p['net'] in targets)
            self.assertEqual((len(source),len(dest)), (4,4))
            ranks = {net:i for i,(_,net) in enumerate(source)}
            self.assertEqual(inversions([ranks[net] for _,net in dest]),6)

    def test_physical_population_and_every_unexchanged_pose_remain_exact(self):
        old = source_builder(self.before)
        new = source_builder(self.floor)
        refs = set(inventory()[0])
        moved = {f'C_ADC_CM{n}{leg}' for n in range(1, 5) for leg in 'PN'}
        self.assertEqual(len(refs), 333)
        self.assertEqual(Counter(old.initial_pose(r)[:3] for r in moved),
                         Counter(new.initial_pose(r)[:3] for r in moved))
        # ADR0027 owns the CM1..4 reference exchange and its fixed ADC anchor.
        # Later ADR0030 clamp/power/silk poses are checked by the complete
        # local-placement/entry/source-native gates, not frozen to f2675b43.
        self.assertEqual(old.initial_pose('U_ADC'), new.initial_pose('U_ADC'))
        self.assertEqual(set(old.place_cfg['anchors']), set(new.place_cfg['anchors']))
        comp = inventory()[0]
        self.assertEqual(len({comp[r] for r in moved}), 1)
        self.assertFalse(any('ADC_CM' in r for bank in self.floor['placement']['repeat'] for r in bank['members']))

    def test_pad_overrides_follow_physical_lands_through_ref_exchange(self):
        # RED on the original ADR0027 source: the CM3 solid GND exception
        # stayed on the logical name, starving the two physical CM2 lands.
        # Compare all declared pad settings by physical pose, independently
        # of the generator's patterns_for/SetLocalZoneConnection consumer.
        def physical_overrides(floor):
            builder = source_builder(floor)
            result = Counter()
            # Scope this association test to the eight exchanged CM lands.
            # test_ground_connections owns the exact full-board override census.
            for ref in {f'C_ADC_CM{n}{leg}' for n in range(1, 5) for leg in 'PN'}:
                for pattern in floor['placement']['patterns']:
                    matches = pattern['match']
                    if isinstance(matches, str):
                        matches = [matches]
                    if any(fnmatchcase(ref, match) for match in matches):
                        for override in pattern.get('pad_overrides', []):
                            # Thermal angles have a separate exact census.
                            if 'zone_connection' not in override: continue
                            result[(tuple(builder.initial_pose(ref)[:3]),
                                    json.dumps(override, sort_keys=True))] += 1
            return result

        before = physical_overrides(self.before)
        scoped = copy.deepcopy(self.floor)
        for pattern in scoped['placement']['patterns']:
            if isinstance(pattern['match'], list):
                pattern['match'] = [r for r in pattern['match'] if r not in {'C_ADC_CM4P','C_ADC_CM4N'}]
        current = physical_overrides(scoped)
        self.assertGreater(sum(before.values()), 0)
        self.assertEqual(current, before)
        # Reject the original missed migration even after the source is fixed.
        bad = copy.deepcopy(scoped)
        for pattern in bad['placement']['patterns']:
            if pattern.get('pad_overrides') and isinstance(pattern['match'], list):
                pattern['match'] = [re.sub(r'^C_ADC_CM2([PN])$', r'C_ADC_CM3\1', ref)
                                    for ref in pattern['match']]
        self.assertNotEqual(physical_overrides(bad), before)

    def test_actual_pin_association_and_capture_slot_table_agree(self):
        # Manufacturer physical identity is fixed independently of map parsing.
        physical = [(40,39),(42,41),(46,45),(48,47),(14,13),(16,15),(20,19),(22,21)]
        pins = self.geometry['pins']
        observed = []
        for p,n in physical:
            pn = pins['U_ADC',str(p)]
            nn = pins['U_ADC',str(n)]
            self.assertRegex(pn, r'^ADC[1-8]P$')
            pod = int(re.fullmatch(r'ADC([1-8])P', pn)[1])
            self.assertEqual(nn, f'ADC{pod}N')
            observed.append(pod)
        result = checker.validate_source(self.nets['length_match'], self.route, pins)
        self.assertEqual(observed, result['slot_to_pod'])
        self.assertEqual(set(observed), set(range(1,9)))
        self.assertEqual(observed[4:], [5,6,7,8])
        self.assertEqual(result['paths'], 144)
        self.assertEqual(result['endpoints'], 192)

    def test_malformed_duplicate_and_cross_domain_maps_are_rejected(self):
        good = checker.CHANNEL_MAP
        bads = [dict(good, extra=True), dict(good, schema=True), dict(good, id=''),
                dict(good, pod_to_adc=[]), dict(good, pod_to_adc=[4,3,2,2,5,6,7,8]),
                dict(good, pod_to_adc=[4,3,2,5,1,6,7,8]),
                dict(good, pod_to_adc=[4,3,2,1,6,5,7,8]),
                dict(good, pod_to_adc=[4,3,2,True,5,6,7,8])]
        self.assertEqual(len(bads), 8)
        for bad in bads:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                checker.validate_channel_map(bad)
        # Incorrect physical membership must fail even if the declared table
        # still looks complete and every logical net is named in the source.
        badpins = dict(self.geometry['pins'])
        badpins['U_ADC','48'],badpins['U_ADC','40'] = badpins['U_ADC','40'],badpins['U_ADC','48']
        with self.assertRaises(checker.PathError):
            checker.validate_source(self.nets['length_match'], self.route, badpins)

    def test_producer_header_rejects_unknown_missing_and_malformed_identity(self):
        source = Path(os.environ.get('CARRIER_PRODUCER_SOURCE', str(
            PROJECT/'03_tscircuit/src/crow_audio_carrier_v1.tsx'))).read_text()
        good = checker.CHANNEL_MAP
        missing = dict(good); missing.pop('id')
        bads = [dict(good, extra=True), missing, dict(good, id='  '),
                dict(good, pod_to_adc=None), dict(good, schema=True),
                dict(good, pod_to_adc=[4,3,2,1,6,5,7,8])]
        script = r"""
const input = JSON.parse(await Bun.stdin.text());
const end = input.source.indexOf('const N =');
if (end < 0) throw new Error('missing actual producer header boundary');
const prefix = input.source.slice(0,end).replace(/^import \{[^\n]+from "\.\/schematic_presentation"\s*$/m,'');
const results = input.cases.map(value => {
  const code = prefix.replace(/^import channelMap from "[^"\n]+"\s*$/m,
    'const channelMap = '+JSON.stringify(value));
  try { eval(new Bun.Transpiler({loader:'tsx'}).transformSync(code)); return true; }
  catch { return false; }
});
console.log(JSON.stringify(results));
"""
        run = subprocess.run([shutil.which('bun'), '--eval', script],
                             input=json.dumps({'source':source,'cases':[good,*bads]}),
                             text=True, capture_output=True, timeout=30)
        self.assertEqual(run.returncode,0,run.stderr)
        self.assertEqual(json.loads(run.stdout),[True]+[False]*len(bads))

    def test_capture_obligations_and_actual_source_digest_cannot_drift(self):
        import hashlib
        data = checker.CHANNEL_MAP
        for kind in ('missing', 'count', 'reject'):
            bad = copy.deepcopy(data)
            if kind == 'missing': bad['capture_requirements']['record_fields'].pop()
            elif kind == 'count': bad['capture_requirements']['impulse_channel_count']=7
            else: bad['capture_requirements']['reject'].remove('unstable')
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                checker.validate_channel_map(bad)
        with self.assertRaisesRegex(ValueError,'duplicate'):
            json.loads('{"schema":1,"schema":2}',object_pairs_hook=checker._unique_json_object)
        result = checker.validate_source(self.nets['length_match'],self.route,self.geometry['pins'])
        raw = (PROJECT/'03_src/adc_channel_map.json').read_bytes()
        self.assertEqual(result['channel_map_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertEqual(result['channel_map_id'],json.loads(raw)['id'])
        self.assertEqual(result['capture_requirements']['impulse_channel_count'],8)
        self.assertEqual(result['capture_identity_status'],'OWED')


if __name__ == '__main__':
    unittest.main()
