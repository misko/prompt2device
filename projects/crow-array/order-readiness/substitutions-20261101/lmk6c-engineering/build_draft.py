"""Isolated UNACCEPTED native TI-clock draft. Never emits an upload package.

Run with /usr/bin/python3 -B build_draft.py --output NEW_DIRECTORY.
Preserves r7; does not invoke acceptance or ordering interfaces.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys
import pcbnew as p

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
import substitute_quote as q
import r7_quote


def xy(v): return (round(p.ToMM(v.x),6),round(p.ToMM(v.y),6))
def vec(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))


def schematic(text):
    changes=[]
    for node in q.forms(text):
        if q.atom(node)!='symbol': continue
        props={json.loads(q.atom(c,1)):c[2] for c in node if isinstance(c,list) and q.atom(c)=='property' and len(c)>=3}
        if 'MPN' not in props: continue
        ref=json.loads(props['Reference'].group())
        if ref not in ('X1','C4'):
            name=q.atom(node,1)
            if not name.startswith('"'):continue
            ref=json.loads(name).split(':')[-1]
        if ref not in ('X1','C4'):continue
        fields=({'MPN':'LMK6CE012288CDLFR','Manufacturer':'Texas Instruments',
                 'Value':'LMK6CE012288CDLFR','Footprint':'CrowPhysical:TI_LMK6C_DLF0004A'}
                if ref=='X1' else {'MPN':'CL21B105KBFNNNE','Value':'1uF 50V X7R 10% CLOCK'})
        for name,value in fields.items():
            tok=props[name];changes.append((tok.start(),tok.end(),json.dumps(value)))
    for a,b,value in sorted(changes,reverse=True):text=text[:a]+value+text[b:]
    return text


def build(out):
    assert not out.exists()
    r7_quote.verify(r7_quote.OUT)
    shutil.copytree(r7_quote.OUT/'native',out/'native')
    # No copied Gerbers/BOM/CPL/manifests: this is not an upload revision.
    parent=out/'native/pcb/carrier'
    for lib in (parent/'CrowPhysical.pretty',out/'native/schematic/CrowPhysical.pretty'):
        lib.mkdir(exist_ok=True)
        shutil.copyfile(HERE/'TI_LMK6C_DLF0004A.kicad_mod',lib/'TI_LMK6C_DLF0004A.kicad_mod')
    sch=out/'native/schematic/crow-carrier.kicad_sch'
    for file in (sch,out/'native/schematic/CrowCarrier.kicad_sym'):
        file.write_text(schematic(file.read_text()))
    shutil.copyfile(sch,parent/'carrier.kicad_sch')
    board=p.LoadBoard(str(parent/'carrier.kicad_pcb'))
    fps={f.GetReference():f for f in board.GetFootprints()}
    old=fps['X1']; oldnets={d.GetNumber():d.GetNet() for d in old.Pads()}
    new=p.FootprintLoad(str(parent/'CrowPhysical.pretty'),'TI_LMK6C_DLF0004A')
    new.SetFPID(p.LIB_ID('CrowPhysical','TI_LMK6C_DLF0004A'))
    new.SetFields(old.GetFieldsText());new.SetReference('X1')
    for field in new.GetFields():
        if field.GetName()!='Reference':field.SetVisible(False)
    new.SetValue('LMK6CE012288CDLFR')
    new.SetField('MPN','LMK6CE012288CDLFR');new.SetField('Manufacturer','Texas Instruments')
    new.SetPath(old.GetPath())
    new.SetPosition(vec(86,85.5));new.SetOrientationDegrees(90)
    new.Reference().SetPosition(vec(86,83.3));new.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    board.Remove(old);board.Add(new)
    for d in new.Pads():
        if d.GetNumber():d.SetNet(oldnets[d.GetNumber()])
    cap=fps['C4'];cap.SetPosition(vec(83.46,82.9));cap.SetOrientationDegrees(0)
    cap.SetValue('1uF 50V X7R 10% CLOCK');cap.SetField('MPN','CL21B105KBFNNNE')
    cap.Reference().SetPosition(vec(82.0,81.5));cap.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
    # Remove only original terminal escapes which are superseded below.
    terminal_points={(88.54,87.6),(88.54,83.4),(83.46,87.6),(83.46,77.05),(83.46,78.95)}
    for t in list(board.GetTracks()):
        if isinstance(t,p.PCB_VIA):continue
        if xy(t.GetStart()) in terminal_points or xy(t.GetEnd()) in terminal_points:board.Remove(t)
    nets={n:board.FindNet(n) for n in ('/GND','/3V3','/MCLK_SRC')}
    def track(net,a,b,width=.3):
        t=p.PCB_TRACK(board);t.SetNet(nets[net]);t.SetLayer(p.F_Cu)
        t.SetStart(vec(*a));t.SetEnd(vec(*b));t.SetWidth(p.FromMM(width));board.Add(t)
    def via(net,at):
        v=p.PCB_VIA(board);v.SetNet(nets[net]);v.SetPosition(vec(*at))
        v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetLayerPair(p.F_Cu,p.B_Cu);board.Add(v)
    track('/MCLK_SRC',(86.825,84.75),(88.4,82.8),.15)
    track('/3V3',(85.175,86.25),(83.46,89.15))
    track('/3V3',(83.46,83.4),(83.46,84.1))
    track('/3V3',(83.46,84.1),(85.175,84.75))
    track('/3V3',(82.51,82.9),(83.46,83.4))
    track('/GND',(84.41,82.9),(85.7,82.9));via('/GND',(85.7,82.9))
    track('/GND',(86.825,86.25),(87.7,86.25),.4);via('/GND',(87.7,86.25))
    track('/GND',(87.7,86.25),(90.2,87.6))
    # Thermal/return spreading for the higher-current oscillator; no via in pad.
    zone=p.ZONE(board);zone.SetLayer(p.F_Cu);zone.SetNet(nets['/GND'])
    zone.SetLocalClearance(p.FromMM(.15));zone.SetMinThickness(p.FromMM(.15))
    zone.SetPadConnection(p.ZONE_CONNECTION_FULL);zone.SetAssignedPriority(10)
    outline=p.VECTOR_VECTOR2I()
    for x,y in ((86.825,85.95),(89.7,85.95),(89.7,88.5),(86.825,88.5)):
        outline.append(vec(x,y))
    zone.AddPolygon(outline)
    board.Add(zone);via('/GND',(89.0,87.8))
    p.SaveBoard(str(parent/'carrier.kicad_pcb'),board)
    report=dict(status='UNACCEPTED_ENGINEERING_DRAFT_DO_NOT_UPLOAD',
        production_ready=False,purchase_authorized=False,
        base_manifest_sha256=q.sha(r7_quote.OUT/'manifest.json'),
        author_sha256=q.sha(Path(__file__)),footprint_sha256=q.sha(HERE/'TI_LMK6C_DLF0004A.kicad_mod'),
        scope='X1 replacement and C4 bypass relocation/value; pod unchanged; no quote files generated',
        missing=['native/ERC/DRC/parity/refill','changed geometry clock analysis',
                 'source/ramp and thermal model review','affected upstream acceptance','complete derivative exports'])
    (out/'draft.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();print(json.dumps(build(args.output),indent=2))
