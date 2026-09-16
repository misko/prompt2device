"""Source presentation must cover the independent census and preserve nets.

This is not a human readability review. Electrical endpoints are compared
against the existing generated candidate; full conductor parity remains owed
whenever that candidate is stale.
"""
import json
import math
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET

import yaml
from source_inventory import inventory, source_rows

PROJECT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = PROJECT / '03_tscircuit/src/schematic_presentation.tsx'


def validate_paths(intent, endpoint_nets):
    for sheet, paths in intent['paths'].items():
        for path in paths:
            if len(path) < 2:
                raise ValueError('empty primary wire')
            nets = set()
            for endpoint in path:
                ref, _ = endpoint.split('.')
                if intent['poses'][ref][0] != sheet:
                    raise ValueError('cross-sheet primary wire')
                if endpoint not in endpoint_nets:
                    raise ValueError('missing or unconnected endpoint')
                nets.add(endpoint_nets[endpoint])
            if len(nets) != 1:
                raise ValueError('primary wire merges different nets')


class PresentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        bun = shutil.which('bun') or str(pathlib.Path.home() / '.bun/bin/bun')
        script = f'import {{presentationIntent}} from {json.dumps(str(SOURCE))}; console.log(JSON.stringify(presentationIntent))'
        cls.intent = json.loads(subprocess.check_output([bun, '--eval', script], text=True))
        circuit = json.loads((PROJECT / '03_tscircuit/build/circuit.json').read_text())
        refs = {e['source_component_id']: e['name'] for e in circuit if e['type'] == 'source_component'}
        cls.endpoint_nets = {
            f"{refs[e['source_component_id']]}.{e['pin_number']}": e['subcircuit_connectivity_map_key']
            for e in circuit if e['type'] == 'source_port' and e.get('subcircuit_connectivity_map_key')
        }

    def test_exact_component_ownership(self):
        census = yaml.safe_load((PROJECT / '03_tscircuit/manifest.yaml').read_text())['components']
        self.assertEqual(set(census), set(self.intent['poses']))
        self.assertEqual(333, len(census))

    def test_every_component_has_finite_producer_coordinates(self):
        # 2026-09-09: D_BUCK_IN omitted the wrapper's section/X/Y inputs.
        # poseFor supplied its human pose, hiding NaN scratch-PCB coordinates
        # until the real build. RED on source8cd07f59; no generated oracle.
        rows = source_rows()
        census = yaml.safe_load((PROJECT / '03_tscircuit/manifest.yaml').read_text())['components']
        self.assertEqual(set(census), {row['name'] for row in rows})
        for row in rows:
            for axis in ('pcbX', 'pcbY'):
                with self.subTest(ref=row['name'], axis=axis):
                    value = row[axis]
                    self.assertTrue(value.endswith('mm'))
                    self.assertTrue(math.isfinite(float(value[:-2])), value)

    def test_every_primary_wire_preserves_existing_net(self):
        validate_paths(self.intent, {f"{r}.{p}":n for (r,p),n in inventory()[1].items()})
        self.assertGreater(sum(map(len, self.intent['paths'].values())), 100)

    def test_reject_cross_net_wire(self):
        bad = {'poses':self.intent['poses'], 'paths':{'input':[['J9.1','J9.2']]}}
        with self.assertRaisesRegex(ValueError, 'different nets'):
            validate_paths(bad, self.endpoint_nets)

    def test_reject_cross_sheet_wire(self):
        bad = {'poses':self.intent['poses'], 'paths':{'input':[['J9.1','J1.1']]}}
        with self.assertRaisesRegex(ValueError, 'cross-sheet'):
            validate_paths(bad, self.endpoint_nets)

    def test_reject_missing_pin(self):
        bad = {'poses':self.intent['poses'], 'paths':{'input':[['J9.1','J9.99']]}}
        with self.assertRaisesRegex(ValueError, 'missing'):
            validate_paths(bad, self.endpoint_nets)

    def test_delivered_pdf_text_floor(self):
        # Integer-rounded native-point inventory, not a substitute for viewing
        # the delivered page. Header size cannot mask undersized circuit text.
        pdf = PROJECT / '03_tscircuit/build/schematic.pdf'
        root = ET.fromstring(subprocess.check_output(
            ['pdftohtml','-xml','-i','-zoom','1','-stdout',str(pdf)], text=True))
        pages = root.findall('page')
        self.assertEqual(19, len(pages))
        graded = 0
        fonts = {}
        for page in pages:
            fonts.update({font.attrib['id']:font.attrib for font in page.findall('fontspec')})
            for text in page.findall('text'):
                font = fonts[text.attrib['font']]
                if font['color'] == '#555555':
                    continue  # provenance caption, never a circuit identifier
                floor = 6 if font['color'] == '#a90000' else 7
                self.assertGreaterEqual(int(font['size']), floor,
                    f"page {page.attrib['number']}: {''.join(text.itertext())}")
                graded += 1
        self.assertGreater(graded, 1000)

    def test_delivered_native_schematic_has_no_ink_occlusion(self):
        # RED on ae0ecbca's native schematic: seven clock/pulldown
        # property collisions survived the PDF review. Grade the delivered
        # KiCad geometry through the independent native checker, not the
        # presentation coordinates or the PDF renderer's text metrics.
        script = PROJECT.parents[1] / 'skills/kicad-pcb/scripts/sch_occlusion.py'
        sheet = PROJECT / '04_kicad/crow_audio_carrier_v1.kicad_sch'
        with tempfile.TemporaryDirectory() as tmp:
            report = pathlib.Path(tmp) / 'occlusion.json'
            result = subprocess.run(['/usr/bin/python3', str(script), str(sheet),
                '--verbose', '--json', str(report)], capture_output=True,
                text=True, timeout=60)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            measured = json.loads(report.read_text())
        self.assertGreater(measured['graded'], 2500)
        self.assertEqual(measured['graded'], measured['total'])
        self.assertEqual([], measured['unmodelled'])
        self.assertEqual([], measured['occlusions'])

    def test_delivered_filter_identifiers_do_not_overlap_other_text(self):
        # Poppler reads the delivered PDF, independently of authored poses.
        # The 2026-09-09 render merged neighboring shunt identifiers; both
        # missing individual labels and positive-area text overlaps fail.
        root = ET.fromstring(subprocess.check_output(
            ['pdftohtml', '-xml', '-i', '-zoom', '1', '-stdout',
             str(PROJECT / '03_tscircuit/build/schematic.pdf')], text=True))
        checked = 0
        for n in range(1, 9):
            texts = root.findall('page')[n + 4].findall('text')
            for leg in ('P', 'N'):
                for k in (1, 2):
                    ref = f'C_FILTER{n}{leg}{k}'
                    matches = [t for t in texts if ''.join(t.itertext()).strip() == ref]
                    self.assertEqual(1, len(matches), f'{ref}: distinct readable identifier')
                    owner = matches[0]
                    def box(t):
                        x, y = float(t.attrib['left']), float(t.attrib['top'])
                        return x, y, x + float(t.attrib['width']), y + float(t.attrib['height'])
                    a = box(owner)
                    for other in texts:
                        if other is owner:
                            continue
                        b = box(other)
                        overlap = min(a[2], b[2]) - max(a[0], b[0])
                        height = min(a[3], b[3]) - max(a[1], b[1])
                        self.assertFalse(overlap > 0 and height > 0,
                            f'{ref} overlaps {"".join(other.itertext())}')
                    checked += 1
        self.assertEqual(32, checked)

    def test_every_channel_displays_shared_audio_enable(self):
        # RED on b8c26163's delivered PDF: electrically connected selector
        # pairs had no readable cross-page net identity on all eight sheets.
        pdf = PROJECT / '03_tscircuit/build/schematic.pdf'
        pages = subprocess.check_output(
            ['pdftotext', '-layout', str(pdf), '-'], text=True).split('\f')
        for n in range(1, 9):
            with self.subTest(channel=n):
                self.assertRegex(pages[n + 4], r'\bAUDIO_EN\b')
                for pin in ('3', '7'):
                    self.assertEqual('AUDIO_EN', inventory()[1][(f'U_ISO{n}', pin)])

    def test_delivered_ldo_nc_labels_clear_ground_pin_labels(self):
        # RED on 8ddb11a1's delivered PDF: the horizontal VIOC_NC label
        # crosses the vertical EP label (and the GND2 text envelope).
        # Poppler measures the actual rotated PDF text, independently of
        # tscircuit's symbol dimensions or our authored pin arrangement.
        pdf = PROJECT / '03_tscircuit/build/schematic.pdf'
        root = ET.fromstring(subprocess.check_output(
            ['pdftotext', '-f', '3', '-l', '3', '-bbox', str(pdf), '-'],
            text=True))
        labels = ('VIOC_NC', 'PG_NC', 'ILIM', 'GND1', 'GND2', 'EP')
        boxes = {}
        for label in labels:
            matches = [word for word in root.iter()
                       if word.tag.endswith('word') and word.text == label]
            self.assertEqual(1, len(matches), f'{label}: distinct pin label')
            boxes[label] = tuple(float(matches[0].attrib[key])
                                 for key in ('xMin', 'yMin', 'xMax', 'yMax'))
        for side in ('VIOC_NC', 'PG_NC'):
            for bottom in ('ILIM', 'GND1', 'GND2', 'EP'):
                with self.subTest(side=side, bottom=bottom):
                    a, b = boxes[side], boxes[bottom]
                    overlap_x = min(a[2], b[2]) - max(a[0], b[0])
                    overlap_y = min(a[3], b[3]) - max(a[1], b[1])
                    self.assertFalse(overlap_x > 0 and overlap_y > 0,
                                     f'{side} overlaps {bottom}')

    def test_delivered_ldo_identity_clears_linear_wires(self):
        # RED on b8c26163: the SET wire crosses the U_LDO reference. Poppler
        # independently extracts actual delivered PDF text and vector paths;
        # no author-coordinate or renderer font metric is the oracle.
        # Scoped to this chip's reference/MPN and straight green wire segments;
        # curved hop-overs, other colors and other glyphs remain human review.
        pdf = PROJECT / '03_tscircuit/build/schematic.pdf'
        words = ET.fromstring(subprocess.check_output(
            ['pdftotext', '-bbox', '-f', '3', '-l', '3', str(pdf), '-'], text=True))
        boxes = []
        for label in ('U_LDO', 'LT3041ADE#TRPBF'):
            matches = [e for e in words.iter() if e.tag.endswith('}word') and e.text == label]
            self.assertEqual(1, len(matches), label)
            boxes.append((label, tuple(float(matches[0].attrib[k])
                for k in ('xMin', 'yMin', 'xMax', 'yMax'))))
        with tempfile.TemporaryDirectory() as tmp:
            svg = pathlib.Path(tmp) / 'page.svg'
            subprocess.run(['pdftocairo', '-svg', '-f', '3', '-l', '3',
                            str(pdf), str(svg)], check=True, capture_output=True)
            root = ET.parse(svg).getroot()
        parents = {child: parent for parent in root.iter() for child in parent}
        segments = []
        for path in root.iter('{http://www.w3.org/2000/svg}path'):
            stroke = path.get('stroke', '')
            if not re.fullmatch(r'rgb\(0%, [\d.]+%, 0%\)', stroke):
                continue
            d = path.get('d', '')
            if set(re.findall('[A-Za-z]', d)) - {'M', 'L'}:
                continue  # explicitly ungraded curved bridge arcs
            ancestor = parents.get(path)
            while ancestor is not None:
                self.assertNotIn('transform', ancestor.attrib,
                    'new nested Cairo transform must be resolved, not ignored')
                ancestor = parents.get(ancestor)
            transform = path.get('transform', 'matrix(1,0,0,1,0,0)')
            self.assertRegex(transform, r'^matrix\([^()]+\)$')
            matrix = [float(v) for v in re.split(r'[,\s]+', transform[7:-1].strip())]
            self.assertEqual(6, len(matrix))
            a, b, c, d0, e, f = matrix
            tokens = re.findall(r'([ML])\s+([-\d.]+)\s+([-\d.]+)', d)
            self.assertGreaterEqual(len(tokens), 2)
            previous = None
            for kind, x0, y0 in tokens:
                x, y = float(x0), float(y0)
                point = (a*x + c*y + e, b*x + d0*y + f)
                if kind == 'L' and previous is not None:
                    segments.append((previous, point))
                previous = point
        self.assertGreater(len(segments), 30, 'must actually grade delivered wires')
        from test_schematic_ground_clearance import segment_hits_box
        for label, box in boxes:
            for start, end in segments:
                self.assertFalse(segment_hits_box(dict(zip(('x','y'), start)),
                    dict(zip(('x','y'), end)), box), f'{label}: wire {start}->{end}')
