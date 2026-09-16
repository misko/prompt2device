"""Evaluate JSX declarations, not tscircuit's producer or generated geometry.

The native baseline supplies only unchanged NC names and legacy footprint/value
spelling. Every connected pin comes from the live TSX; added parts resolve their
exact dossier footprint. This source-test adapter never writes a netlist/board.
Full native regeneration/parity remains mandatory after source correction.
"""
import functools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import yaml

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT.parents[1] / 'skills/kicad-pcb/scripts'))
from generate_board_generic import parse_netlist as parse_baseline

@functools.lru_cache()
def source_rows():
    script = '''
globalThis.React={createElement:(type,props,...children)=>({type,props:{...props,children}}),Fragment:"fragment"};
const m=await import(SOURCE);const rows=[];
function walk(v){if(Array.isArray(v)){v.forEach(walk);return;}
 if(!v||typeof v!=="object")return;
 if(typeof v.type==="function"){walk(v.type(v.props));return;}
 if(v.props?.name&&["chip","resistor","capacitor","testpoint"].includes(v.type))
 rows.push({type:v.type,...v.props,children:undefined});walk(v.props?.children);}
walk(m.default());console.log(JSON.stringify(rows));
'''.replace('SOURCE', json.dumps(str(PROJECT/'03_tscircuit/src/crow_audio_carrier_v1.tsx')))
    return json.loads(subprocess.check_output([shutil.which('bun'), '--eval', script], text=True, timeout=30))

@functools.lru_cache()
def inventory():
    old_comps, old_pins, old_extra = parse_baseline(PROJECT/'06_build/netlists/crow_audio_carrier_v1.net')
    parts={d['mpn']:d for p in (PROJECT/'02_parts').glob('*/part.yaml') for d in [yaml.safe_load(p.read_text())]}
    comps={};pins={}
    for row in source_rows():
        ref=row['name'];mpn=row.get('manufacturerPartNumber')
        value=str(row.get('resistance',row.get('capacitance',mpn or 'TP')))
        fpid=parts[mpn]['footprint'] if mpn in parts else old_comps[ref][0]
        comps[ref]=(fpid,value)
        for (r,p),net in old_pins.items():
            if r==ref and ref!='U_LDO' and net.startswith('unconnected-'):pins[(r,p)]=net
        if ref=='U_LDO':
            for pin in ('4','6'):pins[(ref,pin)]=f'unconnected-U_LDO-{pin}'
        for pin,net in row.get('connections',{}).items():
            assert pin.startswith('pin') and net.startswith('net.'),(ref,pin,net)
            net=net[4:]
            if len(net)>1 and net[0]=='N' and net[1].isdigit():net=net[1:]
            pins[(ref,pin[3:])]=net
    assert len(comps)==len(source_rows()) and len(comps)>300
    return comps,pins,old_extra

def parse_netlist(_path):
    """Compatibility signature for source-only geometry tests."""
    return inventory()
