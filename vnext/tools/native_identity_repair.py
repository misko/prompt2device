"""Constrained native namespace/board-only migration; never repairs connectivity.

Only emit a candidate after exact pin membership proves a bijective net rename.
Preserve geometry by reversing ONLY those metadata changes on a reloaded copy
and requiring full normalized native serialization equality. Re-run raw KiCad
parity separately; this script is not acceptance or a report waiver.
"""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
import xml.etree.ElementTree as ET

import placement as p
import routing as r


def repair(board_path, netlist, output):
    board_path, netlist, output=map(Path,(board_path,netlist,output))
    p.need(not output.exists(),'refusing existing migration output')
    p.need(board_path.is_file() and netlist.is_file(),'native inputs required')
    p.need(not output.resolve().is_relative_to(board_path.parent.resolve()),
           'output must be outside source resource directory')
    p.need(not any(x.is_symlink() for x in board_path.parent.rglob('*')),'linked native resource')
    source_hash=p.sha(board_path);netlist_hash=p.sha(netlist)
    board=p.pcb.LoadBoard(str(board_path));tree=ET.parse(netlist)
    all_components=tree.findall('./components/comp')
    p.need(len({c.get('ref') for c in all_components})==len(all_components),'duplicate schematic reference')
    excluded={c.get('ref') for c in all_components if
              any(v.get('name')=='exclude_from_board' for v in c.findall('property'))}
    components={c.get('ref'):c for c in all_components if c.get('ref') not in excluded}
    p.need(components,'nonzero native schematic components required')
    expected={};nc_pins=set()
    for net in tree.findall('./nets/net'):
        nodes=net.findall('node');name=net.get('name')
        for node in nodes:
            if node.get('ref') in excluded:continue
            key=(node.get('ref'),node.get('pin'))
            p.need(key not in expected,'duplicate schematic pin membership')
            nc=(name.startswith('unconnected-') and len(nodes)==1 and
                'no_connect' in node.get('pintype',''))
            expected[key]=name
            if nc:nc_pins.add(key)
    parts=list(board.GetFootprints());refs=[f.GetReference() for f in parts]
    p.need(len(set(refs))==len(refs) and set(components)<=set(refs),'reference census differs')
    renames={};seen=set();mounts={};nc_assignments={}
    for fp in parts:
        ref=fp.GetReference();pads=list(fp.Pads())
        if ref not in components:
            p.need(not fp.GetFPIDAsString() and pads and all(
                not pad.GetNumber() and not pad.GetNetname() and pad.GetAttribute()==p.pcb.PAD_ATTRIB_NPTH
                for pad in pads),'unexplained extra footprint: '+ref)
            mounts[ref]=fp.GetAttributes();continue
        c=components[ref]
        p.need(fp.GetValue()==c.findtext('value') and fp.GetFPIDAsString()==c.findtext('footprint'),
               'component identity differs: '+ref)
        for pad in pads:
            if not pad.GetNumber():
                p.need(pad.GetAttribute()==p.pcb.PAD_ATTRIB_NPTH and not pad.GetNetname(),'unnumbered electrical pad')
                continue
            key=(ref,pad.GetNumber());p.need(key in expected,'pad missing from native schematic')
            old=pad.GetNetname();new=expected[key];seen.add(key)
            if old=='' and key in nc_pins:
                nc_assignments[key]=new;continue
            p.need(old==new or (old and '/'+old==new),'not a namespace-only migration: '+str(key))
            p.need(old not in renames or renames[old]==new,'ambiguous namespace migration')
            renames[old]=new
    p.need(seen==set(expected),'schematic pin coverage differs')
    p.need(len(set(renames.values()))==len(renames),'net merge refused')
    renames={a:b for a,b in renames.items() if a!=b}
    p.need(not any(not item.GetNetname() for item in board.GetTracks()),
           'unassigned copper prevents isolated NC migration')
    output.mkdir(parents=True)
    shutil.copytree(board_path.parent,output/'native')
    candidate=output/'native'/board_path.name
    with tempfile.TemporaryDirectory(prefix='native-metadata-proof-') as directory:
        before=Path(directory)/'before.kicad_pcb';p.pcb.SaveBoard(str(before),board)
        for net in list(board.GetNetsByNetcode().values()):
            if net.GetNetname() in renames:net.SetNetname(renames[net.GetNetname()])
        isolated={name:p.pcb.NETINFO_ITEM(board,name) for name in nc_assignments.values()}
        for net in isolated.values():board.Add(net)
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                key=(fp.GetReference(),pad.GetNumber())
                if key in nc_assignments:pad.SetNet(isolated[nc_assignments[key]])
            if fp.GetReference() in mounts:
                fp.SetAttributes(fp.GetAttributes() | p.pcb.FP_BOARD_ONLY |
                                 p.pcb.FP_EXCLUDE_FROM_BOM | p.pcb.FP_EXCLUDE_FROM_POS_FILES)
        p.pcb.SaveBoard(str(candidate),board)
        restored=p.pcb.LoadBoard(str(candidate));inverse={b:a for a,b in renames.items()}
        for net in list(restored.GetNetsByNetcode().values()):
            if net.GetNetname() in inverse:net.SetNetname(inverse[net.GetNetname()])
        for fp in restored.GetFootprints():
            if fp.GetReference() in mounts:fp.SetAttributes(mounts[fp.GetReference()])
            for pad in fp.Pads():
                if (fp.GetReference(),pad.GetNumber()) in nc_assignments:pad.SetNetCode(0)
        after=Path(directory)/'restored.kicad_pcb';p.pcb.SaveBoard(str(after),restored)
        p.need(r.normalized(before)==r.normalized(after),'unintended native delta; candidate NOT accepted')
    p.need(p.sha(board_path)==source_hash and p.sha(netlist)==netlist_hash,'input mutated')
    result=dict(source_sha256=source_hash,netlist_sha256=netlist_hash,candidate_sha256=p.sha(candidate),
                renames=renames,mechanical_attributes_before=mounts,pin_membership=len(seen),
                isolated_nc_assignments={ref+'/'+number:name for (ref,number),name in nc_assignments.items()},
                complete_inverse_delta_verified=True,acceptance=False)
    (output/'migration.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('board','netlist','output'):parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(repair(args.board,args.netlist,args.output),indent=2))
