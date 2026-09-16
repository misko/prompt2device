"""Independent source checks for the complete CS5308P analog-input escape.

The source owns each U_ADC-to-common-mode-capacitor bundle and reachable
ADC2N and ADC6N B.Cu landings. The ordinary router still owns the long isolator paths.
These tests grade native shapes and connectivity, not a routed board.
"""
import copy
import math
import subprocess
import unittest
from collections import Counter
from pathlib import Path

import yaml

from test_adc_source import load_source, native_geometry
from test_digital_launch_source import primitive, rect_shape, segment_rows
from test_regulator_source import via_rows

PROJECT = Path(__file__).resolve().parents[2]
REPO = PROJECT.parents[1]
BASE = '28571836bd194c6444240f0d12b7beccae8c2542'
PIN_NUMBERS = [13, 14, 15, 16, 19, 20, 21, 22, 39, 40, 41, 42, 45, 46, 47, 48]
INPUTS = {f'U_ADC.{number}' for number in PIN_NUMBERS}
ADC_NETS = {f'ADC{channel}{polarity}' for channel in range(1, 9) for polarity in 'PN'}
NORTH = {f'ADC{channel}{polarity}' for channel in range(1, 5) for polarity in 'PN'}
LANDING = [93.0, 64.0]


def frozen(name, revision=BASE):
    return yaml.safe_load(subprocess.check_output(
        ['git', 'show', revision + ':projects/crow-audio-carrier-v1/03_src/' + name],
        cwd=REPO, timeout=15))


def bundle_rows(route):
    return [row for row in segment_rows(route) if row['id'] in INPUTS]


def bundle_vias(route):
    return [row for row in via_rows(route) if row['pin'] in INPUTS]


def inspect_bundle(floor, route, nets, geometry):
    rows = bundle_rows(route)
    vias = bundle_vias(route)
    pads = {pad['id']: pad for pad in geometry['pads']}
    areas = {area['name']: area for area in floor['keepouts']}
    failures = []
    checks = Counter()
    owners = {stub['pin']: stub for stub in route['prep']['seed_stubs']['stubs']
              if stub['pin'] in INPUTS}
    if set(owners) != INPUTS or set(row['net'] for row in owners.values()) != ADC_NETS:
        failures.append(('coverage',))

    def fail(kind, *detail):
        failures.append((kind,) + detail)

    def collide(a, b, clearance, kind):
        checks[kind] += 1
        if a['shape'].Collide(b['shape'], max(0, round(clearance * 1e6) - 2)):
            fail(kind, a['id'], b['id'])

    for row in rows:
        expected = pads[row['id']]['net']
        landing = row['width'] == .20  # ordinary analog width needs no thin-copper exception
        if row['net'] != expected or (row['width'] != .15 and not landing) or row['layer'] not in {'F.Cu', 'B.Cu'}:
            fail('identity-width-layer', row['id'])
        if not landing:
            zone = areas['ADC_ANALOG_ESCAPE_NORTH' if row['net'] in NORTH
                         else 'ADC_ANALOG_ESCAPE_SOUTH']
            x0, y0, x1, y1 = zone['rect']
            radius = row['width'] / 2
            if not all(x0 + radius <= x <= x1 - radius and y0 + radius <= y <= y1 - radius
                       for x, y in (row['a'], row['b'])):
                fail('extent', row['id'], row['a'], row['b'])
        if row['layer'] == 'F.Cu':
            for pad in geometry['pads']:
                if pad['net'] != row['net']:
                    collide(row, pad, .127, 'segment-pad')
        for area in floor['keepouts']:
            if row['layer'] in area['layers'] and 'tracks' in area['deny']:
                collide(row, {'id': area['name'], 'shape': rect_shape(area['rect'])},
                        0, 'segment-keepout')

    for index, row in enumerate(rows):
        for other in rows[index + 1:]:
            if row['layer'] == other['layer'] and row['net'] != other['net']:
                collide(row, other, .127, 'segment-segment')

    for via in vias:
        landing = via['pin'] == 'U_ADC.22'
        if (via['size'],via['drill']) != ((.5,.2) if landing else (.3,.2)):
            fail('via-size', via['id'])
        if not landing:
            zone = areas['ADC_ANALOG_ESCAPE_NORTH' if via['net'] in NORTH
                         else 'ADC_ANALOG_ESCAPE_SOUTH']
            x0, y0, x1, y1 = zone['rect']
            radius = via['size'] / 2
            if not (x0 + radius <= via['at'][0] <= x1 - radius and
                    y0 + radius <= via['at'][1] <= y1 - radius):
                fail('via-extent', via['id'])
        for pad in geometry['pads']:
            if pad['net'] != via['net']:
                collide(via, pad, .127, 'via-pad')
                collide({'id': via['id'], 'shape': via['hole']}, pad, .20,
                        'hole-pad')
            # The annulus may legally touch its own same-net launch. Via-in-pad
            # means the drill centre lies on a component land.
            if primitive(via['at'], via['at'], 0).Collide(pad['shape'], 0):
                fail('via-in-pad', via['id'], pad['id'])
        for row in rows:
            if row['net'] != via['net']:
                collide({'id': via['id'], 'shape': via['hole']}, row, .20,
                        'hole-segment')
        for other in vias:
            if via['id'] < other['id'] and via['net'] != other['net']:
                collide(via, other, .127, 'via-via')
                collide({'id': via['id'], 'shape': via['hole']}, other, .20,
                        'hole-via')
                collide(via, {'id': other['id'], 'shape': other['hole']}, .20,
                        'via-hole')
                collide({'id': via['id'], 'shape': via['hole']},
                        {'id': other['id'], 'shape': other['hole']}, .50, 'hole-hole')

    for pin, stub in owners.items():
        net = stub['net']
        nodes = []
        for pad in geometry['pads']:
            if pad['net'] == net:
                nodes.append({'id': pad['id'], 'shape': pad['shape'], 'layers': {'F.Cu'}})
        for index, row in enumerate(rows):
            if row['net'] == net:
                nodes.append({'id': f'segment:{index}', 'shape': row['shape'],
                              'layers': {row['layer']}})
        for via in vias:
            if via['net'] == net:
                nodes.append({'id': via['id'], 'shape': via['shape'],
                              'layers': {'F.Cu', 'B.Cu'}})
        reached = {i for i, node in enumerate(nodes) if node['id'] == pin}
        todo = list(reached)
        while todo:
            i = todo.pop()
            for j, node in enumerate(nodes):
                if (j not in reached and nodes[i]['layers'] & node['layers'] and
                        nodes[i]['shape'].Collide(node['shape'], 0)):
                    reached.add(j)
                    todo.append(j)
        reached_ids = {nodes[i]['id'] for i in reached}
        channel = int(net[3])
        required = {pin, f'C_ADC_CM{channel}{net[-1]}.1'}
        if not required <= reached_ids:
            fail('bundle-reach', pin, tuple(sorted(required - reached_ids)))
        if any(item.startswith('U_ISO') or item.startswith('R_ADC_PD')
               for item in reached_ids):
            fail('overowned-long-route', pin)

    adc2n = owners['U_ADC.45']
    landing_hits = [row for row in rows if row['net'] == 'ADC2N' and row['layer'] == 'B.Cu'
                    and (math.dist(row['a'], LANDING) < 1e-9 or
                         math.dist(row['b'], LANDING) < 1e-9)]
    if len(landing_hits) != 1 or adc2n.get('via') != {'size': .3, 'drill': .2}:
        fail('router-landing', 'ADC2N')
    return {'rows': len(rows), 'vias': len(vias), 'checks': checks, 'failures': failures}


def filter_resistance_model(route):
    """ADR0015 nominal 35um copper / rho85 model; no temperature-rise claim."""
    result = {}
    for net in ['FILT1P', 'FILT2P']:
        rows = [row for row in segment_rows(route) if row['net'] == net]
        resistance = sum(2.1643958e-8 * math.dist(row['a'], row['b']) /
                         (row['width'] * 35e-6) for row in rows)
        result[net] = {'length_mm': sum(math.dist(row['a'], row['b']) for row in rows),
                       'segments': len(rows),
                       'resistance_ohm_at85C_nominal_copper': resistance,
                       'conditional_loss_w_at2_5A': resistance * 2.5 ** 2}
    return result


class AdcAnalogFanoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, cls.nets, *_ = load_source()
        cls.geometry = native_geometry(cls.floor)

    def test_all_sixteen_input_caps_meet_pad_center_keep_short(self):
        # Native P-ADJ carrier938 rejected CM8N at 5.25mm even though its
        # copper-edge adjacency passed. These are distinct physical metrics.
        pads = self.geometry['pads']
        spans = {}
        for pin in INPUTS:
            adc = next(p for p in pads if p['id'] == pin)
            cap = next(p for p in pads if p['id'].startswith('C_ADC_CM')
                       and p['id'].endswith('.1') and p['net'] == adc['net'])
            spans[adc['net']] = math.dist(adc['at'], cap['at'])
        self.assertEqual(set(spans), ADC_NETS)
        for net, span in spans.items():
            self.assertLessEqual(span, 5.0, (net, span))
        adc8n = next(p for p in pads if p['id'] == 'U_ADC.21')
        self.assertGreater(math.dist(adc8n['at'], [100.65, 76.72]), 5.0)

    def test_complete_sixteen_net_bundle_clears_native_geometry(self):
        result = inspect_bundle(self.floor, self.route, self.nets, self.geometry)
        self.assertEqual(result['failures'], [])
        self.assertGreater(sum(result['checks'].values()), 100000)

    def test_missing_link_wrong_width_and_via_in_pad_fail(self):
        bad = copy.deepcopy(self.route)
        row = next(row for row in bad['prep']['seed_stubs']['stubs']
                   if row['pin'] == 'U_ADC.45')
        row['segments'] = row['segments'][:-1]
        self.assertIn('router-landing', {f[0] for f in inspect_bundle(
            self.floor, bad, self.nets, self.geometry)['failures']})

        bad = copy.deepcopy(self.route)
        row = next(row for row in bad['prep']['seed_stubs']['stubs']
                   if row['pin'] == 'U_ADC.48')
        row['segments'][0]['width'] = .14
        self.assertIn('identity-width-layer', {f[0] for f in inspect_bundle(
            self.floor, bad, self.nets, self.geometry)['failures']})

        bad = copy.deepcopy(self.route)
        row = next(row for row in bad['prep']['seed_stubs']['stubs']
                   if row['pin'] == 'U_ADC.46')
        row['vias'][0] = list(next(pad for pad in self.geometry['pads']
                                   if pad['id'] == 'U_ADC.46')['at'])
        self.assertIn('via-in-pad', {f[0] for f in inspect_bundle(
            self.floor, bad, self.nets, self.geometry)['failures']})

    def test_bundle_is_partial_source_ownership_with_reachable_adc2n_landing(self):
        groups = self.route['prep']['waves']['groups']
        excluded = set(self.route['prep']['waves']['exclude'])
        owners = {row['pin']: row for row in self.route['prep']['seed_stubs']['stubs']
                  if row['pin'] in INPUTS}
        for row in owners.values():
            self.assertIn(row['net'], groups['adc'])
            self.assertNotIn(row['net'], excluded)
        self.assertEqual(owners['U_ADC.45']['vias'], [[94.1, 64.975]])
        self.assertEqual(owners['U_ADC.15']['vias'], [[94.65, 75.125]])
        self.assertEqual(set(owners),INPUTS)
        self.assertEqual({row['net'] for row in owners.values()},ADC_NETS)

    def test_old_one_millimetre_stubs_do_not_satisfy_bundle_contract(self):
        bad = copy.deepcopy(self.route)
        for row in bad['prep']['seed_stubs']['stubs']:
            if row['pin'] in INPUTS:
                row['segments'] = row['segments'][:1]
                row.pop('vias', None)
        failures = inspect_bundle(self.floor, bad, self.nets, self.geometry)['failures']
        self.assertIn('bundle-reach', {failure[0] for failure in failures})

    def test_filter_width_lengths_and_conditional_current_are_explicit(self):
        model = filter_resistance_model(self.route)
        old = filter_resistance_model(frozen('route.yaml'))
        for net, row in model.items():
            self.assertEqual(row['segments'], 5)
            self.assertAlmostEqual(row['length_mm'], 8.050464884544218, places=8)
            self.assertGreater(row['resistance_ohm_at85C_nominal_copper'],
                               old[net]['resistance_ohm_at85C_nominal_copper'])
            self.assertAlmostEqual(row['conditional_loss_w_at2_5A'],
                                   row['resistance_ohm_at85C_nominal_copper'] * 6.25)
        self.assertEqual(model['FILT1P'], model['FILT2P'])


if __name__ == '__main__':
    unittest.main()
