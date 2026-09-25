#!/usr/bin/env python3
"""Reproduce a local, non-credit TDM DATA return opportunity."""
import argparse, hashlib, json, shutil, subprocess, tempfile
from collections import Counter
from pathlib import Path
import pcbnew, yaml

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
BASE = PROJECT / '06_build/prototype_board_diagnostic/current-ti-mounting-expanded-locked-20260925/04_kicad/crow_carrier.kicad_pcb'
P1 = PROJECT / '01_docs/research/2026-09-25-ti-expanded-locked-p1-sol/p1_requirements.yaml'
BASE_SHA = 'fe8d2c9a9922eeab2371d0187da9407ac590687a77b03a8a099c35a75b5ddd16'
P1_SHA = 'e8ff456de1868386890dbb5413bb20dc054b5d711b7c9b97d8b02a6b4695ae92'
START, END, VIA = (200.8375, 97.6), (199.805, 97.6), (197.2, 98.2)
GND_PATH, WIDTH = ((197.84, 99.1), (197.55, 98.5), VIA), 0.15

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def pos(point): return pcbnew.VECTOR2I(pcbnew.FromMM(point[0]), pcbnew.FromMM(point[1]))
def mm(point): return [round(pcbnew.ToMM(point.x), 4), round(pcbnew.ToMM(point.y), 4)]
def types(report): return dict(sorted(Counter(x['type'] for x in report['violations']).items()))
def track(board, net, start, end):
    x = pcbnew.PCB_TRACK(board); x.SetLayer(pcbnew.F_Cu); x.SetWidth(pcbnew.FromMM(WIDTH))
    x.SetNet(board.FindNet(net)); x.SetStart(pos(start)); x.SetEnd(pos(end)); board.Add(x)
def run_drc(folder, stem):
    report = folder / (stem + '.json')
    subprocess.run(['kicad-cli','pcb','drc','--refill-zones','--format','json','-o',str(report),str(folder/(stem+'.kicad_pcb'))], check=True, capture_output=True, text=True)
    return json.loads(report.read_text())

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--write-result', type=Path, metavar='NEW_PATH',
                    help='write the JSON to a new path; refuses an existing path')
args = parser.parse_args()
if args.write_result is not None and args.write_result.exists():
    raise SystemExit(f'refusing to overwrite existing result path: {args.write_result}')
if sha(BASE) != BASE_SHA or sha(P1) != P1_SHA: raise SystemExit('bound input drift')
fixed = yaml.safe_load(P1.read_text())['p1_fixed_refs']
if len(fixed) != 33: raise SystemExit('P1 fixed-reference denominator drift')
board = pcbnew.LoadBoard(str(BASE)); fps = {x.GetReference(): x for x in board.GetFootprints()}
fixed_poses = {ref:mm(fps[ref].GetPosition()) for ref in fixed}
pad107 = next(x for x in fps['U_XU'].Pads() if x.GetNumber() == '107')
c106gnd = next(x for x in fps['C_XU_VDD_106'].Pads() if x.GetNumber() == '2')
if pad107.GetNetname() != 'TDM_DATA_1V8' or mm(pad107.GetPosition()) != list(START): raise SystemExit('U_XU.107 drift')
if c106gnd.GetNetname() != 'GND' or mm(c106gnd.GetPosition()) != [198.12,99.1]: raise SystemExit('C106 GND drift')
track(board, 'TDM_DATA_1V8', START, END)
via = pcbnew.PCB_VIA(board); via.SetPosition(pos(VIA)); via.SetNet(board.FindNet('GND')); via.SetWidth(pcbnew.FromMM(.60)); via.SetDrill(pcbnew.FromMM(.30)); via.SetLayerPair(pcbnew.F_Cu,pcbnew.B_Cu); board.Add(via)
track(board, 'GND', GND_PATH[0], GND_PATH[1]); track(board, 'GND', GND_PATH[1], GND_PATH[2])
if {ref:mm(fps[ref].GetPosition()) for ref in fixed} != fixed_poses: raise SystemExit('P1 fixed ref moved')
zones = [x for x in board.Zones() if x.GetNetname() == 'GND' and x.IsOnLayer(pcbnew.In1_Cu)]
if len(zones) != 1: raise SystemExit('In1 GND zone denominator drift')
pcbnew.ZONE_FILLER(board).Fill(zones); fill = zones[0].GetFilledPolysList(pcbnew.In1_Cu)
inside = [i for i in range(fill.OutlineCount()) if fill.Contains(pos(VIA),i)]
if len(inside) != 1: raise SystemExit('via outside filled In1 GND')
with tempfile.TemporaryDirectory(prefix='crow-expanded-tdm-') as temp:
    temp = Path(temp)
    for suffix in ('kicad_pcb','kicad_pro','kicad_dru'):
        shutil.copyfile(BASE.with_suffix('.'+suffix), temp/('baseline.'+suffix))
    shutil.copyfile(BASE.parent/'fp-lib-table',temp/'fp-lib-table')
    pcbnew.SaveBoard(str(temp/'candidate.kicad_pcb'),board)
    for suffix in ('kicad_pro','kicad_dru'): shutil.copyfile(BASE.with_suffix('.'+suffix),temp/('candidate.'+suffix))
    before, after = run_drc(temp,'baseline'),run_drc(temp,'candidate')
new = Counter(x['type'] for x in after['violations']) - Counter(x['type'] for x in before['violations'])
bad = {k:v for k,v in new.items() if k in {'clearance','track_width','shorting_items','hole_clearance','via_dangling'}}
if bad: raise SystemExit('new native violation: '+str(bad))
result = {'schema':1,'kind':'expanded-tdm-data-local-return-opportunity','status':'P2_GEOMETRY_ONLY','p1_accepted':False,'p2_accepted':False,'routing_realized':False,'input_hashes':{'board':sha(BASE),'p1_fixed_refs':sha(P1),'project':sha(BASE.with_suffix('.kicad_pro')),'rules':sha(BASE.with_suffix('.kicad_dru'))},'fixed_reference_count':len(fixed),'fixed_reference_poses_unchanged':True,'connector_geometry_unchanged':True,'data_stub':{'net':'TDM_DATA_1V8','pad':'U_XU.107','layer':'F.Cu','width_mm':WIDTH,'start_mm':START,'end_mm':END,'length_mm':1.0325},'gnd_transition':{'source_pad':'C_XU_VDD_106.2','via_mm':VIA,'via_diameter_mm':.60,'via_drill_mm':.30,'fcu_segments_mm':list(GND_PATH),'in1_filled_polygon':inside[0]},'drc':{'baseline_types':types(before),'candidate_types':types(after),'new_types':dict(new),'baseline_unconnected':len(before['unconnected_items']),'candidate_unconnected':len(after['unconnected_items'])},'limitations':['DATA end intentionally dangling; no route','local plane overlap is not continuous-return proof','no timing, impedance, crosstalk, via-inductance, source/receiver, USB, P1, or P2 credit']}
serialized = json.dumps(result, indent=2, sort_keys=True) + '\n'
if args.write_result is not None:
    args.write_result.parent.mkdir(parents=True, exist_ok=True)
    args.write_result.write_text(serialized)
print(serialized, end='')
