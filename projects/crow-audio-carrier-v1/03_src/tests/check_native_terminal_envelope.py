"""Rerunnable terminal-envelope evidence for independently reviewed Carrier lands.

Printed manufacturer dimensions and pin frames are independent review inputs,
not inferred from the target copper. Includes actual round-rectangle corners.
This grades nominal component registration with terminal dimensional extremes;
assembly placement/process tolerance and solder fillets remain separate.
"""
from pathlib import Path
import argparse,hashlib,math
import pcbnew
P=Path(__file__).resolve().parents[2]
SOURCES={'sma': {'path': '02_parts/B340A-13-F/B340A_DS30891_Rev19-2.pdf', 'sha256': '453cbd34d996482abd07ac694c4e2d812d26b1d679d05ee325acc5c3eeb79917'}, 'us1b': {'path': '02_parts/US1B-13-F/Diodes_US1A_US1M_DS16008_Rev11-2.pdf', 'sha256': 'd50b2773c0300d97a77f5125419098c8130ecaf967202a44be2b182de8a15c1f'}, 'smb': {'path': '02_parts/SMBJ15A/Littelfuse_SMBJ_v4_2025-07-04.pdf', 'sha256': 'd7df155be4b1f612085401e8c946f065e284d65a0e7de22b9225a7b73946e51b'}, 'lvc14': {'path': '02_parts/74LVC1G14GV,125/74LVC1G14_Rev19.pdf', 'sha256': 'b8f37c700d0fc8374de6d14f0e2caf310c34b480ffab9d63c69bb3b6defbebbf'}, 'lvc17': {'path': '02_parts/74LVC1G17GV,125/74LVC1G17.pdf', 'sha256': '3db133d57486306950ba1140ac13a8a0ea95509dcefb88db36c08423a819b163'}, 'ao': {'path': '02_parts/AO3401A/AOS_PO-00001N_SOT23.pdf', 'sha256': 'b6fac64d55f133ce74dd85ddddc618c3d5408e9531cb21e660f6a8ef3d8c5408'}, '2n': {'path': '02_parts/2N7002K-7/2N7002K_DS30896_Rev20-2.pdf', 'sha256': '669e5d68d6458e0879d7396416bdcdb3ef9966ea60f054773d4c891d735aa818'}}
REFS={"D_HOLD":"sma","D_BUCK_IN":"us1b","D_IN":"smb","U_DUMP":"lvc14","U_LDO_EN":"lvc14","U_OE":"lvc14","U_TDM_SCH":"lvc17","Q_PRE":"ao","Q_PRE_EN":"2n","Q_RST1":"2n"}

def terminal_boxes(kind):
    # Coordinates: native footprint-local x-right/y-down, manufacturer top view.
    if kind in ('sma','us1b','smb'):
        inner,outer,half=(.88,2.795,.815) if kind!='smb' else (1.085,2.795,1.1)
        return {'1':(-outer,-half,-inner,half),'2':(inner,-half,outer,half)}
    if kind in ('lvc14','lvc17'):
        centres={'1':(-1,-.95),'2':(-1,0),'3':(-1,.95),'4':(1,.95),'5':(1,-.95)}
        return {n:((-1.5 if x<0 else .65),y-.2,(-.65 if x<0 else 1.5),y+.2) for n,(x,y) in centres.items()}
    if kind=='ao':return {'1':(-1.5,-1.2,-.7,-.7),'2':(-1.5,.7,-.7,1.2),'3':(.7,-.25,1.5,.25)}
    if kind=='2n':return {'1':(-1.275,-1.28,-.6,-.635),'2':(-1.275,.635,-.6,1.28),'3':(.6,-.255,1.275,.255)}
    raise ValueError(kind)

def margin(fp,kind):
    fp.SetOrientationDegrees(0);fp.SetPosition(pcbnew.VECTOR2I(0,0))
    pads={p.GetNumber():p for p in fp.Pads() if p.GetNumber()};boxes=terminal_boxes(kind)
    assert set(pads)==set(boxes)
    values=[]
    for number,(x0,y0,x1,y1) in boxes.items():
        p=pads[number];assert p.GetShape() in (pcbnew.PAD_SHAPE_RECT,pcbnew.PAD_SHAPE_ROUNDRECT)
        assert p.GetOrientationDegrees()%180==0
        cx,cy=p.GetPosition().x/1e6,p.GetPosition().y/1e6
        sx,sy=p.GetSize().x/1e6,p.GetSize().y/1e6
        radius=p.GetRoundRectCornerRadius()/1e6 if p.GetShape()==pcbnew.PAD_SHAPE_ROUNDRECT else 0
        for x in (x0,x1):
            for y in (y0,y1):
                qx=abs(x-cx)-(sx/2-radius);qy=abs(y-cy)-(sy/2-radius)
                outside=math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-radius
                values.append(-outside)
    return min(values)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('ref',choices=sorted(REFS));ap.add_argument('--board',default=str(P/'04_kicad/crow_audio_carrier_v1.kicad_pcb'));ap.add_argument('--hostile-control',action='store_true');a=ap.parse_args()
    source=SOURCES[REFS[a.ref]];assert hashlib.sha256((P/source['path']).read_bytes()).hexdigest()==source['sha256']
    b=pcbnew.LoadBoard(a.board);fp=b.FindFootprintByReference(a.ref);assert fp
    if a.hostile_control:
        p=next(iter(fp.Pads()));p.SetSize(pcbnew.VECTOR2I(100000,100000))
    result=margin(fp,REFS[a.ref]);print(f'{result:.6f}')
    return 0 if result>=-1e-9 else 1
if __name__=='__main__':raise SystemExit(main())
