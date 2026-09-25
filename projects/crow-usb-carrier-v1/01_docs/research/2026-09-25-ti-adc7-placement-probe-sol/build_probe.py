import pcbnew as p, yaml, json, hashlib
from pathlib import Path
src=Path('projects/crow-usb-carrier-v1/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/04_kicad/crow_carrier.kicad_pcb')
b=p.LoadBoard(str(src)); pos={'Y_AUDIO':(195.5,118.0),'C_ADC_I2C_A':(183.0,104.0),'C_ADC_CLOCK_OK':(163.5,90.0)}
fixed=yaml.safe_load(open('projects/crow-usb-carrier-v1/06_build/ti_unrouted_diagnostic/20260925T051055Z-source-packet/project/03_src/rules/p1_corridor_requirements.yaml'))['p1_fixed_refs']
def rect(f):
 z=f.GetBoundingBox(True,True);return [v/1e6 for v in (z.GetLeft(),z.GetTop(),z.GetRight(),z.GetBottom())]
def hit(a,c):return a[0]<c[2] and a[2]>c[0] and a[1]<c[3] and a[3]>c[1]
def pairs(board):
 f={x.GetReference():x for x in board.GetFootprints()}; keys=list(f);return {(keys[i],keys[j]) for i in range(len(keys)) for j in range(i+1,len(keys)) if hit(rect(f[keys[i]]),rect(f[keys[j]]))}
def pad_signature(board):
 return {f.GetReference():sorted((pad.GetNumber(),pad.GetNetname()) for pad in f.Pads()) for f in board.GetFootprints()}
base=pairs(b); baseline_pads=pad_signature(b); basepos={f.GetReference():(f.GetPosition().x,f.GetPosition().y,f.GetOrientationDegrees()) for f in b.GetFootprints() if f.GetReference() in fixed}; bsha=hashlib.sha256(src.read_bytes()).hexdigest()
if bsha != '8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10' or len(fixed) != 27:
 raise SystemExit('exact TI board or fixed-reference set drift')
for f in b.GetFootprints():
 if f.GetReference() in pos:f.SetPosition(p.VECTOR2I(*(round(v*1e6) for v in pos[f.GetReference()])))
out=Path('/tmp/crow-adc7-isolated-move.kicad_pcb');p.SaveBoard(str(out),b)
c=p.LoadBoard(str(out)); ff={f.GetReference():f for f in c.GetFootprints()}; now=pairs(c)
port={'adc7':[166,83.9,167.12,85], 'adc8':[190.5,83.9,191.62,85], 'tdm_neck':[188,94,190,99.84]}
report={'source_board_sha256':bsha,'copy_board_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'copy_path':str(out),'fixed_count':len(fixed),'fixed_unchanged':all((ff[k].GetPosition().x,ff[k].GetPosition().y,ff[k].GetOrientationDegrees())==basepos[k] for k in fixed),'pad_net_identities_unchanged':pad_signature(c)==baseline_pads,'new_full_bbox_overlap_pairs':sorted([list(x) for x in now-base]),'moves':{k:{'origin_mm':pos[k],'full_bbox_mm':rect(ff[k])} for k in pos},'port_target_intersections':{k:[ref for ref in pos if hit(rect(ff[ref]),v)] for k,v in port.items()},'all_port_obstacles':{k:sorted([ref for ref,f in ff.items() if hit(rect(f),v)]) for k,v in port.items()},'baseline_pairs':len(base),'copy_pairs':len(now)}
if not report['fixed_unchanged'] or not report['pad_net_identities_unchanged'] or report['new_full_bbox_overlap_pairs'] or report['all_port_obstacles']['adc7'] or report['all_port_obstacles']['adc8']:
 raise SystemExit('isolated geometry witness failed')
print(json.dumps(report,indent=2))
