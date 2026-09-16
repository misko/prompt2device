"""Project-local rail_down ink regression; not independent PDF acceptance.

Backend gap: the pinned schematic router treats a ground anchor as an endpoint,
not its bar/text clearance envelope. A future shared symbol-ink obstacle schema
would replace this conservative project test. Adapted from the commissioned
read-only ground_collision_screen.py; good/hostile fixtures pin its limits.
"""
import json
from pathlib import Path
import unittest

PROJECT = Path(__file__).resolve().parents[2]


def segment_hits_box(a, b, box):
    low, high = 0.0, 1.0
    for axis, lo, hi in [('x', box[0], box[2]), ('y', box[1], box[3])]:
        delta = b[axis] - a[axis]
        if abs(delta) < 1e-10:
            if a[axis] < lo or a[axis] > hi:
                return False
        else:
            t0, t1 = sorted(((lo-a[axis])/delta, (hi-a[axis])/delta))
            low, high = max(low, t0), min(high, t1)
            if low > high:
                return False
    return True


def ground_clearance(circuit):
    nets = {e['source_net_id']: e for e in circuit if e['type'] == 'source_net'}
    findings = []
    grounds = [e for e in circuit if e['type'] == 'schematic_net_label'
               and e.get('symbol_name') == 'rail_down' and e.get('text') == 'GND']
    for label in grounds:
        owner = nets[label['source_net_id']]['subcircuit_connectivity_map_key']
        x, y = label['anchor_position']['x'], label['anchor_position']['y']
        # Pinned symbol: bar +/-0.12 at y-0.18; text 0.18 high at y-0.23.
        box = (x-.24, y-.45, x+.24, y+.02)
        for foreign in circuit:
            if foreign.get('schematic_sheet_id') != label['schematic_sheet_id']:
                continue
            if foreign['type'] == 'schematic_trace':
                if foreign.get('subcircuit_connectivity_map_key') == owner:
                    continue
                hit = any(segment_hits_box(edge['from'], edge['to'], box)
                          for edge in foreign.get('edges', []))
                identity = foreign['schematic_trace_id']
            elif foreign['type'] == 'schematic_net_label':
                if foreign.get('symbol_name') or foreign.get('source_net_id') == label['source_net_id']:
                    continue
                anchor, center = foreign.get('anchor_position'), foreign.get('center')
                if not anchor or not center:
                    continue
                end = {axis: 2*center[axis]-anchor[axis] for axis in ('x','y')}
                horizontal = foreign['anchor_side'] in ('left','right')
                plate = (min(anchor['x'],end['x'])-(0 if horizontal else .1),
                         min(anchor['y'],end['y'])-(.1 if horizontal else 0),
                         max(anchor['x'],end['x'])+(0 if horizontal else .1),
                         max(anchor['y'],end['y'])+(.1 if horizontal else 0))
                hit = box[0] <= plate[2] and plate[0] <= box[2] and box[1] <= plate[3] and plate[1] <= box[3]
                identity = foreign['schematic_net_label_id']
            else:
                continue
            if hit:
                findings.append((label['schematic_net_label_id'], identity))
    return len(grounds), findings


def fixture():
    return [
        {'type':'source_net', 'source_net_id':'g', 'subcircuit_connectivity_map_key':'ground'},
        {'type':'schematic_net_label', 'schematic_net_label_id':'g1', 'source_net_id':'g',
         'symbol_name':'rail_down', 'text':'GND', 'anchor_position':{'x':0,'y':0}, 'schematic_sheet_id':'one'},
        {'type':'schematic_trace', 'schematic_trace_id':'t1', 'subcircuit_connectivity_map_key':'signal',
         'schematic_sheet_id':'one', 'edges':[{'from':{'x':1,'y':1},'to':{'x':1,'y':-1}}]},
    ]


class GroundClearanceTests(unittest.TestCase):
    def test_good_clear_corridor(self):
        self.assertEqual((1, []), ground_clearance(fixture()))

    def test_hostile_foreign_downleg(self):
        circuit = fixture()
        circuit[-1]['edges'][0] = {'from':{'x':0,'y':1},'to':{'x':0,'y':-1}}
        self.assertEqual(1, len(ground_clearance(circuit)[1]))
        circuit[-1]['subcircuit_connectivity_map_key'] = 'ground'
        self.assertEqual((1, []), ground_clearance(circuit))

    def test_hostile_foreign_label(self):
        circuit = fixture()
        circuit.append({'type':'schematic_net_label', 'schematic_net_label_id':'bad',
                        'source_net_id':'signal', 'schematic_sheet_id':'one',
                        'anchor_position':{'x':.1,'y':-.2}, 'center':{'x':.6,'y':-.2}, 'anchor_side':'left'})
        self.assertEqual(1, len(ground_clearance(circuit)[1]))
        circuit[-1]['schematic_sheet_id'] = 'other'
        self.assertEqual((1, []), ground_clearance(circuit))

    def test_segment_tangent_diagonal_and_clear(self):
        box = (-.24,-.45,.24,.02)
        self.assertTrue(segment_hits_box({'x':-1,'y':0},{'x':1,'y':0},box))
        self.assertTrue(segment_hits_box({'x':-1,'y':-1},{'x':1,'y':1},box))
        self.assertTrue(segment_hits_box({'x':.24,'y':1},{'x':.24,'y':-1},box))
        self.assertFalse(segment_hits_box({'x':.25,'y':1},{'x':.25,'y':-1},box))

    def test_delivered_circuit_ground_clearance(self):
        circuit = json.loads((PROJECT/'03_tscircuit/build/circuit.json').read_text())
        count, findings = ground_clearance(circuit)
        self.assertGreater(count, 150, 'zero/partial ground census cannot pass')
        self.assertEqual([], findings)

    def test_fsync_output_has_no_unmarked_tail(self):
        circuit = json.loads((PROJECT/'03_tscircuit/build/circuit.json').read_text())
        net = next(e for e in circuit if e['type']=='source_net' and e['name']=='FSYNC_BUF')
        key = net['subcircuit_connectivity_map_key']
        point = lambda p: (round(p['x'], 7), round(p['y'], 7))
        source_ports = {e['source_port_id'] for e in circuit if e['type']=='source_port'
                        and e.get('subcircuit_connectivity_map_key')==key}
        terminals = {point(e['center']) for e in circuit if e['type']=='schematic_port'
                     and e['source_port_id'] in source_ports}
        terminals.update(point(e['anchor_position']) for e in circuit
                         if e['type']=='schematic_net_label' and e.get('source_net_id')==net['source_net_id'])
        edges = {tuple(sorted((point(edge['from']), point(edge['to']))))
                 for e in circuit if e['type']=='schematic_trace' and e.get('subcircuit_connectivity_map_key')==key
                 for edge in e.get('edges', []) if point(edge['from']) != point(edge['to'])}
        degrees = {}
        for edge in edges:
            for p in edge:
                degrees[p] = degrees.get(p, 0)+1
        self.assertGreater(len(edges), 0)
        self.assertEqual([], [p for p, degree in degrees.items() if degree==1 and p not in terminals])
