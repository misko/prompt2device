#!/usr/bin/python3
"""Deterministic isolated r10 patch against exact r9; CLI refills and checks.

No pcbnew mutation API. Output must be a new immediate child of this directory.
No schematic, library, rules or exclusions changes. Run from any directory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'projects/crow-array/order-readiness/quote-draft/r9-2c8p-home-clock/native/pcb/carrier'
SOURCE_HASH = 'ddc5f5b1c3cba999db77b1e2a0a8dd24f004579ec825ccec991169a0af3aa099'
BASE = Path(__file__).resolve().parent
PATHS = {
    '/VIN12': [(188,15.2),(182.5,15.2),(179.5,12.2),(179.5,9.455)],
    '/FUSED12': [(179.5,4.545),(179.5,2.5),(192.5,2.5),(194.5,4.5),(194.5,15.1),(190,19.6)],
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def nodes(text):
    starts = [m.start()+1 for m in re.finditer(r'\n\t\([a-z_]+', text)]
    return [(s, starts[i+1] if i+1<len(starts) else text.rfind('\n)'))
            for i,s in enumerate(starts)]

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='candidate1')
    parser.add_argument('--preserve-cooling',action='store_true',
                        help='Causal repair: reconnect left cooling lobe and extend top-right copper')
    parser.add_argument('--jack-anchor-y',type=float,choices=(15.2,14.7),default=15.2,
                        help='14.7 is separately authorized D1 mechanical-margin repair')
    a=parser.parse_args()
    out=BASE/a.output
    assert out.parent==BASE and not out.exists(), 'new immediate child output only'
    assert sha(SOURCE/'carrier.kicad_pcb')==SOURCE_HASH
    shutil.copytree(SOURCE,out/'native/pcb/carrier')
    dest=out/'native/pcb/carrier/carrier.kicad_pcb'
    text=dest.read_text()
    paths={net:list(points) for net,points in PATHS.items()}
    shift=a.jack_anchor_y-15.2
    paths['/VIN12']=[(x,y+shift) if i<3 else (x,y) for i,(x,y) in enumerate(paths['/VIN12'])]
    edits=[]; removed=[]
    for start,end in nodes(text):
        node=text[start:end]
        if node.startswith('\t(footprint "Connector_BarrelJack:BarrelJack_CUI_PJ-102AH_Horizontal"'):
            assert '(property "Reference" "J1"' in node
            for old,new,count in [
                ('(at 188 2.2)',f'(at 188 {a.jack_anchor_y:g} 180)',1),
                ('(at 0 0)','(at 0 0 180)',1),
                ('(at 0 6)','(at 0 6 180)',1),
                ('(at 4.7 3)','(at 4.7 3 180)',1),
            ]:
                assert node.count(old)==count,(old,node.count(old))
                node=node.replace(old,new)
            edits.append((start,end,node))
        elif node.startswith('\t(segment') and any(f'(net "{net}")' in node for net in PATHS):
            removed.append(node)
            edits.append((start,end,''))
    assert len(removed)==8 and len(edits)==9
    for start,end,new in reversed(edits): text=text[:start]+new+text[end:]
    if a.preserve_cooling:
        for start,end in nodes(text):
            node=text[start:end]
            if node.startswith('\t(zone') and '(uuid "7d82bcca-b1ed-4560-904b-a50284924689")' in node:
                assert node.count('(xy 186.2 10)')==1 and node.count('(xy 199 10)')==1
                node=node.replace('(xy 186.2 10)','(xy 186.2 5.5)').replace('(xy 199 10)','(xy 199 5.5)')
                text=text[:start]+node+text[end:]
                break
        else: raise AssertionError('missing inherited FUSED cooling zone')
    added=[]
    for net,coords in paths.items():
        for index,(start,end) in enumerate(zip(coords,coords[1:])):
            uid=uuid.uuid5(uuid.NAMESPACE_URL,'crow-r10-'+net+'-'+str(index))
            added.append(f'\t(segment\n\t\t(start {start[0]} {start[1]})\n\t\t(end {end[0]} {end[1]})\n\t\t(width 0.8)\n\t\t(layer "F.Cu")\n\t\t(net "{net}")\n\t\t(uuid "{uid}")\n\t)\n')
    if a.preserve_cooling:
        coords=[(179.5,4.545),(177.3,6.745),(177.3,11.2),(178.5,12.4)]
        for index,(start,end) in enumerate(zip(coords,coords[1:])):
            uid=uuid.uuid5(uuid.NAMESPACE_URL,'crow-r10-FUSED-cooling-'+str(index))
            added.append(f'\t(segment\n\t\t(start {start[0]} {start[1]})\n\t\t(end {end[0]} {end[1]})\n\t\t(width 0.8)\n\t\t(layer "F.Cu")\n\t\t(net "/FUSED12")\n\t\t(uuid "{uid}")\n\t)\n')
    pos=text.rfind('\n)')
    text=text[:pos]+'\n'+''.join(added)+text[pos:]
    dest.write_text(text)
    record={'source_sha256':SOURCE_HASH,'source_resources':{
        str(f.relative_to(SOURCE)):sha(f) for f in SOURCE.rglob('*') if f.is_file()},
        'jack':{'anchor_mm':[188,a.jack_anchor_y],'angle_deg':180,'body_center_mm':[188,a.jack_anchor_y-6.5],
                'mouth_y_mm':a.jack_anchor_y-13.7,'mouth_direction_native':'-Y'},
        'removed_segment_nodes':removed,'added_segment_nodes':added,'paths_mm':paths,
        'preserve_cooling_repair':a.preserve_cooling}
    (out/'patch-record.json').write_text(json.dumps(record,indent=2)+'\n')
    command=['kicad-cli','pcb','drc','--format','json','--severity-all',
             '--all-track-errors','--schematic-parity','--refill-zones','--save-board',
             '--output',str(out/'drc.json'),str(dest)]
    result=subprocess.run(command,capture_output=True,text=True)
    (out/'drc-command.json').write_text(json.dumps({'command':command,
        'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2)+'\n')
    result.check_returncode()
    drc=json.loads((out/'drc.json').read_text())
    assert not drc['ignored_checks']
    assert all(not drc[key] for key in ('violations','unconnected_items','schematic_parity'))
    subprocess.run(['/usr/bin/python3',str(ROOT/'vnext/tools/routing_geometry.py'),
        str(dest),str(out/'routing-geometry.json'),'--annulus-gap','.15'],check=True)
    geometry=json.loads((out/'routing-geometry.json').read_text())
    assert not geometry['via_drill_smd_overlaps'] and not geometry['via_annulus_smd_gap_findings']
    print(dest)

if __name__=='__main__': main()
