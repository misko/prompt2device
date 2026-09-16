"""ADR0025 physical-source screen, not generated-board or route acceptance.

Use independent native library shapes for the changed cell and every foreign
instance. No BOARD is created or saved. The electrical checker owns population;
this screen cannot qualify stability, thermal resistance or a ground return.
"""
import copy
import math
import unittest
from collections import Counter

import pcbnew
import yaml

from test_digital_launch_source import load_source, native_geometry, segment_rows
from test_regulator_source import via_rows
from test_thermal_source import thermal_rows
from placement_gates import _poly_gap_mm

FILTERS = {f'C_FILTER{n}{leg}{i}' for n in range(1, 9)
           for leg in 'PN' for i in (1, 2)}
MOVED = {'D_IN', 'C_HOLD1', 'C_HOLD2', 'R_PWR_PU', 'R_TDM_PD', 'C_LDO_IN'}
REGULATOR = {'U_LDO', 'R_LDO_SET', 'C_LDO_IN', 'C_LDO_OUT',
             'C_OPA_BULK', 'C_LDO_NR4', 'C_LDO_NR5'}
INPUTS = {f'R_IN{n}{leg}' for n in range(1, 9) for leg in 'PN'}
TARGETS = FILTERS | MOVED | REGULATOR | INPUTS


def inspect(floor, route, geometry=None):
    geometry = geometry or native_geometry(floor)
    refs = sorted({ref for ref, _ in geometry['pins']})
    assert len(refs) == len(geometry['footprints']) and TARGETS <= set(refs)
    fps = dict(zip(refs, geometry['footprints']))
    rows = segment_rows(route)
    vias = via_rows(route) + thermal_rows(floor, geometry)
    failures = []
    checks = Counter()
    for ref in sorted(TARGETS):
        fp = fps[ref]
        body = fp.GetCourtyard(pcbnew.F_CrtYd)
        assert body.OutlineCount(), ref
        outline = floor['board']['outline']
        bounds = body.BBox()
        checks['body-outline'] += 1
        if not (bounds.GetLeft()/1e6 >= outline['x0']+.1 and
                bounds.GetRight()/1e6 <= outline['x1']-.1 and
                bounds.GetTop()/1e6 >= outline['y0']+.1 and
                bounds.GetBottom()/1e6 <= outline['y1']-.1):
            failures.append(('body-outline', ref))
        own = [p for p in geometry['pads'] if p['id'].rsplit('.', 1)[0] == ref]
        for other, foreign in fps.items():
            if ref == other:
                continue
            envelope = foreign.GetCourtyard(pcbnew.F_CrtYd)
            assert envelope.OutlineCount(), other
            checks['courtyard'] += 1
            if _poly_gap_mm(body, envelope, .1) < .1-1e-6:
                failures.append(('courtyard', ref, other))
            for p in foreign.Pads():
                if not p.IsOnCopperLayer() or not p.IsOnLayer(pcbnew.F_Cu):
                    continue
                checks['body-pad'] += 1
                if body.Collide(p.GetEffectiveShape(pcbnew.F_Cu), 99998):
                    failures.append(('body-pad', ref, other+'.'+p.GetNumber()))
            for p in own:
                checks['pad-body'] += 1
                if envelope.Collide(p['shape'], 99998):
                    failures.append(('pad-body', p['id'], other))
        for p in own:
            for q in geometry['pads']:
                if q['id'].rsplit('.', 1)[0] == ref:
                    continue
                # Independent parts must not touch even on the same net.
                checks['pad-pad'] += 1
                if p['shape'].Collide(q['shape'], 126998):
                    failures.append(('pad-pad', p['id'], q['id']))
            for row in rows:
                if row['layer'] != 'F.Cu' or row['net'] == p['net']:
                    continue
                checks['pad-seed'] += 1
                if p['shape'].Collide(row['shape'], 249998):
                    failures.append(('pad-seed', p['id'], row['id']))
            for hole in geometry['holes']:
                if hole['id'] == p['id']:
                    continue
                checks['pad-hole'] += 1
                if p['shape'].Collide(hole['shape'], 254998):
                    failures.append(('pad-hole', p['id'], hole['id']))
            for via in vias:
                if via['net'] != p['net']:
                    checks['pad-via'] += 1
                    if p['shape'].Collide(via['shape'], 249998):
                        failures.append(('pad-via', p['id'], via['id']))
                checks['pad-via-drill'] += 1
                # Only the named thermal host is intentionally drilled. The
                # independent thermal suite grades exact containment/process.
                if via.get('pin') != p['id'] and p['shape'].Collide(via['hole'], 254998):
                    failures.append(('pad-via-drill', p['id'], via['id']))
    return failures, dict(checks)


class SharedRailPlacementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.floor, cls.route, cls.nets, *_ = load_source()
        cls.geometry = native_geometry(cls.floor)

    def test_all_changed_instances_clear_every_foreign_instance(self):
        failures, checks = inspect(self.floor, self.route, self.geometry)
        self.assertEqual(len(TARGETS), 60)
        self.assertEqual(checks['courtyard'], 60*332)
        self.assertGreater(checks['pad-pad'], 90000)
        self.assertEqual(failures, [])

    def test_all_current_adjacencies_have_exact_native_copper_within_budget(self):
        # Independent shapes, same conservative rotation-aware pad-box metric
        # as P-ADJ-PAIR. The owning saved-board policy audit must run again.
        from test_digital_launch_source import PROJECT
        pads = self.geometry['pads']
        def gap(a, b):
            a, b = a['shape'].BBox(), b['shape'].BBox()
            return math.hypot(max(0, a.GetLeft()-b.GetRight(), b.GetLeft()-a.GetRight()),
                              max(0, a.GetTop()-b.GetBottom(), b.GetTop()-a.GetBottom()))/1e6
        count = 0
        for path in (PROJECT/'02_parts').glob('*/part.yaml'):
            for row in yaml.safe_load(path.read_text()).get('layout', {}).get('adjacency', []):
                a, b = row['refdes']
                for net in row['nets']:
                    pairs = [(p, q) for p in pads if p['id'].rsplit('.', 1)[0] == a and p['net'] == net
                             for q in pads if q['id'].rsplit('.', 1)[0] == b and q['net'] == net]
                    self.assertTrue(pairs, (path, row))
                    self.assertLessEqual(min(gap(p, q) for p, q in pairs), row['max_mm']+1e-6, row)
                count += 1
        self.assertEqual(count, 353)

    def test_new_regulator_binds_every_exact_local_partner_within_five_mm(self):
        from test_digital_launch_source import PROJECT
        part = yaml.safe_load((PROJECT/'02_parts/LT3041ADE-TRPBF/part.yaml').read_text())
        pads = {p['id']: p for p in self.geometry['pads']}
        rules = part['layout']['keep_short']
        self.assertEqual({tuple(r['partner_refs']) for r in rules},
                         {(r,) for r in REGULATOR-{'U_LDO'}})
        for row in rules:
            self.assertEqual(row['max_span_mm'], 5)
            for pin in row['anchor_pins']:
                anchor = pads['U_LDO.'+pin]
                self.assertEqual(anchor['net'], row['net'])
                partners = [p for p in pads.values() if p['id'].rsplit('.', 1)[0] in row['partner_refs'] and p['net'] == row['net']]
                self.assertTrue(partners)
                self.assertLessEqual(min(math.dist(anchor['at'], p['at']) for p in partners), 5)

    def test_each_shunt_has_local_signal_owner_and_mirrored_placement(self):
        pads = {p['id']: p for p in self.geometry['pads']}
        north, south = self.floor['placement']['repeat']
        for n in range(1, 9):
            for leg in 'PN':
                for i in (1, 2):
                    ref = f'C_FILTER{n}{leg}{i}'
                    self.assertEqual(pads[ref+'.1']['net'], f'FILTER{n}{leg}')
                    self.assertEqual(pads[ref+'.2']['net'], 'GND')
                    # Engineering placement allocation, not a vendor trace limit.
                    for owner in (f'R_X{n}{leg}.2', f'R_OUT{n}{leg}.2'):
                        self.assertEqual(pads[owner]['net'], f'FILTER{n}{leg}')
                        self.assertLessEqual(math.dist(pads[ref+'.1']['at'], pads[owner]['at']), 9)
        for name in north['members']:
            self.assertEqual(south['members'][name]['at'], [-x for x in north['members'][name]['at']])
            self.assertEqual(south['members'][name]['rot'], (north['members'][name]['rot']+180) % 360)

    def test_provisional_central_filter_cell_is_rejected(self):
        bad = copy.deepcopy(self.floor)
        for bank, sign, rot in zip(bad['placement']['repeat'], (1, -1), (0, 180)):
            for leg, y in [('P', 4.1), ('N', 6.5)]:
                for i, x in [(1, -1.3), (2, 1.3)]:
                    bank['members'][f'C_FILTER{{i}}{leg}{i}'] = {'at': [sign*x, sign*y], 'rot': rot}
        failures, _ = inspect(bad, self.route)
        self.assertIn(('courtyard', 'C_FILTER1N1', 'U_ISO1'), failures)

    def test_original_input_capacitor_collision_is_rejected(self):
        bad = copy.deepcopy(self.floor)
        bad['placement']['anchors']['C_LDO_IN'] = [60, 67.5, 180]
        failures, _ = inspect(bad, self.route)
        self.assertIn(('courtyard', 'C_LDO_IN', 'U_LDO_EN'), failures)


if __name__ == '__main__':
    unittest.main(verbosity=2)
