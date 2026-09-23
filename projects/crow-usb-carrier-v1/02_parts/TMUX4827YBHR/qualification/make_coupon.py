import pcbnew as p
import json
from pathlib import Path
root=Path(__file__).parent
MM=p.FromMM
V=lambda x,y:p.VECTOR2I(MM(x),MM(y))
b=p.BOARD();b.SetCopperLayerCount(4)
netnames={'A1':'NC_A_P','A2':'AUDIO_EN','A3':'NC_A_N','B1':'ADC_P','B2':'GND','B3':'ADC_N','C1':'FILTER_P','C2':'5V_LDO_HOLD','C3':'FILTER_N'}
nets={}
for name in netnames.values():
 n=p.NETINFO_ITEM(b,name);b.Add(n);nets[name]=n
f=p.FOOTPRINT(b);f.SetReference('U_ISO1');f.SetValue('TMUX4827YBHR');f.SetPosition(V(20,20))
b.Add(f);f.Reference().SetVisible(False);f.Value().SetVisible(False)
for row,y in zip('ABC',[-0.4,0,0.4]):
 for col,x in zip('123',[-0.4,0,0.4]):
  pin=row+col; pad=p.PAD(f);pad.SetName(pin);pad.SetAttribute(p.PAD_ATTRIB_SMD);pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetPosition(V(20+x,20+y));pad.SetSize(V(0.35 if pin=='B2' else 0.25,0.35 if pin=='B2' else 0.25));pad.SetLayerSet(p.LSET.FrontMask());pad.SetNet(nets[netnames[pin]]);
  if pin=='B2':
   pad.SetLocalSolderMaskMargin(MM(-0.05));pad.SetLocalSolderPasteMargin(MM(-0.05))
  f.Add(pad)
# Eight outward copper launches, no track passing between adjacent balls.
ends={'A1':(19.6,18.9),'A2':(20,18.9),'A3':(20.4,18.9),'B1':(18.9,20),'B3':(21.1,20),'C1':(19.6,21.1),'C2':(20,21.1),'C3':(20.4,21.1)}
for pin,(ex,ey) in ends.items():
 row,col=pin[0],pin[1]; sx=20+{'1':-0.4,'2':0,'3':0.4}[col]; sy=20+{'A':-0.4,'B':0,'C':0.4}[row]
 tp=p.FOOTPRINT(b);tp.SetReference('TP_'+pin);tp.SetValue(netnames[pin]);tp.SetPosition(V(ex,ey));tp.Reference().SetVisible(False);tp.Value().SetVisible(False);b.Add(tp)
 q=p.PAD(tp);q.SetName('1');q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetShape(p.PAD_SHAPE_CIRCLE);q.SetPosition(V(ex,ey));q.SetSize(V(0.25,0.25));q.SetLayerSet(p.LSET.FrontMask());q.SetNet(nets[netnames[pin]]);tp.Add(q)
 t=p.PCB_TRACK(b);t.SetStart(V(sx,sy));t.SetEnd(V(ex,ey));t.SetWidth(MM(0.09));t.SetLayer(p.F_Cu);t.SetNet(nets[netnames[pin]]);b.Add(t)
v=p.PCB_VIA(b);v.SetPosition(V(20,20));v.SetWidth(MM(0.35));v.SetDrill(MM(0.20));v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(nets['GND']);v.SetPrimaryDrillFilledFlag(True);v.SetPrimaryDrillCappedFlag(True);b.Add(v)
tp=p.FOOTPRINT(b);tp.SetReference('TP_GND');tp.SetValue('GND');tp.SetPosition(V(22,20));tp.Reference().SetVisible(False);tp.Value().SetVisible(False);b.Add(tp)
q=p.PAD(tp);q.SetName('1');q.SetAttribute(p.PAD_ATTRIB_SMD);q.SetShape(p.PAD_SHAPE_CIRCLE);q.SetPosition(V(22,20));q.SetSize(V(0.4,0.4));q.SetLayerSet(p.LSET.BackMask());q.SetNet(nets['GND']);tp.Add(q)
t=p.PCB_TRACK(b);t.SetStart(V(20,20));t.SetEnd(V(22,20));t.SetWidth(MM(0.09));t.SetLayer(p.B_Cu);t.SetNet(nets['GND']);b.Add(t)
for a,c in [((17.0,17.0),(23.0,17.0)),((23.0,17.0),(23.0,23.0)),((23.0,23.0),(17.0,23.0)),((17.0,23.0),(17.0,17.0))]:
 s=p.PCB_SHAPE(b);s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(V(*a));s.SetEnd(V(*c));s.SetWidth(MM(0.05));s.SetLayer(p.Edge_Cuts);b.Add(s)
p.SaveBoard(str(root/'coupon.kicad_pcb'),b)
# Minimal project-specific physical rules: selected Crow advanced4L copper floor (0.09) and JLC BGA spacing (0.10).
pr={'net_settings':{'classes':[{'name':'Default','clearance':0.10,'track_width':0.09,'via_diameter':0.35,'via_drill':0.20,'microvia_diameter':0.25,'microvia_drill':0.15,'diff_pair_gap':0.1,'diff_pair_width':0.09,'diff_pair_via_gap':0.1,'wire_width':6,'bus_width':12,'line_style':0,'pcb_color':'rgba(0, 0, 0, 0.000)','schematic_color':'rgba(0, 0, 0, 0.000)'}], 'netclass_patterns':[]},'board':{'design_settings':{'rules':{'min_clearance':0.09,'min_track_width':0.09,'min_via_diameter':0.25,'min_through_hole_diameter':0.15,'min_via_annular_width':0.075,'min_hole_clearance':0.10,'min_hole_to_hole':0.25,'solder_mask_to_copper_clearance':0.0}}}}
(root/'coupon.kicad_pro').write_text(json.dumps(pr,indent=2))
