#!/usr/bin/env python3
"""Finite 0.05-mm first-via effective-shape screen; no native profile."""
import importlib.util,sys,tempfile,math
from pathlib import Path
sys.path.append('/usr/lib/python3/dist-packages')
import pcbnew as p
S=Path(__file__).resolve().parent.parent/'2026-09-25-ti-tps26625-placement-return-sol/probe.py'
spec=importlib.util.spec_from_file_location('s',S);s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)
with tempfile.TemporaryDirectory() as tmp:
 old=s.trial.GROUP['C_SPOKE_DVDT8'];s.trial.GROUP['C_SPOKE_DVDT8']=s.DVDT_POSE
 try: source,_=s.trial.generate(Path(tmp)/'source')
 finally:s.trial.GROUP['C_SPOKE_DVDT8']=old
 b=p.LoadBoard(str(source));s.trial.prior.add_candidate(b)
 added=[]
 for net,verts in [('GND',s.GND_CIN),('GND',s.GND_OUT),('SPOKE_RTN8',s.RTN_ILIM),('SPOKE_RTN8',s.RTN_DVDT),('SPOKE_RTN8',s.RTN_U3),('SPOKE_RTN8',s.RTN_U5)]:added+=s.path(b,net,verts,.2)
 added += [s.via(b,'GND',s.GND_CIN[-1]),s.via(b,'GND',s.GND_OUT[1])]
 added+=s.path(b,'N12V_PROTECTED',[(188.35,46.025),(188.35,44.0)],1.2)
 added+=s.path(b,'N12V_POD8',s.OUT,.5)
 # Other source-generated copper including ADC8N inspected in candidate gap scan.
 def cgap(shape,obj):
  sh=obj.GetEffectiveShape(p.F_Cu)
  return s.gap(shape,sh)
 pads=[(f.GetReference()+'.'+q.GetNumber(),q) for f in b.GetFootprints() for q in f.Pads() if q.IsOnLayer(p.F_Cu) and q.GetNetname()!='SPOKE_ILIM8']
 copper=[(q.GetNetname(),q) for q in b.GetTracks() if q.IsOnLayer(p.F_Cu) and q.GetNetname()!='SPOKE_ILIM8']
 res=[]
 for xi in range(19195,19236,5):
  x=xi/100
  for yi in range(4760,4806,5):
   y=yi/100
   v=s.via(b,'SPOKE_ILIM8',(x,y));sh=v.GetEffectiveShape(p.F_Cu)
   pg=sorted((g,name) for name,q in pads if (g:=cgap(sh,q)) is not None)
   tg=sorted((g,name) for name,q in copper if (g:=cgap(sh,q)) is not None)
   b.Remove(v)
   # launch geom and via separation from other pads; minor min GND check.
   t=s.track(b,'SPOKE_ILIM8',(191.4,48.0),(x,y),.2)
   lgs=sorted((g,name) for name,q in pads if (g:=cgap(t.GetEffectiveShape(p.F_Cu),q)) is not None)
   lgt=sorted((g,name) for name,q in copper if (g:=cgap(t.GetEffectiveShape(p.F_Cu),q)) is not None)
   b.Remove(t)
   blockers=sorted((g,name) for g,name in (pg[:5]+tg[:5]) if g<.35)
   launch=sorted((g,name) for g,name in (lgs[:5]+lgt[:5]) if g<.20)
   if not launch and all(g>=.2-1e-6 for g,name in pg+tg):
    res.append((min(g for g,name in pg+tg),x,y,blockers,math.dist((191.4,48.0),(x,y))))
 print('feasible',len(res))
 for q in sorted(res,reverse=True)[:20]:print(q)
