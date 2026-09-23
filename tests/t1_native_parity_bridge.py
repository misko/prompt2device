#!/usr/bin/env python3
"""Exact dossier identity is the native symbol/footprint parity authority."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/kicad-pcb/scripts'
sys.path.insert(0, str(SCRIPTS))
import circuit_json_to_kicad_sch as sch
import generate_board_generic as board


def fixture(tmp, bad=None, with_layout=False):
    parts = tmp / '02_parts'
    usb = parts / 'USB-EXACT'
    usb.mkdir(parents=True)
    alias = {name: {'schematic': str(i), 'footprint': name,
                    'why': 'exact drawing', 'evidence': 'drawing rev A'}
             for i, name in enumerate(['A1','A4','A5','A6','A7','A8','A9','A12',
                                       'B1','B4','B5','B6','B7','B8','B9','B12','SH'],1)}
    if bad == 'missing':
        del alias['A5']
    if bad == 'many_to_one':
        alias['A4']['footprint'] = 'A1'
    if bad in ('wrong_net','nc_collapse'):
        alias['A4']['footprint'] = 'A1'
        alias['A4']['fused'] = True
    if bad == 'ambiguous':
        alias['A1']['footprint'] = '2'
    import yaml
    (usb / 'part.yaml').write_text(yaml.safe_dump({
        'mpn':'USB-EXACT', 'footprint':'test:USB',
        'datasheet': {'url':'https://example.org/exact.pdf'},
        'pins': {k:('GND' if bad in ('wrong_net','nc_collapse') and k in ('A1','A4') else k)
                 for k in alias}, 'pin_aliases': alias}))
    source = [{'type':'source_component','source_component_id':'c1','name':'J_USB',
               'ftype':'simple_chip','manufacturer_part_number':'USB-EXACT',
               'supplier_part_numbers':{'jlcpcb':['C123']},
               'internally_connected_source_port_ids':[['p17','p17a']]}]
    nets = {1:'GND',2:'VBUS',3:'CC1',4:'DP',5:'DN',7:'VBUS',8:'GND',9:'GND',
            10:'VBUS',11:'CC2',12:'DP',13:'DN',15:'VBUS',16:'GND',17:'GND'}
    if bad == 'nc_collapse': del nets[2]
    for i in range(1,18):
        if bad == 'missing_port' and i == 6:
            continue
        source.append({'type':'source_port','source_port_id':f'p{i}',
                       'source_component_id':'c1','pin_number':i,'name':f'fn{i}',
                       'port_hints':[f'pin{i}'],
                       'subcircuit_connectivity_map_key':f'k{i}' if i in nets else None})
        if i in nets: source.append({'type':'source_net','subcircuit_connectivity_map_key':f'k{i}',
                                     'name':nets[i]})
    source.append({'type':'source_port','source_port_id':'p17a',
                   'source_component_id':'c1','pin_number':None,'name':'shell_extra',
                   'port_hints':['pin17','17']})
    if with_layout:
        source.append({'type':'schematic_component','schematic_component_id':'sc1',
                       'source_component_id':'c1','center':{'x':0,'y':0},
                       'rotation':0,'size':{'width':12,'height':24}})
        for i in range(1,18):
            side='left' if i <= 9 else 'right'
            row=i-1 if i <= 9 else i-10
            source.append({'type':'schematic_port','schematic_port_id':f'sp{i}',
                           'schematic_component_id':'sc1','source_port_id':f'p{i}',
                           'center':{'x':-6 if side=='left' else 6,'y':10-row*2.5},
                           'facing_direction':side,'side_of_component':side,
                           'pin_number':i,'display_pin_label':f'fn{i}',
                           'is_connected':i in nets})
    path = tmp / 'circuit.json'
    path.write_text(json.dumps(source))
    return parts,path


class NativeBridge(unittest.TestCase):
    def _assert_kicad_parity(self, mode):
        import pcbnew
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);parts,path=fixture(root, with_layout=mode == "layout")
            emitter = sch.convert_layout if mode == 'layout' else sch.convert
            generated=emitter(path,'mini','mini','A','2026-09-23',
                overrides={'USB-EXACT':'test:USB'},
                part_authority=sch.load_part_authority(parts))
            sheet, comps=generated[:2]
            sheet_path=root/'mini.kicad_sch';sheet_path.write_text(sheet)
            net_path=root/'mini.net'
            subprocess.run(['kicad-cli','sch','export','netlist','--format',
                            'kicadsexpr','-o',str(net_path),str(sheet_path)],
                           check=True,capture_output=True)
            _,padnets,_=board.parse_netlist(net_path)
            b=pcbnew.BOARD();b.SetCopperLayerCount(2)
            fp=pcbnew.FOOTPRINT(b);fp.SetReference('J_USB');fp.SetValue('USB-EXACT')
            fp.SetFPIDAsString('test:USB')
            fp.SetPosition(pcbnew.VECTOR2I_MM(10,10))
            fp.SetField('Datasheet','https://example.org/stale.pdf')
            ids=board.parse_identity_fields(net_path)
            for name,value in ids['J_USB'].items():
                fp.SetField(name,value)
            url=board.resolve_datasheet_fields({'J_USB':('test:USB','USB-EXACT')},
                                               ids,parts)['J_USB']
            board.apply_datasheet_field(fp,url)
            for i,(pad,_func,_net) in enumerate(comps[0]['pins']):
                item=pcbnew.PAD(fp);item.SetNumber(pad)
                item.SetSize(pcbnew.VECTOR2I_MM(1,1))
                item.SetPosition(pcbnew.VECTOR2I_MM(10+i*1.5,10))
                item.SetLayerSet(pcbnew.LSET.FrontMask())
                item.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
                net=padnets.get(('J_USB',pad))
                if net:
                    native=b.FindNet(net)
                    if not native:
                        native=pcbnew.NETINFO_ITEM(b,net);b.Add(native)
                    item.SetNet(native)
                fp.Add(item)
            b.Add(fp)
            pcb_path=root/'mini.kicad_pcb';pcbnew.SaveBoard(str(pcb_path),b)
            report=root/'drc.json'
            subprocess.run(['kicad-cli','pcb','drc','--schematic-parity',
                            '--format','json','-o',str(report),str(pcb_path)],
                           check=True,capture_output=True)
            self.assertEqual(json.loads(report.read_text())['schematic_parity'],[])

    def test_kicad_grid_parity(self):
        self._assert_kicad_parity('grid')

    def test_kicad_layout_parity(self):
        self._assert_kicad_parity('layout')

    def test_exact_usb_and_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            parts,path=fixture(Path(d))
            comps,_,ports=sch.load_model(path, overrides={'USB-EXACT':'test:USB'},
                return_ports=True,part_authority=sch.load_part_authority(parts))
            pins={p:(name,net) for p,name,net in comps[0]['pins']}
            self.assertEqual(len(pins),17)
            self.assertEqual(ports['p17a']['pad'],'SH')
            self.assertEqual(pins['A8'][1],None)
            self.assertEqual(pins['B8'][1],None)
            self.assertEqual(pins['A6'][1],pins['B6'][1])
            self.assertEqual(pins['A7'][1],pins['B7'][1])
            self.assertEqual(comps[0]['datasheet'],'https://example.org/exact.pdf')
            ids={'J_USB': {'Manufacturer Part Number':'USB-EXACT',
                           'Supplier Part Numbers':json.dumps({'jlcpcb':['C123']})}}
            self.assertEqual(board.resolve_datasheet_fields({'J_USB':('test:USB','freeform')},ids,parts),
                             {'J_USB':'https://example.org/exact.pdf'})
            self.assertEqual(board.resolve_datasheet_fields({'J_USB':('test:USB','USB-EXACT')},{},parts),{})
            sheet, _ = sch.convert(path, 'test', 'test', 'A', '2026-09-23',
                overrides={'USB-EXACT':'test:USB'},
                part_authority=sch.load_part_authority(parts))
            self.assertIn('(pin "A1"',sheet)
            self.assertIn('(pin "SH"',sheet)
            self.assertIn('(property "Datasheet" "https://example.org/exact.pdf"',sheet)
            self.assertIn('(no_connect ',sheet)
            sheet_path=Path(d)/'mini.kicad_sch';sheet_path.write_text(sheet)
            net_path=Path(d)/'mini.net'
            subprocess.run(['kicad-cli','sch','export','netlist','--format',
                            'kicadsexpr','-o',str(net_path),str(sheet_path)],
                           check=True,capture_output=True)
            self.assertEqual(board.parse_identity_fields(net_path)['J_USB'][
                'Manufacturer Part Number'],'USB-EXACT')
            model = {**comps[0], 'sym':'SYM_J_USB', 'inst':(20,20),
                     'pins_geo':[('A1','GND',-5,0,0,2.54)],
                     'tips':{'A1':(15,20)}, 'sides':{'A1':'left'}}
            layout_instance = sch._emit_layout_component(
                model,'test','root',None,[0],{'J_USB':model},((20,15),(20,25)))
            self.assertIn('(property "Datasheet" "https://example.org/exact.pdf"',
                          '\n'.join(layout_instance))
            import pcbnew
            for initial in ('', 'https://example.org/stale.pdf'):
                fp=pcbnew.FOOTPRINT(pcbnew.BOARD())
                fp.SetField('Datasheet',initial)
                board.apply_datasheet_field(fp,'https://example.org/exact.pdf')
                self.assertEqual(fp.GetField('Datasheet').GetText(),
                                 'https://example.org/exact.pdf')

    def test_hostile_aliases(self):
        for kind in ('missing','missing_port','many_to_one','ambiguous',
                     'wrong_net','nc_collapse'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as d:
                parts,path=fixture(Path(d),kind)
                with self.assertRaises(ValueError):
                    sch.load_model(path, overrides={'USB-EXACT':'test:USB'},
                        part_authority=sch.load_part_authority(parts))

    def test_bad_exact_part_authority(self):
        with tempfile.TemporaryDirectory() as d:
            parts,path=fixture(Path(d))
            other=parts/'OTHER';other.mkdir()
            (other/'part.yaml').write_text('mpn: OTHER\nfootprint: test:OTHER\n'
                                           'sourcing: {lcsc: C123}\n')
            with self.assertRaisesRegex(ValueError,'conflicting exact part identities'):
                sch.load_model(path,overrides={'USB-EXACT':'test:USB'},
                    part_authority=sch.load_part_authority(parts))
            (other/'part.yaml').write_text('mpn: [unterminated\n')
            with self.assertRaisesRegex(ValueError,'malformed part authority'):
                sch.load_part_authority(parts)

    def test_fused_drain_identity(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); parts=root/'02_parts'; p=parts/'FET';p.mkdir(parents=True)
            import yaml
            (p/'part.yaml').write_text(yaml.safe_dump({'mpn':'FET','footprint':'test:FET',
                'pins':{str(i):('DRAIN' if i >= 5 else 'SOURCE')
                        for i in range(1,9)},
                'pin_aliases':{str(i):{'schematic':'5','footprint':'5','fused':True,
                    'why':'one drain land','evidence':'drawing'} for i in range(6,9)}}))
            data=[{'type':'source_component','source_component_id':'c','name':'Q_IN',
                   'manufacturer_part_number':'FET'},
                  {'type':'source_net','subcircuit_connectivity_map_key':'n','name':'DRAIN'}]
            data += [{'type':'source_port','source_port_id':f'p{i}','source_component_id':'c',
                      'pin_number':i,'name':'D','subcircuit_connectivity_map_key':'n'}
                     for i in range(1,6)]
            path=root/'circuit.json';path.write_text(json.dumps(data))
            comps,_=sch.load_model(path,overrides={'FET':'test:FET'},
                part_authority=sch.load_part_authority(parts))
            self.assertEqual([p for p,_,_ in comps[0]['pins']],list('12345'))


if __name__ == '__main__': unittest.main()
