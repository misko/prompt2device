"""Project-local complete-ink screen, not an adopted gate or PDF acceptance.

Backend gap: the schematic router does not reserve rendered net-label plates,
NC stubs, or all filled chip bodies. A shared renderer-owned obstacle schema
would replace this adapter. Widths come from the pinned renderer's actual
Arial metrics, NOT Circuit JSON center offsets (wrong for RESET_RC).
The rectangle screen is conservative at arrow-tip corners; findings must be
viewed, not silently waived. Perpendicular crossings remain legitimate.
Component reference/value text, general schematic_text, nonrectangular symbol
ink and border-only contacts are not fully modeled. Full PDF views remain
mandatory even when this screen and the separate Ground screen report zero.
"""
import collections
import json
from pathlib import Path
import re
import sys
import unittest

from test_schematic_ground_clearance import segment_hits_box
from source_inventory import source_rows

PROJECT = Path(__file__).resolve().parents[2]
RENDERER = PROJECT / '03_tscircuit/node_modules/circuit-to-svg/dist/index.js'


def renderer_widths():
    source = RENDERER.read_text()
    table = source.split('var arialTextMetrics = {', 1)[1].split('\n};', 1)[0]
    widths = {}
    for match in re.finditer(r'\n  ("(?:[^"\\]|\\.)*"|[A-Za-z_]): \{\s+width: (\d+),', table):
        key = match[1]
        widths[json.loads(key) if key.startswith('"') else key] = int(match[2])
    assert len(widths) > 80, 'pinned renderer metric table changed'
    assert 'var NET_LABEL_HEIGHT_MM = 0.2;' in source
    assert 'net_label: 0.18,' in source
    return widths


def plate_box(label, widths):
    # Same leading-N rail convention as the delivered renderer; carrier has
    # no other display aliases. Complete fill, border and glyph envelope.
    text = re.sub(r'^N(?=\d)', '', label['text'])
    length = .18 * (sum(widths.get(c, widths['?']) for c in text)/27 + .9 + .06*len(text))
    x, y = label['anchor_position']['x'], label['anchor_position']['y']
    dx, dy = {'left':(1,0), 'right':(-1,0), 'top':(0,-1), 'bottom':(0,1)}[label['anchor_side']]
    # .02 total stroke width; includes .01 border + .01 foreign stroke.
    return (min(x,x+dx*length)-(.12 if dy else .02),
            min(y,y+dy*length)-(.12 if dx else .02),
            max(x,x+dx*length)+(.12 if dy else .02),
            max(y,y+dy*length)+(.12 if dx else .02))


def boxes_touch(a, b):
    return a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]


def label_wire_hit(label, a, b, widths):
    """Same-net ink is not exempt, except an attachment from behind/side.

    This supplements the broad screen's foreign-net scope for the supervisor
    supply plates. It does not claim general PDF or glyph-shape acceptance.
    """
    anchor = label['anchor_position']
    direction = {'left':(1,0), 'right':(-1,0), 'top':(0,-1), 'bottom':(0,1)}[label['anchor_side']]
    for endpoint, other in [(a, b), (b, a)]:
        if all(abs(endpoint[axis]-anchor[axis]) < 1e-8 for axis in ('x', 'y')):
            dot = sum((other[axis]-anchor[axis])*d for axis, d in zip(('x', 'y'), direction))
            if dot <= 1e-8:
                return False
    return segment_hits_box(a, b, plate_box(label, widths))


def parallel_contact(a, b, c, d, clearance=.04):
    """Visible near-coincident run; no perpendicular-crossing rejection."""
    for fixed, run in [('x','y'), ('y','x')]:
        if abs(a[fixed]-b[fixed]) > 1e-8 or abs(c[fixed]-d[fixed]) > 1e-8:
            continue
        overlap = min(max(a[run],b[run]),max(c[run],d[run])) - max(min(a[run],b[run]),min(c[run],d[run]))
        if overlap > .04 and abs(a[fixed]-c[fixed]) < clearance:
            return True
    return False


def ink_clearance(circuit):
    widths = renderer_widths()
    nets = {e['source_net_id']:e.get('subcircuit_connectivity_map_key') for e in circuit if e['type']=='source_net'}
    refs = {e['source_component_id']:e['name'] for e in circuit if e['type']=='source_component'}
    ports = {e['source_port_id']:e for e in circuit if e['type']=='source_port'}
    sheets = collections.defaultdict(list)
    for e in circuit:
        if e.get('schematic_sheet_id'):
            sheets[e['schematic_sheet_id']].append(e)
    found = set()
    census = collections.Counter()
    for sheet, elements in sheets.items():
        traces = [e for e in elements if e['type']=='schematic_trace']
        labels = [e for e in elements if e['type']=='schematic_net_label' and not e.get('symbol_name') and e.get('text')]
        bodies = [e for e in elements if e['type']=='schematic_component' and not e.get('symbol_name')]
        ncs = [e for e in elements if e['type']=='schematic_port' and not ports[e['source_port_id']].get('subcircuit_connectivity_map_key')]
        census.update(sheets=1, labels=len(labels), bodies=len(bodies), ncs=len(ncs), traces=len(traces))
        for label in labels:
            box = plate_box(label,widths)
            lid, owner = label['schematic_net_label_id'], nets.get(label.get('source_net_id'))
            for trace in traces:
                if owner and owner == trace.get('subcircuit_connectivity_map_key'):
                    continue
                if any(segment_hits_box(e['from'],e['to'],box) for e in trace.get('edges',[])):
                    found.add(('plate-wire',sheet,label['text'],lid,trace['schematic_trace_id']))
            for other in labels:
                if other['schematic_net_label_id'] <= lid or other.get('source_net_id') == label.get('source_net_id'):
                    continue
                if boxes_touch(box,plate_box(other,widths)):
                    found.add(('plate-plate',sheet,label['text'],lid,other['schematic_net_label_id']))
            for nc in ncs:
                a = nc['center']; b = dict(a)
                dx,dy = {'left':(1,0),'right':(-1,0),'up':(0,-1),'down':(0,1)}[nc['facing_direction']]
                distance = nc.get('distance_from_component_edge',.4)
                b['x'] += dx*distance; b['y'] += dy*distance
                if segment_hits_box(a,b,box):
                    port=ports[nc['source_port_id']]
                    found.add(('plate-nc',sheet,label['text'],lid,f"{refs[port['source_component_id']]}.{port['pin_number']}"))
        for i, trace in enumerate(traces):
            for other in traces[i+1:]:
                if trace.get('subcircuit_connectivity_map_key') == other.get('subcircuit_connectivity_map_key'):
                    continue
                if any(parallel_contact(a['from'],a['to'],b['from'],b['to']) for a in trace.get('edges',[]) for b in other.get('edges',[])):
                    found.add(('parallel',sheet,'',trace['schematic_trace_id'],other['schematic_trace_id']))
            for body in bodies:
                x,y=body['center']['x'],body['center']['y']; w,h=body['size']['width'],body['size']['height']
                # Filled rectangular chips only. Numerical epsilon excludes
                # exact boundary touches, not a hidden .03-wide interior band.
                # Border-stroke-only contacts remain a visual-review limit.
                epsilon=1e-8
                box=(x-w/2+epsilon,y-h/2+epsilon,x+w/2-epsilon,y+h/2-epsilon)
                if any(segment_hits_box(e['from'],e['to'],box) for e in trace.get('edges',[])):
                    found.add(('body-wire',sheet,refs[body['source_component_id']],body['schematic_component_id'],trace['schematic_trace_id']))
    return dict(census), sorted(found)


def fixture():
    return [
        {'type':'source_net','source_net_id':'g','subcircuit_connectivity_map_key':'ground'},
        {'type':'source_net','source_net_id':'s','subcircuit_connectivity_map_key':'signal'},
        {'type':'source_component','source_component_id':'u','name':'U1'},
        {'type':'source_port','source_port_id':'nc','source_component_id':'u','pin_number':1},
        {'type':'schematic_component','schematic_component_id':'body','source_component_id':'u',
         'center':{'x':4,'y':0},'size':{'width':2,'height':2},'schematic_sheet_id':'one'},
        {'type':'schematic_port','source_port_id':'nc','center':{'x':2.6,'y':0},
         'facing_direction':'left','distance_from_component_edge':.4,'schematic_sheet_id':'one'},
        {'type':'schematic_net_label','schematic_net_label_id':'label','text':'RESET_RC','source_net_id':'g',
         'anchor_position':{'x':0,'y':0},'anchor_side':'left','schematic_sheet_id':'one'},
        {'type':'schematic_trace','schematic_trace_id':'trace','subcircuit_connectivity_map_key':'signal',
         'schematic_sheet_id':'one','edges':[{'from':{'x':2,'y':-2},'to':{'x':2,'y':2}}]},
    ]


class InkGeometryTests(unittest.TestCase):
    def test_same_net_label_attachment_is_direction_scoped(self):
        label = {'text':'N5V_LDO_HOLD', 'anchor_position':{'x':0,'y':0}, 'anchor_side':'right'}
        widths = renderer_widths()
        point = lambda x, y: {'x':x, 'y':y}
        self.assertFalse(label_wire_hit(label, point(0,0), point(1,0), widths))
        self.assertFalse(label_wire_hit(label, point(0,1), point(0,0), widths))
        self.assertTrue(label_wire_hit(label, point(0,0), point(-1,0), widths))
        self.assertTrue(label_wire_hit(label, point(-.2,1), point(-.2,-1), widths))
        self.assertTrue(label_wire_hit(label, point(-1,0), point(1,0), widths))
        self.assertFalse(label_wire_hit(label, point(.2,1), point(.2,-1), widths))

    def test_delivered_supervisor_supply_plates_include_own_wires(self):
        # RED on the actual 77b5d69e PDF's source: U_AUDIO's same-net
        # downleg passes through HOLD. Electrical ownership cannot excuse ink.
        circuit = json.loads((PROJECT/'03_tscircuit/build/circuit.json').read_text())
        sheet = next(e['schematic_sheet_id'] for e in circuit
                     if e['type']=='schematic_sheet' and e['name']=='supervisors')
        labels = [e for e in circuit if e['type']=='schematic_net_label'
                  and e.get('schematic_sheet_id')==sheet and e.get('text')=='N5V_LDO_HOLD']
        self.assertEqual(4, len(labels))
        traces = [e for e in circuit if e['type']=='schematic_trace' and e.get('schematic_sheet_id')==sheet]
        self.assertGreater(len(traces), 20)
        widths = renderer_widths()
        hits = [(label['schematic_net_label_id'], trace['schematic_trace_id'])
                for label in labels for trace in traces
                if any(label_wire_hit(label, edge['from'], edge['to'], widths)
                       for edge in trace.get('edges', []))]
        self.assertEqual([], hits)

    def test_end_to_end_plate_and_net_ownership(self):
        good=fixture()
        self.assertEqual([],ink_clearance(good)[1])
        good[-1]['edges']=[{'from':{'x':.5,'y':-2},'to':{'x':.5,'y':2}}]
        self.assertEqual(['plate-wire'],[f[0] for f in ink_clearance(good)[1]])
        good[-1]['subcircuit_connectivity_map_key']='ground'
        self.assertEqual([],ink_clearance(good)[1])
        good[-1]['subcircuit_connectivity_map_key']='signal'
        good[-1]['schematic_sheet_id']='other'
        self.assertEqual([],ink_clearance(good)[1])

    def test_end_to_end_nc_and_plate_pair(self):
        bad=fixture()
        bad[5]['center']={'x':.7,'y':-.1}
        self.assertEqual(['plate-nc'],[f[0] for f in ink_clearance(bad)[1]])
        bad[5]['center']={'x':2.6,'y':0}
        bad.append({**bad[6],'schematic_net_label_id':'label2','source_net_id':'s',
                    'anchor_position':{'x':.7,'y':0}})
        self.assertIn('plate-plate',[f[0] for f in ink_clearance(bad)[1]])
        bad[-1]['anchor_position']={'x':0,'y':-3}
        self.assertEqual([],ink_clearance(bad)[1])

    def test_end_to_end_body_has_no_owner_exemption(self):
        bad=fixture()
        bad[-1]['edges']=[{'from':{'x':3.001,'y':-.5},'to':{'x':3.001,'y':.5}}]
        self.assertEqual(['body-wire'],[f[0] for f in ink_clearance(bad)[1]])
        bad[-1]['edges']=[{'from':{'x':2.95,'y':-.5},'to':{'x':2.95,'y':.5}}]
        self.assertEqual([],ink_clearance(bad)[1])

    def test_end_to_end_near_strokes_and_perpendicular_crossing(self):
        bad=fixture()
        bad.append({**bad[-1],'schematic_trace_id':'trace2','subcircuit_connectivity_map_key':'ground',
                    'edges':[{'from':{'x':2.01,'y':-.5},'to':{'x':2.01,'y':.5}}]})
        self.assertEqual(['parallel'],[f[0] for f in ink_clearance(bad)[1]])
        bad[-1]['edges']=[{'from':{'x':1.5,'y':.5},'to':{'x':2.5,'y':.5},'is_crossing':True}]
        self.assertEqual([],ink_clearance(bad)[1])

    def test_complete_plate_not_cj_center(self):
        label={'text':'RESET_RC','anchor_position':{'x':0,'y':0},'center':{'x':0,'y':-.09},'anchor_side':'top'}
        box=plate_box(label,renderer_widths())
        self.assertLess(box[1],-.9)
        self.assertTrue(segment_hits_box({'x':-1,'y':-.8},{'x':1,'y':-.8},box))
        self.assertFalse(segment_hits_box({'x':-1,'y':-2},{'x':1,'y':-2},box))

    def test_hostile_parallel_and_good_crossing(self):
        a,b={'x':-1.52,'y':.8},{'x':-1.52,'y':1.2}
        self.assertTrue(parallel_contact(a,b,{'x':-1.53,'y':.5},{'x':-1.53,'y':1}))
        self.assertFalse(parallel_contact(a,b,{'x':-1.7,'y':.5},{'x':-1.7,'y':1}))
        self.assertFalse(parallel_contact(a,b,{'x':-2,'y':1},{'x':0,'y':1}))

    def test_hostile_body_and_good_external_corridor(self):
        box=(-1,-1,1,1)
        self.assertTrue(segment_hits_box({'x':-2,'y':0},{'x':0,'y':0},box))
        self.assertFalse(segment_hits_box({'x':-2,'y':2},{'x':2,'y':2},box))

    def test_nc_and_plate_tangent(self):
        box=(0,-.1,1,.1)
        self.assertTrue(segment_hits_box({'x':1,'y':-.1},{'x':1.4,'y':-.1},box))
        self.assertFalse(segment_hits_box({'x':1.1,'y':-.1},{'x':1.5,'y':-.1},box))
        self.assertTrue(boxes_touch(box,(1,-1,2,-.1)))
        self.assertFalse(boxes_touch(box,(1.1,-1,2,-.1)))

    def test_delivered_complete_ink(self):
        circuit = json.loads((PROJECT/'03_tscircuit/build/circuit.json').read_text())
        census, findings = ink_clearance(circuit)
        self.assertEqual(19,census['sheets'])
        # ADR0025's LT3041 has two intentional floats (VIOC and PG), versus
        # the old TPS's one. Compare exact identities to live JSX declarations
        # rather than leaving the old 41-pin total in front of the ink check.
        expected_nc = {(row['name'], pin[3:]) for row in source_rows()
                       for pin in row.get('pinLabels', {})
                       if pin not in row.get('connections', {})}
        refs = {e['source_component_id']: e['name'] for e in circuit
                if e['type'] == 'source_component'}
        actual_nc = {(refs[e['source_component_id']], str(e['pin_number']))
                     for e in circuit if e['type'] == 'source_port'
                     and not e.get('subcircuit_connectivity_map_key')}
        self.assertEqual(42, len(expected_nc))
        self.assertEqual(expected_nc, actual_nc)
        self.assertEqual(len(expected_nc), census['ncs'])
        self.assertGreater(census['labels'],200)
        self.assertEqual([],findings)


if __name__=='__main__':
    if len(sys.argv)>1:
        census,findings=ink_clearance(json.loads(Path(sys.argv[1]).read_text()))
        print(json.dumps({'census':census,'findings':findings},indent=2))
    else:
        unittest.main()
