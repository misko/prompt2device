from pathlib import Path
import argparse,hashlib,math
import pcbnew
P=Path(__file__).resolve().parents[2]
SOURCES={"D1":("02_parts/S1M-E3-61T/Vishay_S1_88711.pdf","49c11fe1f333fda1bcdacc72754927dda4ee5bf977bf88d3c46eb1cd6ffe9277",.945,2.640,.825),"D2":("02_parts/SMBJ15A/Littelfuse_SMBJ_v4_2025-07-04.pdf","d7df155be4b1f612085401e8c946f065e284d65a0e7de22b9225a7b73946e51b",1.085,2.795,1.100)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument("ref",choices=sorted(SOURCES));ap.add_argument("--project",type=Path,default=P);ap.add_argument("--hostile-control",action="store_true");a=ap.parse_args()
 path,digest,inner,outer,half=SOURCES[a.ref];assert hashlib.sha256((a.project/path).read_bytes()).hexdigest()==digest
 b=pcbnew.LoadBoard(str(a.project/"04_kicad/crow_mic_pod_v3.kicad_pcb"));f=b.FindFootprintByReference(a.ref);assert f
 f.SetOrientationDegrees(0);f.SetPosition(pcbnew.VECTOR2I(0,0));pads={p.GetNumber():p for p in f.Pads()};assert set(pads)=={"1","2"};values=[]
 for n,p in pads.items():
  assert p.GetShape() in (pcbnew.PAD_SHAPE_RECT,pcbnew.PAD_SHAPE_ROUNDRECT) and p.GetOrientationDegrees()%180==0
  if a.hostile_control:p.SetSize(pcbnew.VECTOR2I(100000,100000))
  cx,cy=p.GetPosition().x/1e6,p.GetPosition().y/1e6;sx,sy=p.GetSize().x/1e6,p.GetSize().y/1e6;r=p.GetRoundRectCornerRadius()/1e6 if p.GetShape()==pcbnew.PAD_SHAPE_ROUNDRECT else 0
  for x in ((-outer,-inner) if n=="1" else (inner,outer)):
   for y in (-half,half):
    qx=abs(x-cx)-(sx/2-r);qy=abs(y-cy)-(sy/2-r);values.append(-(math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-r))
 result=min(values);print(f"{result:.6f}");return 0 if result>=0 else 1
if __name__=="__main__":raise SystemExit(main())
